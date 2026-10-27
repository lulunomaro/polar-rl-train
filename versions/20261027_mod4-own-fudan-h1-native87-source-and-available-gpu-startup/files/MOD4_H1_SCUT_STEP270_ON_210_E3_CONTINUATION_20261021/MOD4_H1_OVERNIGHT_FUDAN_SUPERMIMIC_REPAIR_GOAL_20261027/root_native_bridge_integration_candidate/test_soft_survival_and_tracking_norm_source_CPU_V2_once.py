from pathlib import Path
import sys,json,traceback
D=Path(__file__).resolve().parent;L=D.parent;R=L/'reports/SOFT_SURVIVAL_AND_TRACKING_NORM_SOURCE_CPU_V2_ACTUAL.json'
assert not R.exists()
for p in [D,L/'root_augmented_world_model_candidate/v5',L/'agent_static_dynamic_delay_contract_candidate',L/'root_compact_static_context_candidate']:sys.path.insert(0,str(p))
try:
 import torch
 from converted_MOD4_jump_mdp_v4 import ConvertedMOD4Reference,ConvertedMOD4JumpMdp
 from supermimic_wheel_leg_v3.geometry import unflatten_state
 doc=json.loads((D/'MOD4_OWN_CONVERTED_FUDAN_JUMP_REFERENCE_V1_NOT_ADMITTED.json').read_bytes())
 p=ConvertedMOD4Reference(doc).bind_named_order(doc['joint_names'],scope='source_CPU_fixture')
 m=ConvertedMOD4JumpMdp(p)
 f=torch.tensor([0,0,0]);v,_=p.query(f);v[:,2]=torch.tensor([.2341,.3377423,.5]);s=unflatten_state(torch.cat((v,torch.zeros(3,54)),-1))
 old=(torch.sigmoid((.12-s[0][:,2])*20)+torch.sigmoid((.3-s[1][:,2,2])*10)).clamp(0,1)
 new=m.soft_termination(s,f)
 assert (new<old).all() and new[1]<.0001
 survival_old=(1-old).pow(32);survival_new=(1-new).pow(32)
 # Exact root-position squared norm, as used by the source formulation.
 target,_=p.query(torch.tensor([130]));v=target.clone();v[:,0]+=.1;v[:,1]+=.2;v[:,2]+=.3
 s=unflatten_state(torch.cat((v,torch.zeros(1,54)),-1))
 terms=m.objective_terms(s,torch.tensor([130]),torch.zeros(1,6),torch.zeros(1,6))
 expected=torch.exp(torch.tensor(-(.1**2+.2**2+.3**2)/.3**2))
 assert torch.allclose(terms['position'],expected,atol=1e-6)
 result={'passed':True,'source_only':True,'poses_rootZ':[.2341,.3377423,.5],
  'old_soft_failure':old.tolist(),'new_soft_failure':new.tolist(),
  'old32step_survival':survival_old.tolist(),'new32step_survival':survival_new.tolist(),
  'fixed_source_math':'Original derivative has fake nominal per-step death cost. New .02/.04 sigmoid temperatures match pinned source style; thresholds/hard physical callback truth unchanged.',
  'does_not_prove_physical_failure_cause':True,'root_tracking_masked_squared_sum_verified':True,
  'old_source_preserved':True,'no_PT_actor_WM_GPU_SDK_physics_GO':True}
except BaseException:
 result={'passed':False,'error':traceback.format_exc(),'partials_retained':True};R.write_text(json.dumps(result,indent=2),'utf8');raise
R.write_text(json.dumps(result,indent=2),'utf8');print(json.dumps(result))


