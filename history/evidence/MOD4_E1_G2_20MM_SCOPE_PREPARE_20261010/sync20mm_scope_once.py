from pathlib import Path
import os,sys,json,hashlib,shlex,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports'
try:
 assert not (R/'SYNC_STARTED.json').exists();(R/'SYNC_STARTED.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-20MM-SCOPE-METADATA-01')),encoding='utf8')
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 names={'E1_NEXT20MM_FROZEN_SCOPE_PREPARED.json':'PREPARED.json','E1_NEXT20MM_FROZEN_SCOPE_REPORT.md':'REPORT.md','E1_NEXT20MM_ARTIFACT_ALLOWLIST_REJECTION_REVIEW.json':'ALLOWLIST_REJECTION_REVIEW.json','E1_NEXT20MM_ACTUAL_REPAIRED_PUBLISHED.json':'REPAIRED_PUBLISHED.json','E1_ARTIFACT_SOURCE_WORKER_ADMITTED.json':'E1_ARTIFACT_SOURCE_REVIEW_WORKER_ADMITTED.json','NEXT_E1_20MM_ACTUAL_WORK_ORDER.md':'NEXT_E1_20MM_ACTUAL_WORK_ORDER.md'}
 latest=sorted(R.glob('ACTUAL_REPAIRED_COLLECTED_*.json'))[-1];names['E1_NEXT20MM_FROZEN_SCOPE_CURRENT_ACTUAL.json']=latest.name
 review=sorted(R.glob('ACTUAL_REPAIRED_REVIEW_*.json'))[-1];assert json.loads(review.read_bytes())['both_host_probe_result_bytes_exact'];names['E1_NEXT20MM_COMPLETE_WAVE_ROUTE_ACTUAL_REVIEW.json']=review.name
 with c.open_sftp() as f:
  for name,local in names.items():
   b=(R/local).read_bytes()
   with f.open(E+'/'+name,'wbx') as o:o.write(b)
   assert f.open(E+'/'+name).read()==b
 code=r'''from pathlib import Path
import json,time,hashlib,os
R=Path(REPORTS);H=lambda b:hashlib.sha256(b).hexdigest()
budget=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');bb=budget.read_bytes();ledger=json.loads(bb);assert ledger['active_segment'] is None and ledger['authorized_training_seconds']==828000
protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md')};assert H(protected['MOD4_MOE_MASTER_PLAN.md'])=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
prepared=json.loads((R/'E1_NEXT20MM_FROZEN_SCOPE_PREPARED.json').read_bytes());published=json.loads((R/'E1_NEXT20MM_ACTUAL_REPAIRED_PUBLISHED.json').read_bytes());actual=json.loads((R/'E1_NEXT20MM_FROZEN_SCOPE_CURRENT_ACTUAL.json').read_bytes())
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before)
v['next_E1_20mm_new_geometry_scope']=dict(epoch=time.time(),prepared=str(R/'E1_NEXT20MM_FROZEN_SCOPE_PREPARED.json'),published=str(R/'E1_NEXT20MM_ACTUAL_REPAIRED_PUBLISHED.json'),current_actual=str(R/'E1_NEXT20MM_FROZEN_SCOPE_CURRENT_ACTUAL.json'),work_order=str(R/'NEXT_E1_20MM_ACTUAL_WORK_ORDER.md'),selected_source=prepared['source'],actual_scope_pending=actual['pending'],actual_review=str(R/'E1_NEXT20MM_COMPLETE_WAVE_ROUTE_ACTUAL_REVIEW.json'),current_eval_attention=actual['current_attention'],no_learning_executor_deployed=True,no_new_budget_seconds=True,old121_transport_rejection_before_GPU_retained=True)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert p.read_bytes()==before;tmp=p.with_name(p.name+'.20mm-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,p)
h=R/'LATEST_HANDOFF.md';hb=h.read_bytes();marker='Approved003 next20mm frozen scope20261010:';assert marker.encode() not in hb
append=(chr(10)+chr(10)+marker+' reviewed32053 actual full10mm route and balanced oldskill reused; next20mm only geometric axis, CPU200rays,122 actual20mm source32053 route on3060, model-data-ground/contact accepted with forward27/27/reverse26/27 and one incomplete after-support prefix retained, not native/PPO/learning graduation.121 unchanged artifact allowlist rejected original training-path beforeGPU; original manifest/partial/attention retained,122 uses existing sameSHA permitted checkpoint copy. New E1_ARTIFACT_SOURCE_REVIEW worker only after actual old exit/lockfree, no healthy restart/guard weakening. Read new scope current actual and NEXT_E1_20MM_ACTUAL_WORK_ORDER, positively complete new contracts then bounded training at safe authority. No blind10mm/source32098, no newbudget, master/RM003/002/001 valid exclusions preserved, every report Git including later final.'+chr(10)).encode();assert h.read_bytes()==hb;tmp=h.with_name(h.name+'.20mm-'+str(time.time_ns()));tmp.write_bytes(hb+append);os.replace(tmp,h)
assert budget.read_bytes()==bb and all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),central_evidence_roundtrip=True,master_approval_tracks_RM_preserved=True,canonical_bytes_unchanged=True,current_before_sha256=H(before),current_after_sha256=H(raw),no_GPU_PPO_or_runtime_write=True,remaining_seconds=ledger['authorized_training_seconds']-ledger['charged_training_seconds'])))
'''.replace('Path(REPORTS)','Path('+repr(E)+')')
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);out=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(out+err).decode(errors='replace');proof=json.loads(out);proof['files']=[dict(name=n,bytes=(R/l).stat().st_size,sha256=H((R/l).read_bytes())) for n,l in names.items()]
 (R/'METADATA_SYNCED.json').write_text(json.dumps(proof,indent=2),encoding='utf8');print(json.dumps(proof))
except Exception:
 (R/'SYNC_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_blind_repeat=True),indent=2),encoding='utf8');raise
finally:
 if 'c' in globals():c.close()
 os.environ.pop('RM_SSH_PASSWORD',None)
