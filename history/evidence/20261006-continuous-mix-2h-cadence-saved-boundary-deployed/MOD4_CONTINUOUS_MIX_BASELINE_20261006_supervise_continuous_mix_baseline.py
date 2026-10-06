"""Same mixed scope, one bounded2h baseline block, fewer repeated full suites."""
import argparse,os,subprocess,traceback
from pathlib import Path
import supervise_retention_train as c
import continue_retention_precision_review_once as precision
from retention_autonomous_progress import diagnostic
c.ENTRY=Path(__file__).resolve();c.w.STATE=c.R/'CONTINUOUS_MIX_STATE.json';c.mixed_probe=precision.mixed_probe

def controller():
    assert not c.w.STATE.exists() and not (c.R/'CONTINUOUS_MIX_STARTED.json').exists(),'Executed once; never resume main'
    c.ctl.S=c.w.read(c.ctl.STATE_PATH);c.base.STATE.update(c.w.read(c.P/'status.json'))
    c.helpers.acquire(c.P/'autonomy_controller.lock');c.helpers.acquire(c.ctl.CANONICAL.parent/'native_floor_supervisor.lock')
    c.ctl.idle();c.verify();h=c.w.read(c.R/'CONTINUOUS_MIX_HANDOVER_ACCEPTED.json')
    assert h['old_launch_authority_retired'] and h['budget_handover_operations']==0
    for saved in h['retired_identities']:
        a=c.helpers.identity(saved['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=saved['start_ticks']
    source=Path(h['source']['path']);info=c.base.checkpoint(source);assert info==h['source'] and info['finite_tensors']==68
    X=Path('/home/egde/rl_candidates/MOD4_ROUGH_RETENTION_SOURCE_REVIEW_20261006')
    freeze=c.w.read(X/'reports/SOURCE_FREEZE.json')
    for n,sha in freeze['sha256'].items():assert c.base.sha(c.H/n)==c.base.sha(X/n)==sha
    assert c.w.read(X/'reports/RETENTION_COMPLETE_PREFLIGHT_PASSED.json')['pass_']
    assert c.w.read(X/'reports/RETENTION_MODEL23621_PAIRED_ACTUAL_REVIEW.json')['checkpoint']==info
    before=c.ctl.CANONICAL.read_bytes();c.ctl.S.update(profile='white_v3',chosen_checkpoint=str(source),active_training=None);c.ctl.persist()
    assert c.ctl.CANONICAL.read_bytes()==before
    owner=c.helpers.identity(os.getpid())
    c.base.atomic_json(c.R/'CONTINUOUS_MIX_STARTED.json',dict(owner=owner,source=info,same197_runtime_sources_exact=True,
        existing_scope_preflight_explicitly_reused=True,no_new_preflight_or_budget_extension=True,
        user_instruction='记录各科最佳策略；现在持续混合训练，后续与MoE专家用共同协议比较',
        planned_block_s=7200,quick_checks='mixed32 and white_v3 flat/spin/world',full_two_seed_three_profile_suite_at_stage_closeout=True))
    with (c.H/'guardian_continuous_mix.log').open('x') as log:
        g=subprocess.Popen([c.base.PY,str(c.ENTRY),'--guardian',str(os.getpid()),str(owner['start_ticks'])],cwd=c.P,
            stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    c.base.atomic_json(c.R/'RETENTION_GUARDIAN_STARTED.json',c.helpers.identity(g.pid))
    last=source
    try:
        assert c.ctl.remaining()>120
        c.w.phase('bounded_continuous_mixed_learning',source=info,duration_s=min(7200,c.ctl.remaining()),flat_fraction=.75,rough_fraction=.25,sensor_DR_enabled=False)
        last=c.ctl.training(source,'continuous_mixed_baseline_learning',duration=min(7200,c.ctl.remaining()))
        assessment=c.mixed_probe(last,32,1500,'continuous_mix_quick_assessment')
        quick=[]
        for kind in ('flat','spin','world'):
            raw,path=c.w.probe(last,kind,'white_v3',20261002);c.parameter_readback(raw,'white_v3',kind)
            quick.append(dict(kind=kind,path=str(path),sha256=c.base.sha(path)))
        c.base.atomic_json(c.R/'CONTINUOUS_MIX_QUICK_REVIEW.json',dict(checkpoint=c.base.checkpoint(last),mixed_assessment=assessment,existing_data_admission_pass=True,quick=quick))
        # A full paired suite is meaningful here at the stage's final source.
        pairs,path=c.old_paired(last);decision=diagnostic(last,path,assessment)
        review=dict(checkpoint=c.base.checkpoint(last),paired_path=path,mixed_assessment=assessment,
            strict_world_progress_05_confirmed=pairs['world_progress_05_confirmed'],actual_decision=decision,
            all_curricula_finished=False,sensor_executor_started=False,next_lesson='Independent sensor feedback validation after actual balanced retention review',actual_budget=c.base.budget_state())
        c.base.atomic_json(c.R/'CONTINUOUS_MIX_REVIEW_READY.json',review)
        # The unchanged guardian observes this original generic saved-review index.
        c.base.atomic_json(c.R/'RETENTION_REVIEW_READY.json',review)
        c.w.phase('continuous_mix_baseline_saved_review',**review)
        c.status('continuous_mix_baseline_saved_review',training_pid=None,evaluation_pid=None,final_evaluation=review)
    except BaseException:
        c.w.hold(source,traceback.format_exc());raise

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
    if a.guardian:c.guardian(int(a.guardian[0]),a.guardian[1])
    else:controller()
