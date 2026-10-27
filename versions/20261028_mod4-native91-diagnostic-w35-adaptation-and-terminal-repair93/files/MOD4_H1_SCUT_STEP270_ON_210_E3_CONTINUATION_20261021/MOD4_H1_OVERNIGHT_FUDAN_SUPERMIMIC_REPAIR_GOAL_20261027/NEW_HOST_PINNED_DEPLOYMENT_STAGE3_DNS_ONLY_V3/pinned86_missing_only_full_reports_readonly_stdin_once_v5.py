from pathlib import Path
import sys,json,time,socket,hashlib,paramiko,stat,os
HERE=Path(__file__).resolve().parent;R=HERE/'reports';ROOT='/data/robemo/polar-rl-train';DEADLINE=min(time.time()+45,1793118240.)
def save(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 print('READY_FOR_SINGLE_STDIN_JSON',flush=True);req=json.loads(sys.stdin.readline());assert set(req)=={'host','username','password'} and req['host']=='10.50.0.86' and req['username']=='robemo'
 secret=req.pop('password');t=None;sf=None
 try:
  assert time.time()<DEADLINE-15,'logs-only insufficient finite time'
  sock=socket.create_connection((req['host'],22),timeout=10);t=paramiko.Transport(sock);t.start_client(timeout=10);assert hashlib.sha256(t.get_remote_server_key().asbytes()).hexdigest()=='8adc87f3e75eb307a2429fa97b68761e09c0636b0eea684c71894438757c788b';t.auth_password(req['username'],secret,fallback=False);secret=None
  sf=paramiko.SFTPClient.from_transport(t);sf.get_channel().settimeout(10)
  with sf.open(ROOT+'/.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json','rb') as f:m=json.loads(f.read())
  assert m['initial_probe_id']=='MOD4_NEW_HOST_INITIAL_PROBE_1793110077908242700' and m['authorized_root']==ROOT
  target=R/'missing_only_all_full_original_UTF8_previous_runs';target.mkdir();rows=[]
  for run in [ROOT+'/setup_runs/W35_PINNED_ENV_STAGE1_20261027_V1',ROOT+'/setup_runs/W35_PINNED_ENV_STAGE2_20261028_V2']:
   with sf.open(run+'/SETUP_RUN_OWNER.json','rb') as f:m=json.loads(f.read())
   assert m['root']==ROOT and m['new_run']==run
   files=[(run,x) for x in sf.listdir_attr(run) if stat.S_ISREG(x.st_mode) and x.filename.endswith(('.json','.txt','.log'))]
   files += [(run+'/logs',x) for x in sf.listdir_attr(run+'/logs') if stat.S_ISREG(x.st_mode) and x.filename.endswith(('.json','.txt','.log'))]
   for directory,a in files:
    assert time.time()<DEADLINE-3;path=directory+'/'+a.filename;before=sf.stat(path)
    with sf.open(path,'rb') as f:raw=f.read()
    after=sf.stat(path);assert (before.st_size,before.st_mtime)==(after.st_size,after.st_mtime)
    rel=path[len(ROOT)+1:];local=target/(hashlib.sha256(rel.encode()).hexdigest()[:20]+'_'+a.filename)
    with local.open('xb') as f:f.write(raw)
    raw.decode('utf8');rows.append(dict(remote_path=path,local_path=str(local),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),complete_original_UTF8=True))
  value=dict(passed=True,actual_finite_returned=True,epoch=time.time(),rows=rows,read_only_no_remote_write_or_model_or_GPU_or_install=True)
  save('MISSING_ONLY_FULL_ORIGINAL_REPORTS_RETURNED_ACTUAL_V5.json',value);print(json.dumps(dict(passed=True,actual_finite_returned=True,complete_original_files=len(rows))),flush=True)
 except BaseException as e:
  msg=str(e)
  if secret:msg=msg.replace(secret,'[REDACTED]')
  save('MISSING_ONLY_FULL_REPORTS_ORIGINAL_ERROR_ACTUAL_V5.json',dict(error_type=type(e).__name__,error=msg,epoch=time.time()));raise
 finally:
  secret=None
  if sf:sf.close()
  if t:t.close()
if __name__=='__main__':main()
