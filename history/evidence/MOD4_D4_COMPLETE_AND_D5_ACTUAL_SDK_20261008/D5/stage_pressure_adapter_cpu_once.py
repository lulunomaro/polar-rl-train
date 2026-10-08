from pathlib import Path
import sys,shlex,json
D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'SPRING_PRESSURE_ADAPTER_CPU_PASSED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D5_SPRING_LAW_PREPARE_20261008'
try:
    with c.open_sftp() as f:
        for n in ('spring_pressure_sdk_adapter.py','test_spring_pressure_adapter_cpu.py'):
            raw=(D/n).read_bytes();compile(raw.decode(),n,'exec')
            with f.open(root+'/'+n,'wb') as out:out.write(raw)
            assert f.open(root+'/'+n).read()==raw
    _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python '+shlex.quote(root+'/test_spring_pressure_adapter_cpu.py'),timeout=30)
    raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    v=json.loads(raw);assert v['passed'] and v['CPU_only'] and not v['actual_SDK']
    (R/'SPRING_PRESSURE_ADAPTER_CPU_PASSED.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
finally:c.close()
