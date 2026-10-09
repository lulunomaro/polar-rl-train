"""Sync actual saved G3 review boundary; never resume or relaunch training."""
from pathlib import Path
import hashlib,json,os,sys,shlex,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007'
H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect

def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode())

def main():
 a_path=sorted(R.glob('G3_ACTUAL_*.json'))[-1];a=json.loads(a_path.read_bytes())
 o_path=sorted(R.glob('G3_OWN_SAVE_ACTUAL_*.json'))[-1];own=json.loads(o_path.read_bytes())
 assert len(own['formal_saved'])==1 and not own['pending']
 assert all(v is None for v in a['actual'].values()) and not a['canonical']['active_segment']
 assert not a['reports'].get('E1_ATTENTION.json') and a['canonical']['authorized']==828000
 passed=a['reports']['e1_G3_reviewed_observation_PASSED.json'];health=passed['health'];source=own['formal_saved'][0]
 assert source['checkpoint']['sha256']==passed['checkpoint']['sha256'] and len(passed['unique_completed_segment'])==1
 assert health['actual_physics_callbacks']==health['expected_physics_callbacks'] and health['termination_reason_coverage_exact'] and health['truncation_reason_coverage_exact']
 assert not health['nonfinite_observed'] and not health['integrity_task_reset_events'] and not health['unknown_task_reset_events'] and health['stop_reason'] is None
 published=a['reports']['E1_127-e1-g3-observation_ASYNC_PUBLISHED.json'];assert len(published['jobs'])==4
 collected=sorted(R.glob('CANDIDATE_127_COLLECTED_*.json'))[-1];review=json.loads(collected.read_bytes())
 save('FORMAL_CLOSEOUT_SYNC_STARTED.json',dict(epoch=time.time(),trial_id='E1-G3-FORMAL-CLOSEOUT-SYNC-01',once=True,metadata_only=True))
 segment=passed['unique_completed_segment'][0]
 summary=dict(epoch=time.time(),source_selected=passed['checkpoint'],own_formal_CPU96_source338_verified=str(o_path.resolve()),actual_snapshot=str(a_path.resolve()),source_snapshot_count=source['snapshot_count'],actual_updates=passed['actual_updates'],actual_environment_steps=passed['actual_environment_steps'],health=health,unique_original_parent_segment=segment,actual_charged_seconds=segment['ended_epoch']-segment['started_epoch'],original_parent_guardian_child_exited=True,active_segment_empty=True,phase=a['reports']['E1_STATE.json']['phase'],canonical_remaining=a['canonical']['remaining'],canonical_authorized=828000,new_budget_seconds=0,published_127=published,current_127_collection=str(collected.resolve()),complete_cases=list(review['cases']),pending=review['pending'],no_more_PPO_until_actual127_complete_matched_review=True,scope_fullsave_is_not_35mm_route_graduation_or_permanent_anti_forgetting=True,old125_and_byte_receipt_and_world49_residuals_preserved=True)
 save('FORMAL_CLOSEOUT_ACTUAL_VERIFIED.json',summary)
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  files={'E1_G3_OWN_FORMAL_CPU_SOURCE_VERIFIED.json':o_path,'E1_G3_FORMAL_FINAL_CURRENT_ACTUAL.json':a_path,'E1_G3_FORMAL_FINAL_ACTUAL_REVIEW.json':R/'FORMAL_CLOSEOUT_ACTUAL_VERIFIED.json','E1_G3_127_CANDIDATE_CURRENT_COLLECTION.json':collected}
  with c.open_sftp() as f:
   for name,p in files.items():
    raw=p.read_bytes()
    with f.open(E+'/reports/'+name,'wbx') as out:out.write(raw)
    assert f.open(E+'/reports/'+name).read()==raw
  code=r'''from pathlib import Path
import json,time,hashlib,os
R=Path(REPORTS_VALUE);j=lambda p:json.loads(p.read_bytes());H=lambda b:hashlib.sha256(b).hexdigest()
protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md')};assert H(protected['MOD4_MOE_MASTER_PLAN.md'])=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
report=j(R/'E1_G3_FORMAL_FINAL_ACTUAL_REVIEW.json');p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);event=v['E1_G3_short_observation_execution_event'];event.update(own_formal_final=str(R/'E1_G3_OWN_FORMAL_CPU_SOURCE_VERIFIED.json'),actual_final_review=str(R/'E1_G3_FORMAL_FINAL_ACTUAL_REVIEW.json'),current_actual=str(R/'E1_G3_FORMAL_FINAL_CURRENT_ACTUAL.json'),actual_review_boundary=report['phase'],formal_own_fullsave_verified=True,original_parent_guardian_child_exited=True,active_segment_empty_at_actual=True,candidate127_actual=str(R/'E1_G3_127_CANDIDATE_CURRENT_COLLECTION.json'),no_auto_more_PPO_without_actual127_complete_review=True,not_full_E1_RM_graduation=True,new_budget_seconds=0)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert p.read_bytes()==before;tmp=p.with_name(p.name+'.G3FormalCloseout-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,p)
hp=R/'LATEST_HANDOFF.md';old=hp.read_bytes();marker='E1 G3 actual formal closeout20261010:';assert marker.encode() not in old
message=chr(10)*2+marker+' Own formal model/source338/CPU96/actual source snapshot/PIDreceipt/PASSED and one original parent budget segment verified; all parent guardian child exited and noactive legal review boundary. Four127 cases auto published to healthy frozen3060 worker; actual127 complete matched terrain/flat/spin/world review required before any further PPO. Fullsave is not all35mm route completion, permanent anti-forgetting or fullE1/RM graduation. Actual final/current collection and all prior125/package/byte-receipt/retention false/raw/cost retained. New reports and receipts must be Git supplemented; master/RM003002001/clock/allDR/hardware/S8/gate/pause93-94/MuJoCo constraints and canonical828000/new0 unchanged. Original controller remains closed, do not rerun once/main/resume, nativeSDK/PPO/clock/budget tail. ACTIVE every2h healthy/pending quiet.'+chr(10)
assert hp.read_bytes()==old;tmp=hp.with_name(hp.name+'.G3FormalCloseout-'+str(time.time_ns()));tmp.write_bytes(old+message.encode());os.replace(tmp,hp)
assert all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),actual_formal_final_metadata_synced=True,current_before_SHA=H(before),current_after_SHA=H(raw),master_approval_tracks_bytes_preserved=True,no_training_budget_or_queue_mutation=True)))
'''.replace('REPORTS_VALUE',repr(E+'/reports'))
  compile(code,'<G3FormalCloseout>','exec');_,out,err=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=out.read();errors=err.read();assert out.channel.recv_exit_status()==0,(raw+errors).decode(errors='replace');receipt=json.loads(raw)
  receipt['files']=[dict(name=n,bytes=p.stat().st_size,sha256=H(p.read_bytes())) for n,p in files.items()];save('FORMAL_CLOSEOUT_METADATA_SYNCED.json',receipt)
  with c.open_sftp() as f:
   raw=(R/'FORMAL_CLOSEOUT_METADATA_SYNCED.json').read_bytes()
   with f.open(E+'/reports/E1_G3_FORMAL_CLOSEOUT_METADATA_SYNCED.json','wbx') as out:out.write(raw)
   assert f.open(E+'/reports/E1_G3_FORMAL_CLOSEOUT_METADATA_SYNCED.json').read()==raw
  print(json.dumps(dict(phase=summary['phase'],checkpoint=passed['checkpoint'],updates=passed['actual_updates'],envsteps=passed['actual_environment_steps'],callbacks=health['actual_physics_callbacks'],ordinary=health['ordinary_episode_reset_events'],closure_mm=health['max_closure_error_m']*1000,actual_charged_seconds=summary['actual_charged_seconds'],remaining=summary['canonical_remaining'],metadata_synced=True,case127_complete=list(review['cases']),case127_pending=review['pending'])))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)

if __name__=='__main__':
 try:main()
 except Exception:
  save('FORMAL_CLOSEOUT_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_blind_repeat=True));raise
