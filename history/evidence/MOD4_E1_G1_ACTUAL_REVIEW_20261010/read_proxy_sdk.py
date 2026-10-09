from pathlib import Path
import os,sys,json,hashlib,time
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
secret,_=recover('MOD4_EVAL_SSH_PASSWORD');assert secret;os.environ['MOD4_EVAL_SSH_PASSWORD']=secret;c=connect_eval()
root='D:/claude2/fangzhen/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab/utils/warp'
try:
 with c.open_sftp() as f:
  files=[]
  for name in f.listdir(root):
   if not name.endswith('.py'):continue
   raw=f.open(root+'/'+name).read()
   if b'ProxyArray' not in raw:continue
   p=R/'installed_sdk'/name;p.write_bytes(raw);files.append(dict(source=root+'/'+name,path=str(p),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)))
  raw=f.open(root+'/../../assets/base_articulation_data.py').read() if False else b''
 (R/'INSTALLED_PROXY_READ.json').write_text(json.dumps(dict(epoch=time.time(),files=files,no_GPU=True),indent=2),encoding='utf8');print(json.dumps(files))
finally:c.close();os.environ.pop('MOD4_EVAL_SSH_PASSWORD',None)
