"""Root continues only unfinished CPU candidate mathematics after agent transport failure."""
from pathlib import Path
import json,time,hashlib,torch
from left_joint_domain_cpu_component import candidate_initialization,guarded_targets,legal_raw_left_interval,CPU_mean,SOURCE_SHA
D=Path(__file__).resolve().parent
source=D.parent/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/RECOVERED_WINDOWS512_28UPDATE/model_32411.pt'
assert hashlib.sha256(source.read_bytes()).hexdigest()==SOURCE_SHA and not torch.cuda.is_initialized()
ck=torch.load(source,map_location='cpu',weights_only=False)
offset=torch.tensor(ck['WINDOWS4090_LEFT_HEAD_REPAIR_ACTUAL']['actual_GPU_API_offset_and_default_q_leg_order'],dtype=torch.float32)
desired=(-1.0843+.85)/2
rng=torch.get_rng_state().clone()
out=candidate_initialization(ck,source_sha=SOURCE_SHA,actual_offset_witness=offset,desired_difference=desired)
assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
# Explicit CPU fixtures exercise the scalar action-domain contract, not physical motion.
hip=torch.linspace(-8,8,2001);lo,hi=legal_raw_left_interval(hip,offset)
assert (lo<=hi).all()
raw=torch.zeros(2001,6);raw[:,1]=hip;raw[:,0]=((hip.clip(-6,6)+(desired-float(offset[0]-offset[1]))/.5)).clip(-6,6)
targets=guarded_targets(raw,offset);diff=targets[:,0]-targets[:,1]
assert (diff>=-1.0843-1e-6).all() and (diff<=.85+1e-6).all()
obs=torch.zeros(64,35);obs[:,0]=torch.linspace(-1,1,64)
old=CPU_mean(ck['actor_state_dict'],obs);new=CPU_mean(out['actor_state_dict'],obs)
assert torch.equal(new[:,1:],old[:,1:])
assert torch.allclose(new[:,0]-new[:,1],torch.full((64,),(desired-float(offset[0]-offset[1]))/.5),rtol=0,atol=1e-4)
negative=[]
def reject(label,**kw):
 try:candidate_initialization(ck,**kw)
 except AssertionError:negative.append(label)
 else:raise AssertionError('Wrong candidate accepted: '+label)
base=dict(source_sha=SOURCE_SHA,actual_offset_witness=offset,desired_difference=desired)
reject('wrong source SHA',**dict(base,source_sha='0'*64))
reject('wrong actual offset',**dict(base,actual_offset_witness=offset+torch.tensor([.01,0,0,0])))
reject('outside lower domain',**dict(base,desired_difference=-1.2))
reject('boundary itself rejected',**dict(base,desired_difference=-1.0843))
reject('insufficient interior margin',**dict(base,desired_difference=-1.0343))
reject('wrong scaling',**dict(base,scale=.4))
try:candidate_initialization(out,**base)
except AssertionError:negative.append('repeat initialization rejected')
else:raise AssertionError('repeat initialization accepted')
assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
q=D/'CPU_ONLY_UNADOPTED_JOINT_CANDIDATE';q.mkdir(exist_ok=False);p=q/'source512_left_joint_interior_CPU_prepared_only.pt';torch.save(out,p)
proof=dict(epoch=time.time(),CPU_math_passed=True,component_source_SHA=hashlib.sha256((D/'left_joint_domain_cpu_component.py').read_bytes()).hexdigest(),source=dict(path=str(source),sha256=SOURCE_SHA,bytes=source.stat().st_size),candidate=dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size),desired_crank_minus_hip_rad=desired,negative_cases=negative,no_CPU_RNG_draw_or_CUDA=True,five_other_mean_heads_std_trunk_critic_DR_RNG_history_initial_exact=True,only_left_row0_initial_parameter_copy_and_Adam_row0_moments=True,synthetic_2001_action_domain_fixtures_passed=True,64_synthetic_actor_fixtures_passed=True,existing_RAW_actor_input_behavior_replay_not_done=True,new_GPU_physics_fullstate_and_behavior_not_done=True,no_production_adoption=True,no_running_trainer_modified=True,not_a_unique_failure_cause_proof=True,qualified50=False)
(D/'reports/LEFT_JOINT_INTERIOR_COMPONENT_CPU_ACTUAL_REVIEW.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
print(json.dumps(dict(CPU_math_passed=True,candidate_SHA=proof['candidate']['sha256'],negative_cases=len(negative),GPU_or_deployment_pass_claimed=False)))
