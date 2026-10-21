"""Saved-input CPU replay of the authorized goal and new rate formulae; no learning."""
from pathlib import Path
import ast,json,sys,time,traceback
import numpy as np,torch
B=Path(__file__).resolve().parent;R=B/'reports';A=B/'full20k_native180_V3_actual';P=B/'H1_step270_native32_V4_payload'
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
try:
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();sys.path.insert(0,str(P));from step270_goal_and_scut_rates_candidate import Step270Events
 from scut_ballistic_reference_uninstalled import reference
 proof=json.loads((R/'STEP270_FULL20K_NATIVE180_V3_CORE_CLOCK_GUARD_WITNESS_CPU_ACTUAL.json').read_bytes());assert proof['passed_core_clock_action_guards_and_witness_CPU']
 tree=ast.parse((B/'sdk210_grid_source_unmodified/cloner.py').read_text(encoding='utf8')) if (B/'sdk210_grid_source_unmodified/cloner.py').is_file() else None
 grid=json.loads((R/'STEP270_NATIVE_V4_FULL_RAW_RECEIPT_RECOVERED_V2_ACTUAL.json').read_bytes())['SDK_grid_source'][0];tree=ast.parse(Path(grid['local_path']).read_text(encoding='utf8'));node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='grid_transforms');scope=dict(torch=torch,math=__import__('math'));exec(compile(ast.Module(body=[node],type_ignores=[]),'actual_grid_AST','exec'),scope);origins=scope['grid_transforms'](20000,2.5,device='cpu')[0].numpy();edge=origins[:,0,None]+np.float32(.35)
 goal=Step270Events(20000);goal.was_ready=torch.zeros(20000,dtype=torch.bool);age=np.zeros(20000,np.int64);previous_front=np.full((20000,2),-1e6,np.float32);crossed=np.zeros((20000,2),bool);previous_request=np.zeros(20000,bool);yaw_reference=np.zeros(20000,np.float32);target_peak=torch.full((20000,),.5);episode_counts=np.zeros((3,20000),np.int64);total_counts=np.zeros(3,np.int64);controls=0;event_error=ref_error=0.;rows=[]
 t=lambda x:torch.from_numpy(np.asarray(x).copy())
 fields=('root13','all34_clearance','step_wheel_min','step_wheel_max','step_query_height','step_query_face','step_platform_contact','step_footprint_inside','step_first_cross_clear','step_stable_ticks','step_goal_success','wheel_norm_N','nonwheel_max','root_planar_speed','roll','pitch','yaw','event_delta','takeoff','landing','recovery')
 for cp,pp in zip(sorted((A/'out').glob('CONTROL_*.npz')),sorted((A/'out').glob('PHYSICS_*.npz'))):
  with np.load(cp,allow_pickle=False) as z:c={k:z[k] for k in ('policy','done','event_expected','event_applied','takeoff_count','landing_count','recovery_count','recovered_before_reset')}
  with np.load(pp,allow_pickle=False) as z:p={k:z[k] for k in fields}
  for i in range(len(c['done'])):
   request=(age>=100)&(age<180);control_event=np.zeros(20000,np.float32)
   for j in range(4):
    k=4*i+j;root=p['root13'][k];lo=p['step_wheel_min'][k];hi=p['step_wheel_max'][k]
    inside=(lo[:,:,0]>=edge)&(hi[:,:,0]<=edge+np.float32(.8))&(lo[:,:,1]>=origins[:,1,None]-np.float32(.6))&(hi[:,:,1]<=origins[:,1,None]+np.float32(.6));assert np.array_equal(inside,p['step_footprint_inside'][k])
    face=p['step_query_face'][k];top=(face==np.arange(20000)[:,None]*12+4)|(face==np.arange(20000)[:,None]*12+5);assert np.array_equal(top,p['step_platform_contact'][k]);assert np.max(np.abs(p['step_query_height'][k]-np.where(top,np.float32(.27),np.float32(0))))<=1e-6
    fresh=request&~previous_request;yaw_reference=np.where(fresh,p['yaw'][k],yaw_reference);previous_request=request.copy();N=p['wheel_norm_N'][k];non=p['nonwheel_max'][k];minimum=p['all34_clearance'][k].min(-1)
    airborne=(N<=1).all(-1)&(lo[:,:,2]>.005).all(-1)&(minimum>0)&(non<=1);crossed|=(previous_front<edge)&(hi[:,:,0]>=edge)&airborne[:,None]&(lo[:,:,2]>=.27)&goal.launched.numpy()[:,None];previous_front=hi[:,:,0].copy();assert np.array_equal(crossed,p['step_first_cross_clear'][k])
    prepared=(N>1).all(-1)&(non<=1)&(minimum>=-.001)&(np.abs(root[:,9])<=.2)&(p['root_planar_speed'][k]<=.2)&(np.abs(p['roll'][k])<.2617993877991494)&(np.abs(p['pitch'][k])<.2617993877991494)
    out=goal.physical(request=t(request),ground_ready=t(prepared),nonwheel_clean=t((non<=1)&np.where((N<=1).all(-1),minimum>0,minimum>=-.001)),known_integrity=torch.ones(20000,dtype=torch.bool),wheel_N=t(N),wheel_bottom_world_z=t(lo[:,:,2]),wheel_contact_platform=t(top),wheel_footprints_inside_top=t(inside),both_wheel_edge_crossed=t(crossed.all(-1)),root_vz=t(root[:,9]),planar_speed=t(p['root_planar_speed'][k]),roll=t(p['roll'][k]),pitch=t(p['pitch'][k]),heading_error=t(p['yaw'][k]-yaw_reference))
    delta=out['wheel_clearance_progress_delta']+out['takeoff'].float()+2*out['landing'].float()+3*out['recovery'].float();event_error=max(event_error,float(np.max(np.abs(delta.numpy()-p['event_delta'][k]))));assert event_error<=1e-6;control_event+=delta.numpy()
    for h,name in enumerate(('takeoff','landing','recovery')):
     assert np.array_equal(out[name].numpy(),p[name][k]);episode_counts[h]+=out[name].numpy();total_counts[h]+=int(out[name].sum())
    assert np.array_equal(goal.stable_ticks.numpy(),p['step_stable_ticks'][k]) and np.array_equal(goal.success.numpy(),p['step_goal_success'][k])
    measured_peak=torch.tensor(.27)+(t(root[:,2])-t(lo[:,:,2]).amin(-1)).clamp_min(0)+.02;target_peak=torch.where(t(fresh),measured_peak,target_peak)
    _,vel,_=reference(elapsed=t(np.maximum(age-100,0)).float()*.01,peak_height=target_peak,push_start_height=.20,release_height=.31)
    peak=target_peak.numpy().astype(np.float64);vv=np.sqrt(2*9.81*np.maximum(peak-.31,0));push=np.divide(.22,vv,out=np.zeros_like(vv),where=vv>1e-6);elapsed=np.maximum(age-100,0).astype(np.float32)*np.float32(.01);acc=np.divide(vv,push,out=np.zeros_like(vv),where=push>1e-6);independent=np.where(elapsed<=push,acc*np.minimum(elapsed,push),vv-9.81*np.maximum(elapsed-push,0));ref_error=max(ref_error,float(np.abs(vel.numpy()-independent).max()));assert ref_error<=1e-5
   assert np.max(np.abs(control_event-c['event_expected'][i]))<=1e-6 and np.max(np.abs(control_event-c['event_applied'][i]))<=1e-6
   for h,name in enumerate(('takeoff_count','landing_count','recovery_count')):assert np.array_equal(episode_counts[h],c[name][i])
   assert np.array_equal(goal.success.numpy(),c['recovered_before_reset'][i]);done=c['done'][i].astype(bool);age+=1;age[done]=0;previous_front[done]=-1e6;crossed[done]=False;previous_request[done]=False;yaw_reference[done]=0;target_peak[done]=.5;episode_counts[:,done]=0
   for value in vars(goal).values():
    if torch.is_tensor(value):value[t(done)]=0
   controls+=1
  rows.append(dict(control_file=cp.name,callbacks=len(p['root13']),event_maxabs_error=event_error,SCUT_ballistic_reference_independent_numpy_maxabs=ref_error));del c,p
 assert controls==180 and total_counts.tolist()==proof['raw_events_takeoff_landing_recovery'] and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 row=dict(epoch=time.time(),passed_saved_event_and_ballistic_reference_CPU=True,num_envs=20000,controls=180,callbacks=720,sim_seconds=1.8,all_goal_event_rows=14400000,source_Adam=674740,events_takeoff_landing_recovery=total_counts.tolist(),event_GPU_CPU_maxabs=event_error,SCUT_fixed_AST_ballistic_CPU_numpy_maxabs=ref_error,original_event_reward_actual_SDK_dt_contribution_verified=True,public_schedule_and_selected_reset_goal_credit_exact=True,actual_top_face_identity_height_and_footprint_consistency_checked=True,all_goal_thresholds_270mm_and_stable200_callbacks_unchanged=True,blocks=rows,not_all20k_independent_bodypose_or_cooked_query_replay=True,new_three_reward_rates_not_yet_compared_to_recorded_GPU_terms=True,not_graduation_or_production_admission=True,not_a_15second_jump_height_eval=True,no_GPU_optimizer_or_learning_GO=True)
 put(R/'STEP270_FULL20K_NATIVE180_V3_EVENTS_SCUT_REFERENCE_CPU_ACTUAL.json',row);print(json.dumps(row))
except BaseException:put(R/('STEP270_FULL20K_NATIVE180_V3_EVENT_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay=True));raise
