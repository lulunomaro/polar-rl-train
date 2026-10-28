from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent;old=B/'mod4_fudan_contact_phase_reward_candidate_v1.py';source=old.read_text('utf8');s=source
changes=[("nominal_state=(theta[...,0]-theta[...,1]).square())","nominal_state=(theta[...,0]-theta[...,1]).square()+10*(L0[...,0]-L0[...,1]).square())"),
 ("base_height=torch.exp(-z/.25),base_height_enhance=torch.exp(-z/2.5)-1,","base_height=1.5*torch.exp(-z*1000),base_height_enhance=torch.exp(-z/.01)-1,"),
 ("lin_vel_z=m['world_vertical_velocity'].square()","lin_vel_z=m['body_vertical_velocity'].square()"),
 ("dof_vel=m['actuated_dq'].square().sum(-1)","dof_vel=m['actuated_leg_dq'].square().sum(-1)")]
for a,b in changes:assert s.count(a)==1;s=s.replace(a,b,1)
ast.parse(s);new=B/'mod4_fudan_contact_phase_reward_candidate_v2.py'
with new.open('x',encoding='utf8') as f:f.write(s)
with (B/'reports/SOURCE_FORMULA_REFINEMENT_BEFORE_FIRST_CPU_TEST_V2_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(original_candidate_SHA=hashlib.sha256(source.encode()).hexdigest(),selected_candidate_SHA=hashlib.sha256(s.encode()).hexdigest(),upstream_checked_changes=changes,original_v1_unexecuted_and_retained=True,no_model_SDK_GPU_or_network=True),f,indent=2)
print('v2 exact instantaneous formula corrections prepared; no model or GPU')
