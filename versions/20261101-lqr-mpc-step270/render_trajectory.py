"""Render stored physical states only; no policy inference or dynamics replay."""
import os,json,argparse,subprocess,numpy as np,mujoco
from pathlib import Path
from control_core import ROOT,make_model

def main():
    a=argparse.ArgumentParser();a.add_argument('--case',default='cross_trace_v1');a.add_argument('--out',default='rendered_cross_v1');args=a.parse_args()
    src=ROOT/'results'/args.case;out=ROOT/'results'/args.out;out.mkdir(exist_ok=False)
    rows=json.load(open(src/'trajectory.json'));m=make_model(True)
    result=json.load(open(src/'result.json'))
    if result.get('config',{}).get('full_dr'):
        from dr_components import FullDR
        FullDR(result['config']['seed']).sample(m)
    d=mujoco.MjData(m)
    renderer=mujoco.Renderer(m,height=600,width=960);cam=mujoco.MjvCamera();cam.azimuth=95;cam.elevation=-12;cam.distance=1.5
    frames=[];selected=[]
    from PIL import Image,ImageDraw
    stride=max(1,int(round(.02/(rows[1]['time']-rows[0]['time'])))) if len(rows)>1 else 1
    display_rows=rows[::stride]
    for i,row in enumerate(display_rows):
        d.qpos[:]=row['qpos'];d.qvel[:]=row['qvel'];mujoco.mj_forward(m,d)
        cam.lookat[:]=[np.clip(d.qpos[0],-.3,.6),0,.36]
        renderer.update_scene(d,camera=cam);image=Image.fromarray(renderer.render());draw=ImageDraw.Draw(image)
        draw.rectangle((0,0,960,35),fill='black');tag=('fullDR seed='+str(result['config']['seed'])) if result['config'].get('full_dr') else 'nominal';controller='MPC' if result['config'].get('mpc') else 'LQR';draw.text((10,10),f"MOD4 400N | 270mm | {controller} {tag} | t={row['time']:.2f}s | {row['phase']} | supports={row['tops']}",fill='white')
        frames.append(image)
        if any(abs(row['time']-t)<.015 for t in [.65,.95,1.09,1.3,2.8,4.8]):
            fn=out/f"frame_{i:04d}.png";image.save(fn);selected.append(str(fn))
    frame_ms=max(10,int(round((display_rows[1]['time']-display_rows[0]['time'])*1000))) if len(display_rows)>1 else 20
    frames[0].save(out/'trajectory.gif',save_all=True,append_images=frames[1:],duration=frame_ms,loop=0)
    print(json.dumps({'frames':len(frames),'gif':str(out/'trajectory.gif'),'selected':selected}),flush=True)
    renderer.close()
if __name__=='__main__':main()
