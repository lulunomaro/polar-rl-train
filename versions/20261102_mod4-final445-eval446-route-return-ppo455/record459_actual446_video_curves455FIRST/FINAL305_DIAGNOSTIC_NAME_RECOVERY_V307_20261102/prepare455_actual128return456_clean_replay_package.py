"""Independent455 full445 continuation, actual128return; static-only copy excludes all inherited replay/report artifacts."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import re
import time

P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports'
O=T/'RL_SATURATION_ACTUAL_PPO_PRODUCTION_V445_20261102'
OQ=T/'RL445_SINGLE_PROCESS_POSTROUND_V446_20261102'
OE=T/'RL445_FINAL_INDEPENDENT_EVAL_V446_20261102'
C=T/'RL_LAUNCH_LANDING_RETURN_REPAIR_V454_20261102'
N=T/'RL_ACTUAL128_RETURN_PPO_PRODUCTION_V455_20261102'
Q=T/'RL455_SINGLE_PROCESS_POSTROUND_V456_20261102'
E=T/'RL455_FINAL_INDEPENDENT_EVAL_V456_20261102'
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
read=lambda path:json.loads(path.read_bytes())
def put(path,value):
    with path.open('x',encoding='utf8')as stream:json.dump(value,stream,indent=2,ensure_ascii=False,allow_nan=False)
def py(path,text):
    ast.parse(text);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(text.encode('utf8'))
def rename(text):
    for old,new in((O,N),(OQ,Q),(OE,E)):
        text=text.replace(str(old),str(new)).replace(old.as_posix(),new.as_posix()).replace(old.name,new.name)
    for old,new in((445,455),(446,456)):
        text=re.sub(r'(?<=[A-Za-z_])'+str(old)+r'(?!\d)',str(new),text)
    return text
cpu_path=C/'reports/CPU454_LAUNCH_LANDING_RETURN_FULL_RESTORE_ADMISSION.json';cpu=read(cpu_path)
assert cpu['passed']and cpu['production_optimizer_steps']==0 and cpu['source_offsets']==[56634,13694,36159]
assert cpu['delayed_event_fixture']['next_episode_leak']is False
assert cpu['learnerSHA']==H(C/'source/actual_transition_learner454.py')
facts=read(R/'ANALYSIS450_FINAL445_ACTUAL446_FACTS_AND_REPLAY_REFUSAL.json')
native=read(R/'DIAG452_ACTUAL446_NATIVE_EARLY_YAW_PITCH_AND_GAE_TIMING.json')
assert facts['strict']==facts['whole_footprint_clear']==0 and native['native_review']['current_model_native_viewed']
fullpath=O/'reports/ROOT445_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json';full=read(fullpath)
assert full['passed']and full['SHA']==cpu['sourceSHA']and full['Pi']==169
formal=read(O/'reports/ROOT445_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')['roles']['jump_72']['formal']
copied=[]
for origin,dest in((O,N),(OQ,Q),(OE,E)):
    assert not dest.exists();dest.mkdir();(dest/'reports').mkdir()
    paths=list(origin.glob('*.py'))
    if origin in(O,OE):paths+=list((origin/'source').rglob('*.py'))
    if origin==O:
        paths+=list((origin/'control445').glob('*.py'))+list((origin/'normal445').glob('*.py'))
    for path in sorted(paths):
        assert 'reports'not in path.relative_to(origin).parts and 'replay'not in path.relative_to(origin).parts
        target=dest/rename(str(path.relative_to(origin)));py(target,rename(path.read_text('utf8')))
        copied.append(dict(path=str(target),source=str(path),sourceSHA=H(path),newSHA=H(target)))
    if origin in(O,OE):
        for name in('feedforward389.json','reference389.npz'):(dest/name).write_bytes((origin/name).read_bytes())
for root in(N,E):(root/'source/actual_transition_learner454.py').write_bytes((C/'source/actual_transition_learner454.py').read_bytes())
(N/'reports/CPU455_REUSED454_ACTUALRETURN_ADMISSION.json').write_bytes(cpu_path.read_bytes())

worker_path=N/'source/worker455.py';worker=worker_path.read_text('utf8')
old="ck['kind']=='ACTUAL_RESIDUAL_PPO433_COMPLETE' and ck['total_WM_updates']==30731 and ck['actual_new_PPO_updates']==161"
assert old in worker
worker=worker.replace(old,"ck['kind']=='ACTUAL_RESIDUAL_PPO445_COMPLETE' and ck['total_WM_updates']==36159 and ck['actual_new_PPO_updates']==169")
worker=worker.replace('30731','36159').replace('ActualTransitionLearner442','ActualTransitionLearner454').replace('actual_transition_learner442','actual_transition_learner454')
worker=worker.replace('actor_policy_H=32','actor_policy_H=128')
worker=worker.replace('controls>=64','controls>=128')
worker=worker.replace('restoreexactfinal433','restoreexactfinal445').replace('saturationawareexploration/fullGaussianKL;freshphysicalepisodes','saturationawareexploration/fullGaussianKL/actual128returnlambda1;freshphysicalepisodes')
py(worker_path,worker)
contract=rename((O/'teacher_task445.py').read_text('utf8'))
contract=contract.replace('db6944ceca539106bb392a881185f1e85917efa5a9325bbeec72863f8240e04f',full['SHA'])
for a,b in(('34402073','34229331'),('30731','36159'),('56465','56634'),('13525','13694')):contract=contract.replace(a,b)
contract=contract.replace('actor_policy_H=32','actor_policy_H=128')
contract=contract.replace("actual_onpolicy_PPO=True,", "actual_onpolicy_PPO=True,actual_return_controls=128,GAE_lambda=1.,")
contract=contract.replace("count>=64", "count>=128").replace("d['actual_onpolicy_samples']==2560", "d['actual_onpolicy_samples']==10240 and d['rollout_controls']==128")
for path in(N/'teacher_task455.py',N/'tracking_task455.py',N/'control455/teacher_task455.py',N/'source/teacher_task455.py',N/'source/tracking_task455.py',E/'source/teacher_task455.py',E/'source/tracking_task455.py'):py(path,contract)

original_task=read(O/'TASK445_FROZEN.json')
def values(value):
    if isinstance(value,str):return value if re.fullmatch('[0-9a-f]{64}',value)or value.startswith('GPU-')else rename(value)
    if isinstance(value,list):return[values(x)for x in value]
    if isinstance(value,dict):return{k:values(x)for k,x in value.items()}
    return value
task=values(original_task);nonce=str(time.time_ns());job='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_ACTUAL128_RETURN_PPO455_'+nonce
task.update(kind='ACTUAL_ONPOLICY_RESIDUAL_PPO_400N50_V455',run_id='ACTUAL_RESIDUAL_PPO455_'+nonce,
    job_root=job+'/tracker72',owner_root=job+'/owner72',source_SHA=full['SHA'],model_SHA=full['SHA'],source_parent_SHA=original_task['source_SHA'],
    model_path=formal['path'],model_bytes=full['bytes'],source_bytes=full['bytes'],source_Adam_step=56634,
    source_actor_Adam_step=56634,new_tracking_critic_Adam_step=13694,source_WM_updates=36159,window_start_world_updates=36159,
    worker_SHA=H(worker_path),source_CPU_report_SHA=H(cpu_path),carrier_CPU_receipt_SHA=H(fullpath),CPU455_SHA=H(cpu_path),
    actor_policy_H=128,student_H=128,actual_return_controls=128,GAE_lambda=1.,
    human_authorization='RLup270 proactive targetedrepair afteractual4460strict0wholeclear/58full8s and actualearlypose/native452 timing evidence',
    predecessor_actual='446actual0strict0wholeclear/22orientation58full8smean6.15125; actual451replayrecovered/nativeviewed;454CPU128return/donemaskpasses',
    source_cpu_reuse='ExactCPU454learnerbytes/fullfinal445restore; no repeatPTdecode',policy_rollback='none; restoreexactfinal445allstate',
    resume_scope='Fullfinal445actorcriticSTDallAdamEMAoriginWM36159;freshphysicalDRrollout;savedCUDAresidualRNGrestored',
    actor_objective='Actual128controlonpolicyPPOreturn/gamma.99lambda1clip.2oneepoch; unchangedreward/actuator/exploration; fullGaussianKL<=.01/residualdelta<=.05',
    reward_definition='Unchanged exp(-sameweightedtrackingcost/5); actualdonecutsGAE/nextbootstrap; actual128controlreturn gamma.99lambda1',
    deterministic_eval_formula_unchanged=True,WM_H=32,WM_replay64_independent=True)
put(N/'TASK455_FROZEN.json',task)
launcher=N/'launch455_actual_residual_RL_once.py';text=launcher.read_text('utf8')
text=text.replace("T/'RL_BOUNDED_ACTUAL_PPO_PRODUCTION_V433_20261102/reports/ROOT433_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'", "T/'RL_SATURATION_ACTUAL_PPO_PRODUCTION_V445_20261102/reports/ROOT445_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'")
text=text.replace("final['totalWM']==30731", "final['totalWM']==36159")
text=text.replace("T/'RL433_FIRST_ACTUAL_INDEPENDENT_EVAL_V437_20261102/reports/ROOT437_EVALUATION_FULL_RETURNED.json'", "T/'RL445_FINAL_INDEPENDENT_EVAL_V446_20261102/reports/ROOT446_EVALUATION_FULL_RETURNED.json'")
text=text.replace('CPU455_REUSED442_SATURATION_ADMISSION.json','CPU455_REUSED454_ACTUALRETURN_ADMISSION.json').replace('actual_transition_learner442.py','actual_transition_learner454.py')
text=text.replace('CPU442fullfinal433restore/syntheticstate-dependentGaussianfixture; liveactualonpolicygradientandfullGaussiantrustrequired','CPU454fullfinal445restore/synthetic128return-donemaskfixture; liveactual128controlreturnPPO/fullGaussiantrustrequired')
text=text.replace("pattern='collect_actual", "pattern='stage_new|dispatch|retention|collect_actual")
py(launcher,text)
normal=N/'normal455';path=normal/'collect455_fullclose_transfer_once.py';py(path,path.read_text('utf8').replace('30731','36159'))
review=N/'review455_new_final_full_CPU_once.py';text=review.read_text('utf8')
for a,b in(('30731','36159'),('56465','56634'),('13525','13694')):text=text.replace(a,b)
text=text.replace("s['actor_horizon_actual_controls']==32", "s['actor_horizon_actual_controls']==128 and s['GAE_lambda']==1.")
py(review,text)
collector=N/'collect455_status_readonly.py';py(collector,collector.read_text('utf8').replace("patterns='collect_actual","patterns='stage_new|dispatch|retention|collect_actual"))

etask=values(read(OE/'TASK446_PENDING_FINAL_IDENTITY.json'))
etask.update(kind='FROZEN455_ACTUAL_RESIDUAL_PPO_EVAL456',source_run=task['run_id'],model_path=None,model_SHA=None,model_bytes=None,
    expected_Pi_updates=None,source_full_CPU_receipt_SHA=None,worker_SHA=H(E/'source/evaluate456.py'),pending_actual_final_identity=True,
    human_request='ActualRL455finalactor+origin+samefixed50Hzfeedforward,noonlineMPC',
    distinct_evaluation_purpose='Immediatelyevaluateactual128return455finalafterfullsave/safeclose')
put(E/'TASK456_PENDING_FINAL_IDENTITY.json',etask)
post=Q/'postround456_close_actual455_eval_once.py';text=post.read_text('utf8')
text=text.replace("pattern='collect_actual", "pattern='stage_new|dispatch|retention|collect_actual")
text=text.replace("normal=N/'normal455'", "normal=N/'normal455'")
py(post,text)
assert N.name in post.read_text('utf8')and E.name in post.read_text('utf8')
assert not(E/'replay').exists()and not(E/'RECORDED456_NATIVE_FRAMES').exists()
assert not list((E/'reports').iterdir())
assert "ck['kind']=='ACTUAL_RESIDUAL_PPO455_COMPLETE'"in(E/'source/evaluate456.py').read_text('utf8')
assert 'path!=index'in post.read_text('utf8')
for i,path in enumerate((N/'teacher_task455.py',N/'control455/teacher_task455.py',N/'source/teacher_task455.py',N/'source/tracking_task455.py')):
    spec=importlib.util.spec_from_file_location('contract455_'+str(i),path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.validate_task(task)
    assert H(path)==H(N/'teacher_task455.py')
for path in list(N.rglob('*.py'))+list(Q.rglob('*.py'))+list(E.rglob('*.py')):ast.parse(path.read_bytes())
assert H(N/'source/actual_transition_learner454.py')==cpu['learnerSHA']==H(E/'source/actual_transition_learner454.py')
assert H(N/'feedforward389.json')==task['fixed_command_feedforward']['SHA']==H(E/'feedforward389.json')
assert H(N/'reference389.npz')==task['reference']['SHA']==H(E/'reference389.npz')
put(normal/'INDEX455_NORMAL_SOURCE_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in(normal/'normal455_common.py',normal/'collect455_fullclose_transfer_once.py',N/'teacher_task455.py')]))
frozen=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in sorted(N.rglob('*'))if path.is_file()and'__pycache__'not in path.parts]
put(N/'INDEX455_SOURCE_TASK_CALLERS_FROZEN.json',dict(epoch=time.time(),files=frozen,self_excluded=True))
frozen=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for root in(Q,E)for path in sorted(root.rglob('*'))if path.is_file()and'__pycache__'not in path.parts]
put(Q/'INDEX456_POSTROUND_FOR455_FROZEN.json',dict(epoch=time.time(),files=frozen,self_excluded=True))
put(R/'STATIC455_ACTUAL128RETURN456_CLEAN_SOURCE_PACKAGE.json',dict(epoch=time.time(),passed=True,root=str(N),run=task['run_id'],
    indexSHA=H(N/'INDEX455_SOURCE_TASK_CALLERS_FROZEN.json'),workerSHA=task['worker_SHA'],learnerSHA=cpu['learnerSHA'],sourcefinalSHA=full['SHA'],
    source_offsets=[56634,13694,36159],postroot=str(Q),postindexSHA=H(Q/'INDEX456_POSTROUND_FOR455_FROZEN.json'),evalroot=str(E),
    static_onlycopy_no_oldreplay_or_renderreports=True,copiedfiles=copied,source_root_control_contract_identical=True,CPU454learnerbyteexact=True,
    actualPPOcontrols=128,GAElambda=1.,WMH32_unchanged=True,reward_physics_evalaction_unchanged=True,
    allAST=True,START=False,modelreads=0,SDK=0,physics=0,network=0))
print(json.dumps(dict(passed=True,run=task['run_id'],indexSHA=H(N/'INDEX455_SOURCE_TASK_CALLERS_FROZEN.json'),postindexSHA=H(Q/'INDEX456_POSTROUND_FOR455_FROZEN.json'),workerSHA=task['worker_SHA'])),flush=True)
