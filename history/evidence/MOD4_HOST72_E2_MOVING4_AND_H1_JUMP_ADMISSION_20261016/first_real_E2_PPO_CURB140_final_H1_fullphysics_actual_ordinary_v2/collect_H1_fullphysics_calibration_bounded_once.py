"""Own finite diagnostic data/exit collection, no repeated probes or runtime changes."""
from pathlib import Path
import json,time,os,getpass,paramiko,shlex,hashlib,traceback,subprocess
D=Path(__file__).resolve().parent;R=D/'reports';ROOT='/home/lc01/Zonglin Li/zonglin2/tasks/'+D.name+'/h1_flat_fullphysics_calibration_v1';PY='/home/lc01/Zonglin Li/zonglin2/run-python.sh'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 put('H1_CALIBRATION_BOUND_COLLECTION_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),creation_UTC=subprocess.check_output(['powershell','-NoProfile','-Command',"(Get-Process -Id %d).StartTime.ToUniversalTime().ToString('o')"%os.getpid()]).decode().strip(),maximum_seconds=900,only_same_connection_own_scope=True));pw=getpass.getpass('Host72 own calibration read-only collection password (hidden): ');c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());sf=None
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,look_for_keys=False,allow_agent=False);pw=None;assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795';start=time.monotonic()
  script='ROOT='+repr(ROOT)+'\n'+r'''
from pathlib import Path
import json,time,psutil,hashlib
B=Path(ROOT);files=[]
for p in list(B.glob('*.json'))+list((B/'output').glob('*.json')):
 if p.stat().st_size<5000000:
  try:files.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest(),value=json.loads(p.read_bytes())))
  except (ValueError,OSError):pass
procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if any(str(B) in z for z in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
p=B/'worker.log';tail=''
if p.exists():
 with p.open('rb') as f:f.seek(max(0,p.stat().st_size-3000));tail=f.read().decode(errors='replace')
print(json.dumps(dict(epoch=time.time(),files=files,actual_processes=procs,worker_tail=tail,parent_final=(B/'PARENT_FINAL.json').exists(),parent_exit=(B/'PARENT_EXIT_ACTUAL.json').exists(),errors=[x for x in files if 'ORIGINAL_ERROR' in x['path']])))
'''
  while True:
   si,so,se=c.exec_command(shlex.quote(PY)+' -B -',timeout=45);si.write(script);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();assert so.channel.recv_exit_status()==0,err.decode();v=json.loads(raw)
   if (v['parent_final'] and v['parent_exit'] and not v['actual_processes']) or time.monotonic()-start>=900:break
   time.sleep(15)
  if v['parent_exit'] and not v['actual_processes']:
   index=next((x['value'] for x in v['files'] if x['path'].endswith('/VALID_PREFIX_INDEX_ACTUAL.json')),None);rows=[]
   if index:rows=index['physics']+index['controls']
   sf=c.open_sftp();sf.get_channel().settimeout(120);collected=[];outdir=D/'H1_fullphysics_calibration_actual_raw';outdir.mkdir()
   for r in rows:
    out=outdir/Path(r['path']).name;part=out.with_suffix(out.suffix+'.partial');sf.get(r['path'],str(part));assert part.stat().st_size==r['bytes'] and H(part)==r['SHA'];part.replace(out);collected.append(dict(path=str(out.resolve()),bytes=out.stat().st_size,SHA=H(out),remote=r['path'],twohost_bytes_SHA_exact=True))
   v['complete_local_raw']=collected
  put('H1_FULLPHYSICS_CALIBRATION_ACTUAL_BOUND_COLLECTION.json',v);print(json.dumps(dict(parent_final=next((x['value'] for x in v['files'] if x['path'].endswith('/PARENT_FINAL.json')),None),errors=v['errors'],actual_processes=v['actual_processes'],local_raw_files=len(v.get('complete_local_raw',[])),worker_tail=v['worker_tail'][-1200:])),flush=True)
 finally:
  pw=None
  if sf:sf.close()
  c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('H1_CALIBRATION_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_replay=True));raise
