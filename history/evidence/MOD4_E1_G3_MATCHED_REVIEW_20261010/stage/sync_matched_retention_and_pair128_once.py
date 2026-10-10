"""New127complete/SCUT/128 metadata transaction only. No old sync or training replay."""
from pathlib import Path
import hashlib,json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';B='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode())
def main():
 save('MATCHED_RETENTION_SYNC_STARTED.json',dict(epoch=time.time(),trial_id='E1-G3-127-SCUT-128-METADATA-01',once=True,metadata_only=True))
 files={
 'E1_G3_127_COMPLETE_MATCHED_ACTUAL_REVIEW.json':W/'MOD4_E1_G3_LEARNING_PREPARE_20261010/reports/CANDIDATE_127_REVIEW_1791592441.json',
 'E1_G3_127_PREFIX_RETENTION_DECISION.json':R/'PAIRED_PREFIX_RETENTION_DIAGNOSIS.json',
 'SCUT_E1_RETENTION_ACTUAL_SOURCE_AUDIT.json':R/'SCUT_SOURCE_AUDIT_1791633510.json',
 'SCUT_E1_RETENTION_MATCHED_FINDINGS.json':R/'SCUT_RETENTION_FINDINGS.json',
 'SCUT_E1_RETENTION_DETAILED_REVIEW.md':R/'SCUT_RETENTION_DETAILED_REVIEW.md',
 'E1_G3_128_PAIRED_APPROACH_PUBLISHED.json':R/'PAIRED_APPROACH_PUBLISHED.json',
 'E1_G3_128_ACTUAL_CURRENT_COLLECTION.json':sorted(R.glob('G3_128_COLLECTED_*.json'))[-1],
 'E1_G3_RETAINED_FLAT_COMMAND_CPU_CANDIDATE.json':R/'RETAINED_FLAT_COMMAND_CPU_REVIEW.json',
 'E1_G3_FLAT_COMMAND_CPU_NAMED_RNG_DISK_VERIFIED.json':R/'FLAT_CPU_NAMED_GENERATOR_DISK_VERIFIED.json',
 'NEXT_E1_G3_RETENTION_REPAIR_WORK_ORDER.json':R/'NEXT_E1_G3_RETENTION_REPAIR_WORK_ORDER.json',
 'NEXT_E1_G3_RETENTION_REPAIR_WORK_ORDER.md':R/'NEXT_E1_G3_RETENTION_REPAIR_WORK_ORDER.md'}
 review=json.loads(files['E1_G3_127_COMPLETE_MATCHED_ACTUAL_REVIEW.json'].read_bytes());assert review['review_complete'] and not review['pending']
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  with c.open_sftp() as f:
   budget=f.open(B).read();ledger=json.loads(budget);assert ledger['active_segment'] is None and ledger['authorized_training_seconds']==828000
   for n,p in files.items():
    raw=p.read_bytes()
    with f.open(E+'/reports/'+n,'wbx') as out:out.write(raw)
    assert f.open(E+'/reports/'+n).read()==raw
  code=r'''from pathlib import Path
import hashlib,json,time,os
R=Path(REPORTS);B=Path(BUDGET);H=lambda b:hashlib.sha256(b).hexdigest();j=lambda p:json.loads(p.read_bytes())
protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')}
assert H(protected['MOD4_MOE_MASTER_PLAN.md'])=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
budget=B.read_bytes();assert H(budget)==EXPECTED_BUDGET_SHA and j(B)['active_segment'] is None
review=j(R/'E1_G3_127_COMPLETE_MATCHED_ACTUAL_REVIEW.json');assert review['review_complete'] and not review['pending']
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before)
event=v['E1_G3_short_observation_execution_event'];event.update(actual127_complete_review=str(R/'E1_G3_127_COMPLETE_MATCHED_ACTUAL_REVIEW.json'),actual127_retention_decision=str(R/'E1_G3_127_PREFIX_RETENTION_DECISION.json'),candidate32063_not_blind_learning_source=True,not_advance50mm_from_this_candidate=True,SCUT_retention_source_audit=str(R/'SCUT_E1_RETENTION_MATCHED_FINDINGS.json'),next_paired128=str(R/'E1_G3_128_PAIRED_APPROACH_PUBLISHED.json'),current_paired128=str(R/'E1_G3_128_ACTUAL_CURRENT_COLLECTION.json'),next_retention_work_order=str(R/'NEXT_E1_G3_RETENTION_REPAIR_WORK_ORDER.json'),new_command_CPU_candidate_only=str(R/'E1_G3_RETAINED_FLAT_COMMAND_CPU_CANDIDATE.json'),not_permanent_anti_forgetting_or_all35mm_graduation=True,no_new_learning_launched_at_this_transaction=True,new_budget_seconds=0)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert p.read_bytes()==before;tmp=p.with_name(p.name+'.Matched127-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,p)
hp=R/'LATEST_HANDOFF.md';old=hp.read_bytes();marker='E1 G3 complete127 SCUT retention paired12820261010:';assert marker.encode() not in old
message=chr(10)*2+marker+' Actual127 complete4case/bridge bytes/fullNPZ/ground-contact-COMlink/hardware/root30q/recipes reviewed.32063 forward aftersupport13of27 versus32058 17of27; world56of64 versus62of64; negative4pi2of8 versus5of8. Preserve all oldfalse/raw/cost/prefixes; reject blind32063PPO or next50mm. New128 immutable two checkpoints approach.65to.40 only,15s/full10wave/two-wheel200mm aftersupport same; healthy worker unchanged, frozenonly/newbudget0. Read actual128 collector/reviewer; missingfuture result is pending, old127pending history. SCUT current1a263 source+July30 saved params show persistent eligible old live on-policy command modes and terrain restrictions, not proven permanent memory/MoE cure. New command-only CPU sampler prepared: existingplane family only signed straight/world yaw1-2,nonflatgentleyaw0,physical clearance/SDK/native/fullresume/PPO new scope admission still required before bounded300s repair; no old once/main/resume/clock replay. Master/RM003002001/E0freeze/828000sixextensions/S3otherexperts-gate-protection/S8laterapproval/gateuntrained/paused93-94/MuJoCoended unchanged. All new reports, rejections, readers, sync and saved monitoring receipts requireGit; ACTIVEevery2h healthypendingquiet.'+chr(10)
assert hp.read_bytes()==old;tmp=hp.with_name(hp.name+'.Matched127-'+str(time.time_ns()));tmp.write_bytes(old+message.encode());os.replace(tmp,hp)
assert B.read_bytes()==budget and all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),current_before_SHA=H(before),current_after_SHA=H(raw),master_approval_tracks_RM_bytes_preserved=True,canonical_bytes_preserved=True,no_GPU_queue_or_budget_write=True,actual127_complete_synced=True,pair128_published_not_learning=True)))
'''.replace('REPORTS',repr(E+'/reports')).replace('EXPECTED_BUDGET_SHA',repr(H(budget))).replace('BUDGET',repr(B))
  compile(code,'<matched127Sync>','exec');_,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');receipt=json.loads(raw)
  receipt['files']=[dict(name=n,bytes=p.stat().st_size,sha256=H(p.read_bytes())) for n,p in files.items()];save('MATCHED_RETENTION_METADATA_SYNCED.json',receipt)
  with c.open_sftp() as f:
   raw=(R/'MATCHED_RETENTION_METADATA_SYNCED.json').read_bytes()
   with f.open(E+'/reports/E1_G3_127_S CUT_128_METADATA_SYNCED.json'.replace('S CUT','SCUT'),'wbx') as out:out.write(raw)
   assert f.open(E+'/reports/E1_G3_127_SCUT_128_METADATA_SYNCED.json').read()==raw
  print(json.dumps(dict(actual127_complete_synced=True,master_RM_canonical_preserved=True,new_budget_seconds=0)))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:
  save('MATCHED_RETENTION_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_repeat_executed_transaction=True));raise
