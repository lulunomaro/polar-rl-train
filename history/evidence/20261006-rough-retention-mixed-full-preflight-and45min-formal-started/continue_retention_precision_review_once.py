"""Named fullscale precision review; reuse the two completed long readbacks."""
import argparse,os,time,subprocess,traceback,types
from pathlib import Path
import supervise_retention_train as c
H,R,P,CODE,ctl,base,helpers,w=c.H,c.R,c.P,c.CODE,c.ctl,c.base,c.helpers,c.w
U=Path('/home/egde/rl_candidates/MOD4_ROUGH_RETENTION_TRAIN_20261006')
c.ENTRY=Path(__file__).resolve();w.STATE=R/'RETENTION_PRECISION_STATE.json'
verify=c.verify;status=c.status
ctl.PROBES+=('/retention_precision_probe.py',)
original_status=c.status
def status(stage=None,**kw):
    active=ctl.S.get('active_training')
    kw.setdefault('repair_training_started',bool(active and active['phase']=='retention_mixed_learning'))
    original_status(stage,**kw)
c.status=w.status=ctl.status=status
def mixed_probe(checkpoint,count,steps,kind,automatic=False):
    ctl.idle();verify();before=ctl.CANONICAL.read_bytes()
    label=ctl.fresh_label('retention_mix_'+kind);out=ctl.REPORTS/(label+'.json')
    argv=[str(CODE/'retention_precision_probe.py'),'--headless','--checkpoint',str(checkpoint),'--output',str(out),'--num_envs',str(count),'--steps',str(steps)]
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
    assert raw['full30q_writeback_error']<1e-5 and raw['reset_xy_coordinate_ulp_pass'] is True
    assert raw['physics_callback_ticks']>=steps*20 and [raw[k] for k in ('actor_obs_dim','critic_obs_dim','action_dim')]==[35,38,6]
    assert any(max(row)>0 for row in raw['mean_world_z_wheel_load_n'])
    assert ctl.CANONICAL.read_bytes()==before,'Frozen probe changed canonical budget'
    if not automatic and steps>=1500:
        assert raw['complete_world_cycles'] and all(x['metrics']['complete_cycle_count']>=1 for x in raw['complete_world_cycles'])
    base.atomic_json(out.with_name(out.stem+'_admission.json'),dict(pass_=True,raw=str(out),sha256=base.sha(out),engine_errors=[],complete_circle_counts=[r['metrics']['complete_cycle_count'] for r in raw['complete_world_cycles']],finite_quality_is_diagnostic=True))
    status(evaluation_pid=None);return str(out)


c.mixed_probe=mixed_probe
def continuation():
    ctl.S=w.read(ctl.STATE_PATH);base.STATE.update(w.read(P/'status.json'))
    helpers.acquire(P/'autonomy_controller.lock');helpers.acquire(ctl.CANONICAL.parent/'native_floor_supervisor.lock')
    ctl.idle();verify();assert not w.STATE.exists() and not (R/'PRECISION_CONTINUATION_STARTED.json').exists()
    prior=w.read(U/'reports/RETENTION_TRAIN_STATE.json');assert prior['phase']=='repair_hold' and 'auto_0342_retention_mix_fullscale_physical' in prior['reason']
    for marker in ('LOCK_REVIEW_LAUNCHED.json','RETENTION_GUARDIAN_STARTED.json'):
        saved=w.read(U/'reports'/marker);actual=helpers.identity(saved['pid']);assert not actual or actual['state']=='Z' or actual['start_ticks']!=saved['start_ticks']
    before=ctl.CANONICAL.read_bytes();assert base.sha(ctl.CANONICAL)==w.read(U/'reports/RETENTION_INSTALL_BOUNDARY.json')['budget_sha256']
    source=Path(w.read(c.F/'reports/PHYSICAL_DR_STAGE1_REVIEW_READY.json')['checkpoint']['path']);info=base.checkpoint(source)
    assert info['sha256']==c.SOURCE_SHA and info['finite_tensors']==68
    reused=[]
    for number,kind,steps in ((340,'timed_lifecycle',1700),(341,'complete_cycles',1500)):
        path=P/'reports'/f'auto_{number:04d}_retention_mix_{kind}_cap12.5664_white_v3.json';raw=w.read(path)
        assert raw['pass_'] and raw['steps_completed']==steps and raw['actual_task_resets']==0 and raw['checkpoint_sha256']==info['sha256']
        assert raw['actual_material_bindings']['pass_'] and raw['initial_parameters']['actual_parameters_pass'] and raw['final_parameters']['actual_parameters_pass']
        if kind=='complete_cycles':assert all(row['metrics']['complete_cycle_count']>=1 for row in raw['complete_world_cycles'])
        reused.append(dict(path=str(path),sha256=base.sha(path),steps=steps,source_sha256=info['sha256'],explicitly_reused=True))
    assert ctl.CANONICAL.read_bytes()==before and not ctl.S.get('active_training')
    ctl.S.update(profile='white_v3',chosen_checkpoint=str(source),active_training=None);ctl.persist()
    owner=helpers.identity(os.getpid());base.atomic_json(R/'PRECISION_CONTINUATION_STARTED.json',dict(owner=owner,source=info,reused_readbacks=reused,old_failed_fullscale_retained=True,budget_bytes_exact=True,budget_operations=0))
    with (H/'guardian_precision_continuation.log').open('x') as log:
        guardian=subprocess.Popen([base.PY,str(c.ENTRY),'--guardian',str(os.getpid()),str(owner['start_ticks'])],cwd=P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    base.atomic_json(R/'RETENTION_GUARDIAN_STARTED.json',helpers.identity(guardian.pid))
    try:
        physical=mixed_probe(source,20000,120,'fullscale_precision_physical',automatic=True)
        small=c.preflight(source,128,2);large=c.preflight(source,20000,4)
        base.atomic_json(R/'RETENTION_COMPLETE_PREFLIGHT_PASSED.json',dict(pass_=True,source=info,lifecycle=reused[0]['path'],complete_circles=reused[1]['path'],physical=physical,small=small,large=large,all_preflight_weights_discarded=True,old_long_readbacks_explicitly_reused=True))
        charge=base.budget_state()['charged_training_seconds'];assert ctl.remaining()>120
        w.phase('bounded_retention_mixed_learning',source=info,duration_s=min(2700,ctl.remaining()),flat_fraction=.75,rough_fraction=.25)
        checkpoint=ctl.training(source,'retention_mixed_learning',duration=min(2700,ctl.remaining()))
        assessment=mixed_probe(checkpoint,32,1500,'learning_assessment')
        pairs,path=c.old_paired(checkpoint)
        review=dict(checkpoint=base.checkpoint(checkpoint),effective_exposure_s=base.budget_state()['charged_training_seconds']-charge,mixed_assessment=assessment,old_skill_paired_path=path,old_skill_paired_pass=pairs['pass_'],world_summary=pairs['world_summary'],all_curricula_finished=False,actual_budget=base.budget_state())
        base.atomic_json(R/'RETENTION_REVIEW_READY.json',review);w.phase('retention_mix_review_ready',**review)
        status('retention_mix_review_ready',training_pid=None,evaluation_pid=None,validation_pid=None,final_evaluation=review)
    except BaseException:
        w.hold(source,traceback.format_exc());raise
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
    if a.guardian:c.guardian(int(a.guardian[0]),a.guardian[1])
    else:continuation()
