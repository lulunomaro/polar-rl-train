"""Read completed evidence and exact source bytes, without changing any authority."""
from pathlib import Path
import sys,json,hashlib,shlex
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
roots=dict(original='/home/egde/rl_candidates/MOD4_E0_SENSOR_DR_STAGE1_20261007',dependency='/home/egde/rl_candidates/MOD4_E0_SENSOR_DEPENDENCY_REVIEW_20261007',publisher_original='/home/egde/rl_candidates/MOD4_E0_SENSOR_ASYNC_PUBLICATION_20261007',publisher='/home/egde/rl_candidates/MOD4_E0_SENSOR_ASYNC_DEPENDENCY_PUBLICATION_20261007')
try:
 with c.open_sftp() as s:
  for label,root in roots.items():
   dest=R/'native_evidence'/label;dest.mkdir(parents=True,exist_ok=True)
   for entry in s.listdir_attr(root+'/reports'):
    if entry.filename.endswith('.json') and entry.st_size<2000000:s.get(root+'/reports/'+entry.filename,str(dest/entry.filename))
   for name in ('controller.log','sensor_baseline_flat.log','publisher.log'):
    try:s.get(root+'/'+name,str(dest/name))
    except FileNotFoundError:pass
  dest=R/'runtime_source';dest.mkdir(exist_ok=True)
  for name in ('continue_sensor_dependency_review_once.py','history_actor_label_ppo.py','history_latent_component.py','isaac/mod4/sensor_mild_math.py','isaac/mod4/sensor_a0_runtime.py','isaac/mod4/test_sensor_checkpoint_cpu.py','isaac/mod4/train_sensor_ppo.py','isaac/mod4/sensor_flat_probe.py','isaac/mod4/sensor_spin_probe.py','isaac/mod4/sensor_world_probe.py','isaac/mod4/frozen_history_policy.py','native_sensor1000_probe.py'):
   out=dest/name;out.parent.mkdir(parents=True,exist_ok=True);s.get(roots['dependency']+'/'+name,str(out))
 code=r'''
from pathlib import Path
import json,hashlib,time
S=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_DR_STAGE1_20261007');D=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_DEPENDENCY_REVIEW_20261007');f=json.loads((D/'reports/SOURCE_FREEZE.json').read_text())['sha256']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for n,h in f.items():assert sha(D/n)==h,n
old=json.loads((S/'reports/SOURCE_FREEZE.json').read_text())['sha256']
for n,h in old.items():assert sha(S/n)==h and sha(D/n)==h,n
row=json.loads((S/'reports/sensor_native20k_COMPLETE.json').read_text());raw=json.loads(Path(row['output']).read_text());assert sha(Path(row['output']))==row['output_sha256']
summary={k:raw[k] for k in ('actual_physics_dt','actual_step_dt','actual_task_failed_environments','nonfinite','max_closure_error_m','max_mimic_error_rad','physical_callback_count','expected_callback_count','sensor_recipe')}
summary['initial_parameters_pass']=raw['initial_parameters']['actual_parameters_pass'];summary['final_parameters_pass']=raw['final_parameters']['actual_parameters_pass']
proof=dict(epoch=time.time(),source_count=len(f),original199_exact=True,all202_actual_hashes_exact=True,native20k_SHA_index=row,native20k_actual_summary=summary,large_native20k_root_q_not_embedded=True,weights_assets_not_copied=True)
print(json.dumps(proof))
'''
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode();v=json.loads(raw)
 (R/'SENSOR_DEPENDENCY_SOURCE_AND_NATIVE20K_VERIFIED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
finally:c.close()
