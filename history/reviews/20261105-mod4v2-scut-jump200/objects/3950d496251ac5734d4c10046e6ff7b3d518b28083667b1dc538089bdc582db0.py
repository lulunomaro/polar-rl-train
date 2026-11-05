"""Bounded candidate solver diagnosis with a single actual final881 read."""
from pathlib import Path
import argparse,hashlib,json,sys,time,traceback
import numpy as np
import torch,warp as wp

N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
sys.path.insert(0,str(G/'project/isaac'))
from mod4v2_scut.newton_env import NewtonEnv
from mod4v2_scut.config import runner_config
from rsl_rl.runners import OnPolicyRunner

p=argparse.ArgumentParser();p.add_argument('--ls',type=int,required=True);p.add_argument('--iterations',type=int,default=32)
p.add_argument('--controls',type=int,default=80)
p.add_argument('--output',required=True);a=p.parse_args()
R=N/a.output;R.mkdir(exist_ok=False)
A=N/'newton_fudan_final620_1h/episode_reset04'
ck=json.loads((A/'reports/FORMAL_TRANSFERS.json').read_bytes())['files'][0]
out=dict(epoch=time.time(),kind='FINAL881_SAMESEED_SOLVER_LINESSEARCH_CANDIDATE',
    production_PT_reads=1,production_unchanged=True,SSH=0,ls_iterations=a.ls,passed=False)
env=None
try:
    torch.manual_seed(9137);np.random.seed(9137)
    env=NewtonEnv('F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package',
        N.parents[1]/'workspace/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/payload/job0/runtime/isaac/mod4',
        N/'runtime_refs/runtime/isaac/mod4/reset_bank.json',80,'cuda:0',9137)
    env.solver.mjw_model.opt.ls_iterations=a.ls
    env.solver.mjw_model.opt.iterations=a.iterations
    env.solver.mjw_model.opt.graph_conditional=False
    env.solver.mj_model.opt.ls_iterations=a.ls
    env.solver.mj_model.opt.iterations=a.iterations
    runner=OnPolicyRunner(env,runner_config(),None,env.device)
    with Path(ck['local_path']).open('rb')as f:assert hashlib.file_digest(f,'sha256').hexdigest()==ck['SHA']
    saved=torch.load(ck['local_path'],map_location='cpu',weights_only=False)
    runner.alg.actor.load_state_dict(saved['actor_state_dict']);actor=runner.alg.actor.eval();del saved
    rows=[];peak=dict(closure=0.,mimic=0.,root_speed=0.)
    active=torch.ones(80,dtype=torch.bool,device=env.device)
    def observe(e):
        c,m=e.closure_errors()
        peak['closure']=max(peak['closure'],float(c[active].max())if active.any()else 0.)
        peak['mimic']=max(peak['mimic'],float(m[active].max())if active.any()else 0.)
        peak['root_speed']=max(peak['root_speed'],float(e.data.root_lin_vel_w[active].abs().max())if active.any()else 0.)
    env.physics_observer=observe
    with torch.inference_mode():
        obs=env.get_observations()
        for i in range(a.controls):
            obs,reward,done,info=env.step(actor(obs))
            ended=done&active
            for k in ended.nonzero().flatten().tolist():
                rows.append(dict(env=k,control=i+1,**{x:v[k].cpu().tolist()for x,v in env.terminal_snapshot.items()}))
            active&=~done
    out.update(passed=True,controls=a.controls,first_episode_terminations=rows,active_remaining=int(active.sum()),
        peak=peak,numerical_resets=int(env.numerical_reset_counts.sum()),
        constraint_resets=int(env.constraint_reset_counts.sum()),
        overflow=env.solver_overflow_summary(),physical_dt=.0025,
        solver_iterations=env.solver.mj_model.opt.iterations,
        candidate_is_qualification_not_new_training=True)
except BaseException:out['error']=traceback.format_exc()
finally:
    if env is not None:env.close()
    with(R/'RESULT.json').open('x',encoding='utf8')as f:json.dump(out,f,indent=2)
    print(json.dumps(out))
if not out['passed']:raise SystemExit(1)
