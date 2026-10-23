"""Resolve the timed-out readback first, then only missing kinematic evidence."""
from pathlib import Path
import importlib.util,json,sys,time,traceback
D=Path(__file__).resolve().parent;T=D.parent;W=T.parent;R=D/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE=r'''
from pathlib import Path
import hashlib,json,os,psutil,time,xml.etree.ElementTree as ET
B=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MoE_matched_player_4090_2410v1');old=B/'out/SAVED_POSE_BODY_XBODY_READBACK_V1.json';deadline=time.monotonic()+450
expected="import sys,json;v=json.loads(sys.stdin.readline());exec(v['code'])"
def old_readback_candidates():
 rows=[]
 for p in psutil.process_iter(['pid','create_time']):
  if p.pid==os.getpid() or not (v['old_min_epoch']<=p.info['create_time']<=v['old_max_epoch']):continue
  try:
   argv=p.cmdline()
   if len(argv)>=2 and argv[-2:] == ['-c',expected]:rows.append(dict(pid=p.pid,creation=p.info['create_time'],argv=argv))
  except psutil.Error:pass
 return rows
initial=old_readback_candidates()
while old_readback_candidates():
 assert time.monotonic()<deadline,'Previous exact RPC/time-window candidates still running; no new model loaded'
 time.sleep(2)
if old.exists():
 result=dict(epoch=time.time(),original_full_readback_file_present=True,old_RPC_candidates_at_entry=initial,old_RPC_candidates_now_out=True,ownership_scope='Exact known RPC argv plus narrow creation window; no signals or peer identity inspection outside the time filter.',value=json.loads(old.read_bytes()),no_old_readback_reexecution=True)
else:
 import numpy as np,mujoco
 source=B/'player/rm7v7_latest_moe.xml';root=ET.parse(source).getroot();bodies=list(root.iter('body'));assert len(bodies)==31 and all(x.find('inertial') is not None for x in bodies)
 # All 31 rigid-body inertials, joint order, poses and equality/site/sensor
 # definitions remain exact. Mesh/static geoms are irrelevant to this frame
 # readback and are removed only from this private, non-stepped XML string.
 parents={x:p for p in root.iter() for x in p}
 for x in list(root.iter('geom')):parents[x].remove(x)
 asset=root.find('asset')
 if asset is not None:root.remove(asset)
 model=mujoco.MjModel.from_xml_string(ET.tostring(root,encoding='unicode'));data=mujoco.MjData(model);bid=mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_BODY,'chassis');rows={}
 for case in ('auto_vx_0p6','E0_vx_0p6','auto_vx_1p2'):
  with np.load(B/'out'/(case+'.npz'),allow_pickle=False) as z:
   q=z['qpos'];qd=z['qvel'];state=z['state'];assert q.shape[1]==model.nq and qd.shape[1]==model.nv;selected=[]
   for i in (int(np.argmax(qd[:,0])),len(q)-101,len(q)-1):
    data.qpos[:]=q[i];data.qvel[:]=qd[i];mujoco.mj_forward(model,data);bi=np.zeros(6);xb=np.zeros(6);world=np.zeros(6);mujoco.mj_objectVelocity(model,data,mujoco.mjtObj.mjOBJ_BODY,bid,bi,1);mujoco.mj_objectVelocity(model,data,mujoco.mjtObj.mjOBJ_XBODY,bid,xb,1);mujoco.mj_objectVelocity(model,data,mujoco.mjtObj.mjOBJ_XBODY,bid,world,0);direct=data.xmat[bid].reshape(3,3).T@qd[i,:3];assert np.max(np.abs(xb[3:]-direct))<1e-8 and np.max(np.abs(world[3:]-qd[i,:3]))<1e-8
    selected.append(dict(control=i+1,xyz=q[i,:3].tolist(),old_BODY_inertial_v=bi[3:].tolist(),new_XBODY_regular_v=xb[3:].tolist(),world_v=world[3:].tolist(),old_stored_HUD_vx=float(state[i,2]),old_value_exactly_reproduced=bool(abs(bi[3]-state[i,2])<1e-8),new_body_value_matches_independent_qvel_rotation=True))
   rows[case]=dict(selected_rows=selected,tail_world_vx_saved_qvel=float(qd[-100:,0].mean()),tail_world_vx_position_difference=float((np.diff(q[:,0])/.01)[-100:].mean()),last_x=float(q[-1,0]),source_flat_route_endpoint_x=-5.5)
 result=dict(epoch=time.time(),original_full_readback_file_present=False,old_RPC_candidates_at_entry=initial,old_RPC_candidates_now_out=True,old_full_readback_not_reexecuted=True,minimal_missing_kinematic_readback_on_remote_host=True,all31_explicit_body_inertials_and_joint_order_retained=True,all_collision_mesh_geoms_removed_only_from_private_nonstepped_string=True,no_physics_or_contact_or_policy_rollout=True,mujoco_version=mujoco.__version__,body_inertial_quat=model.body_iquat[bid].tolist(),result=rows,not_evidence_of_identical_full_plant_or_contacts=True)
out=B/'out/SAVED_POSE_VELOCITY_FRAME_MISSING_V2.json';assert not out.exists();out.write_text(json.dumps(result,indent=2));print(json.dumps(result))
'''
try:
 old_error=sorted(R.glob('4090_SAVED_POSE_READER_ORIGINAL_ERROR_*.json'))[-1];old=json.loads(old_error.read_bytes());put('4090_MISSING_POSE_V2_STARTED_ACTUAL.json',dict(epoch=time.time(),original_timeout=str(old_error),no_local_simulation=True))
 s=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);secret=m.recover();c=d.connect72(secret);secret=None
 try:value=d.code(c,d.PY72,CODE,dict(old_min_epoch=old['epoch']-125,old_max_epoch=old['epoch']-75),timeout=550)
 finally:c.close()
 put('4090_MISSING_SAVED_POSE_BODY_XBODY_FRAME_V2_ACTUAL.json',value);print(json.dumps(dict(passed=True,full_old_readback_available=value['original_full_readback_file_present'],old_RPC_now_out=value['old_RPC_candidates_now_out'])))
except BaseException:put('4090_MISSING_POSE_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_replay=True));raise
