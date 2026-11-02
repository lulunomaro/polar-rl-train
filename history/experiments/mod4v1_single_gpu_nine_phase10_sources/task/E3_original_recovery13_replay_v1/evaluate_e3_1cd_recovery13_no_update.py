"""NEW purpose: E3 b3 N20k complete source restore +24 mean-policy controls.
Exactly one source physical read/hash/decode via PinnedSource208. NO PPO/GO/budget.
"""
from pathlib import Path
import argparse,json,os,runpy,sys,time,traceback
SOURCE='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E3_PPO50_GAS400_2610v97/e3/adaptation/final_valid_update87.pt'
SHA='1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8'
BYTES=14715029;ITER=43090;ADAM=866060;LR=.0002562890625000001


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--task',type=Path,required=True);args=parser.parse_args()
    out=args.task.parent;task=json.loads(args.task.read_bytes());job=Path(task['runtime_job'])
    def put(name,value):
        with (out/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False)
    assert task['kind']=='MOD4V1_E3_1CD_RECOVERY13_SKILL160_EVAL_ONLY_V1'
    assert task['execution_scope']=='EVAL_ONLY_NO_OPTIMIZER' and task['source_read_purpose'].startswith('NEW_E3_1CD_RECOVERY13_SKILL160_')
    assert task['model_path']==SOURCE and task['model_SHA']==SHA and task['model_bytes']==BYTES
    assert task['num_envs']==20000 and task['controls']==160 and task['worker_limit_s']==900
    assert os.environ['CUDA_VISIBLE_DEVICES']==task['GPU_UUID']
    original=json.loads((job/'original_run_manifest.json').read_bytes())
    assert original['terrain']=='flat' and original['skill_tasks']=='all' and original['env']['RM_JUMP_SCRIPT_PROB']=='0'
    for key in list(os.environ):
        if key.startswith('RM_') or key in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):del os.environ[key]
    os.environ.update({k:str(v) for k,v in original['env'].items() if k not in ('RM_RESCUE_STOP_FILE','RM_RESCUE_DEADLINE')})
    os.environ.update(RM_MOD4_USD=str(job/'runtime/assets/robot.usd'),MOD4V1_E3_ASSET_DIR=str(job/'runtime/assets'),MOD4V1_E3_JOB_ROOT=str(job),MOD4_RESUME_QUEUE_CONTROL_US='20000')
    assert os.environ['RM_KEEP_STD']=='1' and os.environ['RM_MOD4_TERRAIN']=='flat'
    os.environ.update(OWN_E2_H1_KIND='E3_PUBLIC_RECOVERY',RM_SPAWN_GRACE_STEPS='5',RM_JUMP_SCRIPT_PROB='0',RM_MOD4_MAP='',RM_MOD4_TERRAIN='flat')
    storage=job/'kit_isolation';storage.mkdir(exist_ok=False);(storage/'data').mkdir();(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}');os.environ['MOD4V1_E3_KIT_STORAGE_ROOT']=str(storage)
    mod=job/'runtime/isaac/mod4';sys.path[:0]=[str(mod),str(job/'runtime'),str(job/'lib')]
    import torch
    from source_cache208_v3 import PinnedSource208,selected_source
    cache=PinnedSource208(torch,SOURCE,SHA,BYTES)  # sole physical source byte/hash/decode
    assert cache.state['iter']==ITER
    entry=mod/'train_mod4v1_e3.py';sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','20000','--seed','20260928','--steps_per_env','24','--learning_rate',str(LR),'--init_checkpoint',SOURCE,'--log_root',str(out/'logs'),'--run_name','E3_1CD_RECOVERY13_SKILL160_NO_UPDATE','--additional_iterations','1']
    ns=None;holder={};forbidden={'alg_update':0,'optimizer_step':0,'runner_learn':0}
    try:
        ns=runpy.run_path(str(entry),run_name='e3_1cd_fullrestore_native24_eval_only')
        import rescue_training
        from spring_pressure_checkpoint import exact
        glob=ns['main'].__globals__;oldbuild=glob['build_env'];olddescribe=glob['describe']
        def witnessed_build():
            env=oldbuild();holder['env']=env;oldclose=env.close
            def closed(*a,**k):
                result=oldclose(*a,**k)
                if not (out/'ENV_CLOSE_RETURNED.json').exists():put('ENV_CLOSE_RETURNED.json',dict(closed=True))
                return result
            env.close=closed;return env
        def described(env,extra=None):
            return olddescribe(env,dict(extra or {},mode='EVAL_ONLY_NO_OPTIMIZER',source_read_purpose=task['source_read_purpose']))
        glob['build_env']=witnessed_build;glob['describe']=described
        def work(runner,n,log_dir):
            env=runner.env.unwrapped;vec=runner.env;source=cache.state
            runner.logger.writer=None
            def forbidden_call(name):
                def fail(*a,**k):forbidden[name]+=1;raise RuntimeError('NO_UPDATE_EVAL forbids '+name)
                return fail
            runner.alg.update=forbidden_call('alg_update');runner.alg.optimizer.step=forbidden_call('optimizer_step');runner.learn=forbidden_call('runner_learn')
            runner.alg.actor.eval();runner.alg.critic.eval()
            def core_exact():
                for key,value in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(value,source[key]),key
                state=runner.alg.optimizer.state_dict();assert len(state['state'])==17 and {int(v['step']) for v in state['state'].values()}=={ADAM}
                assert all(g['lr']==LR for g in state['param_groups']) and runner.current_learning_iteration==ITER
            core_exact();assert runner.alg.learning_rate==LR
            assert env.num_envs==20000 and env.physics_dt==.0025 and env.step_dt==.02 and env.cfg.decimation==8
            assert env.cfg.terminations.closure.params['threshold']==.01 and env.cfg.terminations.mimic.params['threshold']==.01
            assert env._physics_action_delay.queue.control_us==20000 and env._sim_step_counter==0
            receipts={p.name:p for p in Path(log_dir).glob('*STARTUP_VERIFIED.json')}
            required={'SENSOR_RESUME_STARTUP_VERIFIED.json','DELAY_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E3_PHASE_FULLSTATE_RESUME_STARTUP_VERIFIED.json'}
            assert required.issubset(receipts)
            for name in required:
                receipt=json.loads(receipts[name].read_bytes());assert receipt.get('source_sha256',receipt.get('source_SHA'))==SHA
            phase_proof=json.loads(receipts['E3_PHASE_FULLSTATE_RESUME_STARTUP_VERIFIED.json'].read_bytes());assert phase_proof['source_had_E3']
            phase=source['E3_public_recovery_state']['phase'];assert len(phase['tensors'])==7 and all(v.shape[0]==20000 for v in phase['tensors'].values())
            term=env.command_manager.get_term('twist');assert type(env).__module__=='e3_recovery_runtime_v1' and term._dt==.02
            assert env.e3_reset_enabled and not env.recovery.age.any() and env._e3_fixed_reset_cache.pick==34
            assert env._e3_fixed_reset_cache.source_sha=='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83'
            assert env.recovery.recipe.shape==(20000,) and set(env.recovery.recipe.tolist())==set(range(13))
            guard=env._mod4v1_e3_nominal_guard;guard.assert_new_nominals_unchanged();nominal=guard.receipt();assert guard.reset_calls==1
            audit=env._mild_dr.audit();assert audit['actual_parameters_pass']
            obs=vec.get_observations();guard.check_observations(obs)
            assert obs['policy'].shape==(20000,35) and obs['critic'].shape==(20000,38)
            put('E3_RECOVERY13_FULLRESTORE_BEFORE_REPLAY.json',dict(passed=True,execution_scope='EVAL_ONLY_NO_OPTIMIZER',source_SHA=SHA,source_iteration=ITER,source_Adam17=ADAM,source_LR=LR,original_core_STD17Adam_exact=True,original_seven_helper_receipts={k:str(receipts[k]) for k in sorted(required)},nominal_guard=nominal,actual_mild_DR_audit=audit,interface=[35,38,6],source_cache=cache.receipt(),no_production_GO=True,canonical_access=False))
            tick=int(env._integrated_contact.tick);feedback=int(env._feedback_100hz_tick);calls=dict(env._physics_action_delay.calls);finite=True
            phase_runtime=env.recovery
            initial_episode=env._sensor_mild.episode.clone()
            initial_recipe=phase_runtime.recipe.clone()
            original_credit_seen=torch.zeros(20000,dtype=torch.bool,device=env.device)
            original_peak=phase_runtime.peak.clone()
            first_age=torch.zeros(20000,dtype=torch.long,device=env.device)
            max_stable=torch.zeros_like(first_age)
            first_credit_age=torch.full_like(first_age,-1)
            first_terminated=torch.zeros_like(original_credit_seen)
            first_timeout=torch.zeros_like(original_credit_seen)
            old_phase_update=phase_runtime.update
            old_compute_term=env.termination_manager.compute
            def observe_original_phase(gravity_z,root_speed,angular_speed):
             old_phase_update(gravity_z,root_speed,angular_speed)
             mask=env._sensor_mild.episode==initial_episode
             event=mask&phase_runtime.credited&~original_credit_seen
             first_credit_age[event]=phase_runtime.age[event]
             original_credit_seen[mask]|=phase_runtime.credited[mask]
             original_peak[mask]=torch.maximum(original_peak[mask],phase_runtime.peak[mask])
             first_age[mask]=phase_runtime.age[mask]
             max_stable[mask]=torch.maximum(max_stable[mask],phase_runtime.stable[mask])
            def observe_original_term(*aa,**kk):
             result=old_compute_term(*aa,**kk)
             mask=env._sensor_mild.episode==initial_episode
             first_terminated[mask]|=env.termination_manager.terminated[mask]
             first_timeout[mask]|=env.termination_manager.time_outs[mask]
             return result
            phase_runtime.update=observe_original_phase
            env.termination_manager.compute=observe_original_term
            with torch.inference_mode():
                for control_index in range(160):
                    before=int(env._integrated_contact.tick);fb=int(env._feedback_100hz_tick)
                    action=runner.alg.actor(obs,stochastic_output=False);assert action.shape==(20000,6)
                    obs,reward,done,info=vec.step(action)
                    finite=finite and all(bool(torch.isfinite(v).all()) for v in (action,obs['policy'],obs['critic'],reward))
                    assert int(env._integrated_contact.tick)-before==8 and int(env._feedback_100hz_tick)-fb==2
                    if control_index==23:put('NATIVE24_PART_OF_RECOVERY13_CASE.json',dict(passed=True,controls=24,physics=192,feedback=48,optimizer_updates=0,source_SHA=SHA))
            assert finite and int(env._integrated_contact.tick)-tick==1280 and int(env._feedback_100hz_tick)-feedback==320
            assert {k:env._physics_action_delay.calls[k]-calls[k] for k in ('legs','wheels')}=={'legs':1280,'wheels':1280}
            core_exact();guard.assert_new_nominals_unchanged();after=env._mild_dr.audit();assert after['actual_parameters_pass']
            counts=cache.receipt();assert counts['source_physical_byte_opens']==counts['source_decodes']==1 and all(v==0 for v in forbidden.values())
            phase_runtime.update=old_phase_update
            env.termination_manager.compute=old_compute_term
            recipe_rows=[]
            for recipe_id in range(13):
             ids=initial_recipe==recipe_id
             n=int(ids.sum())
             credit=original_credit_seen[ids]
             peaks=original_peak[ids]
             ages=first_credit_age[ids&original_credit_seen]
             recipe_rows.append(dict(recipe=recipe_id,num_envs=n,initial_request_recipe=recipe_id!=12,original_credited_count=int(credit.sum()),original_credited_and_no_first_termination_count=int((ids&original_credit_seen&~first_terminated).sum()),first_terminated_count=int(first_terminated[ids].sum()),first_timeout_count=int(first_timeout[ids].sum()),first_age_max=int(first_age[ids].max()),max_original_stable_age=int(max_stable[ids].max()),original_peak_min=float(peaks.min()),original_peak_mean=float(peaks.mean()),original_peak_max=float(peaks.max()),first_credit_age_min=int(ages.min())if ages.numel()else None,first_credit_age_max=int(ages.max())if ages.numel()else None))
            put('ORIGINAL_E3_RECOVERY13_FIRST_EPISODE_FACTS.json',dict(kind='ORIGINAL13RECIPES_PHASE_CREDIT_OBSERVATION_NOT_NEW_GRADUATION_GATE',source_SHA=SHA,num_envs=20000,controls=160,seconds=3.2,policy_hz=50,public_phase_age_hz=100,original_request_age_limit=300,original_good_gravity_z_less_than=-.984807753,original_good_speed_m_s_less_than=.03,original_good_ang_rad_s_less_than=.2,original_credit_stable_age_at_least=50,source_phase_SHA='5883e0461d667ed474c29f1a07f78b88d4a8ee07f9570ae9c9df81a6584319a7',rows=recipe_rows,first_episode_identity_not_reset_stitched=True,no_new_RNG_action_mode_physics_reward_or_grad_threshold=True,does_not_infer_full_expert_graduation=True))
            put('E3_RECOVERY13_SKILL160_COMPLETE.json',dict(passed=True,execution_scope='EVAL_ONLY_NO_OPTIMIZER',source_SHA=SHA,source_iteration=ITER,source_Adam17=ADAM,source_LR=LR,num_envs=20000,controls=160,physics_callbacks=1280,feedback_samples=320,actor_calls=160,optimizer_updates=0,forbidden_calls=forbidden,finite_policy_critic_action_reward=finite,core_actor_critic_STD17Adam_before_after_exact=True,source_iteration_and_LR_unchanged=True,one_original_fresh_reset=guard.reset_calls,E3_recovery13_phase7_private_command_RNG_restored=True,original_declared_fall_publish_after_ONE_reset=True,producer_effort_owner_field="UNDEFINED_OR_UNKNOWN_NO_NEW_GATE",new_nominal_guard=guard.receipt(),actual_mild_DR_audit_after=after,source_cache=counts,D6_scope='original gas damping not all joint friction',canonical_reads=0,canonical_writes=0,skill_evaluation=True,expert_graduation=False))
        rescue_training.learn=work
        with selected_source(cache):ns['main']()
        put('TRAINER_MAIN_CLOSE_RETURNED.json',dict(returned=True,mode='EVAL_ONLY_NO_OPTIMIZER'))
    except BaseException:
        put('E3_RECOVERY13_SKILL160_ORIGINAL_ERROR.json',dict(error=traceback.format_exc(),source_cache=cache.receipt(),forbidden_calls=forbidden,canonical_access=False));raise
    finally:
        put('SOURCE_FINAL_READ_COUNTS.json',cache.receipt())
        try:
            if 'env' in holder and not (out/'ENV_CLOSE_RETURNED.json').exists():holder['env'].close()
        finally:
            if ns is not None:put('APP_CLOSING.json',dict(calling_original_App_close=True));ns['app'].close()


if __name__=='__main__':main()
