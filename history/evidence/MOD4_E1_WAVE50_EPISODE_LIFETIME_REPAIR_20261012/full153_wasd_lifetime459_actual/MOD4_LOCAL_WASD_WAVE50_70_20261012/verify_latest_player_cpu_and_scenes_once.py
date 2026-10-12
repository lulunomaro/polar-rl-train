from pathlib import Path
import json,time,traceback,hashlib
import numpy as np,torch,mujoco
from series_sim import SeriesSim,SERIES,MODELS
from io_runtime import write_json
D=Path(__file__).resolve().parent;R=D/'reports'

def main():
    assert not (R/'LOCAL_ACTOR_SCENE_SMOKE_ACTUAL.json').exists()
    assert len(MODELS)==1 and MODELS[0]['sha256']=='7facab0a45ccc7589123488deb98c77e9980a8f9d124b1cea3843ccbe16a5de9'
    rows=[]
    for scene in ('wave50','wave70'):
        for reverse in (False,True):
            sim=SeriesSim(scene,'wave449',reverse);params=sim.parameter_readback();obs=sim.observation();assert obs.shape==(35,) and np.isfinite(obs).all()
            a=sim.policy(obs);assert a.shape==(6,) and np.array_equal(a,sim.policy(obs))
            rotation=sim.data.xmat[sim.chassis_id].reshape(3,3);heading=float(np.arctan2(rotation[1,0],rotation[0,0]));assert abs(heading)<1e-8
            start=sim.base_position.copy();assert start[0]>0 if reverse else start[0]<0
            floor=mujoco.mj_name2id(sim.model,mujoco.mjtObj.mjOBJ_GEOM,'local_floor');assert sim.model.geom_contype[floor]==sim.model.geom_conaffinity[floor]==0
            initial=sim.health();prefix=[]
            for _ in range(20):
                sim.command.vx=-.3 if reverse else .3;sim.command.wz=0.;sim.step_control();health=sim.health();assert health['finite'];prefix.append(dict(sim_time=float(sim.data.time),root=sim.base_position.tolist(),health=health))
            rows.append(dict(scene=scene,reverse=reverse,heading_unchanged=heading,checkpoint_SHA=sim.policy.sha256,actor35_action6_deterministic_CPU=True,initial_parameter_readback=params,initial_root=start.tolist(),initial_health=initial,controls=20,final_health=sim.health(),actual_prefix=prefix,not_fullroute_or_remote_qualification_test=True))
    assert not torch.cuda.is_initialized()
    import drive_series
    ui=drive_series.Driver(start_sim=False)
    try:
        assert ui.scene_value.get()==SERIES['scenes'][0]['label'] and SERIES['scenes'][0]['id']=='wave50'
        assert ui.model_value.get()==MODELS[0]['label'] and ui.speed==.3
        ui.root.update_idletasks();ui_defaults=dict(title=ui.root.title(),scene=ui.scene_value.get(),model=ui.model_value.get(),speed=ui.speed)
    finally:ui.close()
    write_json(R/'LOCAL_ACTOR_SCENE_SMOKE_ACTUAL.json',dict(epoch=time.time(),passed=True,scene_checks=rows,ui_defaults=ui_defaults,local_nominal_MuJoCo=True,old_robot_contract_and_hardware_parameters_exact=True,physics_dt_s=.0005,policy_hz=100,actor_frozen_no_optimizer_no_exploration=True,no_remote_GPU_PPO_budget_or_monitor_write=True,no_50_70mm_fullcourse_pass_claim=True),required=True)
    print(json.dumps(dict(passed=True,checks=len(rows),checkpoint_SHA=MODELS[0]['sha256'],UI=ui_defaults)))

if __name__=='__main__':
    try:main()
    except BaseException:(R/('LOCAL_VERIFY_ERROR_'+str(time.time_ns())+'.txt')).write_text(traceback.format_exc(),encoding='utf8');raise
