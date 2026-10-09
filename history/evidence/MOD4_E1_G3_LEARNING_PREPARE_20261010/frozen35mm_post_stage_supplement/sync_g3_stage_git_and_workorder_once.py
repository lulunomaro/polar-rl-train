"""Publish concrete stage Git proof and corrected126 workorder; no training authority."""
from pathlib import Path
import hashlib,json,os,sys,subprocess,shlex,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';P=W/'polar-rl-train';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';B='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'
TAG='trial-20261010-e1-matched-retention-tradeoff-and-35mm-frozen-package-repair'
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode())
def git(*a):return subprocess.check_output(['git','-C',str(P),*a],encoding='utf8').strip()
def main():
 save('STAGE_GIT_SYNC_STARTED.json',dict(epoch=time.time(),once=True,trial_id='E1-G3-STAGE-GIT-WORKORDER-SYNC-05'))
 commit=git('rev-parse',TAG+'^{}');obj=git('rev-parse',TAG);remote=dict(x.split('\t')[::-1] for x in git('ls-remote','origin','refs/heads/main','refs/tags/'+TAG,'refs/tags/'+TAG+'^{}').splitlines());assert remote['refs/heads/main']==git('rev-parse','HEAD') and remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==commit
 idx=P/'history/evidence/MOD4_E1_G3_35MM_SCOPE_PREPARE_20261010/REPORT_CAPTURE_INDEX.json';j=json.loads(idx.read_bytes());tracked=set(git('ls-tree','-r','--name-only',commit).splitlines());assert all(x['Git_path'] in tracked and H((P/x['Git_path']).read_bytes())==x['archived_sha256'] for x in j['reports_and_implementation'])
 latest=sorted(R.glob('G3_126_COLLECTED_*.json'))[-1];v=json.loads(latest.read_bytes());assert v['current_attention'] is None
 proof=dict(epoch=time.time(),tag=TAG,commit=commit,tagobject=obj,remote_main=remote['refs/heads/main'],remote_main_tag_peeled_verified=True,push_pending=False,stage_reports_captured=len(j['reports_and_implementation']),large_indices=len(j['large_originals_index_only']),prior_same_SHA_references=len(j['prior_identical_reports_reused']),all_stage_reports_tracked_archive_SHA_verified=True,latest126_snapshot=dict(path=str(latest.resolve()),bytes=latest.stat().st_size,sha256=H(latest.read_bytes()),pending=v['pending'],worker=v['worker_actual']),post_stage_saved_reports_require_supplement=True,no_training_or_budget_authority=True)
 save('STAGE_GIT_RECORDED.json',proof)
 secret,_=recover('RM_SSH_PASSWORD');assert secret;os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  files={'E1_G3_35MM_FROZEN_REPAIR_GIT_RECORDED.json':R/'STAGE_GIT_RECORDED.json','NEXT_E1_G3_MANIFEST_REVIEWED126_ACTUAL_WORK_ORDER.md':D/'NEXT_E1_G3_MANIFEST_REVIEWED126_ACTUAL_WORK_ORDER.md','E1_G3_126_CURRENT_ACTUAL_COLLECTED.json':latest}
  with c.open_sftp() as f:
   for n,p in files.items():
    b=p.read_bytes()
    with f.open(E+'/reports/'+n,'wbx') as o:o.write(b)
    assert f.open(E+'/reports/'+n).read()==b
  code=r'''from pathlib import Path
import json,hashlib,time,os
R=Path(REPORTS_VALUE);B=Path(BUDGET_VALUE);budget=B.read_bytes();j=lambda p:json.loads(p.read_bytes());H=lambda b:hashlib.sha256(b).hexdigest();assert j(B)['active_segment'] is None and j(B)['authorized_training_seconds']==828000
protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md')};assert H(protected['MOD4_MOE_MASTER_PLAN.md'])=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);assert v['actual_phase']=='E1_G2_matched_continuation_saved_review_ready';scope=v['next_E1_G3_frozen_scope'];actual=j(R/'E1_G3_126_CURRENT_ACTUAL_COLLECTED.json');assert actual['current_attention'] is None
scope.update(work_order=str(R/'NEXT_E1_G3_MANIFEST_REVIEWED126_ACTUAL_WORK_ORDER.md'),stage_Git_recorded=str(R/'E1_G3_35MM_FROZEN_REPAIR_GIT_RECORDED.json'),actual126_snapshot=str(R/'E1_G3_126_CURRENT_ACTUAL_COLLECTED.json'),actual_result_pending=bool(actual['pending']),actual_independent_CPU_review_pending=True,no_G3_learning_executor_deployed=True,new_budget_seconds=0)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert p.read_bytes()==before;tmp=p.with_name(p.name+'.G3Git126-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,p)
hp=R/'LATEST_HANDOFF.md';hb=hp.read_bytes();marker='E1 G3 stage Git and corrected126 workorder20261010:';assert marker.encode() not in hb
text=chr(10)*2+marker+' Newannotated trial-20261010-e1-matched-retention-tradeoff-and-35mm-frozen-package-repair commit29e1064250c5aca5f3ca96d681159a69c6d7c98b/tagobject1926640c87e19d3f4418fb1b4f7ddebf2367d3b7 remote main/tag/peeled and73report archiveSHA/4largeindices/43priorreferences actualverified. Original124 retention tradeoff,125preGPU refusal,LF/CRLF receipt refusal and v2/newworker/new126 deployment receipts captured. Read NEXT_E1_G3_MANIFEST_REVIEWED126_ACTUAL_WORK_ORDER.md and E1_G3_126_CURRENT_ACTUAL_COLLECTED.json; actualnamespace E1_G3_PACKAGE_REVIEW. Pending or actualfrozenchild healthy is legal; not35mm admitted/E1 graduated/4090learningactive. Newworkorder uses126/newreadonlycollector/reviewer; neverreplay125 oroldonce. Later saved actual/CPUreview/sync/monitor reports still need supplement Git. Parent330 naturalclosed/own32103/uniqueaccount/canonical noactive preserved; no newPPO orbudget.'+chr(10)
assert hp.read_bytes()==hb;tmp=hp.with_name(hp.name+'.G3Git126-'+str(time.time_ns()));tmp.write_bytes(hb+text.encode());os.replace(tmp,hp)
assert B.read_bytes()==budget and all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),master_approval_tracks_RM_canonical_bytes_preserved=True,stage_Git_and126_workorder_synced=True,actual_result_pending=bool(actual['pending']),independent_review_pending=True,no_G3_learning_executor_deployed=True,current_before_SHA=H(before),current_after_SHA=H(raw),new_budget_seconds=0)))
'''.replace('REPORTS_VALUE',repr(E+'/reports')).replace('BUDGET_VALUE',repr(B))
  compile(code,'<G3Git126>','exec');_,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);out=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(out+err).decode(errors='replace');done=json.loads(out);done['files']=[dict(name=n,bytes=p.stat().st_size,sha256=H(p.read_bytes())) for n,p in files.items()];save('STAGE_GIT_METADATA_SYNCED.json',done)
  with c.open_sftp() as f:
   b=(R/'STAGE_GIT_METADATA_SYNCED.json').read_bytes()
   with f.open(E+'/reports/E1_G3_35MM_STAGE_GIT_METADATA_SYNCED.json','wbx') as o:o.write(b)
   assert f.open(E+'/reports/E1_G3_35MM_STAGE_GIT_METADATA_SYNCED.json').read()==b
  print(json.dumps(dict(stage_Git_metadata_synced=True,remote_main_tag_peeled_verified=True,push_pending=False,actual126_pending=bool(v['pending']),new_budget_seconds=0)))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:save('STAGE_GIT_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_blind_repeat=True));raise
