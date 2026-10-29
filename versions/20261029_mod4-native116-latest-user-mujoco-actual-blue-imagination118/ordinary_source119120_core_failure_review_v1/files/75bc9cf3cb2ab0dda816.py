"""Candidate120: add the original2mm/grace closure boundary to analytic planning.
Built from116, WITHOUT secondary119 goal change. No runtime/model/physics action.
"""
from pathlib import Path
import ast,hashlib,json,time
T=Path(__file__).resolve().parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';D=L/'native120_original_closure_vs_imagined_stop_CPU_review_v1';B=T/'MOD4_H1_FUDAN270_DIRECT_COMMAND_RESOURCE_V116_20261029/payloads/seed27/source'
source=B/'native_fudan_step_adapter_candidate_v2.py';raw=source.read_bytes();s=raw.decode('utf8')
a="        self.reward_parameters=provider.parameters;p=provider.parameters"
cache="""        closure_rows=list(contract['closures'].items())
        self._closure_names=tuple(name for name,_ in closure_rows)
        self._closure_i0=torch.tensor([self.wheel_geometry.body_names.index(c['body0']) for _,c in closure_rows],dtype=torch.long,device=provider.device)
        self._closure_i1=torch.tensor([self.wheel_geometry.body_names.index(c['body1']) for _,c in closure_rows],dtype=torch.long,device=provider.device)
        self._closure_a0=torch.tensor([c['anchor0_m'] for _,c in closure_rows],dtype=torch.float32,device=provider.device)
        self._closure_a1=torch.tensor([c['anchor1_m'] for _,c in closure_rows],dtype=torch.float32,device=provider.device)
        self._planning_closure_threshold_m=.002
        self._planning_original_spawn_grace_controls=10
"""
assert s.count(a)==1;s=s.replace(a,cache+a)
a='    def soft_termination(self,state,frames):'
helper="""    def closure_surrogate_error_m(self,state):
        # Own q-tree FK, NOT a substitute for original PhysX body-anchor truth.
        # Candidate use requires actual-action WM error/false-stop calibration.
        g=self.wheel_geometry(state);p=g['body_position'];R=g['body_rotation']
        p0=p.index_select(-2,self._closure_i0)+(R.index_select(-3,self._closure_i0)@self._closure_a0.unsqueeze(-1)).squeeze(-1)
        p1=p.index_select(-2,self._closure_i1)+(R.index_select(-3,self._closure_i1)@self._closure_a1.unsqueeze(-1)).squeeze(-1)
        return (p0-p1).norm(dim=-1).amax(-1)
"""
assert s.count(a)==1;s=s.replace(a,helper+a)
a="        return torch.where(certain,torch.ones_like(soft),soft)"
b="""        age=decode_private_frame(frames)['public_age']
        past_original_grace=(age>=self._planning_original_spawn_grace_controls)
        closure_stop=(self.closure_surrogate_error_m(state)>self._planning_closure_threshold_m)&past_original_grace
        certain=certain|closure_stop
        return torch.where(certain,torch.ones_like(soft),soft)"""
assert s.count(a)==1;s=s.replace(a,b)
a='physical_low_base_disabled_minus1=True,quiet_includes_world_vertical_velocity_heading_and_tilt=True,'
b=a+"\n            imagined_closure_surrogate_threshold_m=.002,imagined_original_spawn_grace_controls=10,\n            closure_from_own_q_FK_not_full_PhysX_body_compliance=True,actual_action_WM_false_stop_calibration_required=True,"
assert s.count(a)==1;s=s.replace(a,b)
ast.parse(s);target=D/'native120_imagined_original_closure_stop_SOURCE_ONLY.py';assert not target.exists();target.write_text(s,encoding='utf8',newline='\n')
(D/'ORIGINAL116_ADAPTER_EXACT_BYTES.txt').write_bytes(raw)
report=dict(epoch=time.time(),source_only=True,not_installed_or_runtime_admitted=True,original_source=str(source),original_SHA=hashlib.sha256(raw).hexdigest(),candidate_SHA=hashlib.sha256(target.read_bytes()).hexdigest(),original_physical_threshold_and_grace_retained=dict(m=.002,controls=10),
    source119_neutral_X_change_NOT_bundled=True,no_reward_goal_actor_WM_architecture_norm_opt_or_real_physics_guard_change=True,
    new_source_only_closure_boundary_is_planning_surrogate=True,requires_actual_action_WM_closure_false_stop_calibration_before_use=True,
    no_checkpoint_raw_NPZ_SDK_GPU_SSH_or_account_action=True)
(D/'reports/SOURCE120_CLOSURE_STOP_CANDIDATE_DERIVATION_NOT_RUNTIME.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(dict(source_only=True,candidate=str(target),candidate_SHA=report['candidate_SHA'])))
