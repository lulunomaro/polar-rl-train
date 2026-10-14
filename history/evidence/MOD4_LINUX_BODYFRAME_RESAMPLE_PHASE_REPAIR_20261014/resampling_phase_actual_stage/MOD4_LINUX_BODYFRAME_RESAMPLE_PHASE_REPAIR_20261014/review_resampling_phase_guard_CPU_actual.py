"""Reproduce the observed transient command with actual saved whole-state rows."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,sys,time,types
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
D=Path(__file__).resolve().parent;W=D.parent;S=W/'MOD4_LINUX_WAVE50_BODYFRAME_SECOND_PREPARE_20261014';R=D/'reports';P=D/'payload_v1'
sys.path.insert(0,str(S/'payload_v1'))
from birth_bodyframe_state_v1 import KEY,clone,mapped_command
from bodyframe_original_CPU_guard import tree_sha
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 out=R/'BODY_RESAMPLE_PHASE_OLD_REJECTION_NEW_DEFER_AND_STABLE_NEGATIVES_CPU_ACTUAL.json';assert not out.exists()
 positive=json.loads((S/'reports/SECOND_BODY_OWN_POSITIVE_SAVED_ACTUAL_1791990466943186800.json').read_bytes());row=positive['two_host_byteSHA_exact'][0];path=Path(row['local_path']);assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
 ck=torch.load(path,map_location='cpu',weights_only=False);state=clone(ck[KEY]);command=ck['E1_retained_flat_command_state']['BODY_command'];family=ck['E1_retained_flat_command_state']['family'];standing=(command==0).all(-1)
 ids=torch.nonzero(state['wave_mask']&(family==4)&~standing).flatten();assert len(ids)>1000
 old=load('old_guard_preserved',S/'payload_v1/birth_bodyframe_reset_adapter_v6.py');new=load('new_resample_phase_only',P/'birth_bodyframe_reset_adapter_v7_resample_phase.py')
 def adapter(module,resampling,reset=False):
  a=object.__new__(module.BirthAdapter);a.state=clone(state);a.env=types.SimpleNamespace(_e1_episode=state['bound_episode'].clone());a.reset_in_progress=reset
  a.term=types.SimpleNamespace(manual_evaluation_mode=False,_retention_resampling=resampling,vel_command_b=command.clone(),family=family.clone(),is_standing_env=standing.clone())
  return a
 rng=torch.get_rng_state().clone();before=tree_sha(ck);transient=adapter(old,True);transient.term.vel_command_b[ids,0]=0.;transient.term.vel_command_b[ids,2]=1.2
 old_rejected=False
 try:transient.apply_commands(ids)
 except AssertionError:old_rejected=True
 assert old_rejected,'The actual old adapter must reproduce the primary assertion on the transient original sample'
 deferred=adapter(new,True);deferred.term.vel_command_b.copy_(transient.term.vel_command_b);bits=deferred.term.vel_command_b.clone();deferred.apply_commands(ids);assert torch.equal(bits,deferred.term.vel_command_b)
 # Once the original retained sampler finishes, all final BODY mapping and limits stay the original ones.
 complete=adapter(new,False);world=command.clone();world[ids,0]*=state['BODY_coefficient'][ids];complete.term.vel_command_b.copy_(world);expected=mapped_command(world,family,standing,state,ids);complete.apply_commands(ids);assert torch.equal(expected,complete.term.vel_command_b)
 unchanged=~torch.isin(torch.arange(20000),ids);assert torch.equal(world[unchanged],complete.term.vel_command_b[unchanged])
 resetting=adapter(new,False,True);bits=resetting.term.vel_command_b.clone();resetting.apply_commands(ids);assert torch.equal(bits,resetting.term.vel_command_b)
 bad=[]
 for kind in ('speed','yaw','standing'):
  a=adapter(new,False);a.term.vel_command_b.copy_(world)
  if kind=='speed':a.term.vel_command_b[ids[0],0]=state['world_toward_sign'][ids[0]]*.31
  elif kind=='yaw':a.term.vel_command_b[ids[0],2]=1e-3
  else:a.term.is_standing_env[ids[0]]=True
  try:a.apply_commands(ids)
  except AssertionError:bad.append(kind)
  else:raise AssertionError('Stable invalid command was accepted: '+kind)
 assert tree_sha(ck)==before and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 s=(P/'birth_bodyframe_reset_adapter_v7_resample_phase.py').read_text(encoding='utf8');normalized=s.replace('if self.reset_in_progress or self.term._retention_resampling:\n            # The original sampler finishes its private transient command first.','if self.reset_in_progress:')
 assert ast.dump(ast.parse(normalized),include_attributes=False)==ast.dump(ast.parse((S/'payload_v1/birth_bodyframe_reset_adapter_v6.py').read_text(encoding='utf8')),include_attributes=False)
 value=dict(epoch=time.time(),passed=True,actual_saved_source=row,selected_real_saved_Wave_moving_rows=len(ids),old_adapter_transient_ASSERT_reproduced=True,new_adapter_defers_during_original_sampler_only=True,defer_command_and_state_bytes_unchanged=True,stable_original_mapping_exact=True,nonselected_other_families_unchanged=True,original_reset_guard_unchanged=True,stable_negative_speed_yaw_standing_rejected=bad,all_other_adapter_AST_exact=True,whole_source_and_CPU_RNG_unchanged=True,no_CUDA_SSH_PPO=True,new_GPU_native_and_complete_resampling_cycle_NOT_yet_verified=True)
 out.write_text(json.dumps(value,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),passed=True,real_saved_rows=len(ids),old_rejection_reproduced=True,stable_negatives=bad,new_GPU_pending=True)))
if __name__=='__main__':main()
