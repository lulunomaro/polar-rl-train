"""Explicit qualified CURB20->35 height-only migration; original typed D0-D7 loaders."""
from pathlib import Path
import hashlib,json,os,time,torch
from e1_terrain_checkpoint import current_state as base_state,identity
from e1_terrain_state import validate as validate_base
from curb20_entry_current_state import validate as validate_source20
from chassis_pd_checkpoint import install_chassis_pd_save_contract,resume_chassis_pd_new_episode
from retention_command_state import validate as validate_command,same
SOURCE_SHA='06314ce7a996885bd268104cfa0842417d2d3d9619f1e9b1a7936f3762485d33'
PROFILE='mod4_CURB_derived35mm_strip150_mirrored_entryreset_v1'
def validate(state,n):
 assert state['profile']==PROFILE and state['CURB_height_m']==.035 and state['CURB_strip_width_m']==.150
 assert state['CURB_vertical_unsmoothed'] and state['CURB_derived_not_actual_RM002']
 assert len(state['CURB_profile_sha256'])==64 and state['entry_origin_bound_cache'] and state['entry_no_new_rng']
 validate_base(dict(state,profile='mod4_intro_gentle_v1'),n)
def current_state(env):
 from curb20_entry_v3_runtime import reset_entry_xy
 reset_entry_xy(env,torch.arange(env.num_envs,device=env.device));s=base_state(env);r=env._curb_entry_map_receipt
 s.update(profile=PROFILE,CURB_height_m=.035,CURB_strip_width_m=.150,CURB_vertical_unsmoothed=True,CURB_derived_not_actual_RM002=True,CURB_profile_sha256=hashlib.sha256(Path(__file__).with_name('curb35_profile.json').read_bytes()).hexdigest(),entry_reset_profile=r['profile'],entry_origin_bound_cache=True,entry_no_new_rng=True,entry_map_sha256=r['map_sha256'],entry_assignment_sha256=env.scene.terrain.retention_assignment_sha,entry_runtime_sha256=hashlib.sha256(Path(__file__).with_name('curb20_entry_v3_runtime.py').read_bytes()).hexdigest())
 validate(s,env.num_envs);return s
def install_e1_save_contract(runner,env):
 install_chassis_pd_save_contract(runner,env);original=runner.save
 def save(path,*a,**kw):
  original(path,*a,**kw);ck=torch.load(path,map_location='cpu',weights_only=False);ck['E1_terrain_state']=current_state(env);ck['E1_retained_flat_command_state']=env.command_manager.get_term('twist').state_dict_retention();ck['E1_current_command_profile']=ck['E1_retained_flat_command_state']['profile'];ck['E1_terrain_state_legacy_command_ranges_are_noneligible_gentle_only']=True;ck['independent_terrain_expert']='E1_CURB35';ck['CURB35_source878_SHA']=SOURCE_SHA;ck['E1_terrain_resume_contract']='Explicit same CURB35 protected140 continuation; full typed state restored then one fresh physical episode, not PhysX exactresume.';torch.save(ck,path)
 runner.save=save
def resume_e1_new_episode(runner,env,path,log_dir):
 path=Path(path);ck=torch.load(path,map_location='cpu',weights_only=False);assert hashlib.sha256(path.read_bytes()).hexdigest()==SOURCE_SHA
 st=ck['E1_terrain_state'];validate(st,env.num_envs);cmd=ck['E1_retained_flat_command_state'];validate_command(cmd,env.num_envs)
 assert st['CURB_height_m']==.035 and st['CURB_strip_width_m']==.15
 for key,attr in [('spawn_xy','_rough_spawn_xy'),('reset_expected_q','_rough_probe_expected_q'),('episode','_e1_episode')]:
  getattr(env,attr).copy_(st[key].to(env.device));assert torch.equal(getattr(env,attr).cpu(),st[key].cpu())
 term=env.command_manager.get_term('twist');assignment=env.scene.terrain.retention_assignment_sha
 if assignment==cmd['assignment_sha256']:
  term.load_state_retention(cmd);assert same(term.state_dict_retention(),cmd);migration=dict(source_command_and_private_RNG_exact=True,assignment_changed=False)
 else:
  from curb20_command_migration_environment_view import restore_source_then_bind_CURB
  migration=restore_source_then_bind_CURB(term,cmd,cmd['assignment_sha256'])
 before=current_state(env);assert identity(st)==identity(before),'Same35 geometry/recipe identity must match protected source';command=term.state_dict_retention();roundtrip=Path(log_dir)/'CURB35_TYPED_TERRAIN_COMMAND_ACTUAL_CUDA_ROUNDTRIP.pt';torch.save(dict(terrain=before,command=command),roundtrip);rt=torch.load(roundtrip,map_location='cpu',weights_only=False);assert same(rt['terrain'],before) and same(rt['command'],command)
 for key,attr in [('spawn_xy','_rough_spawn_xy'),('reset_expected_q','_rough_probe_expected_q'),('episode','_e1_episode')]:getattr(env,attr).copy_(rt['terrain'][key].to(env.device))
 term.load_state_retention(rt['command']);assert same(current_state(env),before) and same(term.state_dict_retention(),command)
 episode=st['episode'].to(env.device).clone();old=resume_chassis_pd_new_episode(runner,env,path,log_dir)
 assert torch.equal(env._e1_episode,episode+1) and env._rough_query_tick is None
 assert identity(current_state(env))==identity(before)
 term._write_dynamic(torch.arange(env.num_envs,device=env.device));assert term.audit_retention()['projection_error']<=1e-6
 proof=dict(epoch=time.time(),pid=os.getpid(),source_SHA=SOURCE_SHA,explicit_same_height35_continuation=True,source_actor_critic_STD_optimizer_retained=True,source_terrain_bookkeeping_restored_before_new_physical_episode=True,actual_CUDA_terrain_and_command_disk_roundtrip_exact=True,sourceepisode_plus_one=True,command_migration=migration,all_D1_D7_original_fullstate_loaders=old,actual_source_geometry_identity_equal_same35=True,new_geometry_identity=identity(current_state(env)),PhysX_exactresume=False)
 for name in ('E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json'):Path(log_dir,name).write_text(json.dumps(proof,indent=2))
 return proof
