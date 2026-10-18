"""Restore previously deployed frozen V3 auditor; never alter GPU/source/physical gates."""
from pathlib import Path
import json,ast,shutil,time,hashlib,sys
import numpy as np,torch
B=Path(__file__).resolve().parent;P=B.parent;R=B/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):
 with Path(p).open('x',encoding='utf8') as f:f.write(s if isinstance(s,str) else json.dumps(s,ensure_ascii=False,indent=2))
def main():
 rng=torch.get_rng_state().clone();old=P/'h1_owned_dual_FP64_mean_reference_same_bound_v1.py';shutil.copy2(old,B/old.name)
 source=B/'review_8a7c_GPU1_allrow_source_FP32_CPU_once.py';s=source.read_text(encoding='utf8');begin=s.index(' for start in range(0,len(flat),120000):');end=s.index(" phase=H1TakeoffProgressPhaseV2",begin)
 s=s[:begin]+''' from h1_owned_dual_FP64_mean_reference_same_bound_v1 import audit_saved_mean
 precision=audit_saved_mean(sd,flat,actual);mean_error=precision['torch64_maxabs']
'''+s[end:]
 s=s.replace('actor_reference_protocol="original_FP32_fixed120000row_batch_same_absolute1e-4_declared_before_GPU",','actor_reference_protocol="Restored existing frozen V3 independent Torch/NumPy FP64 references on original F32 weights/obs/GPU output; same absolute1e-4",precision_metrics=precision,old_FP32_reference_failure_retained=True,no_posthoc_rowwise_reference_selection=True,')
 s=s.replace("'_ALL_PHYSICAL_PUBLIC04_SOURCE_CPU_ACTUAL.json'","'_ALL_PHYSICAL_PUBLIC04_SOURCE_FP64_REFERENCE_CPU_V3_ACTUAL.json'").replace('H1_LINUX72_FROZEN_ALLROW_CPU_ORIGINAL_ERROR_','H1_8A7C_FROZEN_V3_CPU_ORIGINAL_ERROR_')
 ast.parse(s);write(B/'review_8a7c_allrow_existing_frozen_V3_reference_CPU_once.py',s)
 # The full GPU case has never been created: bind its only ready check to the restored V3 result.
 oldfull=B/'dispatch_8a7c_GPU1_unused_full1500_after_nativeCPU_once.py';new=oldfull.read_text(encoding='utf8').replace('H1_CR3FINAL_LINUX72_120_ALL_PHYSICAL_PUBLIC04_SOURCE_CPU_ACTUAL.json','H1_CR3FINAL_LINUX72_120_ALL_PHYSICAL_PUBLIC04_SOURCE_FP64_REFERENCE_CPU_V3_ACTUAL.json');ast.parse(new);write(B/'dispatch_8a7c_GPU1_unused_full1500_after_restored_V3_nativeCPU_v2_once.py',new)
 # Same four established reference rejection fixtures; no new threshold.
 sys.path.insert(0,str(B));from h1_owned_dual_FP64_mean_reference_same_bound_v1 import audit_saved_mean
 sd={}
 for i,shape in [(0,(256,35)),(2,(128,256)),(4,(64,128)),(6,(6,64))]:sd[f'mlp.{i}.weight']=torch.zeros(shape);sd[f'mlp.{i}.bias']=torch.zeros(shape[0])
 x=np.zeros((2,35),np.float32);y=np.zeros((2,6),np.float32);audit_saved_mean(sd,x,y);bad=[]
 for label,xx,yy in [('shape',x[:,:34],y),('dtype',x.astype(np.float64),y),('NaN',x,np.full_like(y,np.nan)),('above_original_bound',x,np.full_like(y,.0003))]:
  try:audit_saved_mean(sd,xx,yy)
  except AssertionError:bad.append(label)
  else:raise AssertionError(label)
 assert len(bad)==4 and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 write(R/'H1_8A7C_EXISTING_FROZEN_V3_AUDITOR_RESTORED_CPU_ACTUAL.json',dict(epoch=time.time(),own_process_regression='Mistakenly applied native FP32 numerical reference to frozen evaluation, replacing the already established frozen V3 precision repair; user did not request a new training hurdle.',human_steering=['你这个新增门槛又是啥门槛？怎么天天加一堆门槛？','不是哥们之前有这个门槛吗？你又新加门槛隔着拖慢我进度呢？'],original_absolute1e4_preexisted=True,restored_prior_frozen_reference_source=dict(path=str(old),SHA=H(old)),new_reference_byteexact_prior=True,same_uniform_reference_for_all9600_native_and_future120000_full_rows=True,original_fixed_FP32_false_stays_false=True,full_dispatch_old_helper_not_executed=True,new_unused_full_helper='dispatch_8a7c_GPU1_unused_full1500_after_restored_V3_nativeCPU_v2_once.py',reference_negative_cases=bad,no_model_training_precision_reward_LR_STD_physics_or_gate_change=True,no_new_PPO_GPU_replay_or_budget=True,CPU_RNG_unchanged0CUDA0optimizer=True,local_lookup_miss_retained='review_public4_V2_final_Linux_GPU1_allrow_source_CPU_FP64_reference_v3_once.py alias not found; actual prior V3 reader located via rg --files'))
 print(json.dumps(dict(existing_frozen_V3_reference_restored=True,negative_cases=bad,original_FP32_false_retained=True)))
if __name__=='__main__':main()
