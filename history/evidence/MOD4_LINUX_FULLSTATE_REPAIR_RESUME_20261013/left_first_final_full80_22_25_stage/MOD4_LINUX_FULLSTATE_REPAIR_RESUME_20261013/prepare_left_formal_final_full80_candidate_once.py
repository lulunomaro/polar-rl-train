"""Independent final CPU review and unchanged-backend frozen80 candidate assembly."""
from pathlib import Path
import json,time,hashlib,shutil,zipfile,ast,torch
from left_exploration_resume_contract_v1 import same,KEY
D=Path(__file__).resolve().parent;W=D.parent;OLD=W/'MOD4_3060_FULL80_FROZEN_CURRENT_20261014';P=W/'MOD4_3060_LEFT_REPAIR_FULL80_20261014'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
j=json.loads((D/'reports/LEFT_FORMAL_FINAL_ACTUAL_COLLECTION.json').read_bytes());v=j['actual_remote_review'];assert j['passed'] and v['actual_parent_child_guardian_exit_twofcntlFree_idle']
row=j['collected_files'][0];source=Path(row['local_path']);assert H(source)==v['own_checkpoint']['sha256']=='2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971'
c=torch.load(source,map_location='cpu',weights_only=False);s=torch.load(D/'left_fresh_retained_postexit_actual/4_model_own_repaired0PPO.pt',map_location='cpu',weights_only=False)
assert c['E1_terrain_state']['num_envs']==20000 and same(c[KEY],s[KEY])
delta=[float(c['optimizer_state_dict']['state'][i]['step'])-float(s['optimizer_state_dict']['state'][i]['step']) for i in range(17)];assert delta==[3780.]*17 and v['saved_updates']==189
assert sum(not torch.equal(x,s['actor_state_dict'][k]) for k,x in c['actor_state_dict'].items())==9
def walk(x):
 if isinstance(x,torch.Tensor):yield x
 elif isinstance(x,dict):
  for z in x.values():yield from walk(z)
 elif isinstance(x,(tuple,list)):
  for z in x:yield from walk(z)
f=[x for x in walk(c) if x.is_floating_point()];assert len(f)==107 and all(bool(torch.isfinite(x).all()) for x in f) and not torch.cuda.is_initialized()
assert not P.exists();P.mkdir();(P/'reports').mkdir();Q=P/'payload'
shutil.copytree(OLD/'payload',Q,ignore=shutil.ignore_patterns('__pycache__','model_32411_17b.pt'))
own=Q/'source/model_32635_left_repair.pt';shutil.copy2(source,own);assert H(own)==H(source)
worker=Q/'paired_full80_parameter_bound_v2.py';old=worker.read_text();new=old.replace('1aa77fa8e9d9813fcd3c722e249ebf3a755e1817e970f17955dd54fbcc1cff06',H(source)).replace('MOD4_3060_FULL80_FROZEN_CURRENT_20261014',P.name);compile(new,str(worker),'exec');worker.write_text(new,encoding='utf8')
assert H(Q/'full80_runtime_native_v1.py')==H(OLD/'payload/full80_runtime_native_v1.py')=='f8373bb6bce14c8e39e243e1e4ea9b88542b4033d5dc8f6b1c15eb95d1ddd0cc'
# Only identity literals in the worker change; every instruction of the physical runtime is byteexact.
manifest=Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json';previous=json.loads(manifest.read_bytes());rows=[]
for p in sorted(Q.rglob('*')):
 if p.is_file() and p!=manifest and '__pycache__' not in p.parts:rows.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,sha256=H(p)))
previous.update(file_rows=rows,actual_candidate_final_source_SHA=H(source),actual_final_updates189=True,previous_manifest_SHA=H(OLD/'payload/REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json'),new_scope_policy_only_frozen_no_PPO=True)
manifest.write_text(json.dumps(previous,indent=2),encoding='utf8')
archive=P/'FULL80_FROZEN1500_SOURCE_V1.zip'
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
 for p in sorted(Q.rglob('*')):
  if p.is_file() and '__pycache__' not in p.parts:z.write(p,p.relative_to(Q).as_posix())
prep=dict(epoch=time.time(),CPU_prepared=True,source_SHA=H(source),source_own_final=source.as_posix(),whole20k_full107finite=True,actor9changed_Adam3780_actual=True,final_actual_saved_updates=189,actual_training_fulltrace_review_receipt=max((D/'reports').glob('LEFT_FORMAL_FINAL_FULLTRACE_CPU_ACTUAL_*.json')).as_posix(),worker=dict(path=str(worker),sha256=H(worker)),runtime=dict(path=str(Q/'full80_runtime_native_v1.py'),sha256=H(Q/'full80_runtime_native_v1.py')),manifest=dict(path=str(manifest),sha256=H(manifest)),package=dict(path=str(archive),bytes=archive.stat().st_size,sha256=H(archive)),original_full80_backend_native_and_physical_scope_SHA_reused=True,only_new_frozen_policy_source_and_namespace=True,full1500_GPU_NOT_launched=True,qualified50=False)
(P/'reports/FULL80_NATIVE_CPU_PORT_PREPARED_ACTUAL.json').write_text(json.dumps(prep,indent=2),encoding='utf8')
script=(OLD/'deploy_full80_frozen1500_unique_once.py').read_text().replace(OLD.name,P.name).replace('native3060_Linux20k_final_full80_frozen1500_v1','native3060_left_repair_final_full80_frozen1500_v1').replace('MOD4_Linux20kFinalFull80Frozen_20261014_Frozen1500_v1','MOD4_LeftRepairFinalFull80_20261014_Frozen1500_v1').replace('1aa77fa8e9d9813fcd3c722e249ebf3a755e1817e970f17955dd54fbcc1cff06',H(source)).replace('source/model_32411_17b.pt','source/model_32635_left_repair.pt')
assert 'model_32411_17b.pt' not in script
script=script.replace("assert finite(source)==107 and source['E1_terrain_state']['num_envs']==20000 and len(source['actor_state_dict'])==9", "assert finite(source)==107 and source['E1_terrain_state']['num_envs']==20000 and len(source['actor_state_dict'])==9\nassert source['LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION']['profile']=='left_initial_joint_margin014_std1_v1'")
q=P/'deploy_left_repair_final_full80_unique_once.py';compile(script,str(q),'exec');q.write_text(script,encoding='utf8')
for n in ('collect_full80_frozen1500_readonly.py','review_full80_full1500_CPU_actual.py','review_full80_original_route_prefix_CPU_actual.py'):
 a=(OLD/n).read_text().replace(OLD.name,P.name).replace('native3060_Linux20k_final_full80_frozen1500_v1','native3060_left_repair_final_full80_frozen1500_v1').replace('1aa77fa8e9d9813fcd3c722e249ebf3a755e1817e970f17955dd54fbcc1cff06',H(source))
 compile(a,str(P/n),'exec');(P/n).write_text(a,encoding='utf8')
q=D/'reports/LEFT_FORMAL_FINAL_LOCAL_CPU_AND_FROZEN80_CANDIDATE_PREPARED.json';assert not q.exists();q.write_text(json.dumps(dict(epoch=time.time(),passed=True,own_final_source=row,whole107finite=True,actor9changed_Adam3780=True,updates=189,envsteps=90720000,thirteen_CPUCUDA_sameidentity_verified=True,actual_parent_unique_seconds=v['exit']['parent_load_learn_save_exit_seconds'],actual_exit_idle=True,candidate_preparation=prep,new_GPUcase_not_yet_dispatched=True,qualified50=False),indent=2),encoding='utf8');print(json.dumps(dict(report=str(q),sourceSHA=H(source),package_bytes=archive.stat().st_size,next_unique_deployment=str(P/'deploy_left_repair_final_full80_unique_once.py'))))
