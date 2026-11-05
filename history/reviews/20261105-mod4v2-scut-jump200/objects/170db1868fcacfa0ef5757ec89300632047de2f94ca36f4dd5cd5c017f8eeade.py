"""Bounded real local full-step timing, without production policy or SSH."""
from pathlib import Path
import argparse,json,sys,time,traceback
import torch,warp as wp
N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
sys.path.insert(0,str(G/'project/isaac'))
from mod4v2_scut.newton_env import NewtonEnv
from mod4v2_scut.newton_sampling import install_state_read
p=argparse.ArgumentParser();p.add_argument('--output',default='sampling_state_fullstep03')
a=p.parse_args();R=N/a.output;R.mkdir(exist_ok=False)
out=dict(epoch=time.time(),passed=False,production_PT_reads=0,SSH=0,
    active_run_modified=False,envs=128,measurements={})
env=None
try:
    torch.manual_seed(9140)
    env=NewtonEnv('F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package',
        N.parents[1]/'workspace/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/payload/job0/runtime/isaac/mod4',
        N/'runtime_refs/runtime/isaac/mod4/reset_bank.json',128,'cuda:0',9140)
    action=torch.zeros(128,6,device=env.device)
    original=env.update_data
    # Alternate order to expose warm-up/drift instead of timing two cold runs.
    for label in ('torch','fused','fused','torch'):
        # The original method rebinds env.data tensor fields. Reinstall the
        # fused reader after that method, so its output buffers remain the
        # very tensors consumed by the task, rather than stale hidden outputs.
        if label=='fused':install_state_read(env)
        else:env.update_data=original
        env.reset(torch.arange(env.num_envs,device=env.device))
        for _ in range(4):env.step(action)
        wp.synchronize();start=time.perf_counter()
        for _ in range(8):env.step(action)
        wp.synchronize();seconds=time.perf_counter()-start
        out['measurements'].setdefault(label,[]).append(seconds)
    a=out['measurements'];ratio=sum(a['torch'])/sum(a['fused'])
    out.update(passed=True,controls_per_measurement=8,local_fullstep_ratio=ratio,
        physical_ticks=env.physics_ticks,numerical_resets=int(env.numerical_reset_counts.sum()),
        constraint_resets=int(env.constraint_reset_counts.sum()),GPU=torch.cuda.get_device_name(),
        production_20k_speedup_claim=False,stage_scope='Only state-read dispatch changed',
        pointer_rebinding_benchmark_repaired=True,
        prior_invalid_benchmark=str(N/'sampling_state_fullstep03/RESULT.json'))
except BaseException:out['error']=traceback.format_exc()
finally:
    if env is not None:env.close()
with(R/'RESULT.json').open('x',encoding='utf8')as f:json.dump(out,f,indent=2)
print(json.dumps(out))
if not out['passed']:raise SystemExit(1)
