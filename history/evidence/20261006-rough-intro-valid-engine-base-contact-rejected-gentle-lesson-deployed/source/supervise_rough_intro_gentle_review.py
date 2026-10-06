"""One new intro terrain exposure, existing sole ledger, then saved review.

The completed initial DR and terrain components are never rerun. All learning
weights are warm-started from exact 23509; preflight weights are discarded.
"""
import argparse,os,sys,time,subprocess,traceback,shutil,math
from pathlib import Path
import supervise_world_spin as w
from physical_dr_contract import parameter_readback,paired_review,compact_worlds
H,R,P,CODE,ctl,base,helpers=w.D,w.R,w.P,w.CODE,w.ctl,w.base,w.helpers
F=Path('/home/egde/rl_candidates/MOD4_PHYSICAL_DR_STAGE1_20261006')
w.STATE=R/'ROUGH_INTRO_GENTLE_STATE.json'
VERSION='rough_intro_gentle_geometry_exact_triangle_chunked_collision_bounded_review'
SOURCE_SHA='2f82374fe07a849dbbaeabbf8dd34b20d0df8da789f2ebc2be3e688a1b24498a'
ENTRY=H/'supervise_rough_intro_gentle_review.py'

def verify():
    b=base.budget_state();assert b['owner_root']==str(P)
    for n,sha in w.read(P/'reports/SPIN_SOURCE_FREEZE.json')['sha256'].items():
        path=Path(n);path=path if path.is_absolute() else P/path
        actual=base.sha(path)
        if actual!=sha:
            ui=w.read(R/'DISPLAY_SOURCE_REVIEW.json')
            assert n==ui['path']=='isaac/mod4/tui_spin_rate.py' and sha==ui['original_sha256'] and actual==ui['approved_sha256'] and ui['only_evaluation_panel_changed']
    for n,sha in w.read(w.F)['sha256'].items():assert base.sha(H/n)==sha,n
    cfg=w.read(CODE/'env.json');original=w.read(F/'isaac/mod4/env.json');assert cfg==original
    assert cfg['RM_MILD_DR_PROFILE']=='white_v3' and cfg['RM_KEEP_STD']=='1' and cfg['RM_WORLD_DRIFT_PROFILE']=='cycle_v1'
    assert float(cfg['RM_SPIN_MAX_RAD_S'])==4*math.pi
    for n,sha in w.read(F/'reports/SOURCE_FREEZE.json')['sha256'].items():assert base.sha(F/n)==sha,n

def status(stage=None,**kw):
    b=base.budget_state()
    values=dict(supervisor_pid=os.getpid(),active_code_root=str(H),canonical_budget=str(ctl.CANONICAL),
        authorized_training_seconds=b['authorized_training_seconds'],budget_seconds=b['authorized_training_seconds'],
        autonomy_version=VERSION,controller_version=VERSION,lesson='rough_intro_stage1',profile='white_v3',
        actual_terrain='MOD4 gentle intro; pinned five-family source with explicit amplitude overrides',terrain_stand_fraction=.2,terrain_body_vx_range=[-.3,.3],
        terrain_body_vy_yaw_zero=True,spin_stage_finished=True,physical_dr_stage1_practical_closeout=True,
        rough_lesson_finished=False,all_curricula_finished=False)
    if stage:values['stage']=stage
    values.update(kw);base.status(**values)

def freeze_run(run):
    out=run/'rolling_source_freeze.json'
    if out.exists():return
    freeze=w.read(w.F)
    for n,sha in freeze['sha256'].items():
        assert base.sha(H/n)==sha
        dst=run/'rough_intro_source_snapshot'/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(H/n,dst)
    base.atomic_json(out,dict(candidate_root=str(H),sha256=freeze['sha256'],controller_version=VERSION,
        acceptance_version=w.VERSION,lesson='rough_intro_stage1',actual_terrain='mod4_intro_gentle_v1',legacy_mod4_terrain_tag='flat',
        full_joint_reset=30,ground_query_phase='postphysics_before_termination_reward',body_vx_range=[-.3,.3],vy_yaw=[0.,0.],
        observations_and_PPO_hardware_DR_reward_weights_unchanged=True,rolling_proxy_not_used_for_terrain_spin=True,
        forward_scan_diagnostic_only=True))

w.verify=ctl.verify=verify;w.status=ctl.status=status;w.rate.freeze_run=freeze_run
ctl.PROBES=tuple(ctl.PROBES)+('/rough_intro_probe.py',)

def rough_probe(checkpoint,count,steps,kind):
    ctl.idle();verify()
    label=ctl.fresh_label('rough_intro_'+kind);out=ctl.REPORTS/(label+'.json')
    p=base.spawn([str(CODE/'rough_intro_probe.py'),'--headless','--checkpoint',str(checkpoint),'--output',str(out),'--num_envs',str(count),'--steps',str(steps)],out.with_suffix('.log'))
    ctl.LIVE=p;w.phase('frozen_rough_'+kind,child=helpers.identity(p.pid),output=str(out),source=base.checkpoint(checkpoint))
    status('frozen_rough_'+kind,training_pid=None,evaluation_pid=p.pid,active_log=str(out.with_suffix('.log')))
    result=base.wait_probe(p,out);ctl.LIVE=None
    compact={k:result.get(k) for k in ('pass_','steps_completed','alive_count','actual_task_resets','nonfinite','failure_snapshots')}
    log_text=out.with_suffix('.log').read_text(errors='replace')
    errors=[line for line in log_text.splitlines() if ('PhysX error:' in line or 'simulation will miss interactions' in line or 'buffer overflow' in line.lower() or 'cooking failure' in line.lower() or 'Unable to create triangle mesh' in line or 'BV4 tree failed' in line)]
    base.atomic_json(out.with_name(out.stem+'_engine_error_review.json'),dict(engine_errors=errors,pass_=not errors))
    assert not errors,dict(physics_engine_errors=errors[:10],raw_report=str(out))
    assert result['pass_'] and result['steps_completed']==steps and result['actual_task_resets']==0,compact
    assert result['exact_collision_partition']['pass_'] and result['physical_contact_callback_ticks']>=steps*20
    assert any(max(row)>0 for row in result['mean_world_z_wheel_load_n']), 'No actual wheel support despite authored ground rays'
    assert [result[k] for k in ('actor_obs_dim','critic_obs_dim','action_dim')]==[35,38,6]
    assert result['initial_parameters']['actual_parameters_pass'] and result['final_parameters']['actual_parameters_pass']
    status(evaluation_pid=None);return str(out)

def old_paired(checkpoint):
    rows=[];profiles=('nominal','white_v2','white_v3')
    for seed in (20261002,20261003):
        for kind in ('flat','spin','world'):
            rs=[]
            for profile in profiles:
                r,p=w.probe(checkpoint,kind,profile,seed)
                parameter_readback(r,profile,kind);rs.append((r,p))
            rows.append(dict(seed=seed,kind=kind,paths=[str(p) for _,p in rs]))
    result=paired_review(rows,lambda p:w.read(Path(p)),w.assess_flat,w.evidence,w.target,base.checkpoint(checkpoint),profiles)
    result.update(pairs=rows,world_summary=compact_worlds(result['world_tracking']),learning_admission_only=True)
    path=ctl.REPORTS/(ctl.fresh_label('rough_intro_old_flat_skill_paired')+'.json');base.atomic_json(path,result)
    return result,str(path)

def guardian(owner,ticks):
    while True:
        identity=helpers.identity(owner);b=base.budget_state();active=b['active_segment']
        if active:
            remaining=b['authorized_training_seconds']-b['charged_training_seconds']-max(0,time.time()-active['accounted_through_epoch'])
            trainer=helpers.identity(active['pid'])
            if remaining<=0 and trainer and str(CODE/'train_mod4_ppo.py') in trainer['argv'] and trainer['cwd']==str(P):
                run=w.rate.trainer_run(P/'logs' if not active['kind'].endswith('discard') else P/'autonomy_preflight_logs',trainer['pid'])
                stop=run/'STOP_AFTER_SAVE'
                if not stop.exists():stop.write_text('Sole canonical budget exhausted; atomic full save then stop.\n')
        if not active and ((R/'ROUGH_INTRO_REVIEW_READY.json').exists() or not identity or str(identity['start_ticks'])!=str(ticks)):return
        time.sleep(15)

def controller():
    ctl.S=w.read(ctl.STATE_PATH);base.STATE.update(w.read(P/'status.json'))
    helpers.acquire(P/'autonomy_controller.lock');helpers.acquire(ctl.CANONICAL.parent/'native_floor_supervisor.lock')
    ctl.idle();verify();assert not w.STATE.exists() and not (R/'ROUGH_INTRO_STARTED.json').exists(),'Entry already executed'
    before=ctl.CANONICAL.read_bytes();readback=w.read(R/'INTRO_SIGNATURE_READBACK.json');state=w.read(R/'INTRO_SIGNATURE_REVIEW_STATE.json')
    assert state['phase']=='intro_task_readback_ready' and readback['pass_'] and readback['steps_completed']==300
    prior=helpers.identity(state['owner']['pid']);assert not prior or prior['state']=='Z' or prior['start_ticks']!=state['owner']['start_ticks']
    ready=w.read(F/'reports/PHYSICAL_DR_STAGE1_REVIEW_READY.json');source=Path(ready['checkpoint']['path'])
    info=base.checkpoint(source);assert info['sha256']==SOURCE_SHA and info['finite_tensors']==68
    assert ready['paired_pass'] and ready['world_progress_05_confirmed'] and info['sha256']==base.sha(Path(readback['checkpoint']))
    assert w.read(F/'reports/PHYSICAL_DR_STAGE1_PRACTICAL_CLOSEOUT.json')['stage1_practical_closeout_accepted']
    for marker in ('PHYSICAL_DR_LAUNCHED.json','PHYSICAL_DR_GUARDIAN_STARTED.json'):
        old=w.read(F/'reports'/marker);actual=helpers.identity(old['pid']);assert not actual or actual['state']=='Z' or actual['start_ticks']!=old['start_ticks']
    assert base.budget_state()['active_segment'] is None and ctl.CANONICAL.read_bytes()==before
    ctl.S['profile']='white_v3';ctl.S['chosen_checkpoint']=str(source);ctl.S['active_training']=None;ctl.persist()
    owner=helpers.identity(os.getpid())
    base.atomic_json(R/'ROUGH_INTRO_STARTED.json',dict(owner=owner,source=info,readback_explicitly_reused=str(R/'INTRO_SIGNATURE_READBACK.json'),
        old_flat_skill_closeout_evidence_reused=ready['paired_path'],baseline_old_runtime_byte_exact_except_unused_train_entry=True,budget_handover_operations=0))
    with (H/'guardian_rough_intro.log').open('x') as log:
        g=subprocess.Popen([base.PY,str(ENTRY),'--guardian',str(os.getpid()),str(owner['start_ticks'])],cwd=P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    base.atomic_json(R/'ROUGH_INTRO_GUARDIAN_STARTED.json',helpers.identity(g.pid))
    last=source
    try:
        w.phase('rough_intro_preflight',source=info,owner=owner)
        # F18 exact-source flat/4pi/world baselines and new10env3s actual task
        # readback are reused, not executed again.
        short=rough_probe(source,10,300,'gentle_task_readback')
        physical=rough_probe(source,20000,120,'gentle_fullscale_physical')
        ctl.training(source,'rough_intro_128_discard',count=128,iterations=2,duration=600)
        ctl.training(source,'rough_intro_20k_discard',count=20000,iterations=4,duration=600)
        before_charge=base.budget_state()['charged_training_seconds']
        assert ctl.remaining()>120
        w.phase('bounded_rough_intro_learning',source=info,duration_s=min(2700,ctl.remaining()),preflight_physical=physical)
        checkpoint=ctl.training(source,'rough_intro_stage1_learning',duration=min(2700,ctl.remaining()))
        exposure=base.budget_state()['charged_training_seconds']-before_charge
        paths=[rough_probe(checkpoint,10,1500,'learning_assessment')]
        pairs,path=old_paired(checkpoint);last=checkpoint
        review=dict(checkpoint=base.checkpoint(checkpoint),effective_exposure_s=exposure,rough_paths=paths,old_skill_paired_path=path,
            old_skill_paired_pass=pairs['pass_'],world_summary=pairs['world_summary'],all_terrain_skills_completed=False,
            first_intro_learning_only=True,actual_budget=base.budget_state())
        base.atomic_json(R/'ROUGH_INTRO_REVIEW_READY.json',review)
        w.phase('rough_intro_stage1_review_ready',**review,last_validated_source=base.checkpoint(last))
        status('rough_intro_stage1_review_ready',training_pid=None,evaluation_pid=None,validation_pid=None,final_evaluation=review)
    except BaseException:
        reason=traceback.format_exc();w.hold(last,reason);raise

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--guardian',nargs=2);args=parser.parse_args()
    if args.guardian:guardian(int(args.guardian[0]),args.guardian[1])
    else:controller()
