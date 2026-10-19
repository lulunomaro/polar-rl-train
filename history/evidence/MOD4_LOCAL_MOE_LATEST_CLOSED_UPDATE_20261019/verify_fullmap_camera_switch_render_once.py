"""Exercise both actual passive-viewer camera modes against the full map."""
from pathlib import Path
import json,sys,time,traceback
import mujoco,mujoco.viewer
B=Path(__file__).resolve().parent;D=B.parent/'MOD4_LOCAL_MUJOCO_DRIVE_20261008'
sys.path.insert(0,str(D))
from rm7v7_moe_sim import RM7V7MoESim
from player_camera import set_player_camera

def main():
    report=B/'reports/FULLMAP_CAMERA_SWITCH_RENDER_ACTUAL.json';assert not report.exists()
    sim=RM7V7MoESim();switches=[]
    with mujoco.viewer.launch_passive(sim.model,sim.data,show_left_ui=False,show_right_ui=False) as viewer:
        for i in range(100):
            overview=bool(i%2);set_player_camera(viewer,sim.chassis_id,overview)
            with viewer.lock():
                assert viewer.cam.trackbodyid==sim.chassis_id and 0<=viewer.cam.trackbodyid<sim.model.nbody
                assert viewer.cam.type==(mujoco.mjtCamera.mjCAMERA_FREE if overview else mujoco.mjtCamera.mjCAMERA_TRACKING)
                switches.append(dict(index=i,overview=overview,type=int(viewer.cam.type),trackbodyid=viewer.cam.trackbodyid))
            viewer.sync();time.sleep(.05);assert viewer.is_running()
        assert sim.health()['finite'] and sim.data.time==0
    result=dict(epoch=time.time(),status='PASS',full_original_RM7V7_model=True,actual_passive_viewer_render=True,
        consecutive_camera_switches=len(switches),camera_states=switches,physics_steps=0,
        source_bundle=sim.policy.path.name,chassis_id=sim.chassis_id,nbody=sim.model.nbody,
        no_training_or_policy_or_physics_change=True,not_a_skill_qualification=True)
    with report.open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps({k:v for k,v in result.items() if k!='camera_states'}))
if __name__=='__main__':
    try:main()
    except BaseException:
        with (B/'reports'/('CAMERA_RENDER_CHECK_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc()),f,indent=2)
        raise
