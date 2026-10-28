from pathlib import Path
import ast,hashlib,json,sys,time,traceback,types
N=Path(__file__).resolve().parent;R=N/'reports';B=N/'payloads/seed27'
sys.path[:0]=[str(B/'source'),str(B/'source/sm_deps')]
def main():
 import torch
 torch.set_num_threads(2)
 from private_phase_frame_v1 import encode,decode,horizon_checks,STRIDE,PUBLIC_EPISODE_MAX_TICKS
 from native_fudan_step_adapter_candidate_v2 import OwnFudanStepReference,OwnFudanStepMdp
 from supermimic_wheel_leg_v3.geometry import unflatten_state
 from static_dynamic_delay_contract_v1 import task_relative_observation
 from flat95_task_focused_starts_v1 import focused_mask,CONTRACT
 doc=json.loads((B/'source/OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json').read_bytes());provider=OwnFudanStepReference(doc)
 mdp=object.__new__(OwnFudanStepMdp);mdp.provider=provider;mdp.step_edge_x_m=.35;mdp.platform_top_z_m=.27
 ages=torch.arange(2001,dtype=torch.long);ids=torch.arange(250,dtype=torch.long);f=encode(ages[None,:],ids[:,None]);d=decode(f)
 assert STRIDE==4096 and PUBLIC_EPISODE_MAX_TICKS==2000
 assert torch.equal(d['public_age'],ages[None,:].expand(250,-1)) and torch.equal(d['delay_ticks'],ids[:,None].expand(-1,2001))
 target,_=provider.query(f);state=unflatten_state(torch.cat((target,torch.zeros(250,2001,54)),-1));features=mdp.relative_features(state,f)
 reference=task_relative_observation(state[0].reshape(-1,3),target[...,:3].reshape(-1,3),torch.full((f.numel(),),.35),torch.full((f.numel(),),.27),d['public_age'].reshape(-1)).reshape(250,2001,7)
 expected=((d['public_age']>=200)&(d['public_age']<2000)).float()
 assert torch.equal(features[...,5],expected) and torch.equal(features[...,:5],reference[...,:5]) and torch.equal(features[...,6:],reference[...,6:])
 assert mdp.valid_imagination_start(f[:,:2000],32).all() and not mdp.valid_imagination_start(f[:,2000:],32).any()
 assert focused_mask(f[:,180:2000]).all() and not focused_mask(f[:,:180]).any()
 for offset,kind in [(10,'policy'),(32,'world')]:
  q=horizon_checks(encode(torch.tensor([1999,2000]),torch.tensor([249,249])),offset,kind=kind)
  assert q['lookup_encoding_valid'].all() and q['same_private_delay'].all() and not q['within_episode'].any()
 # Exercise the exact real request body from the installed-source bridge AST.
 tree=ast.parse((B/'source/native_fudan_step_bridge_v1.py').read_bytes());func=next(x for x in ast.walk(tree) if isinstance(x,ast.FunctionDef) and x.name=='request');ns={};exec(compile(ast.fix_missing_locations(ast.Module(body=[func],type_ignores=[])),'actual_request_predicate','exec'),ns)
 assert torch.equal(ns['request'](types.SimpleNamespace(age_control=d['public_age'])),expected.bool())
 # Inverse single-literal deltas prove that architecture, clip, optimizers and
 # simulation configuration did not get altered by a broad replacement.
 A=N.parent/'MOD4_H1_FUDAN270_NATIVE_RESOURCE_V103_20261028/payloads_v4/seed27'
 worker=(B/'h1_native_flat90_worker_v1.py').read_text('utf8');assert worker.replace('c.episode_length_s=20.','c.episode_length_s=5.')==(A/'h1_native_flat90_worker_v1.py').read_text('utf8')
 for rel in ['source/supermimic_wheel_leg_v3/learner.py','source/supermimic_wheel_leg_v3/networks.py','source/mod4_fudan_contact_phase_reward_candidate_v2.py','source/static_dynamic_delay_contract_v1.py','job0/runtime/isaac/mod4/h1_public_request_phase_v1.py']:
  assert (B/rel).read_bytes()==(A/rel).read_bytes(),rel
 assert not torch.cuda.is_initialized()
 value=dict(passed=True,epoch=time.time(),grid_delays=250,actual_ages=2001,private_stride=4096,terminal_lookup_max_age=2032,request_interval_ticks=[200,2000],feature_other6_literal_unchanged=True,real_request_matches_observation_every_grid_row=True,negative_legacy100_180_request_rejected=True,world_policy_future_no_alias=True,original_networks_learner_reward_physics_success_bytes_retained=True,no_model_load_forward_SDK_GPU_SSH_or_account_action=True)
 with (R/'SOURCE106_COHERENT20S_CLOCK_AND_INVERSE_DELTAS_CPU_ACTUAL.json').open('x',encoding='utf8') as fp:json.dump(value,fp,indent=2)
 print(json.dumps(value))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('SOURCE106_CLOCK_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_model_or_GPU=True),f,indent=2)
  raise
