"""Requested saved-pose visual only. No ONNX/actor/model, FK solve or physics."""
from pathlib import Path
import xml.etree.ElementTree as ET
import json,hashlib,time,sys,importlib.util,traceback,struct,math
import numpy as np
S=Path(__file__).resolve().parent;T=S.parent;R=S/'reports';V=S/'FUDAN_AND_CURRENT_REFERENCE_SAVED_VISUAL_COMPARISON'
J=T/'MOD4_UNISUPERMIMIC_FUDAN_JUMP_REFERENCE_TRANSFER_20261026';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
def put(n,x):
 with (R/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2,allow_nan=False)
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def artifact(p):return dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))
def main():
 receipt=json.loads((R/'EXACT_EXISTING_FUDAN_VISUAL_XML_STL_RETURNED_ACTUAL.json').read_bytes());assert receipt['actual_finite_transport_returned']
 root=V/'exact_original_fudan_assets';xml=root/'mujoco/assert_now/infantry_binglian_yuntai/infantry_V2/meshes/mjmodel.xml';assert H(xml)=='37d934a964acc66f3ebafcf74741fcb6302c5aa8856a7e4b99e97c864bbff0f0'
 put('NEW_PURPOSE_ORIGINAL_FUDAN_BODY_POSE_AND_ACTIVE_REFERENCE_VISUAL_CONSUMED_ACTUAL.json',dict(epoch=time.time(),user_requested_original_and_converted_motion_comparison=True,original_NPZ_existing_producer_SHA='9461c534056357da479de2b9d63ea7def8299f1b59d954133ad27af92e92750f',original_NPZ_members_to_materialize=['body_position','body_quaternion_wxyz'],all_other_motion_from_saved_canonical_JSON=True,no_policy_physics_SDK_GPU_or_native_model_read=True))
 canonical=json.loads((J/'agent_reference_retarget_cpu/ACTUAL_FUDAN_TO_OWN_STATIC_RETARGET_1793004790656605900/upstream_actual_default_dt_standing_jump_CANONICAL_TASKSPACE_DEMO.json').read_bytes())
 time_s=np.asarray(canonical['time_s']);source_root=np.asarray(canonical['chassis_position_m']);contact=np.asarray(canonical['wheel_contact'],bool);bottom=np.asarray(canonical['wheel_bottom_world_z_m'])
 original=J/'actual_72_reference_artifacts/upstream_actual_default_dt_standing_jump/ORIGINAL_ROBOT_REFERENCE_CONTROL_ROWS.npz';assert original.stat().st_size==1991407
 with np.load(original,allow_pickle=False) as data:bodyp=data['body_position'];bodyq=data['body_quaternion_wxyz']
 tree=ET.parse(xml);world=tree.getroot().find('worldbody');bodies=list(world.iter('body'));names=['world']+[b.attrib['name'] for b in bodies]
 assert bodyp.shape==(len(time_s),len(names),3) and bodyq.shape==(len(time_s),len(names),4)
 # Only pure original renderer math, never its old main or inputs.
 old=T/'H1_STEP270_NATIVE86_FULL_SINGLE_ATTEMPT_REPLAY_20261027/render_actual_single_native_attempt_CPU_unused_once.py'
 sp=importlib.util.spec_from_file_location('pure_collider_math_for_requested_teacher_visual',old);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 def rot_wxyz(q):return m.rotation([q[1],q[2],q[3],q[0]])
 def nums(text,default):return np.asarray([float(x) for x in text.split()]) if text else np.asarray(default,float)
 mesh_nodes={x.attrib['name']:x for x in tree.getroot().find('asset').findall('mesh')};meshpoints={}
 from scipy.spatial import ConvexHull,QhullError
 for name,node in mesh_nodes.items():
  path=(xml.parent/node.attrib['file']).resolve();assert path.is_relative_to(root.resolve()) and path.exists()
  raw=path.read_bytes();n=struct.unpack_from('<I',raw,80)[0];assert 84+50*n==len(raw),'binary original STL layout'
  dtype=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attribute','<u2')]);points=np.frombuffer(raw,dtype=dtype,count=n,offset=84)['vertices'].reshape(-1,3).astype(float)
  points=np.unique(points,axis=0)*nums(node.get('scale'),[1,1,1])
  try:points=points[ConvexHull(points).vertices]
  except QhullError:pass
  meshpoints[name]=points
 geoms=[]
 for body in bodies:
  bid=names.index(body.attrib['name'])
  for geom in body.findall('geom'):
   kind=geom.get('type','sphere');position=nums(geom.get('pos'),[0,0,0]);rotation=rot_wxyz(nums(geom.get('quat'),[1,0,0,0]))
   if kind=='mesh':points=meshpoints[geom.attrib['mesh']]
   elif kind=='cylinder':
    size=nums(geom.get('size'),[.06,.03]);theta=np.linspace(0,2*np.pi,40,endpoint=False);points=np.concatenate([np.stack([size[0]*np.cos(theta),size[0]*np.sin(theta),np.full_like(theta,z)],-1) for z in (-size[1],size[1])])
   elif kind=='box':
    size=nums(geom.get('size'),[.1,.1,.1]);points=np.asarray([[x,y,z] for x in (-1,1) for y in (-1,1) for z in (-1,1)])*size
   else:continue
   geoms.append((bid,body.attrib['name'],points@rotation.T+position))
 # Active9223 goal, not an outdatedV3 plot and not learned MOD4 movement.
 N=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027';B=N/'payloads/h1';task=json.loads((B/'job0/TASK.json').read_bytes());reference_path=B/task['native_reference_relative'];assert H(reference_path)=='9223a53e7bf85a0dc3505cc46c0eb33d04fc35a9bf85e7ffe0e4fbd03e1e46c3'
 ref=json.loads(reference_path.read_bytes());states=np.asarray(ref['packed73']);ages=np.asarray(ref['ages']);phase=ref['phase'];assert states.shape==(len(ages),73)
 sys.path[:0]=[str(J/'agent_reference_retarget_cpu'),str(L/'agent_MOD4_step_reference_conversion_candidate_v1')]
 from own_usd_closed_chain_ik_v1 import OwnUsdKinematics,transform
 from supermimic_reference_adapter_v1 import quat_to_mat
 from mod4_step_reference_conversion_v1 import build_recorded_kinematics
 own_geometry=json.loads((S/'actual210/seed_20260928/ACTUAL_RENDER_GEOMETRY.json').read_bytes());contract=json.loads((B/'job0/assets/import_contract.json').read_bytes());kin=build_recorded_kinematics(contract,own_geometry,OwnUsdKinematics,transform,quat_to_mat)
 reorder=[ref['joint_names'].index(n) for n in kin.joint_names];ownp=[];ownq=[]
 for state in states:
  poses=kin.forward(state[13:43][reorder],enforce_transmission=False);R0=quat_to_mat(state[3:7]);positions=[];rotations=[]
  for name in kin.body_names:positions.append(R0@poses[name][:3,3]+state[:3]);rotations.append(R0@poses[name][:3,:3])
  ownp.append(positions);ownq.append(rotations)
 ownp=np.asarray(ownp);ownq=np.asarray(ownq);own_shapes=[(g,m.local_points(g)) for g in own_geometry['shapes']]
 baseline=int(np.argmin(abs(time_s-1.)));source_x0=float(source_root[baseline,0]);source_z0=float(bottom[baseline].mean())
 derived=V/'SAVED_FUDAN_BODY_AND_ACTIVE_OWN_GOAL_VISUAL_DERIVED.npz';assert not derived.exists();np.savez_compressed(derived,source_time=time_s,source_body_position=bodyp,source_body_quaternion_wxyz=bodyq,source_body_names=np.asarray(names),source_contact=contact,source_origin=np.asarray([source_x0,0,source_z0]),own_age=ages,own_states73=states,own_body_position=ownp,own_body_rotation=ownq)
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.patches import Polygon,Rectangle
 from PIL import Image
 def polygon_draw(ax,items):
  for _,name,vertices in sorted(items,key=lambda x:x[0],reverse=True):
   hull=m.hull(vertices[:,[0,2]]);col='#263c50' if 'wheel' in name.lower() else '#b6c7d8' if name in ('base_Link_del','chassis') else '#d6955a' if name.startswith(('l2','r2','left_crank','right_crank')) else '#708da6'
   if len(hull)>=3:ax.add_patch(Polygon(hull,facecolor=col,edgecolor='#3f5368',linewidth=.55))
 def draw_source(ax,index):
  origin=np.asarray([source_x0,0,source_z0]);items=[]
  for bid,name,points in geoms:
   vertices=points@rot_wxyz(bodyq[index,bid]).T+bodyp[index,bid]-origin;items.append((float(vertices[:,1].mean()),name,vertices))
  # Actual original landing platform, translated with the body coordinates.
  g=next(x for x in world.findall('geom') if x.get('name')=='landing_box');pos=nums(g.get('pos'),[0,0,0])-origin;size=nums(g.get('size'),[0,0,0]);ax.add_patch(Rectangle((pos[0]-size[0],pos[2]-size[2]),2*size[0],2*size[2],facecolor='#e5eaf0',edgecolor='#8996a8'))
  polygon_draw(ax,items);ax.text(.02,.96,f"source t={time_s[index]:.3f}s\nsupport L/R={contact[index].astype(int).tolist()}",transform=ax.transAxes,va='top',fontsize=8)
 def draw_own(ax,index):
  ax.add_patch(Rectangle((-.55,-.04),2,.04,facecolor='#e5eaf0'));ax.add_patch(Rectangle((.35,0),.8,.27,facecolor='#d2dae4',edgecolor='#8996a8'));items=[]
  for g,points in own_shapes:
   bid=kin.body_names.index(g['body']);vertices=points@ownq[index,bid].T+ownp[index,bid];items.append((float(vertices[:,1].mean()),g['body'],vertices))
  polygon_draw(ax,items);label='Fudan-derived static air reference' if ages[index]<145 else 'Own designed platform IK target'
  ax.text(.02,.96,f"own age={ages[index]}\n{label}",transform=ax.transAxes,va='top',fontsize=8)
 def decorate(ax):
  ax.set_xlim(-.5,1.25);ax.set_ylim(-.04,1.02);ax.set_aspect('equal');ax.grid(alpha=.12);ax.set_xlabel('forward X (m)');ax.set_ylabel('height above initial support (m)')
 keytimes=[1.0,1.5,1.72,1.86,2.0,2.5];fig,axes=plt.subplots(2,6,figsize=(20,7),dpi=120)
 for col,t in enumerate(keytimes):
  si=int(np.argmin(abs(time_s-t)));oi=int(np.argmin(abs(ages-(t-.5)*100)));draw_source(axes[0,col],si);draw_own(axes[1,col],oi)
  for row in (0,1):decorate(axes[row,col])
 axes[0,0].set_title('FUDAN: recorded standing jump',loc='left',fontsize=10);axes[1,0].set_title('MOD4: designed reference, not a rollout',loc='left',fontsize=10)
 fig.suptitle('Original Fudan saved movement vs CURRENT9223 MOD4 goal\nTeacher record is a standing jump on its original platform; own forward travel / 270mm landing are synthesized goals',fontsize=13);fig.tight_layout(rect=(0,0,1,.91));sheet=V/'FUDAN_ORIGINAL_VS_CURRENT_MOD4_REFERENCE_KEYFRAMES.png';fig.savefig(sheet);plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(12,6),dpi=100);images=[];selected_times=np.arange(1.,2.801,.02)
 for t in selected_times:
  for ax in axes:ax.clear()
  si=int(np.argmin(abs(time_s-t)));oi=int(np.argmin(abs(ages-(t-.5)*100)));draw_source(axes[0],si);draw_own(axes[1],oi)
  for ax in axes:decorate(ax)
  axes[0].set_title('Fudan ORIGINAL saved standing-jump poses');axes[1].set_title('MOD4 CURRENT9223 static target / NO physics')
  fig.suptitle('Same recorded-source clock | 2x slow GIF | no new policy or simulation',fontsize=11);fig.tight_layout();fig.canvas.draw();images.append(Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[...,:3].copy()))
 plt.close(fig);gif=V/'FUDAN_ORIGINAL_VS_CURRENT_MOD4_REFERENCE_2X_SLOW.gif';images[0].save(gif,save_all=True,append_images=images[1:],duration=40,optimize=False)
 report=dict(epoch=time.time(),passed=True,user_requested_visual=True,original_motion_producer_SHA='9461c534056357da479de2b9d63ea7def8299f1b59d954133ad27af92e92750f',only_new_NPZ_members_read=['body_position','body_quaternion_wxyz'],canonical_time_contact_and_pose_from_already_saved_JSON=True,original_exact_MJCF_SHA=H(xml),current_reference_SHA=H(reference_path),original_is_command0_standing_jump_not_step_ascent=True,own9223_forward_and_post145_landing_are_designed_not_measured=True,own_FK_only_no_IK_resolve_or_physics=True,source_geometry_render='convex silhouettes from exact pinned original meshes plus original primitive wheel geoms',body_order=names,artifacts=[artifact(sheet),artifact(gif),artifact(derived)],source_data_original_retained=True,no_model_actor_WM_forward_SDK_or_physics=True,not_any_new_skill_success=True)
 put('USER_REQUESTED_FUDAN_ORIGINAL_AND_CURRENT_REFERENCE_VISUAL_ACTUAL.json',report);print(json.dumps(dict(passed=True,artifacts=report['artifacts'],original_standing_jump=True,own_static_goal=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('FUDAN_REFERENCE_VISUAL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_repeat_of_original_NPZ_body_read_or_actor=True));raise
