"""Read-only error by physical reference phase; no optimizer or pass-rate inference."""
from pathlib import Path
import argparse,json,torch,hashlib,time
p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--out',required=True);a=p.parse_args();T=Path(__file__).resolve().parent;torch.set_num_threads(1)
ref=torch.load(T/'rearward_reference_dataset.pt',map_location='cpu',weights_only=False);file=Path(a.model);data=torch.load(file,map_location='cpu',weights_only=False);net=torch.nn.Sequential(torch.nn.Linear(35,256),torch.nn.ELU(),torch.nn.Linear(256,128),torch.nn.ELU(),torch.nn.Linear(128,64),torch.nn.ELU(),torch.nn.Linear(64,6));net.load_state_dict({k.removeprefix('mlp.'):v for k,v in data['actor_state_dict'].items()if k.startswith('mlp.')})
with torch.no_grad():
 predicted=net(ref['policy']);error=(predicted[:,:4]-ref['actions'][:,:4]).square().sum(1);phases={name:dict(frames=int((ref['phase']==i).sum()),leg_MSE=float(error[ref['phase']==i].mean()))for i,name in enumerate(['initial','rearward_lift','forward_place','parent_catch'])}
 initial=(ref['phase']==0).nonzero().flatten()[0];cue=dict(target=ref['actions'][initial,:4].tolist(),predicted=predicted[initial,:4].tolist())
result=dict(epoch=time.time(),model=str(file),sha256=hashlib.sha256(file.read_bytes()).hexdigest(),iteration=data['iter'],no_optimizer=True,no_physical_success_claim=True,phase_errors=phases,first_initial_cue=cue)
out=Path(a.out);assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
