"""Canonical scenario detail and freshly evaluated, read-only evidence views."""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / '.agents/ask'))

from verification.traceability.contracts import Invalid, slug
from verification.traceability.evidence import git
from verification.traceability.service import evidence_state, inspect_completion


def inspect(root, work_id, candidate_sha=None):
    """Inspect retained evidence without executing checks, writing, or admitting work.

    ``historical`` is relative to this checkout's HEAD and remains true even if
    historical evidence is invalid or unavailable. Only a valid current candidate
    can have ``current_completion`` true; this projection grants no acceptance.
    """
    root = Path(root).resolve()
    result = {'schema': 'ask-engineering-evidence/v1', 'work_id': work_id,
              'status': 'invalid', 'candidate_sha': candidate_sha, 'current_sha': None,
              'historical': False, 'current_completion': False, 'scenarios': []}
    try:
        if not slug(work_id):
            raise Invalid('invalid work_id')
        try:
            current = git(root, 'rev-parse', 'HEAD')
        except Invalid:
            result['status'] = 'unavailable'
            result['completion'] = {
                'schema': 'ask-completion/v1', 'status': 'fail', 'scope': 'workstream',
                'task_id': None, 'candidate_sha': candidate_sha, 'input_digests': {},
                'criterion_evidence': [], 'missing_evidence': [],
                'errors': ['Git evidence inspection is unavailable because the configured model root is not a Git checkout.'],
                'execution_artifacts': [],
            }
            return result
        result['current_sha'] = current
        sha = current if candidate_sha is None else git(
            root, 'rev-parse', '--verify', candidate_sha + '^{commit}')
        historical = sha != current
        result.update(candidate_sha=sha, historical=historical)
        completion, contracts = inspect_completion(root, work_id, sha, historical=historical)
        result['completion'] = completion
        if contracts is not None:
            obligations = {item['criterion_id']: item['required_types']
                           for item in contracts['plan']['obligations']}
            evidence = {row['criterion_id']: row for row in completion['criterion_evidence']}
            for criterion in contracts['spec']['criteria']:
                cid = criterion['id']
                result['scenarios'].append({
                    'criterion_id': cid, 'given': criterion['given'], 'when': criterion['when'],
                    'then': criterion['then'], 'verification_mode': criterion['verification_mode'],
                    'required_types': obligations.get(cid, []),
                    'tests': [test for test in contracts['plan']['tests'] if cid in test['criterion_ids']],
                    'evidence': evidence.get(cid),
                    'reference': {'path': f'specs/current/{work_id}.json', 'id': cid},
                    'candidate_sha': sha,
                })
        if completion['status'] == 'pass':
            result['status'] = 'historical' if historical else 'valid'
            result['current_completion'] = not historical
        else:
            result['status'] = completion.get('evidence_state',
                'invalid' if completion['errors'] else 'unavailable')
    except (Invalid, OSError, ValueError, TypeError) as exc:
        result['status'] = evidence_state(exc)
        result['completion'] = {
            'schema': 'ask-completion/v1', 'status': 'fail', 'scope': 'workstream',
            'task_id': None, 'candidate_sha': result['candidate_sha'], 'input_digests': {},
            'criterion_evidence': [], 'missing_evidence': [], 'errors': [str(exc)],
            'execution_artifacts': [],
        }
    return result
