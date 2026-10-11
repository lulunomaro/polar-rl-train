"""Read current worker attention and failed136 raw without any signal or restart."""
from slope_io import *
sys.path.insert(0,str(W/'MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011'))
from curb_io import WIN
import traceback,base64

def main():
 n,w=connect_both();jid='clk2500-closure-episode-d3-136-e1-slope8-source404-mirrored-fullroute-flat'
 try:
  with n.open_sftp() as nf,w.open_sftp() as wf:
   report={};files=[]
   for name in ('E1_G3_PACKAGE_REVIEW_WORKER_ATTENTION.json','E1_G3_PACKAGE_REVIEW_WORKER_STATE.json','E1_G3_PACKAGE_REVIEW_WORKER_STARTED.json'):
    try:raw=wf.open(WIN+'/'+name).read();report[name]=dict(sha256=H(raw),bytes=len(raw),data=json.loads(raw))
    except FileNotFoundError:report[name]=None
   folder=WIN+'/jobs/'+jid
   for a in wf.listdir_attr(folder):
    files.append(dict(name=a.filename,bytes=a.st_size))
    if a.filename.endswith(('.json','.log','.txt')):
     raw=wf.open(folder+'/'+a.filename).read();dest=R/'failed136'/a.filename;dest.parent.mkdir(exist_ok=True)
     if dest.exists():assert dest.read_bytes()==raw
     else:dest.write_bytes(raw)
     report[a.filename]=dict(bytes=len(raw),sha256=H(raw),text=raw.decode(errors='replace')[-50000:])
   ps="[pscustomobject]@{rows=@(Get-CimInstance Win32_Process|Where-Object {$_.Name -like 'python*' -and $_.CommandLine -like '*closure_episode_clock2500_v15*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}})}|ConvertTo-Json -Depth 6 -Compress"
   _,o,e=w.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0;processes=json.loads(raw)
   p=save('SLOPE136_FAILURE_ACTUAL_'+str(time.time_ns())+'.json',dict(epoch=time.time(),trial_id='SLOPE136-FAILED-FROZEN-ACTUAL-READ-01',job_id=jid,files=files,evidence=report,processes=processes,no_signal_restart_or_budget=True))
   print(json.dumps(dict(report=str(p),files=files,evidence={k:v for k,v in report.items() if k.endswith('result.json') or 'ATTENTION' in k or 'error' in k.lower()},processes=processes),ensure_ascii=True))
 finally:cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:save('SLOPE136_FAILURE_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only=True));raise
