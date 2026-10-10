"""CPU-only undeployed new-command proof; actual SDK/PPO admission still required."""
from pathlib import Path
import hashlib,json,math,sys,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D/'implementation'))
import torch
from retained_flat_command_math import sample_commands,update_world_projection
def main():
 p=R/'RETAINED_FLAT_COMMAND_CPU_REVIEW.json';assert not p.exists()
 torch.set_num_threads(1);assert not torch.cuda.is_initialized()
 n=20000;gen=torch.Generator(device='cpu').manual_seed(20261010)
 # Synthetic eligibility only tests branch mathematics, not actual terrain clearance.
 eligible=torch.arange(n)<6000;standing=torch.arange(n)%5==0
 heading=torch.linspace(-math.pi,math.pi,n);state=gen.get_state().clone()
 a=sample_commands(gen,eligible,standing,heading);after=gen.get_state().clone()
 gen.set_state(state);b=sample_commands(gen,eligible,standing,heading)
 assert all(torch.equal(a[k],b[k]) for k in a) and torch.equal(gen.get_state(),after)
 c=a['command'];lin=a['linear'];moving=a['moving'];non=~eligible & ~standing
 assert not (lin&moving).any() and not (moving&standing).any()
 assert torch.equal(lin|moving,eligible&~standing)
 assert c[non,0].abs().max()<=.3 and not c[non,1:].any()
 assert not c[standing].any() and not c[:,1].any()
 assert c[lin,0].abs().min()>=1 and c[lin,0].abs().max()<=1.5
 assert c[moving,0].abs().max()<=1 and c[moving,2].abs().min()>=1 and c[moving,2].abs().max()<=2
 for mask in (lin,moving):assert (c[mask,0 if mask is lin else 2]>0).any() and (c[mask,0 if mask is lin else 2]<0).any()
 # Independent analytic integral over full signed circles; world progress is .5,
 # not instantaneous heading velocity, and cross integral is zero.
 alpha=torch.tensor([-2.2,-.4,1.1,2.7],dtype=torch.float64)
 yaw=torch.tensor([-2.,-1.,1.,2.],dtype=torch.float64)
 phase=torch.linspace(0,2*math.pi,20001,dtype=torch.float64)
 theta=torch.sign(yaw)[:,None]*phase[None,:]+.37
 vx=torch.cos(theta-alpha[:,None]);wx=vx*torch.cos(theta);wy=vx*torch.sin(theta)
 along=wx*torch.cos(alpha[:,None])+wy*torch.sin(alpha[:,None])
 cross=-wx*torch.sin(alpha[:,None])+wy*torch.cos(alpha[:,None])
 alongmean=torch.trapezoid(along,phase,dim=1)/(2*math.pi)
 crossmean=torch.trapezoid(cross,phase,dim=1)/(2*math.pi)
 assert (alongmean-.5).abs().max()<1e-12 and crossmean.abs().max()<1e-12
 newheading=heading+.25;update_world_projection(c,moving,newheading,a['world_direction'],a['signed_yaw'])
 assert torch.equal(c[moving,0],torch.cos(newheading[moving]-a['world_direction'][moving]))
 body_law=dict(along_integral_mean=alongmean.tolist(),cross_integral_mean=crossmean.tolist(),no_position_correction=True)
 out=dict(epoch=time.time(),trial_id='E1-G3-RETAINED-FLAT-COMMAND-CPU-CANDIDATE-01',source=str((D/'implementation/retained_flat_command_math.py').resolve()),sha256=hashlib.sha256((D/'implementation/retained_flat_command_math.py').read_bytes()).hexdigest(),CPU_passed=True,samples=n,synthetic_flat=6000,synthetic_standing=int(standing.sum()),linear=int(lin.sum()),moving=int(moving.sum()),linear_negative=int((c[lin,0]<0).sum()),moving_negative=int((c[moving,2]<0).sum()),named_generator_disk_state_semantics_exact=True,ordinary_nonflat_yaw0_preserved=True,world_full_signed_circle_math=body_law,
 actual_terrain_assignment_or_physical_clearance_verified=False,SDK_native_PPO_admitted=False,new_learning_launched=False,own_fullsave_resume_contract_pending=True,CPU_proof_is_not_physical_skill_or_anti_forgetting=True,no_CUDA_initialized=True,new_budget_seconds=0)
 p.write_bytes(json.dumps(out,indent=2).encode());print(json.dumps(out))
if __name__=='__main__':
 try:main()
 except Exception:
  p=R/'RETAINED_FLAT_COMMAND_CPU_ERROR.json';assert not p.exists();p.write_bytes(json.dumps(dict(epoch=time.time(),trial_id='E1-G3-RETAINED-FLAT-COMMAND-CPU-CANDIDATE-01',error=traceback.format_exc(),no_production_mutation=True),indent=2).encode());raise
