"""Prepare the actually collected new immutable first source for independent LinuxGPU1 evaluation."""
from pathlib import Path
import os,sys,json,time,hashlib,shutil,zipfile,ast,copy,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(__file__).resolve().parent;R=B/'reports';X=B.parent/'MOD4_H1_FROZEN_FE1709_REVIEW_20261018';E=B/'frozen_public4_normal1_linux_v1';Q=E/'payload';OLD=X/'h1_b326_linux4090_v7/payload';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();proof=json.loads((B/'paid_mean_public4_v2/reports/PUBLIC4_V2_H1_IMMUTABLE_FIRST_COMPLETE_LOCAL_CPU_V3_ACTUAL.json').read_bytes());assert proof['passed_real_immutable_first_complete_local_CPU'];row=next(x for x in proof['all_models'] if x['kind']=='immutable_first');source=Path(row['local_path']);assert row['twohost_complete_SHA'] and H(source)==row['SHA'];assert not E.exists()
 shutil.copytree(OLD,Q,ignore=shutil.ignore_patterns('__pycache__','*.pt'));dest=Q/'source/H1_public4_normal_only_update1.pt';dest.parent.mkdir(exist_ok=True);shutil.copy2(source,dest)
 oldSHA='b32656cf3bfec37cef4ccfcbe06b6ce421054194f8ad627425e367d67240ccce';guard=(OLD/'h1_closed24_source_guard_v1.py').read_text('utf8').replace(oldSHA,row['SHA']).replace('645620','645640').replace("ck['owned_H1_completed_updates']==24","ck['owned_H1_completed_updates']==1").replace('Exact latest H1 closed24/Adam645640 source','Exact H1 mean-repair immutable first1/Adam645640 source')
 guard=guard.replace(" task=ck['owned_H1_learning_task']"," task=ck['owned_H1_learning_task']\n assert task['optimization_candidate']['name']=='public4_only_mean_overflow_regularizer_v2' and task['optimization_candidate']['coefficient']==.001")
 (Q/'h1_public4_normal_update1_source_guard_v1.py').write_text(guard,encoding='utf8')
 for name in ('h1_closed24_single35_public04_v1.py','h1_frozen_witness_v1.py'):
  p=Q/name;p.write_text(p.read_text('utf8').replace('h1_closed24_source_guard_v1','h1_public4_normal_update1_source_guard_v1'),encoding='utf8')
 for name in ('h1_linux_eval_contract_v1.py','h1_linux4090_frozen_worker_v1.py','h1_linux4090_frozen_parent_v1.py'):
  p=Q/name;s=p.read_text('utf8').replace(oldSHA,row['SHA']).replace('H1_B326_LINUX4090_V7_20261018','H1_PUBLIC4_NORMAL1_LINUX4090_V1_20261018').replace('H1_B326_LINUX4090_MANIFEST_V7.json','H1_PUBLIC4_NORMAL1_LINUX4090_MANIFEST_V1.json').replace('h1_closed24_source_guard_v1','h1_public4_normal_update1_source_guard_v1');p.write_text(s,encoding='utf8')
 sys.path[:0]=[str(Q),str(Q/'frozen_shared/runtime/isaac/mod4')];from h1_public4_normal_update1_source_guard_v1 import validate_H1_source;from h1_closed24_single35_public04_v1 import Single35
 ck=torch.load(source,map_location='cpu',weights_only=False);assert validate_H1_source(ck);badlabels=[]
 for label,mut in [('phase',lambda c:c.__setitem__('owned_H1_phase','native')),('updates',lambda c:c.__setitem__('owned_H1_completed_updates',0)),('Adam',lambda c:next(iter(c['optimizer_state_dict']['state'].values()))['step'].fill_(645620)),('kind',lambda c:c['owned_H1_learning_task'].__setitem__('kind','E2')),('shape',lambda c:c['actor_state_dict'].__setitem__('mlp.0.weight',torch.zeros(256,34))),('STD',lambda c:c['actor_state_dict']['distribution.std_param'].fill_(-1)),('nonfinite',lambda c:c['critic_state_dict']['mlp.0.weight'].fill_(float('nan'))),('failed_prefix',lambda c:c.__setitem__('failed_partial_prefix',True)),('wrong_candidate',lambda c:c['owned_H1_learning_task']['optimization_candidate'].__setitem__('coefficient',0.))]:
  wrong=copy.deepcopy(ck);mut(wrong)
  try:validate_H1_source(wrong)
  except AssertionError:badlabels.append(label)
  else:raise AssertionError(label)
 actor=Single35(dest,8,'cpu');obs=torch.zeros(8,35);obs[:,28]=1;mode=torch.zeros(8,dtype=torch.long)
 for i in range(2):
  tick=actor.begin(i,lambda:obs,mode);actor.finish(tick['clipped_action'],torch.zeros(8,dtype=torch.bool));obs[:,22:28]=tick['clipped_action']
 assert actor.exact() and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 manifest=json.loads((OLD/'H1_B326_LINUX4090_MANIFEST_V7.json').read_bytes());manifest.update(version=1,source=dict(path=str(dest),bytes=dest.stat().st_size,SHA=row['SHA']),source_relative='source/H1_public4_normal_only_update1.pt',source_is_immutable_first1_not_closed24_or_future_final=True,actual_source_Adam645640=True,target_backend='Linux72_GPU1',namespace='H1_PUBLIC4_NORMAL1_LINUX4090_V1_20261018');manifest['recipe']=dict(manifest['recipe'],source_SHA=row['SHA'],source_Adam645640=True);manifest['recipe'].pop('source_Adam645620',None)
 manifest['files']=[dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(Q.rglob('*')) if p.is_file() and '__pycache__' not in p.parts];manifest['package_files_v8']=[dict(relative=x['relative'],bytes=x['bytes'],sha256=x['SHA']) for x in manifest['files']];mf=Q/'H1_PUBLIC4_NORMAL1_LINUX4090_MANIFEST_V1.json';mf.write_text(json.dumps(manifest,indent=2),encoding='utf8');bundle=E/'H1_PUBLIC4_NORMAL1_LINUX_FROZEN_PAYLOAD_V1.zip'
 with zipfile.ZipFile(bundle,'x',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
  for row in manifest['files']:z.write(Q/row['relative'],row['relative'])
  z.write(mf,mf.name)
 out=dict(epoch=time.time(),passed_complete_payload_CPU_only=True,source=manifest['source'],source_immutable_first1_Adam645640=True,first_control24_normal_only_aux0_not_public4_loss_effectiveness_test=True,negative_cases=badlabels,manifest=dict(path=str(mf),bytes=mf.stat().st_size,SHA=H(mf)),package=dict(path=str(bundle),bytes=bundle.stat().st_size,SHA=H(bundle)),worker=dict(path=str(Q/'h1_linux4090_frozen_worker_v1.py'),SHA=H(Q/'h1_linux4090_frozen_worker_v1.py')),parent=dict(path=str(Q/'h1_linux4090_frozen_parent_v1.py'),SHA=H(Q/'h1_linux4090_frozen_parent_v1.py')),source_guard='h1_public4_normal_update1_source_guard_v1',no_target_upload_GPU_native_or_full_yet=True,own_unused_native120_then_CPU_before_full1500=True,original_H1_physics_reward_public_schedule_and_all_guards_unchanged=True,RNG_unchanged0CUDA0optimizer=True)
 with (R/'PUBLIC4_V2_NORMAL_ONLY_FIRST_LINUX_COMPLETE_FROZEN_CPU_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(frozen_normal_only_first_CPU=True,source_SHA=manifest['source']['SHA'],target_dispatch=False)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('PUBLIC4_V2_NORMAL_FIRST_FROZEN_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_source_change=True),f,indent=2)
  raise
