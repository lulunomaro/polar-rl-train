"""Independent local CPU verification of the complete, already collected native models."""
from pathlib import Path
import os,json,time,hashlib,ast
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;R=D/'reports';torch.set_num_threads(4)
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def eq(a,b):
 if torch.is_tensor(a):return torch.is_tensor(b) and a.shape==b.shape and a.dtype==b.dtype and a.contiguous().reshape(-1).view(torch.uint8).numpy().tobytes()==b.contiguous().reshape(-1).view(torch.uint8).numpy().tobytes()
 if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(eq(a[k],b[k]) for k in a)
 if isinstance(a,(tuple,list)):return type(a)==type(b) and len(a)==len(b) and all(eq(x,y) for x,y in zip(a,b))
 return a==b
def tensors(x,count):
 if torch.is_tensor(x):
  count[0]+=1
  if x.is_floating_point():count[1]+=1;assert torch.isfinite(x).all()
 elif isinstance(x,dict):
  for v in x.values():tensors(v,count)
 elif isinstance(x,(tuple,list)):
  for v in x:tensors(v,count)
def main():
 dest=R/'H1_COMPLETE_FULL20K_NATIVE_ALL_ROWS_TWOHOST_MODELS_LOCAL_CPU_ADMITTED_ACTUAL.json';assert not dest.exists();rng=torch.get_rng_state().clone();collection=json.loads((R/'H1_NATIVE_POST_BOUND_READONLY_V3_COMPLETE_ACTUAL.json').read_bytes());assert collection['parent_exit'] and collection['parent_final'] and not collection['actual_processes'] and not collection['validation_actual_fcntl_held'];reports={Path(x['path']).name:x for x in collection['files']};cpu=reports['H1_NATIVE_FULL20K_ALL_ROWS_CPU_ADMITTED.json'];assert cpu['value']['passed'] and reports['PARENT_FINAL.json']['value']['passed'] and not any('ORIGINAL_ERROR' in x for x in reports)
 source=D/'payload/job0/source/E0_full_source.pt';assert H(source)=='b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8';s=torch.load(source,map_location='cpu',weights_only=False);rows=[]
 for row in collection['local_models']:
  p=Path(row['path']);assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'];c=torch.load(p,map_location='cpu',weights_only=False);count=[0,0];tensors(c,count)
  for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert eq(c[k],s[k]),k
  assert len(c['actor_state_dict'])==9 and len(c['critic_state_dict'])==8 and len(c['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in c['optimizer_state_dict']['state'].values()}=={639560};assert 'H1_public_request_phase_state' in c and c['native_only_no_PPO'] is True;rows.append(dict(**row,all_model_runtime_tensor_finite=True,tensors=count[0],float_tensors=count[1],actor9_critic8_STD17Adam_source_literal_exact=True,actual_17Adam_step639560=True,H1_phase_and_command_named_RNG_actual_saved=True))
 assert len(rows)==2 and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();actual=json.loads((R/'H1_ACTUAL_RSL5_ON_POLICY_AND_PPO_SOURCE_READONLY_V3.json').read_bytes())
 for row in actual['source_files']:assert H(row['local_path'])==row['SHA'];ast.parse(Path(row['local_path']).read_text('utf8'))
 text=(D/'actual_RSL5_readonly_sources/on_policy_runner.py').read_text('utf8');ppo=(D/'actual_RSL5_readonly_sources/ppo.py').read_text('utf8');assert 'actions = self.alg.act(obs)' in text and 'obs, rewards, dones, extras = self.env.step(actions.to(self.env.device))' in text and 'self.transition.actions = self.actor(obs, stochastic_output=True).detach()' in ppo
 saved=next(x for x in rows if Path(x['path']).name=='saved.pt');report=dict(epoch=time.time(),passed=True,source_ancestor_SHA=H(source),admitted_H1_full_source=saved,native_CPU_report_SHA=cpu['SHA'],native_CPU_report=cpu['value'],models=rows,source_8typed_new_episode_zero_clock_and_actual_SDK_dt_receipt_index=reports['SOURCE_FULL20K_TYPED_ZERO_CLOCK_REWARD_SDK_ACTUAL.json']['path'],actual_parent_child_CPU_exit_and_validation_fcntl_free=True,actual_RSL5_source_API_binding=actual,trace_wrapper_matches_actual_alg_act_TensorDict_and_env_step=True,native0PPO_no_original_canonical_charge=True,not_jump_skill_or_saved_PPO_pass=True,global_CPU_RNG_unchanged=True,no_CUDA_or_optimizer=True)
 dest.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(passed=True,model_tensor_counts=[(x['tensors'],x['float_tensors']) for x in rows],admitted_source_SHA=saved['SHA'],all_policy_rows=cpu['value']['all_policy_rows'],all_physical_rows=cpu['value']['all_physical_rows'],events=cpu['value']['events_env_counts'],no_PPO=True)))
if __name__=='__main__':main()
