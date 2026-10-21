from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;R=B/'reports';P=B/'H1_step270_native32_V4_payload';H=lambda b:hashlib.sha256(b).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
assert json.loads((R/'STEP270_COOKED_QUERY_V5_ALL256_ORIGINAL_AXIS_CPU_V3_ACTUAL.json').read_bytes())['passed']
assert json.loads((R/'STEP270_20K_EXPLICIT_FULLSTATE_MIGRATION_CPU_REFERENCE_ACTUAL.json').read_bytes())['passed_CPU_reference_only']
s=(P/'worker.py').read_text(encoding='utf8').replace('assert steps==480','assert steps==180').replace("'--num_envs','32'","'--num_envs','20000'").replace('c.scene.num_envs=32','c.scene.num_envs=20000').replace('env.num_envs==32','env.num_envs==20000').replace('num_envs=32','num_envs=20000').replace('x.shape==(32,35)','x.shape==(20000,35)')
s=s.replace("  torch.optim.Optimizer.__init__=forbid;factory=ns['build_env'];original_cfg=ns['Mod4EnvCfg']", "  factory=ns['build_env'];original_cfg=ns['Mod4EnvCfg']")
start=s.index('   for k,v in dict(gpu_max_rigid_contact_count=');end=s.index('   return c\n',start);s=s[:start]+s[end:]
s=s.replace("env.h1_witness_ids=torch.arange(32,device=env.device);env.h1_capture=True", "env.h1_capture=True")
start=s.index('  # Read-only COM observations,');end=s.index('  env.scene.update=update;',start)
s=s[:start]+s[end:].replace('  env.scene.update=update;old_term=', '  old_term=',1)
needle=";env.reset();env._h1_publish_external_request();assert not env.h1_phase.age_control.any();obs=vec.get_observations()"
assert s.count(needle)==1
resume='''
  # Actual RSL loader and original full D0-D7 chain, with no PPO update.
  runner_cfg=ns['runner_config']();runner_cfg=ns['handle_deprecated_rsl_rl_cfg'](runner_cfg,ns['metadata'].version('rsl-rl-lib'));owned_cfg=runner_cfg.to_dict();owned_cfg['algorithm']['class_name']='owned_h1_public4_mean_overflow_ppo_v2:PPO'
  assert owned_cfg['num_steps_per_env']==24 and owned_cfg['algorithm']['gamma']==.99 and owned_cfg['algorithm']['lam']==.95
  runner=ns['OnPolicyRunner'](vec,owned_cfg,log_dir=str(O/'fullstate_startup'),device='cuda:0');runner.load(str(src));runner.alg.optimizer.step=forbid
  from h1_step270_fullstate_checkpoint_candidate_uninstalled import resume_step270_new_episode,install_step270_save_contract,exact
  resume_proof=resume_step270_new_episode(runner,env,str(src),str(O/'fullstate_startup'));install_step270_save_contract(runner,env)
  startup=O/'ACTUAL_STEP270_FULL20K_STARTUP_FULLSTATE.pt';runner.save(str(startup));artifacts.append(dict(path=str(startup),relative=startup.relative_to(B).as_posix(),bytes=startup.stat().st_size,SHA=H(startup),kind='complete_new_task_startup_checkpoint_no_updates'))
  put('ACTUAL_RSL_FULLSTATE_AND_NEW_TASK_CONFIG.json',dict(epoch=time.time(),source_SHA=cfg['source_SHA'],source_Adam=674740,effective_runner_config=owned_cfg,all_original_D0_D7_resume_proof=resume_proof,no_optimizer_updates=True,new_phase_terrain_reward_migration=True,actual_GPU_roundtrip_complete=True))
  assert not env.h1_phase.age_control.any();obs=vec.get_observations()
'''
s=s.replace(needle,resume)
s=s.replace('witness_ids=list(range(32))','witness_ids=env.h1_witness_ids.detach().cpu().tolist()').replace('fresh32_seed=20260928,source20k_DR_not_restored=True','source20k_DR_and_command_private_RNG_restored_before_one_fresh_episode=True,source_phase_explicitly_migrated=True')
s=s.replace("steps=steps,callbacks=4*steps,num_envs=20000", "steps=steps,callbacks=4*steps,num_envs=20000")
s=s.replace('all_body_COM_and_all34_geometry_saved=True','all34_geometry_all31_contacts_saved=True,full_body_pose_witnesses8_not_all20k=True,actual_D7_COM_parameter_roundtrip=True')
s=s.replace("   persist();assert all(torch.equal", "   persist();assert exact(runner.alg.optimizer.state_dict(),state['optimizer_state_dict']) and exact(runner.alg.actor.state_dict(),state['actor_state_dict']) and exact(runner.alg.critic.state_dict(),state['critic_state_dict']);assert all(torch.equal")
s=s.replace("'Frozen source16 public0/4 jump evaluation; no PPO, scripted jump or added force.'", "'Source16 step270 full20k native180; optimizer loaded but zero updates; no learning GO.'")
# Configuration argument kept explicit; source optimizer LR is inherited separately by RSL.load.
s=s.replace("'--seed','20260928']", "'--seed','20260928','--steps_per_env','24','--learning_rate','0.0001']")
ast.parse(s)
payload=B/'H1_step270_full20k_native180_V1_delta';payload.mkdir()
with (payload/'worker.py').open('x',encoding='utf8',newline='\n') as f:f.write(s)
(payload/'h1_step270_fullstate_checkpoint_candidate_uninstalled.py').write_bytes((B/'h1_step270_fullstate_checkpoint_candidate_uninstalled.py').read_bytes())
parent=(P/'parent.py').read_text(encoding='utf8').replace('no_optimizer=True','optimizer_loaded_but_zero_updates=True')
with (payload/'parent.py').open('x',encoding='utf8',newline='\n') as f:f.write(parent)
cfg=json.loads((P/'FROZEN_CONFIG.json').read_bytes());cfg.update(kind='H1_step270_full20k_native180_V1',num_envs=20000,steps=180,wall_seconds=1800,no_optimizer_no_training_charge=False,optimizer_state_loaded_zero_updates_no_learning_charge=True);put(payload/'FROZEN_CONFIG.json',cfg)
manifest=json.loads((P/'SOURCE_MANIFEST.json').read_bytes())
for row in manifest['files']:
    if row['relative'] in ('worker.py','parent.py','FROZEN_CONFIG.json'):
        data=(payload/row['relative']).read_bytes();row.update(bytes=len(data),SHA=H(data))
extra=payload/'h1_step270_fullstate_checkpoint_candidate_uninstalled.py';manifest['files'].append(dict(relative=extra.name,bytes=extra.stat().st_size,SHA=H(extra.read_bytes())))
put(payload/'SOURCE_MANIFEST.json',manifest)
deploy=(B/'deploy_step270_cooked_query_V5_unused_root_once.py').read_text(encoding='utf8').replace('STEP270_COOKED_QUERY_V5','STEP270_FULL20K_NATIVE180_V1').replace('H1step270_cookedquery_2110v5','H1step270_full20k_native180_2110v1')
deploy=deploy.replace("('worker.py','FROZEN_CONFIG.json','SOURCE_MANIFEST.json')", "('worker.py','parent.py','h1_step270_fullstate_checkpoint_candidate_uninstalled.py','FROZEN_CONFIG.json','SOURCE_MANIFEST.json')")
deployer=B/'deploy_step270_full20k_native180_V1_unused_root_once.py';ast.parse(deploy)
with deployer.open('x',encoding='utf8',newline='\n') as f:f.write(deploy)
report=dict(epoch=time.time(),passed_source_AST_only=True,source_SHA=cfg['source_SHA'],source_Adam=674740,payload=str(payload),zip=json.loads((R/'STEP270_COOKED_QUERY_V5_SOURCE_AST_PREPARED_ACTUAL.json').read_bytes())['zip'],num_envs=20000,steps=180,callbacks=720,policy_hz=100,physics_dt=.0025,decimation=4,original_20k_physics_capacities_retained=True,original_RSL_actor9_critic8_optimizer17_loaded=True,all_D0_D7_and_command_private_RNG_resume_chain=True,new_phase270_explicit_roundtrip=True,source_optimizer_LR_inherited_not_reset=True,no_optimizer_step_or_learning_GO=True,deployer=dict(path=str(deployer),SHA=H(deployer.read_bytes()),unused=True),source_only_no_remote_Task_or_native_started=True,raw_allrow_geometry_contacts_and8_body_witnesses=True,cooked32_GPU_and_independent_CPU_pass_required=True)
put(R/'STEP270_FULL20K_NATIVE180_V1_SOURCE_AST_PREPARED_ACTUAL.json',report);print(json.dumps(report))
