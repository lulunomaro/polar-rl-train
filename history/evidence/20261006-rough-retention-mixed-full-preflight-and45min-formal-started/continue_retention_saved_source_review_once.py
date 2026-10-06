"""Reuse finished physics/128 PPO; validate sources and train sequentially."""
import argparse,os,time,subprocess,traceback
from pathlib import Path
import supervise_retention_train as c
import continue_retention_precision_review_once as precision
from retention_saved_source_review import saved_preflight,preflight
from retention_autonomous_progress import diagnostic
H,R,P,CODE,ctl,base,helpers,w=c.H,c.R,c.P,c.CODE,c.ctl,c.base,c.helpers,c.w
V=Path('/home/egde/rl_candidates/MOD4_ROUGH_RETENTION_PRECISION_REVIEW_20261006')
W=Path('/home/egde/rl_candidates/MOD4_RETENTION_AUTO_PROGRESS_20261006')
c.ENTRY=Path(__file__).resolve();w.STATE=R/'RETENTION_SOURCE_REVIEW_STATE.json'
c.mixed_probe=precision.mixed_probe

def exited(root,names):
    for name in names:
        saved=w.read(root/'reports'/name);actual=helpers.identity(saved['pid'])
        assert not actual or actual['state']=='Z' or actual['start_ticks']!=saved['start_ticks'],name

def controller():
    ctl.S=w.read(ctl.STATE_PATH);base.STATE.update(w.read(P/'status.json'))
    helpers.acquire(P/'autonomy_controller.lock');helpers.acquire(ctl.CANONICAL.parent/'native_floor_supervisor.lock')
    ctl.idle();c.verify();assert not w.STATE.exists() and not (R/'SAVED_SOURCE_CONTINUATION_STARTED.json').exists()
    old=w.read(V/'reports/RETENTION_PRECISION_STATE.json');assert old['phase']=='repair_hold' and 'rolling_source_freeze.json' in old['reason']
    exited(V,('PRECISION_LAUNCHED.json','RETENTION_GUARDIAN_STARTED.json'))
    exited(W,('AUTO_PROGRESS_LAUNCHED.json',))
    before=ctl.CANONICAL.read_bytes()
    source=Path(w.read(c.F/'reports/PHYSICAL_DR_STAGE1_REVIEW_READY.json')['checkpoint']['path']);info=base.checkpoint(source)
    assert info['sha256']==c.SOURCE_SHA and info['finite_tensors']==68
    assert not ctl.S.get('active_training') and not base.budget_state()['active_segment']
    reused=[]
    for number,kind,steps in ((340,'timed_lifecycle',1700),(341,'complete_cycles',1500),(343,'fullscale_precision_physical',120)):
        path=P/'reports'/f'auto_{number:04d}_retention_mix_{kind}_cap12.5664_white_v3.json';raw=w.read(path)
        assert raw['pass_'] and raw['steps_completed']==steps and raw['actual_task_resets']==0 and not raw['nonfinite']
        assert raw['checkpoint_sha256']==info['sha256'] and raw['actual_material_bindings']['pass_']
        assert raw['initial_parameters']['actual_parameters_pass'] and raw['final_parameters']['actual_parameters_pass']
        assert raw['max_closure_m']<=.002 and raw['max_mimic_rad']<=.01
        if kind=='complete_cycles':assert all(x['metrics']['complete_cycle_count']>=1 for x in raw['complete_world_cycles'])
        if number==343:assert raw['reset_xy_coordinate_ulp_pass'] and raw['physics_callback_ticks']>=2400
        reused.append(dict(path=str(path),sha256=base.sha(path),explicitly_reused=True))
    smallrun=P/'autonomy_preflight_logs/2026-10-06_17-54-41_auto_0344_retention_mix_128_discard_cap12.5664_white_v3'
    small=saved_preflight(c,smallrun,source,128,2,V)
    assert ctl.CANONICAL.read_bytes()==before
    owner=helpers.identity(os.getpid())
    base.atomic_json(R/'SAVED_SOURCE_CONTINUATION_STARTED.json',dict(owner=owner,source=info,explicitly_reused=reused,
        small_preflight_reused=True,old_reader_rejection_preserved=True,budget_operations=0,budget_bytes_exact=True,
        user_instruction='自主判断够用后接下一科；主机顺序训练及回归，不等待桌面巡检'))
    with (H/'guardian_saved_source_review.log').open('x') as log:
        g=subprocess.Popen([base.PY,str(c.ENTRY),'--guardian',str(os.getpid()),str(owner['start_ticks'])],cwd=P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    base.atomic_json(R/'RETENTION_GUARDIAN_STARTED.json',helpers.identity(g.pid))
    last=source
    try:
        large=preflight(c,source,20000,4)
        base.atomic_json(R/'RETENTION_COMPLETE_PREFLIGHT_PASSED.json',dict(pass_=True,source=info,lifecycle=reused[0]['path'],complete_circles=reused[1]['path'],physical=reused[2]['path'],small=small,large=large,all_preflight_weights_discarded=True))
        charge=base.budget_state()['charged_training_seconds'];cycles=0
        while True:
            exposure=base.budget_state()['charged_training_seconds']-charge
            # Initial45min, then at most a planned2h additional envelope. Save
            # and exit time remain fully charged; no budget extension here.
            planned=2700 if cycles==0 else min(2700,9900-exposure)
            if planned<=0 or ctl.remaining()<=120:break
            w.phase('bounded_retention_mixed_learning',source=base.checkpoint(last),duration_s=min(planned,ctl.remaining()),flat_fraction=.75,rough_fraction=.25,sequential_block=cycles)
            last=ctl.training(last,'retention_mixed_learning',duration=min(planned,ctl.remaining()))
            assessment=c.mixed_probe(last,32,1500,'learning_assessment')
            pairs,path=c.old_paired(last);cycles+=1
            review=dict(checkpoint=base.checkpoint(last),effective_exposure_s=base.budget_state()['charged_training_seconds']-charge,mixed_assessment=assessment,old_skill_paired_path=path,old_skill_paired_pass=pairs['pass_'],world_summary=pairs['world_summary'],all_curricula_finished=False,actual_budget=base.budget_state())
            base.atomic_json(R/('RETENTION_BLOCK_REVIEW_'+str(cycles)+'.json'),review)
            decision=diagnostic(last,path,assessment)
            base.atomic_json(R/('RETENTION_AUTO_DECISION_'+str(cycles)+'.json'),dict(checkpoint=base.checkpoint(last),**decision))
            if decision['auto_closeout_sufficient']:
                closeout=dict(**review,actual_decision=decision,next_lesson='independent observation noise and episode encoder bias validation',next_executor_deployed=False)
                base.atomic_json(R/'RETENTION_PRACTICAL_CLOSEOUT.json',closeout)
                w.phase('retention_repaired_next_sensor_DR_preparation',**closeout)
                break
            # Non-perfect target facts are optimization diagnostics. A later
            # agent may accept small residuals, never an endless100% loop.
        base.atomic_json(R/'RETENTION_REVIEW_READY.json',review)
        if not (R/'RETENTION_PRACTICAL_CLOSEOUT.json').exists():w.phase('retention_auto_progress_saved_review',**review)
        c.status(w.read(w.STATE)['phase'],training_pid=None,evaluation_pid=None,validation_pid=None,final_evaluation=review)
    except BaseException:
        w.hold(source,traceback.format_exc());raise

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
    if a.guardian:c.guardian(int(a.guardian[0]),a.guardian[1])
    else:controller()
