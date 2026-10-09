"""Append reviewed evidence and update only actual current-stage pointers with CAS."""
from pathlib import Path
import os,sys,json,hashlib,shlex,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';sha=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports'
def main():
 assert not (R/'METADATA_SYNC_STARTED.json').exists();(R/'METADATA_SYNC_STARTED.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G1-REPAIR-METADATA-01')),encoding='utf8')
 actual=json.loads(sorted(R.glob('G1_ACTUAL_*.json'))[-1].read_text());assert actual['reports'].get('E1_ATTENTION.json') is None
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  payload={'E1_GENTLE_BLOCK2_MATCHED_ACTUAL_REVIEW.json':(D/'block2/REVIEW.json').read_bytes(),'E1_RETENTION_ROLLBACK_G1_REPAIR_REVIEW.json':(R/'REPAIR_REVIEW.json').read_bytes(),'E1_RETENTION_ROLLBACK_G1_REPAIR_REPORT.md':(R/'REPORT.md').read_bytes(),'SELECTED_E1_RETENTION_REPAIR_SOURCE.json':(R/'SELECTED_E1_REPAIR_SOURCE.json').read_bytes(),'E1_G1_REPAIR_CURRENT_ACTUAL.json':sorted(R.glob('G1_ACTUAL_*.json'))[-1].read_bytes()}
  with c.open_sftp() as sf:
   indexed=[]
   for name,b in payload.items():
    with sf.open(E+'/'+name,'wbx') as out:out.write(b)
    assert sha(sf.open(E+'/'+name).read())==sha(b);indexed.append(dict(name=name,bytes=len(b),sha256=sha(b)))
  code="""from pathlib import Path
import json,hashlib,time,os
R=Path(E);sha=lambda b:hashlib.sha256(b).hexdigest()
protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json')}
master=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/MOD4_MOE_MASTER_PLAN.md')
if master.exists():assert sha(master.read_bytes())=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);a=json.loads((R/'E1_G1_REPAIR_CURRENT_ACTUAL.json').read_text());s=a['reports']['E1_STATE.json'];r=a['runs'];saved=a['reports'].get('E1_CURRENT_SAVE.json');sel=json.loads((R/'SELECTED_E1_RETENTION_REPAIR_SOURCE.json').read_text())
v['previous_E1_G0_stable_cached_snapshot_retained']={k:v.get(k) for k in ('epoch','root','source_count','actual_phase','parent','guardian','trainer','source','active_log','deadline_epoch','run','own_current_save','own_PID_bound_receipt','live_health')}
v.update(epoch=a['epoch'],root=a['root'],source_count=321,actual_phase=s['phase'],plan_stage='S3 independent E1 rollback32053 and003 G1 derived10mm bounded repair',parent=a['actual']['owner'],guardian=a['actual']['guardian'],trainer=a['actual']['child'],source=sel['source'],active_log=s.get('active_log'),deadline_epoch=s.get('deadline_epoch'),run=saved.get('own_run') if saved else None,own_current_save=saved,own_PID_bound_receipt=saved.get('receipt') if saved else None,own_snapshot_count=None,actual_PPO_log_count=None,live_health=a['reports'].get('E1_ACTIVE_HEALTH.json'),live_health_is_not_final=True,new_budget_seconds=0)
v['E1_persistent_retention_regression_and_bounded_repair']=dict(review=str(R/'E1_RETENTION_ROLLBACK_G1_REPAIR_REVIEW.json'),actual=str(R/'E1_G1_REPAIR_CURRENT_ACTUAL.json'),selected_source=str(R/'SELECTED_E1_RETENTION_REPAIR_SOURCE.json'),no_third_unchanged_G0_block=True,first_observation_s=900,no_auto_more_PPO_before_behavior_review=True,G1_behavior_pending=True)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert p.read_bytes()==before
tmp=p.with_name(p.name+'.g1-repair-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,p);assert p.read_bytes()==raw
handoff=R/'LATEST_HANDOFF.md';hb=handoff.read_bytes();append=(chr(10)+chr(10)+'Human-requested E1 repair: both G0 stable blocks naturally completed and uniquely settled; block2 inherited world14/64 and negative4pi0/8, flat env38 reset and original task admission false retained. Earlier balanced complete E1 model32053 SHA655a36b7 selected for independent321-source G1 derived10mm repair, first observation900s, original313 byteexact and all clock/DR/hardware/budget unchanged. Read E1_RETENTION_ROLLBACK_G1_REPAIR_REVIEW/REPORT and E1_G1_REPAIR_CURRENT_ACTUAL; actual/proc/ownreceipts precede cached pointers. NewG1 terrain and old-skill behavior pending; no further automatic PPO before review, no quota scheme, no RM graduation, no optional93/94 revival.003/002 and001 valid exclusions retained; all reports must Git.'+chr(10)).encode()
assert b'Human-requested E1 repair: both G0' not in hb and handoff.read_bytes()==hb
tmp=handoff.with_name(handoff.name+'.g1-repair-'+str(time.time_ns()));tmp.write_bytes(hb+append);os.replace(tmp,handoff);assert handoff.read_bytes()==hb+append
assert all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),current_before_sha256=sha(before),current_after_sha256=sha(raw),handoff_append_exact=True,approval_tracks_bytes_unchanged=True,RM_annotations_preserved=True,actual_phase=s['phase'],central_evidence_roundtrip=True,no_runtime_GPU_PPO_or_canonical_mutation=True)))
""".replace('Path(E)', 'Path('+repr(E)+')')
  _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);b=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(b+err).decode(errors='replace')
  proof=json.loads(b);proof['files']=indexed;(R/'METADATA_SYNCED.json').write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(proof))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:
  (R/'METADATA_FIRST_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G1-REPAIR-METADATA-01',error=traceback.format_exc(),no_blind_repeat=True),indent=2),encoding='utf8');raise
