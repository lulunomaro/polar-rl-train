"""Frozen W35 original20k mean loop, NEW observed commandUID/cycle measurement."""
from pathlib import Path
import argparse,hashlib,json,os,runpy,sys,time,traceback
import skill_task208 as C
OUT=None
def H(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(name,value):
    with (OUT/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)

def main():
    global OUT
    p=argparse.ArgumentParser();p.add_argument('--job-root',required=True,type=Path);a=p.parse_args()
    job=a.job_root.resolve();assert str(job)==C.JOB
    task=read(job/'FROZEN_CASE_TASK.json');C.validate_task(task)
    assert H(__file__)==task['worker_SHA'] and os.environ.get('CUDA_VISIBLE_DEVICES')==C.GPU
    assert H(job/C.CPU_REPORT)==task['actual_CPU_report_SHA'] and H(job/C.CPU_WAIT)==task['actual_CPU_waited_proof_SHA']
    wait=read(job/C.CPU_WAIT);assert wait['passed'] and wait['actual_waited'] and wait['returncode']==0 and not wait['deadline_terminated']
    OUT=job/'frozen_regression';OUT.mkdir();deadline=time.time()+1680
    source=job/'source/W35_ADAPTED92_FINAL78.pt';assert source.stat().st_size==C.MODEL_BYTES and H(source)==C.MODEL
    K=job/'kit_isolation';assert not K.exists();K.mkdir()
    for name in ('data','DerivedDataCache'):(K/name).mkdir()
    with (K/'data/user.config.json').open('x') as f:f.write('{}')
    os.environ['MOD4_W35_OWN_KIT_STORAGE_ROOT']=str(K)
    os.environ['MOD4_NEW208_JOB_ROOT']=str(job)
    original=read(job/'original_run_manifest.json');assert H(job/'original_run_manifest.json')=='0543b0c47c53e15da0d7d017693d2b69f7f6354ef088c3a1b8ed2b9cc56e2beb'
    for key in list(os.environ):
        if key.startswith('RM_') or key in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):del os.environ[key]
    env={k:str(v) for k,v in original['env'].items() if k not in ('RM_RESCUE_STOP_FILE','RM_RESCUE_DEADLINE')}
    assert env['RM_HEIGHT_MIN']==env['RM_HEIGHT_MAX']=='.25' and env['RM_KEEP_STD']=='1'
    env.update(RM_MOD4_USD=str(job/'runtime/assets/robot.usd'),RM_RESCUE_STOP_FILE=str(OUT/'STOP.json'),RM_RESCUE_DEADLINE=str(deadline))
    os.environ.update(env);os.environ['MOD4_RESUME_QUEUE_CONTROL_US']='20000'
    mod=job/'runtime/isaac/mod4';sys.path[:0]=[str(job),str(job/'lib'),str(mod),str(job/'runtime')]
    entry=mod/'skill_entry208.py'
    sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','20000','--seed','20260928','--steps_per_env','24','--learning_rate','.00011390625000000003','--save_interval','25','--init_checkpoint',str(source),'--log_root',str(OUT/'logs'),'--run_name','FROZEN_W35_FULL_WORLD_SKILL208_NO_PPO','--additional_iterations','1']
    import launcher208 as own_launcher
    assert Path(own_launcher.__file__).resolve()==mod/'launcher208.py'
    ns=runpy.run_path(str(entry),run_name='frozen_W35_original92_restore_config')
    import carb,torch,rescue_training,sensor_resume_contract,retention_checkpoint
    from retention_flat_runtime_named_owned import RetainedFlatNamedOwnedCommand
    from spring_pressure_checkpoint import exact
    from spring_nominal_sdk_readback import tensor
    from panel208 import W35DomainPanel
    from early208 import W35EarlyObserver
    from skill_cycle208 import FullWorldCycle208 as W35UIDCycleBook
    from w35_base208 import profile_key
    settings=carb.settings.get_settings()
    assert Path(settings.get('/UJITSO/datastore/localCachePath')).resolve()==K/'DerivedDataCache'
    assert Path(settings.get('/app/userConfigPath')).resolve()==K/'data/user.config.json'
    assert settings.get('/physics/cooking/ujitsoCollisionCooking') is True
    assert settings.get('/physics/cooking/ujitsoRemoteCacheEnabled') is False
    assert settings.get('/persistent/physics/cooking/ujitsoCookingMaxProcessCount')==16
    put('ACTUAL_OWN_KIT_STORAGE_PATHS_BEFORE_ENV.json',dict(passed=True,cache=str(K/'DerivedDataCache'),user_config=str(K/'data/user.config.json'),cooking_controls_unchanged=True))
    early=W35EarlyObserver(torch,OUT/'early_original_retained_resample',expected_n=20000)
    early.install(RetainedFlatNamedOwnedCommand,sensor_resume_contract,retention_checkpoint)
    panel_state=[None]

    def work(runner,n,log_dir):
        runner.logger.writer=None;runner.alg.learning_rate=runner.alg.optimizer.param_groups[0]['lr']
        real=runner.env.unwrapped;vec=runner.env;cmd=real.command_manager.get_term('twist');robot=real.scene['robot']
        assert real.num_envs==20000 and real.physics_dt==.0025 and real.step_dt==.02 and real.cfg.decimation==8 and real._sim_step_counter==0
        assert real.cfg.episode_length_s==20 and real._physics_action_delay.queue.control_us==20000
        assert runner.current_learning_iteration==32336 and runner.alg.learning_rate==.00011390625000000003
        assert len(runner.alg.optimizer.state_dict()['state'])==17 and {int(x['step']) for x in runner.alg.optimizer.state_dict()['state'].values()}=={648360}
        assert real.spring_pressure_recipe()['nominal_stiffness_N_m']==2000
        assert real._w35_gas400_selected_bank_compatibility['selected_pose_index']==34
        assert len(real._w35_gas400_asset_compatibility['authorized_four_scalar_changes'])==4
        receipts=list(Path(log_dir).glob('*STARTUP_VERIFIED.json'))
        required={'SENSOR_RESUME_STARTUP_VERIFIED.json','DELAY_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','E1_COMMAND_RETENTION_STARTUP_VERIFIED.json'}
        assert required<={x.name for x in receipts}
        for q in receipts:assert read(q).get('source_sha256',C.MODEL)==C.MODEL
        runner.alg.actor.eval();runner.alg.critic.eval()
        before={key:{name:value.detach().clone() for name,value in model.state_dict().items()} for key,model in [('actor',runner.alg.actor),('critic',runner.alg.critic)]}
        opt={key:{name:value.detach().clone() if torch.is_tensor(value) else value for name,value in row.items()} for key,row in runner.alg.optimizer.state_dict()['state'].items()}
        put(C.FULLRESTORE,dict(passed=True,source_SHA=C.MODEL,Adam_step=648360,stored_RSL_iteration=32336,
            actual_algorithm_and_optimizer_LR=runner.alg.learning_rate,receipts=[dict(path=str(q),value=read(q)) for q in receipts],
            original_D1_D7_G3_retained_command_nearest250_reset_preserved=True,no_PPO_norm_or_optimizer_update=True))
        names=list(real.termination_manager.active_terms)
        declared=[dict(name=name,time_out=bool(real.termination_manager.get_term_cfg(name).time_out),function=repr(real.termination_manager.get_term_cfg(name).func),parameters=repr(real.termination_manager.get_term_cfg(name).params)) for name in names]
        put('ORIGINAL_W35_TASK_COMMAND_AND_TERMINATION_CRITERIA.json',dict(original_run_manifest_SHA=H(job/'original_run_manifest.json'),height_command_m=.25,
            retained_command_scope=cmd.audit_retention(),criterion_terms=declared,original_reward_reset_thresholds_unmodified=True,
            cycle_or_command_event_NOT_original_skill_graduation=True))
        book=W35UIDCycleBook(torch,real.num_envs,real.device,OUT)
        adopted=early.adopt_original_origin(cmd,book.adopt_observed_initial_packet)
        early.consumer=book.original_event
        put(C.ORIGIN,dict(passed=adopted,source_SHA=C.MODEL,ids_observed=20000 if adopted else 0,
            initial_left_censored=not adopted,physics_tick=int(real._sim_step_counter),
            timer_min=float(cmd.time_left.min()),timer_max=float(cmd.time_left.max()),
            original_counter_min=int(cmd.command_counter.min()),original_counter_max=int(cmd.command_counter.max()),
            phase_zero=bool((cmd.phase_elapsed==0).all()),diagnostic_errors=list(early.errors),
            original_sampler_RNG_commands_timers_not_modified=True,not_source_CPU_synthetic_claim=True))
        panel=W35DomainPanel(real,torch,OUT,task);panel_state[0]=panel
        apply_start=dict(real._physics_action_delay.calls);start_tick=int(real._integrated_contact.tick);start_feedback=int(real._feedback_100hz_tick)
        oldterm=real.termination_manager.compute;ctx={};terminal_calls=[0];coverage=[True]
        def term(*args,**kwargs):
            result=oldterm(*args,**kwargs);tm=real.termination_manager;terminal_calls[0]+=1
            non_timeout=torch.zeros_like(tm.terminated);timeouts=torch.zeros_like(tm.time_outs)
            for name in names:
                if tm.get_term_cfg(name).time_out:timeouts|=tm.get_term(name).bool()
                else:non_timeout|=tm.get_term(name).bool()
            coverage[0]=coverage[0] and bool(torch.equal(non_timeout,tm.terminated)) and bool(torch.equal(timeouts,tm.time_outs))
            panel.terminal(ctx)
            body=tensor(robot.data.root_lin_vel_b);yaw=tensor(robot.data.root_ang_vel_b)[:,2]
            height=tensor(robot.data.root_pos_w)[:,2]-real._mod4_ground_z
            book.observe208(ctx,tensor(robot.data.root_pos_w)[:,:2],tensor(robot.data.heading_w),
                [(ctx['command'][:,0]-body[:,0]).abs(),(ctx['command'][:,2]-yaw).abs(),(height-.25).abs()],tm.terminated,tm.time_outs,
                physics_end_tick=int(real._sim_step_counter),termination_reasons={name:tm.get_term(name).bool() for name in names})
            return result
        real.termination_manager.compute=term;obs=vec.get_observations();completed=0;last=0
        try:
            with torch.inference_mode():
                for i in range(C.CONTROL_COUNT):
                    if time.time()>=deadline:break
                    if (Path(log_dir)/'STOP_AFTER_SAVE').exists():raise RuntimeError('original E1 health observer requested integrity stop; original reason retained')
                    ctx=dict(control=i,profile_key=profile_key(torch,cmd),command=cmd.command.clone(),moving=cmd.moving.clone(),eligible=cmd.eligible_flat.clone(),
                        direction=cmd.direction.clone(),signed_yaw=cmd.signed_yaw.clone(),heading=tensor(robot.data.heading_w).clone(),before_root_xy=tensor(robot.data.root_pos_w)[:,:2].clone())
                    book.begin(cmd,ctx);panel.begin(i,ctx)
                    tick=real._integrated_contact.tick;feedback=real._feedback_100hz_tick
                    action=runner.alg.actor(obs,stochastic_output=False);panel.requested(action,obs)
                    obs,reward,done,info=vec.step(action)
                    assert real._integrated_contact.tick-tick==8 and real._feedback_100hz_tick-feedback==2
                    assert terminal_calls[0]==i+1 and obs['policy'].shape==(20000,35) and obs['critic'].shape==(20000,38)
                    assert torch.isfinite(reward).all() and torch.isfinite(obs['policy']).all() and torch.isfinite(obs['critic']).all()
                    panel.after_step(done,info);completed+=1
                    if completed==24:
                        delta={key:real._physics_action_delay.calls[key]-apply_start[key] for key in ('legs','wheels')}
                        assert delta=={'legs':192,'wheels':192} and panel.trace_controls[:24]==list(range(1,25))
                        assert int(real._integrated_contact.tick)-start_tick==192 and int(real._feedback_100hz_tick)-start_feedback==48
                        put(C.NATIVE,dict(passed=True,source_SHA=C.MODEL,controls=24,physics_callbacks=192,feedback_samples=48,policy_hz=50,nominal_force_N_each=400,Adam_step_unchanged=648360,no_optimizer_update=True))
                        put(C.QUEUE,dict(passed=True,source_SHA=C.MODEL,controls=24,physics_callbacks=192,feedback_samples=48,
                            queue_apply_calls_per_group=delta,actual_first24_trace_controls=panel.trace_controls[:24],policy_hz=50,physics_us=2500,control_us=20000,
                            original_D1_D7_fullrestore_before_mean=True,Adam648360_unchanged=True,early_origin_proven=adopted,
                            early_observer_errors=list(early.errors),no_optimizer_norm_or_extra_actor_call=True))
                        put(C.NATIVE_COMPLETE,dict(prior_native_queue_origin_files_closed=True))
                    if time.time()-last>=25:
                        put('PROFILE_PROGRESS_'+str(completed).zfill(4)+'.json',dict(epoch=time.time(),controls=completed,physical_seconds=completed*.02,
                            original_command_audit=cmd.audit_retention(),own_observed_UID_opened=book.opened_events))
                        print(json.dumps(dict(stage='ACTUAL_FROZEN_W35_UID_CYCLE800',controls=completed,physical_seconds=completed*.02)),flush=True);last=time.time()
            assert completed>0 and coverage[0]
            assert all(exact(model.state_dict(),before[key]) for key,model in [('actor',runner.alg.actor),('critic',runner.alg.critic)])
            assert exact(runner.alg.optimizer.state_dict()['state'],opt) and runner.current_learning_iteration==32336 and runner.alg.learning_rate==.00011390625000000003
            panel.finish();panel_state[0]=None
            command_report=book.finish();put('W35_OBSERVED_COMMAND_UID_AND_CYCLES_ACTUAL.json',command_report)
            diagnostic_valid=bool(adopted and not early.errors and not command_report['command_instance_JSONL']['retention_limited'] and not command_report['cycle_JSONL']['retention_limited'])
            put(C.FINAL,dict(passed_execution=True,source_SHA=C.MODEL,num_envs=20000,controls=completed,requested_controls=C.CONTROL_COUNT,
                simulated_seconds=completed*.02,warmup_controls=min(100,completed),steady_controls=max(0,completed-100),wall_time_limited=completed<C.CONTROL_COUNT,
                all17_Adam_steps=648360,stored_RSL_iteration=32336,actual_LR_unchanged=.00011390625000000003,
                core_actor_critic_STD_norm_optimizer_literal_unchanged=True,termination_and_truncation_union_exact=coverage[0],
                diagnostic_command_UID_cycle_valid=diagnostic_valid,initial_original_origin_adopted=adopted,
                command_report='W35_OBSERVED_COMMAND_UID_AND_CYCLES_ACTUAL.json',profile_report='W35_PROFILE_ENV_DOMAIN_PANEL_ACTUAL.json',
                typed_command_JSONL=command_report['command_instance_JSONL'],typed_cycle_JSONL=command_report['cycle_JSONL'],
                no_optimizer_step_no_norm_update=True,original_rough_route_timeout_unchanged=True,
                requested800_diagnostic_not_old1200_case=True,complete_WM_dataset=False,skill_graduation=False))
        finally:
            real.termination_manager.compute=oldterm;early.consumer=None
            if panel_state[0] is not None:panel_state[0].uninstall();panel_state[0]=None
            # Close new own metadata streams even on an ORIGINAL failure.
            for stream in (book.instance_records,book.cycle_records):
                if not stream.closed:stream.finish()

    rescue_training.learn=work
    try:ns['main']()
    except BaseException:
        put('FROZEN_W35_ORIGINAL_EXCEPTION_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),traceback=traceback.format_exc(),original_exception_captured_before_SDKclose=True));raise
    finally:
        try:early.finish()
        finally:put('APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()
if __name__=='__main__':
    try:main()
    except BaseException:
        if OUT and OUT.exists():put('FROZEN_W35_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_source_promotion_or_optimizer_step=True))
        raise
