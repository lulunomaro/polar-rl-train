"""Independent bounded CPU review; explicitly does not grant production admission."""
from pathlib import Path
import ast,hashlib,json,math,sys,time,traceback
import numpy as np,psutil,torch
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';A=B/'full20k_native180_V3_actual'
def H(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
 return h.hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
try:
 torch.set_num_threads(2);rng=torch.get_rng_state().clone()
 receipt=json.loads((R/'STEP270_FULL20K_NATIVE180_V3_COMPLETE_RAW_AND_EXIT_RECOVERED_V2_ACTUAL.json').read_bytes());co=receipt['parent_complete'];f=co['final'];assert receipt['actual_finite_transport_returned'] and co['passed'] and not co['errors'] and receipt['parent_exit']['all_own_children_waited'] and receipt['parent_exit']['own_eval_lease_released']
 assert (f['steps'],f['callbacks'],f['num_envs'])==(180,720,20000) and f['zero_optimizer'] and f['actor9_STD_literal_exact'] and f['health']['integrity_task_reset_events']==f['health']['unknown_task_reset_events']==0
 sys.path[:0]=[str(B),str(B/'candidate_uninstalled'),str(W/'MOD4_SCUT_FUDAN_SIXTEENTH_HOUR_20261019/payload/h1')]
 from h1_step270_fullstate_checkpoint_candidate_uninstalled import exact,SOURCE_SHA
 from h1_reference_geometry_cpu import support
 from step270_triangle_geometry_cpu import generate
 source=W/'MOD4_SCUT_FUDAN_SIXTEENTH_HOUR_20261019/actual_closed_three_finals/h1/model_update42.pt';s=torch.load(source,map_location='cpu',weights_only=False)
 startup=A/'out/ACTUAL_STEP270_FULL20K_STARTUP_FULLSTATE.pt';ck=torch.load(startup,map_location='cpu',weights_only=False)
 for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert exact(ck[k],s[k])
 assert len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8 and len(ck['optimizer_state_dict']['state'])==17 and {int(v['step']) for v in ck['optimizer_state_dict']['state'].values()}=={674740}
 assert ck['H1_step270_task_state']['version']==270 and ck['H1_step270_task_state']['phase']['num_envs']==20000 and not ck['H1_step270_task_state']['phase']['tensors']['age_control'].any()
 proof=json.loads((A/'out/fullstate_startup/STEP270_FULLSTATE_RESUME_STARTUP_VERIFIED.json').read_bytes());assert proof['actual_CUDA_new_task_roundtrip_exact'] and proof['source_SHA']==SOURCE_SHA
 gridreceipt=json.loads((R/'STEP270_NATIVE_V4_FULL_RAW_RECEIPT_RECOVERED_V2_ACTUAL.json').read_bytes())['SDK_grid_source'][0];gridfile=Path(gridreceipt['local_path']);assert H(gridfile)==gridreceipt['SHA'];tree=ast.parse(gridfile.read_text(encoding='utf8'));node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='grid_transforms');scope=dict(torch=torch,math=math);exec(compile(ast.Module(body=[node],type_ignores=[]),str(gridfile),'exec'),scope);origins=scope['grid_transforms'](20000,2.5,device='cpu')[0].numpy()
 geo=json.loads((A/'out/GEOMETRY_AND_CLOCK_ACTUAL.json').read_bytes());terrain=json.loads((A/'out/ACTUAL_STEP270_TERRAIN_AND_REWARD_TASK.json').read_bytes());assert geo['policy_hz']==100 and geo['physics_dt']==.0025 and geo['decimation']==4 and geo['source20k_DR_and_command_private_RNG_restored_before_one_fresh_episode']
 vertices,faces,groups=generate(origins[:,:2],**terrain['geometry']);assert hashlib.sha256(vertices[faces].astype('<f4').tobytes()).hexdigest()==terrain['actual_stage_ordered_triangle_SHA'];ids=np.array(geo['witness_ids']);assert len(ids)==8
 known={x['relative']:x for x in receipt['raw']};known.update({x['relative']:x for x in f['artifacts']});checked=[]
 for rel,row in known.items():
  p=A/rel;assert p.is_file() and p.stat().st_size==row['bytes'];sha=H(p)
  if row.get('SHA'):assert sha==row['SHA']
  checked.append(dict(path=str(p),relative=rel,bytes=p.stat().st_size,SHA=sha,producer_equality_verified=True if row.get('SHA') else 'first collector verified equality before its later space guard; checksum recovered from immutable local copy'))
 controls=sorted((A/'out').glob('CONTROL_*.npz'));physics=sorted((A/'out').glob('PHYSICS_*.npz'));assert len(controls)==len(physics)==8
 age=np.zeros(20000,np.int64);last=np.zeros((20000,6),np.float32);episode=ck['sensor_DR_state']['episode'].numpy().copy();total=done_count=0;gerr=ferr=0.;events=np.zeros(3,np.int64);records=[]
 names=['all34_clearance','all31_contact_force','wheel_raw','witness_body_pos','witness_body_quat_xyzw','episode','takeoff','landing','recovery']
 wheel=[geo['contact_names'].index(n) for n in ('left_wheel','right_wheel')]
 for cp,pp in zip(controls,physics):
  assert psutil.virtual_memory().available>8*1024**3
  with np.load(cp,allow_pickle=False) as z:c={k:z[k] for k in z.files}
  with np.load(pp,allow_pickle=False) as z:
   for k in z.files:
    if k in names:continue
    x=z[k];assert x.shape[1]==(8 if k.startswith('witness_') else 20000)
    if x.dtype.kind in 'fc':assert np.isfinite(x).all(),k
   p={k:z[k] for k in names}
  for k,x in c.items():
   assert x.shape[1]==20000
   if x.dtype.kind in 'fc':assert np.isfinite(x).all(),k
  for k,x in p.items():
   assert x.shape[1]==(8 if k.startswith('witness_') else 20000)
   if x.dtype.kind in 'fc':assert np.isfinite(x).all(),k
  assert len(p['all34_clearance'])==4*len(c['policy']) and np.array_equal(c['executed6'],np.clip(c['raw_action'],-6,6))
  measured=support(p['witness_body_pos'],p['witness_body_quat_xyzw'],geo['shapes']);gerr=max(gerr,float(np.abs(measured-p['all34_clearance'][:,ids]).max()));assert gerr<=1e-6
  ferr=max(ferr,float(np.abs(p['all31_contact_force'][:,:,wheel]-p['wheel_raw']).max()));assert ferr<=.1
  for i in range(len(c['policy'])):
   request=(age>=100)&(age<180);mode=np.zeros((20000,7),np.float32);mode[:,0]=~request;mode[:,4]=request
   assert np.array_equal(c['policy'][i,:,28:35],mode) and np.array_equal(c['policy'][i,:,22:28],last) and np.array_equal(c['policy'][i,:,0],request.astype(np.float32)*.8) and not c['policy'][i,:,1:3].any()
   assert np.array_equal(c['public_request'][i],request) and np.array_equal(c['age_after'][i],age+1) and np.array_equal(c['episode'][i],episode)
   assert np.array_equal(p['episode'][4*i:4*i+4],np.broadcast_to(episode,(4,20000)))
   done=c['done'][i].astype(bool);assert np.all(done[c['closure'][i]>.002]) and np.all(done[c['mimic'][i]>.01])
   done_count+=int(done.sum());age+=1;age[done]=0;episode[done]+=1;last=c['executed6'][i].copy();last[done]=0;total+=1
  events+=np.array([p[k].sum() for k in ('takeoff','landing','recovery')],dtype=np.int64)
  records.append(dict(control_file=cp.name,physics_file=pp.name,controls=len(c['policy']),callbacks=len(p['all34_clearance']),all_rows_finite=True,geometry_z_witness_maxabs_m=gerr,force_sensor_crosscheck_maxabs_N=ferr))
  del c,p,measured
 assert total==180 and done_count==f['health']['ordinary_episode_reset_events'] and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 row=dict(epoch=time.time(),passed_core_clock_action_guards_and_witness_CPU=True,num_envs=20000,controls=total,callbacks=4*total,source_SHA=SOURCE_SHA,source_Adam=674740,source_actor9_critic8_sixSTD_all17Adam_literal_exact=True,actual_D0_D7_original_CUDA_resume_and_new_phase_roundtrip_verified=True,SDK_grid_AST_and_actual_stage_triangle_SHA_exact=True,geometry_z_1um_witness8_maxabs_m=gerr,all31_to_wheel_sensor_force_error_N=ferr,public04_forward_command_previous6_and_selected_reset_clock_literal_exact=True,ordinary_selected_resets=done_count,integrity_resets=0,unknown_resets=0,raw_events_takeoff_landing_recovery=events.tolist(),raw_all_complete_SHA_local_verified=checked,raw_blocks=records,not_all20k_bodypose_independent_replay=True,not_production_admission=True,new_task_PPO=False,remaining_before_H1_learning=['independent original actor-mean/PPO and new SCUT step reward/event replay for the full20k saved rows','actual new-task production worker/controller/source SDK math RSL CPU admission and original resources','wait for current E3 finite complete closure; then new original writer h1+recovery'],old_CPU_and_native_errors_retained=True)
 put(R/'STEP270_FULL20K_NATIVE180_V3_CORE_CLOCK_GUARD_WITNESS_CPU_ACTUAL.json',row);print(json.dumps({k:x for k,x in row.items() if k not in ('raw_all_complete_SHA_local_verified','raw_blocks')}))
except BaseException:put(R/('STEP270_FULL20K_NATIVE180_V3_CORE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay=True));raise
