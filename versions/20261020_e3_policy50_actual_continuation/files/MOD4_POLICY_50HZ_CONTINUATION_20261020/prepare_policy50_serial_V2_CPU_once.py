"""Prepare production binding, explicit clock admission and a separate serial parent; CPU only."""
from pathlib import Path
import ast,hashlib,json,shutil,time,traceback,sys
B=Path(__file__).resolve().parent;R=B/'reports';A=B.parent/'MOD4_E3_AUTOMATIC_CONTINUATION_20261020';V=B/'candidate_overlay_V2';C=B/'controller50'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert not V.exists() and not C.exists();shutil.copytree(B/'candidate_overlay',V);C.mkdir()
 worker=V/'recovery_worker.py';s=worker.read_text('utf8');start=s.index('  if native:\n');end=s.index('  go=json.loads',start)
 native='''  if native:
   runner.alg.actor.eval();runner.alg.critic.eval();obs=vec.get_observations();tick=env._integrated_contact.tick;fbt=env._feedback_100hz_tick;checks=[]
   with torch.inference_mode():
    for i in range(24):
     before=env._integrated_contact.tick;fb=env._feedback_100hz_tick;action=runner.alg.actor(obs,stochastic_output=False);obs,reward,done,info=vec.step(action)
     assert env._integrated_contact.tick-before==8 and env._feedback_100hz_tick-fb==2
     assert obs['policy'].shape==(20000,35) and obs['critic'].shape==(20000,38) and torch.isfinite(obs['policy']).all() and torch.isfinite(reward).all()
     checks.append(dict(control=i+1,callbacks=env._integrated_contact.tick-before,feedback_10ms_samples=env._feedback_100hz_tick-fb))
     assert not (OUT/'STOP_AFTER_SAVE.json').exists()
   for k,v in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(v,s[k]),k
   assert env._integrated_contact.tick-tick==192 and env._feedback_100hz_tick-fbt==48
   last=save(OUT/'own_clock_native24.pt',0);put(OUT/'CLOCK_NATIVE24_COMPLETE.json',dict(epoch=time.time(),source_SHA=task['source_SHA'],controls=24,callbacks=192,actual_step_s=float(env.step_dt),physics_dt_s=float(env.physics_dt),maximum_target_error=env._physics_action_delay.formula_max_error,all_policy_steps_exactly_8_physics_callbacks=True,all_feedback_steps_exactly_2_10ms_samples=True,no_optimizer_update=True,checks=checks,not_skill_or_336_native_qualification=True));put(OUT/'FINAL.json',dict(epoch=time.time(),passed=True,final=last,clock_protocol_only=True));return
  original_step=vec.step
  def step50(action):
   before=env._integrated_contact.tick;fb=env._feedback_100hz_tick;out=original_step(action)
   assert env._integrated_contact.tick-before==8 and env._feedback_100hz_tick-fb==2
   return out
  vec.step=step50
'''
 s=s[:start]+native+s[end:];s=s.replace("v['E3_production_updates']=updates;torch.save(v,tmp)","v['E3_production_updates']=updates;v['policy_clock']=dict(policy_hz=50,physics_dt_s=.0025,decimation=8,feedback_sampling_hz=100,source_policy_hz=task['source_policy_hz']);torch.save(v,tmp)");worker.write_text(s,encoding='utf8');ast.parse(s)
 changes=json.loads((R/'POLICY50_ISOLATED_OVERLAY_AND_CLOCK_COMPONENTS_CPU_ACTUAL.json').read_bytes())['changes']
 for row in changes:row.update(candidate_bytes=(V/row['relative']).stat().st_size,candidate_SHA=H(V/row['relative']))
 put(C/'POLICY50_OVERLAY_CONFIG.json',dict(changes=changes,worker_baseline_Adam=701620,policy_hz=50,source_policy_hz_first=100,native_protocol='24 controls / 192 physical callbacks / zero optimizer',explicit_migration=True))
 for name in ['auto_E3_pending_owner_v2.py','three_slot_common_v1.py','owner_listener_ready_single_cpu_v1.py','target_full_source_sdk_cpu_review.py']:
  shutil.copy2(A/name,C/name)
 shutil.copy2(B/'policy50_closed_source_CPU_v1.py',C/'policy50_closed_source_CPU_v1.py');shutil.copy2(B/'policy50_native_CPU_v1.py',C/'policy50_native_CPU_v1.py')
 common=C/'three_slot_common_v1.py';t=common.read_text('utf8');marker=" if spec.get('closed_production_continuation'):\n"
 branch=""" if spec.get('policy_hz')==50:
  q=row.get('closed_source_CPU') or {};v=q.get('value') or {};kind='policy_clock_100_to_50_migration' if spec['source_policy_hz']==100 else 'closed_same_backend_policy50_production'
  return bool(row.get('key')=='recovery' and row.get('phase')=='ready' and q.get('actual_CPU_waited_EXIT0') and q.get('SHA')==hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest() and v.get('kind')==kind and v.get('passed') and v.get('explicit_policy_clock_50Hz_admitted') and (v.get('policy_clock_native_CPU_SHA') if spec['source_policy_hz']==100 else v.get('same_clock_closed_production')) and v.get('source_SHA')==spec['source_SHA'] and v.get('GPU_UUID')==spec['GPU_UUID'] and v.get('execution_backend')==spec['execution_backend'] and v.get('all_source_model_runtime_finite_CPU') and v.get('old_complete_production_checkpoint_actual_EXIT0') and v.get('original_clip6_query_COM_closure_mimic_hardware_savedstop_guards_retained') and row.get('manifest_SHA')==spec['manifest_SHA'] and not row.get('original_error'))
"""
 assert marker in t;t=t.replace(marker,branch+marker,1);common.write_text(t,encoding='utf8')
 owner=C/'auto_E3_pending_owner_v2.py';t=owner.read_text('utf8').replace("source_qualification_kind='closed_same_backend_production'","source_qualification_kind=row['closed_source_CPU']['value']['kind']");owner.write_text(t,encoding='utf8')
 parent=(A/'auto_E3_serial_supervisor_v1.py').read_text('utf8');parent=parent.replace('MOD4_E3_AUTO_PENDING_SERIES_20261020.json','MOD4_E3_AUTO50_PENDING_SERIES_20261020.json')
 parent=parent.replace("-cfg['prior_single_E3_pending_seconds']-spent","-cfg['prior_single_E3_pending_seconds']-cfg['prior_100hz_series_pending_seconds']-spent")
 old="before=(previous_node/'recovery_worker.py').read_text('utf8');after=before.replace(oldfilename,newfilename).replace(str(oldAdam),str(newAdam));assert ast.dump(ast.parse(after.replace(newfilename,oldfilename).replace(str(newAdam),str(oldAdam))))==ast.dump(ast.parse(before));worker.write_text(after,encoding='utf8')"
 new="before=(previous_node/'recovery_worker.py').read_text('utf8');overlay=read(B/'POLICY50_OVERLAY_CONFIG.json');binding=[]\n for change in overlay['changes']:\n  rel=change['relative'];src=B/'overlay'/rel;assert H(src)==change['candidate_SHA'];prior=previous_node/rel;assert H(prior) in (change['baseline_SHA'],change['candidate_SHA']) or rel=='recovery_worker.py';dst=node/rel;shutil.copy2(src,dst);binding.append(change)\n old_policy=previous_spec.get('policy_hz',100);after=(B/'overlay/recovery_worker.py').read_text('utf8').replace(str(overlay['worker_baseline_Adam']),str(newAdam));worker.write_text(after,encoding='utf8');put(node/'POLICY50_OVERLAY_BINDING_ACTUAL.json',dict(changes=binding,source_policy_hz=old_policy,policy_hz=50))"
 assert old in parent;parent=parent.replace(old,new)
 parent=parent.replace("task.update(id=", "task.update(policy_clock_migration_authorized=True,source_policy_hz=old_policy,policy_hz=50,id=")
 parent=parent.replace("shutil.copy2(B/'closed_production_continuation_pending_CPU_v3.py',node/'closed_production_continuation_CPU_v2.py')", "shutil.copy2(B/'policy50_closed_source_CPU_v1.py',node/'closed_production_continuation_CPU_v2.py');shutil.copy2(B/'policy50_native_CPU_v1.py',node/'policy50_native_CPU_v1.py')")
 parent=parent.replace("m.update(source_SHA=", "m.update(policy_hz=50,source_policy_hz=old_policy,source_SHA=")
 parent=parent.replace("'PREVIOUS_CLOSED_WHOLE_MODEL_CPU_REPORT.json'}", "'PREVIOUS_CLOSED_WHOLE_MODEL_CPU_REPORT.json','POLICY50_OVERLAY_BINDING_ACTUAL.json','policy50_native_CPU_v1.py'}")
 parent=parent.replace("spec.update(source_SHA=", "spec.update(policy_hz=50,source_policy_hz=old_policy,source_SHA=")
 parent=parent.replace("CPU_source(node);runid=", "CPU_source(node);qualify_clock_native(node,newspec) if newspec['source_policy_hz']==100 else None;runid=")
 parent=parent.replace("assert not LEASE.exists();fd=os.open", "verify_previous_100hz_series(cfg);assert not LEASE.exists();fd=os.open")
 extra='''
def verify_previous_100hz_series(cfg):
 import psutil
 old=Path(cfg['previous_100hz_controller']);state=read(old/'SERIES_STATE.json');ex=read(old/'SERIES_EXIT_ACTUAL.json');assert ex['status']=='requested_stop_at_boundary' and read(old/'SERIES_CURRENT.json')['active'] is None
 assert not any(p.pid!=os.getpid() and any(x.startswith(str(old.parent)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
 rows=state['completed'];assert len(rows)==len({x['run_id'] for x in rows}) and sum(x['actual_pending_seconds'] for x in rows)==cfg['prior_100hz_series_pending_seconds']
 with (OWNED/'state/MOD4_E3_AUTO_PENDING_SERIES_20261020.json').open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 assert rows[-1]['final']['SHA']==cfg['initial_source']['SHA']
def qualify_clock_native(node,spec):
 import importlib.util
 sp=importlib.util.spec_from_file_location('clock_native_common',node/'three_slot_common_v1.py');common=importlib.util.module_from_spec(sp);sp.loader.exec_module(common)
 sp=importlib.util.spec_from_file_location('clock_native_resource',node/'three_real_gpu_resource_v1.py');res=importlib.util.module_from_spec(sp);sp.loader.exec_module(res);lock=res.acquire(spec,node);p=None
 try:
  p=common.spawn(spec,'native')
  try:rc=p.wait(timeout=850)
  except subprocess.TimeoutExpired:
   put(node/'job0/native/STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='bounded clock qualification timeout; own saved stop'));p.wait();raise
  put(node/'POLICY50_NATIVE_WORKER_WAITED_EXIT_ACTUAL.json',dict(epoch=time.time(),returncode=rc,pid=p.pid,actual_waited=True));assert rc==0 and read(node/'job0/native/FINAL.json')['passed'] and not list((node/'job0/native').glob('*ORIGINAL_ERROR*'))
  run=subprocess.run([PY,'-u','-B',str(node/'policy50_native_CPU_v1.py'),str(node)],capture_output=True,text=True,timeout=120);put(node/'POLICY50_NATIVE_CPU_PROCESS_ACTUAL.json',dict(epoch=time.time(),returncode=run.returncode,stdout=run.stdout,stderr=run.stderr));assert run.returncode==0
 finally:
  if p and p.poll() is None:put(node/'job0/native/STOP_AFTER_SAVE.json',dict(epoch=time.time(),reason='qualification saved stop'));p.wait()
  fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
'''
 parent=parent.replace("if __name__=='__main__':",extra+"\nif __name__=='__main__':");(C/'auto_E3_serial_supervisor_v1.py').write_text(parent,encoding='utf8')
 # Node imports its own current common module; copy controller common into each
 # node after its old controllers, before manifest construction.
 parent=parent.replace("m.update(policy_hz=50", "shutil.copy2(B/'three_slot_common_v1.py',node/'three_slot_common_v1.py')\n m.update(policy_hz=50")
 (C/'auto_E3_serial_supervisor_v1.py').write_text(parent,encoding='utf8')
 before=ast.parse((A/'auto_E3_pending_owner_v2.py').read_text('utf8'));after=ast.parse(owner.read_text('utf8'));fn=lambda tree,name:ast.dump(next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name));assert fn(before,'advance_cost')==fn(after,'advance_cost')
 assert all(ast.parse(p.read_text('utf8')) for p in list(C.glob('*.py'))+list(V.rglob('*.py')))
 put(R/'POLICY50_SERIAL_V2_SOURCE_PREPARED_CPU_ACTUAL.json',dict(epoch=time.time(),passed_source_CPU=True,controller_files={p.name:H(p) for p in C.iterdir() if p.is_file()},overlay=changes,original_advance_cost_AST_exact=True,old_100hz_pending_additional_reserve=True,no_remote_or_GPU=True,not_actual_target_runtime_admission=True))
 print(json.dumps(dict(prepared=True,files=len(list(C.iterdir())),native_protocol='24/192 zero optimizer',deployed=False)))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/('POLICY50_SERIAL_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_remote_or_GPU=True));raise
