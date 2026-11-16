"""Nominal MuJoCo analogue of repaired native ordinary contact/orientation rules."""
from pathlib import Path
import json,time,os
import numpy as np
import mujoco
from replay_guards import policy_step_without_flat_reset,pose_state


def contact_state(sim):
    e=sim.env;m=e.m;d=e.d
    if not hasattr(sim,'_repair_body_ids'):
        wheels=[m.body(n).id for n in ('left_wheel_link','right_wheel_link')]
        guides=sorted({int(m.geom_bodyid[i]) for i in range(m.ngeom) if m.geom(i).name.startswith('guide_wheel_')})
        assert len(guides)==8,'Expected the unchanged eight MOD4 guide rollers'
        sim._repair_body_ids=(int(e.base_id),guides,wheels)
    chassis,guides,wheels=sim._repair_body_ids
    forces=np.zeros((m.nbody,3));local=np.zeros(6)
    for i in range(d.ncon):
        c=d.contact[i];mujoco.mj_contactForce(m,d,i,local)
        world=np.asarray(c.frame).reshape(3,3).T@local[:3]
        forces[int(m.geom_bodyid[c.geom1])]-=world
        forces[int(m.geom_bodyid[c.geom2])]+=world
    positions=d.xpos[wheels];x=np.abs(positions[:,0]);y=np.abs(positions[:,1]);supported=forces[wheels,2]>5.
    stage=getattr(sim,'_repair_stair_stage',0)
    if bool(((x>1.42)&(x<2.88)&(y<2.88)&(np.abs(positions[:,2]-.2625)<.05)&supported).all()):stage=max(stage,1)
    if bool(((x<1.38)&(y<1.38)&(np.abs(positions[:,2]-.4625)<.05)&supported).all()):stage=2
    sim._repair_stair_stage=stage
    wide=sim.family in (sim._repair_wide_families if hasattr(sim,'_repair_wide_families') else ('low_speed_stair_for_rm','high_speed_stair_for_rm'))
    heights=np.unique(sim.vertices[:,2])
    two200mm=bool(len(heights)==3 and np.allclose(heights,[0.,.2,.4],atol=1e-5))
    edge=2.9 if stage==0 else 1.4
    allowed=bool(wide and sim.direction=='up' and two200mm and stage<2 and np.min(np.abs(x-edge))<.45)
    chassis_force=float(np.linalg.norm(forces[chassis]));guide_force=float(np.max(np.linalg.norm(forces[guides],axis=1)))
    return dict(chassis_contact_force_N=chassis_force,guide_contact_force_max_N=guide_force,
                guide_contact_allowed=allowed,stair_landing_stage=stage,
                contact_bad=bool(chassis_force>1. or (guide_force>1. and not allowed)))


def replay_step(simulation,safety_stop,*,duration_steps=10,event_dir=None):
    advance=policy_step_without_flat_reset(simulation)
    dest=Path(event_dir) if event_dir is not None else None
    if dest is not None:dest.mkdir(parents=True,exist_ok=True)
    def reset(sim,reason,state=None):
        if state is None:state=pose_state(sim)
        sim.reason=reason
        event=dict(epoch=time.time(),reason=reason,contact_counter=getattr(sim,'_repair_contact_steps',0),orientation_counter=getattr(sim,'_replay_tilt_steps',0),duration_steps=duration_steps,**state)
        sim.last_guard_reset=event;print('MANUAL_GUARD_RESET '+json.dumps(event,ensure_ascii=False),flush=True)
        if dest is not None:(dest/(str(time.time_ns())+'_'+str(os.getpid())+'.json')).write_text(json.dumps(event,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        sim.reset_standing();sim._repair_contact_steps=0;sim._replay_tilt_steps=0;sim._repair_stair_stage=0
        return sim.telemetry()
    def step(sim,pressed):
        if sim.paused:return sim.telemetry()
        now=float(sim.env.d.time)
        if now<=getattr(sim,'_replay_last_time',-1.):sim._repair_contact_steps=0;sim._replay_tilt_steps=0;sim._repair_stair_stage=0
        sim.just_reset=False
        try:advance(sim,pressed)
        except safety_stop as exc:return reset(sim,str(exc))
        state=pose_state(sim);state.update(contact_state(sim));sim._replay_last_time=state['simulation_time_s']
        sim.z=state['height_above_wheel_ground'];sim.cos_tilt=state['cos_tilt'];sim.last_contact_state=state
        tilted=abs(state['pitch_deg'])>40. or abs(state['roll_deg'])>40.
        sim._replay_tilt_steps=getattr(sim,'_replay_tilt_steps',0)+1 if tilted else 0
        sim._repair_contact_steps=getattr(sim,'_repair_contact_steps',0)+1 if state['contact_bad'] else 0
        if sim._repair_contact_steps>=duration_steps:return reset(sim,'chassis_or_nonexempt_guide_contact_for_0.2s',state)
        if sim._replay_tilt_steps>=duration_steps:return reset(sim,'roll_or_pitch>40deg_for_0.2s',state)
        if state['root_xyz'][2]<sim.ground(0.,0.)-1.:return reset(sim,'fell_below_terrain_origin_minus1m',state)
        if abs(state['root_xyz'][0])>4.1 or abs(state['root_xyz'][1])>4.1:return reset(sim,'tile_boundary',state)
        return sim.telemetry()
    return step
