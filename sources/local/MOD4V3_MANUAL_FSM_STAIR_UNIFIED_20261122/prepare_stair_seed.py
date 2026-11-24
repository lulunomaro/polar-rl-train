"""CPU imitation of archived physical-success trajectories; no GPU/PPO updates."""
from argparse import ArgumentParser
import time
import numpy as np
import torch
from fsm_paths import HERE,SOFT_DIR,STAIR_DONOR
from fsm_io import put,sha256
from manual_fsm_model import StairExpert

def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument('--steps',type=int,default=1600)
    args=p.parse_args()
    torch.set_num_threads(2)
    torch.manual_seed(1122)
    path=SOFT_DIR/'evidence/softmoe_r2_warmstart/WARMSTART_DATA.npz'
    with np.load(path) as data:
        mask=data['expert']>=1
        x=torch.from_numpy(data['inputs'][mask])
        y=torch.from_numpy(data['actions'][mask]).clamp(-6.,6.)
    net=StairExpert().warm_soft_expert(torch.load(STAIR_DONOR,map_location='cpu',weights_only=False))
    opt=torch.optim.Adam(net.parameters(),lr=1.e-4)
    start=time.monotonic()
    losses=[]
    for step in range(args.steps):
        ids=torch.randint(0,len(x),(256,))
        pred=net(x[ids])
        loss=(pred-y[ids]).square().mean()
        opt.zero_grad();loss.backward();torch.nn.utils.clip_grad_norm_(net.parameters(),1.);opt.step()
        if step%200==0:
            losses.append(dict(step=step,mse=float(loss.detach())))
            print(losses[-1],flush=True)
    net.eval()
    with torch.no_grad():
        mse=float(torch.cat([(net(chunk)-target).square().mean(1) for chunk,target in zip(x.split(512),y.split(512))]).mean())
    out=HERE/'weights/stair_bc_r1.pt'
    out.parent.mkdir(parents=True,exist_ok=True)
    torch.save(dict(format='mod4v3_manual_fsm_stair_v1',stair=net.state_dict(),ppo_updates=0,optimizer_steps=0,
        cpu_bc_optimizer_steps=args.steps,source_sha256=sha256(path),donor_sha256=sha256(STAIR_DONOR)),out)
    put(HERE/'evidence/stair_bc_r1/INITIALIZATION.json',dict(frames=len(x),cpu_bc_steps=args.steps,
        gpu_ppo_updates=0,seconds=time.monotonic()-start,mse=mse,losses=losses,sha256=sha256(out)))
    print('seed',sha256(out),'mse',mse,flush=True)

if __name__=='__main__':main()
