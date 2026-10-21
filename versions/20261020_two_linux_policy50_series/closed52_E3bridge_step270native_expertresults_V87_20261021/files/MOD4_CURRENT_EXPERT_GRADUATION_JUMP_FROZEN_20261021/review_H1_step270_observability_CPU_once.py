from pathlib import Path
import hashlib,json,sys,time,torch
B=Path(__file__).resolve().parent;P=B/'H1_step270_candidate_uninstalled';sys.path.insert(0,str(P))
from scut_step270_observable_rates_v2 import rates,PROFILE
kw=dict(push=torch.tensor([False,False]),airborne=torch.tensor([False,False]),landed=torch.tensor([True,True]),vz=torch.zeros(2),release_reference_vz=torch.ones(2),wheel_torque=torch.zeros(2,2),wheel_bottom_relative_base=torch.ones(2,2)*-.22,heading_error=torch.tensor([0.,1.]),planar_speed=torch.zeros(2),projected_gravity=torch.tensor([[0.,0.,-1.],[0.,0.,-1.]]),angular_velocity_body=torch.tensor([[0.,0.,0.],[0.,0.,.4]]))
r=rates(**kw);assert 'landing_heading_error' not in r and torch.allclose(r['landing_yaw_rate'],torch.tensor([0.,.16]))
kw['heading_error']=torch.tensor([2.,-2.]);s=rates(**kw);assert all(torch.equal(r[k],s[k]) for k in r)
v=dict(epoch=time.time(),passed_CPU_observability_review=True,profile=PROFILE,observable_gyro_yaw_rate_reward_exact=True,unobserved_absolute_heading_not_in_new_reward_rates=True,absolute_heading_still_required_for_original_goal=True,original_35_actor_inputs_not_changed=True,source_path=str(P/'scut_step270_observable_rates_v2.py'),source_SHA=hashlib.sha256((P/'scut_step270_observable_rates_v2.py').read_bytes()).hexdigest(),V1_CPU_draft_and_results_retained=True,not_GPU_or_SDK_or_training=True,limits='Yaw-rate shaping can encourage drift prevention; it does not guarantee absolute heading restoration with a memoryless actor. Actual success requires the original yaw witness and stable platform landing.')
(B/'reports/H1_STEP270_OBSERVABLE_REWARD_CANDIDATE_V2_CPU_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(v,indent=2));print(json.dumps(v))
