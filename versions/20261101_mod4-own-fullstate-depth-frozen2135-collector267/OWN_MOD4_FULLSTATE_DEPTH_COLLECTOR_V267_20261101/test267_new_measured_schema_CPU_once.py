from pathlib import Path
import copy,hashlib,json,os,time
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
from measured224_schema267 import pack224,validate_transition
N=Path(__file__).resolve().parent;R=N/'reports'
with(R/'ROOT267_NEW_MEASURED_SCHEMA_CPU_PURPOSE_CONSUMED.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),old_fixtures_models_raw_SDK_GPU_remote=0),f)
rng=torch.random.get_rng_state().clone();root=torch.zeros(2,13);root[:,3]=1.;q=torch.zeros(2,30);history=torch.zeros(2,3,2,3);torque=torch.ones(2,30);target=torch.zeros(2,6);L=torch.ones(2,2)*.25;theta=torch.zeros(2,2);contact=torch.ones(2,31,3)*400.
s=pack224(root,q,q,history,torque,target,L,theta,contact);assert s.shape==(2,224)and torch.equal(s[:,131:],torch.ones(2,93))and torch.equal(s[:,91:121],torque)
row=dict(producer_kind='SYNTHETIC_CPU_SCHEMA_ONLY',plant='own_MOD4_live_USD',run_id='new267synthetic',generation='fixture',source_admission_SHA='synthetic',physics_us=2500,physics_callbacks=8,feedback_samples=2,policy_us=20000,physics_end_tick=16,depth_age_seconds=0.,s=s,s1=s,xi31=torch.ones(2,31),depth9=torch.zeros(2,9),a=torch.zeros(2,6));assert validate_transition(row,previous_tick=8,synthetic=True)
rejected=0
for key,bad in(('s1',torch.zeros(2,127)),('physics_callbacks',4),('feedback_samples',1),('depth_age_seconds',-.02),('depth_age_seconds',.21),('physics_end_tick',8),('producer_kind','foreign_Fudan'),('source_admission_SHA','')):
 x={**row,key:bad}
 try:validate_transition(x,previous_tick=8,synthetic=True)
 except ValueError:rejected+=1
 else:raise AssertionError(key)
try:pack224(root,q,q,history,torque,target,L,theta,torch.zeros(2,2,3))
except ValueError:rejected+=1
else:raise AssertionError('Missing31 contacts accepted')
assert rejected==9 and not torch.cuda.is_initialized()and torch.equal(rng,torch.random.get_rng_state())
report=R/'ROOT267_NEW_MEASURED_SCHEMA_CPU_RETURNED.json'
with report.open('x',encoding='utf8')as f:json.dump(dict(passed=True,epoch=time.time(),groups=3,new_rejects=rejected,models_raw_SDK_GPU_remote=0,CUDA_initialized=False,global_RNG_unchanged=True,actual_collector_pending=True),f,indent=2)
files=json.loads((N/'SOURCE267_FILES_BEFORE_NEW_CPU.json').read_bytes())['files']
for p in(report,R/'ROOT267_NEW_MEASURED_SCHEMA_CPU_PURPOSE_CONSUMED.json',N/'SOURCE267_FILES_BEFORE_NEW_CPU.json'):files.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
idx=N/'INDEX267_NEW240_MEAN_REGRESSION_FROZEN.json'
with idx.open('x',encoding='utf8')as f:json.dump(dict(kind='FROZEN_NEW_OWN_FULLSTATE_DEPTH_COLLECTOR_SOURCE',epoch=time.time(),files=files),f,indent=2)
print(json.dumps(dict(passed=True,index_SHA=hashlib.sha256(idx.read_bytes()).hexdigest(),new_rejects=rejected)))
