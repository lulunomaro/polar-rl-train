from pathlib import Path
import os,json,time,hashlib,ast,traceback,sys
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np,torch
D=Path(__file__).resolve().parent;P=D.parent/'MOD4_E1_CURB275_BRIDGE_FROM_CURB35_40_20261016';Q=P/'payload';R=P/'reports';O=D/'v9_payload/curb';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 rt=Q/'job0/runtime/isaac/mod4';profile=json.loads((rt/'curb35_profile.json').read_bytes());before=json.loads((O/'job0/runtime/isaac/mod4/curb35_profile.json').read_bytes());b=np.array(before['vertices']);v=np.array(profile['vertices']);f=np.array(profile['triangles']);err=float(abs(v[:,2]-b[:,2]*(.0275/.035)).max());assert err<=1e-17
 put('V1_ORIGINAL_EXACT_FLOAT_SCALING_READER_REJECTION_RETAINED.json',dict(epoch=time.time(),original_source=str(D/'prepare_CURB27p5_bridge_inside_approved20to35_geometry_only_once.py'),original_assertion='np.all(v[:,2]==b[:,2]*(.0275/.035))',original_result=False,actual_FP64_rounding_maxabs=err,no_remote_command_GPU_or_PPO_before_rejection=True,independent_V2_only_CPU_reader_no_candidate_or_physics_change=True))
 assert np.array_equal(b[:,:2],v[:,:2]) and before['triangles']==profile['triangles'] and profile['height_m']==.0275 and profile['strip_width_m']==.15 and .02<profile['height_m']<.035
 for sign in (1,-1):
  vv=v.copy();vv[:,0]*=sign;ff=f if sign==1 else f[:,::-1];n=np.cross(vv[ff[:,1]]-vv[ff[:,0]],vv[ff[:,2]]-vv[ff[:,0]]);n/=np.linalg.norm(n,axis=1)[:,None];assert np.allclose(np.abs(n).sum(1),1) and (n[n[:,2]!=0,2]>0).all()
 old=json.loads((O/'CONTINUATION_COMPLETE_MANIFEST_V2.json').read_bytes());changes=[];files=[]
 for row in old['files']:
  p=Q/row['relative'];h=H(p)
  if h!=row['SHA']:changes.append(dict(relative=row['relative'],original_SHA=row['SHA'],candidate_SHA=h))
 assert {r['relative'] for r in changes}=={'job0/runtime/isaac/mod4/curb35_profile.json','job0/runtime/isaac/mod4/curb35_geometry.py','job0/runtime/isaac/mod4/curb35_checkpoint.py','native_CPU.py','production_worker.py','job0/TASK_CURB35.json'}
 rng=torch.get_rng_state().clone();ck=torch.load(Q/'job0/source/CURB140.pt',map_location='cpu',weights_only=False);assert H(Q/'job0/source/CURB140.pt')==old['source_SHA'];assert {int(x['step']) for x in ck['optimizer_state_dict']['state'].values()}=={672200};sys.path.insert(0,str(rt));from e1_terrain_state import validate as validate_base
 source=ast.parse((rt/'curb35_checkpoint.py').read_text('utf8'));functions=[x for x in source.body if isinstance(x,ast.FunctionDef) and x.name in ('validate','validate_source35')];ns=dict(PROFILE='mod4_CURB_derived27p5mm_strip150_mirrored_entryreset_v1',validate_base=validate_base);exec(compile(ast.Module(body=functions,type_ignores=[]),'<actual_candidate_source_and_new_height_validators>','exec'),ns)
 st=ck['E1_terrain_state'];ns['validate_source35'](st,20000);new=dict(st,profile=ns['PROFILE'],CURB_height_m=.0275,CURB_profile_sha256=H(rt/'curb35_profile.json'));ns['validate'](new,20000);bad=0
 for name,value in (('CURB_height_m',.035),('CURB_strip_width_m',.2),('CURB_vertical_unsmoothed',False),('entry_no_new_rng',False),('profile',st['profile'])):
  try:ns['validate'](dict(new,**{name:value}),20000)
  except AssertionError:bad+=1
 assert bad==5
 # Compile all sources and require original critical mathematical/physical interfaces byteexact.
 for p in sorted(Q.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts or p.name=='CONTINUATION_COMPLETE_MANIFEST_V2.json':continue
  if p.suffix=='.py':ast.parse(p.read_text('utf8'))
  files.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 spec={k:old[k] for k in ('key','source_filename','native_controls','GPU_UUID','native_script','production_script','source_SHA','source_Adamstep','source_schema_counts')};spec.update(max_parent_seconds=1800,exit_headroom_seconds=300,deferred_admission=False,reuse_admitted_native=False)
 mf=Q/'CONTINUATION_COMPLETE_MANIFEST_V2.json';mf.write_text(json.dumps(dict(spec,files=files),indent=2),encoding='utf8');spec['manifest_SHA']=H(mf)
 out=dict(epoch=time.time(),passed_CPU_only=True,attempt_id='e1-curb275-bridge-from-35-40-geometry-only',source_SHA=old['source_SHA'],source_Adamstep=672200,approved_master_height20to35_curriculum_not_new_range=True,actual_new_height_m=.0275,old35_scope_not_claimed_passed=True,reward_command_DR_solver_hardware_actor_input_all_byteexact=True,geometry_XY_triangles_mirrors_strip150_exact=True,source35_and_new27p5_separate_actual_state_validators_passed=True,negative_state_cases_rejected=bad,original_zero_clock_typed_episode_plus_one_query1e6_COM_mimic_closure_guards_retained=True,all_original_and_partial_failures_retained=True,all_other_manifest_file_SHA_exact=True,changed_files=changes,spec=spec,files=len(files),new_actual_GPU_native144_CPU_source_state_required_before_original_accounted_PPO=True,no_native_or_PPO_pass_inferred=True,CPU_RNG_unchanged0CUDA0optimizer=True)
 put('BRIDGE27P5_GEOMETRY_FULL_SOURCE_DIFF_CPU_PREPARED_ACTUAL_V2.json',out);print(json.dumps({k:v for k,v in out.items() if k!='changed_files'}))
if __name__=='__main__':
 try:main()
 except BaseException:put('BRIDGE27P5_V2_ORIGINAL_CPU_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_PPO=True));raise
