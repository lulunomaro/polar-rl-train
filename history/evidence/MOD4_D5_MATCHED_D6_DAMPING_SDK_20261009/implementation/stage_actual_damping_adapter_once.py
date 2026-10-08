"""Stage new isolated D6 adapter and target CPU proof; active D5 untouched."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'D6_DAMPING_ADAPTER_TARGET_CPU_PASSED.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D6_DAMPING_SOURCE_PREPARE_20261008'
try:
    names=('gas_damping_sdk_adapter.py','gas_damping_training_env.py','test_gas_damping_adapter_cpu.py')
    with c.open_sftp() as f:
        for n in names:
            try:f.stat(root+'/'+n);raise AssertionError('New source already exists: '+n)
            except FileNotFoundError:pass
            f.put(str(D/n),root+'/'+n);assert f.open(root+'/'+n).read()==(D/n).read_bytes()
    code=r'''
from pathlib import Path
import sys,json,hashlib,time,os,subprocess,zipfile
D=Path('/home/egde/rl_candidates/MOD4_D6_DAMPING_SOURCE_PREPARE_20261008');R=D/'reports'
assert not (R/'D6_DAMPING_ADAPTER_TARGET_CPU_PASSED.json').exists()
p=subprocess.run([sys.executable,str(D/'test_gas_damping_adapter_cpu.py')],cwd=D,capture_output=True,text=True)
assert p.returncode==0,p.stdout+p.stderr
v=json.loads(p.stdout);assert v['passed'] and v['count']==13 and not v['CUDA_initialized']
v.update(epoch=time.time(),active_D5_unchanged=True,actual_randomized_SDK_pending=True,new_budget_seconds=0)
(R/'D6_DAMPING_ADAPTER_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2))
E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007')
base=E/'artifacts/d5-clock2500-solver32-spring255-closedloop-frozen.zip'
assert hashlib.sha256(base.read_bytes()).hexdigest()=='fe8dc6bcb027215739a9edf7a8b5fa46240326b402e05ae0d0463db87044452c'
with zipfile.ZipFile(base) as z:
    for name in ('runtime/isaac/mod4/frozen_history_flat.py','runtime/isaac/mod4/env.json','SOURCE_MANIFEST.json'):
        raw=z.read(name);dest=D/'sdk_base'/Path(name).name;dest.parent.mkdir(exist_ok=True)
        assert not dest.exists();dest.write_bytes(raw)
print(json.dumps(v))
'''
    _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=45)
    raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    v=json.loads(raw);(R/'D6_DAMPING_ADAPTER_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
    (D/'sdk_base').mkdir(exist_ok=True)
    with c.open_sftp() as f:
        for n in ('frozen_history_flat.py','env.json','SOURCE_MANIFEST.json'):f.get(root+'/sdk_base/'+n,str(D/'sdk_base'/n))
    print(json.dumps(dict(passed=v['passed'],count=v['count'],Torch=v['Torch'],CUDA_initialized=v['CUDA_initialized'],new_budget_seconds=0)))
finally:c.close()
