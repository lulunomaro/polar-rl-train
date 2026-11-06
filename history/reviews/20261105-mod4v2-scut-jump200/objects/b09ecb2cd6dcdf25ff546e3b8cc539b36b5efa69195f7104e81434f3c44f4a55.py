"""Same-state Newton sampling parity, including invalid400Hz endpoints."""
from pathlib import Path
from types import SimpleNamespace
import json,sys,time,traceback
import torch
N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
sys.path.insert(0,str(G/'project/isaac'))
from mod4v2_scut.newton_env import NewtonEnv
from mod4v2_scut.newton_sampling import install_sampling
from mod4v2_scut.jump200 import Jump200Acceptance
from mod4v2_scut.warp_tests import reward_check,acceptance_check
R=N/'sampling_fusion_parity06';R.mkdir(exist_ok=False)
out=dict(epoch=time.time(),passed=False,production_PT_reads=0,SSH=0,maximum_closure_error=0.)
env=None
try:
    out['existing_reward']=reward_check('cuda:0',False)
    out['existing_acceptance']=acceptance_check('cuda:0',False)
    env=NewtonEnv('F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package',
        N.parents[1]/'workspace/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/payload/job0/runtime/isaac/mod4',
        N/'runtime_refs/runtime/isaac/mod4/reset_bank.json',4,'cuda:0',9191)
    original_closure=env.closure_errors;original_reward=env.reward.compute
    out['installation']=install_sampling(env)
    fused_closure=env.closure_errors;fused_reward=env.reward.compute
    old_accept=Jump200Acceptance(4,'cuda:0')
    count=[0]
    def closure():
        expected=original_closure();actual=fused_closure()
        for a,b in zip(actual,expected):
            out['maximum_closure_error']=max(out['maximum_closure_error'],float((a-b).abs().max()))
            torch.testing.assert_close(a,b,atol=1e-6,rtol=2e-5)
        count[0]+=1
        return actual
    env.closure_errors=closure
    fused_accept=env.acceptance.update_world
    def accept(*args):
        for key,value in vars(env.acceptance).items():
            if torch.is_tensor(value):setattr(old_accept,key,value.clone())
        expected=old_accept.update_world(*args)
        fused_accept(*args)
        for key,value in vars(old_accept).items():
            if torch.is_tensor(value):torch.testing.assert_close(getattr(env.acceptance,key),value,equal_nan=True)
    env.acceptance.update_world=accept
    # Compare real reward on identical inputs and restore its state before the
    # fused call; no second physics transition and no altered labels.
    state_names=('fudan_last_contacts','fudan_contact_filt','fudan_was_in_flight',
        'fudan_base_air_time','fudan_leg_length','fudan_leg_theta')
    def reward():
        r=env.reward
        fields={key:getattr(r,key).clone()for key in state_names}
        sums={k:v.clone()for k,v in r._episode_sums.items()}
        command={k:v.clone()for k,v in vars(env.command).items()if torch.is_tensor(v)}
        cpu=torch.get_rng_state();cuda=torch.cuda.get_rng_state()
        expected=original_reward().clone()
        raw={k:v.clone()for k,v in r.raw_terms.items()}
        terms={k:v.clone()for k,v in r._last_reward_terms.items()}
        for key,v in fields.items():getattr(r,key).copy_(v)
        for key,v in sums.items():r._episode_sums[key].copy_(v)
        for key,v in command.items():getattr(env.command,key).copy_(v)
        r.command=env.command.command.clone()
        torch.set_rng_state(cpu);torch.cuda.set_rng_state(cuda)
        actual=fused_reward()
        torch.testing.assert_close(actual,expected,atol=3e-6,rtol=3e-5)
        for key,v in terms.items():torch.testing.assert_close(r._last_reward_terms[key],v,atol=3e-6,rtol=3e-5)
        for key,v in raw.items():torch.testing.assert_close(r.raw_terms[key],v,atol=3e-5,rtol=3e-5)
        return actual
    env.reward.compute=reward
    for i in range(12):env.step(torch.zeros(4,6,device='cuda:0'))
    # An invalid world must not accumulate a ground/takeoff/landing event.
    valid=torch.tensor([True,False,True,False],device='cuda:0')
    d=env.data
    for _ in range(4):
        accept(d.body_pos_w[:,env.wheel_bodies],d.body_quat_w[:,env.wheel_bodies],
            env.contract,env.scene.env_origins,env.top_force,env.ground_force,
            env.net_force[:,env.wheel_bodies],env.net_force[:,env.reward._nonwheel_contact_link_idx].norm(dim=-1).amax(-1),
            d.root_lin_vel_w,d.root_quat_w,valid)
    out.update(passed=True,closure_checks=count[0],real_physics_ticks=env.physics_ticks,
        all16_terms_same=True,all_acceptance_counters_same=True,invalid_mask_preserved=True)
except BaseException:out['error']=traceback.format_exc()
finally:
    if env is not None:env.close()
    (R/'RESULT.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out))
if not out['passed']:raise SystemExit(1)
