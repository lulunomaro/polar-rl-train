"""Three distinct expert tasks, conservative first1800s blocks in existing budget."""
from pathlib import Path
import os,ast,hashlib,json,shutil,time,traceback,sys
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch,numpy as np
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';Q=D/'train_payload';T=W/'MOD4_HOST72_E1_CURB_SLOPE_TRAINING_ASSIGNMENT_20261016'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not Q.exists();Q.mkdir();rows=[];sys.path.insert(0,str(D));from independent_expert_axis_v1 import layout
 rng=torch.get_rng_state().clone();a=np.arange(20000);orig=np.stack(((a%140-70)*2.+.1,(a//140-70)*2.+.1,np.zeros(len(a))),-1);grid=np.zeros((40,40),dtype=np.int64);grid[:,34:40]=4
 c,m=layout(orig,grid);assert c.shape==(20000,2) and m.shape==(20000,)
 negatives=[]
 for name,x,g in [('out_of_grid',orig+1000,grid),('wrong_family_shape',orig,grid[:20])]:
  try:layout(x,g)
  except ValueError:negatives.append(name)
  else:raise AssertionError(name)
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 specs=[('CURB20',0,'10.24.4.210','GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e','train_curb20_entry_resume_ppo.py',None),('SLOPE5',1,'10.24.0.72','GPU-c27eecbd-6838-7290-1cd2-37e34522213d','train_slope5_snapshot_reviewed_resume_ppo.py','slope'),('WAVE35',0,'10.24.0.72','GPU-16828f91-2b45-b646-8dc0-9481138e2842','train_e1_retention_sdk_reviewed_resume_ppo.py','wave')]
 for i,(kind,oldid,host,uuid,entry,axis) in enumerate(specs):
  src=T/'payload'/('job'+str(oldid));j=Q/('job'+str(i));shutil.copytree(src,j,ignore=shutil.ignore_patterns('__pycache__','TASK_ASSIGNMENT.json'));m=j/'runtime/isaac/mod4';shutil.copyfile(D/'independent_expert_axis_v1.py',m/'independent_expert_axis_v1.py')
  original=(m/entry).read_text(encoding='utf8');s=original
  if axis:
   old='from '+('slope5_retention_runtime' if axis=='slope' else 'retention_flat_runtime_sdk_reviewed')+' import configure_retention as configure_intro'
   assert old in s;s=s.replace(old,'from independent_expert_axis_v1 import configure_'+axis+' as configure_intro')
  if host.endswith('.72'):
   needle='from isaaclab.app import AppLauncher';assert needle in s;s=s.replace(needle,'from zonglin2_app_launcher import Zonglin2AppLauncher as AppLauncher')
  out=m/'train_independent_owned_axis_v1.py';assert not out.exists();compile(s,str(out),'exec');out.write_text(s,encoding='utf8')
  ck=torch.load(j/'source/source.pt',map_location='cpu',weights_only=False);ts=[]
  def walk(x):
   if torch.is_tensor(x):assert not x.is_floating_point() or torch.isfinite(x).all();ts.append(x)
   elif isinstance(x,dict):
    for v in x.values():walk(v)
   elif isinstance(x,(tuple,list)):
    for v in x:walk(v)
  walk(ck);assert len(ts)==181 and sum(x.is_floating_point() for x in ts)==102 and len(ck['optimizer_state_dict']['state'])==17
  expected='24b18846fcff1e0b8da7fd478314fca9cd2ed2b97461ca34f65ef5b7c7ff2411' if kind=='SLOPE5' else '3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e';assert H(j/'source/source.pt')==expected
  task=dict(job=i,kind=kind,host=host,GPU_UUID=uuid,source_SHA=expected,source_Adamstep=int(next(iter(ck['optimizer_state_dict']['state'].values()))['step']),entry='train_independent_owned_axis_v1.py',native_controls=120,per_GPU_envs=20000,max_learning_parent_seconds=1800,exit_headroom=60,original_snapshot=str(src/'original_run_manifest.json'),no_STD_or_optimizer_reset=True,axis='Reset-bound normal task command direction toward original CURB with standing and RNG draws retained' if kind=='CURB20' else 'Original target-family geometry and commands; complete route exposure with tile-bound truncation only',not_S8_or_second_gate_or_50mm_blind_repeat=True)
  (j/'TASK.json').write_text(json.dumps(task,indent=2),encoding='utf8');freeze=j/'runtime/reports/SOURCE_FREEZE.json';freeze.write_text(json.dumps(dict(sha256={p.relative_to(j/'runtime').as_posix():H(p) for p in sorted((j/'runtime').rglob('*')) if p.is_file() and p!=freeze}),indent=2),encoding='utf8');rows.append(task)
 shutil.copyfile(D/'independent_expert_axis_v1.py',Q/'independent_expert_axis_v1.py')
 (R/'THREE_DISTINCT_EXPERT_SOURCE_AXIS_CPU_PREPARED_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),CPU_prepared=True,rows=rows,whole_source181tensor102float_17Adam_finite=True,route_layout_CPU_N20000=True,negative_fixtures=negatives,no_CUDA_or_optimizer=True,new_task_axes_not_native_or_PPO_passed=True,human_authorized_independent_GPU_tasks=True,cohort_charging='Original solecanonical owner sums each distinct expert actual learning/loadsaveexit interval; no new budget or threefold charge for prior shared-PPO interval',source878_not_used_as_qualified_CURB_or_blind_continuation=True),indent=2),encoding='utf8');print(json.dumps(dict(prepared=3,new_target_GPU=False)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  (R/('THREE_EXPERT_CPU_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_dispatch=True),indent=2));raise
