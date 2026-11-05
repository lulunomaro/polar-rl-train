"""Bounded local sampling attribution, with no production checkpoint or SSH."""
from pathlib import Path
import argparse
import functools
import hashlib
import json
import sys
import time
import traceback

import torch
import warp as wp

N = Path(__file__).resolve().parent
G = Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
sys.path.insert(0, str(G/'project/isaac'))
from mod4v2_scut.newton_env import NewtonEnv
from mod4v2_scut.config import ground_scan_config
from mod4v2_scut.math_ops import quat_apply, quat_from_euler_xyz, euler_xyz_from_quat


def old_scans(env):
    """Pre-repair formula, evaluated on the same state without physics."""
    d=env.data
    scan=ground_scan_config()
    sx,sy=scan['size'];res=scan['resolution']
    x=torch.linspace(-sx/2,sx/2,int(sx/res)+1,device=env.device)
    y=torch.linspace(-sy/2,sy/2,int(sy/res)+1,device=env.device)
    xx,yy=torch.meshgrid(x,y,indexing='ij')
    offsets=torch.stack((xx.flatten(),yy.flatten(),torch.zeros(xx.numel(),device=env.device)),-1)
    yaw=euler_xyz_from_quat(d.root_quat_w)[2]
    q=quat_from_euler_xyz(torch.zeros_like(yaw),torch.zeros_like(yaw),yaw)
    points=d.root_pos_w[:,None]+quat_apply(q[:,None].expand(-1,len(offsets),-1),offsets[None].expand(env.num_envs,-1,-1))
    _,hits=env.raycast(points)
    ground=hits[...,2].mean(-1)
    wheels=ground[:,None].expand(-1,2)
    far,far_hits=env.forward_scan(False)
    near,near_hits=env.forward_scan(True)
    return ground,wheels,far,far_hits,near,near_hits


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--num-envs', type=int, default=128)
    parser.add_argument('--controls', type=int, default=8)
    parser.add_argument('--scan-comparison', action='store_true')
    a = parser.parse_args()
    a.output.mkdir(exist_ok=False)
    report = dict(epoch=time.time(), kind='LOCAL_SAMPLING_ATTRIBUTION',
        production_PT_reads=0, SSH=0, active_run_changed=False,
        production_20k_throughput_claim=False, num_envs=a.num_envs,
        controls=a.controls, passed=False)
    env = None
    originals = []

    def instrument(obj, name, label):
        original = getattr(obj, name)
        @functools.wraps(original)
        def wrapped(*args, **kwargs):
            with torch.profiler.record_function(label):
                return original(*args, **kwargs)
        originals.append((obj, name, original))
        setattr(obj, name, wrapped)

    try:
        torch.manual_seed(9170)
        env = NewtonEnv(
            'F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package',
            N.parents[1]/'workspace/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/payload/job0/runtime/isaac/mod4',
            N/'runtime_refs/runtime/isaac/mod4/reset_bank.json', a.num_envs, 'cuda:0', 9170)
        action = torch.zeros(a.num_envs, 6, device='cuda:0')
        if a.scan_comparison:
            comparison=[]
            original_pos=env.data.root_pos_w.clone()
            original_quat=env.data.root_quat_w.clone()
            with torch.inference_mode():
                for scale in (0., .2, 1.):
                    env.data.root_pos_w=original_pos+torch.randn_like(original_pos)*scale
                    angles=torch.randn(a.num_envs,3,device=env.device)*scale
                    env.data.root_quat_w=quat_from_euler_xyz(*angles.unbind(-1))
                    before=old_scans(env);after=env.scans()
                    wp.synchronize()
                    errors=[float((x-y).abs().max())for x,y in zip(before,after)]
                    assert all(x==0. for x in errors),errors
                    comparison.append(dict(pose_scale=scale,max_errors=errors))
                env.data.root_pos_w=original_pos
                env.data.root_quat_w=original_quat
                timing={}
                for label,fn in [('old',lambda:old_scans(env)),('cached',env.scans)]:
                    fn();wp.synchronize();start=time.perf_counter()
                    for _ in range(a.controls):fn()
                    wp.synchronize()
                    timing[label]=(time.perf_counter()-start)/a.controls
            report.update(passed=True,kind='LOCAL_SCAN_CACHE_PARITY_AND_TIMING',
                actual_physics_steps=0,parity=comparison,scan_seconds_per_call=timing,
                local_scan_ratio=timing['old']/timing['cached'],
                production_speedup_not_measured=True,
                GPU=torch.cuda.get_device_name())
            return
        with torch.inference_mode():
            for _ in range(4):
                env.step(action)
            wp.synchronize()
            start = time.perf_counter()
            for _ in range(a.controls):
                env.step(action)
            wp.synchronize()
            report['unprofiled_local_seconds'] = time.perf_counter()-start

        for name in ('update_data', 'sample_feedback', 'reset', 'scans',
                     'closure_errors', 'observations'):
            instrument(env, name, 'MOD4/'+name)
        instrument(env.sensor, 'update', 'MOD4/contact_sensor')
        instrument(env.acceptance, 'update_world', 'MOD4/acceptance400Hz')
        for name in ('begin', 'compute', '_get_dones'):
            instrument(env.reward, name, 'MOD4/reward_'+name)
        for name in ('submit', 'apply'):
            instrument(env._physics_action_delay, name, 'MOD4/action_queue_'+name)
        instrument(wp, 'capture_launch', 'MOD4/physics_graph_launch')
        with torch.profiler.profile(
                activities=[torch.profiler.ProfilerActivity.CPU,
                            torch.profiler.ProfilerActivity.CUDA],
                record_shapes=False, profile_memory=False, with_stack=False) as prof:
            with torch.inference_mode():
                for _ in range(a.controls):
                    with torch.profiler.record_function('MOD4/env_step'):
                        env.step(action)
                wp.synchronize()

        rows = []
        for item in prof.key_averages():
            rows.append(dict(name=item.key, count=item.count,
                self_cpu_us=item.self_cpu_time_total, cpu_us=item.cpu_time_total,
                self_device_us=item.self_device_time_total,
                device_us=item.device_time_total))
        rows.sort(key=lambda x:x['self_cpu_us'], reverse=True)
        table = prof.key_averages().table(sort_by='self_cpu_time_total', row_limit=35)
        (a.output/'CPU_TABLE.txt').write_text(table, encoding='utf8')
        trace = a.output/'TRACE.json'
        prof.export_chrome_trace(str(trace))
        data = env.plant.solver.mjw_data
        report.update(passed=True, GPU=torch.cuda.get_device_name(),
            CUDA_driver=wp.get_cuda_driver_version(),
            graph_conditional=env.plant.solver.mjw_model.opt.graph_conditional,
            physical_ticks=env.physics_ticks,
            numerical_resets=int(env.numerical_reset_counts.sum()),
            solver_niter=data.solver_niter.numpy().tolist(),
            overflow=data.overflow.numpy().tolist(),
            rows=rows,
            interpretation='Small local batch diagnostic; profiler changes timing and GPU differs from production RTX4090',
            trace=dict(path=str(trace), bytes=trace.stat().st_size,
                SHA=hashlib.sha256(trace.read_bytes()).hexdigest()))
        print(table)
    except BaseException:
        report['error'] = traceback.format_exc()
    finally:
        for obj, name, original in reversed(originals):
            setattr(obj, name, original)
        if env is not None:
            env.close()
        (a.output/'RESULT.json').write_text(json.dumps(report, indent=2), encoding='utf8')
        print(json.dumps({k:v for k,v in report.items() if k not in ('rows','solver_niter','overflow')}))
    if not report['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
