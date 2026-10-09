"""Synchronize new actual G2 closeout evidence at the verified saved boundary; no runtime/budget write."""
from pathlib import Path
import os,sys,json,time,hashlib,shlex,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_G2_REVIEWED_20261010';ER='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports'
def main():
 assert not (R/'SYNC_STARTED.json').exists();(R/'SYNC_STARTED.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-ACTUAL-CLOSEOUT-METADATA-01')),encoding='utf8')
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  files={'E1_G2_FULL_CONTRACT_SHORT_OBSERVATION_REVIEW.json':R/'STAGE_REVIEW.json','E1_G2_FULL_CONTRACT_SHORT_OBSERVATION_REPORT.md':R/'REPORT.md','SELECTED_E1_G2_REVIEWED_SOURCE.json':R/'SELECTED_E1_G2_SOURCE.json','NEXT_G2_SHORT_OBSERVATION_REVIEW_WORK_ORDER.md':R/'NEXT_G2_SHORT_OBSERVATION_REVIEW_WORK_ORDER.md','E1_G2_FULL_CONTRACT_CURRENT_ACTUAL.json':sorted(R.glob('G2_ACTUAL_*.json'))[-1],'E1_G2_OWN_FINAL_CPU_SOURCE_VERIFIED.json':sorted(R.glob('G2_OWN_SAVE_ACTUAL_*.json'))[-1],'E1_G2_CANDIDATE_PARTIAL_BEHAVIOR_ACTUAL_REVIEW.json':sorted(R.glob('OBSERVATION_123_REVIEW_*.json'))[-1],'E1_G2_CANDIDATE_EVALUATOR_CURRENT_ACTUAL.json':sorted(R.glob('OBSERVATION_123_COLLECTED_*.json'))[-1]}
  with c.open_sftp() as f:
   for name,p in files.items():
    b=p.read_bytes()
    with f.open(ER+'/'+name,'wbx') as o:o.write(b)
    assert f.open(ER+'/'+name).read()==b
  code=r'''from pathlib import Path
import json,os,time,hashlib
R=Path(ER);D=Path(ROOT);j=lambda p:json.loads(p.read_bytes());H=lambda b:hashlib.sha256(b).hexdigest()
state=j(D/'reports/E1_STATE.json');own=j(D/'reports/e1_G2_reviewed_observation_PASSED.json');guardian=j(D/'reports/E1_GUARDIAN_STARTED.json');assert state['phase']=='E1_G2_reviewed_saved_review_ready' and state['child'] is None
def gone(row):
 p=Path('/proc')/str(row['pid'])
 if not p.exists():return True
 s=(p/'stat').read_text().split(') ',1)[1].split();return s[0]=='Z' or int(s[19])!=row['start_ticks']
assert gone(state['owner']) and gone(guardian) and gone(dict(pid=own['own_PID_bound_receipt']['pid'],start_ticks=72362884))
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');budget=B.read_bytes();ledger=json.loads(budget);assert ledger['active_segment'] is None and ledger['authorized_training_seconds']==828000
assert len([x for x in ledger['completed_segments'] if x['pid']==own['own_PID_bound_receipt']['pid']])==1
protected={name:(R/name).read_bytes() for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md')};assert H(protected['MOD4_MOE_MASTER_PLAN.md'])=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
vfy=j(R/'E1_G2_OWN_FINAL_CPU_SOURCE_VERIFIED.json');assert vfy['formal_saved'][0]['checkpoint']['sha256']==own['checkpoint']['sha256'] and vfy['formal_saved'][0]['snapshot_count']==62
P=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=P.read_bytes();v=json.loads(before);v['previous_G1_to_G2_cached_snapshot_retained']={k:v.get(k) for k in ('epoch','actual_phase','parent','guardian','trainer','active_log','deadline_epoch','run','own_current_save','live_health')}
v.update(epoch=time.time(),actual_phase=state['phase'],parent=None,guardian=None,trainer=None,active_log=None,deadline_epoch=None,own_current_save=own['checkpoint'],own_snapshot_count=62,live_health=own['health'],live_health_is_not_final=False,new_budget_seconds=0)
v['E1_G2_full_contract_short_observation_execution_event']=dict(root=str(D),source_count=329,review=str(R/'E1_G2_FULL_CONTRACT_SHORT_OBSERVATION_REVIEW.json'),report=str(R/'E1_G2_FULL_CONTRACT_SHORT_OBSERVATION_REPORT.md'),actual=str(R/'E1_G2_FULL_CONTRACT_CURRENT_ACTUAL.json'),selected_source=str(R/'SELECTED_E1_G2_REVIEWED_SOURCE.json'),next_work_order=str(R/'NEXT_G2_SHORT_OBSERVATION_REVIEW_WORK_ORDER.md'),candidate_partial_behavior=str(R/'E1_G2_CANDIDATE_PARTIAL_BEHAVIOR_ACTUAL_REVIEW.json'),candidate_behavior_review_pending=True,no_auto_more_PPO_before_review=True,source32098_not_selected=True,permanent_anti_forgetting_not_claimed=True)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert P.read_bytes()==before;tmp=P.with_name(P.name+'.G2-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,P)
handoff=R/'LATEST_HANDOFF.md';hb=handoff.read_bytes();marker='E1 G2 reviewed20mm short observation actual closeout20261010:';assert marker.encode() not in hb
append=('\n\n'+marker+' root329/original321 exact/new8, actual CPU14/SDK10/native20k and fullPPO128x2/20kx4 discarded unique ledger passed; formal32058/42cdc9d24519778a9da3e35b05a3eb3bb5745760c26a5842c78fcde2bd39e53b CPU96/snapshot62/PID1866058,6updates/2.88Msteps/576callbacks/ordinary0/integrity0/nonfinitefalse/closure.823352mm. ExplicitG0_to_G2/new physical episode after full old streams; not PhysX exactresume. Parentguardianchild natural exit/noactive unique315.180510s settled, legal review boundary. Four123 candidate cases published and current3060 healthy; partial flat paired errors negative.024461027/positive.043439623 close to32053, remaining terrain/spin/world pending, no automatic furtherPPO before actual complete review. Read stage reports/workorder; preserve current actual not stale active claim. MainSHA/RM003/002/001/exclusions/budget828000 unchanged/new0, all new saved reports and reader KeyError retained Git including later completion.\n').encode();assert handoff.read_bytes()==hb;tmp=handoff.with_name(handoff.name+'.G2-'+str(time.time_ns()));tmp.write_bytes(hb+append);os.replace(tmp,handoff)
assert B.read_bytes()==budget and all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),central_new_evidence_roundtrip=True,master_approval_tracks_RM_and_canonical_bytes_preserved=True,actual_saved_boundary_verified=True,actual_phase=state['phase'],current_before_sha256=H(before),current_after_sha256=H(raw),remaining_seconds=ledger['authorized_training_seconds']-ledger['charged_training_seconds'],candidate_behavior_still_pending=True,no_GPU_PPO_runtime_or_budget_write=True)))
'''.replace('Path(ER)','Path('+repr(ER)+')').replace('Path(ROOT)','Path('+repr(ROOT)+')')
  _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');proof=json.loads(raw);proof['files']=[dict(name=n,bytes=p.stat().st_size,sha256=H(p.read_bytes())) for n,p in files.items()]
  (R/'METADATA_SYNCED.json').write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(proof))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:
  (R/'SYNC_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-ACTUAL-CLOSEOUT-METADATA-01',error=traceback.format_exc(),no_blind_repeat=True),indent=2),encoding='utf8');raise
