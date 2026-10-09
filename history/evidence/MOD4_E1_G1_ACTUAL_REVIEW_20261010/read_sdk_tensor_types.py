"""Read installed SDK sources and failed package exactly; no app/CUDA initialization."""
from pathlib import Path
import os,sys,hashlib,json,time,base64,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
try:
 secret,_=recover('MOD4_EVAL_SSH_PASSWORD');assert secret;os.environ['MOD4_EVAL_SSH_PASSWORD']=secret;c=connect_eval();files=[]
 with c.open_sftp() as sf:
  roots=['D:/claude2/fangzhen/IsaacLab/source/isaaclab/isaaclab','D:/claude2/IsaacLab/source/isaaclab/isaaclab']
  for root in roots:
   try:b=sf.open(root+'/assets/articulation/articulation_data.py').read()
   except FileNotFoundError:continue
   out=R/'installed_sdk'/'articulation_data.py';out.parent.mkdir(exist_ok=True);out.write_bytes(b);files.append(dict(path=root+'/assets/articulation/articulation_data.py',sha256=H(b),bytes=len(b)));break
  ps="$r=@(Get-ChildItem -LiteralPath 'D:\\claude2\\fangzhen' -Filter articulation_data.py -File -Recurse -ErrorAction SilentlyContinue|Select-Object -ExpandProperty FullName);$r|ConvertTo-Json -Compress"
  if not files:
   _,o,e=c.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0
   paths=json.loads(raw);paths=[paths] if isinstance(paths,str) else paths
   for path in paths:
    b=sf.open(path.replace('\\','/')).read();out=R/'installed_sdk'/(str(len(files))+'_articulation_data.py');out.parent.mkdir(exist_ok=True);out.write_bytes(b);files.append(dict(path=path,sha256=H(b),bytes=len(b)))
 v=dict(epoch=time.time(),trial_id='E1-G1-SDK-TENSOR-TYPE-READ-01',files=files,no_GPU_or_import=True)
 (R/'INSTALLED_SDK_TENSOR_READ.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v))
except Exception:
 (R/'SDK_TENSOR_READ_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),read_only=True)),encoding='utf8');raise
finally:
 if 'c' in globals():c.close()
 os.environ.pop('MOD4_EVAL_SSH_PASSWORD',None)
