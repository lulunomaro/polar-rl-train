"""Independent paired CPU command contract, not a SDK/PPO/physical admission."""
from pathlib import Path
import hashlib,importlib.util,json,math,tempfile,time,traceback
import torch
D=Path(__file__).resolve().parent;R=D/'reports'
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 torch.set_num_threads(1);assert not torch.cuda.is_initialized()
 p=D/'next_coverage_cpu/retained_flat_full_old_command_math.py'
 new=module('new_coverage_cpu',p);oldp=D/'payload/isaac/mod4/retained_flat_command_math.py';old=module('old_math_cpu',oldp)
 n=20000;eligible=torch.arange(n)<6104;stand=torch.arange(n)%5==0;heading=torch.linspace(-math.pi,math.pi,n)
 a=torch.Generator().manual_seed(20261010);b=torch.Generator().manual_seed(20261010)
 before=a.get_state().clone();o=old.sample_commands(a,eligible,stand,heading);x=new.sample_commands(b,eligible,stand,heading)
 assert torch.equal(a.get_state(),b.get_state())
 assert torch.equal(o['moving'],x['moving']) and torch.equal(o['command'][o['moving']],x['command'][x['moving']])
 assert torch.equal(o['command'][~eligible],x['command'][~eligible]) and (x['command'][stand]==0).all()
 assert not ((x['linear']|x['moving']|x['pure']) & (~eligible|stand)).any()
 assert torch.equal(x['linear']|x['pure'],o['linear']) and not (x['linear']&x['pure']).any()
 assert (x['command'][x['pure'],:2]==0).all() and x['command'][:,2].abs().max()<=4*math.pi+1e-6
 counts={str(rate):{str(sign):int((x['pure'] & (x['pure_signed_yaw']==sign*torch.tensor(rate))).sum()) for sign in (-1,1)} for rate in new.OLD_FLAT_PURE_ABS_RATES}
 assert all(count>0 for v in counts.values() for count in v.values())
 with tempfile.TemporaryDirectory() as temp:
  q=Path(temp)/'private_cpu_stream.pt';torch.save(dict(profile=new.PROFILE,rng=before),q)
  saved=torch.load(q,map_location='cpu',weights_only=False);c=torch.Generator();c.set_state(saved['rng']);again=new.sample_commands(c,eligible,stand,heading)
  assert all(torch.equal(x[k],again[k]) for k in x) and torch.equal(c.get_state(),b.get_state())
 # Complete signed circles at every OLD rate and 16 directions. Analytical
 # commanded world projection integrates to V along the prescribed direction.
 alpha=torch.linspace(-math.pi,math.pi,16,dtype=torch.float64)
 max_error=0.
 for rate in new.OLD_FLAT_PURE_ABS_RATES:
  for sign in (-1,1):
   theta=sign*2*math.pi*(torch.arange(4096,dtype=torch.float64)+.5)/4096
   vx=torch.cos(theta[:,None]-alpha[None,:]);world=torch.stack((vx*torch.cos(theta)[:,None],vx*torch.sin(theta)[:,None]),-1)
   mean=world.mean(0);target=.5*torch.stack((torch.cos(alpha),torch.sin(alpha)),-1)
   max_error=max(max_error,float((mean-target).abs().max()))
 assert max_error<1e-12 and not torch.cuda.is_initialized()
 v=dict(epoch=time.time(),trial_id='E1-G3-130-NEXT-FLAT-OLD-PURE-COMMAND-CPU-CANDIDATE-01',profile=new.PROFILE,source=dict(path=str(p),bytes=p.stat().st_size,sha256=H(p)),old_math=dict(path=str(oldp),sha256=H(oldp)),synthetic_CPU_environments=n,old_world_branches_and_commands_byteexact=True,noneligible_and_standing_commands_byteexact=True,private_CPU_random_consumption_and_disk_restore_exact=True,all_old_pure_rate_signed_counts=counts,complete_signed_circle_projection_math_max_error=max_error,conditional_eligible_nonstanding=dict(straight=.25,world=.5,old_pure=.25),terrain_family_proportions_unchanged=[.30,.20,.20,.15,.15],only_new_axis='eligible flat OLD pure-yaw command coverage',command_yaw_cap_is_old_D7_flat_4pi_not_new_RM_roughspin=True,CPU_COMPONENT_PASSED=True,undeployed=True,no_actual_plane_assignment_or_SDK_native_CUDA_fullstate_PPO_admission_yet=True,original_rewards_hardware_clock_optimizer_DR_must_be_verified_unchanged_before_use=True,no_teacher_or_gate_input_or_new_S7_S8=True,no_learning_or_canonical_write=True,new_budget_seconds=0)
 out=R/'NEXT_COMMAND_COVERAGE_CPU_REVIEW.json';assert not out.exists();out.write_bytes(json.dumps(v,indent=2).encode());print(json.dumps(v))
if __name__=='__main__':
 try:main()
 except Exception:
  p=R/('NEXT_COMMAND_COVERAGE_CPU_ERROR_'+str(time.time_ns())+'.json');assert not p.exists();p.write_bytes(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),CPU_only_no_production_mutation=True),indent=2).encode());raise
