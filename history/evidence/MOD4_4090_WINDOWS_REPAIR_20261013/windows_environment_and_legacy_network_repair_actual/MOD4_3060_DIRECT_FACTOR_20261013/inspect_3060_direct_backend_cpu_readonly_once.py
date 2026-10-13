"""One authorized readonly connection to host249. No RPC / 210 / GPU launch.

Collect installed SDK source and actual OS lock/process boundary to prepare the
new direct-local backend. Credentials remain transient and are never serialized.
"""
from pathlib import Path
import sys, os, json, time, base64, hashlib, traceback

D=Path(__file__).resolve().parent;W=D.parent
R=D/'reports';S=D/'sdk_readonly_source'
CODE=r'''
from pathlib import Path
import importlib.metadata as m,importlib.util,json,time,hashlib,psutil,socket,msvcrt,os
names=['isaacsim','isaaclab','isaaclab-rl','isaaclab-physx','isaaclab-isaacsim','torch','tensordict','rsl-rl-lib','warp-lang','numpy','scipy','gymnasium']
packages=[]; roots=[]; errors=[]
for name in names:
 try:
  d=m.distribution(name); row=dict(name=name,version=d.version,metadata_root=str(d._path))
  p=Path(d._path)/'direct_url.json'
  if p.exists():
   u=json.loads(p.read_bytes());url=u.get('url','')
   assert url.startswith('file:') or not u.get('dir_info',{}).get('editable'), 'Unexpected editable URL'
   row['direct_url']=u
   if url.startswith('file:///'):
    from urllib.parse import unquote
    path=Path(unquote(url[8:]));row['editable_source_root']=str(path);roots.append(path)
  row['requires_dist']=d.metadata.get_all('Requires-Dist') or []
  packages.append(row)
 except m.PackageNotFoundError:packages.append(dict(name=name,absent=True))
for top in ['isaaclab','isaaclab_rl','isaaclab_physx','isaaclab_isaacsim','rsl_rl']:
 try:
  sp=importlib.util.find_spec(top)
  if sp:
   roots += [Path(p).parent for p in (sp.submodule_search_locations or [])]
 except Exception as e:errors.append(dict(scope='find_spec '+top,error=repr(e)))
roots=list(dict.fromkeys(str(p) for p in roots if p.exists()))
relative_targets={
 'isaaclab/sim/simulation_cfg.py','isaaclab/envs/manager_based_rl_env.py',
 'isaaclab/envs/manager_based_env.py','isaaclab/assets/articulation/articulation.py',
 'isaaclab/assets/articulation/articulation_data.py','isaaclab/assets/articulation/articulation_cfg.py',
 'isaaclab/sensors/contact_sensor/contact_sensor.py','isaaclab/sensors/contact_sensor/contact_sensor_data.py',
 'isaaclab/utils/math.py','isaaclab/scene/interactive_scene.py','isaaclab/sim/__init__.py',
 'isaaclab/assets/__init__.py','isaaclab/sensors/__init__.py','isaaclab/app/app_launcher.py',
 'isaaclab_rl/rsl_rl/vecenv_wrapper.py','isaaclab_rl/rsl_rl/__init__.py',
 'isaaclab_physx/physics.py','isaaclab_physx/sim/physics.py','isaaclab_physx/__init__.py',
 'isaaclab_physx/assets/articulation/articulation.py','isaaclab_physx/assets/articulation/articulation_data.py',
 'isaaclab_physx/sensors/contact_sensor/contact_sensor.py','isaaclab_isaacsim/__init__.py',
 'rsl_rl/runners/on_policy_runner.py','rsl_rl/modules/actor_critic.py',
}
files=[]
for root in roots:
 for rel in sorted(relative_targets):
  p=Path(root)/rel
  if p.is_file():
   b=p.read_bytes();assert len(b)<=700000
   files.append(dict(path=str(p),relative_api=rel,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
files=list({r['path']:r for r in files}.values())
identities=[]
for p in psutil.process_iter(['pid','create_time','name','exe','cmdline','ppid']):
 try:
  a=p.info;argv=a.get('cmdline') or [];joined=' '.join(argv).lower()
  if any(s in joined for s in ['eval_worker','factor','mirror_target_tui','isaac','kit.exe','python']) or 'kit' in (a.get('name') or '').lower():
   safe=[]; hide=False
   for arg in argv:
    if hide:safe.append('[REDACTED]');hide=False;continue
    if any(s in arg.lower() for s in ['password','passwd','secret','token=','private key']):safe.append('[REDACTED_ARGUMENT]');hide=True
    else:safe.append(arg)
   a['cmdline']=safe;identities.append(a)
 except (psutil.NoSuchProcess,psutil.AccessDenied):pass
lock=Path('D:/MOD4_async_eval/worker.lock'); lock_receipt=dict(path=str(lock),exists=lock.exists(),probe_without_file_creation=True)
if lock.exists():
 try:
  with lock.open('rb') as f:
   f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
   f.seek(0);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)
  lock_receipt['actual_OS_lock_free']=True
 except OSError as e:
  lock_receipt.update(actual_OS_lock_free=False,error_type=type(e).__name__,winerror=getattr(e,'winerror',None),errno=e.errno)
outbound=[]
for c in psutil.net_connections(kind='tcp'):
 if c.raddr and c.raddr.ip in ['10.24.4.210','172.27.131.74']:
  outbound.append(dict(remote=list(c.raddr),status=c.status,pid=c.pid))
print(json.dumps(dict(epoch=time.time(),hostname=socket.gethostname(),packages=packages,SDK_source_roots=roots,SDK_API_files=files,
 process_identities=identities,shared_lock=lock_receipt,target210_or_ZT_outbound=outbound,errors=errors,
 readonly=True,no_Isaac_or_CUDA_import=True,no_GPU_no_RPC_no_OS_process_mutation=True,no_connect210=True)))
'''

def main():
    R.mkdir(parents=True,exist_ok=True);S.mkdir(parents=True,exist_ok=True)
    assert not (R/'DIRECT3060_READONLY_CPU_SDK_API_ACTUAL.json').exists()
    compile(CODE,'<remote only readonly metadata source>','exec')
    sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'))
    from reuse_authorized_session_transport import recover
    secret,_=recover('MOD4_EVAL_SSH_PASSWORD');assert secret
    os.environ['MOD4_EVAL_SSH_PASSWORD']=secret
    sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'))
    from eval_remote_io import connect_eval
    c=connect_eval();sf=None
    try:
        enc=base64.b64encode(CODE.encode()).decode()
        command='"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" -X utf8 -c "import base64;exec(base64.b64decode(\''+enc+'\'))"'
        _,o,e=c.exec_command(command,timeout=60);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
        assert rc==0,('Read-only collector failed',rc,err.decode('utf8','replace'))
        a=json.loads(raw);sf=c.open_sftp();capture=[]
        for idx,row in enumerate(a['SDK_API_files']):
            with sf.open(row['path'].replace('\\','/'),'rb') as f:b=f.read()
            assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
            target=S/(str(idx)+'_'+row['relative_api'].replace('/','__'))
            assert not target.exists();target.write_bytes(b)
            capture.append(dict(**row,local_path=str(target),remote_bytes_local_exact=True))
        a['SDK_source_capture']=capture
        a['preparation_readonly_search_error']={'error':'rg os error5 access denied on unrelated rmuc2026_work/unpack_verify_4zomhj13','scope':'local file search only','no_GPU_or_remote_contact':True}
        p=R/'DIRECT3060_READONLY_CPU_SDK_API_ACTUAL.json';p.write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8')
        print(json.dumps({'report':str(p),'metadata_versions':{p['name']:p.get('version') for p in a['packages']},'captured_API_files':len(capture),'shared_lock':a['shared_lock'],'target210_connections':len(a['target210_or_ZT_outbound']),'process_count':len(a['process_identities'])}),flush=True)
    except Exception as e:
        p=R/'DIRECT3060_READONLY_CPU_SDK_API_ORIGINAL_ERROR.json'
        assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),error=repr(e),traceback=traceback.format_exc(),no_GPU_or_remote_process_mutation=True),ensure_ascii=False,indent=2),encoding='utf8');raise
    finally:
        if sf:sf.close()
        c.close();os.environ.pop('MOD4_EVAL_SSH_PASSWORD',None)

if __name__=='__main__':main()
