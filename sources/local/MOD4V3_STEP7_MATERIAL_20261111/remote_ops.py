from pathlib import Path
import sys,json,hashlib,base64,posixpath
sys.path.insert(0,str(Path(__file__).resolve().parent))
from step7_remote_access import connect
ROOT=Path(r"D:\claude2\fangzhen")
def remote(c,code,timeout=45):
 cmd="python3 -c \"import base64;exec(base64.b64decode('"+base64.b64encode(code.encode()).decode()+"'))\""
 _,o,e=c.exec_command(cmd,timeout=timeout);out=o.read().decode();err=e.read().decode();status=o.channel.recv_exit_status()
 if status:raise RuntimeError(f"remote exit {status}: {out} {err}")
 return out
if __name__=="__main__":
 stage=sys.argv[1];action=sys.argv[2];trial=ROOT/("_mod4v2_src_20261106/sources/local/MOD4V3_STEP7_"+stage.upper()+"_20261111");plan=json.loads((trial/"PLAN.json").read_text(encoding="utf-8"));base=plan["support"].rsplit("/support",1)[0];c=connect()
 try:
  if action=="upload":
   sf=c.open_sftp();manifest=[]
   for p in sorted(trial.rglob("*")):
    if not p.is_file() or "evidence" in p.parts or "__pycache__" in p.parts:continue
    rel=p.relative_to(trial).as_posix();dest=base+"/"+rel
    parent=posixpath.dirname(dest);parts=parent.strip("/").split("/");cur=""
    for part in parts:
     cur+="/"+part
     try:sf.stat(cur)
     except FileNotFoundError:sf.mkdir(cur)
    try:sf.stat(dest);raise RuntimeError("destination exists: "+dest)
    except FileNotFoundError:pass
    sf.put(str(p),dest)
    with sf.open(dest,"rb") as f:data=f.read()
    sha=hashlib.sha256(p.read_bytes()).hexdigest();assert hashlib.sha256(data).hexdigest()==sha
    manifest.append(dict(path=rel,bytes=p.stat().st_size,sha256=sha))
   sf.close();(trial/"evidence/SOURCE_UPLOAD.json").write_text(json.dumps(dict(remote=base,files=manifest),indent=2)+"\n",encoding="utf-8");print("UPLOADED",len(manifest),base)
  elif action=="probe":
   code="""import pathlib,json,subprocess,os,time
base=pathlib.Path(BASE);plan=json.loads((base/'PLAN.json').read_text());name='probe64_r1'
assert not (base/name).exists() and not (base/(name+'.log')).exists()
r=subprocess.run(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True);assert not r.stdout.strip(),r.stdout
env=dict(os.environ);root=pathlib.Path(plan['root']);env.update(WARP_CACHE_PATH=str(root/'cache/warp'),XDG_CACHE_HOME=str(root/'cache'),TMPDIR=str(root/'tmp'),TMP=str(root/'tmp'),TEMP=str(root/'tmp'),PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES='0',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
cmd=[plan['python'],'-B','-u',str(base/PROBE),'--plan',str(base/'PLAN.json'),'--out',str(base/name),'--num-envs','64','--steps','80']
with (base/(name+'.log')).open('xb',buffering=0) as log:child=subprocess.Popen(cmd,cwd=base/'support',env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
receipt=dict(pid=child.pid,cmd=cmd,epoch=time.time());(base/(name+'_LAUNCH.json')).write_text(json.dumps(receipt));print(json.dumps(receipt))
""".replace("BASE",repr(base),1).replace("PROBE",repr(stage+"_probe.py"),1)
   result=remote(c,code);(trial/"evidence/probe64_r1_LAUNCH.json").write_text(result,encoding="utf-8");print(result)
  elif action=="inspect":
   sf=c.open_sftp();ev=trial/"evidence"
   for name in ["probe64_r1/RESULT.json","probe64_r1/ERROR.json","probe64_r1/SAFE_CLOSED.json","probe64_r1/RESET_READBACK.json","probe64_r1.log","train040m_"+stage+"_r1_LAUNCH.json","train040m_"+stage+"_r1/STARTUP.json","train040m_"+stage+"_r1/RESTORE.json","train040m_"+stage+"_r1/PPO_EFFECTIVE.json","train040m_"+stage+"_r1/LATEST_PROGRESS.json","train040m_"+stage+"_r1/ERROR.json"]:
    try:sf.stat(base+"/"+name)
    except FileNotFoundError:continue
    dest=ev/name.replace("/","_");sf.get(base+"/"+name,str(dest))
    if name.endswith("log"):print(dest.read_text(encoding="utf-8",errors="replace")[-2000:])
    elif name.endswith(("RESULT.json","ERROR.json","LATEST_PROGRESS.json")):print(name,dest.read_text(encoding="utf-8")[:5000])
   sf.close()
  elif action=="train":
   code="""import subprocess,pathlib,json
base=pathlib.Path(BASE);p=json.loads((base/'PLAN.json').read_text());r=json.loads((base/'probe64_r1/RESULT.json').read_text());assert r['passed'];assert (base/'probe64_r1/SAFE_CLOSED.json').exists()
x=subprocess.run(['python3',str(base/'launch.py'),JOB,'--kind','train','--seconds','2400','--num-envs','4096'],capture_output=True,text=True,check=True);print(x.stdout)
""".replace("BASE",repr(base),1).replace("JOB",repr("train040m_"+stage+"_r1"),1)
   print(remote(c,code))
 finally:c.close()
