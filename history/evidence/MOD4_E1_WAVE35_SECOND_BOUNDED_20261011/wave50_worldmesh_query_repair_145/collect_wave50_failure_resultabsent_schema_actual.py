"""Collect actual retained_failed evidence even when worker attention is expected; no restart/replay."""
from second_io import *
from curb_io import WIN
import base64
def main():
 pub=json.loads((R/'WAVE50_FROZEN_PUBLISHED.json').read_bytes());jid=pub['jobs'][0]['job_id'];n,w=io.connect_both();rows=[];dest=D/('wave50_failed_actual_'+str(time.time_ns()));dest.mkdir()
 try:
  with n.open_sftp() as nf,w.open_sftp() as wf:
   names=wf.listdir(WIN+'/jobs/'+jid);r=json.loads(wf.open(WIN+'/jobs/'+jid+'/result.json').read());assert r['phase']=='retained_failed' and not r['result_present'] and r['error_files']==['probe.json.error.txt']
   for name in names:
    if not name.endswith(('.json','.txt','.log')):continue
    raw=wf.open(WIN+'/jobs/'+jid+'/'+name).read();p=dest/name;p.write_bytes(raw);back=None
    try:back=nf.open(io.E+'/eval_results/'+jid+'/'+name).read()
    except FileNotFoundError:pass
    rows.append(dict(source=WIN+'/jobs/'+jid+'/'+name,local=str(p),bytes=len(raw),sha256=H(raw),bridge_bytes_exact=back==raw if back is not None else None))
   assert next(x for x in rows if x['local'].endswith('result.json'))['bridge_bytes_exact']
   attention_raw=wf.open(WIN+'/E1_SLOPE8_QUERY_REVIEW_WORKER_ATTENTION.json').read();(dest/'worker_attention.json').write_bytes(attention_raw)
   base=wf.open(WIN+'/eval_worker_closure2500.py').read();worker=wf.open(WIN+'/eval_worker_e1_slope8_query_review.py').read();(dest/'baseguard_source.py').write_bytes(base);(dest/'worker_source.py').write_bytes(worker)
   ps="[pscustomobject]@{rows=@(Get-CimInstance Win32_Process|Where-Object {$_.Name -like 'python*' -and $_.CommandLine -like '*closure_episode_clock2500_v15*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}})}|ConvertTo-Json -Depth 6 -Compress"
   _,o,e=w.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');processes=json.loads(raw)['rows']
   out=save('WAVE50_144_FAILED_ACTUAL_COLLECTION_'+str(time.time_ns())+'.json',dict(epoch=time.time(),job_id=jid,result=r,evidence=rows,actual_attention=json.loads(attention_raw),actual_processes=processes,worker_source_SHA=H(worker),baseguard_SHA=H(base),original_failed_scope_not_relabelled=True,no_GPU_PPO_queue_budget_or_signal_action=True))
   print(json.dumps(dict(report=str(out),result=r,evidence=rows,processes=processes)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('WAVE50_FAILED_COLLECTION_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only=True));raise
