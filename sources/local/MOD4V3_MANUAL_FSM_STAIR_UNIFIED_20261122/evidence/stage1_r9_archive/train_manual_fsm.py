"""600-step zero-update precheck or guarded dedicated 2048-env stair PPO."""
from argparse import ArgumentParser
import json
import os
from pathlib import Path
import random
import sys
import time
import traceback
from fsm_io import put, sha256
from fsm_geometry import PHYSICS_DT, POLICY_SUBSTEPS, physx_tire_geometry

def main():
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('job',type=Path)
    parser.add_argument('--seconds',type=int,default=0)
    parser.add_argument('--lr',type=float,default=5.e-5)
    parser.add_argument('--dr-exposure-schedule',action='store_true')
    args=parser.parse_args()
    if args.seconds < 0 or args.seconds > 2400:
        parser.error('Each round has an explicit 0..2400 second bound')
    root=Path(__file__).resolve().parent
    job=args.job.resolve()
    job.mkdir()
    app=env=None
    error=None
    try:
        inputs=json.loads((root/'INPUTS.json').read_text())
        for name,digest in inputs.items():
            if sha256(root/name)!=digest:
                raise ValueError(f'Input SHA mismatch: {name}')
        dep=root/'dependencies'
        plant=root/'plant'
        sources=json.loads((dep/'SOURCE_PATHS.relative.json').read_text())
        put(job/'source_paths.json',{k:str(dep/v) for k,v in sources.items()})
        storage=job/'kit_isolation'
        (storage/'data').mkdir(parents=True)
        (storage/'DerivedDataCache').mkdir()
        (storage/'data/user.config.json').write_text('{}')
        os.environ.update(MOD4V1_E0_JOB_ROOT=str(job),MOD4V1_E0_KIT_STORAGE_ROOT=str(storage),
            MOD4_SCUT_SOURCE_PATHS=str(job/'source_paths.json'),OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y',
            WARP_CACHE_PATH=str(root/'cache/warp'),JOINT_FRICTION_SCALE='1',SPRING_DAMPING_FRACTION='1',
            EXTERNAL_DR_FRACTION='1',OBS_NOISE_FRACTION='1',PHYSICAL_DELAY_QUANTUM_MS='5',
            PHYSICAL_ACTION_DELAY_MIN_MS='5',PHYSICAL_ACTION_DELAY_MAX_MS='10',
            PHYSICAL_SENSOR_DELAY_MIN_MS='5',PHYSICAL_SENSOR_DELAY_MAX_MS='15',PYTHONDONTWRITEBYTECODE='1')
        sys.path[:0]=[str(dep/'launcher'),str(dep/'package'),str(plant),str(root/'support')]
        from launcher_mod4v1_e0 import IsolatedAppLauncher208
        app=IsolatedAppLauncher208(dict(headless=True,device='cuda:0',enable_cameras=False)).app
        import numpy as np
        import torch
        from tensordict import TensorDict
        from rsl_rl.algorithms import PPO
        from rsl_rl.models import MLPModel
        from rsl_rl.runners import OnPolicyRunner
        from mod4v1_scut.config import runner_config
        from mod4v3_ppo_v1.model import metadata,reset_bank
        from mod4v3_ppo_v1.scut_flat_env import configuration,tensor
        from fsm_isaac_env import FSMStairEnv,install_course,COURSES
        from manual_fsm_model import StairExpert,SymmetricE0,mirror_obs,mirror_action
        from manual_fsm_core import ManualFSM,DetectorConfig,Phase

        class ActorModel(MLPModel):
            def __init__(self,*parameters,**options):
                super().__init__(*parameters,**options)
                self.mlp=StairExpert()

        class MaskedStairPPO(PPO):
            warmup_only=False
            def update(self):
                means=dict(value=0.,surrogate=0.,entropy=0.,anchor=0.,active_fraction=0.)
                for batch in self.storage.mini_batch_generator(self.num_mini_batches,self.num_learning_epochs):
                    values=self.critic(batch.observations)
                    loss_v=(values-batch.returns).square().mean()
                    mask=batch.observations['stair_active'].float().reshape(-1)
                    count=mask.sum().clamp_min(1.)
                    if self.warmup_only:
                        loss_s=entropy=anchor=loss_v.new_zeros(())
                        loss=2.*loss_v
                    else:
                        self.actor(batch.observations,stochastic_output=True)
                        prob=self.actor.get_output_log_prob(batch.actions)
                        advantage=batch.advantages.squeeze(-1)
                        avg=(advantage*mask).sum()/count
                        std=(((advantage-avg).square()*mask).sum()/count+1.e-8).sqrt()
                        advantage=(advantage-avg)/std
                        ratio=(prob-batch.old_actions_log_prob.squeeze(-1)).exp()
                        loss_s=(torch.maximum(-advantage*ratio,-advantage*ratio.clamp(.90,1.10))*mask).sum()/count
                        entropy=(self.actor.output_entropy*mask).sum()/count
                        mean=self.actor.mlp(batch.observations['policy'])
                        with torch.no_grad():
                            prior=anchor_model(batch.observations['policy'])
                        anchor=((mean-prior).square().mean(-1)*mask).sum()/count
                        loss=loss_s+2.*loss_v-1.e-4*entropy+.035*anchor
                    self.optimizer.zero_grad()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(list(self.actor.parameters())+list(self.critic.parameters()),1.,error_if_nonfinite=True)
                    self.optimizer.step()
                    with torch.no_grad():
                        self.actor.distribution.std_param[:4].clamp_(.012,.065)
                        self.actor.distribution.std_param[4:].clamp_(.025,.11)
                    for key,value in zip(means,(loss_v,loss_s,entropy,anchor,mask.mean()),strict=True):
                        means[key]+=float(value.detach())
                self.storage.clear()
                return {k:v/(self.num_mini_batches*self.num_learning_epochs) for k,v in means.items()}

        seed=11222026
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        install_course()
        meta=metadata(plant)
        bank=reset_bank(plant,dep/'reset_bank.json')
        cfg_env=configuration(meta,bank,2048,seed,terrain_selection='rough_scut_v1')
        env=FSMStairEnv(cfg_env,meta,bank,physx_tire_geometry(plant),initial_dr=0.)
        env.render_enabled=False
        env.scene['contacts'].cfg.update_period=0.
        original_update=env.scene.update
        def sample(dt):
            original_update(dt)
            env.sample_physics(dt)
        env.scene.update=sample
        env.reset()
        fsm=ManualFSM(2048,env.device,DetectorConfig(**json.loads((root/'DETECTOR.json').read_text())['config']))
        pending=torch.ones(2048,dtype=torch.bool,device=env.device)
        history=torch.zeros(2048,12,35,device=env.device)
        last_climb=torch.zeros(2048,6,device=env.device)
        phase_counts=torch.zeros(6,dtype=torch.long,device=env.device)
        actor_control_frames=torch.zeros((),dtype=torch.long,device=env.device)
        premature_activation_frames=torch.zeros_like(actor_control_frames)
        riser_seen=torch.zeros(2048,dtype=torch.bool,device=env.device)
        native_trace=[]
        trace_ids=torch.arange(0,2048,16,device=env.device)
        def reset_fsm(ids):
            fsm.reset(ids)
            pending[ids]=True
            last_climb[ids]=0.
            riser_seen[ids]=False
        env.fsm_reset_callback=reset_fsm
        e0=SymmetricE0().load_e0(torch.load(root/'parent.pt',map_location=env.device,weights_only=False)).to(env.device).eval()
        if (root/'E0_CALIBRATION.json').is_file():
            e0.load_calibration(json.loads((root/'E0_CALIBRATION.json').read_text()))
        def observations(raw):
            frame=raw['policy'][:,:35].clone()
            frame[:,28:35]=frame.new_tensor([1.,0.,0.,0.,0.,0.,0.])
            forward=env.episode_length_buf>=env.runup_steps
            fsm.update(frame,mode=torch.ones_like(forward),forward=forward)
            frame[:,3]=fsm.height*5.
            env.fsm_phase.copy_(fsm.phase)
            env.course_height.copy_(fsm.height)
            history[:,:-1]=history[:,1:].clone()
            history[:,-1]=frame
            history[pending]=frame[pending,None]
            pending.zero_()
            # Phase and masks belong to rollout bookkeeping, never actor inputs.
            return TensorDict(dict(policy=torch.cat((frame,history.flatten(1)),-1),critic=raw['critic'],
                stair_active=(fsm.phase==Phase.STAIR_CLIMB_ACTIVE).clone()),batch_size=[2048])
        obs=observations(env._get_observations())
        class VectorEnv:
            num_envs=2048
            num_actions=6
            device=env.device
            max_episode_length=env.max_episode_length
            cfg=env.cfg
            episode_length_buf=env.episode_length_buf
            def get_observations(self):return obs
        cfg=runner_config()
        cfg.update(num_steps_per_env=24,clip_actions=6.)
        cfg['actor']['class_name']=ActorModel
        cfg['algorithm'].update(class_name=MaskedStairPPO,learning_rate=args.lr,schedule='fixed',clip_param=.1,
                                num_learning_epochs=3,value_loss_coef=2.,entropy_coef=1.e-4)
        alg=OnPolicyRunner(VectorEnv(),cfg,log_dir=None,device=env.device).alg
        initial=torch.load(root/'stair.pt',map_location=env.device,weights_only=False)
        alg.actor.mlp.load_state_dict(initial['stair'])
        base=torch.load(root/'parent.pt',map_location=env.device,weights_only=False)
        alg.critic.load_state_dict(initial.get('critic_state_dict',base['critic_state_dict']))
        with torch.no_grad():alg.actor.distribution.std_param.copy_(torch.tensor([.035]*4+[.065]*2,device=env.device))
        anchor_model=StairExpert().to(env.device).eval().requires_grad_(False)
        anchor_model.load_state_dict(initial['stair'])
        alg.optimizer=torch.optim.Adam([dict(params=alg.actor.parameters(),lr=args.lr),
                                        dict(params=alg.critic.parameters(),lr=2.e-4)])
        optimizer_steps=updates=0
        def count_step(*_):
            nonlocal optimizer_steps
            optimizer_steps+=1
        alg.optimizer.register_step_post_hook(count_step)
        initial_actor={k:v.clone() for k,v in alg.actor.state_dict().items()}
        initial_e0={k:v.clone() for k,v in e0.base.state_dict().items()}
        def dispatch(action):
            nonlocal actor_control_frames,premature_activation_frames
            w=fsm.stair_weight
            active=fsm.phase==Phase.STAIR_CLIMB_ACTIVE
            last_climb[active]=action[active]
            base_action=e0(obs['policy'][:,:35])
            chosen=torch.lerp(base_action,last_climb,w[:,None])
            phase_counts.scatter_add_(0,fsm.phase,torch.ones_like(fsm.phase))
            actor_control_frames+=active.sum()
            # Training-only truth audits routing; it cannot control dispatch.
            wheels=env.view.data.body_pos_w[:,env.wheel_body_ids]-env.centers[:,None]
            first=torch.where(env.double[:,None],
                (env.edge_offset+.70*wheels[...,1]).maximum(env.edge_min).minimum(env.second_edge-.31),
                torch.where((env.group==4)[:,None],env.edge_sign[:,None]*wheels[...,1]*.404026226,0.))
            pre=(first-wheels[...,0]).amin(1)>.40
            forces=tensor(env.scene['contacts'].data.net_forces_w)
            horizontal=torch.stack([(-forces[:,ids,0]-forces[:,ids,2].abs()).amax(1) for ids in env.contact_ids],1)
            face=(horizontal>5.).any(1)&((first-wheels[...,0]).amin(1)<.40)
            riser_seen.logical_or_(face)
            audited_pre=pre&~riser_seen
            premature_activation_frames+=(audited_pre&active).sum()
            if not args.seconds:
                native_trace.append(torch.cat((obs['policy'][trace_ids,:35],fsm.features[trace_ids],
                    fsm.phase[trace_ids,None].float(),audited_pre[trace_ids,None].float(),
                    face[trace_ids,None].float(),env.episode_length_buf[trace_ids,None].float()),1).cpu().numpy())
            return chosen.clamp(-6.,6.)
        def advance(action):
            nonlocal obs
            raw,reward,term,timeout,_=env.step(dispatch(action))
            if not all(bool(torch.isfinite(v).all()) for v in (*raw.values(),reward)):
                raise FloatingPointError('Nonfinite simulation output')
            obs=observations(raw)
            return reward,term,timeout
        put(job/'STARTUP.json',dict(envs=2048,seed=seed,physics_hz=400,policy_hz=50,leg_pd_hz=100,wheel_hz=400,
            input_obs=35,history=420,critic=78,actions=6,action_order=env.order,
            obstacle_replicas=int(env.obstacle.sum()),groups=torch.bincount(env.group,minlength=len(COURSES)).tolist(),
            detector_config=fsm.config.to_dict(),e0_sha256=inputs['parent.pt'],stair_parent_sha256=inputs['stair.pt'],
            nominal_sensors='unnoised standard obs35; targeted SDK reset-cache refresh',
            fsm_inputs='obs35 plus operator forward/mode; no simulator state',actor_loss='active-stair-only PPO',
            privileged_geometry_usage='reward, reset and offline audit only',seconds=args.seconds,
            critic_parent='stair checkpoint' if 'critic_state_dict' in initial else 'E0 checkpoint',
            dr_curriculum='scheduled exposure; no graduation claim' if args.dr_exposure_schedule else 'success-gated',
            aa_center_tread_m=1.20))
        if not args.seconds:
            count0=env.sample_count
            rays_finite=True
            with torch.inference_mode():
                for step in range(600):
                    a=alg.actor(obs)
                    exploration=(torch.arange(2048,device=env.device)%5<2)
                    a+=torch.randn_like(a)*alg.actor.distribution.std_param*exploration[:,None]
                    advance(a)
                    for key in ('ground','ground_left','ground_right'):
                        rays_finite &= bool(torch.isfinite(tensor(env.scene[key].data.ray_hits_w)).all())
                    if (step+1)%50==0:
                        put(job/'LATEST.json',dict(steps=step+1,phase_counts=phase_counts.tolist(),
                            completed=env.completed.tolist(),actor_control_frames=int(actor_control_frames)))
            # Zero optimizer calls: backward verifies learnability and finite gradients.
            alg.actor.zero_grad();alg.critic.zero_grad()
            (alg.actor(obs).square().mean()+alg.critic(obs).square().mean()).backward()
            grads=[p.grad for p in alg.actor.parameters() if p.grad is not None]
            gradient_finite=all(bool(torch.isfinite(g).all()) for g in grads)
            unchanged=all(torch.equal(initial_actor[k],v) for k,v in alg.actor.state_dict().items())
            frozen=all(torch.equal(initial_e0[k],v) for k,v in e0.base.state_dict().items())
            x=obs['policy'][:32]
            mx=torch.cat((mirror_obs(x[:,:35]),mirror_obs(x[:,35:].reshape(-1,12,35)).flatten(1)),-1)
            with torch.no_grad():
                symmetry_error=float((alg.actor.mlp(mx)-mirror_action(alg.actor.mlp(x))).abs().max())
            passed=(unchanged and frozen and gradient_finite and rays_finite and optimizer_steps==0
                    and env.sample_count-count0==600*POLICY_SUBSTEPS and symmetry_error<1.e-5
                    and int(env.obstacle.sum())==2048 and int(actor_control_frames)>0
                    and env.nominal_observation_error==0.)
            put(job/'PROBE.json',dict(passed=passed,steps=600,envs=2048,ppo_updates=0,optimizer_steps=optimizer_steps,
                actor_unchanged=unchanged,e0_unchanged=frozen,gradients_finite=gradient_finite,
                physics_samples=env.sample_count-count0,rays_finite=rays_finite,
                z2_max_error=symmetry_error,phase_counts=phase_counts.tolist(),
                nominal_observation_error=env.nominal_observation_error,
                removed_nominal_noise_peak=env.removed_nominal_noise_peak,
                reset_sensor_cache_stats=getattr(env,'reset_sensor_cache_stats',None),
                premature_activation_frames=int(premature_activation_frames),actor_control_frames=int(actor_control_frames),
                active_dr=int(env.full_dr.applied_dr.sum()),completed=env.completed.tolist()))
            np.savez_compressed(job/'NATIVE_CALIBRATION.npz',frames=np.stack(native_trace),
                env_ids=trace_ids.cpu().numpy(),course=env.group[trace_ids].cpu().numpy())
            if not passed:raise RuntimeError('Native precheck failed')
            return
        start=time.monotonic()
        epoch=time.time()
        deadline=start+args.seconds
        put(job/'TRAIN_START.json',dict(epoch=epoch,compute_stop_seconds=args.seconds,hard_stop_epoch=epoch+args.seconds+30))
        due=180
        def stats():
            return dict(ppo_updates=updates,optimizer_steps=optimizer_steps,elapsed_s=time.monotonic()-start,
                target_dr=env.target_dr,active_dr=int(env.full_dr.applied_dr.sum()),dr_promotions=env.dr_history,
                completed_by_course=dict(zip(COURSES,env.completed.tolist())),episode_counts=env.episode_counts.tolist(),
                deck_posture_reward_sum=float(env.posture_reward_sum),
                phase_counts=phase_counts.tolist(),actor_control_frames=int(actor_control_frames),
                premature_activation_frames=int(premature_activation_frames))
        def save(name):
            assert all(torch.equal(initial_e0[k],v) for k,v in e0.base.state_dict().items())
            path=job/name
            tmp=path.with_suffix('.partial')
            torch.save(dict(format='mod4v3_manual_fsm_stair_v1',stair=alg.actor.mlp.state_dict(),
                actor_state_dict=alg.actor.state_dict(),critic_state_dict=alg.critic.state_dict(),
                optimizer_state_dict=alg.optimizer.state_dict(),e0_sha256=inputs['parent.pt'],e0_unchanged=True,
                detector=fsm.config.to_dict(),inputs=inputs,**stats()),tmp)
            tmp.replace(path)
            put(path.with_suffix('.json'),dict(checkpoint=name,sha256=sha256(path),**stats()))
            return sha256(path)
        alg.train_mode()
        stop=job/'REQUEST_STOP'
        while time.monotonic()<deadline and not stop.exists():
            elapsed=time.monotonic()-start
            env.promote_dr(elapsed,elapsed/max(1.,args.seconds*.8) if args.dr_exposure_schedule else None)
            rollout=0
            with torch.inference_mode():
                for _ in range(24):
                    if time.monotonic()+1.5>=deadline or stop.exists():break
                    a=alg.act(obs)
                    reward,term,timeout=advance(a)
                    terminal=TensorDict(env.terminal_observations,batch_size=[2048])
                    reward=reward+alg.gamma*alg.critic(terminal).squeeze(-1)*timeout
                    alg.process_env_step(obs,reward,term|timeout,{})
                    rollout+=1
                if rollout==24:alg.compute_returns(obs)
            if rollout<24:break
            alg.warmup_only=updates<3
            losses=alg.update()
            updates+=1
            put(job/'LATEST.json',dict(**stats(),losses=losses,critic_warmup=alg.warmup_only))
            if updates in (1,4):save('model_first_complete.pt' if updates==1 else 'model_first_actor.pt')
            if time.monotonic()-start>=due:
                save(f'model_{due//60:03d}m.pt')
                due+=180
        digest=save('model_final.pt')
        put(job/'FINAL.json',dict(**stats(),sha256=digest,checkpoint='model_final.pt',
            end_reason='request' if stop.exists() else 'budget',unfinished_rollout_steps=rollout))
    except Exception:
        error=traceback.format_exc()
        (job/'ERROR.txt').write_text(error,encoding='utf-8')
        raise
    finally:
        scene_closed=False
        try:
            if env is not None:
                env.close()
                scene_closed=True
        finally:
            put(job/'SAFE_CLOSED.json',dict(epoch=time.time(),scene_closed=scene_closed,error=error))
            if app is not None:app.close()

if __name__=='__main__':main()
