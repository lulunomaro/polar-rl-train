"""Render actual 400 Hz trajectories at 25 fps (1x), retaining failed outcomes."""
from nav_common import HERE,put
from pathlib import Path
import argparse
import json
import math
import numpy as np
import mujoco as mj
from PIL import Image,ImageDraw
import imageio.v2 as imageio
from nav4d_runtime import Nav4DPolicy,Nav4DSimulation
from eval_stair_nav4d import run_case,cases
from eval_jump_all_regimes import run_jump

class Recorder:
    def __init__(self,path,label):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        self.writer=imageio.get_writer(self.path,fps=25,codec='libx264',quality=8,macro_block_size=16)
        self.renderer=None;self.counter=0;self.frames=0;self.label=label
    def __call__(self,sim,measurement):
        self.counter+=1
        if self.counter%16:return
        if self.renderer is None:self.renderer=mj.Renderer(sim.m,height=720,width=1280)
        option=mj.MjvOption();option.geomgroup[4]=1
        option.geomgroup[3]=0 if sim.scene_meta['course']=='suite_rmul2027' else 1
        if sim.scene_meta.get('hide_group5'):option.geomgroup[5]=0
        camera=mj.MjvCamera();camera.type=mj.mjtCamera.mjCAMERA_FREE
        camera.lookat[:]=[sim.d.qpos[0]+.35,sim.d.qpos[1],sim.d.qpos[2]+.10]
        camera.distance=3.4;camera.azimuth=135.;camera.elevation=-22.
        self.renderer.update_scene(sim.d,camera=camera,scene_option=option)
        image=Image.fromarray(self.renderer.render().copy());draw=ImageDraw.Draw(image)
        draw.rectangle((0,0,1280,70),fill=(14,23,32))
        draw.text((18,12),self.label,fill=(123,230,214))
        draw.text((18,35),f't={sim.d.time:.2f}s  v={measurement["vx"]:+.2f}m/s  pitch={math.degrees(measurement["pitch"]):+.1f}deg  g={np.round(sim.last_g,2)}',fill=(230,238,244))
        self.writer.append_data(np.asarray(image));self.frames+=1
    def close(self):
        self.writer.close()
        if self.renderer is not None:self.renderer.close()
        return dict(path=str(self.path),frames=self.frames,fps=25,physics_hz=400,video_speed=1.,duration_s=self.frames/25.)

def arenas():
    folder=HERE/'media';folder.mkdir(exist_ok=True);result=[]
    for course,lookat,distance,elevation in [('suite_rmul2027',[0.,0.,.1],14.,-63.),('suite_rmuc2027',[-11.2,-4.9,.2],26.,-65.)]:
        sim=Nav4DSimulation(Nav4DPolicy());sim.load_scene(course)
        option=mj.MjvOption();option.geomgroup[4]=1;option.geomgroup[3]=int(course!='suite_rmul2027')
        if sim.scene_meta.get('hide_group5'):option.geomgroup[5]=0
        cam=mj.MjvCamera();cam.lookat[:]=lookat;cam.distance=distance;cam.azimuth=120.;cam.elevation=elevation
        with mj.Renderer(sim.m,height=900,width=1440) as renderer:
            renderer.update_scene(sim.d,camera=cam,scene_option=option)
            path=folder/(course+'_arena.png');Image.fromarray(renderer.render()).save(path)
            result.append(str(path))
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--stair',type=Path);p.add_argument('--jump',type=Path);p.add_argument('--arenas-only',action='store_true')
    p.add_argument('--part',choices=('all','stairs','jumps'),default='all');a=p.parse_args()
    report=HERE/'evidence/VIDEO_VERIFICATION.json'
    result=json.loads(report.read_text(encoding='utf-8')) if report.exists() and a.part!='all' else {}
    if a.part=='all' or 'arena_images' not in result:result['arena_images']=arenas()
    if not a.arenas_only and a.part in ('all','stairs'):
        selected=[next(c for c in cases('screen') if c['course']=='suite_rmul2027'),next(c for c in cases('screen') if c['course']=='step_20'),
                  next(c for c in cases('screen') if c['course']=='suite_rmuc2027')]
        result['stairs']=[]
        for case in selected:
            recorder=Recorder(HERE/'media'/(case['course']+'_stairs_1X.mp4'),case['course']+' raw nav4d / 1x')
            outcome,_=run_case(case,a.stair,a.jump,record=recorder)
            result['stairs'].append(dict(outcome=outcome,video=recorder.close()))
    if not a.arenas_only and a.part in ('all','jumps'):
        result['jumps']=[]
        for h,v,release in [(.42,0.,True),(.28,.6,True),(.39,2.2,True)]:
            case=dict(height=h,c=True,speed=v,release=release,hold_ticks=5)
            recorder=Recorder(HERE/'media'/f'jump_h{h}_v{v}_release_1X.mp4','Raw unified jump / release W / 1x')
            outcome,_=run_jump(case,a.jump,record=recorder)
            result['jumps'].append(dict(outcome=outcome,video=recorder.close()))
    put(HERE/'evidence/VIDEO_VERIFICATION.json',result)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
