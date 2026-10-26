"""Original complete source restoration and explicit new deterministic H1 phase state."""
from pathlib import Path
import torch,json,time,hashlib
from chassis_pd_checkpoint import resume_chassis_pd_new_episode,install_chassis_pd_save_contract
from spring_pressure_checkpoint import exact
COMMAND_FIELDS=('is_standing_env','is_heading_env','is_pure_spin','is_moving_spin','is_transition_spin','world_direction','signed_yaw','phase_elapsed','vel_command_b')
def state(env):
 t=env.command_manager.get_term('twist');return dict(version=1,phase=env.h1_phase.state_dict(),external_command={k:getattr(t,k).clone() for k in COMMAND_FIELDS},private_command_mode_rng=t._mode_rng.get_state().clone())
def load(env,s):
 assert s['version']==1;env.h1_phase.load_state_dict(s['phase']);t=env.command_manager.get_term('twist')
 for k,v in s['external_command'].items():
  a=getattr(t,k);assert a.shape==v.shape and a.dtype==v.dtype;a.copy_(v.to(a.device))
 t._mode_rng.set_state(s['private_command_mode_rng'].cpu());env._h1_publish_external_request()
def resume_h1_new_episode(runner,env,path,log_dir):
 ck=torch.load(path,map_location='cpu',weights_only=False);has='H1_public_request_phase_state' in ck
 if has:load(env,ck['H1_public_request_phase_state'])
 current=state(env);tmp=Path(log_dir)/'H1_PHASE_ACTUAL_CUDA_STARTUP_ROUNDTRIP.pt';torch.save(current,tmp);load(env,torch.load(tmp,map_location='cpu',weights_only=False));assert exact(state(env),current)
 proof=resume_chassis_pd_new_episode(runner,env,path,log_dir);assert not env.h1_phase.age_control.any() and not env.h1_phase.attempt.any() and not env.h1_phase.public_request().any()
 row=dict(epoch=time.time(),source_SHA=hashlib.sha256(Path(path).read_bytes()).hexdigest(),complete_original_D0_D7_proof=proof,source_had_H1_phase=has,new_phase_group_explicit_no_new_rng=True,actual_CUDA_disk_roundtrip_exact=True,new_physical_episode_resets_external_schedule_and_reward_credits=True,phase_truth_not_actor_input=True,not_PhysX_exact_resume=True);Path(log_dir,'H1_PHASE_FULLSTATE_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(row,indent=2));return row
def install_h1_save_contract(runner,env):
 install_chassis_pd_save_contract(runner,env);original=runner.save
 def save(path,*a,**kw):
  original(path,*a,**kw);ck=torch.load(path,map_location='cpu',weights_only=False);ck['H1_public_request_phase_state']=state(env);torch.save(ck,path)
 runner.save=save
