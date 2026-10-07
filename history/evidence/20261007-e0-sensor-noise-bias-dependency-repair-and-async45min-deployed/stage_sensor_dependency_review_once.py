"""Explicit new authority with exact inference dependency closure; reuse finished SDK/20k."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
assert not (R/'SENSOR_DEPENDENCY_REVIEW_LAUNCHED.json').exists()
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,json,hashlib,shutil,time,subprocess,os
S=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_DR_STAGE1_20261007');D=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_DEPENDENCY_REVIEW_20261007');F=Path('/home/egde/rl_candidates/MOD4_S1A_FROZEN_SAVED_SCHEMA_REVIEW_20261007');N=Path('/home/egde/rl_candidates/MOD4_PHYSICS_DT1000_WORKER_REVIEW_20261007')
assert not D.exists();sys.path.insert(0,str(N));import continue_clock1000_worker_manifest_review_once as q
q.verify();assert q.base.budget_state()['active_segment'] is None and not q.base.trainers() and not q.w.read(q.ctl.STATE_PATH).get('active_training')
assert not q.helpers.identity(803760) and not q.helpers.identity(804240)
error=q.w.read(S/'reports/E0_SENSOR_ATTENTION.json');assert not error['active_segment'] and not error['own_child_still_alive']
text=(S/'sensor_baseline_flat.log').read_text();assert "ModuleNotFoundError: No module named 'history_actor_label_ppo'" in text
assert not (S/'reports/sensor_baseline_flat.json').exists() and 'Scene creation complete' not in text
before=q.ctl.CANONICAL.read_bytes();freeze=q.w.read(S/'reports/SOURCE_FREEZE.json')['sha256'];assert len(freeze)==199
D.mkdir();(D/'reports').mkdir()
for n,h in freeze.items():
 assert q.base.sha(S/n)==h;p=D/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(S/n,p)
for n in ('history_actor_label_ppo.py','history_latent_component.py'):
 h=q.w.read(F/'reports/SOURCE_FREEZE.json')['sha256'][n];assert q.base.sha(F/n)==h;shutil.copy2(F/n,D/n);freeze[n]=h
source=(S/'supervise_e0_sensor_dr_stage1.py').read_text()
begin=source.index(' sdk=[]\n');end=source.index(' sys.path.insert(0,str(CODE));from scut_curriculum_gate_v4 import evidence',begin)
replacement=""" old=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_DR_STAGE1_20261007');proof=q.w.read(old/'reports/SENSOR_ACTUAL_SDK_PASSED.json')
 assert proof['off_on_fixed_clean_plant_root_q_parameters_bit_exact'] and proof['real_manager_formula_tick_selected_reset_cleancritic_verified']
 reused=[]
 for label,count,steps in (('sensor_sdk_off',10,300),('sensor_sdk_noise_bias_mild_v1',10,300),('sensor_native20k',20000,120)):
  row=q.w.read(old/'reports'/(label+'_COMPLETE.json'));p=Path(row['output']);assert q.base.sha(p)==row['output_sha256'] and row['exit_code']==0
  raw=q.w.read(p);assert raw['actual_task_failed_environments']==0 and not raw['nonfinite'] and raw['max_closure_error_m']<=.002 and raw['max_mimic_error_rad']<=.01 and raw['physical_callback_count']==steps*10
  assert raw['initial_parameters']['actual_parameters_pass'] and raw['final_parameters']['actual_parameters_pass'];reused.append(row)
 write('SENSOR_SDK_NATIVE20K_EXACT_REUSED.json',dict(epoch=time.time(),receipts=reused,SDK=proof,same199_runtime_files_exact=True,new_PPO=0,no_duplicate_probe=True))
"""
source=source[:begin]+replacement+source[end:]
source=source.replace("assert not q.helpers.identity(x['owner']['pid'])","assert not q.helpers.identity(x['owner']['pid']) and not q.helpers.identity(803760)")
name='continue_sensor_dependency_review_once.py';compile(source,name,'exec');(D/name).write_text(source);freeze[name]=q.base.sha(D/name)
for n,h in freeze.items():assert q.base.sha(D/n)==h
q.base.atomic_json(D/'reports/SOURCE_FREEZE.json',dict(candidate_root=str(D),sha256=freeze,original199_byte_exact=True,added_dependencies_exact_from_frozen221=True,new_controller_only_reuses_3_finished_probes=True))
shutil.copy2(S/'reports/SENSOR_CPU_CONTRACT.json',D/'reports/SENSOR_CPU_CONTRACT.json');shutil.copy2(S/'reports/S1A_ARCHITECTURE_SELECTION.json',D/'reports/S1A_ARCHITECTURE_SELECTION.json')
sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));import frozen_history_policy
assert Path(frozen_history_policy.__file__).resolve()==D/'isaac/mod4/frozen_history_policy.py'
assert not __import__('torch').cuda.is_initialized()
q.base.atomic_json(D/'reports/INFERENCE_DEPENDENCY_CPU_PASSED.json',dict(epoch=time.time(),actual_full_dependency_import_passed=True,no_CUDA_initialized=True,missing_dependency_rejection_preserved=str(S/'reports/E0_SENSOR_ATTENTION.json')))
assert before==q.ctl.CANONICAL.read_bytes()
with (D/'controller.log').open('x') as log:p=subprocess.Popen([q.base.PY,str(D/name)],cwd=q.P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
time.sleep(.6);assert p.poll() is None
proc=Path('/proc')/str(p.pid);stat=(proc/'stat').read_text().rsplit(')',1)[1].split();receipt=dict(epoch=time.time(),root=str(D),owner=q.helpers.identity(p.pid),ppid=int(stat[1]),source_count=len(freeze),old199_runtime_byte_exact=True,all_previous_failures_retained=True,canonical_bytes_exact_at_handover=True,no_new_budget_seconds=0,unique_new_entry=name)
q.base.atomic_json(D/'reports/SENSOR_DEPENDENCY_REVIEW_LAUNCHED.json',receipt);q.base.atomic_json(q.ER/'SENSOR_DEPENDENCY_REVIEW_LAUNCHED.json',receipt)
print(json.dumps(receipt))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=40)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode();v=json.loads(raw)
 (R/'SENSOR_DEPENDENCY_REVIEW_LAUNCHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
finally:c.close()
