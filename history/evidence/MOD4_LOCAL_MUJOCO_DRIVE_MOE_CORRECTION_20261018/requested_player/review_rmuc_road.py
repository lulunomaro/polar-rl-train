"""Verify local CAD road geometry and observe the unchanged actor on it."""
from pathlib import Path
import hashlib,json,time,xml.etree.ElementTree as ET
import mujoco,numpy as np
from current_sim import CurrentSim
D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    old=ET.parse(D/'original_mild_playground/playground.xml').getroot()
    new=ET.parse(D/'playground.xml').getroot()
    for a,b in [(old.find('worldbody/body'),new.find('worldbody/body'))]+[(old.find(k),new.find(k)) for k in ['option','actuator','equality']]:
        assert ET.tostring(a)==ET.tostring(b),'Robot, actuator, solver or constraints changed'
    s=CurrentSim();params=s.parameter_readback()
    hf=mujoco.mj_name2id(s.model,mujoco.mjtObj.mjOBJ_HFIELD,'rmuc2026_road')
    gid=mujoco.mj_name2id(s.model,mujoco.mjtObj.mjOBJ_GEOM,'rmuc2026_ripple_lane')
    field=np.load(D/'terrain.npz')['rmuc2026_road']
    errors=[];hits=[];expected_heights=[]
    for iy in (10,50,100,150,190):
        for ix in range(8,633,13):
            p=np.array([1.+ix*.005,-1.+iy*.01,1.]);out=np.zeros(1,dtype=np.int32)
            distance=mujoco.mj_ray(s.model,s.data,p,np.array([0.,0.,-1.]),None,True,-1,out)
            expected=float(field[iy,ix]*s.model.hfield_size[hf,2])
            errors.append(abs(1.-distance-expected));hits.append(int(out[0]));expected_heights.append(expected)
    assert max(errors)<1e-6,max(errors)
    assert all(h==gid for h,z in zip(hits,expected_heights) if z>1e-6)
    cases=[]
    for speed in (.3,.5):
        s.reset(.3,0.,0.);start=s.base_position.copy();begin=time.perf_counter();minup=1.;minz=1.;fault=None;departure=None;max_lateral=0.
        for i in range(1800):
            s.command.vx=speed*min(1.,i/80);s.command.wz=0.;s.step_control()
            health=s.health();minup=min(minup,health['upright_cos']);minz=min(minz,float(s.base_position[2]))
            max_lateral=max(max_lateral,abs(float(s.base_position[1])))
            if not health['finite'] or minup<.60 or minz<.12:
                fault='fallen, low chassis or non-finite';break
            if abs(s.base_position[1])>1. and s.base_position[0]<4.45:
                departure=dict(control_step=i+1,xyz_m=s.base_position.tolist());break
            if s.base_position[0]>4.45:break
        item=dict(command_vx_m_s=speed,control_steps=i+1,sim_seconds=float(s.data.time),wall_seconds=time.perf_counter()-begin,
                  displacement_m=(s.base_position-start).tolist(),end_xyz_m=s.base_position.tolist(),
                  traversed_road_inside_lane=bool(s.base_position[0]>4.45 and departure is None),lateral_departure=departure,
                  maximum_lateral_offset_m=max_lateral,minimum_upright_cos=minup,minimum_root_z_m=minz,
                  fault=fault,health=s.health())
        cases.append(item);print(json.dumps(item),flush=True)
    report=dict(epoch=time.time(),parameter_readback=params,robot_actuator_solver_constraints_unchanged=True,
                checkpoint_sha256=sha(D/'model_30900.pt'),onnx_sha256=sha(D/'model_30900.onnx'),
                terrain_npz_sha256=sha(D/'terrain.npz'),mujoco_ray_samples=len(errors),max_geometry_ray_error_m=max(errors),
                cases=cases,scope='Local nominal MuJoCo observation only. Preserves actual failures; not Isaac or RM graduation.')
    (D/'RMUC_ROAD_SMOKE_REVIEW.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    # Render the actual MuJoCo heightfield, rather than a schematic wave.
    with mujoco.Renderer(s.model,height=600,width=1000) as renderer:
        s.reset(.3,0.,0.)
        cam=mujoco.MjvCamera();cam.type=mujoco.mjtCamera.mjCAMERA_FREE
        cam.lookat[:]=[2.6,0.,.05];cam.distance=4.7;cam.azimuth=105;cam.elevation=-35
        renderer.update_scene(s.data,camera=cam)
        from PIL import Image
        Image.fromarray(renderer.render()).save(D/'RMUC_ROAD_PREVIEW.png')
if __name__=='__main__':main()
