"""Parity and timing of only state translation; no checkpoint or physics."""
from pathlib import Path
from types import SimpleNamespace as NS
import json,sys,time,traceback
import torch,warp as wp
N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
sys.path.insert(0,str(G/'project/isaac'))
from mod4v2_scut.newton_env import NewtonEnv
from mod4v2_scut.newton_sampling import install_state_read
R=N/'sampling_state_fusion01';R.mkdir(exist_ok=False)
out=dict(epoch=time.time(),production_PT_reads=0,SSH=0,physics_steps=0,
    active_run_modified=False,passed=False,measurements=[])
fields=('joint_pos','joint_vel','body_pos_w','body_quat_w','body_lin_vel_w',
        'root_pos_w','root_quat_w','root_lin_vel_w','root_lin_vel_b',
        'root_ang_vel_b','projected_gravity_b')
try:
    wp.init();device='cuda:0'
    wp.set_stream(wp.stream_from_torch(torch.cuda.current_stream(device)))
    torch.manual_seed(9139)
    for n in (128,20000):
        q=torch.randn(n,37,device=device);v=torch.randn(n,36,device=device)
        bodies=torch.randn(n*31,7,device=device)
        bodies[:,3:]/=bodies[:,3:].norm(dim=-1,keepdim=True)
        velocity=torch.randn(n*31,6,device=device)
        com=torch.randn(n*31,3,device=device)*.03
        env=NS(num_envs=n,device=device,qadr=torch.arange(7,37,device=device),
            vadr=torch.arange(6,36,device=device),data=NS(),plant=NS(
                state=NS(joint_q=wp.from_torch(q.flatten()),joint_qd=wp.from_torch(v.flatten()),
                    body_q=wp.from_torch(bodies,dtype=wp.transform),
                    body_qd=wp.from_torch(velocity,dtype=wp.spatial_vector)),
                model=NS(body_com=wp.from_torch(com,dtype=wp.vec3))))
        NewtonEnv.update_data(env)
        reference={k:getattr(env.data,k).clone()for k in fields}
        install_state_read(env);wp.synchronize()
        errors={k:float((getattr(env.data,k)-reference[k]).abs().max())for k in fields}
        assert max(errors.values())<3e-6,errors
        # A second alternating state buffer must be read, not a stale pointer.
        saved=env.plant.state
        second=NS(joint_q=wp.from_torch((q+1).flatten()),joint_qd=saved.joint_qd,
            body_q=saved.body_q,body_qd=saved.body_qd)
        env.plant.state=second;env.update_data();wp.synchronize()
        assert torch.equal(env.data.joint_pos,(q+1)[:,env.qadr])
        env.plant.state=saved
        times={}
        for label,fn in [('torch',lambda:NewtonEnv.update_data(env)),('fused',env.update_data)]:
            fn();wp.synchronize()
            start=time.perf_counter()
            for _ in range(32):fn()
            wp.synchronize();times[label]=(time.perf_counter()-start)/32
        out['measurements'].append(dict(envs=n,max_errors=errors,seconds_per_call=times,
            local_component_ratio=times['torch']/times['fused']))
    out.update(passed=True,alternate_state_buffer_correct=True,all11outputs_match=True,
        GPU=torch.cuda.get_device_name(),full_production_speedup_measured=False)
except BaseException:out['error']=traceback.format_exc()
with(R/'RESULT.json').open('x',encoding='utf8')as f:json.dump(out,f,indent=2)
print(json.dumps(out))
if not out['passed']:raise SystemExit(1)
