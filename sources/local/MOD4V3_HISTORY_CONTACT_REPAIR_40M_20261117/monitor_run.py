"""Collect completed checkpoints, run10/20min independent probes, then frozen full regression."""
from pathlib import Path
import sys,json,hashlib,time,os,shlex,subprocess,traceback,datetime
T=Path(__file__).resolve().parent;R=T.parents[2];sys.path.insert(0,str(T));from remote_run import connect,execute,P,REMOTE
E=T/'evidence';W=T/'weights';J=REMOTE+'/'+P['training_job'];(E/'training').mkdir(exist_ok=True);(E/'checkpoint_evals').mkdir(exist_ok=True)
def put(p,d):
 tmp=p.with_name(p.name+'.partial');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(tmp,p)
def main():
 assert not(E/'MONITOR_COMPLETE.json').exists();models={};queue=[];active=None;completed=[];closed=False
 while True:
  try:
   c=connect()
   try:
    sf=c.open_sftp();entries=sf.listdir_attr(J)
    for f in entries:
     if f.filename.endswith('.json'):
      target=E/'training'/f.filename
      if target.exists()and target.stat().st_size==f.st_size and int(target.stat().st_mtime)==f.st_mtime:continue
      tmp=target.with_name(target.name+'.partial');sf.get(J+'/'+f.filename,str(tmp));json.loads(tmp.read_text());os.replace(tmp,target);os.utime(target,(f.st_mtime,f.st_mtime))
    for f in entries:
     n=f.filename
     if not n.startswith('model_')or not n.endswith('.pt')or n in models:continue
     target=W/n;tmp=target.with_name(n+'.partial');sf.get(J+'/'+n,str(tmp));digest=hashlib.sha256(tmp.read_bytes()).hexdigest();assert execute(c,'sha256sum -- '+shlex.quote(J+'/'+n)).split()[0]==digest;os.replace(tmp,target);models[n]=dict(path=str(target),sha256=digest,bytes=target.stat().st_size);print('CHECKPOINT',n,digest,flush=True)
     if n in ['model_005m.pt','model_010m.pt','model_020m.pt']:queue.append((str(target),'midrun'))
     if n=='model_final.pt':queue.append((str(target),'final'))
    closed=(E/'training/SAFE_CLOSED.json').exists()
    if closed:sf.get(REMOTE+'/'+P['training_job']+'.log',str(E/'training/stdout.log'))
   finally:c.close()
  except FileNotFoundError:pass
  except Exception:
   put(E/'MONITOR_LAST_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc()));print('COLLECT_RETRY',flush=True)
  if active is not None and active['process'].poll()is not None:
   completed.append(dict(model=active['model'],kind=active['kind'],exit_code=active['process'].returncode));active=None
  if active is None and queue:
   model,kind=queue.pop(0);cmd=[sys.executable,'-X','utf8','-B','-u',str(T/'evaluate_checkpoint.py'),model]+(['midrun']if kind=='midrun'else[]);log=(E/(Path(model).stem+'_eval_worker.log')).open('wb');child=subprocess.Popen(cmd,cwd=R,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT);log.close();active=dict(process=child,model=model,kind=kind);print('INDEPENDENT_EVAL',Path(model).name,kind,flush=True)
  progress=E/'training/LATEST_PROGRESS.json';d=json.loads(progress.read_text())if progress.exists()else{}
  put(E/'MONITOR_STATUS.json',dict(epoch=time.time(),pid=os.getpid(),training_elapsed_seconds=d.get('training_elapsed_seconds'),iteration=d.get('iteration'),models=models,queued=queue,active=active['model']if active else None,closed=closed,completed=completed))
  put(E/'MODEL_COLLECTION.json',models)
  if closed and not queue and active is None:
   put(E/'MONITOR_COMPLETE.json',dict(epoch=time.time(),completed=completed,closed=True,training_error=(E/'training/ERROR.json').exists(),automatic_extension=False,promoted=False))
   with(E/'finalize.log').open('wb')as log:r=subprocess.run([sys.executable,'-X','utf8','-B',str(T/'finalize_run.py')],cwd=R,stdout=log,stderr=subprocess.STDOUT)
   put(E/'FINALIZE_RECEIPT.json',dict(epoch=time.time(),exit_code=r.returncode));break
  time.sleep(20)
if __name__=='__main__':main()
