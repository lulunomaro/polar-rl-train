from pathlib import Path
import torch,json,hashlib,os,time
import wave50_direction_full_checkpoint as old
from wave50_route_state import KEY,PROFILE,validate
from wave50_route_runtime import bind,state_dict,load_state,audit
from retention_command_state import same
def install_e1_save_contract(runner,env):
 old.install_e1_save_contract(runner,env);original=runner.save
 def save(path,*a,**k):
  original(path,*a,**k);ck=torch.load(path,map_location='cpu',weights_only=False);ck[KEY]=state_dict(env,refresh=True);ck['E1_WAVE50_route_lifecycle_profile']=PROFILE;torch.save(ck,path)
  Path(path).parent.joinpath('WAVE50_ROUTE_ACTUAL.json').write_text(json.dumps(audit(env),indent=2))
 runner.save=save
def resume_e1_new_episode(runner,env,path,log_dir):
 ck=torch.load(path,map_location='cpu',weights_only=False);h=hashlib.sha256(Path(path).read_bytes()).hexdigest();new=KEY not in ck
 if new:assert h==old.old.SOURCE_SHA;before=state_dict(env,refresh=True)
 else:validate(ck[KEY],env.num_envs);load_state(env,ck[KEY]);before=state_dict(env);assert same(before,ck[KEY])
 p=Path(log_dir)/'WAVE50_ROUTE_ACTUAL_CUDA_ROUNDTRIP.pt';torch.save(before,p);loaded=torch.load(p,map_location='cpu',weights_only=False);load_state(env,loaded);assert same(state_dict(env),before)
 proof=old.resume_e1_new_episode(runner,env,path,log_dir);bind(env);report=audit(env)
 source_episode=ck['E1_terrain_state']['episode'].to(env.device);assert torch.equal(env._wave50_route_state['bound_episode'],source_episode+1)
 own=dict(epoch=time.time(),pid=os.getpid(),source_sha256=h,passed=True,explicit_new_route_lifecycle_scope=new,predecessor_route_state_restored_exact=not new,actual_CUDA_route_disk_roundtrip_exact=True,saved_source_episode_plus_one_verified=True,old_full_actor_critic_optimizer_D0D7_global_named_private_restore_unmodified=True,route_audit=report,no_new_rng=True,PhysX_exact_resume_claimed=False)
 Path(log_dir,'E1_WAVE50_ROUTE_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(own,indent=2));return proof
