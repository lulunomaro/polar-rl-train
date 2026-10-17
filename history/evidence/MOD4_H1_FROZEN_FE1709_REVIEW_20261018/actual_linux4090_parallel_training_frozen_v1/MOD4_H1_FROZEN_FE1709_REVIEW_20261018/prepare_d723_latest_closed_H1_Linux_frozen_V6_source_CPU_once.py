"""Freeze the actually newer closed d723 source; no new learning or changed recipe."""
from pathlib import Path
import os,sys,time,json,hashlib,ast,shutil,copy,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(__file__).resolve().parent;R=B/'reports';Q=B/'h1_d723_linux4090_v6/payload';OLD=B/'h1_fe1709_linux4090_v5/payload';SHA='d7238b885879705fa8312758337bf0b6ca1d97c2f906df51b72c27b475e7786a';FE='fe1709ec470aa4995e0b271947b65135d2e0bd43bec26b28316a451c5f1fa49e';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 torch.set_num_threads(2);assert not Q.exists();rng=torch.get_rng_state().clone();shutil.copytree(OLD,Q,ignore=shutil.ignore_patterns('__pycache__','H1_fe1709_closed24.pt'))
 source=B.parent/'MOD4_H1_HUMAN_REQUESTED_SAME_SCOPE_RESTART_20261017/actual_closed_H1_final/model_update24.pt';assert H(source)==SHA;shutil.copy2(source,Q/'source/H1_d723_closed24.pt')
 changes=[]
 for name in ('h1_closed24_source_guard_v1.py','h1_closed24_single35_public04_v1.py','h1_linux_eval_contract_v1.py','h1_linux4090_frozen_worker_v1.py'):
  p=Q/name;s=p.read_text('utf8').replace(FE,SHA).replace('644660','645140').replace('H1_FE1709_LINUX4090_V5_20261018','H1_D723_LINUX4090_V6_20261018').replace('H1_FE1709_LINUX4090_MANIFEST_V5.json','H1_D723_LINUX4090_MANIFEST_V6.json');ast.parse(s);p.write_text(s,encoding='utf8');changes.append(dict(relative=name,old_SHA=H(OLD/name),new_SHA=H(p)))
 sys.path[:0]=[str(Q),str(Q/'frozen_shared/runtime/isaac/mod4')]
 from h1_closed24_source_guard_v1 import validate_H1_source
 ck=torch.load(source,map_location='cpu',weights_only=False);assert validate_H1_source(ck);negative=[]
 for label,mut in [('wrong_phase',lambda c:c.__setitem__('owned_H1_phase','native')),('wrong_updates',lambda c:c.__setitem__('owned_H1_completed_updates',23)),('wrong_Adam',lambda c:next(iter(c['optimizer_state_dict']['state'].values()))['step'].fill_(644660)),('wrong_kind',lambda c:c['owned_H1_learning_task'].__setitem__('kind','E2')),('wrong_shape',lambda c:c['actor_state_dict'].__setitem__('mlp.0.weight',torch.zeros(256,34))),('bad_STD',lambda c:c['actor_state_dict']['distribution.std_param'].fill_(-1)),('nonfinite_critic',lambda c:c['critic_state_dict']['mlp.0.weight'].fill_(float('nan'))),('wrong_phase_dtype',lambda c:c['H1_public_request_phase_state']['phase']['tensors'].__setitem__('age_control',c['H1_public_request_phase_state']['phase']['tensors']['age_control'].float())),('failed_prefix',lambda c:c.__setitem__('failed_partial_prefix',True))]:
  bad=copy.deepcopy(ck);mut(bad)
  try:validate_H1_source(bad)
  except AssertionError:negative.append(label)
  else:raise AssertionError(label)
 from h1_closed24_single35_public04_v1 import Single35
 controller=Single35(Q/'source/H1_d723_closed24.pt',8,'cpu');obs=torch.zeros(8,35);obs[:,28]=1.;mode=torch.zeros(8,dtype=torch.long)
 for tick in range(2):
  p=controller.begin(tick,lambda:obs,mode);controller.finish(p['clipped_action'],torch.zeros(8,dtype=torch.bool));obs[:,22:28]=p['clipped_action']
 assert controller.exact() and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 m=json.loads((OLD/'H1_FE1709_LINUX4090_MANIFEST_V5.json').read_bytes());m.update(version=6,source=dict(path=str(Q/'source/H1_d723_closed24.pt'),bytes=source.stat().st_size,SHA=SHA),source_relative='source/H1_d723_closed24.pt',latest_closed_d723_not_fe1709=True,original_recipe_and_runtime_physics_reward_command_exact=True);m['recipe']=dict(m['recipe'],source_SHA=SHA,source_Adam645140=True);m['recipe'].pop('source_Adam644660',None);m['recipe'].pop('not_latest_d723_weights',None)
 m['files']=[dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(Q.rglob('*')) if p.is_file() and '__pycache__' not in p.parts];m['package_files_v8']=[dict(relative=x['relative'],bytes=x['bytes'],sha256=x['SHA']) for x in m['files']];(Q/'H1_D723_LINUX4090_MANIFEST_V6.json').write_text(json.dumps(m,indent=2),encoding='utf8')
 put('H1_D723_LINUX4090_V6_COMPLETE_SOURCE_FROZEN_CPU_PREPARED_ACTUAL.json',dict(epoch=time.time(),passed_full_source_guard_CPU_and9negative=True,source=m['source'],source_Adam645140=True,negative_cases=negative,changes=changes,original_physical_reward_phase_command_and_observer_bytes_exact=True,controller_two_ticks_actor9STD_exact_RNG_unchanged0CUDA0optimizer=True,fresh80_same_recipe_own_unused_native120_required=True,no_target_GPU_yet=True))
 print(json.dumps(dict(d723_frozen_V6_CPU=True,negative_cases=len(negative),files=len(m['files']))),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('H1_D723_FROZEN_V6_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_remote=True));raise
