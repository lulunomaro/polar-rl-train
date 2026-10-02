"""PPO training entry point; --steps 4096 is an interface/optimizer smoke test."""
from pathlib import Path
import argparse,json,time,hashlib
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.vec_env import DummyVecEnv,VecMonitor
from stable_baselines3.common.callbacks import CheckpointCallback
from robomaster_env import RoboMasterEnv

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--steps',type=int,default=1_000_000)
    ap.add_argument('--envs',type=int,default=4)
    ap.add_argument('--seed',type=int,default=42)
    ap.add_argument('--velocity',type=float,default=0.)
    ap.add_argument('--output',default='runs/ppo')
    ap.add_argument('--randomize',action='store_true')
    ap.add_argument('--model',help='Path to a training MJCF; defaults to scene_training.xml beside this script')
    ap.add_argument('--resume',help='Resume from a saved PPO policy.zip')
    ap.add_argument('--checkpoint-every',type=int,default=100000)
    args=ap.parse_args()
    if args.steps<1 or args.envs<1 or args.checkpoint_every<1:ap.error('steps, envs and checkpoint-every must be positive')
    import torch
    torch.set_num_threads(1)
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    check=RoboMasterEnv(model_path=args.model);check_env(check,warn=True);check.close()
    def make():return RoboMasterEnv(command_velocity=args.velocity,domain_randomization=args.randomize,model_path=args.model)
    env=VecMonitor(DummyVecEnv([make for _ in range(args.envs)]),filename=str(out/'episodes'))
    model=PPO.load(args.resume,env=env,device='cpu') if args.resume else PPO('MlpPolicy',env,n_steps=256,batch_size=256,n_epochs=5,learning_rate=3e-4,
              gamma=.99,gae_lambda=.95,clip_range=.2,ent_coef=.005,verbose=1,seed=args.seed,
              device='cpu',policy_kwargs={'net_arch':[128,128]})
    before=[p.detach().cpu().numpy().copy() for p in model.policy.parameters()]
    initial_timesteps=model.num_timesteps;initial_epochs=model._n_updates
    optimizer_count={'steps':0}
    def counted_step(optimizer,step_args,step_kwargs):optimizer_count['steps']+=1
    hook=model.policy.optimizer.register_step_post_hook(counted_step)
    checkpoint=CheckpointCallback(save_freq=max(1,args.checkpoint_every//args.envs),save_path=str(out/'checkpoints'),name_prefix='ppo')
    tic=time.perf_counter()
    try:model.learn(total_timesteps=args.steps,callback=checkpoint,reset_num_timesteps=not bool(args.resume))
    except KeyboardInterrupt:
        model.save(out/'interrupted_policy');env.close();raise
    model.save(out/'policy')
    hook.remove()
    after=[p.detach().cpu().numpy() for p in model.policy.parameters()]
    assert all(np.isfinite(p).all() for p in after),'Optimizer produced non-finite parameters'
    changed=any(np.max(abs(a-b))>0 for a,b in zip(after,before))
    assert changed,'Policy did not update'
    evaluation=make();obs,_=evaluation.reset(seed=123)
    max_error=0.;total_reward=0.;numerical_failures=0;episodes=0
    for _ in range(1000):
        action,_=model.predict(obs,deterministic=True)
        obs,reward,done,trunc,info=evaluation.step(action)
        max_error=max(max_error,info['closure_error_m']);numerical_failures+=info['numerical_failure'];total_reward+=reward
        if done or trunc:episodes+=1;obs,_=evaluation.reset()
    model_path=Path(args.model or Path(__file__).resolve().parent/'scene_training.xml').resolve()
    result={'model':str(model_path),'model_sha256':hashlib.sha256(model_path.read_bytes()).hexdigest(),
            'environment_count':args.envs,'domain_randomization':args.randomize,'command_velocity':args.velocity,
            'requested_steps':args.steps,'actual_steps':model.num_timesteps-initial_timesteps,
            'optimizer_updates':optimizer_count['steps'],'training_epochs':model._n_updates-initial_epochs,
            'environment_execution':'DummyVecEnv: synchronous serial stepping on CPU, not parallel PhysX environments',
            'policy_parameters_updated':changed,'elapsed_s':time.perf_counter()-tic,'seed':args.seed,
            'evaluation_steps':1000,'evaluation_episodes':episodes,'evaluation_return_sum':total_reward,
            'evaluation_max_closure_error_m':max_error,'numerical_failures':numerical_failures,
            'note':'A short run verifies RL data flow and optimizer updates; it does not establish a converged balancing policy.'}
    (out/'training_report.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2));evaluation.close();env.close()

if __name__=='__main__':main()
