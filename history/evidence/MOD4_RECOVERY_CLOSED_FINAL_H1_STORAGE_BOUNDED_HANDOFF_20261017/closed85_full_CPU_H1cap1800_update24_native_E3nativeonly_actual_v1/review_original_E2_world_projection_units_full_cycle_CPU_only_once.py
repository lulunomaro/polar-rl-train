"""Original pinned body-command math on an ideal full cycle; no counterfactual robot rollout."""
from pathlib import Path
import os,sys,time,json,hashlib,importlib.util
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch,math
B=Path(__file__).resolve().parent;R=B/'reports';K=B.parent/'MOD4_V8_FINALS_E2_FROZEN_REGRESSION_RECOVERY_ONLY_HANDOFF_20261017'
def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();p=K/'payload/e2/job0/runtime/isaac/mod4/spin_translation_math.py';sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha=='69575be60f63bc944d4c7edd0b37279a68a47c40d68e629f75d5a69b6fe967c6'
 sp=importlib.util.spec_from_file_location('pinned_original_projection_math_CPU',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);n=16384;phase=torch.arange(n,dtype=torch.float64)*(2*math.pi/n);rows=[]
 for sign in (1,-1):
  for direction in (0.,math.pi/2,math.pi,3*math.pi/2):
   heading=.321+sign*phase;vx,vy=m.body_command(.5,direction,heading,body_speed_limit=1.5);wx=vx*torch.cos(heading)-vy*torch.sin(heading);wy=vx*torch.sin(heading)+vy*torch.cos(heading);along=wx*math.cos(direction)+wy*math.sin(direction);cross=-wx*math.sin(direction)+wy*math.cos(direction)
   assert abs(float(along.mean())-.5)<1e-12 and abs(float(cross.mean()))<1e-12 and float(vy.abs().max())==0 and float(vx.abs().max())<=1
   wrong_vx=.5*torch.cos(heading-direction);wrong=(wrong_vx*torch.cos(heading-direction)).mean();assert abs(float(wrong)-.25)<1e-12
   rows.append(dict(signed_yaw_rad_s=sign*4,world_direction_rad=direction,ideal_full_cycle_world_along_m_s=float(along.mean()),ideal_full_cycle_world_cross_m_s=float(cross.mean()),command_peak_body_speed=float(vx.abs().max()),wrong_single_V_cos_would_yield_point25=float(wrong),not_real_robot_or_actual_reward_effective_config=True))
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 report=dict(epoch=time.time(),passed_pinned_original_command_units_full_cycle_CPU=True,source=dict(path=str(p),bytes=p.stat().st_size,SHA=sha),eight_original_signed4_direction_cases=rows,original_twoVcos_reference_not_changed=True,reference_bodyvy0_requires_twoV_to_ideal_average_V=True,no_claim_actual_robot_follows_ideal_or_unique_regression_cause=True,actual112_positive_along_point59175_overspeed_original_false_preserved=True,actual_effective_live_reward_config_still_requires_separate_evidence=True,E2_paid_learning_hold_unchanged=True,CPU_RNG_unchanged0CUDA0optimizer=True,no_remote_or_GPU_or_reward_command_threshold_change=True)
 with (R/'E2_ORIGINAL_WORLD_PROJECTION_UNITS_IDEAL_FULL_CYCLE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
 print(json.dumps(dict(original_projection_eight_cases_CPU_passed=True,ideal_worldVpoint5=True,do_not_blindly_halve_projection_factor=True,no_robot_or_causal_qualification_claim=True)),flush=True)
if __name__=='__main__':main()
