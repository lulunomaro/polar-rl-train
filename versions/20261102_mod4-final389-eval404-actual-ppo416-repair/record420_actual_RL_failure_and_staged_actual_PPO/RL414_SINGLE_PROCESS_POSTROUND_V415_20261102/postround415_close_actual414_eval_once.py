"""One localprocess timer/normalcollector/evaldispatcher; ownparentCIM conflict avoided."""
from pathlib import Path
import hashlib,json,os,runpy,subprocess,sys,time,traceback
Q=Path(__file__).resolve().parent;T=Q.parent
N=T/'RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V414_20261102';R=N/'reports'
E=T/'RL414_FINAL_INDEPENDENT_EVAL_V415_20261102'
CONTROL='C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe';CPU='C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe'
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
def put(name,value):
 with(R/name).open('x',encoding='utf8')as stream:json.dump(value,stream,indent=2,allow_nan=False)
def inline(path,args):
 before=sys.argv[:];sys.argv=[str(path),*map(str,args)];sys.path.insert(0,str(path.parent))
 try:runpy.run_path(str(path),run_name='__main__')
 finally:sys.argv=before
def command(exe,path):
 result=subprocess.run([exe,'-B','-X','utf8',str(path)],cwd=N,capture_output=True,text=True,encoding='utf8')
 assert result.returncode==0,dict(stdout=result.stdout,stderr=result.stderr,rc=result.returncode)
 return dict(returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
def main():
 assert not(R/'POSTROUND415_ONCE_CONSUMED.json').exists()
 binding=json.loads((R/'ROOT414_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json').read_bytes());go=binding['current']['go']['jump_72']
 put('POSTROUND415_ONCE_CONSUMED.json',dict(epoch=time.time(),PID=os.getpid(),sameprocesslocalcollector=True))
 while time.time()<go['nominal_end_epoch']-898:time.sleep(min(10,max(.01,go['nominal_end_epoch']-898-time.time())))
 # Wait locally while any otherknowncontroller holds the serialscope; no secondSSH.
 pattern='MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021|RMPOLAR|watch_|collect_generic|run_once_after_resume|prepare_archive|single_gpu|collect_nine|collect_e1'
 query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Compress"
 waitstart=time.time()
 while True:
  result=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
  rows=json.loads(result.stdout)if result.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
  other=[row for row in rows if row['ProcessId']!=os.getpid()]
  if not other:break
  assert time.time()-waitstart<10800,'Localserialresourcesnotreleasedwithinbounded3h; preserveonce'
  time.sleep(10)
 normal=N/'normal414'
 inline(normal/'collect414_fullclose_transfer_once.py',['--root-lease-label','ROOT414_EXCLUSIVE_NORMAL900_RECOVERY_POSTROUND','--auth-provider',T.parent/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py','--additional-control-pattern','MOD4_H1|RMPOLAR|collect_generic|watch_|postround','--caller-index-SHA',H(normal/'INDEX414_NORMAL_SOURCE_FROZEN.json')])
 put('POSTROUND414_CPU_RETURNED.json',command(CPU,N/'review414_new_final_full_CPU_once.py'))
 full=json.loads((R/'ROOT414_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json').read_bytes());assert full['passed']
 complete=json.loads((R/'ROOT414_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes())
 task=json.loads((E/'TASK415_PENDING_FINAL_IDENTITY.json').read_bytes())
 task.update(model_path=complete['roles']['jump_72']['formal']['path'],model_SHA=full['SHA'],model_bytes=full['bytes'],expected_Pi_updates=full['Pi'],source_run=complete['run_id'],source_full_CPU_receipt_SHA=H(R/'ROOT414_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'),pending_actual_final_identity=False)
 with(E/'TASK415_FROZEN.json').open('x',encoding='utf8')as stream:json.dump(task,stream,indent=2)
 index=E/'INDEX415_SOURCE_TASK_CALLERS_FROZEN.json'
 with index.open('x',encoding='utf8')as stream:json.dump(dict(epoch=time.time(),files=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in sorted(E.rglob('*'))if path.is_file()and'__pycache__'not in path.parts]),stream,indent=2)
 inline(E/'run415_eval_once.py',['--caller-index-SHA',H(index)])
 put('POSTROUND414_RENDER_RETURNED.json',command(CONTROL,E/'render415_recorded_frames.py'))
 result=json.loads((E/'reports/ROOT415_EVALUATION_FULL_RETURNED.json').read_bytes())['result']
 put('POSTROUND414_RL_REPLAY_EVAL_DECISION.json',dict(epoch=time.time(),status='COMPLETE_ACTUAL_PPO414_EVAL_PENDING_NATIVE_REVIEW',modelSHA=full['SHA'],strict=result['strict_successes'],terminations=result['terminations'],evalroot=str(E),next='Currentmodelmustviewactualbodyposes/manifoldthenproactivelyrepairorcontinueRL'))
if __name__=='__main__':
 try:main()
 except BaseException:put('POSTROUND415_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_replay=True));raise
