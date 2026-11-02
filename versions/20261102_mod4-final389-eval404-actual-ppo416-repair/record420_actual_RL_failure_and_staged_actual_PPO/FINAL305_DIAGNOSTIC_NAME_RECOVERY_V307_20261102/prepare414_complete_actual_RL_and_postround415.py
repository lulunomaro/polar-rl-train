"""Complete independent414 actualPPO production and415 singleprocess postround."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import re
import shutil
import time

P=Path(__file__).resolve().parent;T=P.parent
O=T/'RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V410_20261102'
N=T/'RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V414_20261102'
Q=T/'RL414_SINGLE_PROCESS_POSTROUND_V415_20261102'
E=T/'RL414_FINAL_INDEPENDENT_EVAL_V415_20261102'
OLD389=T/'MPC_COMMAND_RESIDUAL_RL_V389_20261102'
OLD399=T/'RL389_CLOSED_FINAL_RECOVERY_V399_20261102'
OLD404=T/'RL389_EXACT_FINAL_INDEPENDENT_EVAL_V404_20261102'
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
read=lambda path:json.loads(path.read_bytes())
def put(path,value):
 with path.open('x',encoding='utf8')as stream:json.dump(value,stream,indent=2,allow_nan=False)
def token(text,old,new):
 return re.sub(r'(?<=[A-Za-z_])'+str(old)+r'(?!\d)',str(new),text)
def rename(text):return token(text.replace(str(O),str(N)).replace(O.as_posix(),N.as_posix()),410,414)
assert not N.exists()and not Q.exists()and not E.exists()
N.mkdir();(N/'reports').mkdir();Q.mkdir();(Q/'reports').mkdir();E.mkdir();(E/'reports').mkdir()
for path in sorted(O.rglob('*')):
 if not path.is_file()or'__pycache__'in path.parts or 'reports'in path.relative_to(O).parts:continue
 if path.name=='TASK410_FROZEN.json':continue
 dest=N/rename(str(path.relative_to(O)));dest.parent.mkdir(parents=True,exist_ok=True)
 if path.suffix=='.py':dest.write_text(rename(path.read_text('utf8')),encoding='utf8')
 else:shutil.copyfile(path,dest)
shutil.copyfile(O/'reports/CPU410_REUSED409_NO_STEP_ADMISSION.json',N/'reports/CPU414_REUSED409_NO_STEP_ADMISSION.json')
worker=N/'source/worker414.py';text=worker.read_text('utf8')
old="   student=learner.update() if controls>=64 else None\n   if student is not None:put('LATEST_STUDENT414.json',dict(epoch=time.time(),**student))"
new="   proposed=learner.update() if controls>=64 else None\n   if proposed is not None:\n    student=proposed;put('LATEST_STUDENT414.json',dict(epoch=time.time(),**student))"
assert text.count(old)==1;text=text.replace(old,new)
text=text.replace('assert wm.updates>20419 and learner.Pi_updates>0 and first is not None','assert wm.updates>20419 and learner.Pi_updates>0 and first is not None and student is not None')
worker.write_text(text,encoding='utf8')
nonce=str(time.time_ns());job='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_ACTUAL_RESIDUAL_PPO414_'+nonce
task=read(O/'TASK410_FROZEN.json')
task.update(kind='ACTUAL_ONPOLICY_RESIDUAL_PPO_400N50_V414',run_id='ACTUAL_RESIDUAL_PPO414_'+nonce,
 job_root=job+'/tracker72',owner_root=job+'/owner72',worker_SHA=H(worker),
 CPU414_SHA=H(N/'reports/CPU414_REUSED409_NO_STEP_ADMISSION.json'),
 CPU410_SHA=None,resume_scope='Fullfinal389actorcriticSTDallAdamEMAoriginWM20419; actualPPOrolloutfresh; no oldweightsrollback')
put(N/'TASK414_FROZEN.json',task)

# New final evaluation reuses exact source414 and its unchanged data byteforbyte.
shutil.copytree(N/'source',E/'source',ignore=shutil.ignore_patterns('__pycache__'))
shutil.copyfile(OLD404/'source/wheel_geometry220.py',E/'source/wheel_geometry220.py')
for name in('feedforward389.json','reference389.npz'):shutil.copyfile(N/name,E/name)
def evalrename(text):
 text=text.replace(str(OLD404),str(E)).replace(OLD404.as_posix(),E.as_posix())
 return token(text,404,415)
for old,new in(('contract404.py','contract415.py'),('target404_parent.py','target415_parent.py'),
 ('run404_eval_once.py','run415_eval_once.py'),('view404_actual_RL_replay.py','view415_actual_RL_replay.py'),
 ('render404_recorded_frames.py','render415_recorded_frames.py'),('source/evaluate404.py','source/evaluate415.py')):
 text=evalrename((OLD404/old).read_text('utf8'))
 if old=='contract404.py':text=text.replace('FROZEN389_RESIDUAL_RL_EVAL415','FROZEN414_ACTUAL_RESIDUAL_PPO_EVAL415')
 if old.startswith('source/evaluate'):
  text=text.replace("ck['kind']=='REFERENCE_TRACKING_BPTT389_COMPLETE'","ck['kind']=='ACTUAL_RESIDUAL_PPO414_COMPLETE'")
  text=text.replace('learned_residual_RL389','learned_actual_residual_PPO414')
 if old.startswith('view'):
  text=text.replace('policy_updates=3508',"policy_updates='fromfinal414receipt'").replace('RL389','RL414')
 (E/new).write_text(text,encoding='utf8')
etask=read(OLD404/'TASK404_FROZEN.json')
etask.update(kind='FROZEN414_ACTUAL_RESIDUAL_PPO_EVAL415',source_run='PENDING414ACTUALFINAL',
 expected_Pi_updates=1,model_SHA=task['model_SHA'],model_path=task['model_path'],model_bytes=task['model_bytes'],
 worker_SHA=H(E/'source/evaluate415.py'),human_request='ActualPPO414 actoronly eval+origin+fixedtable/noonlineMPC',
 distinct_evaluation_purpose='Immediately evaluate firstactualPPO414 fullfinal aftersafeclose;80firstepisodes/samecourse/newDR9137',
 pending_actual_final_identity=True)
put(E/'TASK415_PENDING_FINAL_IDENTITY.json',etask)

# Full finalCPU414 preserves frozen origin, Adam offsets and actualPPO counters.
cpu=(OLD389/'review389_NEW_final_whole_CPU_UNUSED_once.py').read_text('utf8')
cpu=token(cpu,389,414)
cpu=cpu.replace("REFERENCE_TRACKING_BPTT414_COMPLETE","ACTUAL_RESIDUAL_PPO414_COMPLETE")
cpu=cpu.replace('16879+ck[','20419+ck[').replace('wm-16879','wm-20419')
cpu=cpu.replace("('actor',52636),('critic',9696)","('actor',56144),('critic',13204)")
cpu=cpu.replace("s['actor_Adam_offset']==52636 and s['critic_Adam_offset']==9696","s['actor_Adam_offset']==56144 and s['critic_Adam_offset']==13204")
cpu=cpu.replace("assert s['policy_horizon']==8 and s['WM_supervision_horizon']==32 and s['actor_terminal_bootstrap']is False",
 "assert s['actor_horizon_actual_controls']==32 and s['WM_supervision_horizon']==32 and s['actor_terminal_bootstrap']is False\n    assert s['PPO_updates']==pi==ck['actual_new_PPO_updates'] and s['actual_reward_unchanged'] and not s['actor_model_gradient']\n    assert 'actual_RL_rollout'in s and 'residual_sampling_rng'in s")
cpu=cpu.replace("assert not s['old_Fudan_return']and s['critic_same_tracking_return']and s['goal_dim']==59","assert s['goal_dim']==59 and s['origin_frozen_from389']")
(N/'review414_new_final_full_CPU_once.py').write_text(cpu,encoding='utf8')

# Independent normal collector works within the sole localtimer process.
normal=N/'normal414';normal.mkdir()
common=(OLD399/'normal399_common.py').read_text('utf8')
common=common.replace("T=D.parent;W=T.parent;N=T/'MPC_COMMAND_RESIDUAL_RL_V389_20261102';R=N/'reports'","N=D.parent;T=N.parent;W=T.parent;R=N/'reports'")
common=common.replace('399','414').replace('389','414')
common=common.replace("task=read(D/'TASK414_FROZEN.json')","task=read(N/'TASK414_FROZEN.json')")
common=common.replace("INDEX414_RECOVERY_SOURCE_TASK_CALLER_FROZEN.json","INDEX414_NORMAL_SOURCE_FROZEN.json")
(normal/'normal414_common.py').write_text(common,encoding='utf8')
collector=(OLD399/'collect399_original389_closed_final_once.py').read_text('utf8')
collector=collector.replace('from normal399_common','from normal414_common')
collector=collector.replace('399','414').replace('389','414')
collector=collector.replace('16879+u','20419+u').replace('final.get(\'actual_new_PPO_updates\')==0',"final.get('actual_new_PPO_updates')==final.get('actual_new_Pi_updates')")
postpath=Q/'postround415_close_actual414_eval_once.py'
old=" assert str(Path(__file__).resolve()).lower().replace('\\\\','/') in own[0]['CommandLine'].lower().replace('\\\\','/')"
new=" assert any(str(path).replace(chr(92),'/').lower() in own[0]['CommandLine'].replace(chr(92),'/').lower()for path in(Path(__file__).resolve(),Path("+repr(str(postpath))+")))"
assert old in collector;collector=collector.replace(old,new)
collector=collector.replace('recovery414=True,original396_local_CIM_failure_preserved=True','actualPPO414=True')
(normal/'collect414_fullclose_transfer_once.py').write_text(collector,encoding='utf8')

post='''"""One localprocess timer/normalcollector/evaldispatcher; ownparentCIM conflict avoided."""
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
 query="Get-CimInstance Win32_Process -Filter \\"Name='python.exe' OR Name='ssh.exe'\\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Compress"
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
'''
# The embedded PowerShell quote uses ordinary escaped doublequotes in Python source.
post=post.replace('\\"','"') if False else post
postpath.write_text(post,encoding='utf8')
bind='''"""BindactualFIRST414 and launch sole415timer; no network/modelreads."""
from pathlib import Path
import importlib.util,json,subprocess,time
Q=Path(__file__).resolve().parent;N=Q.parent/'RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V414_20261102';R=N/'reports'
def put(name,value):
 with(R/name).open('x',encoding='utf8')as stream:json.dump(value,stream,indent=2,allow_nan=False)
assert not(R/'BIND415_POSTROUND_ONCE_CONSUMED.json').exists()
snap=json.loads((R/'ROOT414_STATUS_FIRST_UPDATED.json').read_bytes());files={Path(row['path']).name:json.loads(row['UTF8'])for row in snap['full_selected_UTF8']}
assert not any(name in files for name in('ORIGINAL_ERROR.json','NODE_ORIGINAL_ERROR.json','OWNER_ORIGINAL_ERROR.json'))
task=json.loads((N/'TASK414_FROZEN.json').read_bytes());spec=importlib.util.spec_from_file_location('bind414',N/'teacher_task414.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.validate_first(files['FIRST_ACTUAL_TEACHER_DEPTH_STUDENT414_UPDATE.json'],task,files['GO_PRODUCTION.json'])
put('BIND415_POSTROUND_ONCE_CONSUMED.json',dict(epoch=time.time(),run_id=task['run_id'],modelreads=0))
put('ROOT414_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json',dict(epoch=time.time(),passed=True,run_id=task['run_id'],current=files['OWNER_CURRENT.json'],canonical_None=False,files=files,exact_original_owner=json.loads((R/'ROOT414_ORIGINAL_OWNER_LAUNCH_ACTUAL.json').read_bytes())['owner']))
path=Q/'postround415_close_actual414_eval_once.py'
with(R/'POSTROUND415_STDOUT.log').open('xb')as out,(R/'POSTROUND415_STDERR.log').open('xb')as err:
 process=subprocess.Popen(['C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe','-B','-X','utf8',str(path)],cwd=N,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
put('POSTROUND415_WAITER_LAUNCH.json',dict(epoch=time.time(),PID=process.pid,script=str(path),sameprocessserialdispatcher=True))
print(json.dumps(dict(passed=True,PID=process.pid)))
'''
(Q/'bind415_actual_FIRST_and_launch_once.py').write_text(bind,encoding='utf8')
for path in list(N.rglob('*.py'))+list(Q.rglob('*.py'))+list(E.rglob('*.py')):ast.parse(path.read_text('utf8'),filename=str(path))
protocol=importlib.util.spec_from_file_location('validate414',N/'teacher_task414.py');m=importlib.util.module_from_spec(protocol);protocol.loader.exec_module(m);m.validate_task(task)
put(normal/'INDEX414_NORMAL_SOURCE_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in(normal/'normal414_common.py',normal/'collect414_fullclose_transfer_once.py',N/'teacher_task414.py')]))
put(N/'INDEX414_SOURCE_TASK_CALLERS_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in sorted(N.rglob('*'))if path.is_file()and'__pycache__'not in path.parts]))
put(Q/'INDEX415_POSTROUND_FOR414_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for root in(Q,E)for path in sorted(root.rglob('*'))if path.is_file()and'__pycache__'not in path.parts]))
put(P/'reports/STATIC414415_ACTUAL_RL_COMPLETE_PACKAGE.json',dict(epoch=time.time(),passed=True,
 root=str(N),run=task['run_id'],indexSHA=H(N/'INDEX414_SOURCE_TASK_CALLERS_FROZEN.json'),
 postroot=str(Q),postindexSHA=H(Q/'INDEX415_POSTROUND_FOR414_FROZEN.json'),evalroot=str(E),
 CPU409exactlearnerreuse=True,allAST=True,original410_incomplete_preserved=True,
 sameprocesspostround_fix=True,network=0,SDK=0,modelreads=0,START=False))
print(json.dumps(dict(passed=True,root=str(N),run=task['run_id'],indexSHA=H(N/'INDEX414_SOURCE_TASK_CALLERS_FROZEN.json'),postindexSHA=H(Q/'INDEX415_POSTROUND_FOR414_FROZEN.json'))))
