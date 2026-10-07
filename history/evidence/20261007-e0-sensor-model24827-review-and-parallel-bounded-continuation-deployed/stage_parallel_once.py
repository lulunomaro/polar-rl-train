"""New isolated controller staging only. Old206 files exact; no learning."""
from pathlib import Path
import json,sys,shlex
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
ROOT='/home/egde/rl_candidates/MOD4_E0_SENSOR_CONTINUOUS_EXECUTION_20261007'
c=connect()
def run(code,seconds=60):
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=seconds);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode();return json.loads(raw)
try:
 v=run(r'''
from pathlib import Path
import json,shutil,hashlib
T=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_STABLE_CONTINUATION_20261007');D=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_CONTINUOUS_EXECUTION_20261007')
assert not D.exists();D.mkdir();(D/'reports').mkdir();f=json.loads((T/'reports/SOURCE_FREEZE.json').read_text())['sha256'];assert len(f)==206
for n,h in f.items():
 p=T/n;assert hashlib.sha256(p.read_bytes()).hexdigest()==h,n
 out=D/n;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
for n in ('SENSOR_CPU_CONTRACT.json','SENSOR_MODEL24061_FIRST_MATCHED_REVIEW.json'):shutil.copy2(T/'reports'/n,D/'reports'/n)
(D/'reports/INITIAL_FEEDBACK_JOBS.json').write_text(json.dumps(dict(jobs=['clk1000-s2complete-20-stable-'+k for k in ('flat','spin','world')])))
print(json.dumps(dict(old206_exact=True,newroot=str(D))))
''')
 (R/'STAGED_ORIGINAL206.json').write_text(json.dumps(v,indent=2))
 with c.open_sftp() as f:
  for name in ('supervise_sensor_parallel_continuation.py','test_parallel_controller_cpu.py'):f.put(str(D/name),ROOT+'/'+name)
 v=run(r'''
from pathlib import Path
import json,hashlib,subprocess,sys,time,inspect
D=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_CONTINUOUS_EXECUTION_20261007');T=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_STABLE_CONTINUATION_20261007');f=json.loads((T/'reports/SOURCE_FREEZE.json').read_text())['sha256']
for n in ('supervise_sensor_parallel_continuation.py','test_parallel_controller_cpu.py'):f[n]=hashlib.sha256((D/n).read_bytes()).hexdigest()
assert len(f)==208;(D/'reports/SOURCE_FREEZE.json').write_text(json.dumps(dict(sha256=f,original206_byte_exact=True,only_two_new_controller_contract_files=True),indent=2))
source=json.loads((T/'reports/SENSOR_STABLE_COMPLETE.json').read_text())['checkpoint'];assert hashlib.sha256(Path(source['path']).read_bytes()).hexdigest()==source['sha256']
py='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
def cpu(args):
 p=subprocess.run([py,*args],capture_output=True,text=True,cwd=D/'isaac/mod4',timeout=60);assert p.returncode==0,p.stdout+p.stderr;return json.loads(p.stdout)
resume=cpu([str(D/'isaac/mod4/test_sensor_resume_actual_cpu.py'),source['path']]);assert resume['passed'] and resume['no_CUDA_initialized']
(D/'reports/SENSOR_RESUME_CPU_CONTRACT.json').write_text(json.dumps(resume,indent=2))
cadence=cpu([str(D/'test_parallel_controller_cpu.py')]);assert cadence['passed'];(D/'reports/PARALLEL_CONTROLLER_CPU_CONTRACT.json').write_text(json.dumps(cadence,indent=2))
sys.path.insert(0,str(D));import supervise_sensor_parallel_continuation as n
n.s.verify();original=inspect.getsource(n.s.train);patched=original.replace('logs.mkdir();','logs.mkdir(exist_ok=True);');assert patched!=original and patched.replace('logs.mkdir(exist_ok=True);','logs.mkdir();')==original
initial=[n.inspect_result('clk1000-s2complete-20-stable-'+k) for k in ('flat','spin','world')]
assert not any(x.get('attention') for x in initial),initial
v=dict(epoch=time.time(),source=source,source_count=len(f),original206_exact=True,training_function_only_repeat_directory_creation_changed=True,resume_CPU=resume,controller_CPU=cadence,initial_actual_feedback=initial,no_new_preflight=True,no_PPO_started=True)
(D/'reports/PARALLEL_STAGING_VERIFIED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
''',100)
 (R/'PARALLEL_STAGING_VERIFIED.json').write_text(json.dumps(v,indent=2));print(json.dumps(dict(source=v['source'],source_count=v['source_count'],resume_contracts=v['resume_CPU']['count'],cadence_contracts=v['controller_CPU']['contracts'],initial_feedback=[dict(job=x['job'],status=x['status'],attention=x.get('attention'),target=x.get('target_count')) for x in v['initial_actual_feedback']],no_PPO_started=True)))
finally:c.close()
