"""Real native2048-env full-DR admission and frozen all-height parent replay."""
import time,torch,os,json
from pathlib import Path
from tensordict import TensorDict
from isaaclab.utils.warp import raycast_mesh
from .single_step_math import SPEC,COURSE

def run_probe(env,algorithm):
    start=time.time();algorithm.eval_mode();before={k:v.detach().clone()for k,v in algorithm.actor.state_dict().items()}
    mask=env.continuous_stair_mask;ids=mask.nonzero().flatten()
    assert int(mask.sum())==819 and int(env.flat_terrain_mask.sum())==512
    assert env.course_mastered[ids].eq(0).all()and env.course_level[ids].eq(0).all()
    # Query actual cooked collision mesh at each bank level, including lower/upper sides.
    t=env.terrain;column=int(t.terrain_types[ids[0]])
    centers=t.terrain_origins[:9,column]
    starts=centers.repeat_interleave(2,0).clone();starts[:,2]+=2.;starts[1::2,0]+=2.
    direction=torch.zeros_like(starts);direction[:,2]=-1.
    hits=raycast_mesh(starts,direction,t.r1_wp_mesh,max_dist=5.)[0]
    assert torch.isfinite(hits).all()
    actual=(hits[::2,2]-hits[1::2,2]);expected=actual.new_tensor(SPEC.heights)
    assert torch.allclose(actual,expected,atol=1e-5),(actual,expected)
    env.course_accounting=False;env.course_evaluation=True
    # Exercise actual initial5cm population with the same stochastic actor used by PPO.
    env.reset();env.begin_training_counts();obs=TensorDict(env._get_observations(),batch_size=[env.num_envs]);policy=algorithm.get_policy()
    max_closure=0.;max_reward=0.
    for step in range(300):
        with torch.inference_mode():
            action=policy(obs,stochastic_output=True);raw,reward,term,timeout,_=env.step(action)
        assert torch.isfinite(reward).all()
        assert raw['policy'].shape==(env.num_envs,35)and raw['critic'].shape==(env.num_envs,78)
        assert not bool(raw['teacher_keep'][mask].any())and bool((raw['teacher_keep'][~mask]>.5).all())
        obs=TensorDict(raw,batch_size=[env.num_envs]);max_closure=max(max_closure,float(env.closure_error.max()));max_reward=max(max_reward,float(reward.abs().max()))
        if bool((env.closure_error>.002).any())or bool(env.numeric.any()):
            bad=((env.closure_error>.002)|env.numeric).nonzero().flatten()
            records=[]
            for i in bad.tolist():
                records.append(dict(env=i,nominal=bool(env.full_dr.nominal_env_mask[i]),curriculum=bool(mask[i]),family=int(env.terrain_family[i]),level=int(env.terrain.terrain_levels[i]),closure=float(env.closure_error[i]),numerical=bool(env.numeric[i]),root_pos=env.snapshots['root_pos'][i].tolist(),velocity=env.snapshots['velocity'][i].tolist(),length=env.snapshots['length'][i].tolist(),theta=env.snapshots['theta'][i].tolist(),command=env.snapshots['command'][i].tolist(),reset_mode=int(env.reset_modes[i])))
            (Path(os.environ['MOD4V1_E0_JOB_ROOT'])/'FIRST_PHYSICS_FAULT.json').write_text(json.dumps(dict(step=step,records=records,done_totals=dict(env.done_totals)),indent=2)+'\n')
            raise RuntimeError('First closure/numerical fault; preserve diagnosis and reject admission')
    unchanged=all(torch.equal(before[k],v)for k,v in algorithm.actor.state_dict().items())
    assert unchanged and env.enforce_closure_reset and env.cfg.decimation==8
    assert float(env.reward.cfg.rewards['track_lin_vel_xy_square'])==-1.5 and float(env.reward.cfg.lin_vel_xy_square_sigma)==1.
    assert env.course_mastered[ids].eq(0).all(),'Frozen probe advanced mastery'
    (Path(os.environ['MOD4V1_E0_JOB_ROOT'])/'PROBE_ROLLOUT.json').write_text(json.dumps(dict(steps=300,maximum_measured_closure_m=max_closure,done_totals=dict(env.done_totals),course=env.terrain_summary()['single_step_curriculum']),indent=2)+'\n')
    assert max_closure<=.002 and env.done_totals['closure']==0,'2mm closure guard fired; solver admission rejected'
    state=env.terrain_checkpoint_state();assert state['course']==COURSE
    env.course_accounting=False;env.course_mastered[ids[0]]=2
    state=env.terrain_checkpoint_state();env.course_mastered[ids[0]]=0
    with torch.inference_mode():restored=env.restore_terrain_curriculum(state)
    assert restored['counters_restored']and int(env.course_mastered[ids[0]])==2
    return dict(passed=True,no_optimizer_updates=True,actor_identical=unchanged,num_envs=env.num_envs,steps=300,wall_seconds=time.time()-start,actual_collision_heights_m=actual.tolist(),initial_training_population_all5cm=True,initial5cm_stochastic_probe_frozen_no_promotion=True,checkpoint_roundtrip_passed=True,teacher_excludes_all819_stair_envs=True,teacher_retains_all1229_other_envs=True,maximum_measured_closure_m=max_closure,closure_episode_guard_m=.002,maximum_abs_reward=max_reward,done_totals=dict(env.done_totals),course=env.terrain_summary()['single_step_curriculum'],physics_dt_s=env.physics_dt,policy_dt_s=env.step_dt,full_DR=env.mild_dr.summary(),guard_not_relaxed=True)
