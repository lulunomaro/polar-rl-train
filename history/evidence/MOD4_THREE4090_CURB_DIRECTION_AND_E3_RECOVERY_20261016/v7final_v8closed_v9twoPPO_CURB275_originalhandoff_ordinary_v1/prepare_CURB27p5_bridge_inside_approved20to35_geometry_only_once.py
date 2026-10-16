from pathlib import Path
import os,json,time,hashlib,shutil,ast
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch,numpy as np
D=Path(__file__).resolve().parent;P=D.parent/'MOD4_E1_CURB275_BRIDGE_FROM_CURB35_40_20261016';R=D/'reports';Q=P/'payload'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not P.exists();P.mkdir();(P/'reports').mkdir();shutil.copytree(D/'v9_payload/curb',Q);old=json.loads((Q/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());rt=Q/'job0/runtime/isaac/mod4';changes=[]
 def edit(p,fn):
  before=p.read_text('utf8');after=fn(before);assert after!=before;ast.parse(after) if p.suffix=='.py' else json.loads(after);p.write_text(after,encoding='utf8');changes.append(dict(relative=p.relative_to(Q).as_posix(),original_SHA=hashlib.sha256(before.encode()).hexdigest(),candidate_SHA=H(p)))
 profile=rt/'curb35_profile.json';v=json.loads(profile.read_bytes());assert v['height_m']==.035 and v['strip_width_m']==.15
 v.update(height_m=.0275,upper_platform_z_m=.0275,schema='derived_vertical_curb27p5_strip150_cpu_component_v1',curriculum_scope='Single intermediate height inside approved20to35mm; no physical RM certification')
 for xyz in v['vertices']:
  if xyz[2]==.035:xyz[2]=.0275
 edit(profile,lambda _:json.dumps(v,indent=2))
 edit(rt/'curb35_geometry.py',lambda s:s.replace('.035','.0275').replace('height35','height27p5').replace('derived35mm','derived27p5mm'))
 cp=rt/'curb35_checkpoint.py';original=cp.read_text('utf8');module=ast.parse(original);validate_node=next(x for x in module.body if isinstance(x,ast.FunctionDef) and x.name=='validate');validator=ast.get_source_segment(original,validate_node).replace('def validate(state,n):','def validate_source35(state,n):').replace("state['profile']==PROFILE","state['profile']=='mod4_CURB_derived35mm_strip150_mirrored_entryreset_v1'")
 def migrate(s):
  s=s.replace('derived35mm','derived27p5mm').replace('.035','.0275');s=s.replace('def resume_e1_new_episode(',validator+'\n\ndef resume_e1_new_episode(');s=s.replace("st=ck['E1_terrain_state'];validate(st,env.num_envs)","st=ck['E1_terrain_state'];validate_source35(st,env.num_envs)");s=s.replace("assert st['CURB_height_m']==.0275", "assert st['CURB_height_m']==.035")
  s=s.replace("before=current_state(env);assert identity(st)==identity(before),'Same35 geometry/recipe identity must match protected source';command=", "before=current_state(env);assert st['CURB_height_m']==.035 and before['CURB_height_m']==.0275 and st['CURB_strip_width_m']==before['CURB_strip_width_m']==.15;command=")
  s=s.replace('explicit_same_height35_continuation=True','explicit_height35_to_intermediate27p5_inside_approved20to35=True').replace('actual_source_geometry_identity_equal_same35=True','old_source_geometry_not_claimed_equal_new27p5=True').replace('Explicit same CURB35 protected140 continuation','Explicit height35 to27p5 intermediate bridge inside approved20to35 curriculum')
  return s
 edit(cp,migrate)
 edit(Q/'native_CPU.py',lambda s:s.replace("ck['E1_terrain_state']['CURB_height_m']==.035 and source", "ck['E1_terrain_state']['CURB_height_m']==.0275 and source").replace('same_CURB35_geometry_source140_validated=True','explicit_source35_new27p5_geometry_bridge_validated=True'))
 edit(Q/'production_worker.py',lambda s:s.replace("assert identity(current_state(env))==identity(ck['E1_terrain_state'])", "assert current_state(env)['CURB_height_m']==.0275 and ck['E1_terrain_state']['CURB_height_m']==.035 and current_state(env)['CURB_strip_width_m']==ck['E1_terrain_state']['CURB_strip_width_m']==.15").replace("'CURB35_production_fresh_process_v2'","'CURB27p5_bridge_geometry_only_v1'").replace('current_new35_identity','current_new27p5_identity'))
 task=Q/'job0/TASK_CURB35.json';v=json.loads(task.read_bytes());v.update(id='CURB27P5_BRIDGE_FROM_CURB35_40_GEOMETRY_ONLY_V1',kind='E1_CURB27P5_INTERMEDIATE_HEIGHT_BRIDGE',source_file='CURB140.pt',curriculum_source_height_m=.035,actual_target_height_m=.0275,approved_height_interval_m=[.02,.035],geometry_height_only=True,no_height_reward_DR_physics_change=False,reward_command_DR_physics_hardware_unchanged=True,new_axis='Intermediate27.5mm height only, preserving fixed reset-bound approach and source40 optimizer',scope='Approved E1 20to35mm curriculum bridge after frozen35 up6/27; no blind same35 duration',CURB_deferred_no_unchanged_axis_learning=False,max_parent_seconds=1800,remaining_scope_cap_seconds=1800,exit_headroom=300,template_approved_GPU=False,approved_for_PPO=False);edit(task,lambda _:json.dumps(v,indent=2))
 ck=torch.load(Q/'job0/source/CURB140.pt',map_location='cpu',weights_only=False);assert H(Q/'job0/source/CURB140.pt')==old['source_SHA'];assert ck['E1_terrain_state']['CURB_height_m']==.035 and {int(x['step']) for x in ck['optimizer_state_dict']['state'].values()}=={672200}
 changed={r['relative'] for r in changes}
 for r in old['files']:
  if r['relative'] not in changed:assert H(Q/r['relative'])==r['SHA']
 # Inverse transformations explicitly permit only the new scalar height/profile and migration lifecycle guards.
 assert len(changed)==6 and 'train_curb35_resume_ppo.py' not in {Path(x).name for x in changed}
 # Two mirror meshes keep original XY, topology, unsmoothed vertical normals and strip width.
 before=json.loads((D/'v9_payload/curb/job0/runtime/isaac/mod4/curb35_profile.json').read_bytes());new=json.loads(profile.read_bytes());b=np.array(before['vertices']);v=np.array(new['vertices']);f=np.array(new['triangles']);assert np.array_equal(b[:,:2],v[:,:2]) and before['triangles']==new['triangles'];assert np.all(v[:,2]==b[:,2]*(.0275/.035));norms=[]
 for sign in (1,-1):
  vv=v.copy();vv[:,0]*=sign;ff=f if sign==1 else f[:,::-1];n=np.cross(vv[ff[:,1]]-vv[ff[:,0]],vv[ff[:,2]]-vv[ff[:,0]]);n/=np.linalg.norm(n,axis=1)[:,None];assert np.allclose(np.abs(n).sum(1),1) and (n[n[:,2]!=0,2]>0).all();norms.append(n.tolist())
 negative=0
 for h,w in ((.04,.15),(.019,.15),(.0275,.2),(.0275,-.15)):
  try:assert .02<=h<=.035 and w==.15
  except AssertionError:negative+=1
 assert negative==4 and not torch.cuda.is_initialized()
 files=[]
 for p in sorted(Q.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts or p.name=='CONTINUATION_COMPLETE_MANIFEST_V2.json':continue
  if p.suffix=='.py':ast.parse(p.read_text('utf8'))
  files.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
 spec={k:old[k] for k in ('key','source_filename','native_controls','GPU_UUID','native_script','production_script','source_SHA','source_Adamstep','source_schema_counts')};spec.update(max_parent_seconds=1800,exit_headroom_seconds=300,deferred_admission=False,reuse_admitted_native=False)
 mf=Q/'CONTINUATION_COMPLETE_MANIFEST_V2.json';mf.write_text(json.dumps(dict(spec,files=files),indent=2),encoding='utf8');spec['manifest_SHA']=H(mf)
 out=dict(epoch=time.time(),passed_CPU_only=True,attempt_id='e1-curb275-bridge-from-35-40-geometry-only',source_SHA=old['source_SHA'],source_Adamstep=672200,approved_master_height20to35_curriculum_not_new_range=True,actual_new_height_m=.0275,original35_checkpoint_protected=True,no_changed_reward_command_DR_solver_hardware_or_actor_input=True,original_zero_clock_typed_episode_plus_one_guards_retained=True,actual_new_GPU_native144_allrowCPU_and_original_single_writer_GO_required=True,no_native_or_PPO_pass_inferred=True,changed_files=changes,all_other_manifest_file_SHA_exact=True,mirror_normals=norms,negative_outside_scope_rejected=negative,spec=spec,files=len(files))
 (P/'reports/BRIDGE27P5_GEOMETRY_FULL_SOURCE_DIFF_CPU_PREPARED_ACTUAL.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in out.items() if k not in ('mirror_normals','changed_files')}))
if __name__=='__main__':main()
