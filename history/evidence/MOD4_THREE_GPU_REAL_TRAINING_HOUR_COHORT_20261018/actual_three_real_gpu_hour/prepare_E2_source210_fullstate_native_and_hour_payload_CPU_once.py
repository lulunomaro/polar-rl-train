"""Prepare the existing E2closed112 fullstate source on its newly available210 GPU."""
from pathlib import Path
import os,sys,json,time,shutil,hashlib,ast,zipfile,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';R.mkdir(exist_ok=True);OLD=W/'MOD4_V8_FINALS_E2_FROZEN_REGRESSION_RECOVERY_ONLY_HANDOFF_20261017/payload/e2';Q=B/'payload/e2';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False)
def main():
 assert not Q.exists();shutil.copytree(OLD,Q,ignore=shutil.ignore_patterns('__pycache__','*.pyc','migrate_saved_reward.py'));m=json.loads((OLD/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());assert m['source_SHA']=='ca6fc2662d5bfe4d33ad63b370389504961a3c2500b4b476c1c527b17b12b2be' and m['source_Adamstep']==666780
 task=Q/'job0/TASK.json';v=json.loads(task.read_bytes());v.update(GPU_UUID='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e',max_parent_seconds=3900,exit_headroom_seconds=300);assert v['kind']=='E2_WORLD_MOVING_SIGNED4' and v['per_GPU_envs']==20000;task.write_text(json.dumps(v,indent=2),'utf8')
 worker=Q/'native_admission_worker.py';s=worker.read_text('utf8');oldworker=H(worker);s=s.replace('import argparse,hashlib,json,os,runpy,sys,time,traceback','import argparse,hashlib,json,os,runpy,sys,time,traceback,shutil');needle="stop=(phase=='precheck128'";assert needle in s;s=s.replace(needle,"stop=(shutil.disk_usage(B).free<8*1024**3) or (phase=='precheck128'");ast.parse(s);worker.write_text(s,'utf8')
 parent=B/'fullstate_native_only_finite_parent_v1.py';assert parent.is_file();shutil.copy2(parent,Q/parent.name)
 os.environ['CUDA_VISIBLE_DEVICES']='';import torch;torch.set_num_threads(2);rng=torch.get_rng_state().clone();ck=torch.load(Q/'job0/source/E2_final58.pt',map_location='cpu',weights_only=False);assert H(Q/'job0/source/E2_final58.pt')==m['source_SHA'] and ck['owned_phase_complete_updates']==112 and len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8 and {int(x['step']) for x in ck['optimizer_state_dict']['state'].values()}=={666780}
 def finite(x):
  if torch.is_tensor(x):assert not x.is_floating_point() or torch.isfinite(x).all()
  elif isinstance(x,dict):
   for v in x.values():finite(v)
  elif isinstance(x,(tuple,list)):
   for v in x:finite(v)
 finite(ck);assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 for p in Q.rglob('*.py'):ast.parse(p.read_text('utf8'))
 m.update(execution_backend='source210',actual_GPU_UUID=v['GPU_UUID'],max_parent_seconds=3900,training_seconds_before_save=3600,storage_complete_update_stop8GiB=True,original_PPO_reward_command_DR_hardware_unchanged=True,worker_only_adds_original_complete_update_storage_guard=True,native_worker_controls144_unchanged=True,source_filename_historical_label_actual_owned112=True);m['files']=[dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(Q.rglob('*')) if p.is_file() and p.name!='THREE_SLOT_COMPLETE_MANIFEST_V1.json' and '__pycache__' not in p.parts];mf=Q/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';mf.write_text(json.dumps(m,indent=2),'utf8');z=B/'E2_SOURCE210_NATIVE_AND_ONE_HOUR_PAYLOAD.zip'
 with zipfile.ZipFile(z,'x',zipfile.ZIP_DEFLATED,compresslevel=5) as f:
  for p in sorted(Q.rglob('*')):
   if p.is_file():f.write(p,p.relative_to(Q).as_posix())
 put('E2_SOURCE210_EXISTING_FULLSTATE_ONE_HOUR_PAYLOAD_CPU_PREPARED_ACTUAL.json',dict(epoch=time.time(),passed_source_fullstate_finite_CPU=True,source_SHA=m['source_SHA'],source_owned112_Adam666780=True,source=next(r for r in m['files'] if r['relative']=='job0/source/E2_final58.pt'),manifest=dict(path=str(mf),bytes=mf.stat().st_size,SHA=H(mf)),package=dict(path=str(z),bytes=z.stat().st_size,SHA=H(z)),old_worker_SHA=oldworker,new_worker_SHA=H(worker),only_complete_update_storage_guard_and_host_GPU_task_binding_changes=True,new_source_backend_native144_and_original_independentCPU_before_learning=True,no_new_reward_LR_STD_physics_command_budget_or_trial_replay=True,RNG0CUDA0optimizer=True));print(json.dumps(dict(E2_CPU_prepared=True,files=len(m['files']),source_SHA=m['source_SHA'])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('E2_SOURCE210_PREPARER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU=True));raise
