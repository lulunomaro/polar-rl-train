"""One model boot, 30 declared static configurations, no integration or control."""
from pathlib import Path
import hashlib,importlib.util,json,math,sys,traceback,xml.etree.ElementTree as ET
import numpy as np
import mujoco
D=Path(__file__).resolve().parent;R=D.parent;O=R.parent/'traditional_control_20261101'
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
method=load(D/'METHOD.json');lock=load(D/'SOURCE_LOCK.json')
assert sha(D/'METHOD.json')==lock['method_SHA']
for s in lock['sources']:assert sha(Path(s['path']))==s['SHA']
counts={k:0 for k in method['blocked_integrators']};counts['mj_forward']=0
original={};rows=[];boot=0
for name in method['blocked_integrators']:
    assert hasattr(mujoco,name),('missing integration boundary',name)
    original[name]=getattr(mujoco,name)
    def reject(*a,_name=name,**kw):
        counts[_name]+=1;raise RuntimeError('INTEGRATOR_BLOCKED '+_name)
    setattr(mujoco,name,reject)
forward_original=mujoco.mj_forward
def forward(m,d):
    counts['mj_forward']+=1;forward_original(m,d)
    assert d.time==0 and np.all(d.qvel==0)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m
try:
    kin=module('lgcp_nominal_kinematics',O/'kinematics.py')
    helper=module('lgcp_mesh_support',R/'MODEL_AUDIT/mesh_support_helper_v1/mesh_support.py')
    xml=ET.fromstring((R/'MODEL_AUDIT/mod4v1_usd_source_aligned.xml').read_bytes())
    xml.find('compiler').set('meshdir',str((R/'MODEL_AUDIT').resolve()))
    m=mujoco.MjModel.from_xml_string(ET.tostring(xml,encoding='unicode'));boot=1;d=mujoco.MjData(m)
    cache=helper.TireMeshSupport(m)
    guide=int(m.geom('guide_wheel_05').id);body=int(m.geom_bodyid[guide]);chassis=int(m.body('chassis').id)
    assert m.geom_type[guide]==mujoco.mjtGeom.mjGEOM_CYLINDER and m.body_parentid[body]==chassis
    size=np.asarray(m.geom_size[guide],float);assert size[0]>0 and size[1]>0
    own=[m.geom(i).name for i in range(m.ngeom)if m.geom_bodyid[i]==body]
    assert own==['guide_wheel_05']
    primitive=dict(geom_name='guide_wheel_05',geom_id=guide,type='cylinder',body=m.body(body).name,parent=m.body(chassis).name,
        body_pos_in_chassis_m=m.body_pos[body].tolist(),body_quat=m.body_quat[body].tolist(),
        geom_pos_in_body_m=m.geom_pos[guide].tolist(),geom_quat=m.geom_quat[guide].tolist(),size_m=size.tolist(),
        radius_m=float(size[0]),half_length_m=float(size[1]),same_body_geoms=own,
        joint_axis_in_body=m.jnt_axis[m.joint('guide_roller_05').id].tolist())
    connect=[(x.attrib['site1'],x.attrib['site2'])for x in xml.find('equality').findall('connect')]
    maxclosure=0.;maxsupportgap=0.;maxguideformula=0.;maxrefqerror=0.;geom_axis_chassis=None
    crouch=np.asarray(lock['crouch_q7'][3:7],float)
    for candidate in lock['candidates']:
        target=np.asarray(candidate['q7'][3:7],float)
        for weight in method['reference_weights']:
            qref=(1.-weight)*crouch+weight*target
            for pitch in method['pitches_rad']:
                assert len(rows)<30
                mujoco.mj_resetData(m,d)
                for side,active in (('left',qref[:2]),('right',qref[2:])):
                    values,_=kin.leg_configuration(float(active[0]),float(active[1]),side)
                    for name,value in values.items():d.joint(side+'_'+name).qpos[0]=value
                # Temporary collision-free height only; reported support uses exact rigid-Z normalization below.
                d.qpos[:3]=[0.,0.,1.];d.qpos[3:7]=[math.cos(pitch/2),0.,math.sin(pitch/2),0.]
                d.qvel[:]=0.;d.ctrl[:]=0.;forward(m,d)
                world_contacts=sum((m.geom_bodyid[c.geom1]==0)!=(m.geom_bodyid[c.geom2]==0)for c in d.contact)
                assert world_contacts==0,('unexpected reference-height environment contacts',int(world_contacts))
                shift=cache.root_z_translation(d,plane_z_m=0.,clearance_m=0.);dz=shift['root_dz_m']
                gaps=shift['tire_gap_after_shift_m'];consistent=bool(max(abs(x)for x in gaps.values())<=1e-8)
                maxsupportgap=max(maxsupportgap,max(abs(x)for x in gaps.values()))
                rot=d.geom_xmat[guide].reshape(3,3);axis=rot[:,2]
                vertical_support=float(size[0]*math.hypot(float(rot[2,0]),float(rot[2,1]))+size[1]*abs(float(rot[2,2])))
                center=np.asarray(d.geom_xpos[guide],float).copy();center[2]+=dz
                minimum=float(center[2]-vertical_support);margin=minimum-.06
                rootheight=float(1.+dz)
                rootrot=d.xmat[chassis].reshape(3,3)
                local_axis=rootrot.T@axis
                if geom_axis_chassis is None:geom_axis_chassis=local_axis.tolist()
                assert np.allclose(local_axis,geom_axis_chassis,atol=1e-12,rtol=0.)
                guide_formula=rootheight+float((rootrot@m.body_pos[body])[2])-vertical_support
                maxguideformula=max(maxguideformula,abs(guide_formula-minimum))
                closure=max(float(np.linalg.norm(d.site(a).xpos-d.site(b).xpos))for a,b in connect)
                maxclosure=max(maxclosure,closure)
                actualref=np.array([d.joint('left_hip').qpos[0],d.joint('left_crank').qpos[0],d.joint('right_hip').qpos[0],d.joint('right_crank').qpos[0]])
                absref=np.array([qref[0],qref[0]+qref[1],qref[2],qref[2]+qref[3]])
                maxrefqerror=max(maxrefqerror,float(np.max(np.abs(actualref-absref))))
                assert np.isfinite([rootheight,minimum,margin,vertical_support,closure]).all()
                rows.append(dict(candidate=candidate['name'],weight=weight,pitch_rad=pitch,roll_rad=0.,yaw_rad=0.,
                    ideal_absolute_ref4_rad=absref.tolist(),root_supported_z_m=rootheight,tire_gap_after_rigid_shift_m=gaps,
                    two_tire_co_support_numerically_consistent=consistent,guide_center_world_m=center.tolist(),
                    guide_localZ_axis_world=axis.tolist(),cylinder_vertical_support_m=vertical_support,
                    guide_minimum_world_z_m=minimum,clearance_over_6cm_plane_m=margin,
                    sign=('POSITIVE'if margin>0 else'NEGATIVE'if margin<0 else'ZERO')if consistent else'UNKNOWN_CO_SUPPORT',
                    closure_residual_m=closure,wheel_spin_phase_rad=[0.,0.]))
    assert len(rows)==30 and counts['mj_forward']==30 and all(counts[k]==0 for k in method['blocked_integrators'])
    assert maxguideformula<1e-12 and maxrefqerror==0.
    primitive['cylinder_axis_in_chassis_at_hinge0']=geom_axis_chassis
    output=dict(kind='NOMINAL_REFERENCE_STATIC_CLEARANCE_NOT_ACTUAL_4505_OR_OPERATING_LIMIT',method_SHA=sha(D/'METHOD.json'),
        source_lock_SHA=sha(D/'SOURCE_LOCK.json'),script_SHA=sha(Path(__file__)),engine=mujoco.__version__,numpy=np.__version__,
        model=dict(nq=m.nq,nv=m.nv,nbody=m.nbody,ngeom=m.ngeom,nmesh=m.nmesh),model_boots=boot,calls=counts,time_s=float(d.time),
        primitive=primitive,immutable_tire_caches={n:dict(geom_id=x['geom_id'],mesh_id=x['mesh_id'],vertices=len(x['vertices_local_compiled']))for n,x in cache.meshes.items()},
        consistency=dict(max_closure_residual_m=maxclosure,max_tire_support_residual_m=maxsupportgap,
            max_compiled_vs_offset_formula_error_m=maxguideformula,max_ref_q_error_rad=maxrefqerror),
        rows=rows,raw_files_read=0,mesh_asset_hashes=0,DR_samples_read=0,controller_changes=False,gain_selected=False,
        actual4505_clearance_claim=False,static_force_equilibrium_claim=False,dynamic_stability_claim=False,
        confidence_increase=False,PH7_pending=True)
    with (D/'STATIC_GEOMETRY.json').open('x',encoding='utf-8')as f:json.dump(output,f,separators=(',',':'),allow_nan=False);f.write('\n')
    table=[]
    for c in lock['candidates']:
        for w in method['reference_weights']:
            rs=[r for r in rows if r['candidate']==c['name']and r['weight']==w]
            table.append(dict(candidate=c['name'],weight=w,clearance_mm=[r['clearance_over_6cm_plane_m']*1000 for r in rs],
                root_z_m=[r['root_supported_z_m']for r in rs],signs=[r['sign']for r in rs]))
    print(json.dumps(dict(status='STATIC_GRID_COMPLETED_NO_INTEGRATION',calls=counts,model=output['model'],primitive=primitive,
        consistency=output['consistency'],pitch_columns=method['pitches_rad'],table=table,
        result_bytes=(D/'STATIC_GEOMETRY.json').stat().st_size,result_SHA=sha(D/'STATIC_GEOMETRY.json')),indent=2))
except BaseException:
    with (D/'PARTIAL_ERROR.json').open('x',encoding='utf-8')as f:json.dump(dict(status='PARTIAL_UNKNOWN_NOT_SEALED',traceback=traceback.format_exc(),model_boots=boot,calls=counts,completed_rows=rows),f,allow_nan=False)
    raise
finally:
    for name,fn in original.items():setattr(mujoco,name,fn)
