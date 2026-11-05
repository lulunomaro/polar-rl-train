from pathlib import Path
import argparse,json,sys,time,traceback
import torch,warp as wp
import mujoco_warp as mjw
N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
sys.path.insert(0,str(G/'project/isaac'))
from mod4v2_scut.newton_env import NewtonEnv
from mod4v2_scut.config import runner_config
from rsl_rl.runners import OnPolicyRunner
p=argparse.ArgumentParser();p.add_argument('--report',required=True);a=p.parse_args()
out=dict(epoch=time.time(),production_PT_reads=0,passed=False)
env=None
try:
 env=NewtonEnv('F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package',
    N.parents[1]/'workspace/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/payload/job0/runtime/isaac/mod4',
    N/'runtime_refs/runtime/isaac/mod4/reset_bank.json',4,'cuda:0',66)
 runner=OnPolicyRunner(env,runner_config(),None,'cuda:0');obs=env.get_observations()
 assert env.get_observations() is obs
 runner.alg.train_mode();grads=dict(steps=0)
 def gradient(*args):
  grads['steps']+=1
  for label,model in [('actor',runner.alg.actor),('critic',runner.alg.critic)]:
   vals=[x.grad.norm().square() for x in model.parameters() if x.grad is not None]
   grads[label]=float(torch.stack(vals).sum().sqrt())
 runner.alg.optimizer.register_step_pre_hook(gradient)
 start=time.time()
 with torch.inference_mode():
  for _ in range(24):
   action=runner.alg.act(obs);obs,r,d,info=env.step(action)
   assert env.get_observations() is obs
   assert torch.isfinite(obs['policy']).all()and torch.isfinite(obs['critic']).all()
   runner.alg.process_env_step(obs,r,d,info)
  runner.alg.compute_returns(obs)
 losses=runner.alg.update();wp.synchronize()
 ce,me=env.closure_errors()
 overflow=env.solver_overflow_summary()
 assert not(env.solver.mjw_model.opt.warn_overflow & mjw.OverflowType.LS_ITERATIONS)
 current=wp.to_torch(env.solver.mjw_data.overflow)
 assert torch.equal(env.solver_overflow_latched.bitwise_or(current),env.solver_overflow_latched)
 assert grads['steps']==20 and grads['actor']>0 and grads['critic']>0
 assert ce.max()<.01 and me.max()<.01
 out.update(passed=True,controls=24,physics_ticks=env.physics_ticks,gradient=grads,
            losses={k:float(v)for k,v in losses.items()},seconds=time.time()-start,
            closure_max=float(ce.max()),mimic_max=float(me.max()),
            solver_overflow_world_masks=overflow,
            LS_warning_device_print_disabled=True,LS_overflow_bits_still_checked=True,
            command_time_left=env.command.time_left.tolist(),
            gas_stiffness=wp.to_torch(env.model.mujoco.dof_passive_stiffness).reshape(4,-1)[:,env.vadr[env.gas]].tolist())
except BaseException:out['error']=traceback.format_exc()
finally:
 if env is not None:env.close()
 with Path(a.report).open('x',encoding='utf8')as f:json.dump(out,f,indent=2)
 print(json.dumps(out))
if not out['passed']:raise SystemExit(1)
