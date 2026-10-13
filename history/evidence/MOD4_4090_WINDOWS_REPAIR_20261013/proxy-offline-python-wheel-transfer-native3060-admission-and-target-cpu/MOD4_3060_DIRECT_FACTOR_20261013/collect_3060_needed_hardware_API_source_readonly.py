"""One additional necessary readonly SFTP source capture; no remote execution."""
from pathlib import Path
import sys,os,json,time,hashlib,stat,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';S=D/'sdk_hardware_readonly_source'
def main():
 assert not (R/'DIRECT3060_NEEDED_HARDWARE_API_SOURCE_ACTUAL.json').exists()
 sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'))
 from reuse_authorized_session_transport import recover
 secret,_=recover('MOD4_EVAL_SSH_PASSWORD');assert secret;os.environ['MOD4_EVAL_SSH_PASSWORD']=secret
 sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'))
 from eval_remote_io import connect_eval
 c=connect_eval();sf=None
 try:
  sf=c.open_sftp();S.mkdir();files=[];directories=[]
  initial=json.loads((R/'DIRECT3060_READONLY_CPU_SDK_API_ACTUAL.json').read_text(encoding='utf8'))
  lab=next(p['editable_source_root'] for p in initial['packages'] if p['name']=='isaaclab')
  physx=next(p['editable_source_root'] for p in initial['packages'] if p['name']=='isaaclab-physx')
  targets=[(lab,'isaaclab/actuators'),(lab,'isaaclab/utils/warp'),(physx,'isaaclab_physx/physics')]
  for root,rel in targets:
   remote=(root+'/'+rel).replace('\\','/');entries=sf.listdir_attr(remote)
   directories.append(dict(path=remote,entries=[e.filename for e in entries]))
   for e in entries:
    if not stat.S_ISREG(e.st_mode) or not e.filename.endswith('.py'):continue
    p=remote+'/'+e.filename
    with sf.open(p,'rb') as f:b=f.read()
    assert len(b)<=700000
    out=S/(rel.replace('/','__')+'__'+e.filename);assert not out.exists();out.write_bytes(b)
    files.append(dict(path=p,relative_API=rel+'/'+e.filename,local_path=str(out),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),remote_bytes_local_exact=True))
  report=dict(epoch=time.time(),host='10.24.4.249',read_only=True,remote_SFTP_only_no_Python_Kit_or_GPU_launch=True,no_connect210_or_RPC=True,
   targeted_directories=directories,source_files=files,installed_SDK_not_changed=True)
  out=R/'DIRECT3060_NEEDED_HARDWARE_API_SOURCE_ACTUAL.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
  print(json.dumps({'report':str(out),'source_files':len(files),'API_names':[f['relative_API'] for f in files]}),flush=True)
 except Exception as e:
  out=R/'DIRECT3060_NEEDED_HARDWARE_API_SOURCE_ORIGINAL_ERROR.json';assert not out.exists()
  out.write_text(json.dumps(dict(epoch=time.time(),error=repr(e),traceback=traceback.format_exc(),read_only=True,no_GPU=True),indent=2),encoding='utf8');raise
 finally:
  if sf:sf.close()
  c.close();os.environ.pop('MOD4_EVAL_SSH_PASSWORD',None)
if __name__=='__main__':main()
