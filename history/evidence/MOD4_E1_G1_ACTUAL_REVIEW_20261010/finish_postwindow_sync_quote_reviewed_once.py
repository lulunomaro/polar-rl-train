"""New post-window evidence/phase synchronization with actual boundary and CAS; no PPO."""
from pathlib import Path
import os,sys,json,hashlib,shlex,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports';ROOT='/home/egde/rl_candidates/MOD4_S3_E1_G1_REPAIR_20261009';B='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'
try:
 assert not (R/'POSTWINDOW_METADATA_FINISH_STARTED.json').exists();(R/'POSTWINDOW_METADATA_FINISH_STARTED.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G1-POSTWINDOW-METADATA-QUOTE-CONTINUATION-03')),encoding='utf8')
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 payload={'E1_G1_POST_WINDOW_ACTUAL_REVIEW.json':R/'STAGE_REVIEW.json','E1_G1_ROUTE_COVERAGE_REPAIR_REPORT.md':R/'REPORT.md','NEXT_E1_FULL_ROUTE_REPAIR_WORK_ORDER.md':R/'NEXT_E1_FULL_ROUTE_REPAIR_WORK_ORDER.md','E1_G1_FULL_ROUTE_WORKER_ADMITTED.json':R/'E1_FULL_ROUTE_REVIEW_WORKER_ADMITTED.json','SELECTED_E1_NEXT_GEOMETRY_BEHAVIOR_SOURCE.json':R/'SELECTED_E1_NEXT_GEOMETRY_BEHAVIOR_SOURCE.json','E1_NEXT20MM_CPU_GEOMETRY_PREPARED.json':R/'NEXT20MM_GEOMETRY_CPU_PREPARED.json'}
 latest=sorted(R.glob('PROXY_ROUTE_REVIEW_*.json'));latest=[p for p in latest if 'ERROR' not in p.name]
 if latest:payload['E1_G1_COMPLETE_WAVE_ROUTE_ACTUAL_REVIEW.json']=latest[-1]
 with c.open_sftp() as f:
  for name,p in payload.items():
   raw=p.read_bytes()
   assert f.open(E+'/'+name).read()==raw,('Already uploaded payload differs; no rewrite',name)
 code=r'''from pathlib import Path
import json,hashlib,time,os
R=Path(REPORTS);root=Path(ROOT);budget=Path(BUDGET);H=lambda b:hashlib.sha256(b).hexdigest()
lb=budget.read_bytes();ledger=json.loads(lb);assert ledger['active_segment'] is None and ledger['authorized_training_seconds']==828000
state=json.loads((root/'reports/E1_STATE.json').read_bytes());assert state['phase']=='E1_G1_repair_saved_review_ready' and state['child'] is None
actual=json.loads((R/'E1_G1_POST_WINDOW_ACTUAL_REVIEW.json').read_bytes());own=actual['own_complete_source'];pid=own['own_PID_bound_receipt']['pid']
assert not Path('/proc/'+str(pid)).exists()
protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json')}
master=R.parent/'MOD4_MOE_MASTER_PLAN.md';assert H(master.read_bytes())=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before)
v['previous_G1_formal_cached_snapshot_retained']={k:v.get(k) for k in ('epoch','actual_phase','parent','guardian','trainer','active_log','deadline_epoch','run','own_current_save','live_health')}
v.update(epoch=time.time(),actual_phase=state['phase'],parent=None,guardian=None,trainer=None,active_log=None,deadline_epoch=None,own_current_save=own['checkpoint'],own_snapshot_count=62,live_health=own['health'],live_health_is_not_final=False,new_budget_seconds=0)
v['E1_G1_post_window_route_repair']=dict(review=str(R/'E1_G1_POST_WINDOW_ACTUAL_REVIEW.json'),report=str(R/'E1_G1_ROUTE_COVERAGE_REPAIR_REPORT.md'),next_work_order=str(R/'NEXT_E1_FULL_ROUTE_REPAIR_WORK_ORDER.md'),candidate32098_rejected_as_learning_source=True,permanent_repair_not_proved=True,original80_wave_coverage_missing=True,actual_route_pending=actual['route_pending'],current_worker_attention=actual['current_worker_attention'],no_additional_PPO_started=True)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert p.read_bytes()==before
tmp=p.with_name(p.name+'.postwindow-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,p)
h=R/'LATEST_HANDOFF.md';hb=h.read_bytes();marker='E1 G1 post-window full-wave route repair20261010:';assert marker.encode() not in hb
append=('\n\n'+marker+' actual321 formal naturally closed32098/46updates/920.402443409s uniquely settled; inheritedworld19/64 and +1.5m/s error.517403 persist, candidate not selected. Original80 route did not sampleG1 waves;119 anchor dtype error and neverrun119 candidate retained. New frozen-only worker after actual exit/lockfree,120v4 zero-copy Torch route pair; see E1_G1_POST_WINDOW_ACTUAL_REVIEW and NEXT_E1_FULL_ROUTE_REPAIR_WORK_ORDER. Actual completion/raw review precede next authority; no extraPPO/extension, master/RM003/002/001 valid exclusions retained; all reports Git.\n').encode()
assert h.read_bytes()==hb;tmp=h.with_name(h.name+'.postwindow-'+str(time.time_ns()));tmp.write_bytes(hb+append);os.replace(tmp,h)
assert budget.read_bytes()==lb and all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),central_evidence_roundtrip=True,current_before_sha256=H(before),current_after_sha256=H(raw),approval_tracks_master_RM_preserved=True,canonical_bytes_unchanged=True,actual_no_training_boundary_verified=True,remaining_seconds=ledger['authorized_training_seconds']-ledger['charged_training_seconds'],no_GPU_PPO_or_runtime_write=True)))
'''.replace('Path(REPORTS)','Path('+repr(E)+')').replace('Path(ROOT)','Path('+repr(ROOT)+')').replace('Path(BUDGET)','Path('+repr(B)+')')
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);out=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(out+err).decode(errors='replace')
 proof=json.loads(out);proof['files']=[dict(name=n,sha256=H(p.read_bytes()),bytes=p.stat().st_size) for n,p in payload.items()]
 (R/'POSTWINDOW_METADATA_SYNCED.json').write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(proof))
except Exception:
 (R/'POSTWINDOW_METADATA_FINISH_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_blind_repeat_existing_writes=True),indent=2),encoding='utf8');raise
finally:
 if 'c' in globals():c.close()
 os.environ.pop('RM_SSH_PASSWORD',None)
