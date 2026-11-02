"""Save-boundary spin warm start on the existing, uniquely authorized ledger.

One-time takeover. Restart only after real-process and active-segment reconciliation.
Stage one: 10% stand, 60% straight, 30% signed pure yaw 1--2 rad/s. No spin translation.
"""
from pathlib import Path
import json, os, re, shutil, signal, time, traceback
import supervise_mild_trial as helpers
import supervise_native_floor as base
from admission_gate import assess

ROOT=Path(__file__).resolve().parents[2];CODE=ROOT/'isaac/mod4';REPORTS=ROOT/'reports'
OLD=Path('/home/egde/rl_candidates/MOD4_mild_dr_trial_20261001')
CANONICAL=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
base.ROOT,base.CODE,base.REPORTS,base.BUDGET_PATH=ROOT,CODE,REPORTS,CANONICAL
LIVE=None
read=helpers.read;identity=helpers.identity;active=helpers.active_processes
PROBES=('/validate_speed.py','/spin_probe.py','/spin_fullscale_probe.py','/mild_fullscale_probe.py')


def runtime():
    if os.environ.get('RM_SPIN_DISABLED_FALLBACK')=='1':
        cfg=read(OLD/'isaac/mod4/env.json')
        assert cfg.get('RM_SPIN_STAGE')!='pure_yaw_v1'
        e={k:v for k,v in os.environ.items() if not k.startswith('RM_')}
        e.update({k:str(v) for k,v in cfg.items()})
        e.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1')
        return e
    cfg=read(CODE/'env.json')
    must={'RM_DR_OFF':'1','RM_CONTACT_INTEGRATED':'1','RM_CONTACT_EAGER5MS':'1',
          'RM_FLAT_NATIVE_PLANE':'1','RM_KEEP_STD':'1','RM_GYRO_CURRICULUM':'0',
          'RM_SOLVER_POS':'16','RM_SOLVER_VEL':'4','RM_SPIN_STAGE':'pure_yaw_v1',
          'RM_HEADING_CMD':'0','RM_REL_HEADING':'0','RM_MOD4_TERRAIN':'flat'}
    assert all(str(cfg.get(k))==v for k,v in must.items()),'recipe drift'
    assert float(cfg['RM_SPIN_MIN_RAD_S'])==1 and float(cfg['RM_SPIN_MAX_RAD_S'])==2
    assert float(cfg['RM_SPIN_FRACTION'])==.3 and float(cfg['RM_REL_STANDING'])==.1
    assert float(cfg['RM_CMD_VX_MIN'])==-1.5 and float(cfg['RM_CMD_VX_MAX'])==1.5
    e={k:v for k,v in os.environ.items() if not k.startswith('RM_')}
    e.update({k:str(v) for k,v in cfg.items()})
    e.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1')
    return e


base.runtime_env=runtime


def status(stage=None,**kw):
    if stage:kw['stage']=stage
    base.status(supervisor_pid=os.getpid(),canonical_budget=str(CANONICAL),profile='white_v1',
                dr_enabled=True,spin_stage='pure_yaw_v1',yaw_limit_rad_s=2.,speed_limit_m_s=1.5,
                stand_fraction=.1,spin_fraction=.3,straight_fraction=.6,**kw)


def verify_sources():
    manifest=read(REPORTS/'SPIN_SOURCE_FREEZE.json')
    for name,digest in manifest['sha256'].items():
        path=Path(name);path=path if path.is_absolute() else ROOT/path
        assert base.sha(path)==digest,'source drift '+name
    b=base.budget_state();assert b['authorized_training_seconds']==108000
    assert float(b['remaining_training_seconds'])>3600,'not enough remaining budget for safe switch'
    runtime()


def small_gate():
    status('waiting_short_physics',training_pid=None)
    out=REPORTS/'spin_small_baseline.json'
    while not out.exists():
        if Path(str(out)+'.error.txt').exists():raise RuntimeError(Path(str(out)+'.error.txt').read_text())
        started=read(REPORTS/'small_probe_started.json')
        ident=identity(started['pid'])
        assert ident and ident['state']!='Z','small probe exited without result'
        time.sleep(5)
    r=read(out)
    assert r['physical_smoke_pass'] and not r['nonfinite'],'short physical safety failed'
    assert r['initial_parameter_audit']['actual_parameters_pass'] and r['final_parameter_audit']['actual_parameters_pass']
    assert r['observations']['policy']==[18,35] and r['observations']['critic']==[18,38]
    assert r['initial_command_audit']['heading_correction'] is False
    # Wait for the process to release PhysX before taking over the production run.
    while active(PROBES):time.sleep(5)
    base.atomic_json(REPORTS/'SHORT_ACCEPTANCE.json',{'pass':True,'frozen_probe':str(out),
        'yaw_skill_already_passed':r['spin_skill_pass'],'scope':'3s physical acceptance only; new yaw skill not required',
        'budget_added':False})


def handover():
    receipt=REPORTS/'handover_completed.json'
    assert not receipt.exists(),'one-time takeover already completed; reconcile before recovery'
    s=read(OLD/'status.json');parent=identity(int(s['supervisor_pid']));trainer=identity(int(s['training_pid']))
    assert parent and trainer and parent['cwd']==str(OLD) and trainer['cwd']==str(OLD)
    assert any(a.endswith('/supervise_budget30h.py') for a in parent['argv'])
    assert any(a.endswith('/train_mod4_ppo.py') for a in trainer['argv'])
    assert base.trainers()==[trainer['pid']] and not active(PROBES)
    base.atomic_json(REPORTS/'ledger_before_handover.json',base.budget_state())
    base.atomic_json(REPORTS/'processes_before_handover.json',{'parent':parent,'trainer':trainer,'status':s})
    status('waiting_complete_save',training_pid=trainer['pid'],active_log=s['active_log'])
    os.kill(parent['pid'],signal.SIGSTOP);completed=False
    try:
        assert identity(parent['pid'])['start_ticks']==parent['start_ticks']
        assert not active(PROBES),'automatic evaluation raced takeover'
        previous=base.latest(OLD/'logs');stop=previous.parent/'STOP_AFTER_SAVE'
        assert not stop.exists(),'existing stop request needs review'
        stop.write_text('Authorized pure-yaw warm start; atomically preserve actor/critic/optimizer/std/iteration.\n')
        started=time.time()
        while True:
            current=identity(trainer['pid'])
            if current is None or current['state']=='Z':break
            assert current['start_ticks']==trainer['start_ticks'],'PID reuse'
            assert time.time()-started<1200,'save timeout; old weights retained'
            status(last_health_check=time.time());time.sleep(.5)
        ended=time.time();ck=base.latest(OLD/'logs');info=base.checkpoint(ck)
        evidence=read(ck.parent/'latest_complete.json')
        assert Path(evidence['checkpoint'])==ck and int(evidence['pid'])==trainer['pid']
        assert 'Full checkpoint saved; authorized budget or stop-file reached' in Path(s['active_log']).read_text(errors='replace')
        b=base.budget_state();segment=b['active_segment'];assert segment and segment['pid']==trainer['pid']
        tail=max(0.,ended-float(segment['accounted_through_epoch']))
        b['charged_training_seconds']=float(b['charged_training_seconds'])+tail
        b['remaining_training_seconds']=max(0.,float(b['authorized_training_seconds'])-b['charged_training_seconds'])
        segment.update(accounted_through_epoch=ended,ended_epoch=ended,
                       end_evidence='verified graceful trainer exit after full atomic save',observation_uncertainty_upper_s=.5)
        b.setdefault('completed_segments',[]).append(segment);b['active_segment']=None
        base.atomic_json(CANONICAL,b);completed=True
        os.kill(parent['pid'],signal.SIGTERM);os.kill(parent['pid'],signal.SIGCONT)
        for _ in range(100):
            item=identity(parent['pid'])
            if item is None or item['state']=='Z':break
            time.sleep(.1)
        assert not base.trainers() and not active(PROBES)
        # Same original global lock; no second ledger is created.
        helpers.acquire(CANONICAL.parent/'native_floor_supervisor.lock')
        base.update_budget(owner_root=str(ROOT))
        s.update(stage='handed_over_to_spin_preflight',supervisor_pid=None,training_pid=None,
                 handover_root=str(ROOT),latest_checkpoint=str(ck),updated_at=time.time())
        base.atomic_json(OLD/'status.json',s)
        base.atomic_json(receipt,{'source_checkpoint':info,'tail_charged_s':tail,'old_parent':parent,
            'old_trainer':trainer,'canonical_budget':str(CANONICAL),'old_weights_preserved':True,
            'charged_training_seconds':b['charged_training_seconds'],'ended_epoch':ended})
        return ck
    finally:
        if not completed:
            ident=identity(parent['pid'])
            if ident and ident['start_ticks']==parent['start_ticks']:os.kill(parent['pid'],signal.SIGCONT)


def freeze_run(folder):
    out=folder/'spin_source_freeze.json'
    if out.exists():return
    dest=folder/'spin_source_snapshot';dest.mkdir(exist_ok=True)
    files=read(REPORTS/'SPIN_SOURCE_FREEZE.json')['sha256'];evidence={}
    for name,digest in files.items():
        path=ROOT/name
        if not path.is_file():continue
        assert base.sha(path)==digest,'production source drift '+name
        target=dest/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target);evidence[name]=digest
    base.atomic_json(out,{'sha256':evidence,'budget':str(CANONICAL),'hardware_reward_ppo_unchanged':True})


def compact_spin(r):
    return {k:r.get(k) for k in ['checkpoint','seed','seconds','profile','groups','physical_smoke_pass',
        'spin_skill_pass','max_closure_m','max_mimic_rad','nonfinite','initial_command_audit']}


def probe(ck,name,kind='spin',steps=1500,num_envs=None,profile='white_v1',seed=20261002):
    global LIVE
    assert not base.trainers() and not active(PROBES)
    out=REPORTS/(name+'.json');assert not out.exists()
    script='spin_probe.py' if kind=='spin' else 'validate_speed.py'
    argv=['isaac/mod4/'+script,'--headless','--checkpoint',str(ck),'--seed',str(seed),
          '--dr-profile',profile,'--num_envs',str(num_envs or (72 if kind=='spin' else 80)),
          '--steps',str(steps),'--output',str(out)]
    if kind=='flat':argv+=['--speed_limit','1.5','--ramp_suite']
    p=base.spawn(argv,out.with_suffix('.log'));LIVE=p
    status('frozen_'+kind+'_evaluation',training_pid=None,evaluation_pid=p.pid,evaluation_path=str(out),active_log=str(out.with_suffix('.log')))
    r=base.wait_probe(p,out,timeout=1800);LIVE=None
    if kind=='spin':status(evaluation_pid=None,latest_spin_evaluation=compact_spin(r))
    else:status(evaluation_pid=None,latest_evaluation=r,experimental_admission=assess(r))
    return r


def training(ck,phase,duration=None,count=20000,spin=True):
    global LIVE
    assert not base.trainers() and not active(PROBES) and not base.budget_state().get('active_segment')
    b=base.budget_state();remaining=float(b['authorized_training_seconds'])-float(b['charged_training_seconds'])
    assert remaining>120
    began=time.time();deadline=began+min(remaining,duration or remaining)
    base.update_budget(owner_root=str(ROOT),deadline_epoch=began+remaining)
    logroot=ROOT/('preflight_logs' if count==128 else 'logs' if spin else 'fallback_logs')
    index=0
    while (ROOT/f'train_spin_{phase}_{index}.log').exists():index+=1
    log=ROOT/f'train_spin_{phase}_{index}.log'
    # Fallback is the ORIGINAL command recipe in a separate preserved config file.
    if not spin:os.environ['RM_SPIN_DISABLED_FALLBACK']='1'
    train_script='isaac/mod4/train_mod4_ppo.py' if spin else str(OLD/'isaac/mod4/train_mod4_ppo.py')
    p=base.spawn([train_script,'--headless','--num_envs',str(count),
        '--additional_iterations','2' if count==128 else '100000','--steps_per_env','24',
        '--save_interval','2' if count==128 else '25','--learning_rate','.0001','--seed','20260928',
        '--run_name','scut_spin_'+phase,'--log_root',str(logroot),'--init_checkpoint',str(ck)],log,deadline)
    os.environ.pop('RM_SPIN_DISABLED_FALLBACK',None)
    LIVE=p;base.start_segment(p,phase,log)
    status('ppo_preflight' if count==128 else 'training',training_pid=p.pid,num_envs=count,steps_per_env=24,
        active_log=str(log),resume_checkpoint=base.checkpoint(ck),deadline_epoch=began+remaining,
        trainer_deadline_epoch=deadline,production_started_epoch=began,training_phase=phase,
        budget_seconds=b['authorized_training_seconds'],authorized_training_seconds=b['authorized_training_seconds'],
        scope='Pure signed yaw 1--2 rad/s plus retained standing/straight; directional spin translation and terrain remain later stages')
    while p.poll() is None:
        base.account_segment();current=base.latest(logroot)
        if current:
            if spin:freeze_run(current.parent)
            status(latest_checkpoint=str(current),iteration=int(current.stem.rsplit('_',1)[1]),log_dir=str(current.parent))
        status(last_health_check=time.time());time.sleep(1 if count==128 else 5)
    base.account_segment(finish=True);LIVE=None;status(training_pid=None,training_exit_code=p.returncode)
    text=log.read_text(errors='replace');assert p.returncode==0 and 'Traceback (most recent call last)' not in text,'trainer fault; preserve ledger and checkpoints'
    current=base.latest(logroot);assert current
    info=base.checkpoint(current);manifest=read(current.parent/'run_manifest.json')
    assert manifest['start_iteration']==base.checkpoint(ck)['iteration_stored'] and manifest['env']['RM_KEEP_STD']=='1'
    assert manifest['env']['RM_MILD_DR_PROFILE']=='white_v1'
    if count==128:
        times=[float(v) for v in re.findall(r'Iteration time:\s*([0-9.]+)s',text)]
        assert len(times)==2
        base.atomic_json(REPORTS/'PPO_PREFLIGHT_128.json',{'pass':True,'discarded_weights':info,
            'production_source':str(ck),'charged_same_ledger':True,'iteration_time_s':times})
    return current


def fallback(source,reason):
    """Resume the preserved ORIGINAL straight task, not a blind repeat of takeover."""
    assert not base.trainers() and not base.budget_state().get('active_segment')
    base.atomic_json(REPORTS/'NOMINAL_RECIPE_FALLBACK.json',{'reason':reason,
        'source_checkpoint':base.checkpoint(source),'same_budget':str(CANONICAL),
        'original_script':str(OLD/'isaac/mod4/train_mod4_ppo.py'),'new_spin_weights_preserved':True})
    final=training(source,'straight_safe_fallback',spin=False)
    os.environ['RM_SPIN_DISABLED_FALLBACK']='1'
    try:
        # The absolute old validator imports the preserved original command code.
        out=REPORTS/'final_straight_fallback.json'
        p=base.spawn([str(OLD/'isaac/mod4/validate_speed.py'),'--headless','--checkpoint',str(final),
            '--speed_limit','1.5','--ramp_suite','--seed','20260927','--num_envs','80','--steps','1500',
            '--dr-profile','white_v1','--output',str(out)],out.with_suffix('.log'))
        r=base.wait_probe(p,out)
    finally:os.environ.pop('RM_SPIN_DISABLED_FALLBACK',None)
    status('finished_straight_fallback',training_pid=None,final_checkpoint=base.checkpoint(final),
           final_evaluation=assess(r),outcome=reason+'; original straight recipe restored within the same remaining budget')


def fullscale(ck):
    global LIVE
    assert not base.trainers() and not active(PROBES)
    out=REPORTS/'spin_fullscale_20k.json'
    p=base.spawn(['isaac/mod4/spin_fullscale_probe.py','--headless','--checkpoint',str(ck),
        '--num_envs','20000','--steps','120','--output',str(out)],out.with_suffix('.log'));LIVE=p
    status('spin_20k_physics',training_pid=None,validation_pid=p.pid,active_log=str(out.with_suffix('.log')))
    r=base.wait_probe(p,out);LIVE=None
    passed,acceptance=base.accept_physics_smoke(r)
    assert passed and r['mild_initial_parameters']['actual_parameters_pass'] and r['mild_final_parameters']['actual_parameters_pass']
    assert r['initial_command_audit']['spin_fraction_actual']>.2 and r['initial_command_audit']['spin_fraction_actual']<.4
    assert r['initial_command_audit']['spin_positive_fraction']>.1 and r['initial_command_audit']['spin_negative_fraction']>.1
    assert r['initial_command_audit']['spin_command_body_translation_max']==0
    base.atomic_json(REPORTS/'FULLSCALE_ACCEPTANCE.json',acceptance);status(validation_pid=None,physics_preflight_acceptance=acceptance)


def decision(ck,prefix):
    # Learning new yaw is gradual: retain improvements if physics and old running
    # are safe. Skill pass is displayed, never required before a first PPO update.
    flat=probe(ck,prefix+'_flat','flat',seed=20260927)
    spin=probe(ck,prefix+'_spin','spin',seed=20261002)
    allowed=assess(flat)['eligible_for_mild_dr_trial'] and spin['physical_smoke_pass']
    evidence={'continue_spin':allowed,'flat_regression':assess(flat),
        'spin_physical_smoke_pass':spin['physical_smoke_pass'],'spin_15s_skill_pass':spin['spin_skill_pass'],
        'criterion':'Retain physical safety and mature straight policy; yaw-skill learning may be incomplete',
        'checkpoint':base.checkpoint(ck),'budget_added':False}
    base.atomic_json(REPORTS/(prefix+'_decision.json'),evidence)
    return allowed


def main():
    REPORTS.mkdir(exist_ok=True);helpers.acquire(ROOT/'spin_supervisor.lock')
    assert not (REPORTS/'spin_production_started.json').exists(),'recovery requires process/ledger reconciliation first'
    verify_sources();small_gate();source=handover()
    try:
        fullscale(source)
        training(source,'preflight',count=128)
        baseline=probe(source,'handover_flat15s','flat',seed=20260927)
        assert assess(baseline)['eligible_for_mild_dr_trial'],'straight regression before spin start'
    except Exception:
        reason=traceback.format_exc()
        base.atomic_json(REPORTS/'preflight_failure.json',{'error':reason,'preserved_checkpoint':str(source)})
        if base.trainers() or base.budget_state().get('active_segment'):raise
        fallback(source,'Spin preflight failed: '+reason)
        return
    base.atomic_json(REPORTS/'spin_production_started.json',{'checkpoint':base.checkpoint(source),
        'started_epoch':time.time(),'canonical_budget':str(CANONICAL),'discard_preflight_weights':True,
        'fractions':{'stand':.1,'straight':.6,'pure_spin':.3},'yaw_rad_s':[1.,2.]})
    chosen=training(source,'trial_45min',duration=2700)
    allowed=decision(chosen,'trial45')
    if not allowed:
        fallback(source,'Spin trial physical or retained straight regression failed; spin weights retained')
        return
    # Continue in bounded blocks with sequential frozen flat/spin checks. While
    # no trainer is active, frozen evaluation time is excluded from the same budget.
    while base.budget_state()['remaining_training_seconds']>120:
        remaining=base.budget_state()['remaining_training_seconds']
        chosen=training(chosen,'continued_spin',duration=min(7200,remaining))
        if base.budget_state()['remaining_training_seconds']<=120:break
        if not decision(chosen,'block_model'+str(base.checkpoint(chosen)['iteration_stored'])):
            fallback(source,'Later spin physical or retained straight regression; full spin weights retained')
            return
    final_flat=probe(chosen,'final_flat','flat',seed=20261002)
    final_spin=probe(chosen,'final_spin','spin',seed=20261002)
    final_spin_nom=probe(chosen,'final_spin_nominal','spin',profile='nominal',seed=20261002)
    status('finished',training_pid=None,evaluation_pid=None,final_checkpoint=base.checkpoint(chosen),
        final_evaluation={'flat':assess(final_flat),'spin_mild':compact_spin(final_spin),'spin_nominal':compact_spin(final_spin_nom)},
        outcome='Original effective budget finished; spin tracking reported explicitly; directional translation, terrain/high yaw require subsequent acceptance')


if __name__=='__main__':
    try:main()
    except BaseException:
        status('attention_required',error=traceback.format_exc(),child_pid=LIVE.pid if LIVE and LIVE.poll() is None else None,
            instructions='Inspect actual processes and canonical active segment. Never rerun one-time takeover or reset charged time.')
        raise
