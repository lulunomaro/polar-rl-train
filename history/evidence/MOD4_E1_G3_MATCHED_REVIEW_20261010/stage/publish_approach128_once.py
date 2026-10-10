"""Publish new frozen paired approach scope to healthy unchanged worker, no learning."""
from pathlib import Path
import ast,base64,hashlib,json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';G=W/'MOD4_E1_G3_35MM_SCOPE_PREPARE_20261010';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';WIN='D:/MOD4_async_eval/closure_episode_clock2500_v15';B='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json';ROOT='/home/egde/rl_candidates/MOD4_S3_E1_G3_REVIEWED_20261010'
def save(n,v):
 p=R/n;assert not p.exists();p.write_bytes(json.dumps(v,indent=2).encode())
def main():
 save('PUBLISH128_STARTED.json',dict(epoch=time.time(),trial_id='E1-G3-PAIRED-APPROACH040-FROZEN-PUBLISH-01',once=True,no_learning=True))
 for name in ('RM_SSH_PASSWORD','MOD4_EVAL_SSH_PASSWORD'):
  secret,_=recover(name);assert secret;os.environ[name]=secret
 n=connect();w=connect_eval()
 try:
  prepared=json.loads((R/'PAIRED_APPROACH_PREPARED.json').read_bytes());pkg=prepared['package'];assert H(Path(pkg['path']).read_bytes())==pkg['sha256']
  with n.open_sftp() as nf,w.open_sftp() as wf:
   try:attention=json.loads(wf.open(WIN+'/E1_G3_PACKAGE_REVIEW_WORKER_ATTENTION.json').read())
   except FileNotFoundError:attention=None
   assert attention is None
   source=wf.open(WIN+'/eval_worker_e1_g3_package_review.py').read();assert source==(G/'eval_worker_e1_g3_package_review.py').read_bytes()
   base=wf.open(WIN+'/eval_worker_closure2500.py').read();base_tree=ast.parse(base.decode());assert any(isinstance(x,ast.Assert) and "manifest['steps'] in [300, 1500]" in ast.unparse(x) for x in ast.walk(base_tree))
   started=json.loads(wf.open(WIN+'/E1_G3_PACKAGE_REVIEW_WORKER_STARTED.json').read())
   ps="[pscustomobject]@{rows=@(Get-CimInstance Win32_Process|Where-Object {$_.Name -like 'python*' -and $_.CommandLine -like '*closure_episode_clock2500_v15*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}})}|ConvertTo-Json -Depth 6 -Compress"
   _,o,e=w.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');procs=json.loads(raw)['rows'];own=[p for p in procs if p['ProcessId']==started['pid'] and 'eval_worker_e1_g3_package_review.py' in p['CommandLine'] and abs(p['creation_epoch']-started['epoch'])<2];assert len(own)==1
   for j in prepared['jobs']:assert j['job_id']+'.json' not in nf.listdir(E+'/eval_queue') and j['job_id'] not in wf.listdir(WIN+'/jobs')
   budget=nf.open(B).read();ledger=json.loads(budget);assert ledger['active_segment'] is None and ledger['authorized_training_seconds']==828000
   code=r'''from pathlib import Path
import json,fcntl,hashlib
D=Path(ROOT_VALUE);j=lambda p:json.loads(p.read_bytes());s=j(D/'reports/E1_STATE.json');p=j(D/'reports/e1_G3_reviewed_observation_PASSED.json');g=j(D/'reports/E1_GUARDIAN_STARTED.json')
assert s['phase']=='E1_G3_reviewed_saved_review_ready' and s['child'] is None
for v in (s['owner'],g,dict(pid=p['own_PID_bound_receipt']['pid'],start_ticks=74243664)):
 q=Path('/proc')/str(v['pid'])
 if q.exists():
  a=(q/'stat').read_text().split(') ',1)[1].split();assert a[0]=='Z' or int(a[19])!=v['start_ticks']
assert p['checkpoint']['sha256']=='e912058d079bf1db7e40c546c54f55568218d514937cba30c65d8c913882a2cf' and len(p['unique_completed_segment'])==1
locks=[]
for q in (Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock'),Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/autonomy_controller.lock')):
 assert q.is_file(),str(q)
 with q.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(str(q))
print(json.dumps(dict(actual_parent_guardian_child_exited=True,phase=s['phase'],own_final_SHA=p['checkpoint']['sha256'],original_unique_segment=p['unique_completed_segment'],two_original_locks_free=locks)))
'''.replace('ROOT_VALUE',repr(ROOT))
   compile(code,'<paired128boundary>','exec');_,o,e=n.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');boundary=json.loads(raw)
   for job in prepared['jobs']:
    cp=job['artifacts']['checkpoint'];b=nf.open(cp['path']).read();assert len(b)==cp['bytes'] and H(b)==cp['sha256']
   remote=prepared['jobs'][0]['artifacts']['runtime']['path'];assert Path(remote).name not in nf.listdir(E+'/artifacts');nf.put(pkg['path'],remote+'.partial');assert H(nf.open(remote+'.partial').read())==pkg['sha256'];nf.rename(remote+'.partial',remote)
   published=[]
   for job in prepared['jobs']:
    job['published_epoch']=time.time();raw=json.dumps(job,indent=2).encode();q=E+'/eval_queue/'+job['job_id']+'.json'
    with nf.open(q+'.partial','wbx') as f:f.write(raw)
    assert nf.open(q+'.partial').read()==raw;nf.rename(q+'.partial',q);assert nf.open(q).read()==raw;published.append(job)
   assert nf.open(B).read()==budget
   save('PAIRED_APPROACH_PUBLISHED.json',dict(epoch=time.time(),trial_id='E1-G3-PAIRED-APPROACH040-FROZEN-PUBLISH-01',jobs=published,worker_actual=own,worker_source_SHA=H(source),worker_base_SHA=H(base),actual_boundary=boundary,canonical_SHA=H(budget),canonical_bytes_preserved=True,healthy_worker_not_restarted=True,no_4090_PPO_or_learning_launch=True,new_budget_seconds=0))
   print(json.dumps(dict(jobs=[j['job_id'] for j in published],worker_actual=own,package_SHA=pkg['sha256'],boundary=boundary['phase'],budget_preserved=True,no_learning=True)))
 finally:
  n.close();w.close()
  for name in ('RM_SSH_PASSWORD','MOD4_EVAL_SSH_PASSWORD'):os.environ.pop(name,None)
if __name__=='__main__':
 try:main()
 except Exception:
  save('PUBLISH128_ERROR.json',dict(epoch=time.time(),trial_id='E1-G3-PAIRED-APPROACH040-FROZEN-PUBLISH-01',error=traceback.format_exc(),original_partial_retained=True,do_not_blind_retry=True));raise
