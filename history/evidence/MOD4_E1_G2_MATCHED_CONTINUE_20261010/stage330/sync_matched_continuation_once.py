"""Publish complete123 review and actual330 entry metadata without runtime/budget transactions."""
from pathlib import Path
import os,sys,json,time,hashlib,shlex,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_G2_MATCHED_CONTINUE_20261010';ER='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports'
def main():
    assert not (R/'SYNC_STARTED.json').exists();(R/'SYNC_STARTED.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-MATCHED-CONTINUATION-METADATA-01')),encoding='utf8')
    secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
    try:
        files={'E1_G2_MODEL32058_COMPLETE_MATCHED_REVIEW.json':R/'MATCHED_123_REVIEW.json','SELECTED_E1_G2_MATCHED_CONTINUATION_SOURCE.json':R/'SELECTED_E1_G2_MATCHED_CONTINUATION_SOURCE.json','E1_G2_MATCHED_CONTINUATION_REPORT.md':R/'REPORT.md','NEXT_G2_MATCHED_CONTINUATION_REVIEW_WORK_ORDER.md':R/'NEXT_G2_MATCHED_CONTINUATION_REVIEW_WORK_ORDER.md','E1_G2_MATCHED_CONTINUATION_CURRENT_ACTUAL.json':sorted(R.glob('MATCHED_ACTUAL_*.json'))[-1]}
        with c.open_sftp() as f:
            for name,p in files.items():
                b=p.read_bytes()
                with f.open(ER+'/'+name,'wbx') as out:out.write(b)
                assert f.open(ER+'/'+name).read()==b
        code="""from pathlib import Path
import json,hashlib,time,os
R=Path(ER);D=Path(ROOT);j=lambda p:json.loads(p.read_bytes());H=lambda b:hashlib.sha256(b).hexdigest()
state=j(D/'reports/E1_STATE.json');assert state['phase'] in ('bounded_E1_G2_retention_repair_learning','E1_G2_matched_continuation_saved_review_ready')
def actual(row):
 if not row:return None
 p=Path('/proc')/str(row['pid'])
 if not p.exists():return None
 s=(p/'stat').read_text().split(') ',1)[1].split();v=dict(row,state=s[0],start_ticks=int(s[19]),cwd=os.readlink(p/'cwd'),argv=(p/'cmdline').read_bytes().decode().split('\\0'))
 assert v['start_ticks']==row['start_ticks'];return v
owner=actual(state['owner']);child=actual(state.get('child'));guardian=actual(j(D/'reports/E1_GUARDIAN_STARTED.json'))
if child:assert str(D/'isaac/mod4/train_e1_g2_reviewed_resume_ppo.py') in child['argv'] and child['state']!='Z'
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');ledger=j(B);assert ledger['authorized_training_seconds']==828000
if child:assert ledger['active_segment']['pid']==child['pid']
else:assert ledger['active_segment'] is None
protected={name:(R/name).read_bytes() for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md')};assert H(protected['MOD4_MOE_MASTER_PLAN.md'])=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
review=j(R/'E1_G2_MODEL32058_COMPLETE_MATCHED_REVIEW.json');assert review['review_complete'] and not review['pending']
P=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=P.read_bytes();v=json.loads(before);v['previous_G2_first_short_closeout_actual_retained']={k:v.get(k) for k in ('epoch','actual_phase','parent','guardian','trainer','active_log','deadline_epoch','run','own_current_save','live_health')}
current=j(D/'reports/E1_CURRENT_SAVE.json') if (D/'reports/E1_CURRENT_SAVE.json').exists() else None
health=j(D/'reports/E1_ACTIVE_HEALTH.json') if (D/'reports/E1_ACTIVE_HEALTH.json').exists() else None
v.update(epoch=time.time(),actual_phase=state['phase'],parent=owner,guardian=guardian,trainer=child,active_log=state.get('active_log'),deadline_epoch=state.get('deadline_epoch'),own_current_save=current,live_health=health,live_health_is_not_final=child is not None,new_budget_seconds=0)
v['E1_G2_matched_continuation_execution_event']=dict(root=str(D),source_count=330,source32058_behavior_review_complete=True,complete_review=str(R/'E1_G2_MODEL32058_COMPLETE_MATCHED_REVIEW.json'),selected_source=str(R/'SELECTED_E1_G2_MATCHED_CONTINUATION_SOURCE.json'),current=str(R/'E1_G2_MATCHED_CONTINUATION_CURRENT_ACTUAL.json'),next_work_order=str(R/'NEXT_G2_MATCHED_CONTINUATION_REVIEW_WORK_ORDER.md'),same_geometry_observation_seconds=900,no_automatic_more_PPO_before_new124_review=True,permanent_anti_forgetting_not_claimed=True)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert P.read_bytes()==before;tmp=P.with_name(P.name+'.G2matched-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,P)
hp=R/'LATEST_HANDOFF.md';hb=hp.read_bytes();marker='E1 G2 matched32058 same20mm900s continuation20261010:';assert marker.encode() not in hb
append=('\n\n'+marker+' 123 four cases complete/errorfree: full20mm route forward27/27 reverse26/27/stand26 ordinary0 with incomplete after-support prefix retained; flat negative/positive errors.024461027/.043439623; pure+4pi8/8 negative5/8 unchanged; world63/64 to62/64/cross.053276684 small residual retained, no old major collapse but not permanent anti-forgetting/E1/RMgraduation. Complete paired selected32058/42cdc9d2 CPU96/source329/snapshot62, one isolated330 root original329 byteexact/newcontroller only, parent1873629 guardian1873662 child1873663 locators only. Same-G2 fullrestore then fresh episode, actual startup required, no repeated CPU/SDK/native/PPO preflight/clock. Formal900s includes load-save-exit;124fourcases auto after ownfullsave then savedreviewready/noactive legal; no morePPO before actual complete review. Read newworkorder and current actual not prioridle/source32053. Master/RM003/002/001/budget828000 unchanged new0; all failures/raw/costs/reports Git including newlater receipts.\n').encode();assert hp.read_bytes()==hb;tmp=hp.with_name(hp.name+'.G2matched-'+str(time.time_ns()));tmp.write_bytes(hb+append);os.replace(tmp,hp)
assert all((R/n).read_bytes()==b for n,b in protected.items())
after=j(B);assert after['authorized_training_seconds']==828000
print(json.dumps(dict(epoch=time.time(),central_new_evidence_roundtrip=True,master_approval_tracks_RM_bytes_preserved=True,no_canonical_write=True,active_accounting_normal_changes_allowed=True,current_before_sha256=H(before),current_after_sha256=H(raw),actual_phase=state['phase'],child=child,source32058_complete_behavior_review=True,no_GPU_launch_by_sync=True)))
""".replace('Path(ER)','Path('+repr(ER)+')').replace('Path(ROOT)','Path('+repr(ROOT)+')')
        _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);b=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(b+err).decode(errors='replace');proof=json.loads(b);proof['files']=[dict(name=n,bytes=p.stat().st_size,sha256=H(p.read_bytes())) for n,p in files.items()]
        (R/'METADATA_SYNCED.json').write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(proof))
    finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
    try:main()
    except Exception:
        (R/'SYNC_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-MATCHED-CONTINUATION-METADATA-01',error=traceback.format_exc(),no_blind_repeat=True),indent=2),encoding='utf8');raise
