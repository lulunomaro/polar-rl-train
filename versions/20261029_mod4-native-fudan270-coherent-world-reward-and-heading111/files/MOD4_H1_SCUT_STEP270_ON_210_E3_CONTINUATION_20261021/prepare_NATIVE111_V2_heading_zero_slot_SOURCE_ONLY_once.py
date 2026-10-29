"""Select bounded heading encoding without disturbing existing tilt/goal norms."""
from pathlib import Path
import ast,hashlib,json,time
T=Path(__file__).resolve().parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
A=L/'native111_coherent_world_task_reward_source_v1';B=L/'native111_coherent_world_task_reward_source_v2'
assert not B.exists();B.mkdir();(B/'reports').mkdir()
old=(A/'native_fudan_step_adapter_candidate_v2.py').read_text(encoding='utf8')
start=old.index('    # Goal and goal normalizer stay byte-identical.')
end=old.index('    def relative_features(self,state,frames):',start)
new=old[:start]+'''    # yaw_mat(R).T @ R has an identically zero (1,0) entry, barring
    # FP32 roundoff. In the existing 6D column encoding this is feature3
    # after the height. Replace only that redundant zero with .01*yaw/pi.
    # .01 is the inherited RunningNorm eps, giving a bounded <=1 signal
    # even when the old zero slot's variance/count is frozen. Goal/tilt,
    # all weights, all norm tensors and all three optimizers stay inherited.
    # Wrapped yaw has a declared representation seam at +/-pi; it is not
    # an independent RNG stream, a model reset, or a sine-only heading alias.
    @staticmethod
    def _with_task_heading(value,state):
        R=state[1]
        yaw=torch.atan2(R[...,1,0],R[...,0,0])
        return torch.cat((value[...,:3],(.01*yaw/math.pi).unsqueeze(-1),value[...,4:]),-1)
    def obs(self,state,previous_action,context,frames):
        return self._with_task_heading(super().obs(state,previous_action,context,frames),state)
    def critic_features(self,state,frames,normalized_context):
        return self._with_task_heading(super().critic_features(state,frames,normalized_context),state)
'''+old[end:]
assert old.count("actor_orientation_frame='full_world_rotation6d'")==1
new=new.replace("actor_orientation_frame='full_world_rotation6d'","actor_orientation_frame='original_yaw_invariant_tilt_plus_bounded_explicit_world_yaw_in_redundant_zero_slot'")
new=new.replace('from supermimic_wheel_leg_v3.geometry import mat_to_6d\n','')
ast.parse(new)
for name in ('mod4_fudan_contact_phase_reward_candidate_v2.py','OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json'):(B/name).write_bytes((A/name).read_bytes())
(B/'native_fudan_step_adapter_candidate_v2.py').write_text(new,encoding='utf8',newline='\n')
contract=json.loads((A/'SOURCE_DELTA_AND_BEFORE_USE_CONTRACT_111_V1.json').read_bytes())
contract.update(kind='SOURCE_ONLY_NEW_HUMAN_TASK_COHERENCE_REPAIR_V2',epoch=time.time(),selection='V1_NOT_SELECTED_full_rotation_changes_all_tilt_slots_and_can_create_200_normalized_input_change_at_the_inherited_eps_floor',
 heading_encoding='observation_and_critic_feature3=.01*atan2(R10,R00)/pi; original zero slot only',
 inherited_frozen_zero_slot_normalized_absolute_signal_bound=1.,
 preserved_goal_and_all_remaining_observation_and_critic_features=True,
 limits_additional=['Wrapped yaw has a representation seam at +/-pi, explicitly tested on both sides.','The <=1 normalized bound uses a zero-mean/zero-variance historical slot; actual model norm readback is required before runtime use.','Initial slot variance/mean FP32 roundoff is not assumed literally zero before actual target admission.'])
contract['changes']=[dict(name=n,SHA=hashlib.sha256((B/n).read_bytes()).hexdigest()) for n in ('mod4_fudan_contact_phase_reward_candidate_v2.py','native_fudan_step_adapter_candidate_v2.py','OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json')]
(B/'SOURCE_DELTA_AND_BEFORE_USE_CONTRACT_111_V2.json').write_text(json.dumps(contract,indent=2),encoding='utf8')
(A/'reports/NOT_SELECTED_FULL_ORIENTATION_INPUT_SCALE_REASON_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),source_V1_not_used=True,reason=contract['selection'],no_saved_model_was_read=True,new_selected_source=str(B)),indent=2),encoding='utf8')
print(json.dumps(dict(prepared_source_only=True,path=str(B),adapter_SHA=hashlib.sha256(new.encode()).hexdigest())))
