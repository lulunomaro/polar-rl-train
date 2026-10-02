"""Native MuJoCo viewer. --motion shows an analytic articulation audit, not a learned gait."""
from pathlib import Path
import argparse,time
import numpy as np
import mujoco
import mujoco.viewer
from kinematics import set_configuration

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--motion',action='store_true');ap.add_argument('--model');args=ap.parse_args()
    m=mujoco.MjModel.from_xml_path(str(args.model or Path(__file__).resolve().parent/'scene.xml'));d=mujoco.MjData(m)
    with mujoco.viewer.launch_passive(m,d) as v:
        v.opt.geomgroup[3]=0;v.opt.sitegroup[:]=0
        v.cam.lookat[:]=[0,0,.26];v.cam.distance=1.35;v.cam.azimuth=130;v.cam.elevation=-18
        start=time.perf_counter()
        while v.is_running():
            tic=time.perf_counter()
            if args.motion:
                t=tic-start;pose=(.12*np.sin(t),.10*np.sin(t*1.3))
                set_configuration(m,d,left=pose,right=pose)
                for s in ['left','right']:d.qpos[m.joint(s+'_wheel_spin').qposadr[0]]=3*t
                mujoco.mj_forward(m,d)
                z=min(d.site_xpos[m.site(s+'_wheel_center').id,2] for s in ['left','right'])
                d.qpos[2]+=.0645-z;mujoco.mj_forward(m,d)
                interval=.01
            else:
                mujoco.mj_step(m,d,nstep=20);interval=m.opt.timestep*20
            v.sync();time.sleep(max(0,interval-(time.perf_counter()-tic)))

if __name__=='__main__':main()
