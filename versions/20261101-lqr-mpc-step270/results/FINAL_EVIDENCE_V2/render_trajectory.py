"""Render stored physical states only; no policy inference or dynamics replay."""
import os,json,argparse,subprocess,numpy as np,mujoco
from pathlib import Path
from control_core import ROOT,make_model

def main():
    a=argparse.ArgumentParser();a.add_argument('--case',default='cross_trace_v1');a.add_argument('--out',default='rendered_cross_v1');args=a.parse_args()
    src=ROOT/'results'/args.case;out=ROOT/'results'/args.out;out.mkdir(exist_ok=False)
    rows=json.load(open(src/'trajectory.json'));m=make_model(True);d=mujoco.MjData(m)
    renderer=mujoco.Renderer(m,height=600,width=960);cam=mujoco.MjvCamera();cam.azimuth=95;cam.elevation=-12;cam.distance=1.5
    frames=[];selected=[]
    from PIL import Image,ImageDraw
    for i,row in enumerate(rows):
        d.qpos[:]=row['qpos'];d.qvel[:]=row['qvel'];mujoco.mj_forward(m,d)
        cam.lookat[:]=[np.clip(d.qpos[0],-.3,.6),0,.36]
        renderer.update_scene(d,camera=cam);image=Image.fromarray(renderer.render());draw=ImageDraw.Draw(image)
        draw.rectangle((0,0,960,35),fill='black');draw.text((10,10),f"MOD4 400N | 270mm step | t={row['time']:.2f}s | {row['phase']} | support={row['tops']}",fill='white')
        frames.append(image)
        if abs(row['time']-.95)<.015 or abs(row['time']-1.09)<.015 or abs(row['time']-1.3)<.015:
            fn=out/f"frame_{i:04d}.png";image.save(fn);selected.append(str(fn))
    frames[0].save(out/'trajectory.gif',save_all=True,append_images=frames[1:],duration=20,loop=0)
    print(json.dumps({'frames':len(frames),'gif':str(out/'trajectory.gif'),'selected':selected}),flush=True)
    renderer.close()
if __name__=='__main__':main()
