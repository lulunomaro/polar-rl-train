from pathlib import Path
import os,sys,json,hashlib,time,base64,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';WIN='D:/MOD4_async_eval/closure_episode_clock2500_v15';B='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'
try:
 assert not (R/'PUBLISH_STARTED.json').exists();(R/'PUBLISH_STARTED.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-20MM-FROZEN-PUBLISH-01',once=True)),encoding='utf8')
 for name in ('RM_SSH_PASSWORD','MOD4_EVAL_SSH_PASSWORD'):
  secret,_=recover(name);assert secret;os.environ[name]=secret
 n=connect();w=connect_eval();v=json.loads((R/'PREPARED.json').read_bytes());pkg=v['package'];assert H(Path(pkg['path']).read_bytes())==pkg['sha256']
 with n.open_sftp() as nf,w.open_sftp() as wf:
  try:attention=json.loads(wf.open(WIN+'/E1_FULL_ROUTE_REVIEW_WORKER_ATTENTION.json').read())
  except FileNotFoundError:attention=None
  assert attention is None
  actual_worker_source=wf.open(WIN+'/eval_worker_e1_full_route_review.py').read();assert actual_worker_source==(W/'MOD4_E1_G1_ACTUAL_REVIEW_20261010/eval_worker_e1_full_route_review.py').read_bytes()
  started=json.loads(wf.open(WIN+'/E1_FULL_ROUTE_REVIEW_WORKER_STARTED.json').read())
  ps="[pscustomobject]@{rows=@(Get-CimInstance Win32_Process|Where-Object {$_.Name -like 'python*' -and $_.CommandLine -like '*eval_worker_e1_full_route_review.py*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}})}|ConvertTo-Json -Depth 6 -Compress"
  _,o,e=w.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=45);out=o.read();err=e.read();assert o.channel.recv_exit_status()==0
  actual=json.loads(out)['rows'];own=[p for p in actual if p['ProcessId']==started['pid'] and abs(p['creation_epoch']-started['epoch'])<2];assert len(own)==1
  budget_before=nf.open(B).read();ledger=json.loads(budget_before);assert ledger['active_segment'] is None and ledger['authorized_training_seconds']==828000
  state=json.loads(nf.open('/home/egde/rl_candidates/MOD4_S3_E1_G1_REPAIR_20261009/reports/E1_STATE.json').read());assert state['phase']=='E1_G1_repair_saved_review_ready' and state['child'] is None
  source=v['source'];assert H(nf.open(source['path']).read())==source['sha256']
  remote=E+'/artifacts/'+Path(pkg['path']).name
  nf.put(pkg['path'],remote+'.partial');assert H(nf.open(remote+'.partial').read())==pkg['sha256'];nf.rename(remote+'.partial',remote)
  m=json.loads((R/'MANIFEST_TEMPLATE.json').read_bytes());jid='clk2500-closure-episode-d3-121-e1-g2-20mm-source32053-fullroute-flat'
  m.update(job_id=jid,published_epoch=time.time(),role='reviewed32053_next20mm_geometry',protocol=v['protocol'],actual_behavior_scope='Approved003 next derived20mm geometric axis only: complete wave front support to both-wheels after support; frozen new ground/contact/reset evidence, not PPO admission',scope_pending_actual_review=True,no_learning=True,canonical_write_authority=False,no_auto_new_PPO=True)
  m['artifacts']['runtime']=dict(path=remote,bytes=pkg['bytes'],sha256=pkg['sha256']);m['artifacts']['checkpoint']=source;raw=json.dumps(m,indent=2).encode();dest=E+'/eval_queue/'+jid+'.json'
  with nf.open(dest+'.partial','wbx') as f:f.write(raw)
  assert nf.open(dest+'.partial').read()==raw;nf.rename(dest+'.partial',dest);assert nf.open(dest).read()==raw
  assert nf.open(B).read()==budget_before
 report=dict(epoch=time.time(),trial_id='E1-G2-20MM-FROZEN-PUBLISH-01',jobs=[m],current_worker_actual=own,current_worker_source_sha256=H(actual_worker_source),worker_not_restarted=True,source_selected_from_actual_full10mm_and_existing_oldskill_review=True,actual20mm_result_pending=True,no_PPO_native_or_training_executor_deployed=True,canonical_bytes_unchanged=True,new_budget_seconds=0)
 (R/'PUBLISHED.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(job_id=jid,package_sha256=pkg['sha256'],worker_actual=own,no_learning=True,new_budget_seconds=0)))
except Exception:
 (R/'PUBLISH_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-20MM-FROZEN-PUBLISH-01',error=traceback.format_exc(),no_blind_republication=True),indent=2),encoding='utf8');raise
finally:
 if 'n' in globals():n.close()
 if 'w' in globals():w.close()
 for name in ('RM_SSH_PASSWORD','MOD4_EVAL_SSH_PASSWORD'):os.environ.pop(name,None)
