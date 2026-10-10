"""Derive independent entries from immutable source338; never edit or run old entries."""
from pathlib import Path
import ast,hashlib,json,shutil,time
D=Path(__file__).resolve().parent;W=D.parent;P=D/'payload';C=P/'isaac/mod4';R=D/'reports';R.mkdir(exist_ok=True)
L=W/'MOD4_E1_G3_LEARNING_PREPARE_20261010';M=W/'MOD4_E1_G3_MATCHED_REVIEW_20261010'
def replace(s,old,new,count=1):
 assert s.count(old)==count,(old,s.count(old));return s.replace(old,new)
def main():
 # A local build is reversible. Every accepted build has a distinct byte receipt;
 # deployed frozen files are never rebuilt or edited in place.
 shutil.copy2(M/'implementation/retained_flat_command_math.py',C/'retained_flat_command_math.py')
 new=('retained_flat_command_math.py','retention_command_state.py','retention_flat_runtime.py','retention_learning_env.py','retention_checkpoint.py','train_e1_retention_resume_ppo.py','train_e1_retention_fresh_preflight_ppo.py')
 for old,name in (('train_e1_g3_reviewed_resume_ppo.py','train_e1_retention_resume_ppo.py'),('train_e1_g3_fresh_preflight_ppo.py','train_e1_retention_fresh_preflight_ppo.py')):
  s=(L/'payload/isaac/mod4'/old).read_text()
  env_import='from e1_reset_evidence_training_env import E1ResetEvidenceLearningEnv as Mod4Env' if name.endswith('resume_ppo.py') else 'from e1_terrain_training_env import E1TerrainLearningEnv as Mod4Env'
  s=replace(s,env_import,'from retention_learning_env import RetentionLearningEnv as Mod4Env')
  s=replace(s,'from g3_cad_wave_geometry import configure_g3 as configure_intro','from retention_flat_runtime import configure_retention as configure_intro')
  s=s.replace('from g3_terrain_checkpoint import install_e1_save_contract','from retention_checkpoint import install_e1_save_contract')
  if name.endswith('resume_ppo.py'):s=replace(s,'from g3_terrain_checkpoint import resume_e1_new_episode','from retention_checkpoint import resume_e1_new_episode')
  insertion="    for name in "+repr(new)+":\n        shutil.copy2(Path(__file__).parent/name,snapshot_dir/name);snapshot[name]=_sha256(Path(__file__).parent/name)\n    manifest['actual_retained_command_scope']=env.command_manager.get_term('twist').audit_retention()\n    manifest['legacy_terrain_command_ranges_describe_noneligible_gentle_only']=True\n"
  s=replace(s,'    manifest["src_sha256"] = snapshot',insertion+'    manifest["src_sha256"] = snapshot')
  s=replace(s,'        clock_health.write()','        clock_health.write()\n        env.write_retention_trace(log_dir)') if name.endswith('resume_ppo.py') else replace(s,'    info["log_dir"] = log_dir','    env.write_retention_trace(log_dir)\n    info["log_dir"] = log_dir')
  ast.parse(s);(C/name).write_text(s,encoding='utf8')
 s=(L/'payload/native_e1_g3_reviewed_probe.py').read_text()
 s=replace(s,'from e1_reset_evidence_training_env import E1ResetEvidenceLearningEnv as Mod4Env','from retention_learning_env import RetentionLearningEnv as Mod4Env')
 s=replace(s,'from g3_cad_wave_geometry import configure_g3 as configure_intro','from retention_flat_runtime import configure_retention as configure_intro')
 s=replace(s,' env.reset();obs=vec.get_observations();robot=env.scene'," if args.num_envs==10:\n  # SDK scope explicitly tests ten distinct generated plane supports. This is\n  # not a quota/placement change in native20k or PPO training.\n  plane=[r for r in env.scene.terrain.retention_assignment if r['family']=='plane_for_rm' and r['actual_mesh_flat'] and 17<=r['row']<=21 and r['column'] in (9,10)]\n  assert len(plane)==10\n  xy=torch.tensor([[(r['bounds'][0][0]+r['bounds'][1][0])*.5,(r['bounds'][0][1]+r['bounds'][1][1])*.5] for r in plane],device=env.device)\n  env.scene.env_origins[:,:2]=xy;env.scene.terrain.env_origins[:,:2]=xy\n env.reset();obs=vec.get_observations();robot=env.scene")
 s=replace(s,'  obs=one(obs)\n torch.cuda.synchronize();wall=',"  if args.num_envs==10 and i in (50,150,200,250):env.command_manager.get_term('twist')._resample_command(torch.arange(10,device=env.device));obs=vec.get_observations()\n  obs=one(obs)\n torch.cuda.synchronize();wall=")
 s=replace(s," Path(args.output).write_text(json.dumps(report,indent=2));", " env.write_retention_trace(Path(args.output).parent/(Path(args.output).stem+'_trace'))\n report['command_retention']=env.command_manager.get_term('twist').audit_retention()\n report['actual_generated_family_assignments']=env.scene.terrain.retention_assignment\n report['SDK_plane_support_placement_only']=args.num_envs==10\n report['SDK_forced_resampling_controls']=[50,150,200,250] if args.num_envs==10 else []\n assert len(env._retention_trace)==args.warmup+args.steps\n Path(args.output).write_text(json.dumps(report,indent=2));")
 ast.parse(s);(P/'native_e1_retention_probe.py').write_text(s,encoding='utf8')
 s=(L/'payload/supervise_e1_G3_reviewed_short_observation.py').read_text()
 s=s.replace('train_e1_g3_reviewed_resume_ppo.py','train_e1_retention_resume_ppo.py').replace('train_e1_g3_fresh_preflight_ppo.py','train_e1_retention_fresh_preflight_ppo.py').replace('native_e1_g3_reviewed_probe.py','native_e1_retention_probe.py')
 s=replace(s,"    e['RM_E1_G3_INITIAL_ADMISSION']='G2_to_G3_35mm'","    e['RM_E1_G3_INITIAL_ADMISSION']='G2_to_G3_35mm'\n    e['RM_E1_COMMAND_RETENTION_INITIAL_ADMISSION']='old_fullstate_to_verified_flat_modes'")
 s=replace(s,"MOD4_S3_E1_G2_MATCHED_CONTINUE_20261010/reports/SOURCE_FREEZE.json","MOD4_S3_E1_G3_REVIEWED_20261010/reports/SOURCE_FREEZE.json")
 s=replace(s,'    assert len(old)==330 and len(f)==338','    assert len(old)==338 and len(f)==338+read(R/\'COMMAND_SCOPE_BUILD.json\')[\'new_file_count\']')
 s=replace(s,"    assert read(R/'G3_TARGET_CPU_PASSED.json')['passed']","    assert read(R/'RETENTION_TARGET_CPU_PASSED.json')['passed']\n    assert read(R/'COMMAND_SCOPE_BUILD.json')['genuinely_new_command_scope']")
 s=replace(s,"        validator(ck['E1_terrain_state'],count)","        validator(ck['E1_terrain_state'],count)\n        if 'E1_retained_flat_command_state' in ck:\n            from retention_command_state import validate as command_validate\n            command_validate(ck['E1_retained_flat_command_state'],count)\n            assert ck['E1_terrain_state_legacy_command_ranges_are_noneligible_gentle_only']")
 s=replace(s,"MOD4_S3_E1_G2_MATCHED_CONTINUE_20261010/reports');state=read(old/'E1_STATE.json');row=read(old/'e1_G2_matched_continuation_PASSED.json')","MOD4_S3_E1_G3_REVIEWED_20261010/reports');state=read(old/'E1_STATE.json');row=read(old/'e1_G3_reviewed_observation_PASSED.json')")
 s=replace(s,"state['phase']=='E1_G2_matched_continuation_saved_review_ready'","state['phase']=='E1_G3_reviewed_saved_review_ready'")
 s=replace(s,'start_ticks=72519910','start_ticks=74243664')
 s=replace(s,"((10,300,'G3_ACTUAL_SDK'),(20000,120,'G3_NATIVE20K'))","((10,300,'RETENTION_ACTUAL_SDK'),(20000,120,'RETENTION_NATIVE20K'))")
 s=replace(s,"        results[label]=dict(path=", "        a=v['command_retention'];hist=a['sample_histogram'];plane=hist[1]\n        assert a['projection_error']<=1e-6 and all(plane[i]>0 for i in (2,3,4,5))\n        assert all(sum(r[2:6])==0 for r in hist[:1]+hist[2:]) and not a['pure_high_spin']\n        results[label]=dict(path=")
 s=replace(s,"    assert m['gas_damping_recipe']['profile']==", "    a=read(run/'RETENTION_COMMAND_ACTUAL.json');assert a['actual_controls']==h['control_steps']\n    if count==20000:\n        v=read(run/'E1_COMMAND_RETENTION_STARTUP_VERIFIED.json');assert v['actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact'] and v['old_full_D1_D7_optimizer_global_named_streams_verified'] and v['E1_episode_incremented_once']\n    assert m['gas_damping_recipe']['profile']==")
 s=replace(s,"            row['artifacts']['runtime']=read(R/'G3_BEHAVIOR_PACKAGE_READY.json')['runtime']", "            row['artifacts']['runtime']=read(R/'G3_BEHAVIOR_PACKAGE_READY.json')['runtime']\n            row['protocol']='approved_E1_G3_derived35mm_paired_approach040_behavior_v2'\n            row['frozen_approach_distance_m']=.4")
 s=replace(s,"            row['protocol']='approved_E1_G3_derived35mm_complete_wave_route_behavior_v1'", "            row['protocol']='approved_E1_G3_derived35mm_paired_approach040_behavior_v2'")
 s=replace(s,"    publish(init,'127-e1-g3-observation')","    publish(init,'129-e1-g3-command-retention')")
 s=s.replace('g3_discard128','retention_discard128').replace('g3_discard20k','retention_discard20k').replace('e1_G3_reviewed_observation','e1_G3_command_retention_observation')
 # The previous actual file name belongs to source338, not this new controller.
 s=s.replace("row=read(old/'e1_G3_command_retention_observation_PASSED.json')","row=read(old/'e1_G3_reviewed_observation_PASSED.json')")
 s=replace(s,'new_geometry_scope_genuinely_required=True','new_command_scope_genuinely_required=True,geometry_clock_D0_D7_existing_evidence_reused=True')
 s=s.replace("phase('E1_G3_reviewed_saved_review_ready',child=None)","phase('E1_G3_command_retention_saved_review_ready',child=None)")
 s=s.replace("'bounded_E1_G3_retention_repair_learning'","'bounded_E1_G3_command_retention_learning'")
 s=replace(s,"plan_stage='S3 E1 G3 derived35mm wave only replaces original random-height family; reviewed32058, 5min observation; D0-D7 unchanged'","plan_stage='S3 E1 G3 command retention: actual clear plane signed straight/world05 yaw1-2, other four families gentle; reviewed32058,300s observation; geometry/clock/D0-D7 unchanged'")
 ast.parse(s);(P/'supervise_e1_command_retention_once.py').write_text(s,encoding='utf8')
 files={p.relative_to(P).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
 for p in P.rglob('*.py'):ast.parse(p.read_text())
 proof=dict(epoch=time.time(),genuinely_new_command_scope=True,new_file_count=len(files),sha256=files,source338_untouched=True,geometry_clock_D0D7_reused=True,SDK_native_PPO_actual_pending=True,no_new_learning_launched=True,new_budget_seconds=0)
 (R/('PAYLOAD_BUILD_'+str(time.time_ns())+'.json')).write_text(json.dumps(proof,indent=2),encoding='utf8')
 (R/'PAYLOAD_PREPARED.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
 print(json.dumps(dict(files=len(files),prepared=True,no_deployment=True)))
if __name__=='__main__':main()
