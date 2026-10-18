"""Restore actual E3closed85/native336, one-hour controls, and the existing three-slot accounting."""
from pathlib import Path
import os,sys,json,time,hashlib,shutil,ast,copy,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';M=W/'MOD4_RECOVERY_CLOSED_FINAL_H1_STORAGE_BOUNDED_HANDOFF_20261017';H2=W/'MOD4_POST_POWER_RESTORE_H1_SATURATION_REPAIR_20261018/hour2_h1_fe778_v1';Q=B/'payload/recovery';C=B/'controllers';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def digest(rows):return hashlib.sha256(json.dumps([(x['relative'],x['bytes'],x['SHA']) for x in rows if x['relative'].startswith(('job0/runtime/','job0/assets/','lib/'))],sort_keys=True).encode()).hexdigest()
def main():
 assert not Q.exists() and not C.exists();C.mkdir();base=H2/'payload/h1'
 common=(base/'three_slot_common_v1.py').read_text('utf8').replace("'e2':3600,'recovery':3600","'e2':3900,'recovery':3900").replace("'e2':'GPU-16828f91-2b45-b646-8dc0-9481138e2842'","'e2':'GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'");assert "CAPS={'h1':3900,'e2':3900,'recovery':3900}" in common;(C/'three_slot_common_v1.py').write_text(common,'utf8');shutil.copy2(base/'three_slot_finite_owner_v1.py',C/'three_slot_finite_owner_v1.py');shutil.copy2(base/'native_CPU_status_bridge_v1.py',C/'native_CPU_status_bridge_v1.py');shutil.copy2(base/'owner_listener_ready_cpu_reviewed_v1.py',C/'owner_listener_ready_cpu_reviewed_v1.py')
 node=(base/'three_slot_finite_node_v1.py').read_text('utf8').replace('from three_slot_resource_v1 import acquire','from three_real_gpu_resource_v1 import acquire');needle="  p=b.spawn(spec,'native');children.append(p);phase='native'";assert needle in node;node=node.replace(needle,"  if spec.get('reuse_completed_native'):\n   from admitted_existing_same_source_native_CPU_v1 import load\n   native=load(spec,B);phase='ready'\n  else:\n   p=b.spawn(spec,'native');children.append(p);phase='native'");(C/'three_slot_finite_node_v1.py').write_text(node,'utf8')
 for name in ('three_real_gpu_resource_v1.py','admitted_existing_same_source_native_CPU_v1.py'):shutil.copy2(B/name,C/name)
 shutil.copytree(M/'payload/recovery',Q,ignore=shutil.ignore_patterns('__pycache__','*.pyc','migrate_saved_reward.py'));oldm=json.loads((Q/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());assert oldm['source_Adamstep']==657660
 record=json.loads((M/'reports/M_CLOSED24_H1_FINAL_RECOVERY85_NATIVE_COMPLETE_ORIGINAL_HANDOFF_1657_BOUND_ACTUAL.json').read_bytes());rows=record['recovery']['files'];get=lambda suffix:next(x['value'] for x in rows if x['path'].endswith(suffix));original_cpu=get('/job0/native/NATIVE_ALL_ROWS_CPU_ADMITTED.json');final=get('/NATIVE_ONLY_FINAL_ACTUAL.json');assert original_cpu['passed'] and final['actual_GPU_worker_EXIT0'];pt=record['downloaded_models']['recovery_native'];assert pt['twohost_complete_SHA'] and Path(pt['local_path']).stat().st_size==pt['bytes'];(Q/'job0/native').mkdir();shutil.copy2(pt['local_path'],Q/'job0/native/own_native336.pt');(Q/'job0/native/NATIVE336_COMPLETE.json').write_text(json.dumps(dict(SHA=pt['SHA'],path=pt['path'],source_SHA=oldm['source_SHA'],controls=336,callbacks=1344,original_native_metadata_indexed_not_replayed=True),indent=2),'utf8')
 worker=Q/'recovery_worker.py';s=worker.read_text('utf8');oldworker=H(worker);tree=ast.parse(s);branch=next(n for n in ast.walk(tree) if isinstance(n,ast.If) and isinstance(n.test,ast.Name) and n.test.id=='native' and any(isinstance(x,ast.For) for x in n.body if isinstance(x,ast.For))) if False else None
 s=s.replace('import argparse,os,sys,time,json,hashlib,traceback,runpy','import argparse,os,sys,time,json,hashlib,traceback,runpy,shutil').replace("stop=time.time()>=deadline or", "stop=shutil.disk_usage(B).free<8*1024**3 or time.time()>=deadline or");ast.parse(s);worker.write_text(s,'utf8');task=Q/'job0/TASK.json';t=json.loads(task.read_bytes());t.update(GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',max_parent_seconds=3900,exit_headroom_seconds=300);task.write_text(json.dumps(t,indent=2),'utf8')
 def native_branches(text):return [ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(text)) if isinstance(n,ast.If) and isinstance(n.test,ast.Name) and n.test.id=='native' and any(isinstance(x,ast.Return) for x in n.body)]
 assert native_branches((M/'payload/recovery/recovery_worker.py').read_text('utf8'))==native_branches(s)
 os.environ['CUDA_VISIBLE_DEVICES']='';import torch;torch.set_num_threads(2);rng=torch.get_rng_state().clone();src=torch.load(Q/'job0/source/E0_full_source.pt',map_location='cpu',weights_only=False);n=torch.load(Q/'job0/native/own_native336.pt',map_location='cpu',weights_only=False)
 def exact(a,b):
  if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and a.contiguous().numpy().tobytes()==b.contiguous().numpy().tobytes()
  if isinstance(a,dict):return a.keys()==b.keys() and all(exact(v,b[k]) for k,v in a.items())
  if isinstance(a,(list,tuple)):return type(a)==type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
  return a==b
 for key in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert exact(src[key],n[key])
 def finite(x):
  if torch.is_tensor(x):assert not x.is_floating_point() or torch.isfinite(x).all()
  elif isinstance(x,dict):
   for v in x.values():finite(v)
  elif isinstance(x,(tuple,list)):
   for v in x:finite(v)
 finite(src);finite(n);assert {int(v['step']) for v in n['optimizer_state_dict']['state'].values()}=={657660};assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 for p in C.iterdir():shutil.copy2(p,Q/p.name)
 for p in Q.rglob('*.py'):ast.parse(p.read_text('utf8'))
 (Q/'REUSED_ORIGINAL_NATIVE_ALL_ROWS_CPU_REPORT.json').write_text(json.dumps(original_cpu,indent=2),'utf8');cpuSHA=H(Q/'REUSED_ORIGINAL_NATIVE_ALL_ROWS_CPU_REPORT.json');assert cpuSHA==final['native_CPU']['SHA'];runtime_digest=digest(oldm['files']);proof=dict(key='recovery',source_SHA=oldm['source_SHA'],GPU_UUID=t['GPU_UUID'],execution_backend='target72',Adam=657660,controls=336,callbacks=1344,original_native_runtime_assets_digest=runtime_digest,CPU_report_SHA=cpuSHA,native_PT=pt,actual_native_worker_EXIT0=True,actual_CPU_waited_EXIT0=True,old_native_branch_same_or_whole_worker_exact=True,old_worker_filename='recovery_worker.py',old_worker_SHA=oldworker,root='/home/lc01/Zonglin Li/zonglin2/tasks/T3_1710v10hr/recovery');(Q/'ADMITTED_NATIVE_REUSE_PROVENANCE.json').write_text(json.dumps(proof,indent=2),'utf8')
 m=dict(oldm,max_parent_seconds=3900,training_seconds_before_save=3600,native_runtime_assets_digest=runtime_digest,strict_reuse_only_actual_same_source_backend_GPU_native=True);m['files']=[dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(Q.rglob('*')) if p.is_file() and p.name!='THREE_SLOT_COMPLETE_MANIFEST_V1.json' and '__pycache__' not in p.parts];assert digest(m['files'])==runtime_digest;mf=Q/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';mf.write_text(json.dumps(m,indent=2),'utf8')
 put('E3_EXISTING_NATIVE336_REUSE_AND_THREE_HOUR_CONTROLLERS_CPU_PREPARED_ACTUAL.json',dict(epoch=time.time(),passed=True,source_SHA=m['source_SHA'],source_Adam657660=True,source_native_actor9_STD_critic8_17Adam_literalexact=True,all_model_runtime_finite=True,native_complete=pt,native_CPU_SHA=cpuSHA,reuse_proof=proof,manifest=dict(path=str(mf),bytes=mf.stat().st_size,SHA=H(mf)),one_original_writer_and_three_distinct_GPUs=True,all_GO_to_save3600_plus300=True,no_current_H1_hotpatch_or_stop=True,no_new_PPO_reward_LR_STD_physics_command_or_totalbudget=True));print(json.dumps(dict(E3_ready_CPU=True,native_replayed=False,source_SHA=m['source_SHA'],files=len(m['files']))),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('E3_THREE_HOUR_PREPARER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_runtime_mutation=True));raise
