"""Verify completed own330 full save and natural boundary; no restore, learning or accounting."""
from pathlib import Path
import sys,os,json,shlex,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_G2_MATCHED_CONTINUE_20261010';PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
def main():
    secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
    try:
        code="""from pathlib import Path
import sys,torch,json,time,hashlib,os
D=Path(ROOT);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1);import supervise_e1_G2_matched_continuation as m
j=lambda p:json.loads(p.read_bytes());H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state=j(D/'reports/E1_STATE.json');row=j(D/'reports/e1_G2_matched_continuation_PASSED.json');assert state['phase']=='E1_G2_matched_continuation_saved_review_ready' and state['child'] is None and not (D/'reports/E1_ATTENTION.json').exists()
def gone(v):
 p=Path('/proc')/str(v['pid'])
 if not p.exists():return True
 s=(p/'stat').read_text().split(') ',1)[1].split();return s[0]=='Z' or int(s[19])!=v['start_ticks']
assert gone(state['owner']) and gone(j(D/'reports/E1_GUARDIAN_STARTED.json')) and gone(dict(pid=row['own_PID_bound_receipt']['pid'],start_ticks=72519910))
run=Path(row['run']);rec=j(run/'latest_complete.json');assert rec==row['own_PID_bound_receipt'] and rec['pid']==1873663;path=Path(rec['checkpoint']);info=m.fullsave(path);assert info['finite_tensors']==96 and info['sha256']==row['checkpoint']['sha256'] and info['iteration_stored']==32103
f=j(D/'reports/SOURCE_FREEZE.json')['sha256'];mf=j(run/'run_manifest.json');rolling=j(run/'rolling_source_freeze.json');assert len(f)==330 and rolling['sha256']==mf['source_map']==f
for n,h in f.items():assert H(D/n)==H(run/'e1_source_snapshot'/n)==h,n
for n,h in mf['src_sha256'].items():assert H(run/'src_snapshot'/n)==h,n
starts={n:j(run/n) for n in ('E1_TERRAIN_RESUME_STARTUP_VERIFIED.json','CHASSIS_PD_RESUME_STARTUP_VERIFIED.json','GAS_DAMPING_RESUME_STARTUP_VERIFIED.json','SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json','ACTION_DELAY_RESUME_STARTUP_VERIFIED.json')}
assert mf['init_checkpoint_sha256']=='42cdc9d24519778a9da3e35b05a3eb3bb5745760c26a5842c78fcde2bd39e53b' and all(v['source_sha256']==mf['init_checkpoint_sha256'] for v in starts.values())
t=starts['E1_TERRAIN_RESUME_STARTUP_VERIFIED.json'];assert t['terrain_state_restored_exact'] and not t['explicitly_new_E1_terrain'] and t['actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact'] and t['complete_D1_D7_optimizer_global_named_streams_verified'] and t['E1_episode_incremented_once'] and not t['PhysX_exact_resume_claimed']
h=row['health'];assert h==j(run/'CLOCK_TRAINING_HEALTH.json') and h['control_steps']==row['actual_updates']*24==1104 and h['actual_physics_callbacks']==h['expected_physics_callbacks']==4416 and row['actual_environment_steps']==22080000 and h['termination_reason_coverage_exact'] and h['truncation_reason_coverage_exact'] and not h['nonfinite_observed'] and h['stop_reason'] is None
assert h['ordinary_episode_reset_events']==h['integrity_task_reset_events']==h['unknown_task_reset_events']==0
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');before=B.read_bytes();budget=json.loads(before);assert budget['active_segment'] is None and budget['authorized_training_seconds']==828000
segments=[x for x in budget['completed_segments'] if x['pid']==rec['pid']];assert segments==row['unique_completed_segment'] and len(segments)==1
assert not j(m.s.q.ctl.STATE_PATH).get('active_training') and not torch.cuda.is_initialized() and B.read_bytes()==before
ER=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports');approval=j(ER/'PLAN_APPROVAL.json');tracks=j(ER/'EXECUTION_TRACKS.json');current=j(ER/'MOE_PLAN_EXECUTION_CURRENT.json');assert approval['approved'] and approval['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b' and H(ER/'MOD4_MOE_MASTER_PLAN.md')==approval['approved_plan_sha256']
central_names=('E1_G2_MODEL32058_COMPLETE_MATCHED_REVIEW.json','SELECTED_E1_G2_MATCHED_CONTINUATION_SOURCE.json','E1_G2_MATCHED_CONTINUATION_REPORT.md','NEXT_G2_MATCHED_CONTINUATION_REVIEW_WORK_ORDER.md','E1_G2_MATCHED_CONTINUATION_METADATA_SYNCED.json','LATEST_HANDOFF.md')
central={n:dict(path=str(ER/n),bytes=(ER/n).stat().st_size,sha256=H(ER/n)) for n in central_names};assert j(ER/central_names[0])['review_complete'] and j(ER/central_names[4])['only_previously_unexecuted_metadata_CAS_completed']
print(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-MATCHED-NATURAL-FINAL-CPU-01',checkpoint=info,bytes=path.stat().st_size,own_PID_bound_receipt=rec,source_count=len(f),snapshot_count=len(mf['src_sha256']),all_own_source_snapshot_receipt_SHA_exact=True,actual_updates=row['actual_updates'],actual_environment_steps=row['actual_environment_steps'],health=h,unique_completed_segment=segments,actual_segment_seconds=segments[0]['ended_epoch']-segments[0]['started_epoch'],parent_guardian_child_actual_exited=True,active_Sactive_empty=True,canonical_bytes_preserved_by_reader=True,remaining_seconds=budget['authorized_training_seconds']-budget['charged_training_seconds'],CPU_only_no_CUDA_initialized=True,all_courses_finished=False,new_budget_seconds=0,central_context_read=central,plan_approval_annotations=approval.get('plan_annotations'),tracks_curriculum_annotations=tracks.get('curriculum_annotations'),actual_phase=state['phase'],behavior124_still_requires_actual_review=True)))
""".replace('ROOT',repr(ROOT))
        compile(code,'<own-final-read>','exec');_,o,e=c.exec_command(PY+' -c '+shlex.quote(code),timeout=120);b=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(b+err).decode(errors='replace');v=json.loads(b);p=R/('FINAL_ACTUAL_VERIFIED_'+str(int(v['epoch']))+'.json');assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')
        print(json.dumps(dict(report=str(p),checkpoint=v['checkpoint']['path'],sha256=v['checkpoint']['sha256'],CPU=v['checkpoint']['finite_tensors'],source_count=v['source_count'],snapshot_count=v['snapshot_count'],actual_updates=v['actual_updates'],actual_segment_seconds=v['actual_segment_seconds'],actual_boundary_verified=True,remaining_seconds=v['remaining_seconds'],behavior_pending=True)))
    finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
    try:main()
    except Exception:
        p=R/('FINAL_ACTUAL_READER_ERROR_'+str(int(time.time()))+'.json');assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-MATCHED-FINAL-CPU-READER-01',error=traceback.format_exc(),no_production_mutation=True),indent=2),encoding='utf8');raise
