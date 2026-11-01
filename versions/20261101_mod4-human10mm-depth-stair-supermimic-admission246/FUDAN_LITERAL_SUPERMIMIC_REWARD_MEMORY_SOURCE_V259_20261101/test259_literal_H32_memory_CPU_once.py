from pathlib import Path
import hashlib,json,os,sys,time
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';R.mkdir(exist_ok=True)
marker=R/'ROOT259_NEW_SYNTHETIC_H32_PURPOSE_CONSUMED.json'
with marker.open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),kind='NEW_SYNTHETIC_LITERAL_FUDAN_MEMORY_H32',real_models_raw_SDK_GPU_remote=0),f)
P=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package'
sys.path.insert(0,str(P))
from jump194_boundary import LiteralJump194
from literal_imagination259 import RewardMemory,imagined_step
rng=torch.random.get_rng_state().clone();names=['left_wheel','right_wheel']+['own_body_'+str(i)for i in range(29)]
n=2;reference=LiteralJump194(n,'cpu',.02,names);memory=RewardMemory(torch.zeros(n),torch.zeros(n,2,dtype=torch.bool),torch.zeros(n,6,2))
ref_history=torch.zeros(n,6,2);parameter=torch.tensor(.04,requires_grad=True);objective=0.;max_error=0.
for t in range(32):
    flight=t%8 in(3,4,5)
    contact=torch.zeros(n,31,3);contact[:,:2,2]=0. if flight else 60.
    root=torch.zeros(n,13);root[:,2]=.25+parameter*.1;root[:,6]=1.;root[:,9]=.2+parameter
    frame=dict(commands=torch.tensor([[.3,0.,.135,0.]]).repeat(n,1),root_states=root,
        base_lin_vel=torch.stack((parameter.expand(n),torch.zeros(n),torch.zeros(n)),-1),base_ang_vel=torch.zeros(n,3),projected_gravity=torch.tensor([[0.,0.,-1.]]).repeat(n,1),
        L0=torch.full((n,2),.24)+parameter*.1,theta0=torch.zeros(n,2),torques=torch.zeros(n,6),contact_forces=contact)
    action=parameter.expand(n,6);reset=torch.tensor([t%7==6,False])
    got,memory=imagined_step(frame,action,memory,literal_class=LiteralJump194,body_names=names,tick=t,reset_after=reset)
    expected=reference.measured_step(dict(frame,actions=action,last_actions=ref_history),t).clone()
    max_error=max(max_error,float((got-expected).abs().max().detach()))
    ref_history=torch.stack((action,ref_history[:,:,0]),-1)
    ids=reset.nonzero().flatten()
    if len(ids):
        reference.reset_sums(ids)
        ref_history=torch.stack((action,torch.where(reset[:,None],torch.zeros_like(action),ref_history[:,:,1])),-1)
    assert torch.equal(memory.last_contacts,reference.last_contacts)
    assert torch.equal(memory.base_air_time,reference.base_air_time)
    assert torch.equal(memory.last_actions,ref_history)
    objective=objective+.9801**t*got.mean()
grad=torch.autograd.grad(objective,parameter)[0]
assert max_error==0. and torch.isfinite(grad)and grad.abs()>0
bad={**frame};bad.pop('contact_forces')
try:imagined_step(bad,action,memory,literal_class=LiteralJump194,body_names=names,tick=33)
except ValueError:pass
else:raise AssertionError('Missing measured/predicted contacts accepted')
assert torch.equal(rng,torch.random.get_rng_state())and not torch.cuda.is_initialized()
report=R/'ROOT259_LITERAL19_H32_MEMORY_AND_ACTUAL_AUTOGRAD_CPU_RETURNED.json'
with report.open('x',encoding='utf8')as f:json.dump(dict(passed=True,epoch=time.time(),synthetic_steps=32,synthetic_envs=2,groups=3,rejects=1,original_methods_max_reward_error=max_error,H32_direct_reward_scalar_gradient=float(grad),all_contact_air_action_memory_equal=True,CUDA_initialized=False,global_RNG_unchanged=True,real_models_raw_SDK_GPU_remote_reads=0,real_Pi_WM_updates=0,not_skill_or_training=True,required_new_WM_measurements=['contact_forces31x3','applied_effort6','own_L0_theta0_or_differentiable_ownFK','BODY_position_difference_velocity'],old127_state_alone_insufficient=True),f,indent=2,allow_nan=False)
files=[Path(__file__).resolve(),N/'literal_imagination259.py',report,marker]
for name in('jump194_boundary.py','literal_original_methods.py','literal_original_config.py'):
    p=P/name;files.append(p)
idx=N/'INDEX259_LITERAL_IMAGINATION_SOURCE_FROZEN.json'
with idx.open('x',encoding='utf8')as f:json.dump(dict(kind='SOURCE_ONLY_REAL_LITERAL19_H32_REWARD_ADAPTER_NOT_REAL_LEARNER',epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in files]),f,indent=2)
print(json.dumps(dict(passed=True,index_SHA=hashlib.sha256(idx.read_bytes()).hexdigest(),H32_gradient=float(grad),reward_error=max_error,real_training=False)))
