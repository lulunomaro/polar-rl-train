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
JID='clk2500-closure-episode-d3-126-e1-g3-35mm-source32058-manifest-reviewed-fullroute-flat'
def save(name,value):
 p=R/name;assert not p.exists();p.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8')
def run(c,code):
 compile(code,'<G3-scope-metadata>','exec');_,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);b=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(b+err).decode(errors='replace');return json.loads(b)
def main():
 save('PUBLISH126_STARTED.json',dict(epoch=time.time(),trial_id='E1-G3-35MM-REPAIRED-FROZEN-PUBLISH-04',no_learning=True,once=True))
 for name in ('RM_SSH_PASSWORD','MOD4_EVAL_SSH_PASSWORD'):
  secret,_=recover(name);assert secret;os.environ[name]=secret
 n=connect();w=connect_eval()
 try:
  prepared=json.loads((R/'REPAIRED_PREPARED.json').read_bytes());pkg=prepared['package'];assert H(Path(pkg['path']).read_bytes())==pkg['sha256']
  with n.open_sftp() as nf,w.open_sftp() as wf:
   try:attention=json.loads(wf.open(WIN+'/E1_G3_PACKAGE_REVIEW_WORKER_ATTENTION.json').read())
   except FileNotFoundError:attention=None
   assert attention is None
   source=wf.open(WIN+'/eval_worker_e1_g3_package_review.py').read();assert source==(D/'eval_worker_e1_g3_package_review.py').read_bytes()
   started=json.loads(wf.open(WIN+'/E1_G3_PACKAGE_REVIEW_WORKER_STARTED.json').read())
   ps="[pscustomobject]@{rows=@(Get-CimInstance Win32_Process|Where-Object {$_.Name -like 'python*' -and $_.CommandLine -like '*closure_episode_clock2500_v15*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}})}|ConvertTo-Json -Depth 6 -Compress"
   _,o,e=w.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=45);b=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(b+err).decode(errors='replace');actual=json.loads(b)['rows'];own=[p for p in actual if p['ProcessId']==started['pid'] and 'eval_worker_e1_g3_package_review.py' in p['CommandLine'] and abs(p['creation_epoch']-started['epoch'])<2];assert len(own)==1
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
   save('REPAIRED_PUBLISHED.json',dict(epoch=time.time(),trial_id='E1-G3-35MM-REPAIRED-FROZEN-PUBLISH-04',jobs=[m],worker_actual=own,worker_source_sha256=H(source),new_worker_own_admission_verified=True,original125_and_old_worker_rejection_retained=True,actual_boundary=boundary,new35mm_result_pending=True,no_4090_GPU_PPO_or_learning_executor_deployed=True,canonical_bytes_preserved=True,new_budget_seconds=0))
  print(json.dumps(dict(job_id=JID,package_SHA=pkg['sha256'],worker_actual=own,actual_boundary=boundary,new_behavior_pending=True,no_learning=True,new_budget_seconds=0)))
 finally:
  n.close();w.close()
  for name in ('RM_SSH_PASSWORD','MOD4_EVAL_SSH_PASSWORD'):os.environ.pop(name,None)
if __name__=='__main__':
 try:main()
 except Exception:
  save('PUBLISH126_ERROR.json',dict(epoch=time.time(),trial_id='E1-G3-35MM-REPAIRED-FROZEN-PUBLISH-04',error=traceback.format_exc(),no_blind_retry=True,original_partial_files_retained=True));raise
