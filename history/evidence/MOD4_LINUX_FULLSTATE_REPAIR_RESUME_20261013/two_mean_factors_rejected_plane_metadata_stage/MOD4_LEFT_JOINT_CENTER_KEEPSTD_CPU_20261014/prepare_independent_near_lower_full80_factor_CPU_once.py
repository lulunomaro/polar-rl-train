"""Prepare a frozen factor only. Does not start GPU or make a training source."""
from pathlib import Path
import json,shutil,hashlib,zipfile,time,ast,torch
D=Path(__file__).resolve().parent;W=D.parent;OLD=W/'MOD4_3060_LEFT_REPAIR_FULL80_20261014';P=W/'MOD4_3060_LEFT_NEAR_LOWER_FULL80_FACTOR_20261014'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=json.loads((D/'candidate_near_lower_cpu_v1/CANDIDATE_NEAR_LOWER_CPU_PREPARED_MANIFEST.json').read_bytes());source=Path(m['candidate']['path']);SHA=m['candidate']['sha256'];assert H(source)==SHA=='6235d44aa144a73e46d8326187c7fdf1e406a2d0b00ee6d21922b18f198f3bce'
assert m['CPU_counts']==dict(tensors=195,floating_finite=107,perenv=99,saved_envs=20000)
c=torch.load(source,map_location='cpu',weights_only=False);assert c[m['new_private_KEY']]['profile']==m['profile']
assert c['E1_terrain_state']['num_envs']==20000 and not torch.cuda.is_initialized()
assert not P.exists();P.mkdir();(P/'reports').mkdir();Q=P/'payload'
shutil.copytree(OLD/'payload',Q,ignore=shutil.ignore_patterns('__pycache__','model_32635_left_repair.pt'))
own=Q/'source/model_near_lower_CPU_prepared.pt';shutil.copy2(source,own);assert H(own)==SHA
worker=Q/'paired_full80_parameter_bound_v2.py';old=worker.read_text();new=old.replace('2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971',SHA).replace(OLD.name,P.name);compile(new,str(worker),'exec');worker.write_text(new,encoding='utf8')
# Every physical instruction and asset is reused exactly from actual admitted Wave80.
assert H(Q/'full80_runtime_native_v1.py')==H(OLD/'payload/full80_runtime_native_v1.py')=='f8373bb6bce14c8e39e243e1e4ea9b88542b4033d5dc8f6b1c15eb95d1ddd0cc'
manifest=Q/'REFERENCE17B_SOURCE_BUNDLE_MANIFEST.json';prior=json.loads(manifest.read_bytes());rows=[]
for p in sorted(Q.rglob('*')):
 if p.is_file() and p!=manifest and '__pycache__' not in p.parts:rows.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,sha256=H(p)))
prior.update(file_rows=rows,actual_candidate_final_source_SHA=SHA,parent_own_full20k_final_SHA=m['source']['sha256'],candidate_CPU_manifest=m,only_frozen_mean_row_factor=True,new_scope_policy_only_frozen_no_PPO=True,production_adopted=False,initial_fullstate_CUDA_not_performed=True)
manifest.write_text(json.dumps(prior,indent=2),encoding='utf8')
archive=P/'FULL80_FROZEN1500_SOURCE_V1.zip'
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
 for p in sorted(Q.rglob('*')):
  if p.is_file() and '__pycache__' not in p.parts:z.write(p,p.relative_to(Q).as_posix())
prep=dict(epoch=time.time(),CPU_prepared=True,source_SHA=SHA,source_CPU_only_candidate=m['candidate'],parent_final2b_complete_actual=True,whole20k_full107finite=True,candidate_changes_only_one_mean_head_and_optimizer_moments=True,no_PPO=True,not_production_source=True,worker=dict(path=str(worker),sha256=H(worker)),runtime=dict(path=str(Q/'full80_runtime_native_v1.py'),sha256=H(Q/'full80_runtime_native_v1.py')),manifest=dict(path=str(manifest),sha256=H(manifest)),package=dict(path=str(archive),bytes=archive.stat().st_size,sha256=H(archive)),original_complete_full80_physical_backend_bytes_reused=True,new_full1500_firstphysics_pair_and_behavior_pending=True,qualified50=False)
(P/'reports/FULL80_NATIVE_CPU_PORT_PREPARED_ACTUAL.json').write_text(json.dumps(prep,indent=2),encoding='utf8')
s=(OLD/'deploy_left_repair_final_full80_unique_once.py').read_text().replace(OLD.name,P.name).replace('native3060_left_repair_final_full80_frozen1500_v1','native3060_left_near_lower_factor_full80_frozen1500_v1').replace('MOD4_LeftRepairFinalFull80_20261014_Frozen1500_v1','MOD4_LeftNearLowerFactorFull80_20261014_Frozen1500_v1').replace('2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971',SHA).replace('source/model_32635_left_repair.pt','source/model_near_lower_CPU_prepared.pt')
anchor="assert source['LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION']['profile']=='left_initial_joint_margin014_std1_v1'";assert s.count(anchor)==1
s=s.replace(anchor,anchor+"\nassert source['LINUX20K_LEFT_JOINT_LOWER_MARGIN005_KEEP_SAVED_STD_INITIALIZATION_V1']['profile']=='left_initial_joint_lower_margin005_keep_saved_std_v1'")
q=P/'deploy_near_lower_full80_factor_unique_once.py';compile(s,str(q),'exec');q.write_text(s,encoding='utf8')
for n in ('collect_full80_frozen1500_readonly.py','collect_left_full80_bounded_transport_actual.py','review_full80_full1500_CPU_actual.py','review_full80_original_route_prefix_CPU_actual.py'):
 s=(OLD/n).read_text().replace(OLD.name,P.name).replace('native3060_left_repair_final_full80_frozen1500_v1','native3060_left_near_lower_factor_full80_frozen1500_v1').replace('2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971',SHA)
 compile(s,str(P/n),'exec');(P/n).write_text(s,encoding='utf8')
s=(OLD/'review_left_full80_direct_original_prefix_actual.py').read_text().replace(OLD.name,P.name).replace("MOD4_3060_FULL80_FROZEN_CURRENT_20261014/reports/",OLD.name+'/reports/').replace('LEFT_REPAIR_DIRECT_ORIGINAL_FULL80_PREFIX_ACTUAL_REVIEW.json','NEAR_LOWER_FACTOR_DIRECT_PARENT2B_FULL80_PREFIX_ACTUAL_REVIEW.json')
q=P/'review_near_lower_full80_direct_parent2b_prefix_actual.py';compile(s,str(q),'exec');q.write_text(s,encoding='utf8')
print(json.dumps(dict(CPU_factor_prepared=True,source_SHA=SHA,package_bytes=archive.stat().st_size,next_new_deployment=str(P/'deploy_near_lower_full80_factor_unique_once.py'),not_production_adopted=True)))
