"""Root-only new E0V2 exact actions; original memory-only noechoSTDIN secret."""
from pathlib import Path
import ast,types,hashlib,json,subprocess,sys,time,traceback,argparse
S=Path(__file__).resolve().parent;T=S.parent;R=S/'reports'
D=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/E0_82_NEW86_EARLY_RESAMPLE_COMPLETE_CASE_SOURCE_20261029_V2'
INDEX=D/'FROZEN_E0_82_NEW86_EARLY_RESAMPLE_COMPLETE_SOURCE_INDEX_V2.json'
TABLE={
 'install':('upload_admit_detach_NEW86_E0_final82_early_command_secure_stdin_UNUSED_once_v2.py','6f54e2e19bb70ce20ff6097404a7705ea29a99ca8a8f97674b1b1835c6b0d7df',650),
 'first':('read_E0_new86_FIRST_native24_early_queue_secure_stdin_UNUSED_once_v2.py','9869bddb223b263981e865cfe7559f8d909ad505efdbe6e707ab9891c528695c',470),
 'normal':('collect_E0_new86_TERMINAL_fulltext_secure_stdin_UNUSED_once_v2.py','5c7d055ee88466df16982db6bb3377f6b7fd0c9136299451351adb9a02b5764e',950)}
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main(mode):
 assert H(INDEX)=='e52afea5486209fd07ae433c1a00cb48e384e885f2554d3f8f695b1db8ac6f69'
 index=json.loads(INDEX.read_bytes());name,digest,cap=TABLE[mode];entry=D/name;assert H(entry)==digest
 for n,want in index['executable_source_SHAs'].items():assert H(D/n)==want,n
 assert H(D/index['manifest_local_filename'])==index['manifest_SHA']
 marker='ROOT_NEW_E0_V2_'+mode.upper()+'_SECURE_CONSUMED_BEFORE_STDIN.json';assert not (R/marker).exists()
 args=[]
 if mode!='install':
  startup=D/'reports/NEW86_E0_METADATA_WITNESS_AND_DETACHED_RETURNED_ACTUAL.json'
  value=json.loads(startup.read_bytes());assert value['passed_source_CPU_and_detached_only'] and value['detached']['actual_detached']
  args=['--actual-startup-json',str(startup),'--actual-startup-SHA',H(startup)]
 helper=T/'MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029/run_NEW_E2_V4_FIRST360_reviewed_secure_ingress_UNUSED_once.py'
 tree=ast.parse(helper.read_text(encoding='utf8'))
 selected=[x for x in tree.body if isinstance(x,(ast.Import,ast.ImportFrom)) or isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('SESSION','EVENT') for t in x.targets) or isinstance(x,ast.FunctionDef) and x.name=='recover']
 assert sum(isinstance(x,ast.FunctionDef) for x in selected)==1
 ns={};exec(compile(ast.Module(body=selected,type_ignores=[]),str(helper),'exec'),ns)
 put(marker,dict(epoch=time.time(),mode=mode,entry=str(entry),entry_SHA=digest,index_SHA=H(INDEX),root_review_complete=True,global_serial_SSH=True,no_old_main_or_remote_once_replayed=True,no_H1_learning_GO_account_action=True,no_secret_stdout_disk_environment_argv_Git=True))
 req=ns['recover']();child=None;start=time.time();timed=False
 try:
  with (R/('ROOT_NEW_E0_V2_'+mode.upper()+'_COMPLETE_STDOUT_STDERR.log')).open('xb') as out:
   child=subprocess.Popen([sys.executable,'-u','-B','-X','utf8',str(entry),*args],cwd=D,stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT)
   child.stdin.write((json.dumps(req)+'\n').encode());child.stdin.flush();child.stdin.close();req=None
   print(json.dumps(dict(stage='NEW_E0_V2_'+mode.upper()+'_SECURE_SAME_HANDLE',pid=child.pid,epoch=start)),flush=True)
   while child.poll() is None:
    if time.time()-start>cap:
     timed=True;child.terminate()
     try:child.wait(timeout=20)
     except subprocess.TimeoutExpired:child.kill();child.wait(timeout=10)
     break
    try:child.wait(timeout=25)
    except subprocess.TimeoutExpired:print(json.dumps(dict(stage='SAME_FINITE_NEW_E0_V2_'+mode.upper(),elapsed=round(time.time()-start,1))),flush=True)
  result=dict(epoch=time.time(),actual_waited=child.poll() is not None,returncode=child.returncode,deadline_terminated=timed,mode=mode,entry=str(entry),no_H1_GO_or_account_write=True)
  put('ROOT_NEW_E0_V2_'+mode.upper()+'_ACTUAL_LOCAL_WAIT_RETURNED.json',result);print(json.dumps(result),flush=True)
 finally:
  req=None
  if child is not None and child.poll() is None:child.terminate();child.wait(timeout=20)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--mode',required=True,choices=tuple(TABLE));a=p.parse_args()
 try:main(a.mode)
 except BaseException:put('ROOT_NEW_E0_V2_'+a.mode.upper()+'_ORIGINAL_SECURE_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_secret_printed=True,no_automatic_retry=True));raise
