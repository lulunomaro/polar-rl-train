from pathlib import Path
import os,sys,json,time,hashlib,ast,shutil
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;R=D/'reports';Q=D/'v4_payload';V3=D/'recovery_receipt_schema_v3'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
REUSE='''from pathlib import Path
import json,time,hashlib,os,fcntl
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def admitted_native(cfg):
 import three_expert_helpers_v2 as b
 import psutil,shutil
 B=Path(__file__).resolve().parent;A=Path(cfg['admitted_native_root']);assert A.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2'));assert H(A/'CONTINUATION_COMPLETE_MANIFEST_V2.json')==cfg['admitted_base_manifest_SHA'];m=json.loads((A/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes())
 for r in m['files']:
  if r['relative'].startswith(('job0/runtime/','job0/source/','job0/assets/','lib/')) or r['relative'] in ('recovery_worker.py','native_CPU.py'):
   p=B/r['relative'];assert p.is_file() and p.stat().st_size==r['bytes'] and H(p)==r['SHA'],r['relative']
 started=time.time()
 while not (A/'PARENT_EXIT_ACTUAL.json').exists():
  assert time.time()-started<1800;b.send(cfg,dict(key=cfg['key'],phase='waiting_admitted_own_native',original_native_root=str(A),manifest_SHA=cfg['manifest_SHA']));time.sleep(3)
 final=json.loads((A/'PARENT_FINAL.json').read_bytes());assert final['passed_native_CPU'] and final['PPO_updates']==0;identity=json.loads((A/'PARENT_IDENTITY.json').read_bytes());process=None
 try:process=psutil.Process(identity['pid'])
 except psutil.Error:pass
 assert process is None or abs(process.create_time()-identity['creation'])>.1,'Native parent has not actually exited'
 for n in ('WORKER_EXIT_ACTUAL.json','CPU_ACTUAL_EXIT.json'):assert json.loads((A/n).read_bytes())['returncode']==0
 oldlock=Path('/home/lc01/Zonglin Li/zonglin2/state/recovery_schema_v3_gpu1.lock')
 with oldlock.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 O=A/'job0/native';native=json.loads((O/'NATIVE_ALL_ROWS_CPU_ADMITTED.json').read_bytes());complete=json.loads((O/'NATIVE336_COMPLETE.json').read_bytes());assert native['passed'] and native['source_SHA']==cfg['source_SHA'] and native['controls']==336 and native['callbacks']==1344;assert H(Path(complete['path']))==complete['SHA']==native['native_checkpoint_SHA'];target=B/'job0/native';assert not target.exists();target.mkdir()
 for name in ('own_native336.pt','own_startup0.pt','NATIVE336_COMPLETE.json','NATIVE_ALL_ROWS_CPU_ADMITTED.json','FINAL.json','GEOMETRY_AND_RESET_ACTUAL.json','VALID_PREFIX_INDEX.json','SOURCE_TYPED_ZERO_CLOCK_ACTUAL.json'):shutil.copy2(O/name,target/name)
 assert H(target/'own_native336.pt')==native['native_checkpoint_SHA'];b.put(B/'ADMITTED_NATIVE_REUSE_ACTUAL.json',dict(epoch=time.time(),original_root=str(A),original_native_CPU_SHA=H(O/'NATIVE_ALL_ROWS_CPU_ADMITTED.json'),saved_complete_SHA=native['native_checkpoint_SHA'],runtime_assets_source_LIB_bytes_exact=True,actual_original_parent_child_and_CPU_out=True,actual_original_gpu1_fcntl_free=True,no_native_GPU_or_raw_replay=True,raw_indexes_keep_actual_original_paths=True))
 return dict(value=native,path=str(O/'NATIVE_ALL_ROWS_CPU_ADMITTED.json'),SHA=H(O/'NATIVE_ALL_ROWS_CPU_ADMITTED.json'),actual_CPU_waited_EXIT0=True)
'''
def main():
 assert not Q.exists();v=json.loads((R/'V2_TWO_REAL_PPO_COMPLETE_SAFE_HANDOFF_MODELS_AND_CANONICAL_ACTUAL.json').read_bytes());assert v['canonical']['active'] is None and len(v['canonical']['actual_two_fcntl_free'])==2 and not v['curb']['actual_own_processes'] and not v['e2']['actual_own_processes'];rng=torch.get_rng_state().clone();Q.mkdir();specs=[]
 for key in ('curb','e2','recovery'):
  b=Q/key;shutil.copytree(V3 if key=='recovery' else D/'v2_payload'/key,b);p=b/'three_expert_helpers_v2.py';helper=p.read_text('utf8').replace('PORT=29744','PORT=29745');old="put(B/'NODE_IDENTITY.json',ident(os.getpid()));p=spawn(cfg,'native');children.append(p);phase='native'";assert old in helper
  helper=helper.replace(old,"put(B/'NODE_IDENTITY.json',ident(os.getpid()))\n  if cfg.get('reuse_admitted_native'):\n   from admitted_native_reuse_v4 import admitted_native\n   native=admitted_native(cfg);phase='ready';p=None\n  else:p=spawn(cfg,'native');children.append(p);phase='native'")
  p.write_text(helper,encoding='utf8');shutil.copy2(D/'three_expert_finite_owner_node_v2.py',b/'three_expert_finite_owner_node_v4.py');p=b/'three_expert_finite_owner_node_v4.py';s=p.read_text('utf8').replace('Linux_THREE_INDEPENDENT_CURB_APPROACH_E2_RECOVERY_V2_','Linux_THREE_INDEPENDENT_SAFE_HANDOFF_REMAINDERS_V4_');p.write_text(s,encoding='utf8');(b/'admitted_native_reuse_v4.py').write_text(REUSE,encoding='utf8')
  if key in ('curb','e2'):
   row=v[key+'_model'];source=b/'job0/source'/('CURB140.pt' if key=='curb' else 'E2_final58.pt');shutil.copy2(row['local_path'],source);step=row['Adam_step'];priorstep=666160 if key=='curb' else 643760;cost=v['canonical']['last_completed']['experts'][key]['charged_seconds'];cap=(2700-240.26786017417908-cost) if key=='curb' else 2700-cost;assert cap>600
   for name in ('native_admission_worker.py','production_worker.py'):
    p=b/name;s=p.read_text('utf8').replace(str(priorstep),str(step))
    if key=='e2' and name=='production_worker.py':s=s.replace("go['max_parent_seconds']==2700","go['max_parent_seconds']==task['remaining_scope_cap_seconds']")
    p.write_text(s,encoding='utf8')
   if key=='curb':
    p=b/'job0/runtime/isaac/mod4/curb35_checkpoint.py';s=p.read_text('utf8').replace('17d2cb751577441d06b45b7db6182c9addfd6b77fc219cb2c5fd3dcce9c35d23',row['SHA']);p.write_text(s,encoding='utf8')
   p=b/'job0'/('TASK_CURB35.json' if key=='curb' else 'TASK.json');task=json.loads(p.read_bytes());task.update(source_SHA=row['SHA'],source_Adamstep=step,remaining_scope_cap_seconds=cap,cooperative_saved_handoff_completed_not_rollback=True,previous_actual_charged_seconds=cost);p.write_text(json.dumps(task,indent=2),encoding='utf8')
  else:source=b/'job0/source/E0_full_source.pt';step=639560;cap=1800.
  ck=torch.load(source,map_location='cpu',weights_only=False);count=[0,0]
  def walk(x):
   if torch.is_tensor(x):count[0]+=1;count[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
   elif isinstance(x,dict):
    for z in x.values():walk(z)
   elif isinstance(x,(list,tuple)):
    for z in x:walk(z)
  walk(ck);assert len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8 and len(ck['optimizer_state_dict']['state'])==17 and {int(z['step']) for z in ck['optimizer_state_dict']['state'].values()}=={step};spec=dict(key=key,source_SHA=H(source),source_Adamstep=step,source_schema_counts=count,source_filename=source.name,native_controls=336 if key=='recovery' else 144,max_parent_seconds=cap,exit_headroom_seconds=300,GPU_UUID='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e' if key=='curb' else 'GPU-16828f91-2b45-b646-8dc0-9481138e2842' if key=='e2' else 'GPU-c27eecbd-6838-7290-1cd2-37e34522213d',native_script='recovery_worker.py' if key=='recovery' else 'native_admission_worker.py',production_script='recovery_worker.py' if key=='recovery' else 'production_worker.py',reuse_admitted_native=key=='recovery')
  if key=='recovery':spec.update(admitted_native_root='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/recovery_receipt_schema_v3',admitted_base_manifest_SHA=H(V3/'CONTINUATION_COMPLETE_MANIFEST_V2.json'))
  files=[]
  for p in sorted(b.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts or p.name=='CONTINUATION_COMPLETE_MANIFEST_V2.json':continue
   if p.suffix=='.py':ast.parse(p.read_text('utf8'))
   files.append(dict(relative=p.relative_to(b).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
  mf=b/'CONTINUATION_COMPLETE_MANIFEST_V2.json';mf.write_text(json.dumps(dict(spec,files=files),indent=2),encoding='utf8');specs.append(dict(spec,manifest_SHA=H(mf),files=len(files)))
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();out=dict(epoch=time.time(),passed_CPU_only=True,original_all_own_V2_save_exit_and_original_canonical_settled=True,V1_CURB_cost240point267860_plus_V2_actual_subtracted_from_original_same2700=True,E2_V2_actual_subtracted_from_original_same2700=True,no_refund_extra_budget_or_old_GPU_replay=True,E3_original_admitted_native_only_conditional_reuse_no_false_pass=True,three_source_fullmodel_finite_and_17Adam_original_preserved=True,frozen=specs,CPU_RNG_unchanged0CUDA0optimizer=True);(R/'V4_THREEWAY_SAFE_HANDOFF_REMAINDER_MANIFEST_AND_CONDITIONAL_NATIVE_REUSE_CPU_ACTUAL.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out))
if __name__=='__main__':main()
