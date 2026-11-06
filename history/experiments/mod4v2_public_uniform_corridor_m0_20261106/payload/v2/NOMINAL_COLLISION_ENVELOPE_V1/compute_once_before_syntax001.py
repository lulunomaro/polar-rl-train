"""Exactly one original P0 model/data/forward; nominal compiled geom boxes, not dynamics."""
from pathlib import Path
import os,json,hashlib,traceback,math,importlib.util,xml.etree.ElementTree as ET,itertools
os.environ['OPENBLAS_NUM_THREADS']=os.environ['OMP_NUM_THREADS']=os.environ['MKL_NUM_THREADS']='1'
import numpy as np
import mujoco
D=Path(__file__).resolve().parent;R=D.parent;P=R.parent/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package'
COUNTS=dict(model_compile=0,new_MjData=0,mj_forward=0,set_configuration=0,integration=0,statics_DARE_oldQA_raw_Git_Goal_hardware_agents=0)
STAGE='preexec';affinity=None

def save(name,value):
 with(D/name).open('x',encoding='utf-8',newline='\n')as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
def rec(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def forbidden(*a,**k):COUNTS['integration']+=1;raise RuntimeError('integration forbidden in nominal-envelope scope')
original_forward=mujoco.mj_forward

def one_forward(m,d):
 if COUNTS['mj_forward']!=0:raise RuntimeError('second mj_forward forbidden')
 COUNTS['mj_forward']+=1;return original_forward(m,d)

def main():
 global STAGE,affinity
 assert not(D/'RESULT.json').exists()and not(D/'STARTED.json').exists()
 try:
  import psutil
  proc=psutil.Process();allowed=proc.cpu_affinity();proc.cpu_affinity([allowed[0]]);affinity=proc.cpu_affinity()
 except ImportError:affinity='psutil not installed; BLAS threads1'
 inputs=[P/'mjcf/scene.xml',P/'kinematics_v2.py',R/'nominal_gain_v2.json',D/'PREEXEC.json',Path(__file__)]
 pins=[rec(x)for x in inputs];gain=json.loads((R/'nominal_gain_v2.json').read_bytes());q=np.asarray(gain['gain']['q'],float)
 assert q.shape==(7,)and np.isfinite(q).all()and gain['model_SHA']==pins[0]['SHA']
 raw=(P/'mjcf/scene.xml').read_bytes();xml=ET.fromstring(raw);compiler=xml.find('compiler');meshdir=(P/'mjcf'/compiler.get('meshdir','')).resolve();assert meshdir.is_dir();compiler.set('meshdir',str(meshdir))
 spec=importlib.util.spec_from_file_location('_round26_p0_nominal_kin',P/'kinematics_v2.py');kin=importlib.util.module_from_spec(spec);spec.loader.exec_module(kin)
 for name in('mj_step','mj_step1','mj_step2','mj_Euler','mj_RungeKutta','mj_implicit'):setattr(mujoco,name,forbidden)
 mujoco.mj_forward=one_forward
 save('STARTED.json',dict(stage='before_single_model_compile',source_pins=pins,counts=COUNTS.copy(),affinity=affinity,SDK=mujoco.__version__,original_option=xml.find('option').attrib,XML_change_only_absolute_meshdir=True))
 STAGE='one_model_compile';COUNTS['model_compile']+=1;m=mujoco.MjModel.from_xml_string(ET.tostring(xml,encoding='unicode'))
 STAGE='one_MjData';COUNTS['new_MjData']+=1;d=mujoco.MjData(m)
 root=m.body('chassis').id;free=m.joint('floating_base');adr=int(m.jnt_qposadr[free.id]);assert int(m.jnt_type[free.id])==int(mujoco.mjtJoint.mjJNT_FREE)
 d.qpos[adr:adr+3]=[0.,0.,0.];yaw,pitch=float(q[1]),float(q[2]);cy,sy,cp,sp=math.cos(yaw/2),math.sin(yaw/2),math.cos(pitch/2),math.sin(pitch/2);d.qpos[adr+3:adr+7]=[cy*cp,-sy*sp,cy*sp,sy*cp]
 for side in('left','right'):d.qpos[int(m.jnt_qposadr[m.joint(side+'_wheel_spin').id])]=0.
 d.qvel[:]=0.;d.ctrl[:]=0.;d.qfrc_applied[:]=0.;d.xfrc_applied[:]=0.
 STAGE='one_setter_with_sole_forward';COUNTS['set_configuration']+=1;kin.set_configuration(m,d,left=(float(q[3]),float(q[3]+q[4])),right=(float(q[5]),float(q[5]+q[6])),check_limits=True)
 assert COUNTS['mj_forward']==1 and d.time==0.
 STAGE='compiled_geom_arrays_only';rootpos=d.xpos[root].copy();rootR=d.xmat[root].reshape(3,3).copy();assert np.isfinite(rootR).all()and np.isfinite(rootpos).all()
 ids=np.flatnonzero(m.geom_bodyid>0);signs=np.asarray(list(itertools.product((-1.,1.),repeat=3)));rows=[];unknown=[];pad=1e-9
 for g in ids:
  g=int(g);box=np.asarray(m.geom_aabb[g],float).copy();pos=d.geom_xpos[g].copy();rot=d.geom_xmat[g].reshape(3,3).copy();collision=bool(int(m.geom_contype[g])|int(m.geom_conaffinity[g]));typ=int(m.geom_type[g]);why=[]
  row=dict(id=g,name=m.geom(g).name,body_id=int(m.geom_bodyid[g]),body=m.body(int(m.geom_bodyid[g])).name,type=typ,collision_masks_nonzero=collision,contype=int(m.geom_contype[g]),conaffinity=int(m.geom_conaffinity[g]),aabb_local_center_halfsize=box.tolist()if np.isfinite(box).all()else None)
  if box.shape!=(6,)or not np.isfinite(box).all()or not np.isfinite(pos).all()or not np.isfinite(rot).all():why.append('nonfinite_or_shape')
  elif (box[3:]<0).any()or np.max(box[3:])<=0:why.append('negative_or_allzero_halfsize')
  if typ in(int(mujoco.mjtGeom.mjGEOM_PLANE),int(mujoco.mjtGeom.mjGEOM_HFIELD),int(mujoco.mjtGeom.mjGEOM_SDF)):why.append('nonfinite_or_unsupported_robot_geom_type')
  if why:row.update(valid_bound=False,unknown_reasons=why);unknown.append(dict(id=g,name=row['name'],reasons=why))
  else:
   local=box[:3]+signs*box[3:];world=local@rot.T+pos;corners=(world-rootpos)@rootR
   if not np.isfinite(corners).all():row.update(valid_bound=False,unknown_reasons=['nonfinite_corners']);unknown.append(dict(id=g,name=row['name'],reasons=['nonfinite_corners']))
   else:
    row.update(valid_bound=True,root_min_m=(corners.min(axis=0)-pad).tolist(),root_max_m=(corners.max(axis=0)+pad).tolist(),max_corner_norm_m=float(np.max(np.linalg.norm(corners,axis=1)))+pad)
    # Same-model primitive halfsize semantics, no extra compile/forward or mesh pass.
    if typ==int(mujoco.mjtGeom.mjGEOM_CYLINDER):row['primitive_expected_halfsize_error_m']=float(np.max(np.abs(box[3:]-np.array([m.geom_size[g,0],m.geom_size[g,0],m.geom_size[g,1]]))))
  rows.append(row)
 def bounds(sub):
  valid=[r for r in sub if r['valid_bound']];complete=len(valid)==len(sub)and bool(sub);complete=complete and len(ids)==311
  return dict(geom_count=len(sub),valid_bounds=len(valid),complete=complete,min_m=np.min([r['root_min_m']for r in valid],axis=0).tolist()if complete else None,max_m=np.max([r['root_max_m']for r in valid],axis=0).tolist()if complete else None,max_corner_norm_m=max(r['max_corner_norm_m']for r in valid)if complete else None)
 allbox=bounds(rows);colbox=bounds([r for r in rows if r['collision_masks_nonzero']]);wheels=[]
 for side in('left','right'):
  joint=m.joint(side+'_wheel_spin');body=int(m.jnt_bodyid[joint.id]);axis_root=rootR.T@d.xmat[body].reshape(3,3)@m.jnt_axis[joint.id];tire=m.geom(side+'_tire')
  wheels.append(dict(side=side,joint=joint.name,joint_id=int(joint.id),qpos_adr=int(m.jnt_qposadr[joint.id]),axis_local=m.jnt_axis[joint.id].tolist(),axis_root=axis_root.tolist(),joint_anchor_root=((d.xanchor[joint.id]-rootpos)@rootR).tolist(),tire_geom_id=int(tire.id),tire_type=int(m.geom_type[tire.id]),tire_center_root=((d.geom_xpos[tire.id]-rootpos)@rootR).tolist(),wheel_spin_q=float(d.qpos[int(m.jnt_qposadr[joint.id])]),hip=float(d.qpos[int(m.jnt_qposadr[m.joint(side+'_hip').id])]),crank=float(d.qpos[int(m.jnt_qposadr[m.joint(side+'_crank').id])]))
 radius=allbox['max_corner_norm_m'];inflation=None
 if radius is not None:
  ds=2*radius*math.sin(.15);lo=np.asarray(allbox['min_m'])-ds;hi=np.asarray(allbox['max_m'])+ds;lo[1]-=.2;hi[1]+=.2
  inflation=dict(each_RPY_error_bound_rad=.1,angular_distance_triangle_bound_rad=.3,rigid_fixed_joint_displacement_bound_m=ds,formula='2*rmax*sin((abs(dr)+abs(dp)+abs(dy))/2); sum<=.3',plus_original_lateral_offset_bound_m=.2,min_m=lo.tolist(),max_m=hi.tolist(),not_joint_variation_or_dynamic_sweep=True)
 after=[rec(x)for x in inputs];assert after==pins
 result=dict(status='NOMINAL_SOURCE_GEOMETRY_FULL_ENVELOPE'if allbox['complete']else'PARTIAL_UNKNOWN_GEOMETRY_ENVELOPE_NOT_COMPLETE',bbox_all_root3_min_m=allbox['min_m'],bbox_all_root3_max_m=allbox['max_m'],max_corner_norm_m=radius,all_robot=allbox,collision_masks_nonzero=colbox,unknown_flags=unknown,expected_robot_geom_count=311,actual_robot_geom_count=len(ids),world_geoms_excluded=[int(x)for x in np.flatnonzero(m.geom_bodyid==0)],model=dict(nq=m.nq,nv=m.nv,nbody=m.nbody,ngeom=m.ngeom,SDK=mujoco.__version__,source_options_unchanged=True,no_CAD_added=True),nominal_q_eq7=q.tolist(),ROOT=dict(body='chassis',body_id=int(root),joint='floating_base',qpos_adr=adr,world_xyz=rootpos.tolist(),world_rotation=rootR.tolist(),freejoint_qpos=d.qpos[adr:adr+7].tolist()),wheels=wheels,all_geoms=rows,counts=COUNTS.copy(),time_s=float(d.time),affinity=affinity,roundoff_padding_m=pad,source_pins=pins,source_after_same=True,semantics=dict(geom_aabb='geom-local center and halfsize; conservative box, not tight transformed mesh surface',transform='8localcorners -> geom_xmat/xpos world -> ROOT rotation transpose; no second mesh_pos/quat',evidence='installed mjmodel.h471; official MakeBVH AABB(i) +/- AABB(i+3) source',main_source_not_installed_commit_proof=True,nominal_source_geometry_not_measured_robot=True,joint_full_domain_dynamic_swept_volume_proof=False,rigid_RPY_plus_lateral_example=inflation))
 save('RESULT.json',result);STAGE='done'
 note=['# Nominal P0 compiled-geometry envelope','One originalP0 model, one MjData, setter once consuming soleforward; integration/statics/DARE/oldQA0.','Nominal q_eq from own nominal_gain_v2, absolute crank=hip+delta; ROOT chassis frame, wheel phase0.','All robot bodyid>0 geoms versus separate collision-mask OR!=0; world excluded, not an environment corridor collision test.','geom_aabb is local center+halfsize: local8 corners transformed by actual geom pose then into ROOT; mesh scale/PCA already compiled, no double mesh transform.','Boxes enclose primitives/mesh; union is conservative at THIS joint pose, not exact mesh hull or arbitrary-joint sweep.','Any nonfinite/negative/allzero box stays unknown; incomplete envelope fields remain null, no extra run.','Requested top-level bbox_all_root3_min_m / max_m / max_corner_norm_m are in RESULT.','1nm numeric padding is not manufacture/calibration margin.','Example eachRPY error<=.1 yields principal angle<=.3, displacement<=2Rsin(.15); lateral±.2 separately added, fixedjoint rigid rotation only.','Root0 with ground intersection is pose-only: no integration, no physical-contact inference.','Official source: https://raw.githubusercontent.com/google-deepmind/mujoco/main/src/user/user_objects.cc (main not pinned; installed header and primitive numeric check retained).']
 with(D/'NOTE.md').open('x',encoding='utf-8',newline='\n')as f:f.write('\n'.join(note)+'\n')
 print(json.dumps(dict(status=result['status'],counts=COUNTS,bbox_all_root3_min_m=allbox['min_m'],bbox_all_root3_max_m=allbox['max_m'],max_corner_norm_m=radius,all_count=len(rows),collision_count=colbox['geom_count'],unknown_count=len(unknown),affinity=affinity,RESULT=rec(D/'RESULT.json')),ensure_ascii=False))

if __name__=='__main__':
 try:main()
 except BaseException:
  if not(D/'FIRST_ERROR.json').exists():save('FIRST_ERROR.json',dict(stage=STAGE,counts=COUNTS,error=traceback.format_exc(),no_retry=True))
  raise
