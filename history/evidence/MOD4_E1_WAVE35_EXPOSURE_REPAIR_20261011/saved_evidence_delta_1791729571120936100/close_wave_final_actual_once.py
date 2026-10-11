"""Freeze the observed own final and append its metadata; never runs training."""
from wave_io import *

def main():
    proofpath=sorted(R.glob('WAVE_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json'))[-1]
    proof=json.loads(proofpath.read_bytes());assert proof['passed'] and proof['closeout_ready']
    collectionpath=sorted(R.glob('WAVE142_COLLECTED_[0-9]*.json'))[-1]
    collection=json.loads(collectionpath.read_bytes());assert collection['published']
    segment=proof['own_unique_completed_segment'][0]
    seconds=segment['ended_epoch']-segment['started_epoch']
    h=proof['health'];assert proof['actual_updates']==98 and h['control_steps']==2352
    final=dict(epoch=time.time(),root=ROOT,source_count=368,checkpoint=proof['own_checkpoint'],
        actual_updates=98,controls=2352,envsteps=proof['actual_environment_steps'],callbacks=h['actual_physics_callbacks'],
        target_seconds=1800,actual_load_learn_save_exit_seconds=seconds,unique_segment=segment,
        ordinary=h['ordinary_episode_reset_events'],integrity=h['integrity_task_reset_events'],unknown=h['unknown_task_reset_events'],
        nonfinite=h['nonfinite_observed'],STOP=h['stop_reason'],closure_m=h['max_closure_error_m'],mimic_rad=h['max_mimic_error_rad'],
        timeout=16403,route=17903,unique_truncation=34298,overlap=8,two_reason_coverage_exact=True,
        own_CPU_source_PID_snapshot_fullsave_PASSED_verified=True,actual_snapshot_count=proof['actual_snapshot_file_count'],
        actual_original_processes_exited=True,two_OS_locks_free=True,active_Sactive_empty=True,
        legal_phase=proof['actual_state']['phase'],qualified_Wave=False,full142_behavior_pending=True,
        formal_training_trace_exposure_review_pending=True,same_G3_samecommand_full_CPU_CUDA_restored_exact=True,
        not_PhysX_exactresume=True,remaining_seconds_snapshot=proof['remaining_seconds'],canonical_total_seconds=1188000,
        budget_extensions=7,no_new_budget_or_training_authority=True)
    finalpath=save('WAVE_FORMAL_FINAL_ACTUAL_REVIEW.json',final)
    manifestpath=next((D/'own_active_actual').rglob('run_manifest.json'))
    configbase=D/'inherited_source/isaac/mod4'
    names=['autonomy_policy.py','mild_dr.py','sensor_mild_math.py','sensor_a0_runtime.py']
    dr=dict(epoch=time.time(),trial_id='WAVE368-ACTUAL-DR-SCOPE-READONLY',checkpoint_SHA=proof['own_checkpoint']['sha256'],
        unchanged_strength=True,basic_physical_profile='white_v3',sensor_profile='noise_bias_mild_v1',
        RM_DR_OFF_1_disables_only_legacy_monolithic_bundle=True,dedicated_DR_enabled=True,
        mass_and_inertia_factor=[.9,1.1],motor_output_gain_factor=[.9,1.1],wheel_friction_coefficient=[.7,1.0],friction_buckets=33,
        basic_physical_group_nominal_episode_probability=.2,nominal_is_not_all_DR_off=True,
        gas_spring_N_per_m=[3150,3850],gas_damping_Ns_per_m=[2.7,3.3],chassis_COM_xyz_m=[-.005,.005],motor_PD_factor=[.95,1.05],
        feedback_delay_ms=[0,10],physical_action_delay_ms=[0,2.5,5],
        sensor_uniform_raw_pre_scale_noise=dict(angular_velocity_rad_s=.125,projected_gravity=.025,leg_position_rad=.005,leg_velocity_rad_s=.25,wheel_velocity_rad_s=.5),
        episode_leg_encoder_bias_bound_rad=.0075,actor_noise_delay_enabled_critic_clean=True,
        strong_push_armature_joint_friction_randomization_enabled=False,not_full_D6_joint_friction_coverage=True,
        actual_manifest=dict(path=str(manifestpath),bytes=manifestpath.stat().st_size,sha256=H(manifestpath.read_bytes())),
        code_indices=[dict(path=str(configbase/name),bytes=(configbase/name).stat().st_size,sha256=H((configbase/name).read_bytes())) for name in names],
        full_actual_startup_restored_D0_D7_and_rng=True,no_runtime_DR_or_GPU_mutation=True)
    save('WAVE_DR_ACTUAL_SCOPE_REVIEW.json',dr)
    save('WAVE_DR_READER_MISSING_PATH_ERROR.json',dict(epoch=time.time(),attempted_path=str(configbase/'sensor_dr_manager.py'),
        error='Get-Content path not found; original command failed before any mutation.',
        resolved_actual_sources=[str(configbase/'sensor_a0_runtime.py'),str(configbase/'sensor_mild_math.py')],
        evidence_kind='preserved_reader_error_description_not_fabricated_raw_log',no_physical_failure_or_GPU_replay=True))
    n,w=io.connect_both()
    try:
        v=run(n,r'''from pathlib import Path
import json,hashlib,time
D=Path(ROOT_TOKEN);run=Path(RUN_TOKEN);rows=[]
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
for base in (D/'reports',run):
 for p in sorted(base.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts or p.suffix.lower() not in ('.json','.log','.txt','.pt','.npz','.md'):continue
  rows.append(dict(path=str(p),relative_path=str(p.relative_to(D)),bytes=p.stat().st_size,sha256=digest(p),full_capture=p.suffix.lower() not in ('.pt','.npz') and p.stat().st_size<=8000000))
print(json.dumps(dict(epoch=time.time(),root=str(D),run=str(run),entries=rows,actual_final_frozen=True,large_originals_retained=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)).replace('RUN_TOKEN',repr(str(Path(proof['own_checkpoint']['path']).parent).replace('\\','/'))))
        dest=D/'own_final_actual';assert not dest.exists();dest.mkdir()
        with n.open_sftp() as f:
            for row in v['entries']:
                if row['full_capture']:
                    raw=f.open(row['path'],'rb').read();assert len(raw)==row['bytes'] and H(raw)==row['sha256']
                    p=dest/row['relative_path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);row['local_capture']=str(p)
        save('WAVE_FINAL_SOURCE_REPORT_COLLECTION.json',v)
        with n.open_sftp() as f:
            for name,p in [('E1_WAVE35_EXPOSURE_FORMAL_FINAL_ACTUAL_REVIEW.json',finalpath),('E1_WAVE35_EXPOSURE_OWN_FINAL_CPU_VERIFIED.json',proofpath),('E1_WAVE35_142_CURRENT_ACTUAL_COLLECTION.json',collectionpath),('E1_WAVE35_DR_ACTUAL_SCOPE_REVIEW.json',R/'WAVE_DR_ACTUAL_SCOPE_REVIEW.json')]:io.put(f,io.E+'/reports/'+name,p.read_bytes())
        synced=run(n,r'''from pathlib import Path
import json,time,os,hashlib
R=Path(CENTRAL_TOKEN)/'reports';j=lambda p:json.loads(p.read_bytes());proof=j(R/'E1_WAVE35_EXPOSURE_OWN_FINAL_CPU_VERIFIED.json');assert proof['passed'] and proof['closeout_ready']
B=Path(BUDGET_TOKEN);budget_before=B.read_bytes();assert hashlib.sha256(budget_before).hexdigest()==proof['budget_SHA']
protected={name:(R/name).read_bytes() for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json')}
current=dict(epoch=time.time(),root=proof['root'],phase=proof['actual_state']['phase'],formal_final_pending=False,own_final_CPU=str(R/'E1_WAVE35_EXPOSURE_OWN_FINAL_CPU_VERIFIED.json'),own_formal_review=str(R/'E1_WAVE35_EXPOSURE_FORMAL_FINAL_ACTUAL_REVIEW.json'),candidate142_collection=str(R/'E1_WAVE35_142_CURRENT_ACTUAL_COLLECTION.json'),full142_behavior_pending=True,qualified_Wave=False,legal_review_boundary=True)
q=R/'E1_WAVE35_EXPOSURE_FORMAL_FINAL_CURRENT_ACTUAL.json';assert not q.exists();q.write_text(json.dumps(current,indent=2))
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();c=json.loads(before);scope=c['terrain_subexpert_revision004']['wave35_exposure_repair_next_scope'];assert scope['root']==proof['root'] and scope['source_count']==368
scope.update(formal_final_pending=False,actual_phase=proof['actual_state']['phase'],own_final_CPU=current['own_final_CPU'],own_formal_review=current['own_formal_review'],actual_final_checkpoint_SHA=proof['own_checkpoint']['sha256'],actual_final_updates=proof['actual_updates'],actual_final_controls=proof['health']['control_steps'],candidate142_collection=current['candidate142_collection'],full_candidate142_behavior_pending=True,formal_full_trace_review_pending=True)
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.WAVEFINAL-'+str(time.time_ns()));tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2));os.replace(tmp,p)
assert B.read_bytes()==budget_before and all((R/name).read_bytes()==raw for name,raw in protected.items())
v=dict(epoch=time.time(),metadata_synced=True,formal_final_pending=False,full142_behavior_pending=True,protected_plan_and_canonical_bytes_exact=True,no_GPU_queue_or_budget_mutation=True,actual_final_current=current)
p=R/'E1_WAVE35_EXPOSURE_FINAL_CLOSEOUT_METADATA_SYNCED.json';assert not p.exists();p.write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('CENTRAL_TOKEN',repr(io.E)).replace('BUDGET_TOKEN',repr(io.B)))
        save('WAVE_FINAL_CLOSEOUT_METADATA_SYNCED.json',synced)
        print(json.dumps(dict(actual_seconds=seconds,final_report=str(finalpath),metadata_synced=True,captured_indices=len(v['entries']),full142_pending=True)))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('WAVE_FINAL_CLOSEOUT_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),old_once_not_replayed=True));raise
