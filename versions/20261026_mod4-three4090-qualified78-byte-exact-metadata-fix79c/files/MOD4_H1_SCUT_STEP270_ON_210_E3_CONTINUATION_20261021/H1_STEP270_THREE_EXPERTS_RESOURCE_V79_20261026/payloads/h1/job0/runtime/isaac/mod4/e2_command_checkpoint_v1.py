"""Original D0-D7 restore plus explicit new E2 command state; no fake E1 terrain."""
from pathlib import Path
import hashlib,json,time,os,torch
from chassis_pd_checkpoint import resume_chassis_pd_new_episode,install_chassis_pd_save_contract
from spring_pressure_checkpoint import exact
FIELDS=('is_standing_env','is_heading_env','is_pure_spin','is_moving_spin','is_transition_spin','world_direction','signed_yaw','phase_elapsed','vel_command_b')
def current(term):
 return dict(version=1,kind=os.environ['OWN_E2_H1_KIND'],moving_yaw_cap=4.,tensors={k:getattr(term,k).clone() for k in FIELDS},private_mode_rng=term._mode_rng.get_state().clone())
def load(term,state):
 assert state['version']==1 and state['kind']==os.environ['OWN_E2_H1_KIND'] and state['moving_yaw_cap']==4.
 for k in FIELDS:
  a=getattr(term,k);b=state['tensors'][k];assert a.shape==b.shape and a.dtype==b.dtype;a.copy_(b.to(a.device))
 term._mode_rng.set_state(state['private_mode_rng'].cpu());assert exact(current(term),{**state,'tensors':{k:v.to(term.device) for k,v in state['tensors'].items()},'private_mode_rng':state['private_mode_rng']})
def resume_e2_new_episode(runner,env,path,log_dir):
 ck=torch.load(path,map_location='cpu',weights_only=False);term=env.command_manager.get_term('twist');has='E2_moving4_command_state' in ck
 if has:load(term,ck['E2_moving4_command_state'])
 before=current(term);tmp=Path(log_dir)/'E2_COMMAND_ACTUAL_CUDA_STARTUP_ROUNDTRIP.pt';torch.save(before,tmp);load(term,torch.load(tmp,map_location='cpu',weights_only=False));assert exact(current(term),before)
 proof=resume_chassis_pd_new_episode(runner,env,path,log_dir)
 row=dict(epoch=time.time(),source_SHA=hashlib.sha256(Path(path).read_bytes()).hexdigest(),original_D0_D7_full_source_restore=proof,source_has_E2_command_state=has,new_command_group_explicit_not_old_E0_private_stream_claim=True,command_CUDA_disk_roundtrip_exact=True,source_model_critic_STD_optimizer_retained=True,new_physical_episode_not_PhysX_exactresume=True,moving_yaw_cap=4.)
 Path(log_dir,'E2_COMMAND_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(row,indent=2));return row
def install_e2_save_contract(runner,env):
 install_chassis_pd_save_contract(runner,env);original=runner.save
 def save(path,*a,**kw):
  original(path,*a,**kw);v=torch.load(path,map_location='cpu',weights_only=False);v['E2_moving4_command_state']=current(env.command_manager.get_term('twist'));torch.save(v,path)
 runner.save=save
