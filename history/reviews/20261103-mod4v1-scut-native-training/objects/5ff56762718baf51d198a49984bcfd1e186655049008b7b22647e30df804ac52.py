"""MuJoCo display of recorded Isaac body poses, no policy or physics stepping."""
from pathlib import Path
import json
import os
import time
import traceback
import threading
import xml.etree.ElementTree as ET
import numpy as np
import mujoco
import mujoco.viewer

N=Path(__file__).resolve().parent
A=N/'env20000_scut_stairs_1h_20261104/attempt07'
R=A/'reports'
facts=json.loads((R/'POSTROUND_FULL_RETURNED.json').read_bytes())['files']
result=facts['evaluation/RESULT.json']
contract=json.loads(Path('F:/RMPOLAR-RL/mod4_usd_scut_fudan_20261101/candidates/v1/assets/import_contract.json').read_bytes())
with np.load(A/'evaluation/selected_actual_poses.npz',allow_pickle=False)as data:
    poses={key:data[key].copy()for key in data.files}
ids=result['recorded_envs'];names=result['body_names'];origins=np.asarray(result['environment_origins'])
offsets=np.asarray([[0.,i*12.,0.]for i in range(4)])
root=ET.Element('mujoco',model='MOD4v1 SCUT final ffce | recorded native rollout')
ET.SubElement(root,'compiler',angle='radian')
ET.SubElement(root,'option',gravity='0 0 0')
visual=ET.SubElement(root,'visual')
ET.SubElement(visual,'headlight',ambient='.6 .6 .6',diffuse='.8 .8 .8')
ET.SubElement(visual,'global',offwidth='1280',offheight='800')
asset=ET.SubElement(root,'asset');world=ET.SubElement(root,'worldbody')
ET.SubElement(world,'light',pos='0 0 6',dir='0 0 -1',diffuse='.8 .8 .8')
fmt=lambda values:' '.join(format(float(value),'.9g')for value in np.asarray(values).ravel())
for i,eid in enumerate(ids):
    ET.SubElement(asset,'mesh',name='terrain'+str(eid),
        vertex=fmt(poses['terrain_vertices_'+str(eid)]),
        face=' '.join(str(int(v))for v in poses['terrain_faces_'+str(eid)].ravel()))
    terrain=ET.SubElement(world,'body',name='terrain'+str(eid),pos=fmt(offsets[i]))
    ET.SubElement(terrain,'geom',type='mesh',mesh='terrain'+str(eid),contype='0',conaffinity='0',
        rgba='.45 .57 .64 1',group='0')
for name in names:
    body=ET.SubElement(world,'body',name=name,mocap='true')
    for gname,geom in contract['geometry'].items():
        if geom['visual']or geom['body']!=name:continue
        kind={5:'cylinder',6:'box'}.get(geom['type'])
        if kind is None:continue
        size=geom['size'][:2]if kind=='cylinder'else geom['size']
        ET.SubElement(body,'geom',name=gname,type=kind,size=fmt(size),
            pos=fmt(geom['position_m']),quat=fmt(geom['quat_wxyz']),
            contype='0',conaffinity='0',rgba='.91 .58 .18 1'if name in ['left_wheel','right_wheel']else'.3 .48 .65 1')
model=mujoco.MjModel.from_xml_string(ET.tostring(root,encoding='unicode'))
data=mujoco.MjData(model)
mapping=np.asarray([model.body_mocapid[mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_BODY,name)]for name in names])
state=dict(case=2,frame=0,paused=False,speed=1.,reset=True)
lock=threading.Lock()
def put(name,value):
    target=R/name;temp=target.with_suffix('.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8');os.replace(temp,target)
def key(code):
    with lock:
        if code in [49,50,51,52]:state.update(case=code-49,frame=0,reset=True)
        elif code==32:state['paused']=not state['paused']
        elif code in [82,114]:state.update(frame=0,reset=True)
        elif code in [72,104]:state['speed']=.5 if state['speed']==1. else 1.
try:
    put('MUJOCO_REPLAY_PREPARED.json',dict(epoch=time.time(),PID=os.getpid(),
        model_SHA=result['source_SHA'],source_pose=str(A/'evaluation/selected_actual_poses.npz'),
        source_pose_SHA=result['actual_poses']['SHA'],saved_quaternion_order='wxyz',
        body_count=len(names),recorded_envs=ids,live_policy=False,physics_steps=0,PT_reads=0,
        description='Replay actual native recorded first episodes using enhanced contract collision shapes and recorded terrain',
        keys='1 env0;2 env1;3 env40;4 env41;Space pause;R replay;H half speed'))
    with mujoco.viewer.launch_passive(model,data,key_callback=key,show_left_ui=False,show_right_ui=False)as viewer:
        with viewer.lock():
            viewer.cam.distance=2.1;viewer.cam.azimuth=125.;viewer.cam.elevation=-18.
        started=time.perf_counter();last=0.;hold_until=started+2.
        while viewer.is_running():
            begin=time.perf_counter()
            with lock:
                current=state.copy()
                if state['reset']:hold_until=begin+2.;state['reset']=False
            case=current['case'];eid=ids[case]
            valid=np.flatnonzero(poses['active'][:,case])
            frame=min(current['frame'],int(valid[-1]))
            data.mocap_pos[mapping]=poses['body_pos'][frame,case]-origins[eid]+offsets[case]
            data.mocap_quat[mapping]=poses['body_quat'][frame,case]
            data.time=float(poses['tick'][frame])*.0025
            mujoco.mj_forward(model,data)
            viewer.cam.lookat[:]=data.mocap_pos[mapping[names.index('chassis')]]
            viewer.sync()
            if begin-last>1.:
                put('MUJOCO_REPLAY_CURRENT.json',dict(epoch=time.time(),PID=os.getpid(),
                    viewer_running=True,env=eid,frame=frame,time_s=data.time,
                    paused=current['paused'],speed=current['speed'],model_SHA=result['source_SHA'],
                    actual_recorded_rollout=True,live_policy=False,new_physics=0,PT_reads=0))
                print(json.dumps(dict(env=eid,time_s=data.time,paused=current['paused'])),flush=True);last=begin
            if not current['paused']and begin>=hold_until:
                with lock:
                    state['frame']=frame+1 if frame<int(valid[-1]) else 0
                    if state['frame']==0:state['reset']=True
            time.sleep(max(0.,.02/current['speed']-(time.perf_counter()-begin)))
    put('MUJOCO_REPLAY_CLOSED.json',dict(epoch=time.time(),PID=os.getpid(),viewer_closed=True))
except BaseException:
    put('MUJOCO_REPLAY_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()))
    raise
