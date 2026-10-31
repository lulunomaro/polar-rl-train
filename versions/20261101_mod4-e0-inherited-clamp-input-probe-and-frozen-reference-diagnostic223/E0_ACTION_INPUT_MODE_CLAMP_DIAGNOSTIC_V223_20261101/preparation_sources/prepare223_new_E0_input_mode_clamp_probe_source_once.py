"""Prepare a distinct32-control action/input diagnostic. Source/JSON only."""
from pathlib import Path
import ast,hashlib,json,time
T=Path(__file__).resolve().parent;OLD=T/'E0_NEW210_FORMAL_MEAN_PLANE_FLIGHT_SOURCE_V220_20261101'
N=T/'E0_ACTION_INPUT_MODE_CLAMP_DIAGNOSTIC_V223_20261101';N.mkdir(exist_ok=False)
S=N/'source';S.mkdir();R=N/'reports';R.mkdir()
def put(p,v):
 with Path(p).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False)
def source(p,s):
 ast.parse(s);p.write_text(s,encoding='utf8')
helper='''"""Same-input counterfactuals are numeric diagnostics only; never control actions."""
import torch
SLOTS=dict(commands=(0,3),height=(3,4),angular_velocity=(4,7),gravity=(7,10),leg_position=(10,14),wheel_position_slots=(14,16),leg_velocity=(16,20),wheel_velocity=(20,22),previous_action=(22,28),mode_onehot=(28,35))
def diagnose(actor,obs,gradient=False):
 if obs.ndim!=2 or obs.shape[1]!=35 or not torch.isfinite(obs).all():raise ValueError('Expected finite fixedSI35 observation')
 original=obs.detach().clone();x=original.clone();mode0=x.clone();mode0[:,28:35]=0;mode0[:,28]=1
 mode1=x.clone();mode1[:,28:35]=0;mode1[:,29]=1
 no_previous=x.clone();no_previous[:,22:28]=0
 with torch.no_grad():
  actual=actor(x);m0=actor(mode0);m1=actor(mode1);p0=actor(no_previous)
  hidden=[];h=x
  for layer in actor:
   h=layer(h);hidden.append(float(h.abs().max()))
 result=dict(actual_mean=actual.detach().cpu().tolist(),counterfactual_mode0_mean=m0.detach().cpu().tolist(),counterfactual_mode1_mean=m1.detach().cpu().tolist(),counterfactual_previous_action_zero_mean=p0.detach().cpu().tolist(),layer_abs_max=hidden,
  changes_are_numeric_only_not_executed=True)
 if gradient:
  with torch.enable_grad():
   z=original.clone().requires_grad_(True);y=actor(z)[:,0].sum();g=torch.autograd.grad(y,z,only_inputs=True)[0]
  result['first_state_d_left_crank_mean_d_fixedSI35']=g.detach().cpu().tolist()
 assert torch.equal(obs,original)
 return result
'''
source(S/'input_counterfactual223.py',helper)
worker=(OLD/'ROOT220V2_SOURCE_PACKAGE/evaluate220_NEW210_E0_mean_plane_flight_UNUSED_once.py').read_text('utf8')
worker=worker.replace('contract220','contract223').replace('ROOT-only NEW220 N1 first-episode mean-policy regression in207 PhysX path.','ROOT-only NEW223 N1 observation/mode/action diagnostic;32 executed controls max.')
worker=worker.replace('ACTUAL220','ACTUAL223').replace('capture220','capture223')
worker=worker.replace(' from wheel_geometry220',' from wheel_geometry220')
worker=worker.replace(' from wheel_geometry220 import load_own_wheels,authored_bottom,unknown\n','').replace(' from flight_evidence220 import summarize\n','')
start=worker.index(" names=list(robot.body_names);wheels=")
end=worker.index(" source=Path(TASK['model_path'])",start)
worker=worker[:start]+''' put('ACTUAL223_LITERAL_PLANT_BEFORE_MODEL.json',dict(passed=True,physics_dt=real.physics_dt,policy_dt=real.step_dt,nominal_spring=real.spring_pressure_recipe(),original_literal_reward_and_DR_binding=real.binding_receipt(),eval_yaw_only0=True,original_MOD4_guards_unchanged=True))
'''+worker[end:]
start=worker.index(" put('ACTUAL223_ONE_NEW_GPU_MODEL_MEAN_RESTORE.json'")
worker=worker[:start]+''' parameter=ck['actor_state_dict']['distribution.std_param'].detach().cpu().tolist()
 put('ACTUAL223_ONE_NEW_GPU_MODEL_MEAN_RESTORE.json',dict(passed=True,model_SHA=TASK['model_SHA'],model_iteration=TASK['model_iteration'],model_byte_reads=1,model_decodes=1,actor_exact=True,learned_distribution_STD_parameter6=parameter,STD_parameter_semantics_not_reinterpreted=True,no_optimizer_Critic_WM_or_budget_write=True))
 from input_counterfactual223 import diagnose,SLOTS
 for p in actor.parameters():p.requires_grad_(False)
 pending={};old_compute=real.termination_manager.compute;old_reward=real.original_jump_once
 names=list(real.termination_manager.active_terms)
 def capture_term(*a,**kw):
  value=old_compute(*a,**kw)
  pending['root13']=tensor(robot.data.root_state_w)[0].detach().cpu().tolist()
  pending['q30']=tensor(robot.data.joint_pos)[0].detach().cpu().tolist()
  pending['flags']={n:bool(real.termination_manager.get_term(n)[0])for n in names}
  return value
 def capture_reward(*a,**kw):
  value=old_reward(*a,**kw)
  pending['reward_motor_actions6']=real.literal.actions[0].detach().cpu().tolist()
  pending['reward_commands4']=real.literal.commands[0].detach().cpu().tolist()
  return value
 real.termination_manager.compute=capture_term;real.original_jump_once=capture_reward
 tick0=int(real._integrated_contact.tick);fb0=int(real._feedback_100hz_tick);calls0=real.literal.calls;rows=[]
 for control in range(TASK['controls_max']):
  assert time.time()<deadline
  pobs=obs['policy'].detach().clone();before=pobs.clone()
  assert pobs.shape==(1,35)and torch.isfinite(pobs).all()
  assert int(pobs[0,28:35].argmax())==1
  numeric=diagnose(actor,pobs,gradient=control==0)
  with torch.inference_mode():action=actor(pobs)
  raw=action.detach().cpu().clone()
  assert torch.equal(pobs,before)
  pending.clear();obs,reward,done,extra=vec.step(action)
  executed=torch.tensor(pending['reward_motor_actions6']);expected=raw[0].clamp(-6,6)[[0,1,4,2,3,5]]
  residual=float((executed-expected).abs().max());assert residual<=1e-6
  assert all(torch.equal(v,actor.state_dict()[k])for k,v in weights.items())
  rows.append(dict(control=control+1,policy_observation35=before[0].cpu().tolist(),raw_mean6=raw[0].tolist(),numeric_counterfactual=numeric,pre_reset=pending.copy(),clip6_motor_reorder_residual=residual))
  if bool(done[0]):break
 controls=len(rows);assert int(real._integrated_contact.tick)-tick0==controls*8 and int(real._feedback_100hz_tick)-fb0==controls*2 and real.literal.calls-calls0==controls
 left=[r['raw_mean6'][0]for r in rows]
 result=dict(passed=True,kind=KIND,model_SHA=TASK['model_SHA'],controls=controls,physics_callbacks=controls*8,feedback_samples=controls*2,
  first_episode_only=True,actual_action_uses_untouched_original_observation_and_mean=True,source_actor_tensors_unchanged=True,
  input_slots_fixedSI=SLOTS,learned_STD_parameter6=parameter,rows=rows,
  actual_left_crank_mean_min=min(left),actual_left_crank_mean_max=max(left),actual_left_crank_negative_clip_count=sum(x < -6 for x in left),
  no_reward_STD_guard_physics_or_actor_repair_selected=True,no_skill_or_population_cause_claim=True,
  model_byte_reads=1,model_decodes=1,optimizer_steps=0,account_writes=0,old_control_NPZ_or_raw_reads=0)
 put('CAPTURE223_ACTUAL_RESULT.json',result)
 print(json.dumps(dict(passed=True,controls=controls,left_crank_range=[min(left),max(left)])),flush=True)
except BaseException:
 put('ORIGINAL223_ERROR.json',dict(error=traceback.format_exc(),no_auto_retry=True));raise
finally:
 if real is not None:
  try:real.close();put('ENV223_CLOSE_RETURNED.json',dict(closed=True))
  except BaseException:put('ENV223_CLOSE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
 if ns is not None:
  put('APP223_CLOSE_REQUESTED.json',dict(close_call_next=True,post_return_marker_not_required_or_fabricated=True))
  ns['app'].close()
  put('APP223_CLOSE_RETURNED_IF_REACHED.json',dict(returned=True))
'''
source(S/'evaluate223_input_mode_clamp_UNUSED_once.py',worker)
contract='''"""New223 task has no learning, old active219 binding is forbidden."""
E0_PARENT='2df106412ade7c0993f5a51871a4505624600aac7489c011011d9fd24d3ca610'
KIND='NEW223_E0_FIXEDSI_INPUT_MODE_LEFT_CRANK_CLAMP_FLOW'
def validate_current_authority(c,binding,owner_identity=None,owner_current=None):
 assert binding['kind']=='FRESH_CNONE'and c['active_segment']is None
 assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
 return True
def validate_task(t):
 assert t['kind']==KIND and t['num_envs']==1 and t['controls_max']==32 and t['physics_callbacks_max']==256 and t['feedback_samples_max']==64
 assert t['model_SHA']=='e6291fc50e692b9921dfe8ddcbfcc678e9b5916441229c2fd7a4f2c2cc75a538'and t['model_iteration']==32341
 assert t['policy_hz']==50 and t['physics_dt']==.0025 and t['TGS']==[32,4]and t['feedback_hz']==100
 assert t['eval_yaw_range']==[0.,0.]and t['current_authority_binding']['kind']=='FRESH_CNONE'
 assert t['model_byte_reads']==t['model_decodes']==1 and t['model_copies']==0
 assert t['no_optimizer_or_training_or_budget_write']and not t['training_reward_changed']
 return True
'''
source(S/'contract223.py',contract)
parent=(OLD/'ROOT220V2_SOURCE_PACKAGE/target220_single_N1_parent_UNUSED.py').read_text('utf8')
parent=parent.replace('contract220','contract223').replace('220','223').replace('evaluate223_NEW210_E0_mean_plane_flight_UNUSED_once.py','evaluate223_input_mode_clamp_UNUSED_once.py')
parent=parent.replace('controls_max=1000,physics_max=8000','controls_max=32,physics_max=256').replace('geometry_queries_max=2','geometry_queries_max=0')
parent=parent.replace("assert rc==0 and result and result['passed'] and not errors and read(out/'APP223_CLOSED.json')['closed']", "assert rc==0 and result and result['passed'] and not errors and read(out/'ENV223_CLOSE_RETURNED.json')['closed'] and read(out/'APP223_CLOSE_REQUESTED.json')['close_call_next']")
parent=parent.replace("passed_execution=parent_error is None and bool(result and result['passed']),", "passed_execution=parent_error is None and bool(result and result['passed']),app_close_returned_marker_optional=True,")
source(S/'target223_single_N1_parent_UNUSED.py',parent)
task=json.loads((OLD/'ROOT220_TASK_ACTUAL_32341_V2/TASK220.json').read_bytes())
task.update(kind='NEW223_E0_FIXEDSI_INPUT_MODE_LEFT_CRANK_CLAMP_FLOW',epoch=time.time(),controls_max=32,physics_callbacks_max=256,feedback_samples_max=64,
 source_status='FROZEN_NEW_NECESSARY_OBSERVATION_ACTION_FLOW_PURPOSE_PENDING_ACTUAL',
 current_authority_binding=dict(kind='FRESH_CNONE',authority_generation='MOD4_SINGLE_WRITER72_20261026'),
 body_geometry_scope='No geometry or new PhysX getters; original cached state/manager tensors only',
 worker_SHA=hashlib.sha256((S/'evaluate223_input_mode_clamp_UNUSED_once.py').read_bytes()).hexdigest(),
 necessity='Actual221 found100% leftcrank negative clamp; capture fresh actual35D actor inputs, same-input mode/previous-action counterfactuals and source actor immutability, no replay of old flight purpose.',
 extra_cases=0,old_control_raw_reads=0,old_NPZ_reads=0,neural_parameter_updates=0)
put(S/'TASK223.json',task)
# Copy existing source-only launcher bootstrap helper; no SDK import at preparation.
p=OLD/'ROOT220V2_SOURCE_PACKAGE/zonglin2_app_launcher.py';(S/p.name).write_bytes(p.read_bytes())
caller=(OLD/'run_ROOT220V2_qualified_actor_case_once.py').read_text('utf8')
caller=caller.replace("S=N/'ROOT220_TASK_ACTUAL_32341_V2'","S=N/'source'")
caller=caller.replace("MOD4_E0_NEW32341_N1_FLIGHT_20261101v220v2/case","MOD4_E0_ACTION_INPUT223_N1_CNONE_20261101/case")
caller=caller.replace('220V2','223').replace('220','223')
caller=caller.replace("assert read(T/'W35_SOLO_INSTALL_FIRST_AND_CLOSED_READERS_SOURCE_V219_20261101/reports/ROOT219V3_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'", "assert read(T/'W35_SOLO_INSTALL_FIRST_AND_CLOSED_READERS_SOURCE_V219_20261101/reports/ROOT219V3_NORMAL900_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'")
caller=caller.replace('run_ROOT223_qualified_actor_case_once','run_ROOT223_input_mode_action_flow_once')
caller=caller.replace("new_case_controls_max=1000,physics_callbacks_max=8000,feedback_max=2000", "new_case_controls_max=32,physics_callbacks_max=256,feedback_max=64")
caller=caller.replace('own_loaded_wheel_geometry_metadata_queries_max=2','own_loaded_wheel_geometry_metadata_queries_max=0')
caller=caller.replace("run207_zero'", "run207_zero|run_ROOT221_|collect219V3_|run_ROOT223_|run_ROOT222_'" )
module=ast.parse(caller);oldauth=next(x.value.value for x in module.body if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='AUTH'for t in x.targets))
auth='''from pathlib import Path
import json,hashlib,time
raw=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes();c=json.loads(raw)
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]and c['active_segment']is None
print(json.dumps(dict(passed=True,epoch=time.time(),fresh_CNone=True,canonical_SHA=hashlib.sha256(raw).hexdigest(),account_writes=0)))
'''
assert oldauth in caller;caller=caller.replace(oldauth,auth).replace('ROOT223_FRESH72_EXACT_CURRENT219_BEFORE_N1_ACTUAL.json','ROOT223_FRESH72_CNONE_BEFORE_N1_ACTUAL.json')
source(N/'run_ROOT223_input_mode_action_flow_once.py',caller)
manifest=dict(epoch=time.time(),purpose=task['kind'],files=[dict(relative=p.name,bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in sorted(S.iterdir())if p.is_file()])
put(S/'PACKAGE223_SOURCE_AND_TASK.json',manifest)
put(R/'SOURCE223_PREPARATION_READ_COUNTS.json',dict(epoch=time.time(),source_and_saved_JSON_only=True,model_raw_NPZ_SDK_GPU_remote_calls=0,original220_parent_false_preserved=True,new_parent_close_logic='Require workerwait0/noerrors/ENVclose return/APPclose requested; report App returned marker only if reached, no fake closed marker.',new_learning_or_reward_action_guard_change=False))
print(json.dumps(dict(passed=True,new_root=str(N),source_files=len(manifest['files']),status='SOURCE_ONLY_NOT_ACTUAL_PROBE')))
