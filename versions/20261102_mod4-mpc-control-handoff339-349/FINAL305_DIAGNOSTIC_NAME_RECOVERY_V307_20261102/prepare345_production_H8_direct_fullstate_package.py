"""Freeze independent345 fullstate production from CPU344, keeping all old packages."""
from pathlib import Path
import ast, hashlib, importlib.util, json, re, shutil, time

P=Path(__file__).resolve().parent;T=P.parent
S=T/'REFERENCE_H4_TRACKING_REPAIR_V324_20261102'
C=T/'REFERENCE_H8_DIRECT_TRACKING_REPAIR_V344_20261102'
D=T/'REFERENCE_H8_DIRECT_TRACKING_PRODUCTION_V345_20261102'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
def put(path,value):
    with path.open('x',encoding='utf8')as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
def rename(text):
    text=text.replace(str(S),str(D)).replace(str(S).replace('\\','/'),str(D).replace('\\','/'))
    saved=[]
    def hide(m):saved.append(m.group());return '@HASH'+str(len(saved)-1)+'@'
    text=re.sub(r'\b[0-9a-f]{64}\b',hide,text)
    text=re.sub(r'(?<=[A-Za-z_])324(?!\d)','345',text)
    for i,value in enumerate(saved):text=text.replace('@HASH'+str(i)+'@',value)
    return text
def write(path,text):
    ast.parse(text,filename=str(path));path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8')as f:f.write(text)
cpu=read(C/'reports/CPU344_RESTORED324_H8_DIRECT_NO_STEP.json')
assert cpu['passed'] and cpu['optimizer_steps']==0 and cpu['synthetic_H8_direct_no_step']['policy_H']==8
fullpath=S/'reports/ROOT324_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json';full=read(fullpath)
assert full['passed'] and full['SHA']==cpu['source_final_SHA'] and full['totalWM']==16879
evaluation=read(T/'FINAL324_IMPORT_CIM_REPAIR_EVAL_V339_20261102/reports/ROOT339_EVALUATION_FULL_RETURNED.json')['result']
assert evaluation['passed'] and evaluation['strict_successes']==evaluation['crossed_cases']==0
diag=read(T/'FINAL324_ACTUAL_PAIRED_DIRECTION_DIAGNOSTIC_V342_20261102/reports/ROOT342_EVALUATION_FULL_RETURNED.json')['result']
assert diag['passed'] and diag['source_WM_updates']==16879
D.mkdir(exist_ok=False);(D/'reports').mkdir()
for folder in('source','control324','normal324'):
    for path in sorted((S/folder).rglob('*.py')):
        destination=D/rename(folder)/rename(str(path.relative_to(S/folder)))
        write(destination,rename(path.read_text('utf8')))
shutil.copyfile(S/'reference324.npz',D/'reference345.npz')
learner=rename((C/'source/tracking_learner344.py').read_text('utf8')).replace('TrackingLearner344','TrackingLearner345').replace('ACTUAL344_','ACTUAL345_')
# Candidate344 is CPU-admitted. Replace its naming-only generated345 copy.
(D/'source/tracking_learner345.py').write_text(learner,encoding='utf8')
worker=(D/'source/worker345.py').read_text('utf8')
worker=worker.replace("ck['kind']=='REFERENCE_TRACKING_BPTT305_COMPLETE' and ck['total_WM_updates']==12468 and ck['actual_new_Pi_updates']==2724","ck['kind']=='REFERENCE_TRACKING_BPTT324_COMPLETE' and ck['total_WM_updates']==16879 and ck['actual_new_Pi_updates']==4379")
worker=worker.replace('wm.updates==12468','wm.updates==16879').replace("int(v['step'])==12468","int(v['step'])==16879")
worker=worker.replace('inherited_WM_updates=12468','inherited_WM_updates=16879').replace('inherited_world_updates=12468','inherited_world_updates=16879').replace('wm.updates>12468','wm.updates>16879')
worker=worker.replace('actor_policy_H=4','actor_policy_H=8').replace("policy_rollback_source='restoreexactfinal305/allAdam/EMA/STD/WM12468;actorH4trackingonly,WMH32,terminalholdrest;freshphysicalepisodes'","policy_rollback_source='restoreexactfinal324/allAdamEMA_STD_WM16879;actorH8directcost_noalive_mask_noexp_noactorvalue;freshphysicalepisodes'")
(D/'source/worker345.py').write_text(worker,encoding='utf8')
oldSHA=read(S/'TASK324_FROZEN.json')['source_SHA']
for path in (D/'source/teacher_task345.py',D/'source/tracking_task345.py',D/'control345/teacher_task345.py'):
    text=path.read_text('utf8').replace(oldSHA,full['SHA']).replace('model_bytes=32695597','model_bytes=32698221')
    text=text.replace('source_WM_updates=12468','source_WM_updates=16879').replace('source_actor_Adam_step=48257','source_actor_Adam_step=52636').replace('new_tracking_critic_Adam_step=5317','new_tracking_critic_Adam_step=9696')
    text=text.replace('actor_policy_H=4','actor_policy_H=8').replace("['policy_H']==4","['policy_H']==8")
    text=text.replace('==12468+','==16879+').replace('==48257+pi','==52636+pi').replace('==5317+pi','==9696+pi')
    text=text.replace('actor_terminal_bootstrap=False,','actor_terminal_bootstrap=False,actor_direct_tracking_cost=True,')
    text=text.replace("assert r['student']['policy_H']==8", "assert r['student']['actor_direct_tracking_cost'] and not r['student']['actor_alive_mask_applied']\n    assert r['student']['policy_H']==8")
    path.write_text(text,encoding='utf8')
for name in('teacher_task345.py','tracking_task345.py'):
    shutil.copyfile(D/'source'/name,D/name)
for path in (D/'normal345').glob('*.py'):
    text=path.read_text('utf8').replace(oldSHA,full['SHA']).replace('12468+u','16879+u')
    # Parent timer is local-only; all true SSH controllers must be gone first.
    text=text.replace("pattern='","pattern='RMPOLAR|watch_|run339_|run342_|run_once_after_resume|",1)
    path.write_text(text,encoding='utf8')
launch=rename((S/'launch324_reference_tracking_once.py').read_text('utf8'))
start=launch.index('    recovery=');end=launch.index('    a=argparse.ArgumentParser()',start)
launch=launch[:start]+'''    final=read(T/'REFERENCE_H4_TRACKING_REPAIR_V324_20261102/reports/ROOT324_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json');assert final['passed']and final['totalWM']==16879
    evaluation=read(T/'FINAL324_IMPORT_CIM_REPAIR_EVAL_V339_20261102/reports/ROOT339_EVALUATION_FULL_RETURNED.json')['result'];assert evaluation['passed']and evaluation['strict_successes']==0
'''+launch[end:]
start=launch.index('    check=');end=launch.index('    pattern=',start)
launch=launch[:start]+'''    check=read(R/'CPU345_REUSE_EXACT344_SOURCE_ADMISSION.json');assert check['passed']and check['CPU344_optimizer_steps']==0 and check['currentlearner_SHA']==H(N/'source/tracking_learner345.py')
'''+launch[end:]
launch=launch.replace("pattern='","pattern='RMPOLAR|watch_|run339_|run342_|run_once_after_resume|continue_clean_sequential|",1)
write(D/'launch345_reference_tracking_once.py',launch)
status=rename((S/'collect324_status_readonly.py').read_text('utf8')).replace("patterns='","patterns='RMPOLAR|watch_|run339_|run342_|run_once_after_resume|",1)
write(D/'collect345_status_readonly.py',status)
cpu_final=rename((S/'review324_NEW_final_whole_CPU_UNUSED_once.py').read_text('utf8'))
cpu_final=cpu_final.replace('wm==12468+','wm==16879+').replace("('actor',48257),('critic',5317)","('actor',52636),('critic',9696)")
cpu_final=cpu_final.replace("s['actor_Adam_offset']==48257 and s['critic_Adam_offset']==5317","s['actor_Adam_offset']==52636 and s['critic_Adam_offset']==9696").replace("s['policy_horizon']==4","s['policy_horizon']==8").replace('newWM=wm-12468','newWM=wm-16879')
write(D/'review345_NEW_final_whole_CPU_UNUSED_once.py',cpu_final)
task=read(S/'TASK324_FROZEN.json')
def transform(value):
    if isinstance(value,str):return rename(value)
    if isinstance(value,dict):return{rename(key):transform(v)for key,v in value.items()}
    if isinstance(value,list):return[transform(v)for v in value]
    return value
task=transform(task);nonce=str(time.time_ns());remote=read(S/'reports/ROOT324_NORMAL900_JUMP_FULL_UTF8_AND_FORMAL_ACTUAL.json')['formal']['path']
task.update(run_id='REFERENCE_TRACKING345_'+nonce,job_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_REFERENCE_TRACKING345_'+nonce+'/tracker72',owner_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_REFERENCE_TRACKING345_'+nonce+'/owner72',
    source_SHA=full['SHA'],model_SHA=full['SHA'],model_path=remote,source_bytes=full['bytes'],model_bytes=full['bytes'],source_Adam_step=52636,source_WM_updates=16879,window_start_world_updates=16879,source_actor_Adam_step=52636,new_tracking_critic_Adam_step=9696,
    actor_policy_H=8,actor_direct_tracking_cost=True,actor_terminal_bootstrap=False,worker_SHA=H(D/'source/worker345.py'),source_CPU_report_SHA=H(fullpath),carrier_CPU_receipt_SHA=H(fullpath),
    actor_objective='sumdiscounted sameweightedtrackingcost/5 overH8;noexpattenuation/noalivemask/noactorbootstrap',reward_definition='actualexp(-sameweightedtrackingcost/5)unchangedforcriticandcomparison;actorH8directscaledcost',
    source_cpu_reuse='CPU344exactfinal324/H8directno-stepallAdamEMA',resume_scope='exactfinal324 actor103critic106_STD_allthreeAdamEMA_nromRNGWM16879;freshphysicalDRqueuesreplayepisodes',
    policy_rollback='none; full final324 actorAdam52636critic9696 restored',predecessor_actual='339actual0/80crossstrict56orientation24full8s/nativeviewspin;342pairedH8position.018897m;CPU344H8directgrad5.2800terminal0/no-step',
    human_authorization='2026-11-01newtrackingstart/continueclose_thenrepair;targeted objective repair after actual339evalandnativeview',new_budget_seconds=0)
task['reference']['path']='reference345.npz'
put(D/'TASK345_FROZEN.json',task)
put(D/'reports/CPU345_REUSE_EXACT344_SOURCE_ADMISSION.json',dict(epoch=time.time(),passed=True,CPU344_report=str(C/'reports/CPU344_RESTORED324_H8_DIRECT_NO_STEP.json'),CPU344_SHA=H(C/'reports/CPU344_RESTORED324_H8_DIRECT_NO_STEP.json'),CPU344_optimizer_steps=0,currentlearner_SHA=H(D/'source/tracking_learner345.py'),source_final_SHA=full['SHA'],naming_only_CPU344_behavior=True,real_live_gradient_required_before_first_update=True,newmodelreads=0))
normal=[D/'normal345/normal345_common.py',D/'normal345/collect345_tracking_formal_cost_normal900_UNUSED_once.py',D/'teacher_task345.py']
put(D/'normal345/INDEX345_NORMAL_SOURCE_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in normal]))
for path in D.rglob('*.py'):ast.parse(path.read_text('utf8'),filename=str(path))
spec=importlib.util.spec_from_file_location('static345_protocol',D/'teacher_task345.py');protocol=importlib.util.module_from_spec(spec);spec.loader.exec_module(protocol)
assert protocol.validate_task(task)
assert H(D/'reference345.npz')==task['reference']['SHA']
assert 'REFERENCE_TRACKING_BPTT324_COMPLETE' in worker and "kind='REFERENCE_TRACKING_BPTT345_COMPLETE'" in worker
assert '16879' in worker and '52636' in learner and '9696' in learner
assert 'k=8;' in learner and 'total=total-(.99**i)*cost/5.' in learner
files=[path for path in sorted(D.rglob('*'))if path.is_file()and'__pycache__'not in path.parts]
index=D/'INDEX345_SOURCE_TASK_CALLERS_FROZEN.json';put(index,dict(epoch=time.time(),files=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in files]))
put(P/'reports/STATIC345_H8_DIRECT_PRODUCTION_PACKAGE.json',dict(epoch=time.time(),passed=True,root=str(D),run_id=task['run_id'],INDEX_SHA=H(index),source_final324=full['SHA'],CPU344reused=True,actorH8direct=True,WMH32=True,actorvalue0=True,postround_must_prepare_before_GO=True,GO=False,network=0,model_reads=0))
print(json.dumps(dict(passed=True,root=str(D),run_id=task['run_id'],INDEX_SHA=H(index),GO=False)))
