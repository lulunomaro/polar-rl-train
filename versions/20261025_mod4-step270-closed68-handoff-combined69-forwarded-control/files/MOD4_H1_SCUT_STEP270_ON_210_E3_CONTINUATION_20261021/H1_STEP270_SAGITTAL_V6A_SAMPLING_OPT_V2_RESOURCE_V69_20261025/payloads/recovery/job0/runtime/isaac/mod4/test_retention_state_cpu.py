"""Only the new command schema and real disk state, no SDK or old-scope retesting."""
from pathlib import Path
import copy,hashlib,json,tempfile,torch
from retained_flat_command_math import sample_commands
from retention_command_state import PROFILE,FIELDS,validate,same
def main():
 torch.set_num_threads(1);n=20000;g=torch.Generator().manual_seed(20260928+32452843)
 eligible=torch.arange(n)<6000;standing=torch.arange(n)%5==0;heading=torch.linspace(-3.,3.,n)
 row=sample_commands(g,eligible,standing,heading)
 state=dict(version=1,profile=PROFILE,num_envs=n,rng_device_type='cpu',rng=g.get_state().clone(),assignment_sha256='1'*64,no_position_correction=True,no_mask_actor_or_gate_input=True,eligible_flat=eligible,linear=row['linear'],moving=row['moving'],direction=row['world_direction'],signed_yaw=row['signed_yaw'],linear_vx=row['command'][:,0],family=torch.where(eligible,0,4),sample_histogram=torch.zeros((6,7),dtype=torch.long),control_histogram=torch.zeros((6,7),dtype=torch.long),_command_heading=heading,phase_elapsed=torch.zeros(n),BODY_command=row['command'])
 assert validate(state,n);tests=0
 with tempfile.TemporaryDirectory() as d:
  p=Path(d)/'command_state.pt';torch.save(state,p);loaded=torch.load(p,map_location='cpu',weights_only=False);assert same(state,loaded)
  restored=torch.Generator();restored.set_state(loaded['rng']);assert torch.equal(torch.rand(1000,generator=g),torch.rand(1000,generator=restored));disk_SHA=hashlib.sha256(p.read_bytes()).hexdigest()
 for k,v in [('profile','wrong'),('eligible_flat',torch.zeros(n,dtype=torch.bool)),('moving',state['linear'].clone()),('family',torch.full((n,),5)),('direction',torch.full((n,),float('nan'))),('rng',torch.empty(0,dtype=torch.uint8)),('signed_yaw',torch.full((n,),4.)),('sample_histogram',torch.zeros((5,7),dtype=torch.long)),('no_mask_actor_or_gate_input',False),('num_envs',10),('BODY_command',torch.zeros(n,2)),('rng_device_type','unknown'),('assignment_sha256','short'),('phase_elapsed',torch.full((n,),float('nan')))]:
  bad=copy.deepcopy(state);bad[k]=v
  try:validate(bad,n)
  except (AssertionError,KeyError):tests+=1
  else:raise AssertionError('Invalid new command state accepted: '+k)
 assert not torch.cuda.is_initialized()
 print(json.dumps(dict(passed=True,new_command_schema_rejection_tests=tests,actual_CPU_disk_private_rng_roundtrip_exact=True,disk_SHA=disk_SHA,no_CUDA_initialized=True,CPU_only_no_physical_claim=True,target_torch=torch.__version__,actual_SDK_assignment_support_native_CUDA_fullresume_still_required=True)))
if __name__=='__main__':main()
