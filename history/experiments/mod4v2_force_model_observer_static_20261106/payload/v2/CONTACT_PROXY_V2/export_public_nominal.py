"""Offline HW300N60 XML/metadata export; no simulator, mesh or episode reads."""
from pathlib import Path
import hashlib, importlib.util, json, math, os
import xml.etree.ElementTree as ET
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import numpy as np
D=Path(__file__).resolve().parent
PACKAGE=D.parent.parent/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package'
XML=PACKAGE/'mjcf/scene.xml'
XML_SHA='c19c72d2690dce90fdef56bebd3b36e4c319d47b8ac7152cf42b2d01f6dfd125'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def numbers(s,default):return list(map(float,s.split())) if s is not None else list(default)
def quaternion(q):
    w,x,y,z=np.asarray(q,float)/np.linalg.norm(q)
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
                     [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
                     [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def new_json(p,obj):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(obj,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def main():
    target=D/'PUBLIC_NOMINAL_CONSTANTS.json'
    assert not target.exists(),'Do not replace an exported version'
    assert digest(XML)==XML_SHA,'HW300N60 source identity changed'
    param_path=PACKAGE/'model_parameters.json';manifest_path=PACKAGE/'reports/model_manifest.json'
    params=json.loads(param_path.read_text(encoding='utf-8'));manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    gain_path=D.parent/'nominal_gain_v2.json';gain_root=json.loads(gain_path.read_text(encoding='utf-8'))
    assert gain_root['model_SHA']==XML_SHA
    gain=gain_root['gain'];kin_path=PACKAGE/'kinematics_v2.py'
    spec=importlib.util.spec_from_file_location('_contact_v2_public_source_kinematics',kin_path)
    kin=importlib.util.module_from_spec(spec);spec.loader.exec_module(kin)
    boundaries={s:kin.boundary_report(s) for s in ('left','right')}
    root=ET.parse(XML).getroot();default=dict(root.find('default/joint').attrib)
    bodies=[];joints=[];sites=[]
    def body(e,parent):
        ine=e.find('inertial');assert ine is not None,'Explicit public MCI required'
        raw_q=numbers(ine.get('quat'),[1,0,0,0])
        if ine.get('fullinertia'):
            full=numbers(ine.get('fullinertia'),[]);assert len(full)==6
        else:
            diag=numbers(ine.get('diaginertia'),[]);assert len(diag)==3
            ir=quaternion(raw_q);I=ir@np.diag(diag)@ir.T
            full=[float(I[0,0]),float(I[1,1]),float(I[2,2]),float(I[0,1]),float(I[0,2]),float(I[1,2])]
        bodies.append(dict(name=e.get('name'),parent=parent,pos_m=numbers(e.get('pos'),[0,0,0]),
            quat_wxyz=numbers(e.get('quat'),[1,0,0,0]),mass_kg=float(ine.get('mass')),
            com_local_m=numbers(ine.get('pos'),[0,0,0]),inertia_full_body=full,
            joint_names=[j.get('name') for j in e.findall('joint')],
            source_inertial_quat_wxyz=raw_q,source_diaginertia_kgm2=numbers(ine.get('diaginertia'),[]),
            inertia_frame='full tensor rotated from source principal frame into BODY; not diagonal in BODY'))
        for j in e.findall('joint'):
            a={**default,**j.attrib};limit=a.get('limited')=='true'
            rg=numbers(a.get('range'),[0,0]) if limit else [None,None]
            rg=[None if v is None or not math.isfinite(v) else v for v in rg]
            joints.append(dict(name=a['name'],body=e.get('name'),type=a.get('type','hinge'),
                axis=numbers(a.get('axis'),[0,0,1]),pos_m=numbers(a.get('pos'),[0,0,0]),
                limited=limit,range_rad_or_m=rg,damping=float(a.get('damping',0)),armature=float(a.get('armature',0)),
                stiffness_N_per_m=float(a.get('stiffness',0)),springref_m=float(a.get('springref',0)),
                frictionloss=float(a.get('frictionloss',0)),ref=float(a.get('ref',0))))
        for s in e.findall('site'):sites.append(dict(name=s.get('name'),body=e.get('name'),pos_m=numbers(s.get('pos'),[0,0,0])))
        for b in e.findall('body'):body(b,e.get('name'))
    chassis=root.find("worldbody/body[@name='chassis']");body(chassis,None)
    assert len(bodies)==31 and len(joints)==30
    equality=root.find('equality');eq=[dict(type=e.tag,**e.attrib)for e in equality]
    assert sum(e['type']=='connect'for e in eq)==6 and sum(e['type']=='joint'for e in eq)==4
    gas=[j for j in joints if j['name'].endswith('_gas_slide')]
    assert len(gas)==2 and all(abs(j['springref_m']-.1706394410901294)<1e-14 and j['stiffness_N_per_m']==2000. and j['damping']==3. for j in gas)
    assert all(not j['limited']for j in joints if j['name']in('left_hip','left_crank','right_hip','right_crank','left_drive_hip_spin','left_drive_input_spin','right_drive_hip_spin','right_drive_input_spin'))
    collision=[]
    for e in chassis.iter('geom'):
        if e.get('name')in('left_tire','right_tire')or(e.get('name','').startswith('guide_wheel_')):
            collision.append(dict(e.attrib))
    assert len(collision)==10 and all(g['type']=='cylinder'for g in collision)
    q=gain['q'];tau=gain['tau'];sources=[XML,param_path,manifest_path,kin_path,gain_path]
    output=dict(schema='public_nominal_contact_proxy_v2_HW300N60',source_xml_sha256=XML_SHA,
        sources=[dict(path=str(p),bytes=p.stat().st_size,SHA=digest(p))for p in sources],
        frame='chassis BODY; authored root world placement discarded',bodies=bodies,joints=joints,sites=sites,
        motors=[dict(e.attrib)for e in root.find('actuator')],equalities=eq,
        pins_xz_m=manifest['neutral_skeleton_xz_m'],mechanical_delta_boundaries=boundaries,
        mechanical_joint_bounds=params['per_side_joint_bounds_SI'],
        nominal_q4=[q[3],q[3]+q[4],q[5],q[5]+q[6]],nominal_ff_tau4=[tau[i]for i in (0,1,3,4)],
        nominal_proper_root_B=[0.,0.,9.81],total_nominal_mass_kg=sum(b['mass_kg']for b in bodies),
        collision_primitives=collision,source_option=dict(root.find('option').attrib),
        mechanical_identity=dict(model='MOD4v2-HW300N60',nominal_extended_force_N=300.,eye_m=[.14,.20],stroke_m=.06,
            force_curve_calibrated=False,damping_calibrated=False,active_angles='absolute continuous outputs; no active wrapping or old windows'),
        dynamic_omissions=['No wheel spin/drive reaction/contact moment observation','No guide spin observation; guide support identity unknown',
            'No physical rotor beyond declared armature mapping; not complete constrained RNE','Nominal rigid closure branch; soft equality errors/DR/model errors unobserved'])
    assert abs(output['total_nominal_mass_kg']-14.294140288606286)<1e-12
    new_json(target,output)
    print(json.dumps(dict(status='EXPORTED_PUBLIC_P0_HW300N60_PARAMETERS_NO_SIMULATOR',bodies=len(bodies),joints=len(joints),
        mass_kg=output['total_nominal_mass_kg'],constants_SHA=digest(target),bounds={s:[v['delta_min_rad'],v['delta_max_rad']]for s,v in boundaries.items()})))
if __name__=='__main__':main()
