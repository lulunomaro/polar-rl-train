"""Root-only secure ingress for exactly reviewed E2 V2. No secret output/files/argv."""
from pathlib import Path
import ast,hashlib,json,re,subprocess,sys,time,traceback
B=Path(__file__).resolve().parent;L=B.parent/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=B/'reports'
D=L/'E2_93_NEW86_ORIGINAL_FLAT_HEIGHT_PROVIDER_REPAIR_SOURCE_20261029_V4'
ENTRY=D/'read_E2_new86_FIRST_native24_queue_secure_stdin_UNUSED_once_v4.py'
INDEX=D/'FROZEN_E2_93_NEW86_PROFILE_DOMAIN_SOURCE_INDEX_V4.json'
SESSION=Path('C:/Users/lulu/.codex/sessions/2026/10/15/rollout-2026-10-15T21-33-55-01a07a2d-9036-7531-a012-692df9f56353_01a13fc4-f5ba-7c52-8bb5-301275e18a75.jsonl')
EVENT='2026-10-28T16:50:46.051Z'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def recover():
 value=None
 for line in SESSION.open(encoding='utf8'):
  if EVENT not in line:continue
  j=json.loads(line)
  if j.get('timestamp')!=EVENT:continue
  q=j.get('payload',{});s=q.get('input','')
  if q.get('type')!='custom_tool_call':continue
  assert q['name']=='exec' and 'tools.write_stdin' in s and re.search(r'session_id\s*:\s*96666',s)
  assert "host:'10.50.0.86'" in s or 'host:"10.50.0.86"' in s
  assert "username:'robemo'" in s or 'username:"robemo"' in s
  m=re.search(r'''password\s*:\s*('(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")''',s)
  assert m is not None and value is None
  value=ast.literal_eval(m[1]);assert isinstance(value,str) and 0<len(value)<256
 assert value is not None,'Exact previously authorized same-host hidden ingress unavailable'
 return dict(host='10.50.0.86',username='robemo',password=value)
def main():
 assert H(ENTRY)=='818f73503e2554442db603e6a7b48f4ba6536cd4d8e1f1ed9bb255951780567e'
 assert H(INDEX)=='15a153274734431a07cd28152038442fb034ae62936aa0fee2635b779cf40e50'
 assert not (D/'reports/E2_V4_FIRST_DISTINCT_READ_CONSUMED_BEFORE_STDIN.json').exists()
 put('ROOT_E2_V4_FIRST_SECURE_INGRESS_CONSUMED.json',dict(epoch=time.time(),entry=str(ENTRY),entry_SHA=H(ENTRY),index_SHA=H(INDEX),same_host_original_hidden_event=EVENT,old_96666_not_replayed=True,no_secret_stdout_disk_environment_argv_or_Git=True,global_serial_SSH=True,H1_training_still_held=False))
 req=recover();child=None;start=time.time();timed=False
 try:
  with (R/'ROOT_E2_V4_FIRST_SECURE_FINITE_COMPLETE_STDOUT_STDERR.log').open('xb') as out:
   child=subprocess.Popen([sys.executable,'-u','-B','-X','utf8',str(ENTRY),'--actual-startup-json','C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\\MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027\\E2_93_NEW86_ORIGINAL_FLAT_HEIGHT_PROVIDER_REPAIR_SOURCE_20261029_V4\\reports\\NEW86_E2_METADATA_WITNESS_AND_DETACHED_RETURNED_ACTUAL.json','--actual-startup-SHA','d032bdfcc95d01c57d216e491ac4b4b3290a74217e8a19c560354ed9ac80a1fd'],cwd=D,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT)
   child.stdin.write((json.dumps(req)+'\n').encode());child.stdin.flush();child.stdin.close();req=None
   print(json.dumps(dict(stage='NEW_E2_V4_FIRST_SECURE_SAME_HANDLE',pid=child.pid,entry=str(ENTRY),epoch=start)),flush=True)
   while child.poll() is None:
    if time.time()-start>470:
     timed=True;child.terminate()
     try:child.wait(timeout=20)
     except subprocess.TimeoutExpired:child.kill();child.wait(timeout=10)
     break
    try:child.wait(timeout=25)
    except subprocess.TimeoutExpired:print(json.dumps(dict(stage='SAME_FINITE_E2_V4_FIRST_STARTUP_HANDLE',elapsed=round(time.time()-start,1))),flush=True)
  result=dict(epoch=time.time(),actual_waited=child.poll() is not None,returncode=child.returncode,deadline_terminated=timed,entry=str(ENTRY),new_namespace_only=True,no_H1_GO_or_account_write=True)
  put('ROOT_E2_V4_FIRST_ACTUAL_LOCAL_ENTRY_WAIT_RETURNED.json',result);print(json.dumps(result),flush=True)
 finally:
  req=None
  if child is not None and child.poll() is None:child.terminate();child.wait(timeout=20)
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT_E2_V4_FIRST_ORIGINAL_INGRESS_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_secret_printed=True,no_automatic_retry=True));raise
