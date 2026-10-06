"""Validate a finished preflight using its actual saved source evidence.

A short run can exit before the supervisor's periodic full-source copy.
The original manifest/src_snapshot and pre/post candidate hash checks remain
distinct; a post-exit review never masquerades as a runtime full snapshot.
"""
import math,re
from pathlib import Path

def saved_preflight(c,run,checkpoint,count,iterations,source_root):
    run=Path(run);source_root=Path(source_root)
    m=c.w.read(run/'run_manifest.json');latest=c.w.read(run/'latest_complete.json')
    saved=Path(latest['checkpoint']);saved=saved if saved.is_absolute() else run/saved
    assert saved.parent==run and latest['log_dir']==str(run)
    info=c.base.checkpoint(saved);source=c.base.checkpoint(checkpoint)
    assert m['init_checkpoint_sha256']==source['sha256']==c.SOURCE_SHA
    assert m['start_iteration']==23509 and m['num_envs']==count and m['additional_iterations_arg']==iterations
    assert info['finite_tensors']==68 and info['iteration_stored']>=23509+iterations-1
    assert m['actual_retention_mix']['flat_fraction']==.75 and m['actual_retention_mix']['rough_fraction']==.25
    assert m['actual_retention_mix']['complete_joint_reset']==30 and not m['actual_retention_mix']['scan_in_observation']
    freeze=c.w.read(source_root/'reports/SOURCE_FREEZE.json')
    for n,h in freeze['sha256'].items():
        assert c.base.sha(source_root/n)==h,n
        assert c.base.sha(c.H/n)==h,n
    # These bytes were copied by the trainer itself before PPO, not by us.
    assert len(m['src_sha256'])>=11
    snapshots=[]
    for n,h in m['src_sha256'].items():
        assert c.base.sha(run/'src_snapshot'/n)==h,n
        matches=[p for p in (source_root/'isaac/mod4'/n,Path(m['robot_usd']).parent/n) if p.is_file()]
        assert matches and any(c.base.sha(p)==h for p in matches),n
        snapshots.append(dict(name=n,sha256=h))
    rolling=run/'rolling_source_freeze.json'
    if rolling.exists():assert c.w.read(rolling)['sha256']==freeze['sha256']
    env=dict(m['env']);env.pop('RM_RESCUE_DEADLINE',None)
    assert env==c.w.read(c.CODE/'env.json')
    b=c.base.budget_state();assert not b['active_segment'] and not c.ctl.S.get('active_training')
    segments=[s for s in b['completed_segments'] if s['pid']==latest['pid']]
    assert len(segments)==1 and segments[0]['ended_epoch']>=latest['saved_at']
    original=c.helpers.identity(latest['pid']);assert not original or original['state']=='Z'
    text=Path(segments[0]['log']).read_text(errors='replace')
    from rough_saved_preflight_review import ERROR_MARKERS
    errors=[line for line in text.splitlines() if any(s.lower() in line.lower() for s in ERROR_MARKERS)]
    assert not errors,errors[:8]
    assert '[INFO]: SimulationContext cleared' in text
    assert int(re.findall(r'Total steps:\s*(\d+)',text)[-1])==count*24*iterations
    times=[float(x) for x in re.findall(r'Iteration time:\s*([0-9.]+)s',text)]
    assert len(times)==iterations and all(math.isfinite(t) and t>0 for t in times)
    result=dict(pass_=True,num_envs=count,full_iterations=iterations,discarded_weights=info,
        source=source,latest=latest,run_manifest_sha256=c.base.sha(run/'run_manifest.json'),
        actual_trainer_snapshot=snapshots,actual_trainer_snapshot_count=len(snapshots),
        periodic_full_run_freeze_present=rolling.exists(),candidate_root=str(source_root),
        candidate_source_map=freeze['sha256'],candidate_current_exact=True,
        source_evidence_scope='Trainer manifest snapshots plus prelaunch controller verify and post-exit full candidate verification; not a fabricated runtime full snapshot',
        segment=segments[0],charged_once=True,total_steps=count*24*iterations,
        throughput=count*24/(sum(times)/len(times)),throughput_cost_diagnostic=True,errors=[])
    c.base.atomic_json(c.R/('RETENTION_PREFLIGHT_'+str(count)+'_PASSED.json'),result)
    return result

def preflight(c,checkpoint,count,iterations):
    from retention_training import mixed_training
    c.verify()
    saved=mixed_training(c.ctl,checkpoint,'retention_mix_'+str(count)+'_discard',count=count,iterations=iterations,duration=600)
    c.verify()
    return saved_preflight(c,saved.parent,checkpoint,count,iterations,c.H)
