"""Independent443 continuation from final433, saturation-aware exploration only; original windows/physical/reward."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import re
import time

P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports'
O=T/'RL_BOUNDED_ACTUAL_PPO_PRODUCTION_V433_20261102'
OQ=T/'RL433_SINGLE_PROCESS_POSTROUND_V434_20261102'
OE=T/'RL433_FIRST_ACTUAL_INDEPENDENT_EVAL_V437_20261102'
C=T/'RL_SATURATION_EXPLORATION_REPAIR_V442_20261102'
N=T/'RL_SATURATION_ACTUAL_PPO_PRODUCTION_V443_20261102'
Q=T/'RL443_SINGLE_PROCESS_POSTROUND_V444_20261102'
E=T/'RL443_FINAL_INDEPENDENT_EVAL_V444_20261102'
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
read=lambda path:json.loads(path.read_bytes())
def put(path,value):
    with path.open('x',encoding='utf8')as stream:json.dump(value,stream,indent=2,ensure_ascii=False,allow_nan=False)
def rewrite(path,source):
    ast.parse(source);path.write_bytes(source.encode('utf8'))
def rename(source):
    for old,new in((O,N),(OQ,Q),(OE,E)):
        source=source.replace(str(old),str(new)).replace(old.as_posix(),new.as_posix())
    for old,new in((433,443),(434,444),(437,444)):
        source=re.sub(r'(?<=[A-Za-z_])'+str(old)+r'(?!\d)',str(new),source)
    return source
cpu_path=C/'reports/CPU442_SATURATION_EXPLORATION_FULL_RESTORE_ADMISSION.json'
cpu=read(cpu_path);assert cpu['passed']and cpu['production_optimizer_steps']==0
assert cpu['learnerSHA']==H(C/'source/actual_transition_learner442.py')
facts=read(R/'ANALYSIS440_ACTUAL_FINAL433_EVAL437_FACTS_AND_MANIFOLD.json')
assert facts['strict']==facts['whole_footprint_clear']==0 and facts['allSSHclosedFREE']
source_cpu_path=O/'reports/ROOT433_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'
full=read(source_cpu_path);assert full['SHA']==cpu['sourceSHA']and full['Pi']==161
source_final=read(O/'reports/ROOT433_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')['roles']['jump_72']['formal']
for origin,dest in((O,N),(OQ,Q),(OE,E)):
    assert not dest.exists();dest.mkdir();(dest/'reports').mkdir()
    for path in sorted(origin.rglob('*')):
        if not path.is_file()or'__pycache__'in path.parts:continue
        relative=path.relative_to(origin)
        if 'reports'in relative.parts or path.name.startswith('INDEX')or path.name.startswith('TASK')or 'current_closed'in str(relative):continue
        if path.suffix not in('.py','.json','.npz'):continue
        target=dest/rename(str(relative));target.parent.mkdir(parents=True,exist_ok=True)
        if path.suffix=='.py':rewrite(target,rename(path.read_text('utf8')))
        else:target.write_bytes(path.read_bytes())

# Exact CPU-tested learner, including CUDA restore (CPU test used a separate fixture RNG).
for dest in(N,E):
    (dest/'source/actual_transition_learner442.py').write_bytes((C/'source/actual_transition_learner442.py').read_bytes())
(N/'reports/CPU443_REUSED442_SATURATION_ADMISSION.json').write_bytes(cpu_path.read_bytes())
worker_path=N/'source/worker443.py';worker=worker_path.read_text('utf8')
worker=worker.replace("ck['kind']=='ACTUAL_RESIDUAL_PPO416_COMPLETE' and ck['total_WM_updates']==25556 and ck['actual_new_PPO_updates']==160",
    "ck['kind']=='ACTUAL_RESIDUAL_PPO433_COMPLETE' and ck['total_WM_updates']==30731 and ck['actual_new_PPO_updates']==161")
worker=worker.replace('25556','30731').replace('from actual_transition_learner427 import ActualTransitionLearner427','from actual_transition_learner442 import ActualTransitionLearner442').replace('learner=ActualTransitionLearner427(','learner=ActualTransitionLearner442(')
worker=worker.replace('restoreexactfinal416/allAdamEMA_STD_WM30731andsavedorigin;postAdamKLresidualboundactualPPO;freshphysicalepisodes','restoreexactfinal433/allAdamEMA_STD_WM30731andsavedorigin;saturationawareexploration/fullGaussianKL;freshphysicalepisodes')
assert "ck['kind']=='ACTUAL_RESIDUAL_PPO433_COMPLETE'"in worker and 'ActualTransitionLearner442'in worker
rewrite(worker_path,worker)

contract=rename((O/'teacher_task433.py').read_text('utf8'))
contract=contract.replace('8365d243006ef5ed6818d01298003107808f918347ad929f4ea936544f96e01a',full['SHA'])
for old,new in(('33964153','34402073'),('25556','30731'),('56304','56465'),('13364','13525')):contract=contract.replace(old,new)
contract=contract.replace("planned_reference_tracker=True)","planned_reference_tracker=True,saturation_aware_exploration=True)")
contract=contract.replace("trust=d['actor_trust_step'];", "assert d['exploration_gain']==.6 and d['exploration_max_std']==2. and d['latent_std_floor']==.15\n trust=d['actor_trust_step'];")
for path in(N/'teacher_task443.py',N/'tracking_task443.py',N/'control443/teacher_task443.py',N/'source/teacher_task443.py',N/'source/tracking_task443.py',E/'source/teacher_task443.py',E/'source/tracking_task443.py'):
    rewrite(path,contract)

task=read(O/'TASK433_FROZEN.json')
def tasknames(value):
    if isinstance(value,str):return value if re.fullmatch('[0-9a-f]{64}',value)or value.startswith('GPU-')else rename(value)
    if isinstance(value,list):return[tasknames(item)for item in value]
    if isinstance(value,dict):return{key:tasknames(item)for key,item in value.items()}
    return value
task=tasknames(task);nonce=str(time.time_ns());job='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_SATURATION_ACTUAL_PPO443_'+nonce
task.update(kind='ACTUAL_ONPOLICY_RESIDUAL_PPO_400N50_V443',run_id='ACTUAL_RESIDUAL_PPO443_'+nonce,
    job_root=job+'/tracker72',owner_root=job+'/owner72',source_SHA=full['SHA'],model_SHA=full['SHA'],
    model_bytes=full['bytes'],source_bytes=full['bytes'],model_path=source_final['path'],source_parent_SHA=read(O/'TASK433_FROZEN.json')['source_SHA'],
    source_Adam_step=56465,source_actor_Adam_step=56465,new_tracking_critic_Adam_step=13525,
    source_WM_updates=30731,window_start_world_updates=30731,worker_SHA=H(worker_path),
    source_CPU_report_SHA=H(cpu_path),carrier_CPU_receipt_SHA=H(source_cpu_path),CPU443_SHA=H(cpu_path),
    human_authorization='RLup270 proactive targeted repair afteractual4370strict0wholeclear/36full8s and savedresidualsaturation',
    source_cpu_reuse='ExactCPU442learnerbytes/fullfinal433restore; no repeatPTdecode',
    predecessor_actual='437actual0strict0wholeclear/44orientation36full8smean4.30925/nativeviewed;441savedresidualsaturation;442CPUnewexplorationpasses',
    policy_rollback='none; restoreexactfinal433allstate',resume_scope='Fullfinal433actorcriticSTDallAdamEMAoriginWM30731;freshphysicalDRrollout;savedCUDAresidualRNGrestored',
    actor_objective='SameactualPPOrewarddoneGAE32/postAdamfullGaussianKL<=.01/residualdelta<=.05; state-dependentlatentGaussianexploration',
    learning_scope='actual_onpolicy_residual_PPO',saturation_aware_exploration=True,
    exploration_protocol=dict(kind='SATURATION_AWARE_LATENT_GAUSSIAN',floor=.15,gain=.6,max_std=2.,fullGaussianKL=True,deterministic_action_unchanged=True))
put(N/'TASK443_FROZEN.json',task)
launcher=N/'launch443_actual_residual_RL_once.py';source=launcher.read_text('utf8')
source=source.replace("T/'RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V416_20261102/reports/ROOT416_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'", "T/'RL_BOUNDED_ACTUAL_PPO_PRODUCTION_V433_20261102/reports/ROOT433_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'")
source=source.replace("final['totalWM']==25556", "final['totalWM']==30731")
source=source.replace("T/'RL416_FINAL_INDEX_REPAIRED_EVAL_V423_20261102/reports/ROOT423_EVALUATION_FULL_RETURNED.json'", "T/'RL433_FIRST_ACTUAL_INDEPENDENT_EVAL_V437_20261102/reports/ROOT437_EVALUATION_FULL_RETURNED.json'")
source=source.replace('CPU443_REUSED428_TRUST_ADMISSION.json','CPU443_REUSED442_SATURATION_ADMISSION.json')
source=source.replace("check['committed_training_optimizersteps']==0", "check['production_optimizer_steps']==0")
source=source.replace("N/'source/actual_transition_learner427.py'", "N/'source/actual_transition_learner442.py'")
source=source.replace("pattern='MOD4_H1", "pattern='collect_actual|collect_generic|E1collect|PAIR|postround|MOD4_H1")
source=source.replace('CPU428fullfinal416restore/actualsavedrolloutpostAdamtruststeprestored; liveactualonpolicygradientandtrustboundrequired', 'CPU442fullfinal433restore/syntheticstate-dependentGaussianfixture; liveactualonpolicygradientandfullGaussiantrustrequired')
rewrite(launcher,source)
normal=N/'normal443'
path=normal/'collect443_fullclose_transfer_once.py';source=path.read_text('utf8').replace('25556','30731');rewrite(path,source)
review=N/'review443_new_final_full_CPU_once.py';source=review.read_text('utf8')
for old,new in(('25556','30731'),('56304','56465'),('13364','13525')):source=source.replace(old,new)
source=source.replace("assert s['actor_trust_protocol']['KL_limit']==.01", "assert s['exploration_protocol']['kind']=='SATURATION_AWARE_LATENT_GAUSSIAN'and s['exploration_protocol']['gain']==.6 and s['exploration_protocol']['max_std']==2.\n    assert s['actor_trust_protocol']['KL_limit']==.01")
rewrite(review,source)
collector=N/'collect443_status_readonly.py';source=collector.read_text('utf8').replace("patterns='MOD4_H1", "patterns='collect_actual|collect_generic|PAIR|postround|E1collect|MOD4_H1");rewrite(collector,source)

# New deterministic final evaluator; all originalphysical/acceptance code intact.
evalpath=E/'source/evaluate444.py';source=evalpath.read_text('utf8')
assert "ck['kind']=='ACTUAL_RESIDUAL_PPO443_COMPLETE'"in source
rewrite(evalpath,source)
etask=read(OE/'TASK437_FROZEN.json')
etask.update(kind='FROZEN443_ACTUAL_RESIDUAL_PPO_EVAL444',source_run=task['run_id'],model_path=None,model_SHA=None,model_bytes=None,
    source_full_CPU_receipt_SHA=None,expected_Pi_updates=None,worker_SHA=H(evalpath),pending_actual_final_identity=True,
    human_request='ActualRL443 finalactor+savedorigin+samefixed50Hztable; deterministic eval, noonlineMPC',
    distinct_evaluation_purpose='Immediately evaluate saturation-aware actualPPO443 finalafterfullsave/safeclose')
put(E/'TASK444_PENDING_FINAL_IDENTITY.json',etask)
path=E/'contract444.py';source=path.read_text('utf8').replace('FROZEN443_ACTUAL_RESIDUAL_PPO_EVAL444','FROZEN443_ACTUAL_RESIDUAL_PPO_EVAL444');rewrite(path,source)
post=Q/'postround444_close_actual443_eval_once.py';source=post.read_text('utf8')
# The old postround has its own E434 path; declare the actual new E explicitly.
source=re.sub(r"E=T/'[^']+'", "E=T/"+repr(E.name), source, count=1)
source=source.replace("pattern='MOD4_H1", "pattern='collect_actual|collect_generic|E1collect|PAIR|MOD4_H1")
# A newknowncontroller may start between normalclose and eval. Wait locally a
# second time instead of consuming/failing the unique evaluation entrance.
needle=" inline(E/'run444_eval_once.py',['--caller-index-SHA',H(index)])"
waitagain=""" while True:
  check=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
  live=json.loads(check.stdout)if check.stdout.strip()else[];live=live if isinstance(live,list)else[live]
  if not any(row['ProcessId']!=os.getpid()for row in live):break
  time.sleep(10)
 inline(E/'run444_eval_once.py',['--caller-index-SHA',H(index)])"""
assert needle in source;source=source.replace(needle,waitagain)
rewrite(post,source)
for path in Q.glob('*.py'):assert N.name in path.read_text('utf8')

# Check each actual importsite contract and baseline identities before freezing.
for i,path in enumerate((N/'teacher_task443.py',N/'control443/teacher_task443.py',N/'source/teacher_task443.py',N/'source/tracking_task443.py')):
    spec=importlib.util.spec_from_file_location('contract443_'+str(i),path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.validate_task(task)
    assert H(path)==H(N/'teacher_task443.py')
for path in list(N.rglob('*.py'))+list(Q.rglob('*.py'))+list(E.rglob('*.py')):ast.parse(path.read_bytes())
assert H(N/'source/actual_transition_learner442.py')==cpu['learnerSHA']==H(E/'source/actual_transition_learner442.py')
assert H(N/'feedforward389.json')==task['fixed_command_feedforward']['SHA']==H(E/'feedforward389.json')
assert H(N/'reference389.npz')==task['reference']['SHA']==H(E/'reference389.npz')
assert N.name in post.read_text('utf8')and E.name in post.read_text('utf8')
assert 'path!=index'in post.read_text('utf8')
put(normal/'INDEX443_NORMAL_SOURCE_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in(normal/'normal443_common.py',normal/'collect443_fullclose_transfer_once.py',N/'teacher_task443.py')]))
frozen=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in sorted(N.rglob('*'))if path.is_file()and'__pycache__'not in path.parts]
put(N/'INDEX443_SOURCE_TASK_CALLERS_FROZEN.json',dict(epoch=time.time(),files=frozen,self_excluded=True))
frozen=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for root in(Q,E)for path in sorted(root.rglob('*'))if path.is_file()and'__pycache__'not in path.parts]
put(Q/'INDEX444_POSTROUND_FOR443_FROZEN.json',dict(epoch=time.time(),files=frozen,self_excluded=True))
put(R/'STATIC443_SATURATION_PPO444_PACKAGE_NO_PTREAD.json',dict(epoch=time.time(),passed=True,root=str(N),run=task['run_id'],
    indexSHA=H(N/'INDEX443_SOURCE_TASK_CALLERS_FROZEN.json'),workerSHA=task['worker_SHA'],learnerSHA=cpu['learnerSHA'],
    source_finalSHA=full['SHA'],source_offsets=[56465,13525,30731],postroot=str(Q),postindexSHA=H(Q/'INDEX444_POSTROUND_FOR443_FROZEN.json'),evalroot=str(E),
    CPU442_exactlearnerbytes=True,source_root_control_contract_identical=True,source_fullAdam_noreset=True,
    deterministic_evalaction_same=True,reward_physics_unchanged=True,allAST=True,START=False,network=0,SDK=0,physics=0,modelreads=0))
print(json.dumps(dict(passed=True,run=task['run_id'],indexSHA=H(N/'INDEX443_SOURCE_TASK_CALLERS_FROZEN.json'),postindexSHA=H(Q/'INDEX444_POSTROUND_FOR443_FROZEN.json'),workerSHA=task['worker_SHA'])),flush=True)
