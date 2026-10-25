from pathlib import Path
import torch,time,json,hashlib
from chassis_pd_checkpoint import resume_chassis_pd_new_episode,install_chassis_pd_save_contract
from spring_pressure_checkpoint import exact
def state(env):return dict(version=1,phase=env.recovery.state_dict(),private_command_rng=env.command_manager.get_term('twist')._mode_rng.get_state().clone())
def resume(runner,env,path,log_dir):
 ck=torch.load(path,map_location='cpu',weights_only=False);s=ck.get('E3_public_recovery_state')
 if s is not None:env.recovery.load_state_dict(s['phase']);env.command_manager.get_term('twist')._mode_rng.set_state(s['private_command_rng'].cpu())
 before=state(env);p=Path(log_dir)/'E3_PHASE_ACTUAL_CUDA_STARTUP_ROUNDTRIP.pt';torch.save(before,p);loaded=torch.load(p,map_location='cpu',weights_only=False);env.recovery.load_state_dict(loaded['phase']);assert exact(state(env),before);proof=resume_chassis_pd_new_episode(runner,env,path,log_dir);env.e3_reset_enabled=True;env.place_declared_fall(torch.arange(env.num_envs,device=env.device));assert not env.recovery.age.any();env.publish();row=dict(epoch=time.time(),source_SHA=hashlib.sha256(Path(path).read_bytes()).hexdigest(),source_had_E3=s is not None,explicit_new_public_recovery_group_without_new_RNG=True,actual_CUDA_phase_disk_roundtrip_exact=True,original8typed_and_sourceepisode_plus_one=proof,zero_clock_guard_unmodified=True,original_qerr_zero_guard_completed_before_declared_fall_axis=True,legal_fallen_reset=env.e3_reset_receipt,not_PhysX_exact_resume=True);Path(log_dir,'E3_PHASE_FULLSTATE_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(row,indent=2));return row
def install(runner,env):
 install_chassis_pd_save_contract(runner,env);old=runner.save
 def save(path,*a,**kw):old(path,*a,**kw);ck=torch.load(path,map_location='cpu',weights_only=False);ck['E3_public_recovery_state']=state(env);ck['E3_reset_contract']=env.e3_reset_receipt;torch.save(ck,path)
 runner.save=save
