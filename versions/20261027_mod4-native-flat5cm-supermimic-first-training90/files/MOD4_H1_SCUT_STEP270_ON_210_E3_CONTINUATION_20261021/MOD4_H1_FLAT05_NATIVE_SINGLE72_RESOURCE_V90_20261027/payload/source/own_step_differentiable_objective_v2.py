"""SELECTED bounded-positive task head; V1 cost/FK retained as source evidence.

With original survival weighting, negative penalties could reward early death.
Use a single positive monotone rational transform of task-dominant Huber cost,
not an exponential product or free bonuses for easy orientation/joint terms.
"""
from own_step_differentiable_objective_v1 import OwnStepDifferentiableMdp
from own_step_differentiable_geometry_v1 import require
class OwnStepDifferentiableMdpV2(OwnStepDifferentiableMdp):
 def to(self,device):return OwnStepDifferentiableMdpV2(self.provider.to(device),self.wheel_geometry.to(device),self.leg_encoder_joint_names)
 def objective_terms(self,state,frames,action,previous_action):
  r=super().objective_terms(state,frames,action,previous_action)
  # Original action-rate coefficient is retained in cost units near the goal:
  # .06/(1+(.01/.06)*action_cost) ≈ .06-.01*action_cost.
  cost=r['geometry_task_loss']+r['action_rate_cost']/6.
  require((cost>=0).all(),'task/action cost must be nonnegative')
  score=(1+cost).reciprocal()
  r.update(unbounded_V1_diagnostic_score=r['task_score_surrogate'],combined_nonnegative_cost=cost,task_score_surrogate=score,total=.06*score)
  return r
 def contract_manifest(self):
  r=super().contract_manifest();r.update(schema='mod4.native88.own_wheel_step_objective.source_candidate.v2',
   selected_candidate=True,aggregation='reward=.06/(1+weighted_task_Huber_cost+.05*style_deficit+action_rate_cost/6)',
   reward='identical task-dominant bounded own-wheel head for actual and imagined state',
   position_and_velocity_errors='own-wheel normalized Huber; original masked tracking is only bounded style deficit',
   reward_range='0<reward<=.06 for finite evaluated cost; removes negative-future-return avoidance incentive',
   derivative='rational polynomial decay; direction/finite differences demonstrated on the declared newR2 and counterfactuals, not a WM-dynamics proof',
   V1_unbounded_negative_return_rejected=True,actual_training_or_skill_gain=False)
  return r

def build_own_step_mdp(contract_document,geometry_document,reference_document,actual_joint_names,actual_encoder_joint_names,*,device='cpu',order_scope='actual_SDK_readback'):
 """Explicit constructor for root entry; caller owns real SDK/source readback."""
 from own_step_differentiable_geometry_v1 import OwnStepWheelGeometry
 from converted_MOD4_jump_mdp_v4 import ConvertedMOD4Reference
 provider=ConvertedMOD4Reference(reference_document,device).bind_named_order(actual_joint_names,scope=order_scope)
 geometry=OwnStepWheelGeometry(contract_document,geometry_document,actual_joint_names)
 return OwnStepDifferentiableMdpV2(provider,geometry,actual_encoder_joint_names)
