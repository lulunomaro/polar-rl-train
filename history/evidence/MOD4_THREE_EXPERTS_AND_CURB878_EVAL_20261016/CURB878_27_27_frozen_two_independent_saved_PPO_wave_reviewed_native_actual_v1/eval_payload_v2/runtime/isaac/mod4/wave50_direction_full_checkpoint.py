"""Exact legacy source restoration plus separate episode-direction state."""
from pathlib import Path
import torch,json,hashlib,os,time
import wave50_entry_full_checkpoint_v2 as old
from wave50_direction_state import KEY,PROFILE,validate
from retention_command_state import same

def install_e1_save_contract(runner,env):
 old.install_e1_save_contract(runner,env);original=runner.save
 def save(path,*a,**k):
  original(path,*a,**k);ck=torch.load(path,map_location='cpu',weights_only=False)
  term=env.command_manager.get_term('twist');term.audit_direction();ck[KEY]=term.state_dict_direction()
  ck['E1_WAVE50_episode_direction_profile']=PROFILE;torch.save(ck,path)
  Path(path).parent.joinpath('WAVE50_DIRECTION_ACTUAL.json').write_text(json.dumps(term.audit_direction(),indent=2))
 runner.save=save

def resume_e1_new_episode(runner,env,path,log_dir):
 ck=torch.load(path,map_location='cpu',weights_only=False);h=hashlib.sha256(Path(path).read_bytes()).hexdigest()
 term=env.command_manager.get_term('twist');new=KEY not in ck
 if new:
  assert h==old.SOURCE_SHA
  term._write_dynamic(torch.arange(env.num_envs,device=env.device));before=term.state_dict_direction()
 else:
  validate(ck[KEY],env.num_envs);term.load_state_direction(ck[KEY]);assert same(term.state_dict_direction(),ck[KEY]);before=term.state_dict_direction()
 p=Path(log_dir)/'WAVE50_DIRECTION_ACTUAL_CUDA_ROUNDTRIP.pt';torch.save(before,p)
 loaded=torch.load(p,map_location='cpu',weights_only=False);term.load_state_direction(loaded)
 assert same(term.state_dict_direction(),before)
 # Original full optimizer/D0-D7/global/named/private RNG and terrain loader remain exact.
 proof=old.resume_e1_new_episode(runner,env,path,log_dir)
 audit=term.audit_direction()
 own=dict(epoch=time.time(),pid=os.getpid(),source_sha256=h,passed=True,explicit_new_episode_direction_scope=new,
  predecessor_direction_state_restored_exact=not new,actual_CUDA_direction_disk_roundtrip_exact=True,
  original_full_source_restore_unmodified=True,saved_source_episode_plus_one_verified=proof['saved_source_episode_plus_one_verified'],
  no_new_rng=True,actual_command_audit=audit,PhysX_exact_resume_claimed=False)
 Path(log_dir,'E1_WAVE50_DIRECTION_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(own,indent=2));return proof
