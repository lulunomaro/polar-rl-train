"""Append actual125 pre-GPU refusal and separately admitted126; metadata only."""
from pathlib import Path
import hashlib,json,os,sys,shlex,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';B='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode())
def main():
 save('REPAIR126_SYNC_STARTED.json',dict(epoch=time.time(),trial_id='E1-G3-35MM-126-METADATA-SYNC-04',once=True))
 published=json.loads((R/'REPAIRED_PUBLISHED.json').read_bytes());assert '126-e1-g3' in published['jobs'][0]['job_id'] and published['canonical_bytes_preserved']
 admitted=json.loads((R/'E1_G3_PACKAGE_REVIEW_WORKER_ADMITTED.json').read_bytes());assert admitted['admission']['old_worker_and_children_exited'] and admitted['admission']['shared_GPU_lock_was_free']
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  files={'E1_G3_35MM_125_PACKAGE_REJECTION_REVIEW.json':R/'PACKAGE_REJECTION_REVIEW.json','E1_G3_35MM_WORKER_BYTE_RECEIPT_REJECTION_REVIEW.json':R/'WORKER_BYTE_RECEIPT_REJECTION_REVIEW.json','E1_G3_35MM_REPAIRED_PREPARED.json':R/'REPAIRED_PREPARED.json','E1_G3_35MM_126_REPAIRED_PUBLISHED.json':R/'REPAIRED_PUBLISHED.json','E1_G3_PACKAGE_REVIEW_WORKER_ADMISSION_ACTUAL.json':R/'E1_G3_PACKAGE_REVIEW_WORKER_ADMITTED.json'}
  with c.open_sftp() as f:
   for n,p in files.items():
    b=p.read_bytes()
    with f.open(E+'/reports/'+n,'wbx') as o:o.write(b)
    assert f.open(E+'/reports/'+n).read()==b
  code=r'''from pathlib import Path
import hashlib,json,time,os
R=Path(REPORTS);B=Path(BUDGET);j=lambda p:json.loads(p.read_bytes());H=lambda b:hashlib.sha256(b).hexdigest();budget=B.read_bytes();assert j(B)['active_segment'] is None and j(B)['authorized_training_seconds']==828000
protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md')};assert H(protected['MOD4_MOE_MASTER_PLAN.md'])=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json'):assert b'MOD4-RM-TERRAIN-CURRICULUM-REVISION-003' in protected[n] and b'MOD4-RM-OUTER-CURB-AND-ROUGH-GEOMETRY-CLARIFICATION-002' in protected[n]
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);assert v['actual_phase']=='E1_G2_matched_continuation_saved_review_ready';scope=v['next_E1_G3_frozen_scope'];old=dict(scope)
scope.update(epoch=time.time(),previous125_preGPU_rejection=str(R/'E1_G3_35MM_125_PACKAGE_REJECTION_REVIEW.json'),worker_byte_receipt_pre_admission_rejection=str(R/'E1_G3_35MM_WORKER_BYTE_RECEIPT_REJECTION_REVIEW.json'),prepared=str(R/'E1_G3_35MM_REPAIRED_PREPARED.json'),published=str(R/'E1_G3_35MM_126_REPAIRED_PUBLISHED.json'),worker_admission=str(R/'E1_G3_PACKAGE_REVIEW_WORKER_ADMISSION_ACTUAL.json'),actual_result_pending=True,no_G3_learning_executor_deployed=True,no_auto_more_PPO=True,new_budget_seconds=0)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert p.read_bytes()==before;tmp=p.with_name(p.name+'.G3repair126-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,p)
hp=R/'LATEST_HANDOFF.md';hb=hp.read_bytes();marker='E1 G3 immutable manifest repair126 actual20261010:';assert marker.encode() not in hb
text=chr(10)*2+marker+' 125 refused before GPU/PhysX/PPO at immutable file map SHA check, original source/zip/job/attention unchanged; not physical failure or35mm pass. New v2 package keeps all member bytes except explicit SOURCE_MANIFEST, indexes actual approved35mm dispatcher and2 new geometry files; all281 file maps independently SHA exact. First new worker admission rejected before process/lock/task changes because LF-text receipt versus delivered CRLF bytes; exact-byte independently repaired receipt preserved old error. Old artifactsource worker/children actually exited, sharedlock free, original demandtask disabled only after boundary. New E1_G3_PACKAGE_REVIEW demandonly task/no periodic or boot trigger, namespace+exact125 exclusion only, baseguard/bridge/lock/retry unchanged. New126 from selected32058 permitted SHA42cdc9d24519778a9da3e35b05a3eb3bb5745760c26a5842c78fcde2bd39e53b actually published; result pending, no4090GPU/PPO or learningexecutor. Current330 closed32103 unique920.422999s and124 complete49of64 retention tradeoff remains; no more blind20mm PPO. Next actual126 complete/full raw/support/contact review and trulynew35mm contracts before bounded learning; old protocols/clock exactSHA reuse. All reports and original refusals require Git, later results supplements. Master/RM003002001, canonical828000/new0, paused93-94, MuJoCo ended/S8 future specific approval unchanged.'+chr(10)
assert hp.read_bytes()==hb;tmp=hp.with_name(hp.name+'.G3repair126-'+str(time.time_ns()));tmp.write_bytes(hb+text.encode());os.replace(tmp,hp)
assert B.read_bytes()==budget and all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),metadata_updated=True,previous_scope_snapshot=old,master_approval_tracks_RM_canonical_bytes_preserved=True,no_4090_GPU_PPO_or_canonical_write=True,original125_rejection_retained=True,actual126_behavior_pending=True,current_before_sha256=H(before),current_after_sha256=H(raw),new_budget_seconds=0)))
'''.replace('REPORTS',repr(E+'/reports')).replace('BUDGET',repr(B))
  compile(code,'<G3-repair126-metadata>','exec');_,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);out=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(out+err).decode(errors='replace');proof=json.loads(out)
  proof['files']=[dict(name=n,bytes=p.stat().st_size,sha256=H(p.read_bytes())) for n,p in files.items()];save('REPAIR126_METADATA_SYNCED.json',proof)
  with c.open_sftp() as f:
   b=(R/'REPAIR126_METADATA_SYNCED.json').read_bytes()
   with f.open(E+'/reports/E1_G3_35MM_126_REPAIR_METADATA_SYNCED.json','wbx') as o:o.write(b)
   assert f.open(E+'/reports/E1_G3_35MM_126_REPAIR_METADATA_SYNCED.json').read()==b
  print(json.dumps(dict(metadata_synced=True,original125_rejection_preserved=True,actual126_pending=True,new_budget_seconds=0)))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:
  save('REPAIR126_SYNC_ERROR.json',dict(epoch=time.time(),trial_id='E1-G3-35MM-126-METADATA-SYNC-04',error=traceback.format_exc(),do_not_repeat_once=True));raise
