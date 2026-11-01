"""New branch: frozen-E0 residual SuperMimic learns from real LQR task reference."""
import argparse,os,sys,json,time,hashlib,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parent;sys.path[:0]=[str(ROOT/'source'),str(ROOT/'source/sm_deps'),str(ROOT/'runtime/isaac/mod4'),str(ROOT/'runtime/isaac'),str(ROOT/'runtime')]
p=argparse.ArgumentParser();p.add_argument('--num-envs',type=int,default=2048);p.add_argument('--iterations',type=int,default=100000);p.add_argument('--hours',type=float,default=3.);p.add_argument('--run-name',default='supermimic_lqr_e0_v1');p.add_argument('--preflight',action='store_true');p.add_argument('--seed',type=int,default=20261101);a=p.parse_args()
out=ROOT/'runs'/a.run_name;out.mkdir(parents=True,exist_ok=False)
for k in list(os.environ):
    if k.startswith('RM_'):del os.environ[k]
original=json.load(open(ROOT/'frozen/original_run_manifest.json'))['env'];os.environ.update({k:str(v) for k,v in original.items() if k not in ['RM_RESCUE_STOP_FILE','RM_RESCUE_DEADLINE']})
os.environ['MOD4_RESUME_QUEUE_CONTROL_US']='20000'
os.environ.update(RM_MOD4_USD=str(ROOT/'runtime/assets/robot.usd'),RM_SPIN_STAGE='off',RM_PHYSICS_DT_S='.0025',RM_POLICY_HZ='50',RM_SOLVER_POS='32',RM_SOLVER_VEL='4',RM_EPISODE_S='5',RM_JUMP_SCRIPT_PROB='0')

def put(name,value):
    dst=out/name;tmp=dst.with_suffix(dst.suffix+'.partial');tmp.write_text(json.dumps(value,indent=2,allow_nan=False));tmp.replace(dst)

from isaaclab.app import AppLauncher
class OwnLauncher(AppLauncher):
    def _create_app(self):
        self._sim_app_config['enable_crashreporter']=False
        self._sim_app_config['extra_args']=['--/crashreporter/preserveDump=true','--/crashreporter/enabled=false','--/app/renderer/enabled=false','--/renderer/enabled=false','--/app/window/enabled=false']
        super()._create_app()
app=OwnLauncher(headless=True,device='cuda:0').app
env=None
try:
    import torch
    from step_env import LQRStepEnv,configure
    from mod4_task import Mod4EnvCfg
    from isaac_bridge import StepBridge
    from frozen_e0 import FrozenE0,E0ResidualPolicy
    from supermimic_vendor_v2.learner import SuperMimicLearner,SuperMimicConfig
    torch.set_num_threads(4);torch.manual_seed(a.seed)
    cfg=configure(Mod4EnvCfg(),a.num_envs,a.seed);env=LQRStepEnv(cfg=cfg)
    bridge=StepBridge(env,ROOT/'reference/lqr_step270_50hz.npz');bridge.init_state()
    binding=env.binding_receipt();assert binding['num_joints']==30 and binding['num_bodies']==31
    assert binding['physics_dt']==.0025 and binding['policy_dt']==.02
    # Source SDK root quaternion follows xyzw in this installed runtime; validate
    # the bridge quaternion against the official projected-gravity observation.
    from supermimic_vendor_v2.geometry import unflatten_state
    rotation=unflatten_state(bridge.pack())[1];actual_gravity=env.scene['robot'].data.projected_gravity_b
    if hasattr(actual_gravity,'to_torch'):actual_gravity=actual_gravity.to_torch()
    gerr=float(((-rotation[:,2,:])-actual_gravity).abs().max());assert gerr<1e-3,('quaternion convention',gerr)
    expert=FrozenE0(ROOT/'frozen/E0_frozen_a92c9e8d.pt',device='cuda:0');original_hash=expert.state_hash()
    class Learner(SuperMimicLearner):
        def _make_policy(self):return E0ResidualPolicy(super()._make_policy(),expert)
    smcfg=SuperMimicConfig(iterations=a.iterations,buffer_steps=256,utd=.4,horizon=16,goal_frames=5,hist=10,z_dim=32,wm_hidden=(512,512,512),policy_hidden=(512,256,128),critic_hidden=(256,128),wm_window=8,wm_batches=4,wm_batch=512,pi_batch=1024,lr=1e-4,action_noise=.08,warmup_steps=32,wm_only_iters=50,ckpt_every=100,log_every=10,log_backend='tensorboard',amp='bf16',compile=False,seed=a.seed)
    learner=Learner(bridge,smcfg,out/'learner',device='cuda:0',backend='IsaacLab_MOD4_E0_LQR_270')
    learner.opt_pi=torch.optim.Adam(learner.pi.trainable_parameters(),lr=smcfg.lr,betas=(.9,.95))
    trainable={id(x) for g in learner.opt_pi.param_groups for x in g['params']};assert all(id(x) not in trainable for x in expert.parameters())
    put('STARTUP.json',{'epoch':time.time(),'args':vars(a),'env':binding,'expert':expert.receipt(),'expert_state_hash':original_hash,'quaternion_gravity_max_error':gerr,'reference':json.load(open(ROOT/'reference/REFERENCE_RECEIPT.json')),'algorithm':'SuperMimic vendor v2 real WM replay + differentiable imagination actor/critic','new_residual_actor':True,'E0_optimizer_restored':False,'reference_is_only_goal_not_cross_engine_replay':True,'total_raw_action_clip':6,'preflight':a.preflight})
    if a.preflight:
        learner.collect(32);loss,err=learner.wm_update();learner.cfg.pi_batch=64;learner.cfg.horizon=4
        pi,v,imag,grad,surv=learner.policy_update();assert expert.state_hash()==original_hash
        for module in [learner.pi,learner.wm,learner.critic]:
            if module is not None:assert all(torch.isfinite(t).all() for t in module.parameters())
        put('PREFLIGHT.json',{'passed':True,'world_loss':float(loss),'world_last_error':float(err),'policy_loss':float(pi),'value_loss':float(v),'imagination_reward':float(imag),'policy_grad_norm':float(grad),'expert_hash_unchanged':True,'metrics':bridge.metrics()})
        print('PREFLIGHT_PASS '+json.dumps(bridge.metrics()),flush=True)
    else:
        started=time.time();deadline=started+a.hours*3600;wm_updates=0;pi_updates=0
        class StopAfterSave(Exception):pass
        original_wm=learner.wm_update;original_pi=learner.policy_update
        def wm_update():
            nonlocal_unused=None
            global wm_updates
            value=original_wm();wm_updates+=1;return value
        def pi_update():
            global pi_updates
            value=original_pi();pi_updates+=1;return value
        learner.wm_update=wm_update;learner.policy_update=pi_update
        def before_action():
            if time.time()>deadline or (out/'STOP_AFTER_SAVE').exists():raise StopAfterSave()
            if learner.iteration%10==0:
                progress={'epoch':time.time(),'iteration':learner.iteration,'world_updates':wm_updates,'policy_updates':pi_updates,'elapsed_s':time.time()-started,**bridge.metrics()};put('PROGRESS.json',progress)
        bridge.before_action=before_action
        try:result=learner.train()
        except StopAfterSave:result={'bounded_stop':True}
        finally:
            path=learner.save(out/'final.pt',include_optimizers=True);assert expert.state_hash()==original_hash
            put('FINAL.json',{'epoch':time.time(),'iteration':learner.iteration,'world_updates':wm_updates,'policy_updates':pi_updates,'expert_hash_unchanged':True,'checkpoint':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),**bridge.metrics()})
except BaseException:
    put('ERROR.json',{'epoch':time.time(),'error':traceback.format_exc()});raise
finally:
    try:
        if env is not None:env.close()
    finally:app.close()
