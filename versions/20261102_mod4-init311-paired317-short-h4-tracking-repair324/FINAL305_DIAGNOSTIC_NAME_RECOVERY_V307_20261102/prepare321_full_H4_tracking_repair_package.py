"""Prepare a launchable independent321 repair after CPU320; no training GO.

Reuse original sole canonical writer, finite save/close contracts and full state.
No new writer is started while the separate W35 original owner is active.
"""
from pathlib import Path
import ast,hashlib,importlib.util,json,re,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;O=T/'REFERENCE_TRACKING_REAL_VALUE_V305_20261101';P=T/'REFERENCE_H4_TRACKING_ONLY_REPAIR_V320_20261102'
D=T/'REFERENCE_H4_TRACKING_REPAIR_V321_20261102';assert not D.exists();D.mkdir();R=D/'reports';R.mkdir()
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def rename(text,old='305',new='321'):
    preserved=[]
    def hide(m):preserved.append(m.group());return '@SHA'+str(len(preserved)-1)+'@'
    text=re.sub(r'\b[0-9a-f]{64}\b',hide,text);text=re.sub(r'(?<=[A-Za-z_])'+old+r'(?!\d)',new,text)
    for i,value in enumerate(preserved):text=text.replace('@SHA'+str(i)+'@',value)
    return text
def write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True);ast.parse(text);path.write_bytes(text.encode())

proof=json.loads((N/'reports/ROOT307_NEW_FINAL305_WHOLE_CPU_RETURNED_ACTUAL.json').read_bytes())
CPU=json.loads((P/'reports/CPU320_RESTORED305_H4_REPAIR_NO_STEP.json').read_bytes())
assert proof['passed']and CPU['passed']and CPU['synthetic_H4_no_step']['actor_terminal_bootstrap']is False
shutil.copytree(O/'source',D/'source',ignore=shutil.ignore_patterns('__pycache__'))
shutil.copyfile(O/'reference305.npz',D/'reference305.npz')
for name in('worker305.py','tracking_wm305.py','terrain305.py','tracking_task305.py','teacher_task305.py','complete_save305.py','tracking_survival305.py'):
    write(D/'source'/rename(name),rename((O/'source'/name).read_text('utf8')))
for path in(O/'control305').glob('*.py'):write(D/'control321'/rename(path.name),rename(path.read_text('utf8')))
for name in('launch305_reference_tracking_once.py','collect305_status_readonly.py','teacher_task305.py','tracking_task305.py'):
    write(D/rename(name),rename((O/name).read_text('utf8')))

learner=rename((P/'source/tracking_learner320.py').read_text('utf8'),'320','321')
learner=rename(learner,'305','321');learner=rename(learner,'315','321')
write(D/'source/tracking_learner321.py',learner)
reference=rename((P/'source/tracking_reference315.py').read_text('utf8'),'315','321')
write(D/'source/tracking_reference321.py',reference)

path=D/'source/worker321.py';worker=path.read_text('utf8')
worker=worker.replace("ck['kind']=='REFERENCE_TRACKING_BPTT300_COMPLETE' and ck['total_WM_updates']==9712 and ck['actual_new_Pi_updates']==2593", "ck['kind']=='REFERENCE_TRACKING_BPTT305_COMPLETE' and ck['total_WM_updates']==12468 and ck['actual_new_Pi_updates']==2724")
worker=worker.replace('assert wm.updates==9712 and all(int(v[\'step\'])==9712',"assert wm.updates==12468 and all(int(v['step'])==12468")
worker=worker.replace('inherited_WM_updates=9712','inherited_WM_updates=12468').replace('inherited_world_updates=9712','inherited_world_updates=12468').replace('assert wm.updates>9712','assert wm.updates>12468')
worker=worker.replace('ACTUAL321_H32_PAIRED_REAL_WM_ERROR_BEFORE_PI','ACTUAL321_H32_PAIRED_REAL_WM_METRICS_BEFORE_PI')
worker=worker.replace("policy_rollback_source='restore exactfinal300 actor103critic106/allthreeAdam/STD/WM9712/norm/RNG; repair survival+actualTD only'", "policy_rollback_source='restoreexactfinal305/allAdam/EMA/STD/WM12468;actorH4trackingonly,WMH32,terminalholdrest;freshphysicalepisodes'")
worker=worker.replace("reference_phase_steps=copied(epstep),replay_saved=False,", "reference_phase_steps=copied(epstep),replay_saved=False,actor_policy_H=4,WM_training_H=32,actor_terminal_bootstrap=False,")
write(path,worker)

oldsha='e700e546e3cada81dee7cdd6ed1aa59d51eb0d0d1932f0dfda928799de7812a8'
protocolpaths=[D/'teacher_task321.py',D/'tracking_task321.py',D/'source/teacher_task321.py',D/'source/tracking_task321.py',D/'control321/teacher_task321.py']
for path in protocolpaths:
    text=path.read_text('utf8').replace(oldsha,proof['SHA']).replace('model_bytes=32593725','model_bytes=32695597').replace('source_WM_updates=9712','source_WM_updates=12468').replace('source_actor_Adam_step=45533','source_actor_Adam_step=48257').replace('new_tracking_critic_Adam_step=2593','new_tracking_critic_Adam_step=5317').replace('==9712+','==12468+').replace('==45533+pi','==48257+pi').replace('==2593+pi','==5317+pi')
    text=text.replace("source_WM_updates=12468,source_actor_Adam_step=48257,", "source_WM_updates=12468,source_actor_Adam_step=48257,actor_policy_H=4,WM_H=32,actor_terminal_bootstrap=False,")
    needle="assert r['student']['critic_same_tracking_return']and not r['student']['Fudan_objective_used']"
    text=text.replace(needle,needle+"\n    assert r['student']['policy_H']==4 and r['student']['WM_H']==32 and r['student']['actor_terminal_bootstrap']is False")
    text=text.replace("planned_reference_tracker=True,future_actual_depth_in_H32=False", "planned_reference_tracker=True,actor_policy_H=4,WM_H=32,actor_terminal_bootstrap=False,future_actual_depth_in_H32=False")
    write(path,text)

# Integrate312 in this independently versioned control tree; do not modify305.
classification=T/'FINAL_REPORT_CLASSIFICATION_REPAIR_V312_20261102/source'
shutil.copyfile(classification/'report_classification312.py',D/'control321/report_classification312.py')
write(D/'control321/model2050_240_fullstate_slot_node.py',rename((classification/'model2050_240_fullstate_slot_node_UNUSED312.py').read_text('utf8')))
(D/'normal321').mkdir()
for path in(O/'normal305').glob('*.py'):
    text=rename(path.read_text('utf8')).replace(oldsha,proof['SHA']).replace('9712+u','12468+u')
    if path.name.startswith('collect305_'):
        text=rename((classification/'collect_tracking_formal_cost_normal900_UNUSED312.py').read_text('utf8')).replace('9712+u','12468+u')
    write(D/'normal321'/rename(path.name),text)

path=D/'launch321_reference_tracking_once.py';text=path.read_text('utf8')
start=text.index('    closed=');end=text.index('    a=argparse.ArgumentParser()',start)
text=text[:start]+'''    recovery=read(T/'FINAL305_DIAGNOSTIC_NAME_RECOVERY_V307_20261102/reports/ROOT307_EXACT_FINAL_OWN_CLOSURE_AND_DIAGNOSTIC_CLASSIFICATION.json');assert recovery['passed']and recovery['canonical_None']
    evaluation=read(T/'RECOVERED305_TRACKING_REPLAY_EVAL_V308_20261102/reports/ROOT308_EVALUATION_FULL_RETURNED.json')['result'];assert evaluation['passed']and evaluation['strict_successes']==0
'''+text[end:]
start=text.index('    check=');end=text.index('    pattern=',start)
text=text[:start]+'''    check=read(R/'CPU321_REUSE_EXACT320_SOURCE_ADMISSION.json');assert check['passed']and check['CPU320_optimizer_steps']==0 and check['currentlearner_SHA']==H(N/'source/tracking_learner321.py')
    final=read(T/'FINAL305_DIAGNOSTIC_NAME_RECOVERY_V307_20261102/reports/ROOT307_NEW_FINAL305_WHOLE_CPU_RETURNED_ACTUAL.json');assert final['passed']and final['totalWM']==12468
'''+text[end:]
text=text.replace("pattern='", "pattern='watch_w35_eval_terminal|collect_attempt2_wait_and_sdk|snapshot_w35|snapshot_adaptation|deploy_w35|launch_w35|run317_diagnostic|run311_probe|",1)
text=text.replace('ACTUAL321_H32_PAIRED_REAL_WM_ERROR_BEFORE_PI','ACTUAL321_H32_PAIRED_REAL_WM_METRICS_BEFORE_PI')
write(path,text)
path=D/'collect321_status_readonly.py';text=path.read_text('utf8').replace('ACTUAL321_H32_PAIRED_REAL_WM_ERROR_BEFORE_PI','ACTUAL321_H32_PAIRED_REAL_WM_METRICS_BEFORE_PI')
text=text.replace("patterns='","patterns='watch_w35_eval_terminal|collect_attempt2_wait_and_sdk|snapshot_w35|snapshot_adaptation|deploy_w35|launch_w35|",1);write(path,text)

task=json.loads((O/'TASK305_FROZEN.json').read_bytes())
for key in('kind','generation'):task[key]=rename(task[key])
nonce=str(time.time_ns())
task.update(run_id='REFERENCE_TRACKING321_'+nonce,job_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_REFERENCE_TRACKING321_'+nonce+'/tracker72',owner_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_REFERENCE_TRACKING321_'+nonce+'/owner72',worker_SHA=H(D/'source/worker321.py'),source_SHA=proof['SHA'],model_SHA=proof['SHA'],source_bytes=proof['bytes'],model_bytes=proof['bytes'],model_path=proof['remote_path'],source_WM_updates=12468,window_start_world_updates=12468,source_actor_Adam_step=48257,new_tracking_critic_Adam_step=5317,carrier_CPU_receipt_SHA=H(N/'reports/ROOT307_NEW_FINAL305_WHOLE_CPU_RETURNED_ACTUAL.json'),source_CPU_report_SHA=H(N/'reports/ROOT307_NEW_FINAL305_WHOLE_CPU_RETURNED_ACTUAL.json'),source_Adam_step=48257,source_cpu_reuse='CPU320 exactfinal305 actorcriticSTDallAdam/EMA/H4no-step, renamedidenticallearner; live actualgradient beforestep still required',actor_policy_H=4,WM_H=32,actor_terminal_bootstrap=False,reference_terminal_hold='phase>249posefixed/allvelocitytargets0; original250labelsunchanged',predecessor_actual='308failed0/80,311referenceinitnotfix;317actualH32.340mH4.0219m;CPU319terminalgrad56xtracking;CPU320pureH4gradientpass',reward_definition='sameexp(-weightedtrackingcost/5),actorH4nolearnedterminalbootstrap;actualTDcritic/EMAunchanged',resume_scope='exactfinal305 fullactorcriticSTDthreeAdam/EMA/norm/RNG;freshphysicalDRqueue/replay/episode',human_authorization='2026-11-01newtrackingstartandcontinueclose_thenrepair',new_budget_seconds=0)
put(D/'TASK321_FROZEN.json',task)
# Reuse the completed320 experiment, justified by an exact naming-only mapping.
mapped=rename(rename(rename((P/'source/tracking_learner320.py').read_text('utf8'),'320','321'),'305','321'),'315','321')
assert mapped==(D/'source/tracking_learner321.py').read_text('utf8')
put(R/'CPU321_REUSE_EXACT320_SOURCE_ADMISSION.json',dict(epoch=time.time(),passed=True,CPU320_report=str(P/'reports/CPU320_RESTORED305_H4_REPAIR_NO_STEP.json'),CPU320_SHA=H(P/'reports/CPU320_RESTORED305_H4_REPAIR_NO_STEP.json'),CPU320_optimizer_steps=0,CPU320_synthetic_fixture_not_skill=True,naming_onlyexactlearner=True,currentlearner_SHA=H(D/'source/tracking_learner321.py'),source_final_SHA=proof['SHA'],actor48257_critic5317_WM12468_EMA_exact=True,actorH4_WMH32=True,terminal_gradient_zero=True,combined_gradient_finite_nonzero=True,new_checkpoint_reads=0,new_GO=False))
put(R/'SOURCE321_TARGETED_REPAIR_READY_NO_GO.json',dict(epoch=time.time(),passed_static=True,task=str(D/'TASK321_FROZEN.json'),source_final_SHA=proof['SHA'],plannedrepair='H4puretrackingactor,H32WM,actualTDcritic/EMA,315terminalrest,312finalclassifier',no_new_GO=True,production_not_started=True,canonical_solewriter_preserved=True,wait_for_other_W35_fullsaveexit=True,postround='After normal321 and newfullCPU, new322independentfirstepisodes/actualreplay, decidecontinueorrepair; no consumedonce replay'))
files=[D/'normal321/normal321_common.py',D/'normal321/collect321_tracking_formal_cost_normal900_UNUSED_once.py',D/'teacher_task321.py']
put(D/'normal321/INDEX321_NORMAL_SOURCE_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in files]))
for path in D.rglob('*.py'):ast.parse(path.read_text('utf8'),filename=str(path))
spec=importlib.util.spec_from_file_location('contract321',D/'teacher_task321.py');protocol=importlib.util.module_from_spec(spec);spec.loader.exec_module(protocol);protocol.validate_task(task)
files=[path for path in sorted(D.rglob('*'))if path.is_file()and'__pycache__'not in path.parts and path.suffix in('.py','.json','.npz')]
index=D/'INDEX321_SOURCE_TASK_CALLERS_FROZEN.json';put(index,dict(epoch=time.time(),files=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in files]))
print(json.dumps(dict(passed_static=True,root=str(D),index_SHA=H(index),run_id=task['run_id'],new_GO=False,CPU320_reused=True)))
