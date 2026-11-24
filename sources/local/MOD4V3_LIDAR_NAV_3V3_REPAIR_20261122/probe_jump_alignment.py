"""Independent zero-update R10/Warp alignment gate at nominal h=0.28 m."""
from pathlib import Path
import argparse
import json
import sys
import time
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'jump_support'),str(ROOT)]
import torch
import warp as wp
from train_generalized_ppo import put,verify_device

def main():
    p=argparse.ArgumentParser();p.add_argument('job',type=Path);p.add_argument('--seconds',type=int,default=0);a=p.parse_args()
    assert a.seconds==0
    torch.set_num_threads(1);torch.manual_seed(20261122);wp.config.kernel_cache_dir=str(ROOT/'cache/warp')
    from jump_unified_gpu import UnifiedJumpGpu
    from unified_policies import UnifiedJumpActor
    a.job.mkdir(parents=True,exist_ok=False);env=actor=None;error=None
    try:
        verify_device()
        actor=UnifiedJumpActor(ROOT/'weights/jump_r10_donor.pt').to('cuda:0').eval()
        before={n:v.clone() for n,v in actor.state_dict().items()}
        timing=dict(speeds=[0.,3.],heights=[.24,.42],platform_380=[[.5,.5],[1.4,1.4]],platform_360=[[.5,.5],[1.4,1.4]],hurdle_380=[[.5,.5],[1.4,1.4]])
        env=UnifiedJumpGpu(2048,20261122,timing)
        anchors=torch.tensor([0.,.6,.8,1.2,1.6,2.2,2.8],device=env.device)
        band=torch.arange(env.n,device=env.device)%len(anchors);speeds=anchors[band]
        env.height[:]=.28;env.speed.copy_(speeds);env.kind[:]=0;env.wall_height[:]=0.;env.mocap[:,:,2]=-4.
        env.perturb_kind[:]=0;env.perturb_tick[:]=0;env.post_vx.copy_(speeds);env.post_wz[:]=0.
        env.key_hold[:]=25;env.begin_tick[:]=90;env.dr_probability=0.;env.dr[:]=False
        env.observe();env.hist[:]=env.obs[:,None]
        peak=torch.zeros(env.n,device=env.device);completed=torch.zeros(env.n,device=env.device,dtype=torch.bool)
        finite=True
        with torch.inference_mode():
            for i in range(600):
                mean=actor(env.actor_input())
                peak=torch.where(~completed,torch.maximum(peak,env.arc[:,2]),peak)
                obs,hist,reward,done=env.step(mean)
                finite &= bool(torch.isfinite(obs).all()&torch.isfinite(mean).all()&torch.isfinite(reward).all())
                completed|=done
                if (i+1)%100==0:put(a.job/'LATEST.json',dict(steps=i+1,completed=int(completed.sum()),liftoff=int((peak>=.22).sum())))
        unchanged=all(torch.equal(before[n],v) for n,v in actor.state_dict().items())
        by=[]
        for i,v in enumerate(anchors.tolist()):
            mask=band==i;by.append(dict(speed=v,episodes=int(mask.sum()),completed=int((completed&mask).sum()),liftoff=int(((peak>=.22)&mask).sum())))
        rate=float((peak>=.22).float().mean())
        report=dict(passed=finite and unchanged and bool(completed.all()) and rate>.50,kind='jump_alignment',steps=600,envs=2048,
            optimizer_steps=0,ppo_updates=0,actor_unchanged=unchanged,e0_unchanged=unchanged,
            nominal_height_m=.28,nominal_liftoff_rate=rate,by_speed=by,
            motor_law='unchanged R10 Jump380Gpu',actor_checkpoint='4c35c0e1')
        put(a.job/'PROBE.json',report);print(json.dumps(report),flush=True)
    except BaseException:
        import traceback
        error=traceback.format_exc();(a.job/'ERROR.txt').write_text(error);raise
    finally:
        torch.cuda.synchronize();del env,actor;torch.cuda.empty_cache()
        put(a.job/'SAFE_CLOSED.json',dict(scene_closed=True,error=error,cuda_synchronized=True,epoch=time.time()))

if __name__=='__main__':main()
