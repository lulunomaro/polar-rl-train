"""Verified contact-sampling adoption, full-save handover, bounded continuation.

One20k trainer at a time. Same hardware/physics/PPO, same original deadline.
Legacy graduation gate retained. New bin statistics are not learning progress.
"""
from pathlib import Path
import os,json,time,signal,fcntl,subprocess,statistics,re,hashlib,traceback,shutil
import supervise_repair as recipe
core=recipe.core;ROOT=recipe.ROOT;DEADLINE=recipe.DEADLINE
SOURCE=Path('/home/egde/rl_candidates/MOD4_scut_speed_repair10h_20260930')
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
CODE=ROOT/'isaac/mod4';REPORTS=ROOT/'reports'
core.ENV.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1',RM_RESCUE_DEADLINE=str(DEADLINE))

def configure(enabled):
    cfg=json.loads((CODE/'env.json').read_text())
    cfg.update(RM_CONTACT_INTEGRATED=str(int(enabled)),RM_CONTACT_EAGER5MS=str(int(enabled)))
    assert cfg['RM_DR_OFF']=='1' and cfg['RM_GYRO_CURRICULUM']=='0'
    assert float(cfg['RM_CMD_VX_MAX'])==1.5
    (CODE/'env.json').write_text(json.dumps(cfg,indent=2))
    core.ENV.update({k:str(v) for k,v in cfg.items()})
    return cfg

def audit_sources():
    return {n:hashlib.sha256((CODE/n).read_bytes()).hexdigest() for n in
            ['contact_capture.py','mod4_env.py','mod4_task.py','validate_speed.py','env.json']}

def freeze_auxiliary(folder):
    """Supplement the unchanged trainer's snapshot with the new contact modules."""
    out=folder/'capture_source_freeze.json'
    if out.exists():return
    manifest=folder/'run_manifest.json'
    if not manifest.exists():raise RuntimeError('Trainer snapshot missing')
    target=folder/'src_snapshot';target.mkdir(exist_ok=True)
    hashes={}
    for n in ['contact_capture.py','contact_geometry.py','validate_speed.py']:
        source=CODE/n;hashes[n]=hashlib.sha256(source.read_bytes()).hexdigest()
        shutil.copy2(source,target/n)
    out.write_text(json.dumps({'runtime_auxiliary_sha256':hashes,
       'note':'Additional modules frozen alongside original manifest; original manifest unchanged'},indent=2))

def benchmark(ck,enabled):
    if recipe.trainers():raise RuntimeError('Trainer still active before20k benchmark')
    name='bench_integrated' if enabled else 'bench_legacy'
    log=ROOT/(name+'.log');assert not log.exists()
    env=dict(core.ENV)
    env.update({k:str(v) for k,v in json.loads((CODE/'env.json').read_text()).items()})
    env.update(RM_CONTACT_INTEGRATED=str(int(enabled)),RM_CONTACT_EAGER5MS=str(int(enabled)))
    args=[PY,'isaac/mod4/train_mod4_ppo.py','--headless','--num_envs','20000',
          '--additional_iterations','4','--steps_per_env','24','--save_interval','4',
          '--seed','20260928','--learning_rate','.0001','--init_checkpoint',str(ck),
          '--run_name',name,'--log_root',str(ROOT/'benchmark_logs')]
    with log.open('x') as f:
        p=subprocess.Popen(args,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    core.status(stage=name,validation_pid=p.pid)
    peak=0;start=time.time()
    while p.poll() is None:
        q=subprocess.run(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],capture_output=True,text=True)
        if q.returncode==0:peak=max(peak,int(q.stdout.strip().splitlines()[0]))
        if time.time()-start>1000:
            p.send_signal(signal.SIGINT);p.wait(timeout=60);raise RuntimeError('20k benchmark timeout')
        time.sleep(5)
    text=log.read_text(errors='replace')
    times=[float(x) for x in re.findall(r'Iteration time:\s*([0-9.]+)s',text)]
    paths=list((ROOT/'benchmark_logs').glob('**/model_*.pt'))
    if p.returncode or len(times)!=4 or not paths or 'Traceback' in text:
        raise RuntimeError(name+' incomplete; inspect log, no fabricated pass')
    stable=times[1:];mean=statistics.mean(stable)
    return {'mode':name,'iterations':4,'iteration_time_s':times,'stable_mean_s':mean,
            'environment_policy_steps_s':20000*24/mean,'gpu_peak_memory_MiB':peak,
            'checkpoint':core.valid_checkpoint(ck),'log':str(log)}

def handover():
    pre=json.loads((REPORTS/'preflight_status.json').read_text())
    ver=json.loads((REPORTS/'integration_verification.json').read_text())
    assert pre['stage']=='complete' and pre['ppo_pass'] and pre['statistics_pass'] and ver['pass']
    smoke=json.loads((REPORTS/'geometry_smoke.json').read_text());assert smoke['physics_pass'] and not smoke['nonfinite']
    frozen_production=json.loads(Path('/home/egde/rl_candidates/MOD4_contact_sampling_candidate_20260930/reports/pair_status.json').read_text())['source_before']
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in frozen_production.items()), 'production changed during verification'
    state=json.loads((SOURCE/'status.json').read_text());pid=state['training_pid'];folder=Path(state['log_dir'])
    if state.get('evaluation_pid') and core.active(state['evaluation_pid']):
        raise RuntimeError('Wait for source evaluation to finish before adoption')
    cmd=Path(f'/proc/{pid}/cmdline').read_bytes();cwd=Path(f'/proc/{pid}/cwd').resolve()
    assert b'train_mod4_ppo.py' in cmd and b'scut_straight_1.5m_repair' in cmd and cwd==SOURCE
    supervisors=[]
    for proc in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            if b'isaac/mod4/supervise_repair.py' in proc.read_bytes() and proc.with_name('cwd').resolve()==SOURCE:
                supervisors.append(int(proc.parent.name))
        except (OSError,FileNotFoundError):pass
    assert len(supervisors)==1,supervisors
    os.kill(supervisors[0],signal.SIGTERM)
    for _ in range(60):
        if not core.active(supervisors[0]):break
        time.sleep(1)
    if core.active(supervisors[0]):raise RuntimeError('Source supervisor did not release')
    source_lock=open(SOURCE/'supervisor.lock','a');fcntl.flock(source_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    core.STATE.update(latest_evaluation=state.get('latest_evaluation'),source_root=str(SOURCE),
                      deadline_epoch=DEADLINE,speed_limit_m_s=1.5,source_training_pid=pid)
    requested=time.time();(folder/'STOP_AFTER_SAVE').touch()
    core.status(stage='checkpoint_handover',training_pid=pid,source_log_dir=str(folder),handover_requested_epoch=requested)
    while core.active(pid):
        if time.time()-requested>1200:raise RuntimeError('Full-save handover timeout')
        time.sleep(5)
    ck=core.latest(folder);assert ck is not None and ck.stat().st_mtime>=requested
    core.valid_checkpoint(ck)
    core.status(training_pid=None,handover_checkpoint=core.valid_checkpoint(ck))
    return finish_handover(ck,source_lock,supervisors[0])

def finish_handover(ck,source_lock,source_supervisor):
    comparison=REPORTS/'benchmark_comparison.json'
    if comparison.exists():
        result=json.loads(comparison.read_text());enabled=result['deploy_integrated']
        assert result['baseline']['checkpoint']['sha256']==core.valid_checkpoint(ck)['sha256']
        for n,h in result['source_hashes'].items():
            if n!='env.json':assert hashlib.sha256((CODE/n).read_bytes()).hexdigest()==h,'cached benchmark source changed: '+n
    else:
        frozen=audit_sources();baseline=benchmark(ck,False);candidate=benchmark(ck,True)
        ratio=candidate['environment_policy_steps_s']/baseline['environment_policy_steps_s']
        enabled=ratio>=.80
        result={'baseline':baseline,'candidate':candidate,'speed_ratio':ratio,
                'minimum_ratio':.80,'deploy_integrated':enabled,'production_weight_source':str(ck),
                'benchmark_weights_discarded_from_training':True,'source_hashes':frozen}
        comparison.write_text(json.dumps(result,indent=2))
    configure(enabled)
    # Latest saved weight,15s, all constant/ramp groups, old and new statistics together.
    # This measures physics and parameters, not improvement from the changed metric.
    core.status(stage='handover_evaluation',validation_pid=None)
    out=REPORTS/'handover_frozen15s.json'
    if not out.exists():
        oldlog=out.with_suffix('.log')
        if oldlog.exists():oldlog.rename(oldlog.with_name(oldlog.stem+'_partial_'+str(int(time.time()))+'.log'))
        ep,out=recipe.evaluate(ck,1.5,'handover_frozen15s',seed=20260927)
        if ep.wait(timeout=1800)!=0 or not out.exists():raise RuntimeError('Frozen15s paired evaluation missing')
    evaluation=json.loads(out.read_text())
    assert evaluation['checkpoint']==str(ck) and evaluation['seconds']==15
    assert bool(evaluation['contact_capture_metadata'].get('integrated_enabled',False))==enabled
    if not evaluation['physics_pass'] or evaluation['nonfinite']:
        raise RuntimeError('Frozen15s physics validation failed; saved checkpoint retained')
    core.STATE['latest_evaluation']=evaluation
    receipt={'checkpoint':core.valid_checkpoint(ck),'enabled':enabled,'benchmark':result,
             'adopted_at':time.time(),'deadline_epoch':DEADLINE,'source_supervisor':source_supervisor,
             'code_sha256':audit_sources(),'primary_gate':'legacy shadow; binned pass cannot auto-promote',
             'frozen_evaluation':str(out)}
    (ROOT/'handover_completed.json').write_text(json.dumps(receipt,indent=2))
    return ck,source_lock,enabled

def main():
    lock=open(ROOT/'supervisor.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    core.STATE.update(supervisor_pid=os.getpid(),deadline_epoch=DEADLINE)
    receipt=ROOT/'handover_completed.json'
    if receipt.exists():
        d=json.loads(receipt.read_text());enabled=d['enabled'];ck=core.latest(ROOT/'logs') or Path(d['checkpoint']['path'])
        if recipe.trainers():raise RuntimeError('Refusing duplicate trainer on supervisor resume')
        source_lock=open(SOURCE/'supervisor.lock','a');fcntl.flock(source_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        configure(enabled)
    elif (ROOT/'handover_paused.json').exists():
        paused=json.loads((ROOT/'handover_paused.json').read_text())
        if recipe.trainers():raise RuntimeError('Refusing duplicate trainer during paused handover recovery')
        ck=Path(paused['checkpoint']['path']);assert core.valid_checkpoint(ck)['sha256']==paused['checkpoint']['sha256']
        assert ck.resolve().is_relative_to(SOURCE)
        source_lock=open(SOURCE/'supervisor.lock','a');fcntl.flock(source_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        core.STATE.update(handover_checkpoint=paused['checkpoint'],source_root=str(SOURCE),speed_limit_m_s=1.5)
        ck,source_lock,enabled=finish_handover(ck,source_lock,paused['source_supervisor'])
    else:ck,source_lock,enabled=handover()
    attempt=0
    while (ROOT/f'train_repair_{attempt}.log').exists():attempt+=1
    next_eval=time.time()+1800;evalproc=None;failures=0
    while time.time()<DEADLINE:
        core.STATE['evaluation_pid']=None;core.STATE['validation_pid']=None
        proc=recipe.launch_train(ck,1.5,attempt);started=time.time()
        core.status(contact_sampling_repair_enabled=enabled,contact_statistic_change_not_policy_progress=True,
                    primary_gate='strict_pass_window legacy control-endpoint shadow',
                    scope='1.5m flat continuation; no DR or automatic2m promotion')
        while proc.poll() is None:
            current=core.latest(ROOT/'logs')
            if current and current.stat().st_mtime>=started:
                freeze_auxiliary(current.parent)
                ck=current;core.STATE.update(latest_checkpoint=str(ck),iteration=core.iteration(ck),log_dir=str(ck.parent))
                if evalproc is None and time.time()>=next_eval and time.time()<DEADLINE-900:
                    evalproc,out=recipe.evaluate(ck,1.5,f'integrated_model{core.iteration(ck)}')
                    next_eval=time.time()+3600
            if evalproc is not None and evalproc.poll() is not None:
                if evalproc.returncode==0 and out.exists():
                    r=json.loads(out.read_text());core.status(latest_evaluation=r,speed_gate_passed=recipe.gate(r,1.5),
                         integrated_statistic_only=r.get('strict_pass_integrated_mean'),evaluation_error=None)
                else:core.status(evaluation_error=str(out))
                evalproc=None;core.STATE['evaluation_pid']=None
            core.status(last_health_check=time.time());time.sleep(15)
        current=core.latest(ROOT/'logs')
        if current:ck=current
        core.valid_checkpoint(ck);core.status(training_exit_code=proc.returncode)
        if time.time()>=DEADLINE or proc.returncode==0:break
        failures+=1
        if failures>1:raise RuntimeError('Repeated runtime fault; checkpoint retained')
        text=(ROOT/f'train_repair_{attempt}.log').read_text(errors='replace')
        if any(x in text.lower() for x in ['nan','out of memory','xid']):raise RuntimeError('Safety fault; inspect before resuming')
        attempt+=1
    if evalproc is not None:evalproc.wait(timeout=1800)
    core.status(stage='final_evaluation',training_pid=None,evaluation_pid=None)
    ep,out=recipe.evaluate(ck,1.5,'final_integrated_nominal',seed=20260926)
    if ep.wait(timeout=1800)!=0 or not out.exists():raise RuntimeError('Final evaluation missing')
    r=json.loads(out.read_text());core.status(stage='finished',final_checkpoint=core.valid_checkpoint(ck),
         final_evaluation=r,latest_evaluation=r,outcome='legacy_gate_pass_DR_pending' if recipe.gate(r,1.5) else 'legacy_gate_not_passed',evaluation_pid=None)

if __name__=='__main__':
    try:main()
    except BaseException:
        core.status(stage='attention_required',error=traceback.format_exc(),deadline_epoch=DEADLINE)
        raise
