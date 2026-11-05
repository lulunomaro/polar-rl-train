"""Display saved PhysX body poses with released v2 meshes; no policy or mj_step."""
from pathlib import Path
import hashlib, importlib.util, json, shutil, subprocess, sys, time, xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

N=Path(__file__).resolve().parent
A=N/'takeoff_velocity_final239_1h';V=A/'evaluation'
returned=A/'reports/POSTROUND_FULL_RETURNED.json'
f=json.loads(returned.read_bytes())['files'];result=f['evaluation/RESULT.json']
usd=Path('F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package/assets/robot.usd')
assert hashlib.sha256(usd.read_bytes()).hexdigest()=='2237070ddc0a4e33f0c28e23fe5bb3db1f12bb619fddcdd89f9a74d5ac875f18'
pose=V/'selected_actual_poses.npz';raw=pose.read_bytes()
assert hashlib.sha256(raw).hexdigest()==result['actual_poses']['SHA']
assert result['saved_pose_quaternion_order']=='wxyz'
with np.load(pose,allow_pickle=False)as data:poses={k:data[k].copy()for k in data.files}
helper=Path('F:/RMPOLAR-RL/mod4_standing_step200_rlbptt_20261103/render_standing_recorded_v2.py')
sys.path.insert(0,str(helper.parent))
spec=importlib.util.spec_from_file_location('v2_existing_mesh_display',helper)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
names=result['body_names'];elements,vfs=module.mesh_visuals(usd,names)
fmt=lambda a:' '.join(format(float(v),'.9g')for v in np.asarray(a).ravel())
root=ET.Element('mujoco',model='MOD4v2 final346 - actual saved PhysX trajectory')
ET.SubElement(root,'compiler',angle='radian')
vis=ET.SubElement(root,'visual');ET.SubElement(vis,'global',offwidth='960',offheight='600')
ET.SubElement(vis,'headlight',ambient='.6 .6 .6',diffuse='.7 .7 .7')
assets=ET.SubElement(root,'asset')
for name,file in elements:ET.SubElement(assets,'mesh',name=name,file=file)
world=ET.SubElement(root,'worldbody');ET.SubElement(world,'light',pos='0 -1 3',dir='0 0 -1')
eid=41;case=result['recorded_envs'].index(eid)
vertices=poses['terrain_vertices_'+str(eid)];faces=poses['terrain_faces_'+str(eid)]
ET.SubElement(assets,'mesh',name='actual_course',vertex=fmt(vertices),face=' '.join(str(int(i))for i in faces.ravel()))
ET.SubElement(world,'geom',type='mesh',mesh='actual_course',contype='0',conaffinity='0',rgba='.30 .46 .59 1')
for name,_ in elements:
    body=ET.SubElement(world,'body',name='recorded_'+name,mocap='true')
    ET.SubElement(body,'geom',type='mesh',mesh=name,contype='0',conaffinity='0',density='0',
        rgba='.92 .62 .2 1'if 'wheel'in name else'.74 .78 .83 1')
import mujoco
model=mujoco.MjModel.from_xml_string(ET.tostring(root,encoding='unicode'),vfs)
data=mujoco.MjData(model);assert model.nq==0 and model.nmocap==len(names)
ids=np.asarray([model.body_mocapid[mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_BODY,'recorded_'+n)]for n in names])
origin=np.asarray(result['environment_origins'][eid])
camera=mujoco.MjvCamera();camera.lookat[:]=[.50,0,.24];camera.distance=1.9;camera.azimuth=90;camera.elevation=-17
target=V/'actual_video';target.mkdir(exist_ok=False)
ffmpeg=shutil.which('ffmpeg');assert ffmpeg
path=target/'MOD4v2_final346_env41_actual.mp4'
encoder=subprocess.Popen([ffmpeg,'-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
    '-s','960x600','-r','50','-i','-','-an','-c:v','libx264','-crf','20','-pix_fmt','yuv420p',str(path)],
    stdin=subprocess.PIPE,stderr=subprocess.PIPE)
valid=np.flatnonzero(poses['active'][:,case]);images=[]
try:
    with mujoco.Renderer(model,height=600,width=960)as renderer:
        for idx in valid:
            data.mocap_pos[ids]=poses['body_pos'][idx,case]-origin
            data.mocap_quat[ids]=poses['body_quat'][idx,case]
            data.time=float(poses['tick'][idx])*.0025
            mujoco.mj_forward(model,data)
            renderer.update_scene(data,camera=camera);pixels=renderer.render()
            encoder.stdin.write(pixels.tobytes())
            if int(poses['tick'][idx]) in [80,800,1600,3192]:
                image=target/('actual_%0.2fs.png'%data.time);Image.fromarray(pixels).save(image);images.append(str(image))
    encoder.stdin.close();error=encoder.stderr.read().decode('utf8','replace');rc=encoder.wait()
    assert rc==0,error
finally:
    if encoder.poll()is None:encoder.terminate();encoder.wait()
media=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in [path,*map(Path,images)]]
report=dict(epoch=time.time(),media=[row['path']for row in media],media_identity=media,
    actual_saved_body_poses=True,model_SHA=result['source_SHA'],source_pose=result['actual_poses'],
    USD=dict(path=str(usd),SHA=hashlib.sha256(usd.read_bytes()).hexdigest()),
    mesh_helper=dict(path=str(helper),SHA=hashlib.sha256(helper.read_bytes()).hexdigest()),
    recorded_env=eid,frames=len(valid),FPS=50,seconds=len(valid)/50,saved_body_quaternion_order='wxyz',
    NN=0,physics_steps=0,PT_reads=0,SSH=0,canonical_writes=0,
    playback='Actual final346 first episode, authored display meshes at saved PhysX body poses; MuJoCo mj_forward only')
with(target/'RENDER_REPORT.json').open('x',encoding='utf8')as stream:json.dump(report,stream,indent=2)
print(json.dumps(report))
