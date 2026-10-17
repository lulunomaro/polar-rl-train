"""New explicit H1 loss candidate, exact old physical source, no GPU or model update."""
from pathlib import Path
import sys,os,json,time,hashlib,shutil,ast,traceback,copy
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
from h1_action_mean_overflow_loss_v1 import mean_overflow_loss
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;X=W/'MOD4_H1_FROZEN_FE1709_REVIEW_20261018';Z=W/'MOD4_POWER_RESTORED_THREE_HOST_READONLY_CHECK_20261018';Q=B/'payload_h1_native';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();old=X/'paid_d723_v4/payload/h1';assert not Q.exists()
 proof=json.loads((X/'paid_d723_v4/reports/PARALLEL_D723_H1_COMPLETE_FINAL_FULL_CPU_COST_EXIT_ACTUAL.json').read_bytes());assert proof['passed_whole_final_model_local_CPU'] and proof['all17Adam_after']==645620 and proof['actual_original_owner_node_all_children_out']
 mu=torch.tensor([[-100.,-6.,-2.,0.,6.,9.],[2.,3.,-4.,5.,-6.,0.]],requires_grad=True);before=mu.detach().clone();loss=mean_overflow_loss(mu);loss.backward();assert torch.equal(mu.detach(),before) and mu.grad[0,0]<0 and mu.grad[0,5]>0 and torch.equal(mu.grad[0,1:5],torch.zeros(4)) and not mu.grad[1].any()
 zero=mean_overflow_loss(mu,coefficient=0.);assert zero==0;interior=torch.tensor([[-6.,-3.,0.,2.,4.,6.]],requires_grad=True);inside=mean_overflow_loss(interior);inside.backward();assert inside==0 and not interior.grad.any()
 negatives=[]
 for label,args in [('wrong_width',(torch.zeros(4,5),)),('wrong_rank',(torch.zeros(6),)),('empty',(torch.zeros(0,6),)),('nonfinite',(torch.full((1,6),float('nan')),)),('integer',(torch.zeros(1,6,dtype=torch.long),)),('negative_coefficient',(mu,-.001)),('large_coefficient',(mu,.01)),('nonfinite_coefficient',(mu,float('inf'))),('changed_bound',(mu,.001,7.))]:
  try:mean_overflow_loss(*args)
  except ValueError:negatives.append(label)
  else:raise AssertionError(label)
 sourcePPO=Z/'actual_installed_RSL72_sources/rsl_rl/algorithms/ppo.py';assert H(sourcePPO)=='a2d35e7ad7b884c80b7434e7d2ce785a6da1e18d93c96f1179fbd3a208669f8c';base=sourcePPO.read_text('utf8');marker='            loss = surrogate_loss + self.value_loss_coef * value_loss - self.entropy_coef * entropy.mean()';assert base.count(marker)==1
 addition="\n            owned_overflow = mean_overflow_loss(distribution_params[0])\n            loss = loss + owned_overflow\n            self.owned_mean_overflow_last = dict(loss=float(owned_overflow.detach()),mean0_min=float(distribution_params[0][:,0].detach().min()),mean0_max=float(distribution_params[0][:,0].detach().max()),fraction_outside_clip6=float((distribution_params[0].detach().abs()>6.).float().mean()))"
 owned=base.replace('from __future__ import annotations','from __future__ import annotations\nfrom h1_action_mean_overflow_loss_v1 import mean_overflow_loss',1).replace(marker,marker+addition)
 assert owned.replace('\nfrom h1_action_mean_overflow_loss_v1 import mean_overflow_loss','',1).replace(addition,'',1)==base;ast.parse(owned)
 shutil.copytree(old,Q,ignore=shutil.ignore_patterns('__pycache__','THREE_SLOT_COMPLETE_MANIFEST_V1.json'));oldm=json.loads((old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());shutil.copy2(old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',Q/'PREVIOUS_D723_PAID_MANIFEST_HISTORICAL.json')
 src=Q/'job0/source/H1_final10_protected.pt';shutil.copy2(proof['complete_final']['local_path'],src);assert H(src)==proof['complete_final']['SHA']=='b32656cf3bfec37cef4ccfcbe06b6ce421054194f8ad627425e367d67240ccce'
 ck=torch.load(src,map_location='cpu',weights_only=False);assert {int(x['step']) for x in ck['optimizer_state_dict']['state'].values()}=={645620} and ck['owned_H1_completed_updates']==24
 edits=[]
 for name in ('h1_prelaunch_v2_production_worker_v1.py','review_H1_prelaunch_v2_native_allrows_CPU_v1.py'):
  p=Q/name;s=p.read_text('utf8');assert '645140' in s;s=s.replace('645140','645620');p.write_text(s,encoding='utf8');edits.append(name)
 prod=Q/'h1_prelaunch_v2_production_worker_v1.py';s=prod.read_text('utf8');needle='original_log(*aa,**kk);completed+=1;from own_H1_storage_finite_guard_v1 import should_save_stop';assert s.count(needle)==1;s=s.replace(needle,"original_log(*aa,**kk);completed+=1;put(out/'OWNED_MEAN_OVERFLOW_LOSS_CURRENT.json',dict(epoch=time.time(),completed=completed,candidate='mean_overflow_loss_coefficient.001_clip6',last_batch=getattr(runner.alg,'owned_mean_overflow_last',None),environment_reward_STD_LR_and_physics_unchanged=True));from own_H1_storage_finite_guard_v1 import should_save_stop");prod.write_text(s,encoding='utf8')
 runtime=Q/'job0/runtime/isaac/mod4';(runtime/'owned_h1_mean_overflow_ppo_v1.py').write_text(owned,encoding='utf8');shutil.copy2(B/'h1_action_mean_overflow_loss_v1.py',runtime/'h1_action_mean_overflow_loss_v1.py')
 entry=runtime/'train_H1_ground_prelaunch_fullstate_v2.py';s=entry.read_text('utf8');line='    runner = OnPolicyRunner(vec_env, cfg.to_dict(), log_dir=log_dir, device=cfg.device)';assert s.count(line)==1;s=s.replace(line,"    owned_cfg = cfg.to_dict()\n    owned_cfg['algorithm']['class_name'] = 'owned_h1_mean_overflow_ppo_v1:PPO'\n    runner = OnPolicyRunner(vec_env, owned_cfg, log_dir=log_dir, device=cfg.device)");entry.write_text(s,encoding='utf8')
 parent=X/'H1_closed_target72_native_only_parent_v1.py';shutil.copy2(parent,Q/parent.name);shutil.copy2(parent,B/parent.name)
 taskp=Q/'job0/TASK.json';task=json.loads(taskp.read_bytes());task.update(id='H1_B326_MEAN_OVERFLOW_REPAIR_NATIVE180_20261018',source_SHA=H(src),source_Adamstep=645620,source_owned_completed_updates=24,exact_closed_source_owned_updates=24,execution_backend='target72',GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842',native_only_no_production_GO_or_canonical=True,newsource_native180_required=True,optimization_candidate=dict(name='mean_overflow_regularizer',coefficient=.001,original_action_bound=6.,not_environment_reward_change=True,no_STD_reset=True,no_actor_parameter_reset_or_extra_optimizer=True))
 taskp.write_text(json.dumps(task,indent=2),encoding='utf8');files=[]
 for p in sorted(x for x in Q.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.py':ast.parse(p.read_text('utf8'))
  files.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
 allowed='job0/runtime/isaac/mod4/train_H1_ground_prelaunch_fullstate_v2.py';immutable=[x for x in oldm['files'] if (x['relative'].startswith(('lib/','job0/runtime/','job0/assets/')) or x['relative']=='job0/original_run_manifest.json') and x['relative']!=allowed];assert all(H(Q/x['relative'])==x['SHA'] for x in immutable)
 mf=dict(oldm,source_SHA=H(src),source_Adamstep=645620,files=files,owned_optimization_candidate=task['optimization_candidate'],actual_installed_base_PPO_SHA=H(sourcePPO),native_only_no_PPO_or_canonical_permission=True);(Q/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(mf,indent=2),encoding='utf8')
 spec=json.loads((X/'reports/CLOSED_H1_NEW_SOURCE_TARGET72_NATIVE_ONLY_PAYLOAD_AND_PARENT_CPU_PREPARED_ACTUAL.json').read_bytes())['spec'];spec.update(source_SHA=H(src),source_Adamstep=645620,manifest_SHA=H(Q/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),previous_runtime_root='/home/lc01/Zonglin Li/zonglin2/tasks/H1r_1810v4',role='native_only')
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 save('B326_MEAN_OVERFLOW_NATIVE_PAYLOAD_CPU_PREPARED_ACTUAL.json',dict(epoch=time.time(),passed_CPU_static_source_and_actual_mock_parent_flow=True,spec=spec,source_closed_final=proof,source_STD_initial_final_literalexact=ck['actor_state_dict']['distribution.std_param'].tolist(),actual_gradient_toward_clip_domain=True,zero_inside_clip_and_zero_coefficient_identity=True,actual_loss_fixture=loss.item(),negative_cases=negatives,PPO_base_source_SHA=H(sourcePPO),owned_PPO_SHA=H(runtime/'owned_h1_mean_overflow_ppo_v1.py'),base_PPO_exact_after_removing_only_declared_auxiliary_loss=True,environment_physics_reward_commands_DR_hardware_bytes_exact=True,native_parent_byteexact_reuse_from_previously_tested_native_only_parent=True,new_optimization_objective_not_an_environment_reward_or_clipping_change=True,CPU_RNG_unchanged0CUDA0optimizer=True,no_GPU_or_new_learning_grant_yet=True))
 print(json.dumps(dict(payload_CPU=True,source_Adam645620=True,loss_candidate_explicit=True,negative_cases=len(negatives),own_native180_required=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:save('MEAN_OVERFLOW_PAYLOAD_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_source_mutation=True));raise
