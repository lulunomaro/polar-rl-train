from pathlib import Path
import ast,hashlib,json,math,sys,time,traceback
import numpy as np,torch
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';A=B/'native32_v4_actual';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
try:
 q=json.loads((R/'STEP270_NATIVE_V4_FULL_RAW_RECEIPT_RECOVERED_V2_ACTUAL.json').read_bytes());co=q['parent_complete'];f=co['final'];assert q['actual_finite_transport_returned'] and co['passed'] and co['returncode']==0 and co['actual_child_waited'] and not co['errors'] and q['parent_exit']['all_own_children_waited'] and q['parent_exit']['own_eval_lease_released'];assert f['steps']==480 and f['callbacks']==1920 and f['num_envs']==32 and f['actor9_STD_literal_exact'] and f['zero_optimizer'];assert f['health']['ordinary_episode_reset_events']==0 and f['health']['integrity_task_reset_events']==f['health']['unknown_task_reset_events']==0
 torch.set_num_threads(4);rng=torch.get_rng_state().clone();source=W/'MOD4_SCUT_FUDAN_SIXTEENTH_HOUR_20261019/actual_closed_three_finals/h1/model_update42.pt';assert H(source)==f['source_SHA'];s=torch.load(source,map_location='cpu',weights_only=False);assert len(s['actor_state_dict'])==9 and len(s['critic_state_dict'])==8 and len(s['optimizer_state_dict']['state'])==17 and {int(v['step']) for v in s['optimizer_state_dict']['state'].values()}=={674740}
 for key in ('actor_state_dict','critic_state_dict'):
  assert all(torch.isfinite(t).all() for t in s[key].values())
 for st in s['optimizer_state_dict']['state'].values():assert all(torch.isfinite(t).all() for t in st.values() if torch.is_tensor(t))
 weights={k:t.clone() for k,t in s['actor_state_dict'].items()};sys.path[:0]=[str(B/'candidate_uninstalled'),str(W/'MOD4_SCUT_FUDAN_SIXTEENTH_HOUR_20261019/payload/h1')]
 from h1_reference_geometry_cpu import support
 from step270_triangle_geometry_cpu import generate
 from step270_goal_and_scut_rates_candidate import Step270Events
 # Execute only the captured actual SDK pure CPU grid function, retaining its AST.
 gridfile=Path(q['SDK_grid_source'][0]['local_path']);assert H(gridfile)==q['SDK_grid_source'][0]['SHA'];tree=ast.parse(gridfile.read_text(encoding='utf8'));node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='grid_transforms');ns=dict(math=math,torch=torch);exec(compile(ast.Module(body=[node],type_ignores=[]),str(gridfile),'exec'),ns);origins=ns['grid_transforms'](32,2.5,device='cpu')[0].numpy()
 terrain=json.loads((A/'out/ACTUAL_STEP270_TERRAIN_AND_REWARD_TASK.json').read_bytes());geo=json.loads((A/'out/GEOMETRY_AND_CLOCK_ACTUAL.json').read_bytes());assert geo['policy_hz']==100 and geo['decimation']==4 and geo['physics_dt']==.0025 and geo['witness_ids']==list(range(32));vertices,faces,groups=generate(origins[:,:2],**terrain['geometry']);assert hashlib.sha256(vertices[faces].astype('<f4').tobytes()).hexdigest()==terrain['actual_stage_ordered_triangle_SHA'];assert terrain['geometry']['height']>=.270 and terrain['material_inherited_from_original_ground'];topids=np.array([g['top_faces'] for g in groups]);bounds=np.array([g['bounds'] for g in groups]);body=geo['body_names'];wheel_body=[body.index(x) for x in ('left_wheel','right_wheel')];force_wheel=[geo['contact_names'].index(x) for x in ('left_wheel','right_wheel')];shape_groups=[[x for x in geo['shapes'] if x['body']==name] for name in ('left_wheel','right_wheel')]
 raw={x['relative']:x for x in q['raw']};goal=Step270Events(32);goal.was_ready=torch.zeros(32,dtype=torch.bool);last=np.zeros((32,6),np.float32);previous_front=np.full((32,2),-1e6);crossed=np.zeros((32,2),bool);yaw_reference=np.zeros(32);counts=np.zeros((3,32),np.int64);tot=0;gerr=cerr=serr=ferr=werr=qerr=evt=meanerr=0.;ever_top=np.zeros(32,bool)
 def load(p):
  row=raw[p.relative_to(A).as_posix()];assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'];z=np.load(p,allow_pickle=False);v={k:z[k] for k in z.files}
  for k,x in v.items():
   assert x.shape[1]==32
   if x.dtype.kind in 'fc':assert np.isfinite(x).all(),k
  return v
 def wheel_aabb(pos,quat):
  lows=[];highs=[]
  for shapes in shape_groups:
   lo=[];hi=[]
   for sh in shapes:
    p=pos[:,sh['body_index']].astype(np.float64);x,y,z,w=np.moveaxis(quat[:,sh['body_index']].astype(np.float64),-1,0);rot=np.stack([np.stack([1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)],-1),np.stack([2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)],-1),np.stack([2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)],-1)],-2);row=rot@np.array(sh['linear_body_from_shape']);center=p+(rot@np.array(sh['origin_body_m'])[:,None])[...,0];kind=sh['type']
    if kind in ('Cylinder','Capsule'):
     axial=np.abs(row[:,:,sh['axis']]);norm2=(row*row).sum(-1);extent=axial*sh['height']*.5+sh['radius']*(np.sqrt(norm2) if kind=='Capsule' else np.sqrt(np.maximum(norm2-axial*axial,0)))
    elif kind=='Cube':extent=np.abs(row).sum(-1)*sh['size']*.5
    elif kind=='Mesh':pts=row@np.array(sh['points']).T;lo.append(center+pts.min(-1));hi.append(center+pts.max(-1));continue
    else:raise ValueError(kind)
    lo.append(center-extent);hi.append(center+extent)
   lows.append(np.min(lo,axis=0));highs.append(np.max(hi,axis=0))
  return np.stack(lows,1),np.stack(highs,1)
 for cp,pp in zip(sorted((A/'out').glob('CONTROL_*.npz')),sorted((A/'out').glob('PHYSICS_*.npz'))):
  c=load(cp);p=load(pp);assert len(p['root13'])==4*len(c['policy']) and not c['done'].any() and np.array_equal(c['executed6'],np.clip(c['raw_action'],-6,6));assert c['mimic'].max()<=.01 and c['closure'].max()<=.002
  gerr=max(gerr,float(abs(support(p['witness_body_pos'],p['witness_body_quat_xyzw'],geo['shapes'])-p['all34_clearance']).max()));assert gerr<=1e-6
  quat=p['witness_body_quat_xyzw'].astype(np.float64);xyz=quat[...,:3];qw=quat[...,3:4];local=p['actual_body_COM_local'].astype(np.float64);t=2*np.cross(xyz,local);com=p['witness_body_pos'].astype(np.float64)+local+qw*t+np.cross(xyz,t);cerr=max(cerr,float(abs(com-p['actual_body_COM_world']).max()));system=(com*p['actual_mass'][...,None]).sum(-2)/p['actual_mass'].sum(-1)[...,None];serr=max(serr,float(abs(system-p['whole_robot_COM']).max()));assert cerr<=1e-5 and serr<=1e-5;ferr=max(ferr,float(abs(p['all31_contact_force'][:,:,force_wheel]-p['wheel_raw']).max()));assert ferr<=.1
  ref=torch.from_numpy(c['policy'].reshape(-1,35).copy()).double();envelope=torch.zeros_like(ref);eps=torch.finfo(torch.float32).eps
  for n in (0,2,4,6):
   w=weights[f'mlp.{n}.weight'].double();bias=weights[f'mlp.{n}.bias'].double();gamma=(w.shape[1]+1)*eps/(1-(w.shape[1]+1)*eps);envelope=torch.nn.functional.linear(envelope,w.abs())+gamma*torch.nn.functional.linear(ref.abs(),w.abs(),bias.abs());ref=torch.nn.functional.linear(ref,w,bias)
   if n!=6:ref=torch.nn.functional.elu(ref);envelope+=8*eps*torch.maximum(torch.ones_like(ref),ref.abs())
  gpu=torch.from_numpy(c['raw_action'].reshape(-1,6).copy()).double();assert ((gpu-ref).abs()<=envelope+1e-12).all();meanerr=max(meanerr,float((gpu-ref).abs().max()))
  for i in range(len(c['policy'])):
   request=np.full(32,100<=tot<180);mode=np.zeros((32,7),np.float32);mode[:,0]=~request;mode[:,4]=request;assert np.array_equal(c['policy'][i,:,28:35],mode) and np.array_equal(c['policy'][i,:,22:28],last) and np.array_equal(c['policy'][i,:,0],request.astype(np.float32)*.8) and not c['policy'][i,:,1:3].any();control_event=np.zeros(32)
   for j in range(4):
    k=4*i+j;root=p['root13'][k];lo,hi=wheel_aabb(p['witness_body_pos'][k],p['witness_body_quat_xyzw'][k]);werr=max(werr,float(abs(lo-p['step_wheel_min'][k]).max()),float(abs(hi-p['step_wheel_max'][k]).max()));assert werr<=1e-6;edge=origins[:,0,None]+.35;inside=(lo[:,:,0]>=edge)&(hi[:,:,0]<=edge+.8)&(lo[:,:,1]>=origins[:,1,None]-.6)&(hi[:,:,1]<=origins[:,1,None]+.6);assert np.array_equal(inside,p['step_footprint_inside'][k]);wheelxy=p['witness_body_pos'][k,:,wheel_body,:2].transpose(1,0,2) if p['witness_body_pos'][k,:,wheel_body,:2].shape[:2]==(2,32) else p['witness_body_pos'][k][:,wheel_body,:2];center_inside=((wheelxy>=bounds[:,None,0,:2])&(wheelxy<=bounds[:,None,1,:2])).all(-1);height=np.where(center_inside,.270,0);qerr=max(qerr,float(abs(height-p['step_query_height'][k]).max()));assert qerr<=1e-6;top=(p['step_query_face'][k,:,:,None]==topids[:,None,:]).any(-1);assert np.array_equal(top,center_inside) and np.array_equal(top,p['step_platform_contact'][k]);ever_top|=top.all(-1)
    if tot==100 and j==0:yaw_reference=p['yaw'][k].copy()
    N=p['wheel_norm_N'][k];non=p['nonwheel_max'][k];minimum=p['all34_clearance'][k].min(-1);airborne=(N<=1).all(-1)&(lo[:,:,2]>.005).all(-1)&(minimum>0)&(non<=1);crossed|=(previous_front<edge)&(hi[:,:,0]>=edge)&airborne[:,None]&(lo[:,:,2]>=.27)&goal.launched.numpy()[:,None];previous_front=hi[:,:,0];assert np.array_equal(crossed,p['step_first_cross_clear'][k]);prepared=(N>1).all(-1)&(non<=1)&(minimum>=-.001)&(abs(root[:,9])<=.2)&(p['root_planar_speed'][k]<=.2)&(abs(p['roll'][k])<.2617993877991494)&(abs(p['pitch'][k])<.2617993877991494)
    t=lambda x:torch.from_numpy(np.asarray(x).copy());out=goal.physical(request=t(request),ground_ready=t(prepared),nonwheel_clean=t((non<=1)&np.where((N<=1).all(-1),minimum>0,minimum>=-.001)),known_integrity=torch.ones(32,dtype=torch.bool),wheel_N=t(N),wheel_bottom_world_z=t(p['step_wheel_min'][k,:,:,2]),wheel_contact_platform=t(top),wheel_footprints_inside_top=t(inside),both_wheel_edge_crossed=t(crossed.all(-1)),root_vz=t(root[:,9]),planar_speed=t(p['root_planar_speed'][k]),roll=t(p['roll'][k]),pitch=t(p['pitch'][k]),heading_error=t(p['yaw'][k]-yaw_reference));delta=out['wheel_clearance_progress_delta'].numpy()+out['takeoff'].float().numpy()+2*out['landing'].float().numpy()+3*out['recovery'].float().numpy();evt=max(evt,float(abs(delta-p['event_delta'][k]).max()));assert evt<=1e-6
    for z,key in enumerate(('takeoff','landing','recovery')):assert np.array_equal(out[key].numpy(),p[key][k]);counts[z]+=out[key].numpy()
    assert np.array_equal(goal.stable_ticks.numpy(),p['step_stable_ticks'][k]) and np.array_equal(goal.success.numpy(),p['step_goal_success'][k]);control_event+=delta
   assert np.allclose(control_event,c['event_expected'][i],atol=1e-6,rtol=0);last=c['executed6'][i].copy();tot+=1
 assert tot==480 and all(torch.equal(t,weights[k]) for k,t in s['actor_state_dict'].items()) and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 report=dict(epoch=time.time(),passed_saved_rows_execution_CPU=True,source_SHA=f['source_SHA'],source_Adam=674740,num_envs=32,controls=480,callbacks=1920,policy_hz=100,actual_270mm_static_vertical_mesh_SHA=terrain['actual_stage_ordered_triangle_SHA'],actual_SDK_grid_AST_and_stage_triangle_SHA_exact=True,all_rows_finite=True,actor9_STD_critic8_17Adam_source_finite_zero_optimizer=True,geometry_error_m=gerr,body_COM_error_m=cerr,whole_COM_error_m=serr,force_error_N=ferr,wheel_AABB_error_m=werr,terrain_query_error_m=qerr,task_event_delta_error=evt,mean_GPU_vs_double_error=meanerr,original_physical_and_numeric_guards_not_lowered=True,source_public04_command_previous_action_byteexact=True,events=counts.sum(1).tolist(),successful_step270_cases=int(goal.success.sum()),platform_center_query_both_wheels_cases=int(ever_top.sum()),not_skill_graduation_or_production_admission=True,remaining_before_PPO=['actual cooked PhysX scene-query versus authored triangles audit','source20k D0-D7 and command private RNG/core17Adam migration + new-task checkpoint roundtrip','20k production configuration native source SDK/PPO CPU and finite originalwriter admission'])
 (R/'STEP270_NATIVE32_V4_SAVED_ROWS_CPU_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(report,indent=2));print(json.dumps(report))
except BaseException:
 (R/('STEP270_NATIVE32_V4_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8').write(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay=True),indent=2));raise
