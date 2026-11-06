"""One bounded local collect+H32 attribution; no production PT or SSH."""
from pathlib import Path
import argparse,hashlib,json,random,sys,time,traceback
import numpy as np
import torch
N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
sys.path.insert(0,str(G/'project/isaac'))
from mod4v2_scut.newton_env import NewtonEnv
from mod4v2_scut.config import runner_config
from mod4v2_scut.newton_checkpoint import environment_state,FORMAT
from mod4v2_scut.supermimic_train import build

p=argparse.ArgumentParser();p.add_argument('--output',required=True)
p.add_argument('--num-envs',type=int,default=128)
a=p.parse_args();R=N/a.output;R.mkdir(exist_ok=False)
out=dict(epoch=time.time(),production_PT_reads=0,SSH=0,active_modified=False,passed=False)
env=bridge=None
try:
    from rsl_rl.runners import OnPolicyRunner
    random.seed(9188);np.random.seed(9188);torch.manual_seed(9188)
    env=NewtonEnv('F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package',
        N.parents[1]/'workspace/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/payload/job0/runtime/isaac/mod4',
        N/'runtime_refs/runtime/isaac/mod4/reset_bank.json',a.num_envs,'cuda:0',9188)
    runner=OnPolicyRunner(env,runner_config(),None,env.device)
    source=dict(**runner.alg.save(),**environment_state(env),format=FORMAT,
        reward_family='FUDAN_JUMP',num_envs=a.num_envs,iter=0,
        cpu_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all(),
        python_rng=random.getstate(),numpy_rng=np.random.get_state())
    learner,bridge=build(env,source,G/'project/isaac/mod4v2_scut/SUPERMIMIC_BINDINGS.json',R/'learner',residual_scale=.25)
    del source,runner
    learner.collect(64)
    def round():
        with torch.profiler.record_function('TOTAL/collect3'):learner.collect(3)
        with torch.profiler.record_function('TOTAL/WM4_aux4'):
            for _ in range(4):learner.wm_update()
        with torch.profiler.record_function('TOTAL/H32_critic4'):learner.policy_update()
    round();torch.cuda.synchronize()
    start=time.perf_counter();round();torch.cuda.synchronize()
    out['unprofiled_round_seconds']=time.perf_counter()-start
    out['unprofiled_samples_per_second']=3*a.num_envs/out['unprofiled_round_seconds']
    for obj,name in [(learner.buffer,'add'),(learner.buffer,'_batch'),
                     (env,'step'),(env,'closure_errors'),(env,'update_data'),
                     (env,'sample_feedback'),(env.acceptance,'update_world'),
                     (learner,'aux_update')]:
        original=getattr(obj,name)
        def wrap(*args,_fn=original,_label=name,**kwargs):
            with torch.profiler.record_function('DETAIL/'+_label):return _fn(*args,**kwargs)
        setattr(obj,name,wrap)
    with torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CPU,
            torch.profiler.ProfilerActivity.CUDA])as prof:round();torch.cuda.synchronize()
    rows=[]
    for v in prof.key_averages():
        rows.append(dict(name=v.key,count=v.count,cpu_us=v.cpu_time_total,
            self_cpu_us=v.self_cpu_time_total,device_us=v.device_time_total,
            self_device_us=v.self_device_time_total))
    out.update(passed=True,num_envs=a.num_envs,GPU=torch.cuda.get_device_name(),
        production_hidden_dimensions=True,full32_H32_receipt=learner.last_bptt_receipt,
        four_WM_four_aux_four_critic=True,rows=rows,
        numerical_resets=int(env.numerical_reset_counts.sum()),constraint_resets=int(env.constraint_reset_counts.sum()))
    prof.export_chrome_trace(str(R/'TRACE.json'))
    with(R/'TRACE.json').open('rb')as f:out['trace']=dict(path=str(R/'TRACE.json'),bytes=(R/'TRACE.json').stat().st_size,SHA=hashlib.file_digest(f,'sha256').hexdigest())
except BaseException:out['error']=traceback.format_exc()
finally:
    if bridge is not None:bridge.close()
    if env is not None:env.close()
    (R/'RESULT.json').write_text(json.dumps(out,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in out.items()if k!='rows'}))
if not out['passed']:raise SystemExit(1)
