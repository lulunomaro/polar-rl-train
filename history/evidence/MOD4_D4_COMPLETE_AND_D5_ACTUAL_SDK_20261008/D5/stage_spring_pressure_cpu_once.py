"""Run new pressure component CPU contracts on the target's pinned Torch only."""
from pathlib import Path
import json,sys,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'SPRING_PRESSURE_CPU_PASSED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
root='/home/egde/rl_candidates/MOD4_D5_SPRING_LAW_PREPARE_20261008'
c=connect()
try:
    with c.open_sftp() as f:
        for name in ('spring_pressure_component.py','test_spring_pressure_cpu.py'):
            raw=(D/name).read_bytes();compile(raw.decode(),name,'exec')
            with f.open(root+'/'+name,'wb') as out:out.write(raw)
            assert f.open(root+'/'+name).read()==raw
    _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python '+shlex.quote(root+'/test_spring_pressure_cpu.py'),timeout=30)
    raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    v=json.loads(raw);assert v['passed'] and v['CPU_only'] and not v['CUDA_initialized']
    (R/'SPRING_PRESSURE_CPU_PASSED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
finally:c.close()
