"""Record actual frozen sampler integration FIRST without new SSH/model reads."""
from pathlib import Path
import datetime,hashlib,json,time
N=Path(__file__).resolve().parent;G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
D=G/'history/reviews/20261105-mod4v2-scut-jump200';S=N.parents[1]
A=N/'supermimic_final3786_sampling_1h';R=A/'reports'
read=lambda p:json.loads(Path(p).read_bytes())
returned=read(R/'FIRST_ACTUAL_RETURNED.json');f=returned['files']
assert read(R/'FIRST_VALIDATION.json')['valid']
first=f['production/FIRST_UPDATED.json'];latest=f['production/LATEST_PROGRESS.json'];restore=f['production/FULL_STATE_RESTORE.json']
assert first['iteration']==3787 and restore['source_iteration']==3786
assert first['new_verified_BPTT_steps']==1 and first['bptt']['verified_bptt_optimizer_step']
startup=f['production/STARTUP.json'];execution=startup['sampling_execution']
assert execution['geometry']['implementation']=='TorchScript_pure_geometry'
assert all(r['fused']for r in execution['optimizers'].values())
assert restore['all4_optimizers_replay_RNG_7components_restored']
log=f['WORKER.log'];raw=log['text'].encode()
assert log['complete']and len(raw)==log['bytes']and hashlib.sha256(raw).hexdigest()==log['SHA']
errors=[line for line in log['text'].splitlines()if any(s in line.lower()for s in ('traceback','outofmemoryerror','failed to allocate'))]
assert not errors and not f.get('production/ERROR.json')
collector=read(R/'POSTROUND_EXACT_CIM.json')['row'];assert collector['ProcessId']==78196
go=f['GO_PRODUCTION.json'];tz=datetime.timezone(datetime.timedelta(hours=8))
stamp=lambda epoch:datetime.datetime.fromtimestamp(epoch,tz).isoformat()
out=dict(epoch=time.time(),status='ACTUAL_VALID_FIRST3787_FULL3786_RESTORE_OPTIMIZED_SOLE78196',
    root=str(A),remote=read(A/'PLAN.json')['remote_root'],source=restore,FIRST=first,
    latest_returned_snapshot=latest,snapshot_epoch=returned['epoch'],snapshot_time=stamp(returned['epoch']),
    latest_snapshot_not_current_instantaneous=True,
    sampling_execution=execution,full_workerlog={k:v for k,v in log.items()if k!='text'},full_workerlog_errors=errors,
    collector=collector,owner=f['OWNER_STARTED.json']['identity'],worker=f['WORKER_IDENTITY.json'],GO=go,
    window_local=dict(GO=stamp(go['learning_started_epoch']),SAVE=stamp(go['save_deadline']),
        NOMINAL=stamp(go['nominal_end_epoch']),sole_formal_return=stamp(go['save_deadline']+45)),
    first_new_numerical_resets=first['numerical_resets']-973,
    first_new_constraint_resets=first['constraint_resets']-1538,
    latest_new_numerical_resets=latest['numerical_resets']-973,
    latest_new_constraint_resets=latest['constraint_resets']-1538,
    source_final3786_complete_review=str(N/'supermimic_first1941_reboot_periodic_1h/reports/FINAL3786_BOUNDARY_REVIEW.json'),
    actual_old_owner_total_control_steps_per_second=25288.84943098966,
    previous_last_round_total_control_steps_per_second=29063.51784665613,
    actual_new_last_round_total_control_steps_per_second=latest['total_training_control_steps_per_second'],
    snapshot_ratio=latest['total_training_control_steps_per_second']/29063.51784665613,
    snapshot_ratio_is_not_same_state_ABBA_or_hour_mean=True,
    cold_FIRST_total_step_s=first['total_training_control_steps_per_second'],
    six_rounds_with_cold_first_step_s=latest['window_training_control_steps_per_second'],
    worker_including_initialization_and_first_fullsave_step_s=latest['worker_control_steps_per_second'],
    full_hour_speed_pending=True,FIRST_not_skill=True,large_finite_BPTT_gradients_not_no_risk=True,
    cumulative_upper_seconds_before_current=read(A/'PLAN.json')['cumulative_authorized_seconds_before_this_segment'],
    archive_PT_reads=0,production_PT_diagnostic_reads=0,extra_SSH=0,
    next='Healthy sole78196: localexact/children/reports only. No secondSSH/FIRSTreader/modeldecode/hotpatch/relaunch. Originalowner3600fullsave+300safeexit then independent80. After formalcomplete uniqueSuperMimicfinaldiagnosis/all4actualnative review; assess real20k totals and skill before further repair.')
with(R/'VALID_FIRST3787_OPTIMIZATION_ACTUAL.json').open('x',encoding='utf8')as stream:json.dump(out,stream,indent=2)
for path in (D/'WORK_ORDER.json',S/'admin/CURRENT_STATE.json'):
    value=read(path);value['current_training']=out['status'];value['next']=out['next']
    value['sampling_optimization_current']=out
    value['sampling_optimization_20261106']['deployment_status']='ACTUAL_FIRST3787_FULLSAVE_AND_LATEST3792_RETURNED'
    value['sampling_optimization_20261106']['active_root']=str(A)
    value['sampling_optimization_20261106']['sole_collector']=78196
    value['sampling_optimization_20261106']['production20k_speed_not_yet_measured']=False
    value['sampling_optimization_20261106']['full_hour_mean_pending']=True
    if path.name=='WORK_ORDER.json':
        for key in ('newton_migration','supermimic_interleaving'):
            value[key]['current_root']=str(A);value[key]['sole_collector']=collector
        value['supermimic_interleaving']['current_window_status']=out['status']
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps({k:out[k]for k in ('status','snapshot_time','actual_new_last_round_total_control_steps_per_second',
    'cold_FIRST_total_step_s','six_rounds_with_cold_first_step_s','worker_including_initialization_and_first_fullsave_step_s',
    'snapshot_ratio','window_local','first_new_numerical_resets','first_new_constraint_resets')}))
