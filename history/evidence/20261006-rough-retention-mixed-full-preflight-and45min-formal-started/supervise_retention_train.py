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
w.STATE=R/'RETENTION_TRAIN_STATE.json'
VERSION='mixed_flat75_gentle25_retention_full_PPO_v1'
SOURCE_SHA='2f82374fe07a849dbbaeabbf8dd34b20d0df8da789f2ebc2be3e688a1b24498a'
ENTRY=H/'supervise_retention_train.py'
T=Path('/home/egde/rl_candidates/MOD4_ROUGH_RETENTION_MIX_RUNTIME_20261006')

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
    for n,sha in w.read(T/'reports/SOURCE_FREEZE.json')['sha256'].items():assert base.sha(T/n)==sha,n

def status(stage=None,**kw):
    b=base.budget_state()
    values=dict(supervisor_pid=os.getpid(),active_code_root=str(H),canonical_budget=str(ctl.CANONICAL),
        authorized_training_seconds=b['authorized_training_seconds'],budget_seconds=b['authorized_training_seconds'],
        autonomy_version=VERSION,controller_version=VERSION,lesson='rough_retention_mix',profile='white_v3',
        actual_terrain='MOD4 gentle intro; pinned five-family source with explicit amplitude overrides',terrain_stand_fraction=.2,terrain_body_vx_range=[-.3,.3],
        terrain_body_vy_yaw_zero=True,flat_fraction=.75,rough_fraction=.25,repair_executor_deployed=True,repair_training_started=False,spin_stage_finished=True,physical_dr_stage1_practical_closeout=True,
        rough_lesson_finished=False,all_curricula_finished=False)
    if stage:values['stage']=stage
    values.update(kw);values.update(authorized_training_seconds=b['authorized_training_seconds'],budget_seconds=b['authorized_training_seconds']);base.status(**values)

def freeze_run(run):
    out=run/'rolling_source_freeze.json'
    if out.exists():return
    freeze=w.read(w.F)
    for n,sha in freeze['sha256'].items():
        assert base.sha(H/n)==sha
        dst=run/'rough_intro_source_snapshot'/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(H/n,dst)
    base.atomic_json(out,dict(candidate_root=str(H),sha256=freeze['sha256'],controller_version=VERSION,
        acceptance_version=w.VERSION,lesson='rough_retention_mix',actual_terrain='mod4_intro_gentle_v1',legacy_mod4_terrain_tag='flat',
        full_joint_reset=30,ground_query_phase='postphysics_before_termination_reward',body_vx_range=[-.3,.3],vy_yaw=[0.,0.],
        observations_and_PPO_hardware_DR_reward_weights_unchanged=True,flat_fraction=.75,rough_fraction=.25,flat_command_mix={'stand':.1,'straight':.4,'pure':.3,'world':.2},rolling_proxy_not_used_for_terrain_spin=True,
        forward_scan_diagnostic_only=True))

w.verify=ctl.verify=verify;w.status=ctl.status=status;w.rate.freeze_run=freeze_run
ctl.PROBES=tuple(ctl.PROBES)+('/retention_train_probe.py',)

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


def mixed_probe(checkpoint,count,steps,kind,automatic=False):
    ctl.idle();verify();before=ctl.CANONICAL.read_bytes()
    label=ctl.fresh_label('retention_mix_'+kind);out=ctl.REPORTS/(label+'.json')
    argv=[str(CODE/'retention_train_probe.py'),'--headless','--checkpoint',str(checkpoint),'--output',str(out),'--num_envs',str(count),'--steps',str(steps)]
    if automatic:argv+=['--automatic']
    p=base.spawn(argv,out.with_suffix('.log'));ctl.LIVE=p
    w.phase('frozen_retention_'+kind,child=helpers.identity(p.pid),output=str(out),source=base.checkpoint(checkpoint))
    status('frozen_retention_'+kind,training_pid=None,evaluation_pid=p.pid,active_log=str(out.with_suffix('.log')))
    raw=base.wait_probe(p,out);ctl.LIVE=None
    from rough_saved_preflight_review import ERROR_MARKERS
    errors=[line for line in out.with_suffix('.log').read_text(errors='replace').splitlines() if any(s.lower() in line.lower() for s in ERROR_MARKERS)]
    assert not errors,errors[:8]
    assert raw['pass_'] and raw['steps_completed']==steps and raw['actual_task_resets']==0 and not raw['nonfinite']
    assert raw['max_closure_m']<=.002 and raw['max_mimic_rad']<=.01
    assert raw['initial_parameters']['actual_parameters_pass'] and raw['final_parameters']['actual_parameters_pass']
    assert raw['actual_material_bindings']['pass_'] and raw['actor_critic_command_readback_error']<1e-6
    assert raw['ground_fresh_readback_error']<1e-5 and raw['height_reward_readback_error']<1e-6
    assert raw['full30q_writeback_error']<1e-5 and raw['requested_reset_xy_error']<1e-5
    assert raw['physics_callback_ticks']>=steps*20 and [raw[k] for k in ('actor_obs_dim','critic_obs_dim','action_dim')]==[35,38,6]
    assert any(max(row)>0 for row in raw['mean_world_z_wheel_load_n'])
    assert ctl.CANONICAL.read_bytes()==before,'Frozen probe changed canonical budget'
    if not automatic and steps>=1500:
        assert raw['complete_world_cycles'] and all(x['metrics']['complete_cycle_count']>=1 for x in raw['complete_world_cycles'])
    base.atomic_json(out.with_name(out.stem+'_admission.json'),dict(pass_=True,raw=str(out),sha256=base.sha(out),engine_errors=[],complete_circle_counts=[r['metrics']['complete_cycle_count'] for r in raw['complete_world_cycles']],finite_quality_is_diagnostic=True))
    status(evaluation_pid=None);return str(out)

def preflight(checkpoint,count,iterations):
    from retention_training import mixed_training
    prior=base.budget_state();saved=mixed_training(ctl,checkpoint,'retention_mix_'+str(count)+'_discard',count=count,iterations=iterations,duration=600)
    run=saved.parent;m=w.read(run/'run_manifest.json');latest=w.read(run/'latest_complete.json');freeze=w.read(run/'rolling_source_freeze.json')
    assert m['init_checkpoint_sha256']==SOURCE_SHA and m['start_iteration']==23509 and m['num_envs']==count and m['additional_iterations_arg']==iterations
    assert m['actual_retention_mix']['flat_fraction']==.75 and m['actual_retention_mix']['rough_fraction']==.25 and m['actual_retention_mix']['complete_joint_reset']==30
    assert freeze['sha256']==w.read(w.F)['sha256'] and base.checkpoint(saved)['finite_tensors']==68
    segments=[s for s in base.budget_state()['completed_segments'] if s['pid']==latest['pid']];assert len(segments)==1
    log=Path(segments[0]['log']);text=log.read_text(errors='replace')
    from rough_saved_preflight_review import ERROR_MARKERS
    errors=[line for line in text.splitlines() if any(s.lower() in line.lower() for s in ERROR_MARKERS)];assert not errors,errors[:5]
    import re
    assert int(re.findall(r'Total steps:\s*(\d+)',text)[-1])==count*24*iterations
    assert '[INFO]: SimulationContext cleared' in text
    original=helpers.identity(latest['pid']);assert not original or original['state']=='Z'
    actual_env=dict(m['env']);actual_env.pop('RM_RESCUE_DEADLINE',None);assert actual_env==w.read(CODE/'env.json')
    times=[float(x) for x in re.findall(r'Iteration time:\s*([0-9.]+)s',text)]
    result=dict(pass_=True,num_envs=count,full_iterations=iterations,discarded_weights=base.checkpoint(saved),source=base.checkpoint(checkpoint),latest=latest,run_manifest_sha256=base.sha(run/'run_manifest.json'),source_freeze_sha256=base.sha(run/'rolling_source_freeze.json'),segment=segments[0],charged_once=True,total_steps=count*24*iterations,throughput=count*24/(sum(times)/len(times)),throughput_cost_diagnostic=True,errors=[])
    base.atomic_json(R/('RETENTION_PREFLIGHT_'+str(count)+'_PASSED.json'),result);return result

def guardian(owner,ticks):
    while True:
        identity=helpers.identity(owner);b=base.budget_state();active=b['active_segment']
        if active:
            remaining=b['authorized_training_seconds']-b['charged_training_seconds']-max(0,time.time()-active['accounted_through_epoch'])
            trainer=helpers.identity(active['pid'])
            if remaining<=0 and trainer and str(CODE/'train_mod4_ppo.py') in trainer['argv'] and trainer['cwd']==str(P):
                run=w.rate.trainer_run(P/'autonomy_preflight_logs' if active['kind'].endswith('discard') else P/'logs',trainer['pid'])
                stop=run/'STOP_AFTER_SAVE'
                if not stop.exists():stop.write_text('Sole canonical budget exhausted; atomic full save then stop.\n')
        if not active and ((R/'RETENTION_REVIEW_READY.json').exists() or not identity or str(identity['start_ticks'])!=str(ticks)):return
        time.sleep(15)

def controller():
    ctl.S=w.read(ctl.STATE_PATH);base.STATE.update(w.read(P/'status.json'))
    helpers.acquire(P/'autonomy_controller.lock');helpers.acquire(ctl.CANONICAL.parent/'native_floor_supervisor.lock')
    ctl.idle();verify();assert not w.STATE.exists() and not (R/'RETENTION_TRAIN_STARTED.json').exists(),'Already executed; never resume main'
    before=ctl.CANONICAL.read_bytes();state=w.read(T/'reports/RETENTION_COMPONENT_SIGNATURE_STATE.json')
    assert state['phase']=='retention_mixed_component_review_ready'
    for key in ('owner','child'):
        saved=state.get(key);actual=helpers.identity(saved['pid']) if saved else None
        assert not actual or actual['state']=='Z' or actual['start_ticks']!=saved['start_ticks']
    source=Path(w.read(F/'reports/PHYSICAL_DR_STAGE1_REVIEW_READY.json')['checkpoint']['path'])
    info=base.checkpoint(source);assert info['sha256']==SOURCE_SHA and info['finite_tensors']==68 and info['iteration_stored']==23509
    assert w.read(F/'reports/PHYSICAL_DR_STAGE1_REVIEW_READY.json')['world_progress_05_confirmed']
    assert w.read(R/'RETENTION_MIX_SIGNATURE_SDK_READBACK.json')['pass_']
    assert not base.budget_state()['active_segment'] and not ctl.S.get('active_training') and ctl.CANONICAL.read_bytes()==before
    ctl.S.update(profile='white_v3',chosen_checkpoint=str(source),active_training=None);ctl.persist()
    owner=helpers.identity(os.getpid())
    base.atomic_json(R/'RETENTION_TRAIN_STARTED.json',dict(owner=owner,source=info,old_component_reused=True,old23509_paired_baseline_reused=True,old23624_candidate_preserved=True,budget_handover_operations=0,budget_bytes_sha256=base.sha(ctl.CANONICAL)))
    with (H/'guardian_retention_train.log').open('x') as log:
        g=subprocess.Popen([base.PY,str(ENTRY),'--guardian',str(os.getpid()),str(owner['start_ticks'])],cwd=P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    base.atomic_json(R/'RETENTION_GUARDIAN_STARTED.json',helpers.identity(g.pid))
    last=source
    try:
        lifecycle=mixed_probe(source,32,1700,'timed_lifecycle',automatic=True)
        circles=mixed_probe(source,32,1500,'complete_cycles')
        physical=mixed_probe(source,20000,120,'fullscale_physical',automatic=True)
        small=preflight(source,128,2);large=preflight(source,20000,4)
        base.atomic_json(R/'RETENTION_COMPLETE_PREFLIGHT_PASSED.json',dict(pass_=True,source=info,lifecycle=lifecycle,complete_circles=circles,physical=physical,small=small,large=large,all_preflight_weights_discarded=True))
        before_charge=base.budget_state()['charged_training_seconds'];assert ctl.remaining()>120
        w.phase('bounded_retention_mixed_learning',source=info,duration_s=min(2700,ctl.remaining()),flat_fraction=.75,rough_fraction=.25)
        status('bounded_retention_mixed_learning',repair_training_started=True)
        checkpoint=ctl.training(source,'retention_mixed_learning',duration=min(2700,ctl.remaining()))
        exposure=base.budget_state()['charged_training_seconds']-before_charge
        assessment=mixed_probe(checkpoint,32,1500,'learning_assessment')
        pairs,path=old_paired(checkpoint);last=checkpoint
        review=dict(checkpoint=base.checkpoint(checkpoint),effective_exposure_s=exposure,mixed_assessment=assessment,old_skill_paired_path=path,old_skill_paired_pass=pairs['pass_'],world_summary=pairs['world_summary'],all_curricula_finished=False,actual_budget=base.budget_state())
        base.atomic_json(R/'RETENTION_REVIEW_READY.json',review)
        w.phase('retention_mix_review_ready',**review,last_validated_source=base.checkpoint(last))
        status('retention_mix_review_ready',training_pid=None,evaluation_pid=None,validation_pid=None,final_evaluation=review)
    except BaseException:
        reason=traceback.format_exc();w.hold(last,reason);raise

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--guardian',nargs=2);args=parser.parse_args()
    if args.guardian:guardian(int(args.guardian[0]),args.guardian[1])
    else:controller()
