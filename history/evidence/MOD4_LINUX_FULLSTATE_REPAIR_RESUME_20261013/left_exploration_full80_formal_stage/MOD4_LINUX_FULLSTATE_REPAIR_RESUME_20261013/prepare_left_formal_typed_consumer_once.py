"""Prepare the first bounded co-adaptation controller; no dispatch or future pass."""
from pathlib import Path
import json,time,hashlib
D=Path(__file__).resolve().parent
s=(D/'left_PPO_discard_admission_parent_v1.py').read_text()
changes={
 'LEFT_PPO_DISCARD_ADMISSION_MANIFEST.json':'LEFT_FORMAL_ADMISSION_MANIFEST.json',
 'LEFT_NATIVE_OWN_FULLSAVE0PPO_PASSED.json':'LEFT_FRESH_OWN_FULLSAVE0PPO_PASSED.json',
 'LEFT_DISCARD4_PPO_ONCE_CONSUMED.json':'LEFT_FORMAL_ONCE_CONSUMED.json',
 'left_discard4PPO_v1':'left_formal3600_v1',
 'left_exploration_worker_v1.py':'left_exploration_worker_v2.py',
 "'--max_iterations','4'":"'--max_iterations','10000'",
 'E1_WAVE50_left_exploration_discard4':'E1_WAVE50_left_exploration_formal3600',
 'begun+600':'begun+3600',
 'Linux_left20k_discard4_PPO_admission_':'Linux_left20k_first_bounded_formal_',
 'left20k_same_branch_discard4_PPO_admission':'left20k_first_bounded_formal_learning',
 'LEFT_DISCARD4_PARENT_ERROR.json':'LEFT_FORMAL_PARENT_ERROR.json',
 'LEFT_DISCARD4_PPO_PASSED.json':'LEFT_FORMAL_SAVED_REVIEW_READY.json',
 'assert delta==[80.]*17':'assert len(set(delta))==1 and delta[0]>0 and delta[0]%20==0',
 "health['control_steps']==96 and health['actual_physics_callbacks']==384":"health['control_steps']==int(delta[0]/20)*24 and health['actual_physics_callbacks']==int(delta[0]/20)*96",
 'discarded_preflight=True,actual_saved_updates=4,envsteps=1920000,callbacks=384,optimizer_step_delta=80':'discarded_preflight=False,actual_saved_updates=int(delta[0]/20),envsteps=int(delta[0]/20)*480000,callbacks=health[\'actual_physics_callbacks\'],optimizer_step_delta=delta[0]',
 'not_own_formal_source=True':'actual_first_formal_window=True'
}
for a,b in changes.items():assert a in s,a;s=s.replace(a,b)
anchor="    assert m['num_envs']==20000 and m['seed']==20260928"
s=s.replace(anchor,anchor+"\n    assert m['actual_native0PPO_independent_CPU_passed'] and m['actual_discard4_PPO_passed'] and m['actual_fresh0PPO_passed']\n    assert m['actual_original80_full1500_data_reviewed'] and m['new_axis_first_formal_seconds']==3600\n    assert m['source_is_fresh_own0PPO_not_discardtrained']")
q=D/'left_first_formal_typed_parent_v1.py';assert not q.exists();compile(s,str(q),'exec');q.write_text(s,encoding='utf8')
(D/'reports/LEFT_FIRST_FORMAL_CONSUMER_CPU_PREPARED.json').write_text(json.dumps(dict(epoch=time.time(),CPU_compiled=True,path=str(q),sha256=hashlib.sha256(q.read_bytes()).hexdigest(),full_native_and_discard_and_fresh_and_original_full80_actual_review_required=True,first_window_seconds=3600,original20k_all_RL_geometry_command_clock_DR_reward_parameters_unchanged=True,only_previously_approved_left_parameter_initialization_axis=True,source_own_fresh0PPO_not_discardtrained=True,max_two_learning_blocks_then_complete_audit=True,formal_GPU_NOT_dispatched=True,qualified50=False),indent=2),encoding='utf8')
print(str(q))
