"""One finite read-only connection to the new production root; never dispatch."""
from pathlib import Path
import hashlib,json,shlex,sys,time,traceback,subprocess,os
D=Path(__file__).resolve().parent;R=D/'reports';ROOT='/mnt/mod4_linux_durable_20261013/'+D.name+'/production_fresh_process_v2'
sys.path.insert(0,str(D.parent/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as t
CODE=r'''
from pathlib import Path
import json,psutil,time,hashlib
B=Path(ROOT);files=[]
for p in list(B.glob('OWNER_*.json'))+list(B.glob('*EXIT_ACTUAL.json'))+list(B.glob('GO_PRODUCTION_ACTUAL.json'))+list(B.glob('WORKER_STARTED_ACTUAL.json'))+list(B.glob('job0/production_only/*.json')):
 if p.stat().st_size<2000000:
  try:files.append(dict(path=str(p),value=json.loads(p.read_bytes())))
  except (OSError,ValueError):pass
errors=[x for x in files if 'ORIGINAL_ERROR' in x['path'] or 'REJECTED' in x['path']]
logs=[]
for p in B.glob('job0/*.log'):
 with p.open('rb') as f:f.seek(max(0,p.stat().st_size-7000));s=f.read().decode(errors='replace')
 logs.append(dict(path=str(p),tail=s))
first=B/'job0/production_only/model_update1.pt';row=None
if first.exists() and not first.with_suffix('.pt.partial').exists():row=dict(path=str(first),bytes=first.stat().st_size,SHA=hashlib.sha256(first.read_bytes()).hexdigest())
c=json.loads(Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json').read_bytes())
procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if any(str(B) in x for x in p.info['cmdline'] or []) and any('curb35_production_owner_v2.py' in x or 'curb35_production_worker_v2.py' in x for x in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
print(json.dumps(dict(epoch=time.time(),files=files,errors=errors,logs=logs,first_production=row,actual_own_processes=procs,canonical={k:c[k] for k in ('active_segment','charged_training_seconds','remaining_training_seconds')})))
'''
def put(n,x):
 with (R/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2)
def main():
 put('FRESH_V2_FIRST_PRODUCTION_BOUND_COLLECTION_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),creation_UTC=subprocess.check_output(['powershell','-NoProfile','-Command',"(Get-Process -Id %d).StartTime.ToUniversalTime().ToString('o')"%os.getpid()]).decode().strip(),bounded_seconds=900,own_root=ROOT,no_signal_or_dispatch=True));c=sf=None;start=time.monotonic()
 try:
  c=t.connect()
  while True:
   si,so,se=c.exec_command(shlex.quote(t.PY)+' -B -',timeout=40);si.write('ROOT='+repr(ROOT)+'\n'+CODE);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();v=json.loads(raw)
   if v['first_production'] or v['errors'] or time.monotonic()-start>=900:
    put('CURB35_FRESH_V2_FIRST_BOUND_ACTUAL_STATE_'+str(time.time_ns())+'.json',v)
    if v['first_production']:
     r=v['first_production'];out=D/'first_actual_models_fresh_v2/model_update1.pt';out.parent.mkdir();part=out.with_suffix('.pt.partial');sf=c.open_sftp();sf.get_channel().settimeout(120);sf.get(r['path'],str(part));assert part.stat().st_size==r['bytes'] and hashlib.sha256(part.read_bytes()).hexdigest()==r['SHA'];part.replace(out);v['first_local_model']=str(out.resolve());v['twohost_bytes_SHA_complete']=True
    put('CURB35_FRESH_V2_FIRST_PRODUCTION_BOUND_COLLECTION_COMPLETE_ACTUAL.json',v);print(json.dumps(dict(first_production=v['first_production'],error_paths=[x['path'] for x in v['errors']],canonical=v['canonical'],last_worker_tail=v['logs'][-1]['tail'][-1800:] if v['logs'] else '')),flush=True);return
   time.sleep(15)
 finally:
  if sf:sf.close()
  t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:
  put('CURB35_FRESH_V2_FIRST_BOUND_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only_no_GPU_replay=True));raise
