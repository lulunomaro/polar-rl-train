"""Root-only exact E0 secure ingress; existing same-host memory secret, no argv/disk."""
from pathlib import Path
import ast,types,hashlib,importlib.util,json,subprocess,sys,time,traceback
S=Path(__file__).resolve().parent;L=S.parent/"MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027";R=S/"reports"
D=L/"E0_82_NEW86_N20K_LONG_COMMAND_FROZEN_SOURCE_20261029_V1"
ENTRY=D/"upload_admit_detach_NEW86_E0_final82_long_command_secure_stdin_UNUSED_once_v1.py";INDEX=D/"FROZEN_E0_82_NEW86_LONG_COMMAND_SOURCE_INDEX_V1.json"
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open("x",encoding="utf8") as f:json.dump(v,f,indent=2)
def main():
 assert H(ENTRY)=="951447d489f6a14e21923e18311c35d0238984421902d8c48f3f3efe6ae2bed8"
 assert H(INDEX)=="3e598fc574f65c33e21fbc33d6a0c50e2a666cec4aac8067d42fabdb09f1aa77"
 assert not (D/"reports/NEW86_E0_ADMISSION_ENTRY_CONSUMED_BEFORE_STDIN.json").exists()
 helper=S.parent/"MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029/run_NEW_E2_V4_FIRST360_reviewed_secure_ingress_UNUSED_once.py"
 tree=ast.parse(helper.read_text(encoding="utf8")); selected=[x for x in tree.body if isinstance(x,(ast.Import,ast.ImportFrom)) or isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ("SESSION","EVENT") for t in x.targets) or isinstance(x,ast.FunctionDef) and x.name=="recover"]; assert len([x for x in selected if isinstance(x,ast.FunctionDef)])==1; ns={};exec(compile(ast.Module(body=selected,type_ignores=[]),str(helper),"exec"),ns);m=types.SimpleNamespace(recover=ns["recover"])
 put("ROOT_E0_V1_V2_SECURE_STARTUP_CONSUMED.json",dict(epoch=time.time(),entry=str(ENTRY),entry_SHA=H(ENTRY),index_SHA=H(INDEX),H1_actual111_learning_and112_frozen_case_closed=True,old_ingress_not_replayed=True,only_recover_function_reused=True,no_secret_stdout_environment_disk_argv_Git=True))
 req=m.recover();p=None;start=time.time();timed=False
 try:
  with (R/"ROOT_E0_V1_V2_SECURE_STARTUP_COMPLETE_STDOUT_STDERR.log").open("xb") as out:
   p=subprocess.Popen([sys.executable,"-u","-B","-X","utf8",str(ENTRY)],cwd=D,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT)
   p.stdin.write((json.dumps(req)+"\n").encode());p.stdin.flush();p.stdin.close();req=None
   print(json.dumps(dict(stage="NEW_E0_V1_SECURE_SAME_STARTUP_HANDLE",pid=p.pid,epoch=start)),flush=True)
   while p.poll() is None:
    if time.time()-start>650:
     timed=True;p.terminate()
     try:p.wait(timeout=20)
     except subprocess.TimeoutExpired:p.kill();p.wait(timeout=10)
     break
    try:p.wait(timeout=25)
    except subprocess.TimeoutExpired:print(json.dumps(dict(stage="SAME_FINITE_NEW_E0_V1_STARTUP",elapsed=round(time.time()-start,1))),flush=True)
  v=dict(epoch=time.time(),actual_waited=p.poll() is not None,returncode=p.returncode,deadline_terminated=timed,entry=str(ENTRY),no_H1_learning_GO_or_account_action=True)
  put("ROOT_E0_V1_V2_ACTUAL_LOCAL_STARTUP_WAIT_RETURNED.json",v);print(json.dumps(v),flush=True)
 finally:
  req=None
  if p is not None and p.poll() is None:p.terminate();p.wait(timeout=20)
if __name__=="__main__":
 try:main()
 except BaseException:put("ROOT_E0_V1_V2_ORIGINAL_SECURE_ERROR_"+str(time.time_ns())+".json",dict(error=traceback.format_exc(),no_secret_printed=True,no_automatic_retry=True));raise

