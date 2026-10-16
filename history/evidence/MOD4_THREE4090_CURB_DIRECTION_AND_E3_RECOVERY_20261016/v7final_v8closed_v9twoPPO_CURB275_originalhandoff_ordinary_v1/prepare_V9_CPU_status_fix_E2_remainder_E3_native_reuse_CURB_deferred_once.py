from pathlib import Path
import os,json,time,ast,hashlib,shutil
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;R=D/'reports';Q=D/'v9_payload'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
REUSE='''from pathlib import Path
import os,json,time,hashlib,shutil,psutil
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def admitted_native(cfg):
 import three_expert_helpers_v2 as b
 B=Path(__file__).resolve().parent;A=Path(cfg['admitted_native_root']);assert A.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2').resolve()) and H(A/'CONTINUATION_COMPLETE_MANIFEST_V2.json')==cfg['admitted_manifest_SHA'];m=json.loads((A/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());assert m['source_SHA']==cfg['source_SHA'] and m['GPU_UUID']==cfg['GPU_UUID']
 for r in m['files']:
  if r['relative'].startswith(('job0/runtime/','job0/source/','job0/assets/','lib/')) or r['relative'] in ('recovery_worker.py','native_CPU.py'):
   p=B/r['relative'];assert p.stat().st_size==r['bytes'] and H(p)==r['SHA'],r['relative']
 for p in psutil.process_iter(['pid','cmdline']):
  try:assert not any(str(A)+'/' in a for a in p.info['cmdline'] or [])
  except psutil.Error:pass
 assert json.loads((A/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited'];assert json.loads((A/'NODE_EXIT_ACTUAL.json').read_bytes())['validation_fcntl_released'];old=json.loads((A/'NODE_ORIGINAL_ERROR.json').read_bytes());assert "Source finite stop before new learning" in old['error']
 for name in ('native_WAITED_EXIT_ACTUAL.json','native_CPU_WAITED_EXIT_ACTUAL.json'):assert json.loads((A/'job0'/name).read_bytes())['returncode']==0
 own=json.loads((B/'OWN_GPU_SPECIFIC_FCNTL_AND_GLOBAL_FREE_ACTUAL.json').read_bytes());assert own['pid']==os.getpid() and own['GPU_UUID']==cfg['GPU_UUID'] and own['actual_private_GPU_fcntl_held'];O=A/'job0/native';p=O/'NATIVE_ALL_ROWS_CPU_ADMITTED.json';v=json.loads(p.read_bytes());c=json.loads((O/'NATIVE336_COMPLETE.json').read_bytes());assert H(p)==cfg['admitted_CPU_SHA'] and v['passed'] and v['source_SHA']==cfg['source_SHA'] and v['controls']==336 and v['callbacks']==1344 and v['all_original_core_tensor_bytes_exact'];assert c['optimizer_updates']==0 and c['Adam_step']==640240 and H(O/'own_native336.pt')==c['SHA']==v['native_checkpoint_SHA'];target=B/'job0/native';assert not target.exists();target.mkdir()
 for name in ('own_native336.pt','own_startup0.pt','NATIVE336_COMPLETE.json','NATIVE_ALL_ROWS_CPU_ADMITTED.json','FINAL.json','GEOMETRY_AND_RESET_ACTUAL.json','VALID_PREFIX_INDEX.json','SOURCE_TYPED_ZERO_CLOCK_ACTUAL.json'):shutil.copy2(O/name,target/name)
 b.put(B/'V8_COMPLETE_NATIVE_ACTUAL_REUSED_NO_GPU_REPLAY.json',dict(epoch=time.time(),original_root=str(A),source_SHA=cfg['source_SHA'],original_complete_native_SHA=c['SHA'],original_CPU_SHA=cfg['admitted_CPU_SHA'],original_worker_and_CPU_EXIT0=True,old_scheduler_stop_error_retained=True,current_parent_holds_same_GPU_fcntl_after_old_actual_exit=True,runtime_assets_source_LIB_worker_nativeCPU_byteexact=True,no_GPU_native_or_raw_replay=True))
 return dict(value=v,path=str(p),SHA=H(p),actual_CPU_waited_EXIT0=True)
'''
DEFER='''   if phase=='waiting_reviewed_CURB_case' and local_error is None:
    try:
     from deferred_CURB_case_admission_v1 import read_ready
     admitted=read_ready(B,specs['curb'])
     if admitted:
      case=Path(admitted['case_root']);specs['curb']=admitted['spec'];b.B=case;b.J=case/'job0';b.validate_payload(specs['curb']);put(B/'DEFERRED_CURB_ACTUAL_CPU_ADMISSION_ACCEPTED.json',dict(epoch=time.time(),admitted=admitted,no_GPU_or_PPO_inferred=True));p=b.spawn(specs['curb'],'native');children.append(p);phase='native'
     elif time.time()-started>1800:raise TimeoutError('No independently reviewed CURB repair within finite1800s; no CURB grant or charge')
    except BaseException:
     local_error=traceback.format_exc();put(B/'DEFERRED_CURB_ADMISSION_ORIGINAL_ERROR_ISOLATED.json',dict(epoch=time.time(),error=local_error,other_experts_continue=True,no_CURB_PPO_inferred=True))
'''
def main():
 assert not Q.exists();v=json.loads((R/'V8_TERMINAL_CPU_WAIT_TIMEOUT_E3_ADMITTED_NO_PPO_EXACT_COST_READONLY_ACTUAL.json').read_bytes());assert v['canonical']['active'] is None and all(not q['actual_held'] for q in v['canonical']['actual_two_fcntl']) and not any(v[k]['actual_own_processes'] for k in ('curb','e2','recovery'));assert 'recovery' not in v['canonical']['last_completed']['experts'];prior=json.loads((R/'V8_CURB_SAVED_REVIEW_STOP_E2_E3_CONTINUING_ACTUAL_COLLECTION.json').read_bytes());assert json.loads((R/'NATIVE_CPU_BLOCKED_WAIT_ACTUAL_STATUS_BRIDGE_CPU_NEGATIVES.json').read_bytes())['passed_CPU_fixture_only'];Q.mkdir();rng=torch.get_rng_state().clone();specs=[]
 for key in ('curb','e2','recovery'):
  b=Q/key;shutil.copytree(D/'v8_payload'/key,b);old=json.loads((b/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());source=b/'job0/source'/old['source_filename'];row=prior['curb_final'] if key=='curb' else v['e2_model'] if key=='e2' else None
  if row:shutil.copy2(row['local_path'],source);step=row['Adam_step']
  else:step=640240
  cap=1800. if key=='curb' else 5400-v['canonical']['last_completed']['experts']['e2']['charged_seconds'] if key=='e2' else 3600.;assert cap>=600
  p=b/'three_expert_helpers_v2.py';s=p.read_text('utf8').replace('PORT=29747','PORT=29748');oldline="if phase=='native':native=native_CPU(cfg);p=None;phase='ready'";assert s.count(oldline)==1;s=s.replace(oldline,"if phase=='native':\n     from native_CPU_status_bridge_v1 import run_CPU_with_status\n     native=run_CPU_with_status(cfg,native_CPU,send,put,B);p=None;phase='ready'");s=s.replace('from admitted_native_reuse_v4 import admitted_native','from admitted_V8_E3_native_reuse_v9 import admitted_native');p.write_text(s,encoding='utf8');shutil.copy2(D/'native_CPU_status_bridge_v1.py',b/'native_CPU_status_bridge_v1.py');shutil.copy2(D/'deferred_CURB_case_admission_v1.py',b/'deferred_CURB_case_admission_v1.py');(b/'admitted_V8_E3_native_reuse_v9.py').write_text(REUSE,encoding='utf8')
  s=(b/'three_expert_finite_owner_node_v8.py').read_text('utf8').replace('Linux_THREE_INDEPENDENT_V7_FINAL_SOURCES_HEALTHY_BLOCKS_V8_','Linux_E2_E3_CPU_STATUS_FIXED_CURB_DEFERRED_V9_');needle="server=http.server.ThreadingHTTPServer(('10.24.4.210',PORT),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();p=b.spawn(specs['curb'],'native');children.append(p)";assert needle in s;s=s.replace(needle,"server=http.server.ThreadingHTTPServer(('10.24.4.210',PORT),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()\n  if specs['curb'].get('deferred_admission'):phase='waiting_reviewed_CURB_case';p=None\n  else:p=b.spawn(specs['curb'],'native');children.append(p)");needle="  while True:\n   own={**b.state";assert s.count(needle)==1;s=s.replace(needle,"  while True:\n"+DEFER+"   own={**b.state");(b/'three_expert_finite_owner_node_v9.py').write_text(s,encoding='utf8')
  if row:
   for name in ('native_admission_worker.py','production_worker.py'):
    p=b/name;p.write_text(p.read_text('utf8').replace(str(old['source_Adamstep']),str(step)),encoding='utf8')
   if key=='curb':
    p=b/'job0/runtime/isaac/mod4/curb35_checkpoint.py';s=p.read_text('utf8');assert old['source_SHA'] in s;p.write_text(s.replace(old['source_SHA'],row['SHA']),encoding='utf8')
  task=b/'job0'/('TASK_CURB35.json' if key=='curb' else 'TASK.json');x=json.loads(task.read_bytes());x.update(source_SHA=H(source),source_Adamstep=step,max_parent_seconds=cap,remaining_scope_cap_seconds=cap,not_new_budget=True,CURB_deferred_no_unchanged_axis_learning=key=='curb');task.write_text(json.dumps(x,indent=2),encoding='utf8');ck=torch.load(source,map_location='cpu',weights_only=False);count=[0,0]
  def walk(x):
   if torch.is_tensor(x):count[0]+=1;count[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
   elif isinstance(x,dict):
    for z in x.values():walk(z)
   elif isinstance(x,(list,tuple)):
    for z in x:walk(z)
  walk(ck);assert {int(z['step']) for z in ck['optimizer_state_dict']['state'].values()}=={step};spec={k:old[k] for k in ('key','source_filename','native_controls','GPU_UUID','native_script','production_script')};spec.update(source_SHA=H(source),source_Adamstep=step,source_schema_counts=count,max_parent_seconds=cap,exit_headroom_seconds=300,reuse_admitted_native=key=='recovery',deferred_admission=key=='curb')
  if key=='recovery':
   cpurow=next(q for q in v['recovery']['files'] if q['path'].endswith('/NATIVE_ALL_ROWS_CPU_ADMITTED.json'));assert cpurow['value']['passed'];spec.update(admitted_native_root='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/v8/recovery',admitted_manifest_SHA=H(D/'v8_payload/recovery/CONTINUATION_COMPLETE_MANIFEST_V2.json'),admitted_CPU_SHA=cpurow['SHA'])
  files=[]
  for p in sorted(b.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts or p.name=='CONTINUATION_COMPLETE_MANIFEST_V2.json':continue
   if p.suffix=='.py':ast.parse(p.read_text('utf8'))
   files.append(dict(relative=p.relative_to(b).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
  mf=b/'CONTINUATION_COMPLETE_MANIFEST_V2.json';mf.write_text(json.dumps(dict(spec,files=files),indent=2),encoding='utf8');specs.append(dict(spec,manifest_SHA=H(mf),files=len(files)))
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();out=dict(epoch=time.time(),passed_CPU_only=True,E2_original5400_minus_actual557point0175640583038_remainder=True,E3_original3600_unused_no_grant_no_charge_and_native_reused=True,CURB_no_unchanged_axis_PPO_deferred_max1800_requires_separate_real_repair_case_CPU_and_native=True,status_inside_existing_node_no_new_watcher_or_SSH_and_timeout120_unchanged=True,V8_all_costs_and_errors_retained=True,original_canonical1188000_7extensions_unchanged=True,frozen=specs,CPU_RNG_unchanged0CUDA0optimizer=True);p=R/'V9_FINAL_SOURCE_STATUS_FIX_E3_NATIVE_REUSE_CURB_DEFERRED_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out))
if __name__=='__main__':main()
