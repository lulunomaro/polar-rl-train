"""Read existing async cases and the pinned SDK action path; no GPU job submission."""
from pathlib import Path
import sys,json,shlex,hashlib,importlib.util
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
def sources():
    from remote_io import connect
    c=connect()
    try:
        code=r'''
from pathlib import Path
import importlib.util,json,zipfile,hashlib
lab=Path(importlib.util.find_spec('isaaclab').origin).parent
sdk=lab/'envs/mdp/actions/joint_actions.py';assert sdk.exists()
pack=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/artifacts/d3-clock2500-solver32-closure234-frozen.zip')
assert hashlib.sha256(pack.read_bytes()).hexdigest()=='56f6ac8fe847b27e4a59e679b6dba99912652efe6b077d255f85754963fd359d'
with zipfile.ZipFile(pack) as z:
 names=['runtime/isaac/mod4/frozen_history_flat.py','runtime/isaac/mod4/frozen_history_spin.py']
 out={Path(n).name:dict(text=z.read(n).decode(),sha256=hashlib.sha256(z.read(n)).hexdigest(),source=str(pack)+'!'+n) for n in names}
 out['joint_actions.py']=dict(text=sdk.read_text(),sha256=hashlib.sha256(sdk.read_bytes()).hexdigest(),source=str(sdk))
 print(json.dumps(out))
'''
        _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=30)
        raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
        files=json.loads(raw)
        for n,row in files.items():
            data=row['text'].encode();assert hashlib.sha256(data).hexdigest()==row['sha256'];(D/'reviewed_sources'/n).write_bytes(data)
        (R/'SDK_ACTION_SOURCE_READ.json').write_text(json.dumps({n:{k:v for k,v in row.items() if k!='text'} for n,row in files.items()},indent=2),encoding='utf8')
        print(json.dumps({n:row['sha256'] for n,row in files.items()}))
    finally:c.close()
def evaluation():
    p=D.parent/'MOD4_CLOSURE_EPISODE_CONTINUATION_20261008/read_block1_scope_evidence.py'
    s=importlib.util.spec_from_file_location('existing_async_read_only',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    m.D=D;m.R=R;m.evaluator()
    (R/'D3_EXISTING_ASYNC_CASES.json').write_bytes((R/'BLOCK1_EVALUATOR_SCOPE_EVIDENCE.json').read_bytes())
if __name__=='__main__':
    if sys.argv[-1]=='sources':sources()
    elif sys.argv[-1]=='evaluation':evaluation()
    else:raise SystemExit('sources or evaluation')
