"""Fault-inject transient, persistent and unrelated evaluator write failures."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json,os
from resilient_json_atomic import atomic

def sharing(code):
    e=PermissionError('injected Windows file sharing conflict');e.winerror=code;return e

def run():
    with TemporaryDirectory() as folder:
        target=Path(folder)/'state.json';target.write_text('{"old":true}')
        calls=[];delays=[]
        def transient(src,dst):
            calls.append(Path(src));assert target.read_text()=='{"old":true}'
            if len(calls)<=4:raise sharing(5)
            os.replace(src,dst)
        atomic(target,{'new':True},replace=transient,sleep=delays.append)
        assert json.loads(target.read_text())=={'new':True} and len(calls)==5 and len(delays)==4
        assert len(set(calls))==1 and not calls[0].exists()
        retained=[]
        def persistent(src,dst):retained.append(Path(src));raise sharing(32)
        try:atomic(target,{'persistent':True},replace=persistent,sleep=lambda _:None,attempts=3)
        except PermissionError:pass
        else:raise AssertionError('persistent failure hidden')
        assert len(retained)==3 and retained[0].exists() and json.loads(target.read_text())=={'new':True}
        assert retained[0]!=calls[0]
        unrelated=[]
        def other(src,dst):unrelated.append(src);raise FileNotFoundError('not a sharing error')
        try:atomic(target,{'other':True},replace=other,sleep=lambda _:None)
        except FileNotFoundError:pass
        else:raise AssertionError('unrelated error hidden')
        assert len(unrelated)==1
    return dict(passed=True,transient_retries=4,persistent_attempts=3,unrelated_attempts=1,unique_temporary_per_write=True,persistent_payload_preserved=True,no_GPU_PPO_canonical_or_replay=True)

if __name__=='__main__':print(json.dumps(run()))

