from pathlib import Path
import importlib.util,json,sys,time,traceback
D=Path(__file__).resolve().parent;T=D.parent;W=T.parent;R=D/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE=r'''
from pathlib import Path
import json,time,numpy as np,mujoco
B=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MoE_matched_player_4090_2410v1');out=B/'out/SAVED_POSE_BODY_XBODY_READBACK_V1.json';assert not out.exists();m=mujoco.MjModel.from_xml_path(str(B/'player/rm7v7_latest_moe.xml'));data=mujoco.MjData(m);bid=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_BODY,'chassis');result={}
for case in ('auto_vx_0p6','E0_vx_0p6','auto_vx_1p2'):
 with np.load(B/'out'/(case+'.npz'),allow_pickle=False) as z:
  q=z['qpos'];vel=z['qvel'];state=z['state'];idx=sorted(set([int(np.argmax(vel[:,0])),len(q)-101,len(q)-1]+([int(np.flatnonzero(q[:,0]>-5.5)[0])] if (q[:,0]>-5.5).any() else [])));rows=[]
  for i in idx:
   data.qpos[:]=q[i];data.qvel[:]=vel[i];mujoco.mj_forward(m,data);bi=np.zeros(6);xb=np.zeros(6);world=np.zeros(6);mujoco.mj_objectVelocity(m,data,mujoco.mjtObj.mjOBJ_BODY,bid,bi,1);mujoco.mj_objectVelocity(m,data,mujoco.mjtObj.mjOBJ_XBODY,bid,xb,1);mujoco.mj_objectVelocity(m,data,mujoco.mjtObj.mjOBJ_XBODY,bid,world,0);direct=data.xmat[bid].reshape(3,3).T@vel[i,:3];assert np.max(np.abs(xb[3:]-direct))<1e-8 and np.max(np.abs(world[3:]-vel[i,:3]))<1e-8
   contacts=[]
   for j in range(data.ncon):
    c=data.contact[j];g1,g2=int(c.geom1),int(c.geom2)
    if (m.geom_bodyid[g1]==0)!=(m.geom_bodyid[g2]==0):contacts.append(dict(geom1=mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_GEOM,g1),geom2=mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_GEOM,g2),distance=float(c.dist),position=c.pos.tolist()))
   rows.append(dict(control=i+1,time_s=float(state[i,0]),xyz=q[i,:3].tolist(),world_v=world[3:].tolist(),body_regular_v=xb[3:].tolist(),old_inertial_v=bi[3:].tolist(),old_stored_HUD_vx=float(state[i,2]),same_saved_pose_old_BODY_value_reproduced=bool(abs(bi[3]-state[i,2])<1e-8),new_regular_body_v_exact_to_independent_qvel_rotation=True,contacts_from_fresh_saved_pose_forward_kinematics_not_recorded_force=contacts))
  xvel=np.diff(q[:,0])/.01;result[case]=dict(selected_rows=rows,source_route_endpoint_x_m=-5.5,end_x_m=float(q[-1,0]),tail_world_vx_from_saved_qvel=float(vel[-100:,0].mean()),tail_world_vx_from_position_difference=float(xvel[-100:].mean()))
v=dict(epoch=time.time(),mujoco_version=mujoco.__version__,chassis_body_inertial_quat=m.body_iquat[bid].tolist(),chassis_body_inertial_position=m.body_ipos[bid].tolist(),result=result,scope='New selected saved-pose readback on remote4090 host, no control stepping, no optimizer or policy inference, no local simulation. XBODY regular-body velocity crosschecked against independent saved qvel rotation; old BODY metrics retained.',official_primary_source='https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html');out.write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''
try:
 s=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);secret=m.recover();c=d.connect72(secret);secret=None
 try:v=d.code(c,d.PY72,CODE,{},timeout=90)
 finally:c.close()
 put('4090_SAVED_POSE_BODY_XBODY_INDEPENDENT_READBACK_ACTUAL.json',v);print(json.dumps(dict(passed=True,old_HUD_frame_error_confirmed=True,cases=list(v['result']))))
except BaseException:put('4090_SAVED_POSE_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
