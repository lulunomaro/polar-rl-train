"""New component integration fixture, no SDK, model checkpoint or policy."""
from pathlib import Path
from types import SimpleNamespace as S
import sys,json,traceback,hashlib
HERE=Path(__file__).resolve().parent;L=HERE.parent
REPORT=L/'reports/NATIVE_BRIDGE_STATIC31_TERMINAL_RESET_SOURCE_CPU_ACTUAL.json'
assert not REPORT.exists()
for p in [HERE,L/'agent_actual_DR_memory_getter_candidate_v1',
          L/'agent_static_dynamic_delay_contract_candidate',
          L/'root_compact_static_context_candidate',
          L/'root_augmented_world_model_candidate/v4']:
 sys.path.insert(0,str(p))
checks=[]
try:
 import torch
 import actual_DR_memory_getter_v1 as getter
 from native_wheel_leg_bridge_v4 import NativeWheelLegBridge
 from supermimic_wheel_leg_v3.contract import SUPERMIMIC_STATE_KEY as SK,SUPERMIMIC_TRANSITION_KEY as TK
 # Reuse only already-reviewed fixture definitions. Do not import/run its old
 # case registrations or open/write its consumed result.
 fixture_path=L/'agent_actual_DR_memory_getter_candidate_v1/test_actual_DR_memory_getter_CPU_once.py'
 prefix=fixture_path.read_text('utf8').split('\ndef mapping():')[0]
 ns={'__file__':str(fixture_path),'__name__':'new_bridge_fixture_definitions_only'}
 exec(compile(prefix,str(fixture_path),'exec'),ns)
 e,binding,reset,neutral=ns['fixture']()
 torch.set_num_threads(2)
 n=e.num_envs;r=e.scene['robot']
 r.data.root_state_w=torch.zeros(n,13);r.data.root_state_w[:,2]=.3377423;r.data.root_state_w[:,6]=1
 r.data.joint_pos=torch.zeros(n,30);r.data.joint_vel=torch.zeros(n,30)
 r.data.applied_torque=torch.zeros(n,30)
 e._integrated_contact=S(history=torch.zeros(n,3,2,3))
 e.scene=type('Scene',(dict,),{})(e.scene);e.scene.env_origins=torch.zeros(n,3)
 e._sim_step_counter=0;e.physics_dt=.0025;e.step_dt=.01;e.cfg.decimation=4
 e.h1_phase=S(age_control=torch.zeros(n,dtype=torch.long))
 trace=S(frame=None)
 def old_term():
  trace.frame=dict(root13=r.data.root_state_w.clone(),q30=r.data.joint_pos.clone(),
   joint_velocity=r.data.joint_vel.clone(),applied_torque=r.data.applied_torque.clone(),
   executed6=e.action_manager.action.clone(),history5ms=e._integrated_contact.history.clone())
  return 'same-original-term-value'
 e.termination_manager=S(compute=old_term)
 class Vec:
  unwrapped=e
  reset_next=True
  primary_error=False
  seen=None
  output=None
  def step(self,actions):
   self.seen=actions
   clipped=actions.clamp(-6,6);e.action_manager.action=clipped.clone()
   q=e._physics_action_delay.queue;issue=e._sim_step_counter
   for key,sl in [('legs',slice(0,4)),('wheels',slice(4,6))]:
    q.submit(key,clipped[:,sl],issue)
    for tick in range(issue,issue+4):q.apply(key,tick)
   e._sim_step_counter+=4
   r.data.root_state_w[:,2]=.61
   r.data.applied_torque.fill_(2);e._integrated_contact.history.fill_(3)
   result=e.termination_manager.compute()
   assert result=='same-original-term-value'
   if self.primary_error:raise RuntimeError('original vec primary error')
   done=torch.zeros(n,dtype=torch.bool)
   e.h1_phase.age_control+=1
   if self.reset_next:
    ids=torch.tensor([1]);done[ids]=True;reset(ids)
    e.h1_phase.age_control[ids]=0
    r.data.root_state_w[ids,2]=.3377423
    r.data.applied_torque[ids]=0;e._integrated_contact.history[ids]=0
   self.output=(S(),torch.full((n,),-123.),done,{'original':True})
   return self.output
 vec=Vec()
 class Mdp:
  num_joints=30;auxiliary_dim=54;packed_state_dim=127;context_dim=31;action_dim=6
  def reward(self,s,f,a,p):
   assert len(s)==7
   return s[0][...,2]-a.square().mean(-1)*.01
 seen=[]
 bridge=NativeWheelLegBridge(S(env=vec),trace,Mdp(),binding,lambda:seen.append('original before-action hook'))
 bridge.install_exact_pre_reset_aux_hook()
 initial=bridge.init_state()
 assert initial.info[SK]['xi'].shape==(n,31)
 checks.append('all14 actual component fields compact to explicit static31, no fictional joints')
 old=initial.info[SK];xi_before=old['xi'].clone()
 try:bridge.install_exact_pre_reset_aux_hook()
 except ValueError:pass
 else:raise AssertionError('duplicate hook accepted')
 checks.append('duplicate capture hook rejected')
 bridge.before_action();assert seen==['original before-action hook']
 actions=torch.arange(n*6,dtype=torch.float32).reshape(n,6)
 before=actions.clone();out=bridge.step(actions)
 assert vec.seen is actions and torch.equal(actions,before)
 checks.append('same incoming actions object and values delivered to original vec.step')
 tr=out.info[TK];current=out.info[SK]
 assert tr['s1'].shape==(n,127) and current['s'].shape==(n,127)
 assert torch.allclose(tr['s1'][1,2],torch.tensor(.61))
 assert torch.allclose(current['s'][1,2],torch.tensor(.3377423))
 assert torch.all(tr['s1'][1,73:91]==3) and torch.all(tr['s1'][1,91:121]==2)
 assert torch.all(current['s'][1,73:121]==0)
 checks.append('terminal body/contact/torque labels are pre-reset; next current labels are post-reset')
 assert torch.equal(tr['s1'][1,121:127],actions[1].clamp(-6,6))
 assert torch.equal(current['s'][1,121:127],neutral[1])
 checks.append('terminal queue applied6 not overwritten by reset-neutral current6')
 assert torch.equal(tr['xi'],xi_before)
 assert torch.equal(current['xi'][[0,2]],xi_before[[0,2]]) and not torch.equal(current['xi'][1],xi_before[1])
 checks.append('transition uses old static31; selected reset publishes only new row')
 assert torch.equal(out.reward,tr['r']) and torch.equal(out.info['physical_V8_reward_snapshot'],vec.output[1])
 assert not torch.equal(tr['r'],vec.output[1])
 checks.append('real native tracking reward and imagined head agree; original V8 retained separately')
 assert torch.all(current['a_prev'][1]==0) and current['ep_step'].tolist()==[1,0,1]
 checks.append('selected reset clears previous action and native episode history')
 assert set(trace.frame)=={'root13','q30','joint_velocity','applied_torque','executed6','history5ms'}
 assert bridge._terminal_aux54 is None
 checks.append('no extra persisted fulltrace columns; private aux always cleared after success')
 vec.reset_next=False;oldrows=bridge.static.reader.friction_transfer_rows;xi=current['xi'].clone()
 bridge.step(torch.ones(n,6))
 assert bridge.static.reader.friction_transfer_rows==oldrows
 assert torch.equal(bridge.state.info[SK]['xi'],xi)
 checks.append('no reset means no CPU friction transfer and static31 remains cached')
 vec.primary_error=True
 try:bridge.step(torch.zeros(n,6))
 except RuntimeError as ex:assert str(ex)=='original vec primary error'
 else:raise AssertionError('original failure swallowed')
 assert bridge._terminal_aux54 is None
 checks.append('original vec failure propagated and private aux cleared')
 assert not torch.cuda.is_initialized()
 checks.append('CPU-only, no saved native model or policy forward, no GPU/physics/SSH')
 value={'passed':True,'checks':checks,'count':len(checks),'scope':'NEW synthetic component/reset/queue integration only; not actual SDK or dynamics','source':['native_wheel_leg_bridge_v3.py AST-only uninstalled prior draft','native_wheel_leg_bridge_v4.py current candidate; pre-reset privateaux, original27field trace unchanged'],'original_fixture_tests_not_rerun':True,'saved_models_read':False,'GO_fee':False,'real_target_SDK_source_admission':'pending','intent':'Bind correctly timed static/dynamic state and native reward semantics before real GPU task.'}
except BaseException:
 value={'passed':False,'checks_before_failure':checks,'error':traceback.format_exc(),'new_source_and_all_partials_retained':True,'actual_training':False}
 REPORT.write_text(json.dumps(value,indent=2),'utf8');raise
REPORT.write_text(json.dumps(value,indent=2),'utf8')
print(json.dumps({'passed':True,'checks':len(checks),'report':str(REPORT)}))

