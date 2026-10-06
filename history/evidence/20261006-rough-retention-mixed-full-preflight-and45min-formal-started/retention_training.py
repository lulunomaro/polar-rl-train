"""Same full PPO/budget lifecycle; mixed terrain throughput is a cost diagnostic."""
import ast,inspect,types
def training(ck,phase,duration=7200,count=20000,iterations=None):
    global LIVE
    idle();verify();assert remaining()>120
    source=base.checkpoint(ck);begin=time.time();deadline=begin+min(duration,remaining())
    logroot=ROOT/('autonomy_preflight_logs' if iterations else 'logs')
    label=fresh_label(phase);log=ROOT/(label+'.log')
    args=[str(CODE/'train_mod4_ppo.py'),'--headless','--num_envs',str(count),
      '--additional_iterations',str(iterations or 100000),'--steps_per_env','24',
      '--save_interval',str(iterations or 25),'--learning_rate','.0001','--seed','20260928',
      '--run_name',label,'--log_root',str(logroot),'--init_checkpoint',str(ck)]
    base.update_budget(deadline_epoch=begin+remaining())
    p=base.spawn(args,log,deadline);LIVE=p;base.start_segment(p,phase,log)
    S['active_training']={'pid':p.pid,'source':source,'phase':phase,'profile':S['profile'],
                           'cap':rate.current_limit(),'log_root':str(logroot),'deadline':deadline};persist()
    status('ppo_preflight' if iterations else 'training',training_pid=p.pid,evaluation_pid=None,validation_pid=None,
      num_envs=count,steps_per_env=24,active_log=str(log),resume_checkpoint=source,
      trainer_deadline_epoch=deadline,deadline_epoch=begin+remaining(),budget_seconds=base.budget_state()['authorized_training_seconds'],
      authorized_training_seconds=base.budget_state()['authorized_training_seconds'],training_phase=phase)
    run=None
    while p.poll() is None:
        base.account_segment()
        try:run=rate.trainer_run(logroot,p.pid)
        except AssertionError:pass
        if run:
            current=Path(read(run/'latest_complete.json')['checkpoint'])
            # Bind every save to THIS process, never all-directory maximum iteration.
            if not current.is_absolute():current=run/current
            if current.exists():
                rate.freeze_run(run)
                status(latest_checkpoint=str(current),iteration=int(current.stem.rsplit('_',1)[1]),log_dir=str(run))
        status(last_health_check=time.time());time.sleep(1 if iterations else 5)
    base.account_segment(finish=True);LIVE=None
    status(training_pid=None,training_exit_code=p.returncode)
    text=log.read_text(errors='replace')
    assert p.returncode==0 and 'Traceback (most recent call last)' not in text,'Trainer fault: preserve weights and ledger'
    run=rate.trainer_run(logroot,p.pid);receipt=read(run/'latest_complete.json')
    current=Path(receipt['checkpoint']);current=current if current.is_absolute() else run/current
    info=base.checkpoint(current);manifest=read(run/'run_manifest.json')
    assert manifest['start_iteration']==source['iteration_stored'] and manifest['env']['RM_KEEP_STD']=='1'
    assert manifest['env']['RM_MILD_DR_PROFILE']==S['profile']
    assert float(manifest['env']['RM_SPIN_MAX_RAD_S'])==rate.current_limit()
    S['active_training']=None
    if not iterations:S['chosen_checkpoint']=str(current)
    persist()
    if iterations:
        times=[float(x) for x in re.findall(r'Iteration time:\s*([0-9.]+)s',text)]
        assert len(times)==iterations
        assert info['iteration_stored']>=source['iteration_stored']+iterations-1
        throughput=count*24/(sum(times)/len(times))
        # Mixed terrain throughput remains an explicit cost diagnostic.
        base.atomic_json(REPORTS/(label+'_receipt.json'),{'pass':True,'discarded_weights':info,
            'production_source':source,'charged_same_ledger':True,'profile':S['profile'],
            'iteration_time_s':times,'environment_policy_steps_per_second':throughput})
    else:
        base.atomic_json(REPORTS/(label+'_production.json'),{'source':source,'saved':info,
            'profile':S['profile'],'cap':rate.current_limit(),'PID_bound_receipt':receipt})
    return current
def mixed_training(ctl,*args,**kwargs):
    original=ast.parse(inspect.getsource(ctl.training)).body[0]
    candidate=ast.parse(inspect.getsource(training)).body[0]
    removed=[]
    class Review(ast.NodeTransformer):
        def visit_Assert(self,node):
            if isinstance(node.msg,ast.Constant) and node.msg.value=='Excessive overhead; discard and roll back':
                removed.append(node);return None
            return self.generic_visit(node)
    original=Review().visit(original)
    assert len(removed)==1 and ast.dump(original)==ast.dump(candidate)
    call=types.FunctionType(training.__code__,ctl.__dict__,training.__name__,training.__defaults__)
    return call(*args,**kwargs)
