"""Independent429actualPPO postAdamtrustrepair; preserve416/417failures and allstate."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import re
import shutil
import time

P=Path(__file__).resolve().parent;T=P.parent
O=T/'RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V416_20261102'
OQ=T/'RL416_SINGLE_PROCESS_POSTROUND_V417_20261102'
OE=T/'RL416_FINAL_INDEX_REPAIRED_EVAL_V423_20261102'
C=T/'RL_ACTUAL_PPO_TRUST_STEP_REPAIR_V428_20261102'
N=T/'RL_BOUNDED_ACTUAL_PPO_PRODUCTION_V429_20261102'
Q=T/'RL429_SINGLE_PROCESS_POSTROUND_V430_20261102'
E=T/'RL429_FINAL_INDEPENDENT_EVAL_V430_20261102'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
def put(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def write(p,s):
 ast.parse(s);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(s.encode('utf8'))
def token(s,old,new):
 # Hashes and fixeddata never pass through a version substitution.
 hashes=[]
 def stash(m):hashes.append(m[0]);return f'__HASH_KEEP_{len(hashes)-1}__'
 s=re.sub(r'(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])',stash,s)
 s=re.sub(r'(?<=[A-Za-z_])'+str(old)+r'(?!\d)',str(new),s)
 for i,h in enumerate(hashes):s=s.replace(f'__HASH_KEEP_{i}__',h)
 return s
def rename(s):
 for a,b in ((O,N),(OQ,Q),(OE,E)):
  s=s.replace(str(a),str(b)).replace(a.as_posix(),b.as_posix())
 s=token(s,416,429);s=token(s,417,430)
 return s
for root in(N,Q,E):assert not root.exists();root.mkdir();(root/'reports').mkdir()
cpu=read(C/'reports/CPU428_ACTUAL_SAVED_ROLLOUT_TRUST_STEP_ADMISSION.json')
assert cpu['passed']and cpu['source_offsets']==[56304,13364,25556]
assert cpu['learnerSHA']==H(C/'source/actual_transition_learner427.py')
finalcpu=read(O/'reports/ROOT416_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json')
assert finalcpu['passed']and finalcpu['Pi']==160
for sub in('source','control416','normal416'):
 dest=N/rename(sub);dest.mkdir()
 for path in sorted((O/sub).rglob('*')):
  if not path.is_file()or'__pycache__'in path.parts:continue
  if path.name.startswith('INDEX'):continue
  target=dest/rename(str(path.relative_to(O/sub)))
  target.parent.mkdir(parents=True,exist_ok=True)
  if path.suffix=='.py':write(target,rename(path.read_text('utf8')))
  else:shutil.copyfile(path,target)
for name in('feedforward389.json','reference389.npz'):shutil.copyfile(O/name,N/name)
for name in('launch416_actual_residual_RL_once.py','collect416_status_readonly.py','review416_new_final_full_CPU_once.py','teacher_task416.py','tracking_task416.py'):
 write(N/rename(name),rename((O/name).read_text('utf8')))
shutil.copyfile(C/'source/actual_transition_learner427.py',N/'source/actual_transition_learner427.py')
shutil.copyfile(C/'reports/CPU428_ACTUAL_SAVED_ROLLOUT_TRUST_STEP_ADMISSION.json',N/'reports/CPU429_REUSED428_TRUST_ADMISSION.json')

# Worker restores final416carrier, originalsavedorigin and sameGPU RNG.
path=N/'source/worker429.py';s=path.read_text('utf8')
s=s.replace("ck['kind']=='REFERENCE_TRACKING_BPTT389_COMPLETE' and ck['total_WM_updates']==20419 and ck['actual_new_Pi_updates']==3508",
 "ck['kind']=='ACTUAL_RESIDUAL_PPO416_COMPLETE' and ck['total_WM_updates']==25556 and ck['actual_new_PPO_updates']==160")
s=s.replace('actual_transition_learner409 import ActualTransitionLearner409','actual_transition_learner427 import ActualTransitionLearner427')
s=s.replace('learner=ActualTransitionLearner409(', 'learner=ActualTransitionLearner427(')
s=s.replace('20419','25556')
s=s.replace('restoreexactfinal389/allAdamEMA_STD_WM25556andsavedorigin;actualrewarddonePPO;freshphysicalepisodes',
 'restoreexactfinal416/allAdamEMA_STD_WM25556andsavedorigin;postAdamKLresidualboundactualPPO;freshphysicalepisodes')
assert 'ACTUAL_RESIDUAL_PPO416_COMPLETE' in s and 'ActualTransitionLearner427' in s
write(path,s)

# Newcontract incorporates actual acceptedtruststep and new fullstateoffsets.
contract=(N/'teacher_task429.py').read_text('utf8')
contract=contract.replace(finalcpu['SHA'] if False else 'c760f8c2e3441756e1d4f6912d019c6bcdaafa456bdf6e48a9ce152395776f99',finalcpu['SHA'])
for a,b in(('32801003','33964153'),('20419','25556'),('56144','56304'),('13204','13364')):contract=contract.replace(a,b)
contract=contract.replace(' return True\n\ndef validate_first',
 " trust=d['actor_trust_step'];assert trust['applied']and trust['actual_KL']<=.01 and trust['actual_max_action_delta']<=.05 and trust['one_committed_Adam_step']\n return True\n\ndef validate_first")
for path in(N/'teacher_task429.py',N/'tracking_task429.py',N/'control429/teacher_task429.py'):write(path,contract)

# Launcher reuses CPU428 exactlearner, not anotherPTcheck, and startsoneoriginalowner.
path=N/'launch429_actual_residual_RL_once.py';s=path.read_text('utf8')
s=s.replace("final=read(T/'MPC_COMMAND_RESIDUAL_RL_V389_20261102/reports/ROOT389_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json');assert final['passed']and final['totalWM']==20419",
 "final=read(T/'RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V416_20261102/reports/ROOT416_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json');assert final['passed']and final['totalWM']==25556")
s=s.replace("evaluation=read(T/'RL389_EXACT_FINAL_INDEPENDENT_EVAL_V404_20261102/reports/ROOT404_EVALUATION_FULL_RETURNED.json')['result']", "evaluation=read(T/'RL416_FINAL_INDEX_REPAIRED_EVAL_V423_20261102/reports/ROOT423_EVALUATION_FULL_RETURNED.json')['result']")
s=s.replace("check=read(R/'CPU429_REUSED409_NO_STEP_ADMISSION.json');assert check['passed']and check['optimizersteps']==0 and check['learnerSHA']==H(N/'source/actual_transition_learner409.py')",
 "check=read(R/'CPU429_REUSED428_TRUST_ADMISSION.json');assert check['passed']and check['committed_training_optimizersteps']==0 and check['learnerSHA']==H(N/'source/actual_transition_learner427.py')")
s=s.replace('CPU409fullfinal389restore/actualPPOgradient/terminalGAE no-step; liveactualonpolicygradientbeforestep',
 'CPU428fullfinal416restore/actualsavedrolloutpostAdamtruststeprestored; liveactualonpolicygradientandtrustboundrequired')
assert 'CPU429_REUSED428_TRUST_ADMISSION' in s
write(path,s)

# FinalCPU checker newcarrierkind/newinitialoffsets; actuallearner427metadata.
path=N/'review429_new_final_full_CPU_once.py';s=path.read_text('utf8')
for a,b in(('20419','25556'),('56144','56304'),('13204','13364')):s=s.replace(a,b)
s=s.replace("    assert 'actual_RL_rollout'in s", "    assert s['actor_trust_protocol']['KL_limit']==.01 and s['actor_trust_protocol']['max_action_delta']==.05\n    assert 'actual_RL_rollout'in s")
write(path,s)
path=N/'normal429/collect429_fullclose_transfer_once.py';s=path.read_text('utf8').replace('20419+u','25556+u');write(path,s)

task=read(O/'TASK416_FROZEN.json')
nonce=str(time.time_ns());job='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_BOUNDED_ACTUAL_PPO429_'+nonce
task.update(kind='ACTUAL_ONPOLICY_RESIDUAL_PPO_400N50_V429',run_id='ACTUAL_RESIDUAL_PPO429_'+nonce,
 job_root=job+'/tracker72',owner_root=job+'/owner72',source_SHA=finalcpu['SHA'],model_SHA=finalcpu['SHA'],
 source_parent_SHA=task['source_SHA'],source_bytes=finalcpu['bytes'],model_bytes=finalcpu['bytes'],
 model_path=read(O/'reports/ROOT416_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')['roles']['jump_72']['formal']['path'],
 worker_SHA=H(N/'source/worker429.py'),source_WM_updates=25556,window_start_world_updates=25556,
 source_actor_Adam_step=56304,new_tracking_critic_Adam_step=13364,source_Adam_step=56304,
 source_CPU_report_SHA=H(C/'reports/CPU428_ACTUAL_SAVED_ROLLOUT_TRUST_STEP_ADMISSION.json'),
 carrier_CPU_receipt_SHA=H(O/'reports/ROOT416_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json'),
 CPU429_SHA=H(N/'reports/CPU429_REUSED428_TRUST_ADMISSION.json'),
 human_authorization='RLup270 and proactive targetedrepair afteractual416all80earlyorientationfail',
 resume_scope='Fullfinal416actorcriticSTDallAdamEMAoriginWM25556; freshactualPPOphysicalDRrollout; savedCUDAresidualRNGrestored',
 policy_rollback='none; restoreexactfinal416allstate',source_cpu_reuse='ExactCPU428learnerbytes; no newsourcePTread',
 predecessor_actual='423actual0strict/80orientation/mean.812s; nativeviewed;427/428CPUpostAdamtrust bound candidatepasses',
 actor_objective='SameactualonpolicyPPO/GAE32controls,postAdammeanKL<=.01/maxresidualdelta<=.05; rejectedsameproposalweightsandAdamrestored; onecommittedstep',
 actor_trust=dict(KL_limit=.01,max_action_delta=.05,max_backtracks=12),
 generation='FROZEN_BEFORE_GO_ACTUAL_PPO429',actual_learning_GO_pending=True)
put(N/'TASK429_FROZEN.json',task)

# Copy independenteval423mechanics with newnamespace andpendingfinal429identity.
for path in sorted((OE/'source').rglob('*')):
 if not path.is_file()or'__pycache__'in path.parts:continue
 dest=E/'source'/path.relative_to(OE/'source');dest.parent.mkdir(parents=True,exist_ok=True)
 if path.name=='evaluate423.py':continue
 dest.write_bytes(path.read_bytes())
for name in('feedforward389.json','reference389.npz'):shutil.copyfile(N/name,E/name)
def evalrename(s):
 s=s.replace(str(OE),str(E)).replace(OE.as_posix(),E.as_posix());return token(s,423,430)
for old,new in(('contract423.py','contract430.py'),('target423_parent.py','target430_parent.py'),('run423_eval_once.py','run430_eval_once.py'),('view423_actual_RL_replay.py','view430_actual_RL_replay.py'),('render423_recorded_frames.py','render430_recorded_frames.py'),('source/evaluate423.py','source/evaluate430.py')):
 s=evalrename((OE/old).read_text('utf8'))
 s=s.replace('ACTUAL_RESIDUAL_PPO416_COMPLETE','ACTUAL_RESIDUAL_PPO429_COMPLETE').replace('learned_actual_residual_PPO416','learned_actual_residual_PPO429')
 s=s.replace('FROZEN416_ACTUAL_RESIDUAL_PPO_EVAL430','FROZEN429_ACTUAL_RESIDUAL_PPO_EVAL430')
 s=s.replace('RL416','RL429').replace('PPO416','PPO429').replace('RECORDED423_NATIVE_FRAMES','RECORDED430_NATIVE_FRAMES')
 write(E/new,s)
etask=read(OE/'TASK423_FROZEN.json')
etask.update(kind='FROZEN429_ACTUAL_RESIDUAL_PPO_EVAL430',source_run='PENDING429ACTUALFINAL',
 expected_Pi_updates=1,model_SHA=task['model_SHA'],model_bytes=task['model_bytes'],model_path=task['model_path'],
 worker_SHA=H(E/'source/evaluate430.py'),pending_actual_final_identity=True,
 distinct_evaluation_purpose='Immediately evaluate finalboundedactualPPO429afterfullsave/safeclose,80firstepisodesseed9137same270/newDR',
 human_request='ActualRL429actoronly+origin+fixedtable;noonlineMPC')
put(E/'TASK430_PENDING_FINAL_IDENTITY.json',etask)
for name in('bind417_actual_FIRST_and_launch_once.py','postround417_close_actual416_eval_once.py'):
 s=rename((OQ/name).read_text('utf8'))
 s=s.replace("'RL429_FINAL_INDEPENDENT_EVAL_V430_20261102'", "'RL429_FINAL_INDEPENDENT_EVAL_V430_20261102'")
 # Fix index self-reference in the newversion by explicitly excluding indexpath.
 s=s.replace("if path.is_file()and'__pycache__'not in path.parts]", "if path.is_file()and path!=index and'__pycache__'not in path.parts]")
 write(Q/rename(name),s)

for path in list(N.rglob('*.py'))+list(Q.rglob('*.py'))+list(E.rglob('*.py')):ast.parse(path.read_bytes())
assert H(N/'source/actual_transition_learner427.py')==cpu['learnerSHA']
spec=importlib.util.spec_from_file_location('static429',N/'teacher_task429.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.validate_task(task)
for root in(N,E):
 assert H(root/'feedforward389.json')==task['fixed_command_feedforward']['SHA']
 assert H(root/'reference389.npz')==task['reference']['SHA']
normal=N/'normal429'
put(normal/'INDEX429_NORMAL_SOURCE_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in(normal/'normal429_common.py',normal/'collect429_fullclose_transfer_once.py',N/'teacher_task429.py')]))
files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in sorted(N.rglob('*'))if p.is_file()and'__pycache__'not in p.parts]
put(N/'INDEX429_SOURCE_TASK_CALLERS_FROZEN.json',dict(epoch=time.time(),files=files))
files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for root in(Q,E)for p in sorted(root.rglob('*'))if p.is_file()and'__pycache__'not in p.parts]
put(Q/'INDEX430_POSTROUND_FOR429_FROZEN.json',dict(epoch=time.time(),files=files))
put(P/'reports/STATIC429_BOUNDED_ACTUALPPO_FULL_PACKAGE_ADMISSION.json',dict(epoch=time.time(),passed=True,
 root=str(N),run=task['run_id'],indexSHA=H(N/'INDEX429_SOURCE_TASK_CALLERS_FROZEN.json'),workerSHA=task['worker_SHA'],
 learnerSHA=cpu['learnerSHA'],CPU428_exactbytes=True,source_offsets=[56304,13364,25556],
 postroot=str(Q),postindexSHA=H(Q/'INDEX430_POSTROUND_FOR429_FROZEN.json'),evalroot=str(E),
 indexselfexclusionfixed=True,allAST=True,no_new_source_modelread=True,SDK=0,network=0,START=False))
print(json.dumps(dict(passed=True,root=str(N),run=task['run_id'],indexSHA=H(N/'INDEX429_SOURCE_TASK_CALLERS_FROZEN.json'),postindexSHA=H(Q/'INDEX430_POSTROUND_FOR429_FROZEN.json'))))
