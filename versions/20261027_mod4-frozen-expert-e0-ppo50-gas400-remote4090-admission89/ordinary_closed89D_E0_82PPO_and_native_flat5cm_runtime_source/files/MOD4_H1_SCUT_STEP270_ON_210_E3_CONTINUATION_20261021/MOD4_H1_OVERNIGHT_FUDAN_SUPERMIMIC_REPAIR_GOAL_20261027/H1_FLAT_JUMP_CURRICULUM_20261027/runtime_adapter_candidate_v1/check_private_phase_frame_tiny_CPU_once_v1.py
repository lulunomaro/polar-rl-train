"""Tiny encoding/reset-boundary fixture, not an actual provider/learner run."""
from pathlib import Path
import ast,hashlib,json,os,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
import private_phase_frame_v1 as p
HERE=Path(__file__).resolve().parent
def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def reject(fn):
 try:fn()
 except AssertionError:return True
 raise AssertionError('invalid schema accepted')
def main():
 out=HERE/'PRIVATE_PHASE_FRAME_TINY_CPU_ACTUAL_V1.json';assert not out.exists()
 rng=torch.get_rng_state().clone();ids=torch.tensor([0,249,250,501],dtype=torch.long);age=torch.tensor([0,499,500,17],dtype=torch.long)
 ids_before=ids.clone();age_before=age.clone();f=p.encode(age,ids);d=p.decode(f)
 assert f.dtype==torch.long and d['valid_actual'].all()
 assert torch.equal(d['delay_ticks'],ids%250) and torch.equal(d['public_age'],age)
 assert torch.equal(d['phase_age'],age-ids%250)
 assert p.decode(f+1)['public_age'].tolist()==[1,500,501,18]
 assert p.horizon_valid(f,1,kind='policy').tolist()==[True,True,False,True]
 h=p.horizon_checks(f,32,kind='world');assert h['lookup_encoding_valid'].all() and h['same_private_delay'].all()
 assert h['within_episode'].tolist()==[True,False,False,True]
 assert h['next_public_age'].tolist()==[32,531,532,49]
 reset=p.decode(p.encode(torch.zeros_like(age),ids))
 assert reset['public_age'].tolist()==[0,0,0,0] and torch.equal(reset['delay_ticks'],ids%250)
 assert torch.equal(reset['phase_age'],-(ids%250))
 invalid=p.encode(torch.tensor([-1,501]),torch.tensor([1,2]));assert invalid.tolist()==[-1,-1] and not p.decode(invalid)['valid_actual'].any()
 assert p.encode(torch.tensor([0]),torch.tensor([-1])).item()==-1
 negatives=dict(float_frame=reject(lambda:p.decode(f.float())),float_age=reject(lambda:p.encode(age.float(),ids)),
  world33=reject(lambda:p.horizon_valid(f,33,kind='world')),policy11=reject(lambda:p.horizon_valid(f,11,kind='policy')),
  negative_horizon=reject(lambda:p.horizon_valid(f,-1,kind='policy')))
 assert torch.equal(ids,ids_before) and torch.equal(age,age_before) and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 src=HERE/'private_phase_frame_v1.py';ast.parse(src.read_bytes())
 with out.open('x',encoding='utf8') as stream:json.dump(dict(epoch=time.time(),passed=True,source=dict(path=str(src),bytes=src.stat().st_size,SHA=H(src)),
  encoding='f=(env_id%250)*1024+actual_public_age; dtype long',tick_s=.01,max_actual_public_age=500,world_lookahead_limit=32,policy_lookahead_limit=10,
  exact_roundtrip_delay_actual_age_and_signed_phase_age=True,reset_reuses_same_env_delay_and_age0=True,
  actual_episode_validity_separate_from_terminal_lookup_encoding=True,invalid_actual_ages_or_env_IDs_sentinel_minus1=True,
  negative_schema_rejections=negatives,original_inputs_and_RNG_unchanged=True,no_frame_or_age_public_mutation=True,
  no_PT_Actor_SDK_GPU_remote_learner_replay_or_ledger_access=True,actual_provider_and_bridge_integration_pending=True,
  original_source_preparation_error=dict(tool_call='apply_patch initial local source creation',error='A local path typo used a sibling continuation_20261027 instead of existing continuation_20261021/L; immediately relocated the same source bytes to the exact requested folder. No runtime or other files edited; no cleanup performed.'),
  Git_status='ordinary_supplement_pending_root'),stream,indent=2)
 print(json.dumps(dict(passed=True,source_SHA=H(src),report_SHA=H(out),actual_integration_pending=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (HERE/('PRIVATE_FRAME_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(traceback=traceback.format_exc()),indent=2),encoding='utf8');raise
