"""Run the new CPU admission in the authorized SSH administration context."""
from pathlib import Path
import sys,json,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';root='D:/MOD4_async_eval/closure_episode_clock2500_v15'
assert not (R/'SPRING_AUDIT_WORKER_ADMITTED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
c=connect_eval()
try:
    with c.open_sftp() as f:
        for n in ('admit_spring_audit_worker_once.py','eval_worker_spring_audit_review.py'):
            raw=(D/n).read_bytes();compile(raw.decode(),n,'exec')
            with f.open(root+'/'+n,'wb') as out:out.write(raw)
            assert f.open(root+'/'+n).read()==raw
    _,o,e=c.exec_command('"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" "'+root+'/admit_spring_audit_worker_once.py"',timeout=45)
    raw=o.read();err=e.read()
    code=o.channel.recv_exit_status()
    if code:
        (R/'SPRING_AUDIT_ADMISSION_FIRST_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace'),returncode=code),indent=2),encoding='utf8')
        raise RuntimeError((raw+err).decode(errors='replace'))
    value=json.loads(raw);value['source_sha256']={n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in ('admit_spring_audit_worker_once.py','eval_worker_spring_audit_review.py')}
    (R/'SPRING_AUDIT_WORKER_ADMITTED.json').write_text(json.dumps(value,indent=2),encoding='utf8');print(json.dumps(value))
finally:c.close()
