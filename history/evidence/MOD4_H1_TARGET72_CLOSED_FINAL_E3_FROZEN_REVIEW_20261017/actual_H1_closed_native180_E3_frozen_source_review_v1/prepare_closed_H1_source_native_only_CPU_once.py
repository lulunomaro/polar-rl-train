"""Next full source/backend admission only, no new learning grant or canonical writer."""
from pathlib import Path
import os,sys,json,time,shutil,hashlib,ast,types,importlib.util,tempfile,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;O=W/'MOD4_H1_CLOSED24_TARGET72_SAME_SCOPE_FINITE_20261017';M=W/'MOD4_RECOVERY_CLOSED_FINAL_H1_STORAGE_BOUNDED_HANDOFF_20261017';Q=B/'payload_h1_native';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 proof=json.loads((R/'TARGET72_H1_COMPLETE_CLOSED_FINAL_FULL_CPU_COST_EXIT_ORIGINAL_HANDOFF_ACTUAL.json').read_bytes());assert proof['passed_whole_final_model_local_CPU'] and proof['actual_duration_bound_passed'];assert not Q.exists();shutil.copytree(O/'payload/h1',Q,ignore=shutil.ignore_patterns('THREE_SLOT_COMPLETE_MANIFEST_V1.json','__pycache__'));oldmf=json.loads((O/'payload/h1/THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());shutil.copy2(O/'payload/h1/THREE_SLOT_COMPLETE_MANIFEST_V1.json',Q/'PREVIOUS_TARGET72_SOURCE24_MANIFEST_HISTORICAL.json');step=proof['all17Adam_after'];row=proof['complete_final'];shutil.copy2(row['local_path'],Q/'job0/source/H1_final10_protected.pt');assert H(Q/'job0/source/H1_final10_protected.pt')==row['SHA'];edits=[]
 for name in ('h1_prelaunch_v2_production_worker_v1.py','review_H1_prelaunch_v2_native_allrows_CPU_v1.py'):
  p=Q/name;old=p.read_text('utf8');assert '644180' in old;s=old.replace('644180',str(step));p.write_text(s,encoding='utf8');edits.append(dict(path=name,old_SHA=hashlib.sha256(old.encode()).hexdigest(),new_SHA=H(p),only_source_Adam_expectation_and_reader_label=True))
 parent=(M/'recovery_source85_native_only_finite_parent_v1.py').read_text('utf8');parent=parent.replace("spec['key']=='recovery'","spec['key']=='h1'").replace("state['final']['passed']","state['final']['passed_worker_not_independent_CPU']").replace('controls336_callbacks1344=True','controls180_callbacks720=True').replace('not_frozen_selfrescue_skill_qualification=True','not_frozen_jump_skill_qualification=True');ast.parse(parent);(Q/'H1_closed_target72_native_only_parent_v1.py').write_text(parent,encoding='utf8');(B/'H1_closed_target72_native_only_parent_v1.py').write_text(parent,encoding='utf8')
 task=json.loads((Q/'job0/TASK.json').read_bytes());task.update(id='H1_CLOSED_TARGET72_SOURCE24_NATIVE_ONLY_REVIEW_20261017',source_SHA=row['SHA'],source_Adamstep=step,exact_closed_source_owned_updates=proof['updates'],native_only_no_production_GO_or_canonical=True,newsource_native180_required=True);(Q/'job0/TASK.json').write_text(json.dumps(task,indent=2),encoding='utf8');files=[]
 for p in sorted(x for x in Q.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.py':ast.parse(p.read_text('utf8'))
  files.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
 immutable=[x for x in oldmf['files'] if x['relative'].startswith(('lib/','job0/runtime/','job0/assets/','job0/original_run_manifest.json'))];assert all(H(Q/x['relative'])==x['SHA'] for x in immutable)
 mf=dict(oldmf,source_SHA=row['SHA'],source_Adamstep=step,files=files,native_only_no_PPO_or_canonical_permission=True);(Q/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(mf,indent=2),encoding='utf8');spec=json.loads((O/'reports/H1_CLOSED24_TARGET72_SAME_SCOPE_PAYLOAD_FULL_CPU_PREPARED_ACTUAL.json').read_bytes())['specs']['h1'];spec.update(source_SHA=row['SHA'],source_Adamstep=step,manifest_SHA=H(Q/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),previous_runtime_root='/home/lc01/Zonglin Li/zonglin2/tasks/H124_1710b72',role='native_only')
 # Exercise actual parent function with mocked worker/CPU/lock only; no OS/GPU proof.
 results=[]
 for kind in ('passed','GPU_bad_final','CPU_failed','CPU_wrongsource'):
  temp=Path(tempfile.mkdtemp(prefix='mod4_H1_nativeonly_parent_CPU_'));written={};calls=[]
  class Lock:
   def fileno(self):return 19
   def close(self):calls.append('close')
  class Child:
   returncode=0;pid=9876
   def poll(self):return 0
   def wait(self):calls.append('wait');return 0
  child=Child();mock=types.ModuleType('fcntl');mock.LOCK_UN=8;mock.flock=lambda *a:calls.append('unlock');sys.modules['fcntl']=mock;b=types.ModuleType('three_slot_common_v1');b.put=lambda p,v:written.__setitem__(Path(p).name,v);b.ident=lambda pid:dict(pid=pid);b.validate_payload=lambda s:None;b.spawn=lambda s,phase:(calls.append(phase) or child);b.state=lambda *a:dict(final=dict(passed_worker_not_independent_CPU=kind!='GPU_bad_final'),errors=[]);b.native_CPU=lambda s:dict(actual_CPU_waited_EXIT0=kind!='CPU_failed',value=dict(passed=kind!='CPU_failed',source_SHA='wrong' if kind=='CPU_wrongsource' else spec['source_SHA']));b.outdir=lambda phase:temp;sys.modules['three_slot_common_v1']=b;resource=types.ModuleType('three_slot_resource_v1');resource.acquire=lambda *a:Lock();sys.modules['three_slot_resource_v1']=resource;ns=dict(__file__=str(temp/'parent.py'),__name__='CPU_parent_fixture');exec(compile(parent,'actual_new_H1_parent_CPU_fixture','exec'),ns)
  try:ns['run'](spec)
  except RuntimeError:assert kind!='passed'
  else:assert kind=='passed'
  assert 'production' not in calls and 'wait' in calls and 'unlock' in calls and 'close' in calls and written['NATIVE_ONLY_PARENT_EXIT_ACTUAL.json']['passed_native_CPU']==(kind=='passed');results.append(dict(case=kind,actual_parent_function_exercised=True,calls=calls,original_error_preserved=kind!='passed'))
 save('CLOSED_H1_NEW_SOURCE_TARGET72_NATIVE_ONLY_PAYLOAD_AND_PARENT_CPU_PREPARED_ACTUAL.json',dict(epoch=time.time(),passed_CPU_static_source_and_actual_mock_parent_flow=True,source_closed_final=proof,spec=spec,parent_file='H1_closed_target72_native_only_parent_v1.py',parent_SHA=H(B/'H1_closed_target72_native_only_parent_v1.py'),changes=edits,original_runtime_physics_reward_command_DR_hardware_bytes_exact=True,mock_parent_positive_and3negative=results,mock_not_actual_OS_GPU_SDK=True,new_learning_GO_or_budget_permission=False,native_only180_720_allrowCPU_required=True,real_GPU_native_not_yet=True));print(json.dumps(dict(native_only_payload_CPU=True,source_Adam=step,source_SHA=row['SHA'],new_paid_learning=False)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:save('H1_NEW_NATIVEONLY_PAYLOAD_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_remote_or_GPU=True));raise
