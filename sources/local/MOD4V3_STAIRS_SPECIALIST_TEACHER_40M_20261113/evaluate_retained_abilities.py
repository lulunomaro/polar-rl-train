"""Finite teacher/parent frozen Rough-v1 retention comparison. No training."""
from pathlib import Path
import hashlib, importlib.util, json, os, shlex, sys, time, traceback
T=Path(__file__).resolve().parent
S=T.parent/"MOD4V3_STAIRS_SPECIALIST_DISTILL_40M_20261113"
E=T/"evidence/retained_abilities_r1"
spec=importlib.util.spec_from_file_location("student_retention_remote",S/"remote_run.py")
remote=importlib.util.module_from_spec(spec);spec.loader.exec_module(remote)
connect,execute,P,REMOTE=remote.connect,remote.execute,remote.P,remote.REMOTE
teacher_root=json.loads((T/"PLAN.json").read_text(encoding="utf8"))["root"]
models={"parent":REMOTE+"/frozen_best_parent.pt","teacher":teacher_root+"/train040m_specialist_r1/model_final.pt"}
expected={"parent":"db6e9ccf5c6d4d05a68633fd82861d903c4c52fcc1a6dd89132e55e2a4bf1283","teacher":"715c40b6bd18c51d050d0bae38c0d04008f3841cc4a40ddca980a9cd52623ff5"}
script=REMOTE+"/teacher_retention_replay_r1.py"
manifest=REMOTE+"/TEACHER_RETAINED_MODELS_R1.json"
source=S/"rough_retention_replay.py"
(E/"rough_retention_replay.py").write_bytes(source.read_bytes())
(E/"NATIVE_PLAN.json").write_text(json.dumps(dict(models=models,sha256=expected,protocol="Existing paired frozen Rough-v1 L9 traverse/gyro/landing, seed66, same original criteria; new teacher-v-parent inference, no optimizer",evaluator_sha256=hashlib.sha256(source.read_bytes()).hexdigest()),indent=2)+"\n",encoding="utf8")
records=[]
try:
 c=connect()
 try:
  sf=c.open_sftp()
  for label,path in models.items():
   assert execute(c,"sha256sum -- "+shlex.quote(path)).split()[0]==expected[label]
  sf.put(str(source),script)
  with sf.open(manifest,"w") as f:f.write(json.dumps(models))
 finally:c.close()
 for skill in ("traverse","gyro","landing"):
  label="retained_"+skill
  out=REMOTE+"/native_teacher_"+label+"_l9_r1"
  local=E/label;local.mkdir(exist_ok=False)
  cmd=[P["python"],"-B","-u",script,"--plan",REMOTE+"/PLAN.json","--support",REMOTE+"/support","--models",manifest,"--out",out,"--version","teacher715c_parentdb6_retention_r1","--level","9","--skill",skill]
  log_path=REMOTE+"/teacher_"+label+"_r1.log"
  c=connect()
  try:
   busy=execute(c,"nvidia-smi --query-compute-apps=pid --format=csv,noheader").strip()
   assert not busy,"Existing compute owner; no launch: "+busy
   code="from pathlib import Path;import subprocess,os,json,time;root=Path("+repr(REMOTE)+");out=Path("+repr(out)+");assert not out.exists();env=dict(os.environ);env.update(CUDA_VISIBLE_DEVICES='0',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',XDG_CACHE_HOME=str(root/'cache'),WARP_CACHE_PATH=str(root/'cache/warp'),TMPDIR=str(root/'tmp'));log=Path("+repr(log_path)+").open('xb',buffering=0);child=subprocess.Popen("+repr(cmd)+",cwd=root/'support',env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True);print(json.dumps(dict(pid=child.pid,epoch=time.time(),job=str(out))))"
   receipt=json.loads(execute(c,P["python"]+" -B -c "+shlex.quote(code)))
   (local/"LAUNCH.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf8")
   print("TEACHER_RETENTION_STARTED "+skill+" "+str(receipt["pid"]),flush=True)
  finally:c.close()
  previous=-1
  deadline=time.monotonic()+900
  while True:
   assert time.monotonic()<deadline,"Reader limit reached; job was not killed"
   c=connect()
   try:
    sf=c.open_sftp()
    try:names=[x.filename for x in sf.listdir_attr(out)]
    except FileNotFoundError:names=[]
    for name in ("PROGRESS.json","ERROR.json","SAFE_CLOSED.json"):
     if name in names:sf.get(out+"/"+name,str(local/name))
    if (local/"PROGRESS.json").exists():
     progress=json.loads((local/"PROGRESS.json").read_text())
     step=progress.get("step",0)
     if step!=previous:
      previous=step
      print("TEACHER_RETENTION_PROGRESS "+skill+" "+json.dumps(progress),flush=True)
    closed="SAFE_CLOSED.json" in names
    if closed:
     for name in names:
      if name.endswith((".json",".npz")):sf.get(out+"/"+name,str(local/name))
     sf.get(log_path,str(local/"stdout.log"))
     if execute(c,"nvidia-smi --query-compute-apps=pid --format=csv,noheader").strip():closed=False
    if closed:
     assert not (local/"ERROR.json").exists(),"Native evaluation error: "+str(local/"ERROR.json")
     assert (local/"RESULT.json").exists()
     records.append(dict(skill=skill,remote=out,local=str(local/"RESULT.json")))
     break
   finally:c.close()
   time.sleep(5)
  print("TEACHER_RETENTION_COMPLETE "+skill,flush=True)
 (E/"NATIVE_COMPLETE.json").write_text(json.dumps(dict(completed=records,no_optimizer=True,models_sha256=expected),indent=2)+"\n",encoding="utf8")
 print("ALL_TEACHER_RETENTION_COMPLETE",flush=True)
except BaseException:
 (E/"NATIVE_READER_ERROR.json").write_text(json.dumps(dict(error=traceback.format_exc(),completed=records,scope="No training; no process killed"),indent=2)+"\n",encoding="utf8")
 raise
