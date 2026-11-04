"""Independent MuJoCo nominal counterpart of the selected native contract, not backend equivalence."""
from pathlib import Path
import json,xml.etree.ElementTree as E
import numpy as np,mujoco
D=Path(__file__).resolve().parent;O=D/'contract_parity_mujoco_v1';assert not O.exists();O.mkdir();S=Path('C:/Users/lulu/Desktop/claude/mjcf/chassis_mod4');c=json.loads((D.parent/'mod4_usd_scut_fudan_20261101/candidates/v1/assets/import_contract.json').read_bytes());root=E.parse(S/'scene.xml').getroot();compiler=root.find('compiler')
for key in('meshdir','texturedir'):
 if compiler is not None and compiler.get(key) and not Path(compiler.get(key)).is_absolute():compiler.set(key,str((S/compiler.get(key)).resolve()).replace('\\','/'))
fmt=lambda a:' '.join(format(float(x),'.17g')for x in a)
bodies={x.get('name'):x for x in root.iter('body')};joints={x.get('name'):x for x in root.iter('joint')};geoms={x.get('name'):x for x in root.iter('geom')}
for n,v in c['bodies'].items():
 if n not in bodies:
  assert n in c['roller_joints'];rj=c['roller_joints'][n];parent=bodies[rj['parent']];pv=np.asarray(c['bodies'][rj['parent']]['neutral_position_m']);pos=np.asarray(v['neutral_position_m'])-pv;body=E.SubElement(parent,'body',name=n,pos=fmt(pos),quat=fmt(v['neutral_quat_wxyz']));bodies[n]=body;E.SubElement(body,'joint',name=n,type='hinge',axis='0 1 0',limited='false',damping=str(rj['damping_si']),armature=str(rj['armature']));joints[n]=body.find('joint');gn='guide_wheel_'+n.rsplit('_',1)[1];g=c['geometry'][gn];geoms[gn]=E.SubElement(body,'geom',name=gn,type='cylinder',pos='0 0 0',quat=fmt(g['quat_wxyz']),size=fmt(g['size'][:2]),friction='0.9 0.005 0.0001',contype='1',conaffinity='1',rgba='.18 .18 .18 1',group='3')
 body=bodies[n];it=body.find('inertial')
 if it is not None:body.remove(it)
 body.insert(0,E.Element('inertial',mass=str(v['mass_kg']),pos=fmt(v['com_m']),quat=fmt(v['principal_axes_wxyz']),diaginertia=fmt(v['diagonal_inertia_kg_m2'])))
for n,j in joints.items():
 v=c['joints'].get(n,c['roller_joints'].get(n))
 if v is None:continue
 j.set('armature',str(v['armature']));j.set('damping',str(v['damping_si']));lim=v['limits_si'];j.set('limited','false'if lim is None else'true')
 if lim is not None:j.set('range',fmt(lim))
 if n.endswith('gas_slide'):j.set('stiffness','2000');j.set('springref','.2')
# The authored geometry record retained the old chassis-relative position of the reparented guide geoms.
# Guide bodies now carry that translation; their geom local centre is zero as in the roller derivation.
for n,v in c['geometry'].items():
 if v['visual']or n not in geoms or n.startswith('guide_wheel_'):continue
 g=geoms[n];typ={2:('sphere',1),3:('capsule',2),4:('ellipsoid',3),5:('cylinder',2),6:('box',3)}.get(v['type'])
 if typ is None:continue
 for a in('fromto','euler','axisangle','xyaxes','zaxis'):g.attrib.pop(a,None)
 g.set('type',typ[0]);g.set('size',fmt(v['size'][:typ[1]]));g.set('pos',fmt(v['position_m']));g.set('quat',fmt(v['quat_wxyz']))
opt=root.find('option');opt.set('timestep','.0025');opt.set('iterations','32')
path=O/'scene.xml';E.indent(root,space='  ');E.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True);m=mujoco.MjModel.from_xml_path(str(path));data=mujoco.MjData(m);data.qpos[:7]=[0,0,0,1,0,0,0];mujoco.mj_forward(m,data);errors=[]
def R(q):a=np.empty(9);mujoco.mju_quat2Mat(a,np.asarray(q,dtype=float));return a.reshape(3,3)
for n,v in c['bodies'].items():
 i=m.body(n).id;A=R(m.body_iquat[i])@np.diag(m.body_inertia[i])@R(m.body_iquat[i]).T;B=R(v['principal_axes_wxyz'])@np.diag(v['diagonal_inertia_kg_m2'])@R(v['principal_axes_wxyz']).T;errors.append(max(abs(float(m.body_mass[i])-v['mass_kg']),float(np.max(abs(m.body_ipos[i]-v['com_m']))),float(np.max(abs(A-B))),float(np.max(abs(data.xpos[i]-v['neutral_position_m'])))))
assert m.nbody-1==31 and m.njnt-1==30 and m.neq==10,(m.nbody,m.njnt,m.neq);assert max(errors)<1e-8,max(errors)
for n,v in dict(c['joints'],**c['roller_joints']).items():
 try:i=m.joint(n).id
 except KeyError:continue
 assert bool(m.jnt_limited[i])==(v['limits_si']is not None),n
 if v['limits_si']is not None:assert np.max(abs(m.jnt_range[i]-v['limits_si']))<1e-10,n
r=dict(kind='CONTRACT_PARITY_NOMINAL_MUJOCO_NOT_PHYSX_OR_HARDWARE_QUALIFICATION',scene=str(path),bodies=m.nbody-1,coordinates=m.njnt-1,equalities=m.neq,total_mass_kg=float(m.body_mass.sum()),max_mass_COM_fullI_neutral_position_error=max(errors),all_authored_joint_limits_and_enable_flags_match=True,original_sources_modified=False,new_hip_crank_gas_or_passive_envelope_expansion=False,explicit_changes=['correct selected 31-body MCI','add eight source-declared passive guide roller bodies/joints/cylinders','use native authored passive bounds','nominal gas400/k2000/d3','control source physics timestep .0025'],not_claimed=['backend solver/contact equivalence','complete visual mesh parity','correct actor observation frame','specified rear-leg posture feasibility','native training or skill performance']);(D/'CONTRACT_PARITY_MUJOCO_BUILD_V1.json').write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r,indent=2))
