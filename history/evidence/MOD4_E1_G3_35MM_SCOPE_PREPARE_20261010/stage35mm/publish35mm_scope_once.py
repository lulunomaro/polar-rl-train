"""One new approved35mm frozen job on the existing healthy evaluator, no training."""
from pathlib import Path
import base64,hashlib,json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';WIN='D:/MOD4_async_eval/closure_episode_clock2500_v15'
B='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_G2_MATCHED_CONTINUE_20261010'
JID='clk2500-closure-episode-d3-125-e1-g3-35mm-source32058-fullroute-flat'
def save(name,value):
 p=R/name;assert not p.exists();p.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8')
def run(c,code):
 compile(code,'<G3-scope-metadata>','exec');_,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);b=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(b+err).decode(errors='replace');return json.loads(b)
def main():
 save('PUBLISH_STARTED.json',dict(epoch=time.time(),trial_id='E1-G3-35MM-FROZEN-PUBLISH-01',no_learning=True,once=True))
 for name in ('RM_SSH_PASSWORD','MOD4_EVAL_SSH_PASSWORD'):
  secret,_=recover(name);assert secret;os.environ[name]=secret
 n=connect();w=connect_eval()
 try:
  prepared=json.loads((R/'PREPARED.json').read_bytes());pkg=prepared['package'];assert H(Path(pkg['path']).read_bytes())==pkg['sha256']
  with n.open_sftp() as nf,w.open_sftp() as wf:
   try:attention=json.loads(wf.open(WIN+'/E1_ARTIFACT_SOURCE_REVIEW_WORKER_ATTENTION.json').read())
   except FileNotFoundError:attention=None
   assert attention is None
   source=wf.open(WIN+'/eval_worker_e1_artifact_source_review.py').read();assert source==(W/'MOD4_E1_G2_20MM_SCOPE_PREPARE_20261010/eval_worker_e1_artifact_source_review.py').read_bytes()
   started=json.loads(wf.open(WIN+'/E1_ARTIFACT_SOURCE_REVIEW_WORKER_STARTED.json').read())
   ps="[pscustomobject]@{rows=@(Get-CimInstance Win32_Process|Where-Object {$_.Name -like 'python*' -and $_.CommandLine -like '*closure_episode_clock2500_v15*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}})}|ConvertTo-Json -Depth 6 -Compress"
   _,o,e=w.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=45);b=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(b+err).decode(errors='replace');actual=json.loads(b)['rows'];own=[p for p in actual if p['ProcessId']==started['pid'] and 'eval_worker_e1_artifact_source_review.py' in p['CommandLine'] and abs(p['creation_epoch']-started['epoch'])<2];assert len(own)==1
   assert JID+'.json' not in nf.listdir(E+'/eval_queue') and JID not in wf.listdir(WIN+'/jobs')
   budget_before=nf.open(B).read();ledger=json.loads(budget_before);assert ledger['active_segment'] is None and ledger['authorized_training_seconds']==828000
   boundary=run(n,r'''from pathlib import Path
import json,os
D=Path(ROOT_VALUE);j=lambda p:json.loads(p.read_bytes());s=j(D/'reports/E1_STATE.json');p=j(D/'reports/e1_G2_matched_continuation_PASSED.json');g=j(D/'reports/E1_GUARDIAN_STARTED.json')
assert s['phase']=='E1_G2_matched_continuation_saved_review_ready' and s['child'] is None
for v in (s['owner'],g,dict(pid=p['own_PID_bound_receipt']['pid'],start_ticks=72519910)):
 q=Path('/proc')/str(v['pid'])
 if q.exists():
  a=(q/'stat').read_text().split(') ',1)[1].split();assert a[0]=='Z' or int(a[19])!=v['start_ticks']
print(json.dumps(dict(actual_parent_guardian_child_exited=True,phase=s['phase'],own_final_sha256=p['checkpoint']['sha256'])))
'''.replace('ROOT_VALUE',repr(ROOT)))
   m=json.loads((R/'MANIFEST_TEMPLATE.json').read_bytes());assert H(nf.open(m['artifacts']['checkpoint']['path']).read())==prepared['selected_source']['sha256']
   remote=E+'/artifacts/'+Path(pkg['path']).name;assert Path(remote).name not in nf.listdir(E+'/artifacts')
   nf.put(pkg['path'],remote+'.partial');assert H(nf.open(remote+'.partial').read())==pkg['sha256'];nf.rename(remote+'.partial',remote)
   m.update(job_id=JID,published_epoch=time.time());m['artifacts']['runtime']=dict(path=remote,bytes=pkg['bytes'],sha256=pkg['sha256']);raw=json.dumps(m,indent=2).encode();queue=E+'/eval_queue/'+JID+'.json'
   with nf.open(queue+'.partial','wbx') as f:f.write(raw)
   assert nf.open(queue+'.partial').read()==raw;nf.rename(queue+'.partial',queue);assert nf.open(queue).read()==raw and nf.open(B).read()==budget_before
   save('PUBLISHED.json',dict(epoch=time.time(),trial_id='E1-G3-35MM-FROZEN-PUBLISH-01',jobs=[m],worker_actual=own,worker_source_sha256=H(source),worker_not_modified_or_restarted=True,actual_boundary=boundary,new35mm_result_pending=True,no_4090_GPU_PPO_or_learning_executor_deployed=True,canonical_bytes_preserved=True,new_budget_seconds=0))
   C=W/'MOD4_E1_G2_MATCHED_CONTINUE_20261010';files={'E1_G2_MODEL32103_COMPLETE_MATCHED_REVIEW.json':sorted((C/'reports').glob('CONTINUATION_124_REVIEW_*.json'))[-1],'E1_G2_MODEL32103_RETENTION_DECISION.json':R/'CANDIDATE124_RETENTION_DECISION.json','SELECTED_E1_G3_FROZEN_SCOPE_SOURCE.json':R/'SELECTED_E1_G3_FROZEN_SCOPE_SOURCE.json','E1_G3_35MM_FROZEN_PREPARED.json':R/'PREPARED.json','E1_G3_35MM_FROZEN_PUBLISHED.json':R/'PUBLISHED.json','E1_G3_35MM_CPU_GEOMETRY_REVIEW.json':R/'CPU_GEOMETRY_REVIEW.json','E1_G3_35MM_FROZEN_REPORT.md':R/'REPORT.md','NEXT_E1_G3_35MM_ACTUAL_WORK_ORDER.md':R/'NEXT_E1_G3_35MM_ACTUAL_WORK_ORDER.md'}
   for name,p in files.items():
    b=p.read_bytes()
    with nf.open(E+'/reports/'+name,'wbx') as f:f.write(b)
    assert nf.open(E+'/reports/'+name).read()==b
  code=r'''from pathlib import Path
import hashlib,json,time,os
R=Path(REPORTS_VALUE);B=Path(BUDGET_VALUE);budget=B.read_bytes();j=lambda p:json.loads(p.read_bytes());H=lambda b:hashlib.sha256(b).hexdigest();assert j(B)['active_segment'] is None
protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md')}
assert H(protected['MOD4_MOE_MASTER_PLAN.md'])=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
for name in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json'):assert b'MOD4-RM-TERRAIN-CURRICULUM-REVISION-003' in protected[name] and b'MOD4-RM-OUTER-CURB-AND-ROUGH-GEOMETRY-CLARIFICATION-002' in protected[name]
review=j(R/'E1_G2_MODEL32103_COMPLETE_MATCHED_REVIEW.json');assert review['review_complete'] and not review['pending']
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);assert v['actual_phase']=='E1_G2_matched_continuation_saved_review_ready'
event=v['E1_G2_matched_continuation_execution_event'];event.update(candidate124_actual_behavior_pending=False,candidate124_complete_matched_review=str(R/'E1_G2_MODEL32103_COMPLETE_MATCHED_REVIEW.json'),candidate124_retention_decision=str(R/'E1_G2_MODEL32103_RETENTION_DECISION.json'),candidate32103_not_selected_for_more_learning=True)
v['next_E1_G3_frozen_scope']=dict(epoch=time.time(),selected_source=str(R/'SELECTED_E1_G3_FROZEN_SCOPE_SOURCE.json'),prepared=str(R/'E1_G3_35MM_FROZEN_PREPARED.json'),published=str(R/'E1_G3_35MM_FROZEN_PUBLISHED.json'),work_order=str(R/'NEXT_E1_G3_35MM_ACTUAL_WORK_ORDER.md'),actual_result_pending=True,no_G3_learning_executor_deployed=True,no_auto_more_PPO=True,new_budget_seconds=0)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert p.read_bytes()==before;tmp=p.with_name(p.name+'.G3scope-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,p)
hp=R/'LATEST_HANDOFF.md';hb=hp.read_bytes();marker='E1 124 complete tradeoff and35mm frozen scope20261010:';assert marker.encode() not in hb
text=chr(10)*2+marker+' 32103 actual20mm forward/reverse27/27 ordinary0, flat errors-.031751/+ .044210, pure+4pi8of8/-6of8, world49of64 versus earlier32058 62of64 and32053 63of64; signed yaw2 cross worsens both directions, maxabs.063371750m/s. Original raw/strict/cost preserved; no more blind20mm PPO, not permanent repair or E1/RM graduation. Select complete matched32058 SHA42cdc9d24519778a9da3e35b05a3eb3bb5745760c26a5842c78fcde2bd39e53b for next003 derived35mm frozen scope125 only. CPU203 rays exact component check, period/span/normalizedCAD+other4families+30/20/20/15/15 unchanged; no70/20/10 quota mix. Existing healthy3060 artifactsource worker receives125 with permitted artifactcheckpoint; no worker/runtime mutation or4090GPU/PPO/canonicalwrite. Current330 own naturalfinal/unique920.422999s/actualallgone boundary unchanged; active-Sactiveempty legal, no auto morePPO before real35mm scope+newcontracts. Read new review/decision/workorder, true actual/proc/ownreceipts first. Master/RM003002001/S8/gate/hardware/pause93-94 unchanged, budget828000/new0. All new reports require stageGit and later supplements.'+chr(10)
assert hp.read_bytes()==hb;tmp=hp.with_name(hp.name+'.G3scope-'+str(time.time_ns()));tmp.write_bytes(hb+text.encode());os.replace(tmp,hp)
assert B.read_bytes()==budget and all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),central_new_evidence_roundtrip=True,metadata_updated_after_complete124_review=True,no_4090_GPU_PPO_runtime_or_canonical_write=True,master_approval_tracks_RM_canonical_preserved=True,current_before_sha256=H(before),current_after_sha256=H(raw),actual_35mm_behavior_pending=True,new_budget_seconds=0)))
'''.replace('REPORTS_VALUE',repr(E+'/reports')).replace('BUDGET_VALUE',repr(B))
  proof=run(n,code);proof['files']=[dict(name=name,bytes=p.stat().st_size,sha256=H(p.read_bytes())) for name,p in files.items()];save('METADATA_SYNCED.json',proof)
  with n.open_sftp() as nf:
   raw=(R/'METADATA_SYNCED.json').read_bytes()
   with nf.open(E+'/reports/E1_G3_35MM_FROZEN_METADATA_SYNCED.json','wbx') as f:f.write(raw)
   assert nf.open(E+'/reports/E1_G3_35MM_FROZEN_METADATA_SYNCED.json').read()==raw
  print(json.dumps(dict(job_id=JID,package_SHA=pkg['sha256'],worker_actual=own,actual_boundary=boundary,new_behavior_pending=True,metadata_synced=True,no_learning=True,new_budget_seconds=0)))
 finally:
  n.close();w.close()
  for name in ('RM_SSH_PASSWORD','MOD4_EVAL_SSH_PASSWORD'):os.environ.pop(name,None)
if __name__=='__main__':
 try:main()
 except Exception:
  save('PUBLISH_ERROR.json',dict(epoch=time.time(),trial_id='E1-G3-35MM-FROZEN-PUBLISH-01',error=traceback.format_exc(),no_blind_retry=True,original_partial_files_retained=True));raise
