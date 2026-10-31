from pathlib import Path
import ast,hashlib,json,shutil,time
T=Path(__file__).resolve().parent
N=T/'E0_CANDIDATE225_CONTROLLED_PHYSICAL_REGRESSION_V230_20261101'
S=N/'source';R=N/'reports'
S.mkdir(parents=True,exist_ok=False);R.mkdir()
def put(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf8')
base=T/'E0_ACTION_INPUT_MODE_CLAMP_DIAGNOSTIC_V223_20261101'
task=json.loads((base/'source/TASK223.json').read_bytes())
task.update(kind='NEW230_CANDIDATE225_STAND_FORWARD_REVERSE_LITERAL_JUMP_REGRESSION',
 model_path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_CANDIDATE225_REGRESSION230_20261101/case/model_candidate225.pt',
 model_SHA='17696bc47c494ba84a0bd872c4e9be9595410045e90f9abd1a1949d701e9cbaf',model_bytes=22956985,
 num_envs=10,controls_max=2000,physics_callbacks_max=16000,feedback_samples_max=4000,
 worker_seconds=1680,parent_wait_seconds=1800,model_copies=1,
 cases=[dict(name='standing',env=0,vx=0.,height=.25),dict(name='forward',env=0,vx=.3,height=.25),
        dict(name='reverse',env=0,vx=-.3,height=.25),dict(name='literal_jump',env=1,vx=-.39473843574523926,height=.1312776654958725)],
 controls_per_case_max=500,body_geometry_scope='Two bounded already-loaded wheel metadata queries; original cached reward contact tensor reused',
 candidate_CPU_report=str(T/'E0_CAD_MEAN_OUTPUT_REPAIR_CANDIDATE_SOURCE_V225_20261101/reports/ROOT225_ACTUAL_BOUND_COPY_AND_OWN_READBACK_CPU_RETURNED_ACTUAL.json'),
 necessity='Independent repaired-copy short physical regression after actual action and optimizer metadata proof; inspect changed action history before any learning.',
 source_status='FROZEN_NEW_PHYSICAL_REGRESSION_PURPOSE_NOT_LEARNING',extra_cases=3,
 evaluation_scope='Four first episodes, max10s each, fresh10-env DR. Controlled cues only, original ground/JUMP reward routing. Not full expert graduation.',
 no_reward_STD_guard_physics_or_actor_repair_selected=False)
contract='''KIND='NEW230_CANDIDATE225_STAND_FORWARD_REVERSE_LITERAL_JUMP_REGRESSION'
def validate_current_authority(c,binding,owner_identity=None,owner_current=None):
 assert binding['kind']=='FRESH_CNONE' and c['active_segment'] is None
 assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
 return True
def validate_task(t):
 assert t['kind']==KIND and t['num_envs']==10 and t['controls_per_case_max']==500 and t['controls_max']==2000
 assert t['model_SHA']=='17696bc47c494ba84a0bd872c4e9be9595410045e90f9abd1a1949d701e9cbaf' and t['model_bytes']==22956985
 assert t['model_iteration']==32341 and t['actual_17Adam_step']==648340
 assert t['policy_hz']==50 and t['physics_dt']==.0025 and t['TGS']==[32,4] and t['feedback_hz']==100
 assert t['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842' and t['current_authority_binding']['kind']=='FRESH_CNONE'
 assert t['model_byte_reads']==t['model_decodes']==1 and t['model_copies']==1
 assert t['no_optimizer_or_training_or_budget_write'] and not t['training_reward_changed']
 assert [(x['name'],x['env']) for x in t['cases']]==[('standing',0),('forward',0),('reverse',0),('literal_jump',1)]
 return True
'''
(S/'contract230.py').write_text(contract,encoding='utf8')
worker=r'''from pathlib import Path
import argparse,hashlib,io,json,os,runpy,sys,time,traceback
sys.path.insert(0,str(Path(__file__).resolve().parent))
from contract230 import validate_task,KIND
p=argparse.ArgumentParser();p.add_argument('--task',type=Path,required=True);a=p.parse_args()
P=a.task.resolve().parent;TASK=json.loads(a.task.read_bytes());validate_task(TASK)
assert TASK['actual_parent_private_EX_and_authority_admitted'] is True
assert os.environ.get('CUDA_VISIBLE_DEVICES')==TASK['GPU_UUID']
assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==TASK['worker_SHA']
ROOT=Path(TASK['qualified197_package_root']);payload=ROOT/'payload';OUT=P/'actual_capture';OUT.mkdir(exist_ok=False)
def put(n,v):
 with(OUT/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
deadline=time.time()+TASK['worker_seconds'];real=ns=None
try:
 original=json.loads((ROOT/'E0_original_run_manifest_frozen_v1.json').read_bytes())['env']
 for key in list(os.environ):
  if key.startswith('RM_') or key in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[key]
 os.environ.update({k:str(v)for k,v in original.items()if k not in('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')})
 os.environ.update(RM_MOD4_USD=str(payload/'job0/assets/robot.usd'),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_KEEP_STD='1',RM_JUMP_SCRIPT_PROB='0',RM_GYRO_CURRICULUM='0',RM_HEADING_CMD='0',RM_HEIGHT_MIN='.25',RM_HEIGHT_MAX='.25',RM_EPISODE_S='20',RM_HIDDEN_DIMS='256,128,64',RM_VALUE_LOSS_COEF='2.0',RM_SCHEDULE='adaptive',RM_ENTROPY_COEF='.005',RM_DESIRED_KL='.01',RM_RESCUE_DEADLINE=str(deadline),RM_RESCUE_STOP_FILE=str(OUT/'UNREQUESTED_STOP.json'))
 os.environ['MOD4_RESUME_QUEUE_CONTROL_US']='20000'
 kit=OUT/'kit_isolation';kit.mkdir();(kit/'data').mkdir();(kit/'DerivedDataCache').mkdir();(kit/'data/user.config.json').write_text('{}')
 os.environ['MOD4_188_OWN_KIT_ROOT']=str(kit);os.environ['MOD4_188_JOB_ROOT']=str(P)
 runtime=payload/'job0/runtime/isaac/mod4';sys.path[:0]=[str(P),str(ROOT),str(payload/'lib'),str(runtime),str(payload/'job0/runtime')]
 entry=runtime/'train_H1_ground_prelaunch_fullstate_v2.py';sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','10','--seed','27','--log_root',str(OUT/'unused_learning_logs')]
 ns=runpy.run_path(str(entry),run_name='capture230_config_only_no_old_main')
 import numpy as np
 import torch
 from spring_nominal_sdk_readback import tensor
 sys.modules.pop('directional_spin_runtime',None)
 import mixed209_sdk as sdk
 from wheel_geometry220 import load_own_wheels,authored_bottom,unknown
 from flight_evidence220 import summarize
 cfg=ns['Mod4EnvCfg']();cfg.scene.num_envs=10;cfg.seed=27;cfg.sim.device='cuda:0';sdk.configure(cfg)
 real=sdk.Mixed209Env(cfg=cfg);real._physics_action_delay.queue.control_us=20000
 vec=ns['RslRlVecEnvWrapper'](real,clip_actions=6.);robot=real.scene['robot'];cmd=real.command_manager.get_term('twist')
 assert real.physics_dt==.0025 and real.step_dt==.02 and real.cfg.decimation==8
 assert real.spring_pressure_recipe()['nominal_stiffness_N_m']==2000
 assert real.cfg.terminations.closure.params['threshold']==.002 and real.cfg.terminations.mimic.params['threshold']==.01
 assert int(real._mixed209_flat.sum())==1 and real._mod4_mode_bit[:2].tolist()==[0,1]
 assert real.literal.penalised_contact_indices.numel()>0
 wheels=[list(robot.body_names).index(x)for x in('left_wheel','right_wheel')]
 assert real.literal.feet_indices.cpu().tolist()==wheels
 spawn=getattr(cfg.scene.ground.spawn.func,'__name__','UNKNOWN');plane_z=float(cfg.scene.ground.init_state.pos[2])
 if spawn!='spawn_local_native_plane':plane_z+=.5*float(cfg.scene.ground.spawn.size[2])
 assert plane_z==0.
 put('ACTUAL230_ORIGINAL_MIXED_REWARD_AND_PLANT.json',dict(passed=True,binding=real.binding_receipt(),spring=real.spring_pressure_recipe(),ground_mask=real._mixed209_flat.cpu().tolist(),fresh10env_DR_not_checkpoint_slice=True,controlled_cues_only_no_state_or_force_injection=True,original_guards_unchanged=True))
 try:
  import omni.usd
  stage=omni.usd.get_context().get_stage();rp=cfg.scene.robot.prim_path.replace('{ENV_REGEX_NS}','/World/envs/env_0').replace('env_.*','env_0')
  geometry,support=load_own_wheels(stage,rp)
 except Exception as exc:
  geometry=[unknown(x,'STAGE_METADATA_EXCEPTION',error=str(exc))[0]for x in('left_wheel','right_wheel')];support=[None,None]
 put('ACTUAL230_OWN_ALREADY_LOADED_WHEEL_GEOMETRY.json',dict(wheels=geometry,metadata_queries=2,stage_open_calls=0,extra_PhysX_getters=0))
 with Path(TASK['model_path']).open('rb')as f:raw=f.read()
 assert len(raw)==TASK['model_bytes'] and hashlib.sha256(raw).hexdigest()==TASK['model_SHA']
 ck=torch.load(io.BytesIO(raw),map_location='cuda:0',weights_only=False);del raw
 assert ck['iter']==32341 and ck['candidate225_repair_metadata']['status']=='ACTUAL_BOUND_COPY_PENDING_PHYSICAL_REGRESSION_NOT_LEARNING_ADMITTED'
 steps=[float(x['step'])for x in ck['optimizer_state_dict']['state'].values()];assert len(steps)==17 and min(steps)==max(steps)==648340
 actor=torch.nn.Sequential(torch.nn.Linear(35,256),torch.nn.ELU(),torch.nn.Linear(256,128),torch.nn.ELU(),torch.nn.Linear(128,64),torch.nn.ELU(),torch.nn.Linear(64,6)).to(real.device)
 weights={k.removeprefix('mlp.'):v for k,v in ck['actor_state_dict'].items()if k.startswith('mlp.')};actor.load_state_dict(weights,strict=True);actor.eval()
 for q in actor.parameters():q.requires_grad_(False)
 STD=ck['actor_state_dict']['distribution.std_param'].cpu().tolist();del ck
 put('ACTUAL230_CANDIDATE225_ONE_GPU_READ_RESTORE.json',dict(passed=True,SHA=TASK['model_SHA'],model_bytes=TASK['model_bytes'],physical_byte_reads=1,decodes=1,actor_exact=all(torch.equal(v,actor.state_dict()[k])for k,v in weights.items()),STD6=STD,optimizer_constructs=0,optimizer_steps=0,Critic_WM_forwards=0))
 cue=None;selected=0;pending={};old_update=cmd._update_command
 def apply_cue():
  if cue is None:return
  i=cue['env'];cmd.vel_command_b[i,:]=torch.tensor([cue['vx'],0.,0.],device=real.device)
  for name in('is_standing_env','is_heading_env','is_pure_spin','is_moving_spin','is_transition_spin'):getattr(cmd,name)[i]=False
  cmd.signed_yaw[i]=0.;cmd.time_left[i]=20.;sdk.task.height_cmd(real)[i,0]=cue['height']
 def update_command():old_update();apply_cue()
 cmd._update_command=update_command
 old_compute=real.termination_manager.compute;old_reward=real.original_jump_once;names=list(real.termination_manager.active_terms)
 def compute(*args,**kw):
  value=old_compute(*args,**kw);i=selected
  for key,value0 in [('position',robot.data.body_pos_w),('quat_xyzw',robot.data.body_quat_w),('root13',robot.data.root_state_w),('q30',robot.data.joint_pos)]:pending[key]=tensor(value0)[i].detach().cpu().numpy().copy()
  pending['flags']={n:bool(real.termination_manager.get_term(n)[i])for n in names};return value
 def reward(*args,**kw):
  value=old_reward(*args,**kw);i=selected
  pending['wheel_force_xyz']=real.literal.contact_forces[i,real.literal.feet_indices,:].cpu().numpy().copy()
  pending['nonwheel_force_norm_max']=float(torch.linalg.vector_norm(real.literal.contact_forces[i,real.literal.penalised_contact_indices,:],dim=-1).max())
  pending['executed_motor6']=real.literal.actions[i].cpu().numpy().copy();return value
 real.termination_manager.compute=compute;real.original_jump_once=reward
 results=[];total=0
 for cue in TASK['cases']:
  selected=cue['env'];real.reset();apply_cue();obs=vec.get_observations();frames=[];rewards=[];bvx=[]
  assert obs['policy'].shape==(10,35) and int(obs['policy'][selected,28:35].argmax())==(0 if selected==0 else 1)
  tick0=int(real._integrated_contact.tick);fb0=int(real._feedback_100hz_tick);calls0=real.literal.calls
  for control in range(TASK['controls_per_case_max']):
   assert time.time()<deadline
   with torch.inference_mode():action=actor(obs['policy'])
   rawaction=action[selected].cpu().numpy().copy();pending.clear();obs,rew,done,extra=vec.step(action)
   assert np.isfinite(rawaction).all() and torch.isfinite(obs['policy']).all()
   expected=np.clip(rawaction,-6.,6.)[[0,1,4,2,3,5]];assert np.max(np.abs(pending['executed_motor6']-expected))<=1e-6
   bottom=[authored_bottom(support[j],pending['position'][w],pending['quat_xyzw'][w],plane_z)for j,w in enumerate(wheels)]
   frames.append(dict(pending,raw_action=rawaction,bottom=np.array([np.nan if x is None else x for x in bottom],dtype=np.float32)))
   q=pending['root13'][3:7];v=pending['root13'][7:10];q=q/np.linalg.norm(q);u=-q[:3];t=2*np.cross(u,v);local=v+q[3]*t+np.cross(u,t);bvx.append(float(local[0]));rewards.append(float(rew[selected]));total+=1
   if bool(done[selected]):break
  count=len(frames);assert count>0 and int(real._integrated_contact.tick)-tick0==count*8 and int(real._feedback_100hz_tick)-fb0==count*2 and real.literal.calls-calls0==count
  assert all(torch.equal(v,actor.state_dict()[k])for k,v in weights.items())
  root=np.stack([f['root13']for f in frames]);rawa=np.stack([f['raw_action']for f in frames]);bottoms=np.stack([f['bottom']for f in frames]);flags=[f['flags']for f in frames]
  flight=summarize(np.stack([f['wheel_force_xyz']for f in frames]),bottoms,flags,root,rawa,np.array([f['nonwheel_force_norm_max']for f in frames]))
  q0=root[0,3:7];q1=root[-1,3:7]
  def yaw(q):x,y,z,w=q;return float(np.arctan2(2*(w*z+x*y),1-2*(y*y+z*z)))
  yaw_delta=float(np.arctan2(np.sin(yaw(q1)-yaw(q0)),np.cos(yaw(q1)-yaw(q0))))
  artifact=OUT/('CASE230_'+cue['name']+'.npz');np.savez_compressed(artifact,body_position_w=np.stack([f['position']for f in frames]),body_quat_xyzw=np.stack([f['quat_xyzw']for f in frames]),root13=root,q30=np.stack([f['q30']for f in frames]),raw_action6=rawa,wheel_contact_xyz=np.stack([f['wheel_force_xyz']for f in frames]),authored_wheel_bottom=bottoms)
  with artifact.open('rb')as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
  result=dict(name=cue['name'],command=cue,controls=count,seconds=count*.02,requested_window_complete=count==500,first_episode_original_terminal_flags=flags[-1],reward_sum=sum(rewards),BODY_vx_MAE=float(np.mean(np.abs(np.array(bvx)-cue['vx']))),BODY_vx_mean=float(np.mean(bvx)),yaw_delta_rad=yaw_delta,raw_left_crank_range=[float(rawa[:,0].min()),float(rawa[:,0].max())],raw_abs_gt6_count_by_channel=(np.abs(rawa)>6).sum(0).astype(int).tolist(),endpoint_flight=flight,producer=dict(path=str(artifact),bytes=artifact.stat().st_size,SHA=sha,transfer='METADATA_ONLY'),not_full_expert_or270_graduation=True)
  results.append(result);put('CASE230_'+cue['name']+'_RESULT.json',result)
 put('CAPTURE230_ACTUAL_RESULT.json',dict(passed=True,kind=KIND,model_SHA=TASK['model_SHA'],cases=results,controls=total,physics_callbacks=total*8,feedback_samples=total*2,model_byte_reads=1,model_decodes=1,optimizer_steps=0,account_writes=0,original_frozen_E0_or_unrepaired_branch_writes=0,short_regression_not_learning_or_full_skill=True))
 print(json.dumps(dict(passed=True,cases=[dict(name=r['name'],controls=r['controls'],flight=r['endpoint_flight']['status'],flags=r['first_episode_original_terminal_flags'])for r in results])),flush=True)
except BaseException:
 put('ORIGINAL230_ERROR.json',dict(error=traceback.format_exc(),no_auto_retry=True));raise
finally:
 if real is not None:
  try:real.close();put('ENV230_CLOSE_RETURNED.json',dict(closed=True))
  except BaseException:put('ENV230_CLOSE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
 if ns is not None:
  put('APP230_CLOSE_REQUESTED.json',dict(close_call_next=True,post_return_marker_optional=True));ns['app'].close();put('APP230_CLOSE_RETURNED_IF_REACHED.json',dict(returned=True))
'''
(S/'evaluate230_candidate225_regression_UNUSED_once.py').write_text(worker,encoding='utf8')
parent=(base/'source/target223_single_N1_parent_UNUSED.py').read_text(encoding='utf8').replace('223','230').replace("assert rc==0 and result", "assert rc==0 and result")
parent=parent.replace('controls_max=32,physics_max=256','controls_max=2000,physics_max=16000').replace('geometry_queries_max=0','geometry_queries_max=2').replace('timeout=900','timeout=1800')
parent=parent.replace('evaluate230_input_mode_clamp_UNUSED_once.py','evaluate230_candidate225_regression_UNUSED_once.py')
parent=parent.replace('model_artifact_transfers=0','model_artifact_transfers=1')
(S/'target230_single_N1_parent_UNUSED.py').write_text(parent,encoding='utf8')
for name in ('wheel_geometry220.py','flight_evidence220.py'):
 shutil.copyfile(T/'E0_NEW210_FORMAL_MEAN_PLANE_FLIGHT_SOURCE_V220_20261101/source'/name,S/name)
task['worker_SHA']=hashlib.sha256((S/'evaluate230_candidate225_regression_UNUSED_once.py').read_bytes()).hexdigest();put(S/'TASK230.json',task)
rows=[]
for p in sorted(S.iterdir()):
 b=p.read_bytes()
 if p.suffix=='.py':ast.parse(b,filename=str(p))
 rows.append(dict(relative=p.name,bytes=len(b),SHA=hashlib.sha256(b).hexdigest()))
put(S/'PACKAGE230_SOURCE_AND_TASK.json',dict(kind='NEW230_FROZEN_REGRESSION_SOURCE',files=rows))
caller=(T/'E0_ORIGINAL_ACTION_CLOSURE_METADATA_V229_20261101/run_ROOT229_original_action_closure_metadata_once.py').read_text(encoding='utf8').replace('229','230').replace('MOD4_E0_ACTION_OPTIMIZER_META230_CNONE_20261101','MOD4_E0_CANDIDATE225_REGRESSION230_20261101')
caller=caller.replace("task['model_SHA']=='e6291fc50e692b9921dfe8ddcbfcc678e9b5916441229c2fd7a4f2c2cc75a538'", "task['model_SHA']=='17696bc47c494ba84a0bd872c4e9be9595410045e90f9abd1a1949d701e9cbaf'")
caller=caller.replace("q['roles']['e0_72']['SHA']==task['model_SHA']", "q['roles']['e0_72']['SHA']=='e6291fc50e692b9921dfe8ddcbfcc678e9b5916441229c2fd7a4f2c2cc75a538'")
caller=caller.replace("T/'E0_ACTUAL_ACTION_OPTIMIZER_BINDING_METADATA_V228_20261101/reports/ROOT228V2_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json'", "T/'E0_ORIGINAL_ACTION_CLOSURE_METADATA_V229_20261101/reports/ROOT229_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json'")
caller=caller.replace("GPU_model_byte_reads=0,GPU_model_decodes=0", "GPU_model_byte_reads=1,GPU_model_decodes=1")
caller=caller.replace('new_case_controls_max=0,physics_callbacks_max=0,feedback_max=0','new_case_controls_max=2000,physics_callbacks_max=16000,feedback_max=4000')
caller=caller.replace('own_loaded_wheel_geometry_metadata_queries_max=0','own_loaded_wheel_geometry_metadata_queries_max=2')
caller=caller.replace('timeout=1800','timeout=2400')
needle="  finally:sf.close()\n\n  actual="
assert needle in caller
caller=caller.replace(needle,"  finally:sf.close()\n\n  candidate=T/'E0_CAD_MEAN_OUTPUT_REPAIR_CANDIDATE_SOURCE_V225_20261101/actual_cpu_candidate_from_e629/model_candidate225.pt'\n  sf=client.open_sftp()\n  try:sf.put(str(candidate),J+'/model_candidate225.pt')\n  finally:sf.close()\n  verify=\"from pathlib import Path\\nimport hashlib,json\\np=Path(v['path'])\\nwith p.open('rb')as f:sha=hashlib.file_digest(f,'sha256').hexdigest()\\nassert p.stat().st_size==22956985 and sha==v['SHA']\\nprint(json.dumps(dict(passed=True,bytes=p.stat().st_size,SHA=sha,new_candidate_uploads=1,target_postcopy_integrity_reads=1,old_models_read=0)))\"\n  put('ROOT230_ONE_CANDIDATE_UPLOAD_POSTCOPY_ACTUAL.json',d.code(client,d.PY72,verify,dict(path=J+'/model_candidate225.pt',SHA=task['model_SHA']),timeout=90))\n\n  actual=")
caller=caller.replace("model_copies=0,artifact_transfers=0,GUI=False", "model_copies=1,artifact_transfers=0,GUI=False")
caller=caller.replace('neural_forwards=0','neural_forwards_max=2000').replace('NN_actor_only=True','NN_actor_only=True')
caller=caller.replace('local_PT_reads=0','local_PT_upload_stream_reads=1')
caller=caller.replace("  task=read", "  task=read")
ast.parse(caller)
(N/'run_ROOT230_candidate225_physical_regression_once.py').write_text(caller,encoding='utf8')
put(R/'ROOT230_SOURCE_BEFORE_USE_AND_COUNT_ADMISSION_FROZEN.json',dict(epoch=time.time(),passed_source_syntax=True,case_count=4,max_controls=2000,max_physics_callbacks=16000,model_new_candidate_upload_streams=1,target_postcopy_integrity=1,GPU_model_byte_reads=1,GPU_model_decodes=1,old_model_or_raw_NPZ_reads=0,already_loaded_geometry_queries=2,optimizer_or_learning_or_budget=0,original_reward_and_physics_sources_unchanged=True,source_only_until_actual_return=True,all_Python_AST_checked=True))
print(json.dumps(dict(passed=True,source=str(N),files=len(rows),no_model_SDK_remote_reads=True)))
