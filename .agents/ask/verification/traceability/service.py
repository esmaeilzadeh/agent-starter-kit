"""Coordinator operations shared by the thin CLI and the pinned Verify runner."""
from __future__ import annotations
import ast
import fnmatch
import json
import os
from pathlib import Path, PurePosixPath
from types import SimpleNamespace
from .adapters import git
from .completion import evaluate_completion,evidence_state
from .contracts import Invalid,digest,load,slug
from .evidence import load_accepted,read_at,source_changes,write_json


class _RevisionPath:
    """Read-only Path subset used by the existing CheckPlan loader/expander.

    Git supplies both file bytes and executable modes. No checkout, temporary
    files, index refresh, or command execution is needed to expand old globs.
    """
    def __init__(self,root,sha,relative='.',trees=None):
        self.root=root;self.sha=sha;self.relative=PurePosixPath(relative)
        self.trees={} if trees is None else trees

    def __truediv__(self,name):
        relative=self.relative/name
        if relative.is_absolute() or '..' in relative.parts:raise Invalid('unsafe historical CheckPlan path')
        return _RevisionPath(self.root,self.sha,relative,self.trees)

    def __lt__(self,other):return str(self.relative)<str(other.relative)

    def _children(self):
        name=str(self.relative)
        if name not in self.trees:
            target=self.sha+'^{tree}' if name=='.' else self.sha+':'+name
            entries={}
            for line in git(self.root,'cat-file','-p',target).splitlines():
                metadata,filename=line.split('\t',1)
                mode,kind,oid=metadata.split()
                if filename.startswith('"'):
                    filename=os.fsdecode(ast.literal_eval('b'+filename))
                entries[filename]=(int(mode,8),kind,oid)
            self.trees[name]=entries
        return self.trees[name]

    def _entry(self):
        if self.relative==PurePosixPath('.'):return (0o040000,'tree',self.sha+'^{tree}')
        parent=_RevisionPath(self.root,self.sha,self.relative.parent,self.trees)
        try:return parent._children().get(self.relative.name)
        except Invalid:return None

    def is_file(self):
        entry=self._entry()
        # Unsafe/symlink inputs fail closed instead of reading another revision
        # or a path outside the repository.
        return bool(entry and entry[0] in (0o100644,0o100755))

    def stat(self):
        entry=self._entry()
        if not entry:raise FileNotFoundError(str(self.relative))
        return SimpleNamespace(st_mode=entry[0])

    def read_bytes(self):
        if not self.is_file():raise Invalid(f'missing/unsafe historical CheckPlan file: {self.relative}')
        return read_at(self.root,self.sha,str(self.relative))

    def read_text(self,encoding='utf-8'):return self.read_bytes().decode(encoding)

    def relative_to(self,other):return self.relative.relative_to(other.relative)

    def glob(self,pattern):
        parts=PurePosixPath(pattern).parts
        if not parts or PurePosixPath(pattern).is_absolute() or '..' in parts:
            raise Invalid('unsafe historical CheckPlan glob')

        def match(directory,remaining):
            if not remaining:
                yield directory;return
            segment,*tail=remaining
            if segment=='**':
                yield from match(directory,tail)
                for name,entry in directory._children().items():
                    if entry[1]=='tree':yield from match(directory/name,remaining)
            else:
                for name,entry in directory._children().items():
                    if fnmatch.fnmatchcase(name,segment):
                        child=directory/name
                        if not tail:yield child
                        elif entry[1]=='tree':yield from match(child,tail)

        yield from match(self,parts)


def reports(root,work_id,contracts,sha,scope,task_id):
    runtime=Path(root)/'work'/work_id/'traceability'
    try:ledger=json.loads((runtime/'executions.json').read_text())
    except OSError as exc:raise Invalid('no coordinator-executed case evidence') from exc
    except ValueError as exc:raise Invalid('invalid coordinator-executed case evidence') from exc
    if not isinstance(ledger,list) or any(not isinstance(entry,dict) for entry in ledger):
        raise Invalid('invalid coordinator-executed case evidence')
    matching=[e for e in ledger if e.get('spec_digest')==digest(contracts['spec']) and e.get('plan_digest')==digest(contracts['plan'])]
    finals=[e for e in matching if e['phase']=='final_green' and e['candidate_sha']==sha and e['scope']==scope and e['task_id']==task_id]
    selected=[e for e in matching if e['phase']=='red']+finals[-1:]
    docs=[];rejected=[]
    known={(t['runner_id'],t['case_id'],t['id']) for t in contracts['plan']['tests']}
    for entry in selected:
        if not slug(entry['run_id']):raise Invalid('invalid run identity')
        doc=load(runtime/'runs'/entry['run_id']/'results.json')
        if digest(doc)!=entry['digest']:raise Invalid('changed coordinator-executed report')
        if entry['phase']=='red':
            identities=[(c.get('runner_id'),c.get('case_id'),c.get('test_id')) for c in doc.get('cases',[])]
            reasons=[]
            if not doc.get('executions') or any(e.get('collection_status')!='ok' for e in doc['executions']):reasons.append('collection failure or zero cases')
            if not identities or len(identities)!=len(set(identities)) or any(identity not in known for identity in identities):reasons.append('unknown, unsupported or duplicate historical cases')
            if not any(c.get('outcome')=='failed' and c.get('failure_kind')=='behavior_assertion' for c in doc.get('cases',[])):reasons.append('no recognized behavior assertion red')
            if reasons:
                rejected.append({'run_id':entry['run_id'],'candidate_sha':entry['candidate_sha'],'reasons':reasons,'report_digest':entry['digest'],'retained_report':str((runtime/'runs'/entry['run_id']/'results.json').relative_to(root))})
                continue
        docs.append(doc)
    return docs,rejected


def inspect_completion(root,work_id,sha=None,anchor_sha=None,scope='workstream',task_id=None,static=None,runtime_root=None,*,historical=False):
    """Return (fresh completion evaluation, accepted contracts), without writes.

    Only explicit historical inspection changes the source-input view. Normal
    callers retain current-source and detached-candidate completion semantics.
    """
    root=Path(root).resolve();runtime_root=Path(runtime_root or root).resolve();sha=sha or git(root,'rev-parse','HEAD');anchor_sha=anchor_sha or sha
    report={'schema':'ask-completion/v1','status':'fail','scope':scope,'task_id':task_id,'candidate_sha':sha,'input_digests':{},'criterion_evidence':[],'missing_evidence':[],'errors':[],'execution_artifacts':[]}
    contracts=None
    try:
        contracts=load_accepted(root,work_id,anchor_sha,sha)
        if not historical and root==runtime_root and (git(root,'rev-parse','HEAD')!=sha or source_changes(root,work_id)):raise Invalid('dirty or non-current candidate source')
        review=load(runtime_root/'work'/work_id/'traceability'/'reviews'/(sha+'.json'))
        runs,rejected=reports(runtime_root,work_id,contracts,sha,scope,task_id)
        if static is None:
            receipt=load(runtime_root/'work'/work_id/'traceability'/('static-'+sha+'.json'))
            if receipt.get('candidate_sha')!=sha or receipt.get('result')!='pass':raise Invalid('static verification missing/failed/stale')
            from verification.plan import load_plan,expand_plan
            from .contracts import file_digest
            inputs=_RevisionPath(root,sha) if historical else root
            checks=expand_plan(inputs,load_plan(inputs))
            identity=digest({'checks':checks,'yaml_digest':file_digest(inputs/'.agents/verification.yaml')})
            if receipt.get('checkplan_digest')!=identity:raise Invalid('stale static CheckPlan')
            executed=receipt.get('checks',[])
            check_identity=lambda cs:[(c.get('id',c.get('command')),c.get('tier','mandatory'),c.get('command')) for c in cs]
            runner_digest=file_digest(inputs/'.agents/ask/verification/run.py') if historical else file_digest(Path(__file__).parents[1]/'run.py')
            if (check_identity(executed)!=check_identity(checks) or any(type(c.get('exit_code')) is not int or c['exit_code']!=0 or c.get('status')!='pass' for c in executed) or receipt.get('runner_digest')!=runner_digest):raise Invalid('static check execution failed or differs from pinned runner/CheckPlan')
            for check in executed:
                artifact=(runtime_root/check.get('evidence','')).resolve()
                if not artifact.is_relative_to((runtime_root/'work'/work_id/'traceability').resolve()) or file_digest(artifact)!=check.get('output_digest'):raise Invalid('changed/missing static execution log')
            static=receipt
        report=evaluate_completion(contracts,review,runs,{'root':runtime_root,'candidate_sha':sha,'scope':scope,'task_id':task_id,'static_checks':static,'detached_candidate':root!=runtime_root,'historical_candidate':historical})
        report['rejected_historical_attempts']=rejected
    except (Invalid,OSError,ValueError,KeyError,TypeError,AttributeError) as exc:
        report['errors'].append(str(exc));report['evidence_state']=evidence_state(exc)
    if historical:
        report['historical']=True;report['current_completion']=False
    return report,contracts


def check_completion(root,work_id,sha=None,anchor_sha=None,scope='workstream',task_id=None,static=None,runtime_root=None):
    report,_=inspect_completion(root,work_id,sha,anchor_sha,scope,task_id,static,runtime_root)
    path=Path(runtime_root or root).resolve()/'work'/work_id/'traceability'/'completion.json'
    write_json(path,report)
    return report
