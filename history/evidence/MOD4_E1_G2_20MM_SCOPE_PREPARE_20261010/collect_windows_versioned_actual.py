"""Read current3060 output independently; preserve prior reports and disclose missing central proof."""
from pathlib import Path
import os,sys,json,base64,hashlib,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
WIN='D:/MOD4_async_eval/closure_episode_clock2500_v15';JID='clk2500-closure-episode-d3-122-e1-g2-20mm-source32053-fullroute-flat'
def save(p,b):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert p.read_bytes()==b,str(p)
 else:p.write_bytes(b)
def main():
 secret,_=recover('MOD4_EVAL_SSH_PASSWORD');assert secret;os.environ['MOD4_EVAL_SSH_PASSWORD']=secret;c=connect_eval();receipts={};files=[];cases={};pending=[]
 try:
  with c.open_sftp() as f:
   for name in ('STARTED','STATE','ATTENTION','ADMITTED'):
    try:b=f.open(WIN+'/E1_ARTIFACT_SOURCE_REVIEW_WORKER_'+name+'.json').read()
    except FileNotFoundError:receipts[name]=None;continue
    receipts[name]=json.loads(b)
   src=f.open(WIN+'/eval_worker_e1_artifact_source_review.py').read();assert src==(D/'eval_worker_e1_artifact_source_review.py').read_bytes()
   folder=R/'windows_independent'/JID;row={}
   for name in ('manifest.json','result.json','probe.json'):
    try:b=f.open(WIN+'/jobs/'+JID+'/'+name).read()
    except FileNotFoundError:continue
    save(folder/name,b);row[name[:-5]]=json.loads(b);files.append(dict(source=WIN+'/jobs/'+JID+'/'+name,path=str((folder/name).resolve()),bytes=len(b),sha256=H(b),central_return_not_yet_verified=True))
   result=row.get('result')
   if result and result['phase']=='complete' and not result['exit_code'] and not result['errors'] and not result['error_files']:
    expected=json.loads((R/'REPAIRED_PUBLISHED.json').read_bytes())['jobs'][0];assert row['manifest']==expected
    p=row['probe'];info=p['full_route_raw'];out=folder/info['name']
    if not out.exists():
     part=out.with_suffix(out.suffix+'.part');assert not part.exists();f.get(WIN+'/jobs/'+JID+'/'+info['name'],str(part));assert part.stat().st_size==info['bytes'] and H(part.read_bytes())==info['sha256'];part.rename(out)
    assert out.stat().st_size==info['bytes'] and H(out.read_bytes())==info['sha256'];row['raw_SHA_exact']=True
    files.append(dict(source=WIN+'/jobs/'+JID+'/'+info['name'],path=str(out.resolve()),bytes=info['bytes'],sha256=info['sha256'],large_original_index_only=True));cases[JID]=row
   else:pending.append(dict(job_id=JID,result=result,phase='pending_actual_complete_or_errorfree'))
  ps="[pscustomobject]@{processes=@(Get-CimInstance Win32_Process|Where-Object {$_.Name -match '^python' -and $_.CommandLine -like '*closure_episode_clock2500_v15*'}|Select-Object ProcessId,ParentProcessId,CommandLine,@{n='creation_epoch';e={([DateTimeOffset]$_.CreationDate).ToUnixTimeMilliseconds()/1000}})}|ConvertTo-Json -Compress -Depth 6"
  _,o,e=c.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0;procs=json.loads(raw)['processes']
  report=dict(epoch=time.time(),trial_id='E1-G2-WINDOWS-VERSIONED-ACTUAL-READ-02',receipts=receipts,cases=cases,pending=pending,files=files,processes=procs,source_SHA_exact=True,current_attention=receipts['ATTENTION'],central_bridge_bytes_not_yet_verified=True,no_queue_GPU_PPO_or_canonical_write=True)
  path=R/('WINDOWS_VERSIONED_ACTUAL_'+str(int(report['epoch']))+'.json');save(path,json.dumps(report,indent=2).encode());print(json.dumps(dict(report=str(path),complete=list(cases),pending=pending,current_attention=report['current_attention'],processes=procs),ensure_ascii=True))
 finally:c.close();os.environ.pop('MOD4_EVAL_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:
  save(R/('WINDOWS_VERSIONED_ERROR_'+str(int(time.time()))+'.json'),json.dumps(dict(epoch=time.time(),trial_id='E1-G2-WINDOWS-VERSIONED-ACTUAL-READ-02',error=traceback.format_exc(),read_only=True),indent=2).encode());raise
