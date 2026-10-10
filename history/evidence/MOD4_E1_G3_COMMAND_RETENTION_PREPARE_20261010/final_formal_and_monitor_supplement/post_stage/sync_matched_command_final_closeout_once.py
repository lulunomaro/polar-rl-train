"""New365 actual fullsave/final closeout metadata; no ledger reaccounting or restart."""
from pathlib import Path
import hashlib,json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';NEW='/home/egde/rl_candidates/MOD4_S3_E1_G3_COMMAND_RETENTION_MATCHED_20261010'
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,indent=2).encode());return p
def main():
 actual=sorted(R.glob('COMMAND_MATCHED_ACTUAL_[0-9]*.json'))[-1];own=sorted(R.glob('COMMAND_MATCHED_OWN_CPU_[0-9]*.json'))[-1]
 a=json.loads(actual.read_bytes());cpu=json.loads(own.read_bytes());p=a['reports']['e1_G3_command_retention_matched_PASSED.json'];h=p['health']
 assert a['actual']==[None,None,None] and a['canonical']['active'] is None and cpu['saved'][0]['final_PASS_and_unique_segment'] and not cpu['pending']
 assert p['checkpoint']['sha256']==cpu['saved'][0]['checkpoint']['sha256']=='f5b1623e71fc5d6f3682ca19594bdf43db5a391ce9fc046ec48f8ce90dde234a'
 assert h['control_steps']==1008 and h['actual_physics_callbacks']==h['expected_physics_callbacks']==4032 and p['actual_environment_steps']==20160000 and p['actual_updates']==42
 assert h['ordinary_episode_reset_events']==h['integrity_task_reset_events']==h['unknown_task_reset_events']==0 and not h['nonfinite_observed'] and h['stop_reason'] is None and h['termination_reason_coverage_exact'] and h['truncation_reason_coverage_exact']
 assert len(p['unique_completed_segment'])==1
 proof=save('COMMAND_MATCHED_FORMAL_FINAL_ACTUAL_REVIEW.json',dict(epoch=time.time(),trial_id='E1-G3-COMMAND-MATCHED-900S-ACTUAL-CLOSEOUT-01',own_final=p,own_CPU_receipt=str(own),source365_ownfreeze_and_actual72snapshot_verified=True,actual_parent_guardian_child_all_exited=True,phase=a['reports']['E1_STATE.json']['phase'],same_G3_terrain_and_retained_command_restored_exact=True,load_learn_save_exit_unique_seconds=p['unique_completed_segment'][0]['ended_epoch']-p['unique_completed_segment'][0]['started_epoch'],ordinary_integrity_unknown_nonfinite_false_preserved=True,timeout_route_overlap_not_summed_as_unique=True,actual_unique_truncations=h['actual_truncation_reset_events'],future130_complete_behavior_before_more_PPO=True,no_permanent_anti_forgetting_E1_or_RM70mm_graduation=True,no_third_automatic_same_scope_block=True,new_budget_seconds=0))
 save('COMMAND_MATCHED_FINAL_CLOSEOUT_SYNC_STARTED.json',dict(epoch=time.time(),metadata_only=True,no_recharge_or_old_sync_replay=True))
 files={'E1_G3_COMMAND_RETENTION_MATCHED_FORMAL_FINAL_ACTUAL_REVIEW.json':proof,'E1_G3_COMMAND_RETENTION_MATCHED_OWN_FINAL_CPU_VERIFIED.json':own,'E1_G3_COMMAND_RETENTION_MATCHED_FORMAL_FINAL_CURRENT_ACTUAL.json':actual,'E1_G3_COMMAND_RETENTION_130_CURRENT_COLLECTION.json':sorted(R.glob('CANDIDATE_130_COLLECTED_[0-9]*.json'))[-1]}
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  with c.open_sftp() as f:
   for n,pth in files.items():
    raw=pth.read_bytes()
    with f.open(E+'/reports/'+n,'wbx') as out:out.write(raw)
    assert f.open(E+'/reports/'+n).read()==raw
  code=r'''from pathlib import Path
import hashlib,json,time,os,fcntl
R=Path(REPORTS);D=Path(ROOT);B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');H=lambda b:hashlib.sha256(b).hexdigest()
protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')};assert H(protected['MOD4_MOE_MASTER_PLAN.md'])=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
budget=B.read_bytes();ledger=json.loads(budget);assert ledger['active_segment'] is None and ledger['authorized_training_seconds']==828000
for lock in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with lock.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
state=json.loads((D/'reports/E1_STATE.json').read_bytes());assert state['phase']=='E1_G3_command_retention_matched_saved_review_ready' and state['child'] is None
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);event=v['E1_G3_command_retention_365_matched_execution_event'];assert 'formal_actual_closeout' not in event
event['formal_actual_closeout']=dict(epoch=time.time(),actual_phase=state['phase'],reports={n:str(R/n) for n in ['E1_G3_COMMAND_RETENTION_MATCHED_FORMAL_FINAL_ACTUAL_REVIEW.json','E1_G3_COMMAND_RETENTION_MATCHED_OWN_FINAL_CPU_VERIFIED.json','E1_G3_COMMAND_RETENTION_MATCHED_FORMAL_FINAL_CURRENT_ACTUAL.json','E1_G3_COMMAND_RETENTION_130_CURRENT_COLLECTION.json']},ownfullsave_CPU102_source365_actual72snapshot_and_unique_parent_settled=True,noactive_legal_review_boundary=True,all_courses_finished=False,actual130_behavior_required_before_more_PPO=True,new_budget_seconds=0)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert p.read_bytes()==before;tmp=p.with_name(p.name+'.MatchedFinal-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,p)
hp=R/'LATEST_HANDOFF.md';old=hp.read_bytes();marker='E1 source365 matched900s actual final saved closeout20261010:';assert marker.encode() not in old
msg=chr(10)*2+marker+' Ownmodel32104 SHA f5b1623e71fc5d6f3682ca19594bdf43db5a391ce9fc046ec48f8ce90dde234a/CPU102/source365/72snapshot/fullownfreeze/ownPID2313253/actualPASSED/unique920.4243905544281s originalparent settled;42updates1008control20.16Menvsteps4032callbacks exact,ordinary-integrity-unknown0/nonfinitefalse/STOPnone,closure1.088974532mm. SameG3 andsamecommand/privateCUDA restoredexact thenepisode1. Allactualparent/guardian/child exited/two real locksfree/noactive legal reviewboundary, nooldentry resurrection orallcoursefinished.130fourfrozen cases actually published, pendingcomplete/errorfree2hostbytes/fullNPZ and compare direct1293c97 source, old115/128/123reuse no replay; noautomaticthirdblock or50mm before completebehavior decision. Allfinal/130/sync/monitor/readerreports requireGit supplement, latestactual beats22:18active snapshot. ACTIVEevery2h healthypendingquiet.'+chr(10)
assert hp.read_bytes()==old;tmp=hp.with_name(hp.name+'.MatchedFinal-'+str(time.time_ns()));tmp.write_bytes(old+msg.encode());os.replace(tmp,hp)
assert B.read_bytes()==budget and all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),matched900s_actual_final_closeout_synced=True,canonical_master_approval_tracks_RM_bytes_preserved=True,original_parent_unique_settlement_not_repeated=True,two_real_locks_free=True,remaining_seconds=ledger['authorized_training_seconds']-ledger['charged_training_seconds'],current_before_SHA=H(before),current_after_SHA=H(raw),new_budget_seconds=0)))
'''.replace('REPORTS',repr(E+'/reports')).replace('ROOT',repr(NEW))
  compile(code,'<matchedFinalCloseout>','exec');_,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw);v['files']=[dict(name=n,bytes=pth.stat().st_size,sha256=H(pth.read_bytes())) for n,pth in files.items()];receipt=save('COMMAND_MATCHED_FINAL_CLOSEOUT_METADATA_SYNCED.json',v)
  with c.open_sftp() as f:
   raw=receipt.read_bytes()
   with f.open(E+'/reports/E1_G3_COMMAND_RETENTION_MATCHED_FINAL_CLOSEOUT_METADATA_SYNCED.json','wbx') as out:out.write(raw)
   assert f.open(E+'/reports/E1_G3_COMMAND_RETENTION_MATCHED_FINAL_CLOSEOUT_METADATA_SYNCED.json').read()==raw
  print(json.dumps(dict(matched900s_final_synced=True,remaining=v['remaining_seconds'],new_budget_seconds=0)))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:save('COMMAND_MATCHED_FINAL_CLOSEOUT_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_repeat_completed_sync_or_ledger_transaction=True));raise
