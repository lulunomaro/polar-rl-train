"""Only final saved-boundary evidence and metadata CAS, with compile before transport."""
from pathlib import Path
import os,sys,json,time,hashlib,shlex,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_G2_MATCHED_CONTINUE_20261010';ER='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports'
def main():
    assert not (R/'FINAL_SYNC_STARTED.json').exists();(R/'FINAL_SYNC_STARTED.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-MATCHED-NATURAL-FINAL-METADATA-01')),encoding='utf8')
    files={'E1_G2_MATCHED_CONTINUATION_OWN_FINAL_VERIFIED.json':sorted(R.glob('FINAL_ACTUAL_VERIFIED_*.json'))[-1],'E1_G2_MATCHED_CONTINUATION_FINAL_REPORT.md':R/'FINAL_SAVED_REVIEW_REPORT.md','E1_G2_MATCHED_CONTINUATION_FINAL_CURRENT_ACTUAL.json':sorted(R.glob('MATCHED_ACTUAL_*.json'))[-1],'E1_G2_CANDIDATE124_EVALUATOR_CURRENT_ACTUAL.json':sorted(R.glob('CONTINUATION_124_COLLECTED_*.json'))[-1]}
    code=r'''from pathlib import Path
import json,time,hashlib,os
R=Path(ER);D=Path(ROOT);j=lambda p:json.loads(p.read_bytes());H=lambda b:hashlib.sha256(b).hexdigest()
state=j(D/'reports/E1_STATE.json');own=j(D/'reports/e1_G2_matched_continuation_PASSED.json');assert state['phase']=='E1_G2_matched_continuation_saved_review_ready' and state['child'] is None
def gone(v):
 p=Path('/proc')/str(v['pid'])
 if not p.exists():return True
 s=(p/'stat').read_text().split(') ',1)[1].split();return s[0]=='Z' or int(s[19])!=v['start_ticks']
assert gone(state['owner']) and gone(j(D/'reports/E1_GUARDIAN_STARTED.json')) and gone(dict(pid=own['own_PID_bound_receipt']['pid'],start_ticks=72519910))
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');budget=B.read_bytes();ledger=json.loads(budget);assert ledger['active_segment'] is None and ledger['authorized_training_seconds']==828000
assert [x for x in ledger['completed_segments'] if x['pid']==own['own_PID_bound_receipt']['pid']]==own['unique_completed_segment'] and len(own['unique_completed_segment'])==1
protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md')};assert H(protected['MOD4_MOE_MASTER_PLAN.md'])=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
proof=j(R/'E1_G2_MATCHED_CONTINUATION_OWN_FINAL_VERIFIED.json');assert proof['checkpoint']['sha256']==own['checkpoint']['sha256'] and proof['source_count']==330 and proof['snapshot_count']==62
P=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=P.read_bytes();v=json.loads(before);v['previous_G2_matched_active_snapshot_retained']={k:v.get(k) for k in ('epoch','actual_phase','parent','guardian','trainer','active_log','deadline_epoch','own_current_save','live_health')}
v.update(epoch=time.time(),actual_phase=state['phase'],parent=None,guardian=None,trainer=None,active_log=None,deadline_epoch=None,own_current_save=own['checkpoint'],own_snapshot_count=62,live_health=own['health'],live_health_is_not_final=False,new_budget_seconds=0)
event=v['E1_G2_matched_continuation_execution_event'];event.update(final_verified=str(R/'E1_G2_MATCHED_CONTINUATION_OWN_FINAL_VERIFIED.json'),final_report=str(R/'E1_G2_MATCHED_CONTINUATION_FINAL_REPORT.md'),final_current=str(R/'E1_G2_MATCHED_CONTINUATION_FINAL_CURRENT_ACTUAL.json'),candidate124_evaluator=str(R/'E1_G2_CANDIDATE124_EVALUATOR_CURRENT_ACTUAL.json'),candidate124_actual_behavior_pending=True,no_auto_more_PPO_before_complete_actual_review=True,all_courses_finished=False)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert P.read_bytes()==before;tmp=P.with_name(P.name+'.G2final-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,P)
hp=R/'LATEST_HANDOFF.md';hb=hp.read_bytes();marker='E1 G2 matched900s natural fullsave32103 reviewpending20261010:';assert marker.encode() not in hb
append=(chr(10)*2+marker+' actual46updates/1104control/22.08Menvsteps/4416callbacks exact, CPU96/source330/snapshot62/ownPID1873663/final32103 SHA1f63e07d212e2752140ece48b3c516bffd97699a938f1db61f03551a8cda015f. Ordinary/integrity/unknown0/nonfinitefalse/STOPnone, closure.914594508mm, declared time_out/route truncation coverageexact. Own fullsave and actual parentguardianchild exits, sameG2/fulloldstreams/CUDA roundtrip then newepisode verified; original parent uniquely settled920.422999s, active-Sactiveempty legal savedreview boundary not fault/E1 graduation. Four124 auto-published; healthy3060 artifactsource worker actual flat child starting, behavior pending no auto morePPO. Read new final receipts/workorder, do not stale active/mainresume/recharge/clearactive or claim save is mature. Master/RM003002001/budget828000 preserved/new0. All saved final reports must Git supplement original18d1e590, largeweights path-size-SHA only.'+chr(10)).encode()
assert hp.read_bytes()==hb;tmp=hp.with_name(hp.name+'.G2final-'+str(time.time_ns()));tmp.write_bytes(hb+append);os.replace(tmp,hp)
assert B.read_bytes()==budget and all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),actual_natural_boundary_verified=True,central_new_evidence_roundtrip=True,master_approval_tracks_RM_canonical_bytes_preserved=True,actual_phase=state['phase'],final_checkpoint_sha256=own['checkpoint']['sha256'],candidate124_behavior_pending=True,current_before_sha256=H(before),current_after_sha256=H(raw),no_GPU_PPO_runtime_or_canonical_write=True)))
'''.replace('Path(ER)','Path('+repr(ER)+')').replace('Path(ROOT)','Path('+repr(ROOT)+')')
    compile(code,'<final-metadata>','exec');secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
    try:
        with c.open_sftp() as f:
            for n,p in files.items():
                b=p.read_bytes()
                with f.open(ER+'/'+n,'wbx') as out:out.write(b)
                assert f.open(ER+'/'+n).read()==b
        _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);b=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(b+err).decode(errors='replace');proof=json.loads(b);proof['files']=[dict(name=n,bytes=p.stat().st_size,sha256=H(p.read_bytes())) for n,p in files.items()]
        raw=json.dumps(proof,indent=2).encode();(R/'FINAL_METADATA_SYNCED.json').write_bytes(raw)
        with c.open_sftp() as f:
            with f.open(ER+'/E1_G2_MATCHED_CONTINUATION_FINAL_METADATA_SYNCED.json','wbx') as out:out.write(raw)
            assert f.open(ER+'/E1_G2_MATCHED_CONTINUATION_FINAL_METADATA_SYNCED.json').read()==raw
        print(json.dumps(proof))
    finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
    try:main()
    except Exception:
        (R/'FINAL_SYNC_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-MATCHED-NATURAL-FINAL-METADATA-01',error=traceback.format_exc(),no_blind_repeat=True),indent=2),encoding='utf8');raise
