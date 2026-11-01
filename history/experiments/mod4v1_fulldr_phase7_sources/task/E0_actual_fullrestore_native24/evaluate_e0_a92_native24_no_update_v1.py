"""NEW purpose: E0 a92 N20k complete source restore +24 mean-policy controls.
Exactly one source physical read/hash/decode via PinnedSource208. NO PPO/GO/budget.
"""
from pathlib import Path
import argparse,json,os,runpy,sys,time,traceback
SOURCE='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89d/e0/adaptation/final_valid_update82.pt'
SHA='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a'
BYTES=14031973;ITER=31984;ADAM=641200;LR=.00038443359375000017


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--task',type=Path,required=True);args=parser.parse_args()
    out=args.task.parent;task=json.loads(args.task.read_bytes());job=Path(task['runtime_job'])
    def put(name,value):
        with (out/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False)
    assert task['kind']=='MOD4V1_E0_A92_N20K_FULLRESTORE_NATIVE24_EVAL_ONLY_V1'
    assert task['execution_scope']=='EVAL_ONLY_NO_OPTIMIZER' and task['source_read_purpose'].startswith('NEW_E0_A92_FULLRESTORE_NATIVE24_')
    assert task['model_path']==SOURCE and task['model_SHA']==SHA and task['model_bytes']==BYTES
    assert task['num_envs']==20000 and task['controls']==24 and task['worker_limit_s']==900
    assert os.environ['CUDA_VISIBLE_DEVICES']==task['GPU_UUID']
    original=json.loads((job/'original_run_manifest.json').read_bytes())
    assert original['terrain']=='flat' and original['skill_tasks']=='all' and original['env']['RM_JUMP_SCRIPT_PROB']=='0'
    for key in list(os.environ):
        if key.startswith('RM_') or key in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):del os.environ[key]
    os.environ.update({k:str(v) for k,v in original['env'].items() if k not in ('RM_RESCUE_STOP_FILE','RM_RESCUE_DEADLINE')})
    os.environ.update(RM_MOD4_USD=str(job/'runtime/assets/robot.usd'),MOD4V1_E0_ASSET_DIR=str(job/'runtime/assets'),MOD4V1_E0_JOB_ROOT=str(job),MOD4_RESUME_QUEUE_CONTROL_US='20000')
    assert os.environ['RM_KEEP_STD']=='1' and os.environ['RM_MOD4_TERRAIN']=='flat'
    storage=job/'kit_isolation';storage.mkdir(exist_ok=False);(storage/'data').mkdir();(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}');os.environ['MOD4V1_E0_KIT_STORAGE_ROOT']=str(storage)
    mod=job/'runtime/isaac/mod4';sys.path[:0]=[str(mod),str(job/'runtime')]
    import torch
    from source_cache208_v3 import PinnedSource208,selected_source
    cache=PinnedSource208(torch,SOURCE,SHA,BYTES)  # sole physical source byte/hash/decode
    assert cache.state['iter']==ITER
    entry=mod/'train_mod4v1_e0.py';sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','20000','--seed','20260928','--steps_per_env','24','--learning_rate',str(LR),'--init_checkpoint',SOURCE,'--log_root',str(out/'logs'),'--run_name','E0_A92_NATIVE24_EVAL_ONLY_NO_UPDATE','--additional_iterations','1']
    ns=None;holder={};forbidden={'alg_update':0,'optimizer_step':0,'runner_learn':0}
    try:
        ns=runpy.run_path(str(entry),run_name='e0_a92_fullrestore_native24_eval_only')
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
            required={'SENSOR_RESUME_STARTUP_VERIFIED.json','DELAY_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json'}
            assert required.issubset(receipts)
            for name in required:assert json.loads(receipts[name].read_bytes())['source_sha256']==SHA
            guard=env._mod4v1_e0_nominal_guard;guard.assert_new_nominals_unchanged();nominal=guard.receipt();assert guard.reset_calls==1
            audit=env._mild_dr.audit();assert audit['actual_parameters_pass']
            obs=vec.get_observations();guard.check_observations(obs)
            assert obs['policy'].shape==(20000,35) and obs['critic'].shape==(20000,38)
            put('E0_N20K_FULLRESTORE_BEFORE_NATIVE24.json',dict(passed=True,execution_scope='EVAL_ONLY_NO_OPTIMIZER',source_SHA=SHA,source_iteration=ITER,source_Adam17=ADAM,source_LR=LR,original_core_STD17Adam_exact=True,original_six_helper_receipts={k:str(receipts[k]) for k in sorted(required)},nominal_guard=nominal,actual_mild_DR_audit=audit,interface=[35,38,6],source_cache=cache.receipt(),no_production_GO=True,canonical_access=False))
            tick=int(env._integrated_contact.tick);feedback=int(env._feedback_100hz_tick);calls=dict(env._physics_action_delay.calls);finite=True
            with torch.inference_mode():
                for _ in range(24):
                    before=int(env._integrated_contact.tick);fb=int(env._feedback_100hz_tick)
                    action=runner.alg.actor(obs,stochastic_output=False);assert action.shape==(20000,6)
                    obs,reward,done,info=vec.step(action)
                    finite=finite and all(bool(torch.isfinite(v).all()) for v in (action,obs['policy'],obs['critic'],reward))
                    assert int(env._integrated_contact.tick)-before==8 and int(env._feedback_100hz_tick)-fb==2
            assert finite and int(env._integrated_contact.tick)-tick==192 and int(env._feedback_100hz_tick)-feedback==48
            assert {k:env._physics_action_delay.calls[k]-calls[k] for k in ('legs','wheels')}=={'legs':192,'wheels':192}
            core_exact();guard.assert_new_nominals_unchanged();after=env._mild_dr.audit();assert after['actual_parameters_pass']
            counts=cache.receipt();assert counts['source_physical_byte_opens']==counts['source_decodes']==1 and all(v==0 for v in forbidden.values())
            put('E0_N20K_FULLRESTORE_NATIVE24_COMPLETE.json',dict(passed=True,execution_scope='EVAL_ONLY_NO_OPTIMIZER',source_SHA=SHA,source_iteration=ITER,source_Adam17=ADAM,source_LR=LR,num_envs=20000,controls=24,physics_callbacks=192,feedback_samples=48,actor_calls=24,optimizer_updates=0,forbidden_calls=forbidden,finite_policy_critic_action_reward=finite,core_actor_critic_STD17Adam_before_after_exact=True,source_iteration_and_LR_unchanged=True,one_original_fresh_reset=guard.reset_calls,new_nominal_guard=guard.receipt(),actual_mild_DR_audit_after=after,source_cache=counts,D6_scope='original gas damping not all joint friction',canonical_reads=0,canonical_writes=0,skill_evaluation_or_expert_graduation=False))
        rescue_training.learn=work
        with selected_source(cache):ns['main']()
        put('TRAINER_MAIN_CLOSE_RETURNED.json',dict(returned=True,mode='EVAL_ONLY_NO_OPTIMIZER'))
    except BaseException:
        put('E0_N20K_FULLRESTORE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc(),source_cache=cache.receipt(),forbidden_calls=forbidden,canonical_access=False));raise
    finally:
        put('SOURCE_FINAL_READ_COUNTS.json',cache.receipt())
        try:
            if 'env' in holder and not (out/'ENV_CLOSE_RETURNED.json').exists():holder['env'].close()
        finally:
            if ns is not None:put('APP_CLOSING.json',dict(calling_original_App_close=True));ns['app'].close()


if __name__=='__main__':main()
