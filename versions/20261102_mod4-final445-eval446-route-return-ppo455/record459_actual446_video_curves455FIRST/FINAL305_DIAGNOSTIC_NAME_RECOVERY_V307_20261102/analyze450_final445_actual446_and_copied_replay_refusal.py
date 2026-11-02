"""Saved final445/actual446 facts and copied437 replay refusal; no model or newphysics."""
from pathlib import Path
import hashlib
import json
import statistics
import time

P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports'
N=T/'RL_SATURATION_ACTUAL_PPO_PRODUCTION_V445_20261102'
E=T/'RL445_FINAL_INDEPENDENT_EVAL_V446_20261102'
OLD=T/'RL433_FIRST_ACTUAL_INDEPENDENT_EVAL_V437_20261102'
read=lambda path:json.loads(path.read_bytes())
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
returned=read(E/'reports/ROOT446_EVALUATION_FULL_RETURNED.json');result=returned['result']
assert not returned['wrapper_error']and result['passed']and result['first_episodes']==80
cpu=read(N/'reports/ROOT445_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json')
assert cpu['passed']and result['model_SHA']==cpu['SHA']=='056410f592d07ff63c3acc6adac4d1ebb0357bc154e817568bec56ba155f18ed'
complete=read(N/'reports/ROOT445_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
assert complete['passed_collection']and complete['owner_closed']['canonical_None']and complete['owner_closed']['shared_locks_free']
normal=read(N/'reports/ROOT445_NORMAL900_RECOVERY_JUMP_FULL_UTF8_AND_FORMAL_ACTUAL.json')
assert normal['original_node_exit']['all_own_children_waited']
files={Path(row['path']).name:row['UTF8']for row in returned['full_UTF8']}
release=json.loads(files['ACTUAL446_ALL_WAITED_PRIVATE_SHARED_EX_RELEASED.json'])
assert release['all_own_children_waited']and release['private_shared_EX_released']
ssh=read(E/'reports/ROOT446_ALL_SSH_CLOSED_FREE.json')
assert ssh['all_owned_SSH_closed']and ssh['SESSION_restored']and ssh['global_serial_control_client_lease']=='FREE'
rows=result['results'];assert len(rows)==80
strict=[row for row in rows if row['strict270_stable']]
manifold=json.loads(files['ACTUAL446_CONTACT_MANIFOLD_LATCHED_LANDING_TRACE.json'])
audits=[]
for row in strict:
    env=row['env'];longest=run=0;end=None
    for tick in manifold['rows']:
        run=run+1 if tick['active'][env]and tick['steady'][env]else 0
        if run>longest:longest=run;end=tick['tick']
    assert longest>=200 and row['first_flight_whole_footprint_clear']and not row['ground_return_after_clear']and not row['edge_return_after_clear']
    audits.append(dict(env=env,strict_ticks=longest,stable_seconds=longest*.0025,end_tick=end,actual_manifold=True))
trace=json.loads(files['ACTUAL446_CURRENT_STATE_MPC_CONTROL_TRACE.json'])
residual=[row['learned_residual_mean_abs']for row in trace['rows']]
copied=[]
for row in result['replay']:
    existing=E/'replay'/Path(row['path']).name
    original=OLD/'replay'/('REPLAY437_env'+str(row['env'])+'.npz')
    assert existing.exists()and original.exists()
    actualSHA=H(existing);sourceSHA=H(original)
    assert actualSHA==sourceSHA and actualSHA!=row['SHA']
    copied.append(dict(env=row['env'],path=str(existing),bytes=existing.stat().st_size,SHA=actualSHA,
        matches_old437=str(original),old437SHA=sourceSHA,actual446_required_path=row['path'],
        actual446_required_bytes=row['bytes'],actual446_required_SHA=row['SHA'],not_actual446=True))
prior=read(R/'ANALYSIS440_ACTUAL_FINAL433_EVAL437_FACTS_AND_MANIFOLD.json')
summary=dict(epoch=time.time(),passed=True,scope='Actual independent final445 eval446 complete; localreplay transfer failed afterphysics',
    modelSHA=result['model_SHA'],modelbytes=cpu['bytes'],CPU790finite=cpu['finite_tensors']==790,
    Pi=169,critic=169,totalWM=36159,newWM=5428,actorAdam=56634,criticAdam=13694,
    fullstate=cpu,formal=complete['formals']['jump_72'],final=normal['final']['final'],
    controls=result['controls'],physics=result['physics_callbacks'],feedback=result['feedback_samples'],
    first_episodes=80,strict=len(strict),strict_envs=[row['env']for row in strict],
    whole_footprint_clear=sum(row['first_flight_whole_footprint_clear']for row in rows),
    leading_cross=sum(row['first_flight_both_cross']for row in rows),airborne=sum(row['airborne_ever']for row in rows),
    full8s=sum(row['full_window']for row in rows),mean_seconds=statistics.mean(row['seconds']for row in rows),
    median_seconds=statistics.median(row['seconds']for row in rows),terminations=result['terminations'],
    longest_top_support_s=max(row['top_contact_longest_seconds']for row in rows),
    mean_tracking_cost=statistics.mean(row['tracking_cost_mean']for row in rows),
    mean_tracking_components={key:statistics.mean(row['tracking_components'][key]for row in rows)for key in rows[0]['tracking_components']},
    mean_learned_residual_control=statistics.mean(residual),max_learned_residual_control=max(residual),
    strict_manifold_audits=audits,allownwaited_private_shared_released=True,allSSHclosedFREE=True,
    originalfee=complete['owner_closed']['raw_fee_sum_once'],historical_closingbalance=complete['owner_closed']['closing_balance_snapshot'],balance_not_current=True,
    prior433_437={key:prior[key]for key in('strict','whole_footprint_clear','leading_cross','full8s','mean_seconds','median_seconds','terminations','mean_tracking_cost')},
    comparison_caveat='Samefixed270/newDRseed9137protocol but not exactpaired contacttrajectory; survival improvement is not skill or proved singlecause',
    replay_failure=dict(original_errors=[str(path)for path in(E/'reports').glob('ROOT446_ORIGINAL_ERROR_*.json')],
        cause='prepare445copied non-source replay and renderreportdirectories from437 while renaming filenames; fresh446SFTPdest.mkdir refused existing directory',
        original446_once_consumed=True,actual_eval_not_invalidated=True,old_copied_replay=copied,
        no_actual446_native_image=True,old_renderreports_not_actual446_proof=True,
        preserve_all_original_files=True,recovery='Independent451readonlytransfer of knownactual446savedNPZs to newroot, no model/SDK/physics rerun'),
    RL=True,onlineMPC=False,autonomous_depthonly=False,
    next='Recover only actual446 recordedposes, nativeview_image then targeted RLdecision; do not repeat unchanged445hour or oldeval',
    modelreads=0,SDK=0,newphysics=0,network=0)
with(R/'ANALYSIS450_FINAL445_ACTUAL446_FACTS_AND_REPLAY_REFUSAL.json').open('x',encoding='utf8')as stream:json.dump(summary,stream,indent=2,ensure_ascii=False,allow_nan=False)
print(json.dumps({key:summary[key]for key in('passed','strict','whole_footprint_clear','leading_cross','full8s','mean_seconds','terminations','longest_top_support_s','mean_tracking_cost','mean_learned_residual_control')},ensure_ascii=False),flush=True)
