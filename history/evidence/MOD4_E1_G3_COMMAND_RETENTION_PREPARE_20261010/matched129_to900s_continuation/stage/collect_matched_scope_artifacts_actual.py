"""Actual immutable report bytes and path-size-SHA large indices, no launch or ledger write."""
from pathlib import Path
import hashlib,json,os,shlex,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
ROOTS=['MOD4_S3_E1_G3_COMMAND_RETENTION_MATCHED_20261010']
def main():
 secret,_=recover('RM_SSH_PASSWORD');os.environ['RM_SSH_PASSWORD']=secret;c=connect()
 try:
  code=r"""from pathlib import Path
import hashlib,json,time
rows=[]
for name in ROOT_VALUES:
 d=Path('/home/egde/rl_candidates')/name
 paths=list(d.glob('*.json'))+list(d.glob('*.log'))+list((d/'reports').glob('*.json'))
 for folder in ('discard_logs','learning_logs'):
  for run in (d/folder).glob('*'):
   if run.is_dir():paths+=list(run.glob('*.json'))+list(run.glob('*.pt'))+list(run.glob('*.npz'))
 for p in paths:
  try:
   a=p.stat();raw=p.read_bytes();z=p.stat()
   if (a.st_size,a.st_mtime_ns)!=(z.st_size,z.st_mtime_ns):rows.append(dict(path=str(p),dynamic_file_changed_during_read_pending=True));continue
   h=hashlib.sha256(raw).hexdigest()
   rows.append(dict(path=str(p),bytes=len(raw),sha256=h,index_only=p.suffix in ('.pt','.npz') or len(raw)>2000000,original_retained=True))
  except FileNotFoundError:rows.append(dict(path=str(p),dynamic_file_disappeared_during_read_pending=True))
print(json.dumps(dict(epoch=time.time(),files=rows,read_only=True)))
""".replace('ROOT_VALUES',repr(ROOTS))
  _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=60);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw)
  with c.open_sftp() as f:
   for x in v['files']:
    if x.get('index_only') or not x.get('sha256'):continue
    b=f.open(x['path']).read()
    if H(b)!=x['sha256']:x['changed_after_inventory_pending']=True;continue
    name=Path(x['path']).parts[4];p=D/'remote_evidence'/name/(Path(x['path']).name+'.'+x['sha256'][:12]);p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():assert p.read_bytes()==b
    else:p.write_bytes(b)
    x.update(local_capture=str(p.resolve()),byteexact=True)
  v.update(trial_id='E1-G3-COMMAND-OWN-ARTIFACT-COLLECT-01',no_GPU_PPO_signal_or_budget_mutation=True,large_originals_are_hash_indices_not_Git_binaries=True)
  p=R/('SCOPE_ARTIFACTS_COLLECTED_'+str(int(v['epoch']))+'.json');assert not p.exists();p.write_text(json.dumps(v,indent=2),encoding='utf8')
  print(json.dumps(dict(report=str(p),full_text=sum(bool(x.get('byteexact')) for x in v['files']),large_indices=sum(bool(x.get('index_only')) for x in v['files']),pending=sum(bool(x.get('dynamic_file_changed_during_read_pending') or x.get('changed_after_inventory_pending')) for x in v['files']))))
 finally:c.close();os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':
 try:main()
 except Exception:
  (R/('SCOPE_ARTIFACTS_READ_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),read_only=True)),encoding='utf8');raise
