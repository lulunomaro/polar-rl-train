"""Detached MOD4 overnight controller. No new budget or untested bundled DR.

Resume requires a settled ledger and no live children. Sources and receipt-bound
checkpoints are checked before every stage; a crash never implies permission to
duplicate a trainer or repeat a one-shot handover.
"""
from pathlib import Path
import argparse, json, os, re, signal, subprocess, sys, time, traceback
import supervise_spin_rate as rate
from autonomy_policy import DR_PROFILES, LEVELS, next_action, settle_segment, safety_veto

base, spin, helpers = rate.base, rate.spin, rate.helpers
ROOT, CODE, REPORTS, CANONICAL = rate.ROOT, rate.CODE, rate.REPORTS, rate.CANONICAL
STATE_PATH=REPORTS/'AUTONOMY_STATE.json'
RECEIPT=REPORTS/'AUTONOMY_HANDOVER.json'
TURN=Path('/home/egde/rl_candidates/MOD4_fps_turn_candidate_20261003')
PROBES=rate.PROBES+('/autonomy_turn_probe.py',)
spin.PROBES=PROBES
LIVE=None
S={}

def read(p): return helpers.read(p)
def persist(): base.atomic_json(STATE_PATH,S)
def fresh_label(kind):
    S['sequence']=S.get('sequence',0)+1; persist()
    return f"auto_{S['sequence']:04d}_{kind}_cap{rate.current_limit():g}_{S['profile']}"
def identity(pid): return helpers.identity(pid)
def same(identity_before):
    now=identity(identity_before['pid'])
    return now and now['start_ticks']==identity_before['start_ticks'] and now['cwd']==identity_before['cwd']
def alive(pid):
    p=identity(pid)
    return p and p['state']!='Z'
def idle():
    assert not base.trainers() and not helpers.active_processes(PROBES), 'Do not duplicate active work'
    assert not base.budget_state().get('active_segment'), 'Reconcile active budget first'
def remaining(): return float(base.budget_state()['remaining_training_seconds'])

def runtime():
    cfg=read(CODE/'env.json')
    required={'RM_SPIN_STAGE':'pure_yaw_v1','RM_FLAT_NATIVE_PLANE':'1','RM_CONTACT_INTEGRATED':'1',
      'RM_CONTACT_EAGER5MS':'1','RM_KEEP_STD':'1','RM_DR_OFF':'1','RM_GYRO_CURRICULUM':'0',
      'RM_HEADING_CMD':'0','RM_REL_HEADING':'0','RM_SOLVER_POS':'16','RM_SOLVER_VEL':'4','RM_MOD4_TERRAIN':'flat'}
    assert all(str(cfg.get(k))==v for k,v in required.items()),'Recipe drift'
    assert cfg['RM_MILD_DR_PROFILE'] in DR_PROFILES
    assert float(cfg['RM_SPIN_MIN_RAD_S'])==1 and float(cfg['RM_SPIN_FRACTION'])==.3
    assert float(cfg['RM_REL_STANDING'])==.1 and float(cfg['RM_NOMINAL_HEIGHT'])==.25
    assert float(cfg['RM_CMD_VX_MIN'])==-1.5 and float(cfg['RM_CMD_VX_MAX'])==1.5
    rate.current_limit()
    env={k:v for k,v in os.environ.items() if not k.startswith('RM_')}
    env.update({k:str(v) for k,v in cfg.items()})
    env.update(ISAACSIM_ACCEPT_EULA='Y',OMNI_KIT_ACCEPT_EULA='YES',PYTHONUNBUFFERED='1')
    return env

def status(stage=None,**kw):
    kw.pop('scope',None)
    total = base.budget_state()['authorized_training_seconds']
    kw.update(budget_seconds=total, authorized_training_seconds=total)
    base.status(supervisor_pid=os.getpid(),canonical_budget=str(CANONICAL),
        profile=S.get('profile','white_v1'),dr_enabled=True,yaw_limit_rad_s=rate.current_limit(),
        target_yaw_rad_s=4*__import__('math').pi,target_chassis_rev_s=2.,speed_limit_m_s=1.5,
        spin_stage='pure_yaw_rate_v1',stand_fraction=.1,spin_fraction=.3,straight_fraction=.6,
        autonomy_version='sleep_v4_intermediate5_bounded',autonomy_state_path=str(STATE_PATH),
        scope='Separate gated rate/DR changes; BODY arcs are frozen regression; world spin translation/terrain not deployed',
        **({'stage':stage} if stage else {}),**kw)

base.runtime_env=runtime
spin.runtime=runtime
spin.status=status

def verify():
    budget = base.budget_state()  # Validates original authorization and every explicit extension.
    assert budget['owner_root']==str(ROOT)
    runtime()
    for key,digest in read(REPORTS/'SPIN_SOURCE_FREEZE.json')['sha256'].items():
        p=Path(key);p=p if p.is_absolute() else ROOT/p
        assert base.sha(p)==digest,'Source drift: '+key

def set_profile(profile,reason):
    idle();assert profile in DR_PROFILES
    cfg=read(CODE/'env.json');previous=cfg['RM_MILD_DR_PROFILE']
    cfg['RM_MILD_DR_PROFILE']=profile;base.atomic_json(CODE/'env.json',cfg)
    manifest=read(REPORTS/'SPIN_SOURCE_FREEZE.json')
    manifest['sha256']['isaac/mod4/env.json']=base.sha(CODE/'env.json')
    base.atomic_json(REPORTS/'SPIN_SOURCE_FREEZE.json',manifest)
    S['profile']=profile;persist()
    base.atomic_json(REPORTS/(fresh_label('profile_change')+'.json'),
        {'old':previous,'new':profile,'reason':reason,'fixed_yaw_limit':rate.current_limit(),
         'registered_ranges':DR_PROFILES[profile],'budget_added':False,
         'PD_spring_COM_sensor_delay_reward_PPO_unchanged':True})

def probe(ck,label,kind='spin',profile=None,seed=20261002,steps=1500):
    global LIVE
    idle();verify();profile=profile or S['profile']
    out=REPORTS/(label+'.json');assert not out.exists(),'Never overwrite an experiment'
    script=CODE/('spin_rate_probe.py' if kind=='spin' else 'validate_speed.py')
    count=22 if kind=='spin' and steps<1500 else 88 if kind=='spin' else 80
    if kind=='turn':
        script=TURN/'isaac/mod4/autonomy_turn_probe.py';count=96
        cfg=read(TURN/'isaac/mod4/env.json')
        cfg['RM_SPIN_MAX_RAD_S']=str(rate.current_limit());cfg['RM_MILD_DR_PROFILE']=S['profile']
        base.atomic_json(TURN/'isaac/mod4/env.json',cfg)
    args=[str(script),'--headless','--checkpoint',str(ck),'--seed',str(seed),
          '--dr-profile',profile,'--num_envs',str(count),'--steps',str(steps),'--output',str(out)]
    args += ['--speed_limit','1.5','--ramp_suite'] if kind=='flat' else ['--max-rate',str(rate.current_limit())]
    p=base.spawn(args,out.with_suffix('.log'));LIVE=p
    status('frozen_'+kind+'_evaluation',training_pid=None,evaluation_pid=p.pid,active_log=str(out.with_suffix('.log')),evaluation_path=str(out))
    r=base.wait_probe(p,out);LIVE=None
    status(evaluation_pid=None,**({'latest_spin_evaluation':spin.compact_spin(r)} if kind=='spin' else {'latest_evaluation':r,'experimental_admission':rate.assess(r)} if kind=='flat' else {'latest_turn_report':str(out)}))
    return r

def gate(r,kind):
    original=rate.assess(r)['eligible_for_mild_dr_trial'] if kind=='flat' else r['turn_skill_pass'] if kind=='turn' else r['spin_skill_pass']
    return original and safety_veto(r)

def pairs(ck,label,profiles,seeds=(20261002,20261003),kinds=('flat','spin')):
    result=[];passed=True
    for seed in seeds:
        for kind in kinds:
            reports=[]
            for profile in profiles:
                reports.append(probe(ck,f'{label}_{kind}_{profile}_{seed}',kind,profile,seed))
            exact=all(all(r[k]==reports[0][k] for k in ('reset_joint_pos_before_physics','reset_root_before_physics')) for r in reports)
            gates=[gate(r,kind) for r in reports]
            audits=[]
            for profile,r in zip(profiles,reports):
                initial=r.get('initial_parameter_audit') or r.get('mild_initial_parameters')
                final=r.get('final_parameter_audit') or r.get('mild_final_parameters')
                # Flat nominal audit is not included by its original validator.
                clean=profile=='nominal' and initial is None and final is None
                audits.append(clean or bool(initial and final and initial['actual_parameters_pass'] and final['actual_parameters_pass']))
            passed &= exact and all(gates) and all(audits)
            result.append({'seed':seed,'kind':kind,'profiles':list(profiles),'initial_root_q_exact':exact,
                'original_plus_individual_safety_gates':gates,'actual_parameter_readbacks':audits})
    receipt={'pass':bool(passed),'pairs':result,'checkpoint':base.checkpoint(ck),'fixed_cap':rate.current_limit(),
             'profiles':list(profiles),'real_robot_certified':False}
    base.atomic_json(REPORTS/(label+'_paired_decision.json'),receipt)
    return passed

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
        assert count!=20000 or throughput>=23000,'Excessive overhead; discard and roll back'
        base.atomic_json(REPORTS/(label+'_receipt.json'),{'pass':True,'discarded_weights':info,
            'production_source':source,'charged_same_ledger':True,'profile':S['profile'],
            'iteration_time_s':times,'environment_policy_steps_per_second':throughput})
    else:
        base.atomic_json(REPORTS/(label+'_production.json'),{'source':source,'saved':info,
            'profile':S['profile'],'cap':rate.current_limit(),'PID_bound_receipt':receipt})
    return current

def fullscale(ck,label):
    global LIVE
    idle();verify();out=REPORTS/(label+'_20k.json')
    p=base.spawn([str(CODE/'spin_rate_fullscale_probe.py'),'--headless','--checkpoint',str(ck),
       '--num_envs','20000','--steps','120','--max-rate',str(rate.current_limit()),'--output',str(out)],out.with_suffix('.log'))
    LIVE=p;status('fullscale_physics_preflight',validation_pid=p.pid,training_pid=None,active_log=str(out.with_suffix('.log')))
    r=base.wait_probe(p,out);LIVE=None
    passed,a=base.accept_physics_smoke(r)
    base.atomic_json(REPORTS/(label+'_20k_acceptance.json'),a)
    status(validation_pid=None,physics_preflight_acceptance=a)
    assert passed and r['mild_initial_parameters']['actual_parameters_pass'] and r['mild_final_parameters']['actual_parameters_pass']
    return r

def current_decision(ck):
    label=fresh_label('assessment')
    flat=probe(ck,label+'_flat',kind='flat',seed=20260927)
    yaw=probe(ck,label+'_rate')
    physical=gate(flat,'flat') and yaw['physical_smoke_pass'] and safety_veto(yaw)
    skilled=physical and yaw['spin_skill_pass']
    result={'continue_current_rate':physical,'current_rate_skill_pass':skilled,
        'original_rate_skill_pass':yaw['spin_skill_pass'],'original_flat_admission':rate.assess(flat),
        'checkpoint':base.checkpoint(ck),'cap':rate.current_limit(),'profile':S['profile'],
        'flat_seed':20260927,'rate_seed':20261002,'different_protocols_not_a_paired_experiment':True}
    base.atomic_json(REPORTS/(label+'_decision.json'),result);status(latest_rate_decision=result)
    return physical,skilled

def turn_review(ck):
    label=fresh_label('ordinary_turn')
    passed=pairs(ck,label,('nominal',S['profile']),seeds=(20261003,20261004),kinds=('turn',))
    S['turn_review']={'pass':passed,'checkpoint':str(ck),'cap':rate.current_limit(),'profile':S['profile']};persist()
    # No extra training if existing generalization passes; no mixed new course if it fails.
    return passed

def dr_trial(ck,target):
    previous=S['profile'];label=fresh_label('dr_candidate_'+target)
    # Parameter readbacks and nominal/current/wider pairs precede ANY wider PPO.
    if not pairs(ck,label,('nominal',previous,target)):
        S['dr_rejected'].append(target);persist();return ck
    set_profile(target,'Frozen current/nominal/wider two-seed checks passed; yaw held fixed')
    try:
        fullscale(ck,label)
        training(ck,'dr128_preflight',count=128,iterations=2,duration=600)
        training(ck,'dr20k_preflight',count=20000,iterations=4,duration=900)
        # Both preflight policies discarded. Full state starts at original production source.
        S['rollback']={'checkpoint':str(ck),'profile':previous,'cap':rate.current_limit()};persist()
        trial=training(ck,'dr45_trial',duration=2700)
        if not pairs(trial,fresh_label('dr_trial_review'),('nominal',target)):
            raise ValueError('DR trial failed real behavior or retained-skill regression')
    except BaseException:
        if base.trainers() or base.budget_state().get('active_segment'):raise
        error=traceback.format_exc()
        set_profile(previous,'Reject stronger DR; preserve all candidate weights and restore pre-trial full state')
        S['dr_rejected'].append(target);S['chosen_checkpoint']=str(ck);S['rollback']=None;persist()
        base.atomic_json(REPORTS/(label+'_REJECTED.json'),{'error':error,'restored':base.checkpoint(ck),'profile':previous})
        return ck
    S['chosen_checkpoint']=str(trial);S['rollback']=None;S['consecutive']=0;persist()
    base.atomic_json(REPORTS/(label+'_ACCEPTED.json'),{'checkpoint':base.checkpoint(trial),'profile':target,
       'cap_unchanged':rate.current_limit(),'real_robot_certified':False,'budget_added':False})
    return trial

def rate_preflight(ck,target):
    previous=rate.current_limit();label=fresh_label('rate_candidate')
    idle();rate.set_limit(target,'Two independent current-cap checkpoints plus nominal/active-DR multiseed passed')
    try:
        r=probe(ck,label+'_short',steps=300)
        assert r['physical_smoke_pass'] and not r['nonfinite']
        fullscale(ck,label);training(ck,'rate128_preflight',count=128,iterations=2,duration=600)
    except BaseException:
        if base.trainers() or base.budget_state().get('active_segment'):raise
        error=traceback.format_exc();rate.set_limit(previous,'Rejected new yaw physical/PPO preflight; no hardware changes')
        S['rate_rejected'].append(target);persist()
        base.atomic_json(REPORTS/(label+'_REJECTED.json'),{'error':error,'checkpoint':base.checkpoint(ck),'restored_cap':previous})
    S['consecutive']=0;persist()

def finish(ck,outcome):
    idle();label=fresh_label('final')
    flat=probe(ck,label+'_flat','flat')
    yaw=probe(ck,label+'_rate')
    nominal=probe(ck,label+'_rate_nominal',profile='nominal')
    receipt={'checkpoint':base.checkpoint(ck),'profile':S['profile'],'cap':rate.current_limit(),
       'flat':rate.assess(flat),'spin_active_DR':spin.compact_spin(yaw),'spin_nominal':spin.compact_spin(nominal),
       'outcome':outcome,'actual_budget':base.budget_state(),'target_not_assumed_achieved':True,
       'world_spin_translation_terrain_cloud_MoE_not_deployed':True}
    base.atomic_json(REPORTS/'AUTONOMY_FINISHED.json',receipt)
    status('finished',training_pid=None,evaluation_pid=None,validation_pid=None,final_checkpoint=base.checkpoint(ck),
           final_evaluation=receipt,outcome=outcome)

def targeted_hold(ck,target,reason):
    idle();S['chosen_checkpoint']=str(ck);persist()
    info=base.checkpoint(ck)
    evidence={'checkpoint':info,'cap':rate.current_limit(),'profile':S['profile'],'blocked_next_cap':target,
        'reason':reason,'rate_rejected_retained':S['rate_rejected'],'effective_budget_not_extended':True,
        'resume_requires_isolated_repair_evidence':True}
    base.atomic_json(REPORTS/(fresh_label('targeted_repair_hold')+'.json'),evidence)
    status('targeted_repair_hold',training_pid=None,evaluation_pid=None,validation_pid=None,
        latest_checkpoint=str(ck),targeted_repair=evidence,instructions='Mature policy preserved. No repeated mature-cap PPO while rejected next-cap repair is pending.')


def intermediate5_bootstrap(ck):
    pending=S['pending_intermediate5']
    assert pending['id']=='INTERMEDIATE5_FROM_MATURE4_20261003' and pending['phase']=='prepared','Inspect an interrupted targeted trial before resuming; never repeat its preflights'
    assert rate.current_limit()==4. and S['profile']=='white_v2' and 6. in S['rate_rejected']
    assert base.checkpoint(ck)['sha256']==pending['source_sha256']
    label=fresh_label('intermediate5_entry')
    pending['phase']='checking_latest_source';persist()
    # Latest saved source must retain the original cap4 skills before changing commands.
    physical,skilled=current_decision(ck)
    if not physical or not skilled:
        S['pending_intermediate5']=None;S['rate_rejected']=list(set(S['rate_rejected']+[5.]));persist()
        targeted_hold(ck,5.,'Latest source did not pass its cap4 baseline; do not begin new-course PPO')
        return None
    pending['phase']='preflighting5';persist()
    rate_preflight(ck,5.)
    if rate.current_limit()!=5.:
        S['pending_intermediate5']=None;persist()
        targeted_hold(ck,5.,'Intermediate5 physical/PPO preflight rejected; all weights retained')
        return None
    pending['phase']='trial45';S['rollback']={'checkpoint':str(ck),'profile':'white_v2','cap':4.};persist()
    # Preflight weights were discarded by rate_preflight. This restores the exact formal full state.
    trial=training(ck,'intermediate5_trial45',duration=2700)
    S['pending_intermediate5']=None;S['consecutive']=0;S['failed_blocks']=0;persist()
    base.atomic_json(REPORTS/(label+'_TRIAL_STARTED_AND_SAVED.json'),{'source':base.checkpoint(ck),'trial':base.checkpoint(trial),
        'target_cap':5.,'profile_unchanged':'white_v2','preflight_weights_discarded':True,'reward_physics_PPO_hardware_unchanged':True,
        'stage':'45min_saved_pending_original15s_assessment','not_skill_accepted':True})
    return trial


def controller():
    global S
    S=read(STATE_PATH);idle();verify()
    helpers.acquire(ROOT/'autonomy_controller.lock')
    helpers.acquire(CANONICAL.parent/'native_floor_supervisor.lock')
    ck=Path(S['chosen_checkpoint']);base.checkpoint(ck)
    if S.get('pending_intermediate5'):
        ck=intermediate5_bootstrap(ck)
        if ck is None:return
    while remaining()>120:
        physical,skilled=current_decision(ck)
        info=base.checkpoint(ck)
        if not physical:
            # Roll back to last actually certified cap/profile, never global highest iteration.
            m=S['mature'];idle();rate.set_limit(m['cap'],'Real regression; restore measured mature configuration')
            set_profile(m['profile'],'Real regression; restore last paired mature complete policy')
            ck=Path(m['checkpoint']);S['chosen_checkpoint']=str(ck)
            S['consecutive']=0;S['rate_rejected']=list(LEVELS[LEVELS.index(m['cap'])+1:]);persist()
            base.atomic_json(REPORTS/(fresh_label('REGRESSION_ROLLBACK')+'.json'),{'failed':info,'restored':m})
        else:
            different=S.get('last_assessed_sha')!=info['sha256']
            S['consecutive']=(S.get('consecutive',0)+1 if different else S.get('consecutive',0)) if skilled else 0
            S['failed_blocks']=0 if skilled else S.get('failed_blocks',0)+1
            S['last_assessed_sha']=info['sha256'];persist()
            paired=False
            if S['consecutive']>=2 and remaining()>5400:
                paired=pairs(ck,fresh_label('mature_multiseed'),('nominal',S['profile']))
                if paired:
                    S['mature']={'checkpoint':str(ck),'cap':rate.current_limit(),'profile':S['profile']};persist()
                    if rate.current_limit()>=6 and (not S.get('turn_review') or S['turn_review']['cap']!=rate.current_limit()):
                        turn_review(ck)
                action,target=next_action(rate.current_limit(),S['profile'],S['consecutive'],paired,remaining(),S['dr_rejected'],S['rate_rejected'])
                if action=='targeted_repair_hold':
                    targeted_hold(ck,target,'Next rate has a retained rejection; do not spend more budget repeating mature cap')
                    return
                if action=='dr_trial':
                    ck=dr_trial(ck,target);S['consecutive']=0;persist()
                elif action=='rate_preflight' and target not in S['rate_rejected']:
                    rate_preflight(ck,target)
        if remaining()<=120:break
        # Avoid spending the entire remaining budget on a repeatedly failed new cap.
        if S.get('failed_blocks',0)>=3 and rate.current_limit()>S['mature']['cap']:
            failed_cap=rate.current_limit()
            m=S['mature'];rate.set_limit(m['cap'],'Three failed skill blocks; preserve new policy, return to certified cap')
            set_profile(m['profile'],'Use certified source for bounded robustness work, not unverified rate escalation')
            ck=Path(m['checkpoint']);S['chosen_checkpoint']=str(ck);S['consecutive']=0;S['failed_blocks']=0
            S['rate_rejected'].append(failed_cap);persist()
            # The mature 4rad/s policy may receive a wider DR trial independently.
            if S['profile']=='white_v1' and 'white_v2' not in S['dr_rejected'] and remaining()>7200:
                ck=dr_trial(ck,'white_v2')
        if remaining()<=120:break
        ck=training(ck,'autonomous_continued',duration=min(7200,remaining()))
    finish(ck,'Effective budget reached; final measured capabilities and original failed metrics retained')

def handover(parent_pid,parent_ticks):
    global S
    assert not RECEIPT.exists(),'Handover already completed; use explicit settled resume'
    helpers.acquire(ROOT/'autonomy_handover.lock')
    staging=Path('/home/egde/rl_candidates/MOD4_AUTONOMY_SLEEP_20261003')
    install=read(staging/'INSTALL.json')
    for name,digest in install['staged'].items():
        assert base.sha(staging/name)==digest,'Staging source changed'
    parent=identity(parent_pid);assert parent and parent['start_ticks']==parent_ticks and parent['cwd']==str(ROOT)
    assert any(x.endswith('/supervise_spin_rate.py') for x in parent['argv'])
    # Wait for old evaluations to finish without duplicating them.
    start=time.time()
    while True:
        assert same(parent),'Original supervisor identity changed'
        old=read(ROOT/'status.json');trainer=identity(old.get('training_pid',0))
        if trainer and trainer['state']!='Z' and not helpers.active_processes(PROBES):
            try:
                run=rate.trainer_run(ROOT/'logs',trainer['pid'])
                break
            except AssertionError:
                pass  # A new PPO process has not produced its first complete receipt yet.
        assert time.time()-start<7200,'No safe handover window; leave original work intact'
        time.sleep(3)
    assert trainer['cwd']==str(ROOT) and any(x.endswith('/train_mod4_ppo.py') for x in trainer['argv'])
    assert base.trainers()==[trainer['pid']]
    before=base.budget_state();assert before['active_segment']['pid']==trainer['pid']
    base.atomic_json(REPORTS/'AUTONOMY_BEFORE.json',{'parent':parent,'trainer':trainer,'status':old,'budget':before})
    os.kill(parent_pid,signal.SIGSTOP)
    try:
        assert same(parent) and same(trainer) and not helpers.active_processes(PROBES)
        stop=run/'STOP_AFTER_SAVE';assert not stop.exists()
        stop.write_text('Authorized detached autonomous controller handover; full atomic state save then exit.\n')
        while alive(trainer['pid']):
            assert time.time()-start<7500,'Trainer failed to honor save request'
            time.sleep(1)
        ended=time.time();receipt=read(run/'latest_complete.json');assert receipt['pid']==trainer['pid']
        ck=Path(receipt['checkpoint']);ck=ck if ck.is_absolute() else run/ck
        source=base.checkpoint(ck)
        text=Path(old['active_log']).read_text(errors='replace')
        assert 'Full checkpoint saved; authorized budget or stop-file reached' in text and 'Traceback (most recent call last)' not in text
        b=base.budget_state();tail=settle_segment(b,trainer['pid'],ended)
        base.atomic_json(CANONICAL,b)
        # Kill only the frozen, identity-verified retired parent; avoid its SIGTERM cleanup starting old work.
        assert same(parent);os.kill(parent_pid,signal.SIGKILL)
        while alive(parent_pid):time.sleep(.2)
        helpers.acquire(CANONICAL.parent/'native_floor_supervisor.lock')
        # Acquire once here, release this handle before controller() takes ownership.
        lock=helpers.LOCKS.pop();lock.close()
        idle()
        for name in ['mild_dr.py','autonomy_policy.py','spin_rate_probe.py','validate_speed.py','mod4_task.py']:
            assert base.sha(CODE/name)==read(staging/'INSTALL.json')['before'][name]
            __import__('shutil').copy2(staging/name,CODE/name)
        for name in ['mild_dr.py','autonomy_policy.py','autonomy_turn_probe.py']:
            __import__('shutil').copy2(staging/name,TURN/'isaac/mod4'/name)
        assert base.sha(TURN/'isaac/mod4/mod4_task.py')==install['turn_task_before']
        __import__('shutil').copy2(staging/'turn_mod4_task.py',TURN/'isaac/mod4/mod4_task.py')
        manifest=read(REPORTS/'SPIN_SOURCE_FREEZE.json')
        for name in ['mild_dr.py','autonomy_policy.py','spin_rate_probe.py','validate_speed.py','mod4_task.py','supervise_autonomy.py']:
            manifest['sha256']['isaac/mod4/'+name]=base.sha(CODE/name)
        base.atomic_json(REPORTS/'SPIN_SOURCE_FREEZE.json',manifest)
        certified=[read(p) for p in REPORTS.glob('rate*_multiseed.json') if read(p).get('pass')]
        mature_report=max(certified,key=lambda x:float(x['limit_rad_s']))
        mature=mature_report['checkpoint']['path']
        assert base.checkpoint(Path(mature))['sha256']==mature_report['checkpoint']['sha256']
        S={'version':'sleep_v1','profile':'white_v1','chosen_checkpoint':str(ck),'sequence':0,
           'consecutive':0,'failed_blocks':0,'dr_rejected':[],'rate_rejected':[],
           'mature':{'checkpoint':mature,'cap':float(mature_report['limit_rad_s']),'profile':'white_v1'},'active_training':None}
        persist()
        base.atomic_json(RECEIPT,{'source':source,'old_parent':parent,'old_trainer':trainer,'tail_charged_s':tail,
          'save_exit_detection_uncertainty_upper_s':1.,'canonical_budget':str(CANONICAL),'no_budget_added':True,
          'budget_total_s':180000,'installed_sha256':{n:base.sha(CODE/n) for n in ['mild_dr.py','autonomy_policy.py','spin_rate_probe.py','validate_speed.py','supervise_autonomy.py']}})
    except BaseException:
        if not RECEIPT.exists() and same(parent):os.kill(parent_pid,signal.SIGCONT)
        raise

def guardian(owner_pid,owner_ticks,parent_pid,parent_ticks):
    # Separate detached process restores old parent if migration fails BEFORE receipt.
    old={'pid':parent_pid,'start_ticks':parent_ticks,'cwd':str(ROOT)}
    while True:
        now=identity(owner_pid)
        if not now or now['state']=='Z' or now['start_ticks']!=owner_ticks:
            if not RECEIPT.exists() and same(old):os.kill(parent_pid,signal.SIGCONT)
            return
        if (REPORTS/'AUTONOMY_FINISHED.json').exists():return
        b=base.budget_state();a=b.get('active_segment')
        if RECEIPT.exists() and a and alive(a['pid']):
            rem=b['authorized_training_seconds']-b['charged_training_seconds']-max(0,time.time()-a['accounted_through_epoch'])
            if rem<=0:
                p=identity(a['pid'])
                if p['cwd']==str(ROOT) and any(x.endswith('/train_mod4_ppo.py') for x in p['argv']):
                    run=rate.trainer_run(ROOT/'logs',p['pid']);stop=run/'STOP_AFTER_SAVE'
                    if not stop.exists():stop.write_text('Canonical effective budget exhausted; save complete state and stop.\n')
        time.sleep(15)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--takeover',nargs=2,type=int);p.add_argument('--resume',action='store_true')
    p.add_argument('--guardian',nargs=4,type=int);args=p.parse_args()
    if args.guardian:guardian(*args.guardian);sys.exit()
    __import__('torch').set_num_threads(1)
    base.STATE.update(read(ROOT/'status.json'))
    try:
        if args.takeover:
            owner=identity(os.getpid())
            with (ROOT/'autonomy_guardian.log').open('a') as stream:
                subprocess.Popen([base.PY,str(CODE/'supervise_autonomy.py'),'--guardian',str(os.getpid()),str(owner['start_ticks']),
                    *map(str,args.takeover)],stdout=stream,stderr=subprocess.STDOUT,cwd=ROOT,start_new_session=True)
            handover(*args.takeover)
        else:
            assert args.resume and RECEIPT.exists()
            idle();assert not read(STATE_PATH).get('active_training'),'Reconcile the interrupted stage before resuming'
            owner=identity(os.getpid());old=read(RECEIPT)['old_parent']
            with (ROOT/'autonomy_guardian.log').open('a') as stream:
                subprocess.Popen([base.PY,str(CODE/'supervise_autonomy.py'),'--guardian',str(os.getpid()),str(owner['start_ticks']),
                    str(old['pid']),str(old['start_ticks'])],stdout=stream,stderr=subprocess.STDOUT,cwd=ROOT,start_new_session=True)
        controller()
    except BaseException:
        if RECEIPT.exists():
            base.status(stage='attention_required',supervisor_pid=os.getpid(),error=traceback.format_exc(),
              instructions='Preserve weights and canonical budget. Inspect actual children and reconcile any active segment before safe resume.')
        else:
            base.atomic_json(REPORTS/('AUTONOMY_MIGRATION_ERROR_'+str(time.time_ns())+'.json'),
                {'error':traceback.format_exc(),'production_handover_completed':False})
        raise
