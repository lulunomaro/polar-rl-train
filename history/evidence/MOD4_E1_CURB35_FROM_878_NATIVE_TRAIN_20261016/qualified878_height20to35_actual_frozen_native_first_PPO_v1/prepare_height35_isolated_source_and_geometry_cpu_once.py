"""Build an unused height-only CURB35 branch. No network, SDK or optimizer."""
from pathlib import Path
import os,ast,hashlib,json,shutil,time
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch,numpy as np
D=Path(__file__).resolve().parent;W=D.parent;OLD=W/'MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016/train_payload';B=D/'payload';J=B/'job0';C=J/'runtime/isaac/mod4'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not B.exists();shutil.copytree(OLD/'job0',J,ignore=shutil.ignore_patterns('__pycache__'));shutil.copytree(OLD/'lib',B/'lib')
src=W/'MOD4_HOST72_THREE_GPU_SINGLE_PPO_7H_20261016/final878_actual/source210/rank0/model_update878.pt';assert H(src)=='268967941b352709ec6ef9f3f4461ed23aac5457db9c4262f06b0619a974e6f1'
# Preserve copied ancestor source too; the new explicit source has a distinct basename.
shutil.copy2(src,J/'source/qualified_CURB878.pt');ck=torch.load(src,map_location='cpu',weights_only=False);count=[0,0]
def finite(v):
 if torch.is_tensor(v):count[0]+=1;count[1]+=int(v.is_floating_point());assert not v.is_floating_point() or torch.isfinite(v).all()
 elif isinstance(v,dict):
  for z in v.values():finite(z)
 elif isinstance(v,(tuple,list)):
  for z in v:finite(z)
finite(ck);assert len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8 and len(ck['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in ck['optimizer_state_dict']['state'].values()}=={660400}
p=json.loads((C/'curb20_profile.json').read_bytes());p.update(schema='derived_vertical_curb35_strip150_cpu_component_v1',height_m=.035,upper_platform_z_m=.035)
for v in p['vertices']:
 if v[2]==.02:v[2]=.035
(C/'curb35_profile.json').write_text(json.dumps(p,indent=2))
s=(C/'curb20_geometry.py').read_text();s=s.replace('curb20_profile.json','curb35_profile.json').replace('.020','.035').replace('derived20mm','derived35mm').replace('Independent derived CURB geometry','Independent height35 derived CURB geometry');(C/'curb35_geometry.py').write_text(s)
s=(C/'curb20_retention_runtime.py').read_text().replace('from curb20_geometry import configure_curb','from curb35_geometry import configure_curb');(C/'curb35_retention_runtime.py').write_text(s)
s=(C/'curb20_entry_v3_runtime.py').read_text().replace('from curb20_retention_runtime import configure_retention as old_configure','from curb35_retention_runtime import configure_retention as old_configure');(C/'curb35_entry_runtime.py').write_text(s)
shutil.copy2(D/'curb35_checkpoint_candidate.py',C/'curb35_checkpoint.py')
for original,new in [('train_curb20_entry_resume_ppo.py','train_curb35_resume_ppo.py'),('train_curb20_entry_fresh_preflight_ppo.py','train_curb35_fresh128_ppo.py')]:
 s=(C/original).read_text();q=s.replace('from curb20_entry_v3_runtime import configure_retention as configure_intro','from curb35_entry_runtime import configure_retention as configure_intro').replace('from curb20_entry_full_checkpoint import','from curb35_checkpoint import');assert ast.dump(ast.parse(s))==ast.dump(ast.parse(q.replace('from curb35_entry_runtime import configure_retention as configure_intro','from curb20_entry_v3_runtime import configure_retention as configure_intro').replace('from curb35_checkpoint import','from curb20_entry_full_checkpoint import')));compile(q,new,'exec');(C/new).write_text(q)
for file in C.glob('curb35*.py'):compile(file.read_text(),str(file),'exec')
v=np.array(p['vertices']);f=np.array(p['triangles']);assert v.shape==(10,3) and f.shape==(8,3) and np.ptp(v[:,2])==.035
norm=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);horizontal=np.ptp(v[f][:,:,2],axis=1)==0;assert (norm[horizontal,2]>0).all() and (norm[~horizontal,2]==0).all() and (~horizontal).sum()==2
old=json.loads((C/'curb20_profile.json').read_bytes());assert np.array_equal(np.array(old['vertices'])[:,:2],v[:,:2]) and old['triangles']==p['triangles'] and old['strip_width_m']==p['strip_width_m']==.15
task=dict(job=0,kind='CURB35',source_SHA=H(src),source_file='qualified_CURB878.pt',source_Adamstep=660400,entry='train_curb35_resume_ppo.py',GPU_UUID='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e',per_GPU_envs=20000,max_new_scope_learning_parent_seconds_including_PPO_prechecks=2700,exit_headroom=180,only_geometry_height_changed_from20_to35=True,no_STD_optimizer_reset=True,no_S8_or_gate_or_70=True)
(J/'TASK_CURB35.json').write_text(json.dumps(task,indent=2))
r=dict(epoch=time.time(),CPU_only_passed=True,source=dict(path=str(src.resolve()),bytes=src.stat().st_size,SHA=H(src),whole_tensor_counts=count,all17Adam660400=True),height35_geometry=dict(profile_SHA=H(C/'curb35_profile.json'),vertices10_triangles8=True,vertical_faces2=True,mirror_winding_preserved=True,original_XY_faces_strip_reset_entry_reward_commands_physics_unchanged=True),inverse_AST_entry_exact_except_explicit_config_checkpoint_imports=True,original_all_modules_retained=True,native_target_fullstate_resources_and_PPO_not_yet_passed=True,task=task)
(D/'reports/CURB35_HEIGHT_ONLY_SOURCE_GEOMETRY_PREPARED_CPU_ACTUAL.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
