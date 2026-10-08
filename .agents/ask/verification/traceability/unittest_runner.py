"""Adapter-owned instrumentation. Inputs are unittest names or discovery arguments."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import traceback
import unittest

class CaseResult(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.cases=[]
    def record(self,test,outcome,err=None):
        kind=None
        if err:
            tb=err[2];in_method=False
            while tb:
                if tb.tb_frame.f_code.co_name==getattr(test,'_testMethodName',None):in_method=True
                tb=tb.tb_next
            kind='behavior_assertion' if outcome=='failed' and in_method else 'setup_or_runtime_error'
        self.cases.append({'case_id':test.id(),'outcome':outcome,'failure_kind':kind})
    def addSuccess(self,test):super().addSuccess(test);self.record(test,'passed')
    def addFailure(self,test,err):super().addFailure(test,err);self.record(test,'failed',err)
    def addError(self,test,err):super().addError(test,err);self.record(test,'error',err)
    def addSkip(self,test,reason):super().addSkip(test,reason);self.record(test,'skipped')
    def addExpectedFailure(self,test,err):super().addExpectedFailure(test,err);self.record(test,'expected_failure',err)
    def addUnexpectedSuccess(self,test):super().addUnexpectedSuccess(test);self.record(test,'unexpected_success')
    def addSubTest(self,test,subtest,err):
        # v1 requires explicit complete case IDs; unreviewed parameter expansion is refused.
        super().addSubTest(test,subtest,err);self.record(subtest,'unsupported_subtest',err)

def main():
    output=Path(sys.argv[1]);args=sys.argv[2:];sys.path.insert(0,str(Path.cwd()))
    loader=unittest.TestLoader()
    try:
        if args and args[0]=='discover':
            parser=argparse.ArgumentParser();parser.add_argument('-s',default='.');parser.add_argument('-p',default='test*.py');parser.add_argument('-t',default=None)
            ns=parser.parse_args(args[1:]);suite=loader.discover(ns.s,ns.p,ns.t)
        elif args and not any(x.startswith('-') for x in args):suite=loader.loadTestsFromNames(args)
        else:raise ValueError('unsupported unittest selectors')
        result=unittest.TextTestRunner(verbosity=2,resultclass=CaseResult).run(suite)
        doc={'cases':result.cases,'collection_status':'error' if loader.errors or not result.testsRun else 'ok'}
        output.write_text(json.dumps(doc))
        return 0 if result.wasSuccessful() and result.testsRun and not loader.errors else 1
    except Exception:
        traceback.print_exc();output.write_text(json.dumps({'cases':[],'collection_status':'error'}));return 1
if __name__=='__main__':raise SystemExit(main())
