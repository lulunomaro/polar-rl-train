"""Read actual transport/worker/queue progress; absence of a future result is pending."""
from pathlib import Path
import base64,json,os,time,traceback
from publish_approach128_once import connect,connect_eval,recover,E,WIN,B,R
def main():
 for name in ('RM_SSH_PASSWORD','MOD4_EVAL_SSH_PASSWORD'):
  s,_=recover(name);assert s;os.environ[name]=s
 n=connect();w=connect_eval()
 try:
  prepared=json.loads((R/'PAIRED_APPROACH_PREPARED.json').read_bytes());remote=prepared['jobs'][0]['artifacts']['runtime']['path'];rows={}
  with n.open_sftp() as nf,w.open_sftp() as wf:
   for path in (remote,remote+'.partial'):
    try:st=nf.stat(path);rows[path]=dict(bytes=st.st_size,mtime=st.st_mtime)
    except FileNotFoundError:rows[path]=dict(not_generated_yet=True)
   jobs={}
   for j in prepared['jobs']:
    row={};jid=j['job_id']
    for label,f,path in (('queue',nf,E+'/eval_queue/'+jid+'.json'),('result',wf,WIN+'/jobs/'+jid+'/result.json'),('complete',wf,WIN+'/jobs/'+jid+'/complete.json')):
     try:row[label]=json.loads(f.open(path).read())
     except FileNotFoundError:row[label]=None
    jobs[jid]=row
   try:attention=json.loads(wf.open(WIN+'/E1_G3_PACKAGE_REVIEW_WORKER_ATTENTION.json').read())
   except FileNotFoundError:attention=None
   ps="[pscustomobject]@{rows=@(Get-CimInstance Win32_Process|Where-Object {$_.Name -like 'python*' -and $_.CommandLine -like '*closure_episode_clock2500_v15*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}})}|ConvertTo-Json -Depth 6 -Compress"
   _,o,e=w.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=45);b=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(b+err).decode(errors='replace');procs=json.loads(b)['rows'];ledger=json.loads(nf.open(B).read())
  v=dict(epoch=time.time(),trial_id='E1-G3-128-DISPATCH-ACTUAL-READ-01',artifact_actual=rows,jobs=jobs,attention=attention,actual_processes=procs,canonical_authorized=ledger['authorized_training_seconds'],canonical_active=ledger['active_segment'],canonical_remaining=ledger['authorized_training_seconds']-ledger['charged_training_seconds'],read_only=True)
  p=R/('PAIRED_DISPATCH_ACTUAL_'+str(int(v['epoch']))+'.json');p.write_bytes(json.dumps(v,indent=2).encode());print(json.dumps(dict(report=str(p),artifact=rows,jobs={j:dict(queued=x['queue'] is not None,result_phase=x['result'].get('phase') if x['result'] else None,complete=x['complete'] is not None) for j,x in jobs.items()},attention=attention,processes=procs,canonical_remaining=v['canonical_remaining'])))
 finally:
  n.close();w.close()
  for name in ('RM_SSH_PASSWORD','MOD4_EVAL_SSH_PASSWORD'):os.environ.pop(name,None)
if __name__=='__main__':main()
