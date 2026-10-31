"""New220 pure source/metadata/F32-point fixture;no207 or218 fixture replay."""
from pathlib import Path
import ast,copy,hashlib,json,time
import numpy as np
from contract220 import (qualified210,original219_binding,validate_current_authority,validate_task,
 E0_PARENT,W35_INPUT,E0_JOB,KIND,GENERATION)
from wheel_geometry220 import authored_bottom
from flight_evidence220 import summarize
N=Path(__file__).resolve().parent.parent;R=N/'reports'
ID='NEW220_NEW210_MODEL_CURRENT219_BINDING_AND_AUTHORED_PLANE_ENDPOINT_EVIDENCE_CPU_V1'


def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)


def main():
 frozen=json.loads((R/'CPU220_PURPOSE_FROZEN.json').read_bytes())
 assert frozen['purpose_id']==ID and frozen['groups']==3 and frozen['expected_refusals']==11
 assert not (R/'CPU220_ONCE_CONSUMED.json').exists()
 put(R/'CPU220_ONCE_CONSUMED.json',dict(epoch=time.time(),purpose_id=ID,status='STARTED_ONCE_NO_REENTRY',forbidden_calls=0))
 for row in frozen['source_files']:
  p=Path(row['path']);b=p.read_bytes();assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['SHA']
  ast.parse(b.decode('utf8'),filename=str(p))
 worker=(N/'evaluate220_NEW210_E0_mean_plane_flight_UNUSED_once.py').read_text(encoding='utf8')
 geom=(N/'source/wheel_geometry220.py').read_text(encoding='utf8')
 assert "weights_only=False" in worker and 'for control in range(1000)' in worker and "if bool(done[0]):endflags=pending['flags'];ended=True;break" in worker
 assert 'JumpMod4Env(cfg=cfg)' in worker and 'clip_actions=6.' in worker and "ang_vel_z=(0.,0.)" in worker
 assert 'stage.Open' not in geom and 'Usd.Stage.Open' not in geom and 'net_forces_w' not in worker
 assert 'PhysX_getter_calls=0' in geom and "GetPointsAttr().Get()" in geom
 assert "original_reward_command4" in worker and "terminal_flags=" in worker
 groups=[dict(group='source_AST_reused207_plant_no_optimizer_first_episode_and_bounded_stage_metadata',passed=True,
  source_files=len(frozen['source_files']),SDK_imports_or_asset_reads=0)]
 points=np.asarray([[-.1,0.,0.],[.1,0.,0.]],dtype=np.float32)
 a=authored_bottom(points,[0,0,.2],[0,0,0,1],0)
 b=authored_bottom(points,[0,0,.2],[0,np.sqrt(.5),0,np.sqrt(.5)],0)
 assert np.isclose(a,.2) and np.isclose(b,.1) and authored_bottom(None,[0,0,0],[0,0,0,1],0) is None
 contact=np.zeros((6,2,3),dtype=np.float32);contact[0,:,2]=10;contact[3,:,2]=3;contact[5,:,0]=2
 bottom=np.asarray([[0,0],[.01,.01],[.012,.012],[.001,.001],[.01,.01],[.01,.01]],dtype=np.float32)
 flags=[dict(closure=False,mimic=False,time_out=False) for _ in range(6)];flags[5]['closure']=True
 root=np.zeros((6,13),dtype=np.float32);root[:,6]=1;action=np.zeros((6,6),dtype=np.float32)
 nonwheel=np.asarray([0,0,2,0,0,0],dtype=np.float32)
 evidence=summarize(contact,bottom,flags,root,action,nonwheel)
 run=evidence['confirmed_runs'][0]
 assert evidence['status']=='OBSERVED' and run['consecutive_50Hz_endpoints']==2 and run['observed_endpoint_span_s']==.02
 assert run['observed_supported_endpoint_before'] and run['first_contact_reappearance']['control']==4
 assert run['first_contact_reappearance']['stable_landing_claim'] is False
 assert evidence['isolated_single_endpoint_candidates']==[5] and evidence['z_only_would_ignore_lateral_force_rows']==[5]
 assert evidence['wheel_evidence_with_nonwheel_force_gt1N_rows']==[2]
 unknown=summarize(contact,np.full_like(bottom,np.nan),flags,root,action)
 assert unknown['status']=='UNKNOWN_GEOMETRY' and not unknown['confirmed_runs']
 cutflags=copy.deepcopy(flags[:3]);cutflags[-1]['mimic']=True
 censored=summarize(contact[:3],bottom[:3],cutflags,root[:3],action[:3])['confirmed_runs'][0]
 assert censored['right_censored_without_later_both_wheel_contact'] and censored['terminal_flags_in_air'][0]['flags']['mimic']
 groups.append(dict(group='synthetic_F32_xyzw_authored_support_unknown_geometry_two_endpoints_contact_reappearance_and_censoring',
  passed=True,synthetic_points_never_used_as_actual_collision_geometry=True,
  endpoint_count2_observed_span_s=.02,old207_physical_or_model_fixture_replayed=False))
 D=R/'SYNTHETIC220_SCHEMA_ONLY';D.mkdir(exist_ok=False);fake='e'*64
 row=dict(SHA=fake,bytes=22961801,source_SHA=E0_PARENT,saved_iteration=32341,Adam_min=648340,Adam_max=648340)
 closing=dict(synthetic_fixture_only=True,passed_collection=True,
  owner_closed=dict(canonical_None=True,shared_locks_free=True,cohort_final=dict(original_cost_settled=True),owner_exit=dict(original_cost_settled=True)),
  roles=dict(e0_72=dict(qualified_formal=True,errors=[],private_EX_free=True,
   original_node_terminal=dict(row=dict(returncode=0)),original_node_exit=dict(all_own_children_waited=True,private_EX_released=True),
   final=dict(passed=True,actual_new_PPO_updates=275,final=row))),
  formals=dict(e0_72=dict(SHA=fake,bytes=22961801,source=E0_JOB+'/production/model_final_complete.pt',transfers=1,two_host_SHA_equal=True)))
 cpu=dict(synthetic_fixture_only=True,passed=True,old_model_reads=0,roles=dict(e0_72=dict(passed=True,SHA=fake,
  saved_iteration=32341,Adam17_step=648340,new_PPO_updates=275,actor35_critic38_STD6=True,
  complete_task_and_DR_state_present=True,save_at_or_after_requested_deadline=True)))
 def pair(name,c,u):
  x=D/(name+'_CLOSING_SYNTHETIC.json');y=D/(name+'_CPU_SYNTHETIC.json');put(x,c);put(y,u);return x,y
 x,y=pair('positive',closing,cpu);model=qualified210(x,y,synthetic_fixture=True)
 assert model['model_path']==E0_JOB+'/production/model_final_complete.pt' and model['model_iteration']==32341
 owner=dict(pid=123,creation=42.,root='/synthetic/ownerV3')
 go=dict(original_owner_pid=123,original_owner_creation=42.,run_id='SELECTED_ROOT_V3_SYNTHETIC',role_key='w35_72',
  source_model_SHA=W35_INPUT,input_Adam=648360,one_original_writer=True,manifest_SHA='c'*64,
  GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d')
 launch=dict(owner=owner,run_id=go['run_id'],specs=dict(w35_72=dict(manifest_SHA='c'*64,GPU_UUID=go['GPU_UUID'])))
 state=dict(current_owner_matched=True,canonical_None=False,current=dict(go=dict(w35_72=go)))
 lp=D/'SELECTED_ANY_PREFIX_LAUNCH_SYNTHETIC.json';sp=D/'SELECTED_ANY_PREFIX_STATE_SYNTHETIC.json';put(lp,launch);put(sp,state)
 binding=original219_binding(lp,sp)
 c=dict(authority_generation=GENERATION,authorized_training_seconds=2268000,new_authority_budget_extensions=[],active_segment=dict(owner_parent_pid=123))
 assert validate_current_authority(c,binding,owner,state['current'])
 cn=copy.deepcopy(c);cn['active_segment']=None
 assert validate_current_authority(cn,dict(kind='FRESH_CNONE',authority_generation=GENERATION))
 task=dict(kind=KIND,target_host='72',num_envs=1,controls_max=1000,physics_callbacks_max=8000,feedback_samples_max=2000,
  policy_hz=50,physics_dt=.0025,TGS=[32,4],feedback_hz=100,**model,
  GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842',no_optimizer_or_training_or_budget_write=True,
  eval_yaw_range=[0.,0.],vx_range=[-2.1,2.1],height_range=[.12,.15],model_byte_reads=1,model_decodes=1,model_copies=0,current_authority_binding=binding)
 assert validate_task(task)
 refused=[]
 def refuse(name,call):
  try:call()
  except (AssertionError,ValueError,KeyError):refused.append(name);return
  raise AssertionError('Expected refusal '+name)
 changes=[]
 cc=copy.deepcopy(closing);cc['roles']['e0_72']['final']['final']['saved_iteration']=32066;changes.append(('old32066',cc,cpu))
 uu=copy.deepcopy(cpu);uu['passed']=False;changes.append(('newCPU_false',closing,uu))
 uu=copy.deepcopy(cpu);uu['roles']['e0_72']['SHA']='f'*64;changes.append(('CPU_other_SHA',closing,uu))
 cc=copy.deepcopy(closing);cc['formals']['e0_72']['source']='/synthetic/W35/model_final_complete.pt';changes.append(('foreign_model_path',cc,cpu))
 cc=copy.deepcopy(closing);cc['formals']['e0_72']['SHA']=W35_INPUT;changes.append(('W35_not_E0_model',cc,cpu))
 for name,cc,uu in changes:
  xx,yy=pair(name,cc,uu);refuse(name,lambda xx=xx,yy=yy:qualified210(xx,yy,synthetic_fixture=True))
 refuse('synthetic_not_production_qualification',lambda:qualified210(x,y))
 stale=copy.deepcopy(c);stale['active_segment']['owner_parent_pid']=210
 refuse('closed210_owner_not_current219',lambda:validate_current_authority(stale,binding,owner,state['current']))
 refuse('blind_CNone_while219active',lambda:validate_current_authority(c,dict(kind='FRESH_CNONE',authority_generation=GENERATION)))
 wrong=copy.deepcopy(state['current']);wrong['go']['w35_72']['run_id']='OLD_FAILED_219'
 refuse('stale_failed219_GO',lambda:validate_current_authority(c,binding,owner,wrong))
 badtask=copy.deepcopy(task);badtask['GPU_UUID']=go['GPU_UUID']
 refuse('do_not_touch_current219_training_GPU',lambda:validate_task(badtask))
 badtask=copy.deepcopy(task);badtask['model_SHA']=E0_PARENT
 refuse('old_E0_parent_not_new210',lambda:validate_task(badtask))
 assert len(refused)==11
 groups.append(dict(group='dynamic_NEW210_model_and_selected_current_owner_GO_schema',passed=True,refused=refused,
  any_ROOT_selected_success_prefix_supported=True,canonical_budget_or_model_reads=0))
 put(R/'CPU220_SOURCE_EVIDENCE_AND_BINDING_ACTUAL.json',dict(epoch=time.time(),purpose_id=ID,passed=True,
  group_count=3,expected_refusals=11,groups=groups,synthetic_metadata_and_points_only=True,
  actual_target_or_new_model_evaluation_run=False,old207_218_fixture_replays=0,
  PT_NPZ_USD_raw_SDK_GPU_SSH_Git_reads_or_calls=0,no_new_physics_training_gate=True))
 print(json.dumps(dict(passed=True,groups=3,refusals=11,forbidden_calls=0,old207_218_replays=0)))


if __name__=='__main__':main()
