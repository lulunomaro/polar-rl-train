"""Install reviewed receipt retry files after the previous worker actually exited."""
from pathlib import Path
import sys,json,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'GAS_DAMPING_REVIEW_WORKER_ADMITTED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
c=connect_eval();root='D:/MOD4_async_eval/closure_episode_clock2500_v15'
try:
    sources={}
    with c.open_sftp() as f:
        for name in ('eval_worker_gas_damping_review.py','admit_gas_damping_review_once.py'):
            b=(D/name).read_bytes();compile(b.decode(),name,'exec');sources[name]=hashlib.sha256(b).hexdigest()
            try:f.stat(root+'/'+name)
            except FileNotFoundError:pass
            else:raise AssertionError('Already staged new file; do not repeat '+name)
            with f.open(root+'/'+name,'wb') as out:out.write(b)
            with f.open(root+'/'+name) as inp:assert inp.read()==b
    for name in ('admit_gas_damping_review_once.py',):
        _,o,e=c.exec_command('"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" "'+root+'/'+name+'"',timeout=45)
        raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
        if rc:
            (R/'GAS_DAMPING_REVIEW_DEPLOY_ATTENTION.json').write_text(json.dumps(dict(entry=name,stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace'),returncode=rc),indent=2),encoding='utf8')
            raise RuntimeError((raw+err).decode(errors='replace'))
        value=json.loads(raw);value['source_sha256']=sources
        out='GAS_DAMPING_REVIEW_CPU_PASSED.json' if name.startswith('test_') else 'GAS_DAMPING_REVIEW_WORKER_ADMITTED.json'
        (R/out).write_text(json.dumps(value,indent=2),encoding='utf8');print(json.dumps(value))
finally:c.close()
