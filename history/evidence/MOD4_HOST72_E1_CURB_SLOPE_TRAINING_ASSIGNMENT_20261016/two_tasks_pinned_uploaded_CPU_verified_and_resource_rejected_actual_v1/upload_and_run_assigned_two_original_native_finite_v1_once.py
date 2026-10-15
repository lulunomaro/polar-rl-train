from pathlib import Path
import getpass,hashlib,json,os,shlex,subprocess,tarfile,time,traceback,paramiko
D=Path(__file__).resolve().parent;Q=D/'payload';R=D/'reports';ROOT='/home/lc01/Zonglin Li/zonglin2'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 assert not (R/'TWO_ASSIGNED_ORIGINAL_NATIVE_UPLOAD_STARTED_ACTUAL.json').exists()
 archive=D/'two_E1_assigned_jobs_original_native_v1.tar.gz';assert not archive.exists()
 with tarfile.open(archive,'w:gz',compresslevel=1) as t:
  for p in sorted(Q.rglob('*')):
   if p.is_file():t.add(p,arcname=p.relative_to(Q).as_posix(),recursive=False)
 meta=dict(path=str(archive),bytes=archive.stat().st_size,sha256=sha(archive))
 put(R/'TWO_ASSIGNED_ORIGINAL_NATIVE_BUNDLE_ACTUAL.json',meta)
 c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());sf=None
 pw=getpass.getpass('Host72 SSH password (hidden, never saved): ')
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False);pw=None
  assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
  sf=c.open_sftp();sf.get_channel().settimeout(60)
  ci=subprocess.run(['powershell','-NoProfile','-Command','$p=Get-CimInstance Win32_Process -Filter "ProcessId = '+str(os.getpid())+'";$p|Select-Object ProcessId,CreationDate,CommandLine|ConvertTo-Json -Compress'],capture_output=True,text=True,encoding='utf8',check=True)
  put(R/'TWO_ASSIGNED_ORIGINAL_NATIVE_UPLOAD_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_CIM=json.loads(ci.stdout),argv=__import__('sys').argv,exclusive_target72_transport_while_actual_alive=True,original210_not_connected=True,native_only_no_PPO=True))
  target=ROOT+'/downloads/'+archive.name
  with archive.open('rb') as src,sf.open(target,'wx') as dst:
   while b:=src.read(4*1024*1024):dst.write(b)
  with sf.open(ROOT+'/audit/two_E1_assigned_jobs_original_native_v1_manifest.json','wx') as f:f.write(json.dumps(meta).encode())
  controller=Q/'host72_two_jobs_original_native_controller_v1.py';remote=ROOT+'/audit/'+controller.name
  with sf.open(remote,'wx') as f:f.write(controller.read_bytes())
  _,so,se=c.exec_command('python3 -B '+shlex.quote(remote),timeout=1900)
  # Controller only writes logs/files; no high-volume channel output.
  out=so.read();err=se.read();rc=so.channel.recv_exit_status()
  put(R/'TWO_ASSIGNED_ORIGINAL_NATIVE_FINITE_COMMAND_ACTUAL.json',dict(epoch=time.time(),returncode=rc,stdout=out.decode(errors='replace'),stderr=err.decode(errors='replace')))
  base=ROOT+'/tasks/'+D.name;rows=[]
  def walk(path):
   for s in sf.listdir_attr(path):
    p=path+'/'+s.filename
    if s.st_mode&0o170000==0o040000:
     if s.filename not in ('runtime','assets','source','__pycache__'):walk(p)
    elif s.st_mode&0o170000==0o100000:
     if s.filename.endswith(('.json','.log','.txt','.pt','.npz')):
      h=hashlib.sha256();local=D/'actual_target72'/Path(p[len(base)+1:]);download=s.st_size<=32*1024*1024
      if download:local.parent.mkdir(parents=True,exist_ok=True);dest=local.open('xb')
      with sf.open(p,'rb') as f:
       while b:=f.read(4*1024*1024):
        h.update(b)
        if download:dest.write(b)
      if download:dest.close()
      rows.append(dict(remote_path=p,bytes=s.st_size,sha256=h.hexdigest(),local_path=str(local) if download else None,large_original_retained=not download))
  walk(base)
  # Capture controller errors from this own scope too.
  for n in sf.listdir(ROOT+'/audit'):
   if n.startswith('TWO_ORIGINAL_NATIVE_CONTROLLER_ORIGINAL_ERROR_'):
    with sf.open(ROOT+'/audit/'+n,'rb') as f:b=f.read()
    p=D/'actual_target72'/n;p.parent.mkdir(exist_ok=True);p.write_bytes(b)
  put(R/'TWO_ASSIGNED_ORIGINAL_NATIVE_ALL_OUTPUTS_ACTUAL.json',dict(epoch=time.time(),returncode=rc,rows=rows,no_replay_or_learning_claim=True))
  print(json.dumps(dict(returncode=rc,files=len(rows),stdout=out.decode(errors='replace'),stderr=err.decode(errors='replace')[-2000:])),flush=True)
 finally:
  pw=None
  if sf:sf.close()
  c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put(R/('TWO_ASSIGNED_ORIGINAL_NATIVE_UPLOAD_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_blind_replay=True));raise
