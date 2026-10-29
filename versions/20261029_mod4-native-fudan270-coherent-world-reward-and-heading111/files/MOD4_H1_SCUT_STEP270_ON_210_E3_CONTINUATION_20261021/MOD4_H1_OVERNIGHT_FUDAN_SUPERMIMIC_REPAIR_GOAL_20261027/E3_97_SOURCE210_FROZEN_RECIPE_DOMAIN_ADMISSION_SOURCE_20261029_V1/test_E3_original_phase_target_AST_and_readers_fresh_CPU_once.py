"""Fresh CPU tensors/source AST only: no saved model/raw/NPZ/SDK/remote."""
from pathlib import Path
import ast,hashlib,importlib.metadata as md,importlib.util,json,sys,traceback
import torch
from tensordict import TensorDict
B=Path(__file__).resolve().parent;L=B.parent;checks=[]
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def ok(n,v):assert bool(v),n;checks.append(n)
def rejected(n,f):
 try:f()
 except (AssertionError,TypeError):checks.append(n);return
 raise AssertionError('Negative accepted: '+n)
def main():
 torch.set_num_threads(2);assert not torch.cuda.is_initialized()
 cat=load('e3_original_recipe_phase_catalog_v1',B/'e3_original_recipe_phase_catalog_v1.py');snap=load('lossless_snapshot_pinned75d683',B/'lossless_snapshot_pinned75d683.py');tele=load('e3_recipe_domain_telemetry_v1',B/'e3_recipe_domain_telemetry_v1.py');guard=load('e3_frozen_worker_call_guard_v1',B/'e3_frozen_worker_call_guard_v1.py')
 worker=ast.parse((B/'evaluate_E3_adapted97_source210_frozen600_once_v1.py').read_bytes());cpu=ast.parse((B/'E3_source210_target_source_SDK_metadata_admission_v1.py').read_bytes());fn=next(n for n in cpu.body if isinstance(n,ast.FunctionDef) and n.name=='main');section=[n for n in fn.body if isinstance(n,ast.ImportFrom) and n.module=='e3_frozen_worker_call_guard_v1' or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='guard' for t in n.targets)];assert len(section)==2;scope=dict(tree=worker);exec(compile(ast.Module(body=section,type_ignores=[]),'<actual E3 target CPU guard statements>','exec'),scope);ok('actual E3 target CPU AST guard accepts selected worker',scope['guard']['passed'])
 for source in ('runner.alg.update()','optimizer.step()','actor.train()','loss.backward()','env.update(x=1)','os.environ.update(other)','vec.step(other)'):
  trial=ast.parse((B/'evaluate_E3_adapted97_source210_frozen600_once_v1.py').read_bytes());trial.body.extend(ast.parse(source).body);rejected('guard rejects '+source,lambda tr=trial:guard.validate_frozen_worker_calls(tr))
 source=L/'E3_PPO50_gas400_source_preparation_20261028/runtime_candidate_v1/isaac/mod4/e3_public_recovery_phase_v1.py';tree=ast.parse(source.read_bytes());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='RecoveryPhase');scope=dict(torch=torch);exec(compile(ast.Module(body=[cls],type_ignores=[]),'<original E3 RecoveryPhase CPU synthetic>','exec'),scope);phase=scope['RecoveryPhase'](13,'cpu');book=tele.E3Book(torch,13,'cpu',['timeout']);episode=torch.zeros(13,dtype=torch.long);zeros=torch.zeros(13,dtype=torch.bool)
 for i in range(151):
  c=dict(key=cat.profile_key(torch,phase.recipe,phase.age),phase=0 if i<100 else 1,episode=episode.clone(),recipe=phase.recipe.clone(),age=phase.age.clone(),request=cat.upcoming_request(torch,phase.recipe,phase.age),credited=phase.credited.clone(),peak=phase.peak.clone())
  phase.begin();phase.update(-torch.ones(13),torch.zeros(13),torch.zeros(13));after=dict(episode=episode.clone(),recipe=phase.recipe.clone(),age=phase.age.clone(),request=phase.request.clone(),credited=phase.credited.clone(),peak=phase.peak.clone(),stable=phase.stable.clone(),errors=[torch.zeros(13) for _ in range(6)]);book.observe(c,after,zeros,zeros,[zeros],[zeros,zeros])
  if i==0:ok('positive peak reward alone is not original recovery credit',int(book.credits.sum())==0 and int((phase.delta>0).sum())==12)
  if i==23:ok('24 controls insufficient for original .5s stable credit',int(book.credits.sum())==0)
  if i==24:ok('25controls stable counter50 gives twelve original credits',int(book.credits.sum())==12 and not bool(phase.credited[12]))
 ok('original request ends age300 at next begin, age increments2',phase.age.tolist()==[302]*13 and not bool(phase.request.any()))
 rows=book.summary();req=next(x for x in rows if x['phase']=='whole' and x['profile']==0);post=next(x for x in rows if x['phase']=='whole' and x['profile']==1);baseline=next(x for x in rows if x['phase']=='whole' and x['profile']==24)
 ok('request and post exposure exact150 plus1',req['population_controls']==150 and post['population_controls']==1)
 ok('baseline recipe12 separate151controls zero recoverycredit',baseline['population_controls']==151 and baseline['original_new_recovery_credit_events']==0)
 ok('uniqueenv not sum of events/controls',req['unique_exposed_env']==1 and req['original_new_recovery_credit_events']==1)
 ok('whole attempt exposure deduplicates warmup/steady',req['attempt_profile_exposures']==1)
 phase.reset(torch.tensor([0]));episode[0]+=1;c=dict(key=cat.profile_key(torch,phase.recipe,phase.age),phase=1,episode=episode.clone(),recipe=phase.recipe.clone(),age=phase.age.clone(),request=cat.upcoming_request(torch,phase.recipe,phase.age),credited=phase.credited.clone(),peak=phase.peak.clone());phase.begin();phase.update(-torch.ones(13),torch.zeros(13),torch.zeros(13));after=dict(episode=episode.clone(),recipe=phase.recipe.clone(),age=phase.age.clone(),request=phase.request.clone(),credited=phase.credited.clone(),peak=phase.peak.clone(),stable=phase.stable.clone(),errors=[torch.zeros(13) for _ in range(6)]);book.observe(c,after,zeros,zeros,[zeros],[zeros,zeros]);req=next(x for x in book.summary() if x['phase']=='whole' and x['profile']==0);ok('new reset attempt has new denominator without fake credit',req['attempt_profile_exposures']==2 and req['original_new_recovery_credit_events']==1)
 rejected('credit cannot cross reset UID',lambda:cat.new_original_credit(torch,torch.tensor([False]),torch.tensor([True]),torch.tensor([1]),torch.tensor([2])))
 fresh=TensorDict({'policy':torch.arange(6).reshape(3,2)},batch_size=[3]);value=snap.LosslessSnapshot(torch,3,torch.tensor([0,2]))._snapshot(fresh);ok('actual local TensorDict selection preserved',value['entries']['policy']['value']==[[0,1],[4,5]])
 w=load('E3_fresh_worker_guard_only',B/'evaluate_E3_adapted97_source210_frozen600_once_v1.py');task=dict(kind='MOD4_E3_ADAPTED97_SOURCE210_FROZEN_RECIPE_DOMAIN_V1',source_SHA=w.MODEL_SHA,num_envs=20000,controls=600,warmup_controls=100,maximum_worker_seconds=1680,no_optimizer_steps=True,actual_source210_SDK_admission_passed=True,actual_private_GPU_EX_held_by_parent=True,canonical72_known_owner_readonly_passed=True,domain_kind='E3_PUBLIC_RECOVERY',original_Adam=866060,original_LR=.0002562890625000001);w.guard(task);checks.append('E3 exact declared Task positive')
 for key,v in [('domain_kind','E2_WORLD_MOVING_SIGNED4'),('original_Adam',864320),('original_LR',.00022500000000000002),('controls',900)]:rejected('Task rejects '+key,lambda k=key,x=v:w.guard(dict(task,**{k:x})))
 codetree=ast.parse((B/'E3_source210_actual_receipts_readonly_CODE_v1.py').read_bytes());code=next(ast.literal_eval(n.value) for n in codetree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CODE' for t in n.targets));rt=ast.parse(code);fs=[n for n in rt.body if isinstance(n,ast.FunctionDef) and n.name in ('native_valid','full_coverage')];scope=dict(MODEL=w.MODEL_SHA);exec(compile(ast.Module(body=fs,type_ignores=[]),'<E3 readonly pure metadata>','exec'),scope)
 rr=dict(passed=True,source_SHA=w.MODEL_SHA,Adam_step=866060,stored_RSL_iteration=43090,actual_constructor_algorithm_optimizer_LR=.0002562890625000001);nn=dict(passed=True,source_SHA=w.MODEL_SHA,controls=24,physics_callbacks=192,feedback_samples=48,legs_queue_apply=192,wheels_queue_apply=192,trace_controls=list(range(1,25)),RewardManager_calls=24,RewardManager_dt_s=.02,original_Adam866060_unchanged=True);ok('actual first receipt predicates positive only metadata fixture',scope['native_valid'](rr,nn));ok('native missing192 group cannot pass',not scope['native_valid'](rr,dict(nn,wheels_queue_apply=191)))
 result=dict(controls=600,requested_controls=600,warmup_controls=100,steady_controls=500,wall_time_limited=False,all17_Adam_steps=866060,actual_LR_unchanged=.0002562890625000001,core_actor_critic_STD_norm_optimizer_literal_unchanged=True);ok('full600/100/500 receipt predicate positive',scope['full_coverage'](True,result));ok('partial is not full600',not scope['full_coverage'](True,dict(result,controls=599)))
 parsed=[]
 for p in B.glob('*.py'):ast.parse(p.read_bytes());parsed.append(p.name)
 ok('target metadata has no PT decode','torch.load(' not in (B/'E3_source210_target_source_SDK_metadata_admission_v1.py').read_text());ok('fresh CPU leaves CUDA uninitialized',not torch.cuda.is_initialized())
 with (B/'reports/E3_SOURCE210_FRESH_ORIGINAL_PHASE_CPU_TARGET_AST_AND_READERS_ACTUAL.json').open('x') as f:json.dump(dict(passed=True,checks=checks,count=len(checks),parsed=parsed,local_torch=torch.__version__,local_tensordict=md.version('tensordict'),target_expected_tensordict='0.14.1',local_test_not_target_API_proof=True,no_PT_raw_NPZ_savedmodel_SDK_remote_GPU_call=True),f,indent=2)
 print(json.dumps(dict(passed=True,checks=len(checks),source_only=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/'reports/E3_FRESH_CPU_SOURCE_ORIGINAL_ERROR_'+str(__import__('time').time_ns())+'.json').open('x') as f:json.dump(dict(traceback=traceback.format_exc(),source_only=True,no_model_remote=True),f,indent=2)
  raise
