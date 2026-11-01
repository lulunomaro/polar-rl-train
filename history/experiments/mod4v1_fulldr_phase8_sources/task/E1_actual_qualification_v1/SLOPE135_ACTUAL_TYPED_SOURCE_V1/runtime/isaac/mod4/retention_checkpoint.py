"""Old full state restored first; new command state explicitly saved and resumed."""
from pathlib import Path
import hashlib,json,os,time,torch
import g3_terrain_checkpoint as g
from retention_command_state import validate,same,PROFILE
def install_e1_save_contract(runner,env):
 g.install_e1_save_contract(runner,env);original=runner.save
 def save(path,*a,**kw):
  original(path,*a,**kw);ck=torch.load(path,map_location='cpu',weights_only=False)
  ck['E1_retained_flat_command_state']=env.command_manager.get_term('twist').state_dict_retention()
  ck['E1_current_command_profile']=PROFILE
  ck['E1_terrain_state_legacy_command_ranges_are_noneligible_gentle_only']=True
  torch.save(ck,path);env.write_retention_trace(Path(path).parent)
 runner.save=save
def resume_e1_new_episode(runner,env,path,log_dir):
 ck=torch.load(path,map_location='cpu',weights_only=False);term=env.command_manager.get_term('twist');same_scope='E1_retained_flat_command_state' in ck
 if same_scope:term.load_state_retention(ck['E1_retained_flat_command_state']);assert same(term.state_dict_retention(),ck['E1_retained_flat_command_state'])
 else:assert os.environ.get('RM_E1_COMMAND_RETENTION_INITIAL_ADMISSION')=='old_fullstate_to_verified_flat_modes'
 before=term.state_dict_retention();tmp=Path(log_dir)/'E1_RETAINED_COMMAND_ACTUAL_CUDA_ROUNDTRIP.pt';torch.save(before,tmp);term.load_state_retention(torch.load(tmp,map_location='cpu',weights_only=False));assert same(before,term.state_dict_retention())
 episode=env._e1_episode.clone();old=g.resume_e1_new_episode(runner,env,path,log_dir);assert torch.equal(env._e1_episode,episode+1)
 proof=dict(epoch=time.time(),pid=os.getpid(),source_sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),command_profile=PROFILE,predecessor_command_state_restored_exact=same_scope,explicitly_new_command_scope=not same_scope,actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact=True,old_full_D1_D7_optimizer_global_named_streams_verified=old['complete_D1_D7_optimizer_global_named_streams_verified'],old_terrain_bookkeeping_and_new_G2_G3_disclosure=old,one_new_physical_episode=True,E1_episode_incremented_once=True,PhysX_exact_resume_claimed=False,actual_command_audit=term.audit_retention())
 Path(log_dir,'E1_COMMAND_RETENTION_STARTUP_VERIFIED.json').write_text(json.dumps(proof,indent=2));return proof
