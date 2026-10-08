"""Stage complete state schema and target CPU tests; no GPU launch authority."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'D6_DAMPING_CHECKPOINT_TARGET_CPU_PASSED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D6_DAMPING_SOURCE_PREPARE_20261008'
try:
    with c.open_sftp() as f:
        for name in ('gas_damping_checkpoint.py','test_gas_damping_checkpoint_cpu.py'):
            try:f.stat(root+'/'+name);raise AssertionError('Checkpoint source already staged')
            except FileNotFoundError:pass
            raw=(D/name).read_bytes()
            with f.open(root+'/'+name,'wb') as o:o.write(raw)
            assert f.open(root+'/'+name).read()==raw
    code=r'''
from pathlib import Path
import subprocess,sys,json,time,hashlib
D=Path('/home/egde/rl_candidates/MOD4_D6_DAMPING_SOURCE_PREPARE_20261008');R=D/'reports'
assert not (R/'D6_DAMPING_CHECKPOINT_TARGET_CPU_PASSED.json').exists()
p=subprocess.run([sys.executable,str(D/'test_gas_damping_checkpoint_cpu.py')],capture_output=True,text=True,cwd=D)
assert p.returncode==0,p.stdout+p.stderr
v=json.loads(p.stdout);assert v['passed'] and v['count']==10 and not v['CUDA_initialized']
v.update(epoch=time.time(),source_sha256={n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in ('gas_damping_checkpoint.py','test_gas_damping_checkpoint_cpu.py')})
(R/'D6_DAMPING_CHECKPOINT_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''
    _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=45)
    raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    v=json.loads(raw);(R/'D6_DAMPING_CHECKPOINT_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
    print(json.dumps(v))
finally:c.close()
