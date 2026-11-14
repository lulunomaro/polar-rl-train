"""Render recorded MuJoCo states; do not rerun or modify the learned policy."""
import argparse
import hashlib
import json
from pathlib import Path
import time

import imageio.v2 as imageio
import mujoco
import numpy as np
from PIL import Image,ImageDraw,ImageFont

T=Path(__file__).resolve().parent
R=T.parents[2]
parser=argparse.ArgumentParser()
parser.add_argument('--run',required=True)
parser.add_argument('--case',required=True)
a=parser.parse_args()
case=T/'evidence'/a.run/a.case
result=json.loads((case/'RESULT.json').read_bytes())
scene=T/'evidence'/a.run/'map_cache'/('single_'+result['terrain']+'.xml')
if not scene.exists():scene=R/'sources/local/MOD4V3_FORWARD_JUMP_MANUAL_20261114/map_cache'/('single_'+result['terrain']+'.xml')
trace=np.load(case/'trajectory.npz',allow_pickle=False)
model=mujoco.MjModel.from_xml_path(str(scene))
data=mujoco.MjData(model)
model.vis.headlight.active=1
model.vis.headlight.ambient[:]=(.65,.65,.65)
model.vis.headlight.diffuse[:]=(.8,.8,.8)
camera=mujoco.MjvCamera()
camera.azimuth=100.
camera.elevation=-14.
camera.distance=1.8
camera.lookat[:]=[result['step_edge_x_m']-.05,0.,.35]
option=mujoco.MjvOption()
option.geomgroup[3]=0;option.geomgroup[5]=0
renderer=mujoco.Renderer(model,height=540,width=960)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
labels=['DRIVE','CROUCH','PUSH','FLIGHT','LAND']
request=float(result['request_time_s'])
indices=np.flatnonzero((trace['t']>=request-.7)&(trace['t']<=request+3.7))[::2]
images=[]
try:
    for index in indices:
        data.qpos[:]=trace['qpos'][index]
        data.qvel[:]=trace['qvel'][index]
        data.time=float(trace['t'][index])
        mujoco.mj_forward(model,data)
        renderer.update_scene(data,camera=camera,scene_option=option)
        pixels=renderer.render().copy()
        assert float(pixels.std())>3.,'Blank rendering'
        image=Image.fromarray(pixels)
        draw=ImageDraw.Draw(image)
        draw.rectangle((0,0,960,69),fill=(247,249,249))
        elapsed=float(trace['t'][index])-request
        title=f"MuJoCo | {a.case} | {result['step_height_m']*100:.0f} cm step | pass: {result['accepted']}"
        draw.text((14,8),title,font=font,fill=(24,32,36))
        tops=trace['top'][index].astype(int).tolist()
        detail=f"Space {elapsed:+.2f} s | {labels[int(trace['phase'][index])]} | top contacts L/R {tops} | stable {trace['stable_hold'][index]:.2f} s"
        draw.text((14,39),detail,font=small,fill=(40,53,58))
        draw.rectangle((0,510,960,540),fill=(247,249,249))
        rim=float(trace['wheels'][index,:,2].min()-.0625)
        draw.text((14,516),f"Lower wheel rim above approach floor {rim*100:.1f} cm | vx {trace['vx'][index]:.2f} m/s | recorded actual physics",font=small,fill=(35,48,53))
        images.append(image)
finally:renderer.close()
output=case/'attempt.mp4'
with imageio.get_writer(output,fps=25,codec='libx264',quality=8,macro_block_size=None) as writer:
    for image in images:writer.append_data(np.asarray(image))
key_indices=np.linspace(0,len(images)-1,6,dtype=int)
sheet=Image.new('RGB',(1440,600),(246,248,248))
for number,index in enumerate(key_indices):
    image=images[index].resize((480,270),Image.Resampling.LANCZOS)
    x=(number%3)*480;y=(number//3)*300
    sheet.paste(image,(x,y))
    draw=ImageDraw.Draw(sheet)
    elapsed=float(trace['t'][indices[index]])-request
    draw.text((x+10,y+275),f"Space {elapsed:+.2f} s",font=small,fill=(35,48,53))
sheet_path=case/'keyframes.png'
sheet.save(sheet_path)
report=dict(epoch=time.time(),source_trajectory=str(case/'trajectory.npz'),scene=str(scene),
            source_trajectory_sha256=hashlib.sha256((case/'trajectory.npz').read_bytes()).hexdigest(),
            video=str(output),keyframes=str(sheet_path),frames=len(images),fps=25,
            actual_recorded_MuJoCo_states=True,new_physics_steps=0,policy_or_dynamics_changed=False,
            nonblank_pixels_checked=True,result=result['accepted'])
(case/'RENDER.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,indent=2))
