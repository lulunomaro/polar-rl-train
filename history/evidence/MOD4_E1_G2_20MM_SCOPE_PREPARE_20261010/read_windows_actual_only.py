"""Independent current3060 read when central SSH is unavailable; no bridge equivalence claim."""
from pathlib import Path
import os,sys,json,base64,hashlib,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
WIN='D:/MOD4_async_eval/closure_episode_clock2500_v15';jid='clk2500-closure-episode-d3-122-e1-g2-20mm-source32053-fullroute-flat'
try:
 secret,_=recover('MOD4_EVAL_SSH_PASSWORD');assert secret;os.environ['MOD4_EVAL_SSH_PASSWORD']=secret;c=connect_eval();receipts={};files=[]
 with c.open_sftp() as f:
  for name in ('STARTED','STATE','ATTENTION','ADMITTED'):
   try:b=f.open(WIN+'/E1_ARTIFACT_SOURCE_REVIEW_WORKER_'+name+'.json').read()
   except FileNotFoundError:receipts[name]=None;continue
   receipts[name]=json.loads(b)
  for name in ('manifest.json','result.json','probe.json'):
   try:b=f.open(WIN+'/jobs/'+jid+'/'+name).read()
   except FileNotFoundError:continue
   out=R/'windows_only'/jid/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(b);files.append(dict(source=WIN+'/jobs/'+jid+'/'+name,path=str(out.resolve()),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),central_return_not_yet_verified=True))
  src=f.open(WIN+'/eval_worker_e1_artifact_source_review.py').read();assert src==(D/'eval_worker_e1_artifact_source_review.py').read_bytes()
 ps="[pscustomobject]@{processes=@(Get-CimInstance Win32_Process|Where-Object {$_.Name -like 'python*' -and $_.CommandLine -like '*closure_episode_clock2500_v15*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}})}|ConvertTo-Json -Compress -Depth 6"
 _,o,e=c.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=45);out=o.read();err=e.read();assert o.channel.recv_exit_status()==0;ps=json.loads(out)['processes']
 report=dict(epoch=time.time(),trial_id='E1-G2-WINDOWS-INDEPENDENT-ACTUAL-READ-01',receipts=receipts,processes=ps,files=files,source_SHA_exact=True,central_read_attempts_two_TCP_timeout_before_any_mutation=True,not_full_bridge_byte_or_behavior_acceptance=True,no_restart_or_signal_or_PPO_canonical_write=True)
 (R/'WINDOWS_CURRENT_ACTUAL.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(receipts=receipts,processes=ps,files=files),ensure_ascii=True))
except Exception:
 (R/'WINDOWS_CURRENT_READ_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),read_only=True),indent=2),encoding='utf8');raise
finally:
 if 'c' in globals():c.close()
 os.environ.pop('MOD4_EVAL_SSH_PASSWORD',None)
