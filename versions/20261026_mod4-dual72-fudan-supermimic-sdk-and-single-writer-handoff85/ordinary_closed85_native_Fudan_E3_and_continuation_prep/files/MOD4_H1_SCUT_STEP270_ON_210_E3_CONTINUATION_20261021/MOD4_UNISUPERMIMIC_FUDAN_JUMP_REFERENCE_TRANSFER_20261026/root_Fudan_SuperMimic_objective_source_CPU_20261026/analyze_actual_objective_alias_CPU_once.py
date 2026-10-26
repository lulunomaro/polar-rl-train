"""Source-only CPU counterexamples, no model weights, policy forward, or physics."""
from pathlib import Path
import ast, importlib.util, json, sys, time, traceback
import torch

HERE=Path(__file__).resolve().parent
T=HERE.parent.parent
N=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026'
S=N/'payloads/e2/source'
sys.path.insert(0,str(S))
from supermimic_vendor_v2.geometry import invariant_features, quat_to_mat
from supermimic_vendor_v2.networks import WorldModel
from supermimic_reference_adapter_v1 import read_json_reference, PartialReferenceImitationMdp

def main():
 out=HERE/'ACTUAL_SOURCE_TASK_DISTANCE_ALIAS_AND_HEIGHT_GRADIENT_CPU.json'
 assert not out.exists()
 source=(S/'h1_supermimic_bridge_v1.py').read_text('utf8')
 parsed=ast.parse(source)
 base_class=next(x for x in parsed.body if isinstance(x,ast.ClassDef) and x.name=='H1GoalMdp')
 scope={'torch':torch}
 scope['invariant_features']=invariant_features
 exec(compile(ast.Module(body=[base_class],type_ignores=[]),str(S/'h1_supermimic_bridge_v1.py'),'exec'),scope)
 ref=read_json_reference(N/'payloads/e2/reference/H1_PARTIAL_JUMP_NATIVE_REFERENCE_PACKED73_PHASE_V3.json')
 ref=ref.for_offline_joint_order(ref.joint_names)
 provider=ref.torch_provider('cpu',offline_cpu_only=True)
 nominal=float(ref.metadata['partial_phase_contract']['own_task_nominal_chassis_height_m'])
 base=scope['H1GoalMdp'](provider.states[0,13:43],nominal)
 mdp=PartialReferenceImitationMdp(base,provider)
 context=torch.zeros(1,49)
 action=torch.zeros(1,6)
 previous=torch.zeros(1,6)
 records=[]
 for frame in (95,120,140,160):
  f=torch.tensor([frame],dtype=torch.int32)
  raw=provider.raw_reference_at_frames(f)
  pair=[]
  for x in (.10,.40):
   pos=torch.tensor([[x,0.,nominal]],requires_grad=True)
   state=(pos,quat_to_mat(raw[:,3:7]),torch.zeros(1,3),torch.zeros(1,3),raw[:,13:43],raw[:,43:73])
   terms=mdp.objective_terms(state,f,action,previous)
   dz=float(torch.autograd.grad(terms['total'].sum(),pos,retain_graph=True)[0][0,2])
   pair.append(dict(x=x,z=nominal,reward=float(terms['total']),d_reward_d_z=dz,
                    ascent=float(terms['demo_height_vz_active']),support=float(terms['own_task_support_region_weight']),
                    own_landing_height_cost=float(terms['own_task_landing_height_cost']),
                    obs=mdp.obs(state,previous,context,f).detach(),
                    wm_input=WorldModel.inputs(None,state,action,mdp.normalize_context(context)).detach(),
                    critic_input=mdp.critic_features(state,f,mdp.normalize_context(context)).detach()))
  checks={k:torch.equal(pair[0][k],pair[1][k]) for k in ('obs','wm_input','critic_input')}
  assert all(checks.values())
  for v in pair:
   for k in checks:v.pop(k)
  records.append(dict(frame=frame,identical_inputs=checks,goal_same_because_same_frame=True,cases=pair))
 late=next(x for x in records if x['frame']==160)
 assert late['cases'][0]['d_reward_d_z']==0 and late['cases'][1]['d_reward_d_z']>0
 baseline=(torch.tensor([[0.,0.,nominal]]),torch.eye(3)[None],torch.zeros(1,3),torch.zeros(1,3),provider.states[0:1,13:43],torch.zeros(1,30))
 upright_softdone=float(base.soft_termination(baseline,torch.tensor([0])))
 result=dict(status='SOURCE_COUNTEREXAMPLES_REPRODUCED_NOT_UNIQUE_RUNTIME_CAUSE',epoch=time.time(),
   scope='actual installed source, existing small reference, synthetic CPU states only; no actor/model checkpoint/physics/GPU/remote reads',
   reference_SHA_from_existing_producer='0b9d642f3530ad55bd353c19918a0778378746ecc250e1f22c10c58b8c095c94',
   bridge_SHA_from_existing_producer='e01ff501d198f927cb634ccb381f1e0e71ecdb54214029aa04a0ac2a4275ed8c',
   cases=records,
   proved=['same state except world X yields identical current actor observation, WM input and critic features while reward changes',
           'at frame160 (after ascent mask), before step edge the own landing height term has exactly zero vertical reward derivative in this fixture',
           'after step edge this same vertical displacement has a positive reward derivative'],
   limitations=['same instantaneous observation can still differ in real observation histories/contact; no claim every real trajectory is indistinguishable',
                'invariant WM can model some flat terrain motion; this counterexample exposes omitted fixed step position, not a general claim translation invariance is wrong',
                'zero late pre-edge vertical derivative does not prove all jump gradients zero: earlier ascent/leg/orientation/critic terms remain',
                'dynamic feasibility of 90-percent-attenuated limb excursion was not proved by original static IK; no new physical rollout performed',
                'not proof these omissions uniquely caused all zero events; actual phase occupancy/gradient alignment require separate evidence'],
   nominal_upright_softdone=upright_softdone,
   nominal_constant_state_16step_survival=(1-upright_softdone)**16,
   no_runtime_edits=True,no_training_started=True)
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':
 try:main()
 except BaseException:
  (HERE/('ORIGINAL_CPU_READER_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps({'error':traceback.format_exc(),'no_model_or_runtime_changes':True},indent=2),'utf8')
  raise
