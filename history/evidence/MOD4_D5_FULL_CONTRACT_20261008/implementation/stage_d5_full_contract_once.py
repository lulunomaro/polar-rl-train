"""Stage immutable D5 extension and target CPU proof; no GPU/budget authority."""
from pathlib import Path
import sys,json,shlex,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'STAGED_D5_FULL_CONTRACT.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D5_FULL_CONTRACT_20261008'
try:
    setup=r'''
from pathlib import Path
import json,shutil,hashlib
D=Path('/home/egde/rl_candidates/MOD4_D5_FULL_CONTRACT_20261008');OLD=Path('/home/egde/rl_candidates/MOD4_D4_FULL_CONTRACT_20261008')
assert not D.exists();(D/'reports').mkdir(parents=True)
f=json.loads((OLD/'reports/SOURCE_FREEZE.json').read_text())['sha256']
for n,h in f.items():
 assert hashlib.sha256((OLD/n).read_bytes()).hexdigest()==h
 p=D/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OLD/n,p)
print(json.dumps(dict(original_source_count=len(f))))
'''
    _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(setup),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    new=[]
    with c.open_sftp() as f:
        for p in (D/'isaac/mod4').glob('*.py'):
            name='isaac/mod4/'+p.name;f.put(str(p),root+'/'+name);assert f.open(root+'/'+name).read()==p.read_bytes();new.append(name)
        for name in ('supervise_d5_full_contract.py','native_d5_spring_probe.py','test_spring_checkpoint_cpu.py'):
            f.put(str(D/name),root+'/'+name);new.append(name)
        for name in ('SELECTED_D4_BEHAVIOR_SOURCE.json','D5_STIFFNESS_PRESSURE_ACTUAL_SDK_REVIEW.json','SPRING_PRESSURE_CPU_PASSED.json','SPRING_PRESSURE_ADAPTER_CPU_PASSED.json'):
            f.put(str(R/name),root+'/reports/'+name)
    code=r'''
from pathlib import Path
import sys,os,json,hashlib,time,subprocess,ast
D=Path('/home/egde/rl_candidates/MOD4_D5_FULL_CONTRACT_20261008');R=D/'reports';OLD=Path('/home/egde/rl_candidates/MOD4_D4_FULL_CONTRACT_20261008')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=read(OLD/'reports/SOURCE_FREEZE.json')['sha256'];f=dict(old)
for n,h in old.items():assert sha(D/n)==h
new=NEW_SOURCE_NAMES
for n in new:ast.parse((D/n).read_text());f[n]=sha(D/n)
(R/'SOURCE_FREEZE.json').write_text(json.dumps(dict(epoch=time.time(),candidate_root=str(D),sha256=f,source_count=len(f),all243_predecessor_exact=True,new_scope='D5 stiffness-only factor.9-1.1',hardware_force_stroke_calibration=False),indent=2))
p=subprocess.run([sys.executable,str(D/'test_spring_checkpoint_cpu.py')],cwd=D,env=dict(os.environ,PYTHONPATH=str(D/'isaac/mod4')),capture_output=True,text=True)
assert p.returncode==0,p.stdout+p.stderr;cpu=json.loads(p.stdout);assert cpu['passed'] and not cpu['CUDA_initialized']
(R/'SPRING_CHECKPOINT_CPU_PASSED.json').write_text(json.dumps(cpu,indent=2))
sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));import supervise_d5_full_contract as w
w.verify();src=w.source();assert not __import__('torch').cuda.is_initialized()
v=dict(epoch=time.time(),source_count=len(f),all243_predecessor_exact=True,checkpoint_CPU=cpu,actual_behavior_source=w.fullsave(src,require_spring=False),controller_import_schema_pass=True,GPU_started=False,budget_transactions=0,old_training_not_interrupted=True)
(R/'STAGED_D5_FULL_CONTRACT.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('NEW_SOURCE_NAMES',repr(new))
    compile(code,'D5 stage CPU transport','exec')
    _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    v=json.loads(raw);(R/'STAGED_D5_FULL_CONTRACT.json').write_text(json.dumps(v,indent=2),encoding='utf8')
    with c.open_sftp() as f:
        for n in ('SOURCE_FREEZE.json','SPRING_CHECKPOINT_CPU_PASSED.json'):f.get(root+'/reports/'+n,str(R/n))
    print(json.dumps(v))
finally:c.close()
