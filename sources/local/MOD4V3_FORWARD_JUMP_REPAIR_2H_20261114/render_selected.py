"""Visualize recorded native policy poses without integrating another simulator."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import imageio.v2 as imageio
import mujoco
import numpy as np
from PIL import Image,ImageDraw,ImageFont

T = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--outputs',required=True)
args = parser.parse_args()
output = Path(args.outputs)
summary = json.loads((T/'evidence/RESULTS_SUMMARY.json').read_bytes())
selected = summary['selected']
assert selected is not None
evidence = T/'evidence'/selected['job']
result = json.loads((evidence/'RESULT.json').read_bytes())
all_rows=result['episodes']
good=[row for row in all_rows if row['success'] and not row['terminated']]
nominal_good=[row for row in good if row['nominal']]
rows = nominal_good or good or [row for row in all_rows if row['nominal']]
row = max(rows,key=lambda item:(bool(item['success']) and not item['terminated'],bool(item['retracted']),bool(item['takeoff']),item['rim_peak'],-item['env']))
qualified = bool(row['success']) and not bool(row['terminated'])
group_label='Nominal' if row['nominal'] else 'FullDR'
index = row['env']
trace = np.load(evidence/'trajectory.npz')
names = trace['joint_names'].tolist()
model = mujoco.MjModel.from_xml_path(str((T/'native_package/mjcf/scene.xml').resolve()))
model.vis.headlight.active=1
model.vis.headlight.ambient[:]=(.65,.65,.65)
model.vis.headlight.diffuse[:]=(.75,.75,.75)
if model.nlight:
    model.light_ambient[:]=(.25,.25,.25)
    model.light_diffuse[:]=(.75,.75,.75)
for geom in range(model.ngeom):
    if model.geom_type[geom]==mujoco.mjtGeom.mjGEOM_PLANE:
        model.geom_matid[geom]=-1
        model.geom_rgba[geom]=(.82,.86,.85,1.)
data = mujoco.MjData(model)
addresses = [model.joint(name).qposadr[0] for name in names]
root_address = int(model.joint('root_joint').qposadr[0])
origin = trace['env_origins'][index]
done = np.flatnonzero(trace['done'][:,index])
end = int(done[0]) if len(done) else len(trace['done'])
assert end > 1
camera = mujoco.MjvCamera()
camera.azimuth = 112
camera.elevation = -16
camera.distance = 1.35
option = mujoco.MjvOption()
option.geomgroup[3] = 0
option.geomgroup[5] = 0
font_path = Path('C:/Windows/Fonts/arial.ttf')
font = ImageFont.truetype(str(font_path),20) if font_path.exists() else ImageFont.load_default()
small = ImageFont.truetype(str(font_path),16) if font_path.exists() else ImageFont.load_default()
labels = ['FORWARD','CROUCH','PUSH','FLIGHT','LAND / RECOVER']
renderer = mujoco.Renderer(model,height=540,width=960)
rendered_rims = []


def frame(step):
    mujoco.mj_resetData(model,data)
    root = trace['root_pos'][step,index]-origin
    data.qpos[root_address:root_address+3] = root
    data.qpos[root_address+3:root_address+7] = trace['root_quat'][step,index]
    data.qpos[addresses] = trace['native_q'][step,index]
    mujoco.mj_forward(model,data)
    rim = min(data.xpos[model.body(name).id,2] for name in ('left_wheel_link','right_wheel_link'))-.0625
    if int(trace['phase'][step,index])==3:rendered_rims.append(float(rim))
    camera.lookat[:] = [root[0],root[1],.30]
    renderer.update_scene(data,camera=camera,scene_option=option)
    pixels = renderer.render().copy()
    assert float(pixels.std()) > 3., 'Blank recorded-pose rendering'
    image = Image.fromarray(pixels)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0,0,960,72),fill=(245,247,247))
    phase = int(trace['phase'][step,index])
    draw.text((16,9),f'LEARNED POLICY | {labels[phase]} | {float(trace["age"][step,index]):.2f} s',font=font,fill=(20,30,30))
    draw.text((16,41),f'{group_label} case {index} | native state | pass: {qualified} | vx {float(trace["vx"][step,index]):.2f} m/s | x {root[0]:.2f} m',font=small,fill=(50,65,65))
    draw.rectangle((0,504,960,540),fill=(245,247,247))
    pitch = np.rad2deg(float(trace['air_pitch'][step,index]))
    roll = np.rad2deg(float(trace['air_roll'][step,index]))
    draw.text((16,512),f'Air pitch {pitch:.2f} deg | roll {roll:.2f} deg | air {float(trace["air_s"][step,index]):.2f} s | tuck: {bool(trace["retracted"][step,index])}',font=small,fill=(30,45,45))
    return image


output.mkdir(parents=True,exist_ok=True)
video = output/'learned_policy_recording.mp4'
with imageio.get_writer(video,fps=50,codec='libx264',quality=8,macro_block_size=None) as writer:
    for step in range(end):
        writer.append_data(np.asarray(frame(step)))
keys = []
phases = trace['phase'][:end,index]
joint_case=trace['native_q'][:end,index]
leg_delta=.5*(joint_case[:,names.index('left_front1_joint')]-joint_case[:,names.index('left_rear1_joint')]
              +joint_case[:,names.index('right_front1_joint')]-joint_case[:,names.index('right_rear1_joint')])
for phase in range(5):
    options = np.flatnonzero(phases == phase)
    if len(options):
        if phase == 1:
            height = trace['root_pos'][options,index,2]
            step = int(options[int(height.argmin())])
        elif phase == 3:
            step = int(options[int(leg_delta[options].argmin())])
        elif phase == 2:
            step = int(options[int(leg_delta[options].argmax())])
        else:
            step = int(options[len(options)//2])
        keys.append(step)
keys.append(end-1)
board = Image.new('RGB',(1440,810),(245,247,247))
for slot,step in enumerate(keys[:6]):
    tile = frame(step).resize((480,270),Image.Resampling.LANCZOS)
    board.paste(tile,((slot%3)*480,(slot//3)*270))
board = board.crop((0,0,1440,270*((min(len(keys),6)+2)//3)))
board.save(output/'learned_policy_frames.png')
renderer.close()
actual_peak = float(trace['rim_peak'][:end,index].max())
rendered_peak = max(rendered_rims,default=0.)
receipt = dict(checkpoint_sha256=selected['sha256'],evaluation=selected['job'],case=row,
    accepted_complete_case=qualified,
    playback='Recorded native PhysX policy states; MuJoCo renderer only, no physics integration',
    visualization='Render-only lighting and floor contrast; plant file and physical state unchanged',
    teacher_executed=False,frames=end,fps=50,terminal_reset_frame_omitted=True,
    native_recorded_rim_peak_m=actual_peak,rendered_rim_peak_m=rendered_peak,
    pose_height_difference_m=abs(actual_peak-rendered_peak),
    video_path=str(video),video_bytes=video.stat().st_size,
    video_sha256=hashlib.sha256(video.read_bytes()).hexdigest())
(T/'evidence/RECORDED_POLICY_RENDER.json').write_text(json.dumps(receipt,indent=2)+'\n')
shutil.copy2(output/'learned_policy_frames.png',T/'evidence/learned_policy_frames.png')
print(json.dumps(receipt,indent=2))
