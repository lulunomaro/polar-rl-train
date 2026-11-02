"""Generate isolated, auditable MOD4v1 derivatives. CPU compile only; no state/time APIs.
Primary target is the actual SHA-pinned USD, not stale contract geometry origins.
USD angular Drive damping follows the existing exporter convention (per degree).
An optional contract damping variant is NEVER silently substituted.
Run with existing Python + numpy + mujoco. No SDK/project module imports.
"""
from pathlib import Path
import argparse, copy, csv, difflib, hashlib, json, traceback, xml.etree.ElementTree as ET
import numpy as np

HERE=Path(__file__).resolve().parent
BASE=Path(r'F:\RMPOLAR-RL\traditional_control_20261101\model\mod4_400N.xml')
V1=Path(r'F:\RMPOLAR-RL\mod4_usd_scut_fudan_20261101\candidates\v1')
EXPECTED_BASE='5d52284a618c95ac49c97666b00f9e4567d20abb4728e322dc8651f07f4ba0ee'
EXPECTED_USD='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
EXPECTED_CONTRACT='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
ORDER=['left_hip','left_crank','left_wheel_spin','right_hip','right_crank','right_wheel_spin']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def js(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def fmt(x):return ' '.join(format(float(v),'.17g') for v in x)
def six(A):return [A[0,0],A[1,1],A[2,2],A[0,1],A[0,2],A[1,2]]
def record(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def rot(q):
    w,x,y,z=np.array(q,float)/np.linalg.norm(q)
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)], [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)], [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def set_mci(el, mass, com, I):
    for k in ['fullinertia','diaginertia','quat','euler','axisangle','xyaxes','zaxis']:el.attrib.pop(k,None)
    el.set('mass',format(float(mass),'.17g'));el.set('pos',fmt(com));el.set('fullinertia',fmt(six(I)))
def emit(root,name,original):
    path=HERE/name;assert not path.exists(),str(path)+' already exists'
    text="<?xml version='1.0' encoding='utf-8'?>\n"+ET.tostring(root,encoding='unicode')
    path.write_bytes(text.encode('utf-8'))
    diff=''.join(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile=str(BASE),tofile=str(path)))
    (HERE/(name+'.diff')).write_text(diff,encoding='utf-8')
    return path

def compile_only(path, expected):
    try: import mujoco
    except ImportError as e:return {'status':'NOT_RUN_EXISTING_MUJOCO_MISSING','error':str(e),'install_attempted':False}
    # Never instantiate MjData or call forward/step/reset/viewer.
    m=mujoco.MjModel.from_xml_path(str(path))
    s={'status':'PASS_COMPILE_ONLY','mujoco':mujoco.__version__,'nbody_including_world':m.nbody,'robot_body_count':m.nbody-1,'njnt_including_free':m.njnt,'nq':m.nq,'nv':m.nv,'nu':m.nu,'neq':m.neq,'ngeom_including_ground':m.ngeom,'mesh_count':m.nmesh,'mass_sum_kg':float(m.body_mass.sum()),'physics_dt_s':m.opt.timestep,'time_advanced_s':0,'MjData_created':False,'mj_forward_calls':0,'mj_step_calls':0,'body_com_inertia_max_errors':{}}
    for n,b in expected.items():
        bid=m.body(n).id; R=rot(m.body_iquat[bid]);I=R@np.diag(m.body_inertia[bid])@R.T
        s['body_com_inertia_max_errors'][n]={'mass_kg':float(m.body_mass[bid]-b['mass_kg']),'com_m':float(np.max(np.abs(m.body_ipos[bid]-b['com_m']))),'inertia_kg_m2':float(np.max(np.abs(I-b['I'])))}
    s['actuated_joint_order']=[m.joint(int(m.actuator_trnid[i,0])).name for i in range(m.nu)];assert s['actuated_joint_order']==ORDER
    s['joint_table']=[]
    for i in range(m.njnt):
        n=m.joint(i).name;v=int(m.jnt_dofadr[i]);q=int(m.jnt_qposadr[i])
        s['joint_table'].append({'index':i,'name':n,'body':m.body(int(m.jnt_bodyid[i])).name,'type':int(m.jnt_type[i]),'qposadr':q,'dofadr':v,'axis':m.jnt_axis[i].tolist(),'range':m.jnt_range[i].tolist(),'limited':bool(m.jnt_limited[i]),'armature':float(m.dof_armature[v]),'damping_si':float(m.dof_damping[v]),'stiffness':float(m.jnt_stiffness[i]),'springref':float(m.qpos_spring[q])})
    s['actuator_table']=[{'index':i,'name':m.actuator(i).name,'joint':m.joint(int(m.actuator_trnid[i,0])).name,'gear':m.actuator_gear[i].tolist(),'ctrlrange':m.actuator_ctrlrange[i].tolist(),'forcerange':m.actuator_forcerange[i].tolist()} for i in range(m.nu)]
    return s

def main(roller_source='usd'):
    assert sha(BASE)==EXPECTED_BASE
    assert sha(V1/'assets/robot.usd')==EXPECTED_USD
    assert sha(V1/'assets/import_contract.json')==EXPECTED_CONTRACT
    source=js(HERE/'SOURCE_AUDIT_DATA.json');usd=source['usd'];meas=js(HERE/'ALIGNMENT_MEASUREMENTS.json');contract=js(V1/'assets/import_contract.json')
    original=BASE.read_text(encoding='utf-8');root=ET.fromstring(original);full=copy.deepcopy(root);partial=copy.deepcopy(root)
    mapping={r['usd_body']:r['old_mjcf_body'] for r in meas['frame_mapping']};inverse={v:k for k,v in mapping.items()}
    assert len(mapping)==31
    oldbody=source['old_compile']['bodies']
    frames={}
    def frame(n):
        if n in frames:return frames[n]
        b=oldbody[n];r=rot(b['parent_relative_quat_wxyz']);p=np.array(b['parent_relative_position_m'])
        if b['parent']=='world':value=(p,r)
        else:
            pp,rr=frame(b['parent']);value=(pp+rr@p,rr@r)
        frames[n]=value;return value
    p0,R0=frame('chassis');targets={};changes=[]
    for name,ub in usd['bodies'].items():
        on=mapping[name];pM,RM=frame(on);pM=R0.T@(pM-p0);RM=R0.T@RM
        pU=np.array(ub['base_relative_position_m']);RU=np.array(ub['base_relative_rotation_col'])
        # Coordinates in MJCF body from USD body: x_M=t+R_MU*x_U.
        R_MU=RM.T@RU;t_MU=RM.T@(pU-pM)
        com=t_MU+R_MU@np.array(ub['com_m']);I=R_MU@np.array(ub['full_inertia_kg_m2'])@R_MU.T;I=(I+I.T)/2
        assert np.min(np.linalg.eigvalsh(I))>0
        el=full.find(".//body[@name='%s']/inertial"%on)
        before=dict(el.attrib);set_mci(el,ub['mass_kg'],com,I)
        target={'mass_kg':ub['mass_kg'],'com_m':com.tolist(),'I':I.tolist()};targets[name]=target
        changes.append({'usd_body':name,'old_mjcf_body':on,'rotation_USD_to_MJCF_col':R_MU.tolist(),'translation_USD_to_MJCF_m':t_MU.tolist(),'before_xml':before,'after_xml':dict(el.attrib),'mass_delta_kg':ub['mass_kg']-oldbody[on]['mass_kg']})
        if name in ['chassis','left_shin','right_shin']:
            set_mci(partial.find(".//body[@name='%s']/inertial"%on),ub['mass_kg'],com,I)
    # Only the dependency resolver path changes; original STL bytes are referenced read-only.
    meshdir='../../traditional_control_20261101/model/assets'
    full.find('compiler').set('meshdir',meshdir);partial.find('compiler').set('meshdir',meshdir)
    choices=[]
    for r in meas['joint_mapping']:
        uj=r['usd_joint'];oj=r['old_mjcf_joint'];el=full.find(".//worldbody//joint[@name='%s']"%oj);assert el is not None
        sa=usd['joints'][uj]['attrs']
        if r['usd_child'].startswith('guide_roller'):
            damping = r['usd_damping_si'] if roller_source=='usd' else r['contract_damping_si']
            el.set('damping',format(damping,'.17g'));el.set('armature',format(float(contract['joints'][uj]['armature']),'.17g'));el.set('name',uj)
            choices.append({'joint':uj,'USD_authored_angular_damping_per_degree':sa['drive:angular:physics:damping'],'USD_converted_SI_damping':r['usd_damping_si'],'contract_damping_si':r['contract_damping_si'],'chosen_damping_si':damping,'selected_source':roller_source,'USD_armature_authored':False,'contract_armature_chosen':contract['joints'][uj]['armature'],'flag':'USD_CONTRACT_GUIDE_DAMPING_UNIT_DISAGREEMENT'})
        else:
            # Keep all other passive damping, axes and armatures, matching static USD
            # to float precision. This is not a task runtime damping=0 override.
            lim=r['usd_limits_si']
            if lim is None:
                el.attrib.pop('range',None);el.set('limited','false')
            else:
                el.set('range',fmt(lim));el.set('limited','true')
    for r in meas['geometry_mapping']:
        if not r['usd_body'].startswith('guide_roller'):continue
        ug=r['usd_geometry'];og=r['old_mjcf_geometry'];el=full.find(".//geom[@name='%s']"%og);assert el is not None
        sg=usd['geometry'][ug];a=sg['attrs'];assert sg['type']=='Cylinder'
        el.set('size',fmt([a['radius'],a['height']/2]));el.set('pos',fmt(np.array(sg['local_transform_row'])[3,:3]));el.set('quat',fmt(a['xformOp:orient']));el.set('name',ug)
        # USD material provides only sliding mu; retain explicit MJCF torsional/rolling losses.
        mat=usd['materials'][sg['physics_material']];el.set('friction',fmt([mat['physics:dynamicFriction'],r['old_friction'][1],r['old_friction'][2]]))
    # Replace names only by evidence-established position/axis mapping. Preserve DOF/XML order.
    for on,name in inverse.items():
        if name==on:continue
        full.find(".//body[@name='%s']"%on).set('name',name)
        for ex in full.findall('contact/exclude'):
            for k in ['body1','body2']:
                if ex.get(k)==on:ex.set(k,name)
    # Verify closures: the identical body frame mapping makes anchor components comparable.
    for r in meas['closures']:
        name=r['name'];ex=full.find("equality/connect[@name='%s']"%name)
        for key,bodykey,pk in [('site1','body0','usd_local_pos0'),('site2','body1','usd_local_pos1')]:
            site=full.find(".//site[@name='%s']"%ex.get(key));assert site is not None
            assert np.max(np.abs(np.fromstring(site.get('pos'),sep=' ')-np.array(r[pk])))<1e-7
    for tag in ['equality','actuator','contact','sensor','option','default']:
        # Contact body rename is immaterial here since old exclusions have no guide bodies.
        assert ET.tostring(full.find(tag))==ET.tostring(root.find(tag)),tag+' changed'
    assert len(full.findall('.//body'))==31
    assert len(full.findall('.//body/geom'))==311
    # Primary target uses USD-literal damping units; contract variant has explicit filename.
    full_name='mod4v1_fullaligned_candidate.xml' if roller_source=='usd' else 'mod4v1_contract_guide_damping_candidate.xml'
    primary=emit(full,full_name,original)
    diagnostic=emit(partial,'mod4v1_three_mci_diagnostic.xml',original)
    receipt={'mode':'SRC_ONLY','status':'GENERATED_STATIC_CANDIDATE_WITH_DECLARED_CROSS_ENGINE_CHOICES','base':record(BASE),'source_usd':record(V1/'assets/robot.usd'),'source_contract':record(V1/'assets/import_contract.json'),
             'primary':record(primary),'diagnostic':record(diagnostic),'body_frame_mapping':mapping,'mci_changes':changes,'guide_semantic_choices':choices,
             'critical_flags':['NOT_PHYSX_OR_FULLDR_VALIDATED','USD_CONTRACT_GUIDE_DAMPING_UNIT_DISAGREEMENT','GUIDE_ARMATURE_ZERO_FROM_CONTRACT_NOT_AUTHORED_USD','MUJOCO_EXTRA_TORSIONAL_ROLLING_FRICTION_INHERITED','MUJOCO_SOLVER_CONTACTS_NOT_PHYSX_EQUIVALENT','RUNTIME_DAMPING_ZERO_OVERRIDE_NOT_APPLIED','HARDWARE_MCI_AND_TORQUE_SPEED_UNCALIBRATED'],
             'retained':{'option':root.find('option').attrib,'actuator_order':ORDER,'all_6_connect_closures_and_4_mimics_byte_equal':True,'actuators_contact_exclusions_sensors_defaults_byte_equal':True,'nonroller_meshes_unchanged':True,'gas_slide_values':{side:root.find(".//worldbody//joint[@name='%s_gas_slide']"%side).attrib for side in ['left','right']},'DOF_order_preserved':True,'root_spawn_height_m':contract['spawn_height_m'],'leg_passive_damping_si':0.2,'wheel_passive_damping_si':0.015},
             'not_performed':['simulation','state_allocation','forward_dynamics','RL','DR sampling','hardware/SDK operation','network/SSH','Git','package installation']}
    meshes=[];prov=js(BASE.parents[1]/'MODEL_PROVENANCE.json')
    for el in root.findall('asset/mesh'):
        p=(HERE/meshdir/el.get('file')).resolve();assert p.is_file(),str(p)
        meta=record(p);meta.update(mesh_name=el.get('name'),xml_file=el.get('file'),scale=el.get('scale','1 1 1'),expected_provenance_sha256=prov['files']['model/assets/'+el.get('file')]['sha256'])
        assert meta['sha256']==meta['expected_provenance_sha256'];meshes.append(meta)
    (HERE/'MESH_DEPENDENCIES.json').write_text(json.dumps({'meshdir':meshdir,'file_count':len(meshes),'total_bytes':sum(x['bytes'] for x in meshes),'all_exist_and_hash_match_original_provenance':True,'portable_without_relocating_referenced_legacy_assets':False,'meshes':meshes},indent=2),encoding='utf-8')
    for label,path,expected in [('primary',primary,targets),('diagnostic',diagnostic,{k:v for k,v in targets.items() if k in ['chassis','left_shin','right_shin']})]:
        try: receipt[label+'_compile']=compile_only(path,expected)
        except Exception:
            receipt[label+'_compile']={'status':'FAILED_COMPILE_ONLY','error':traceback.format_exc()}
            (HERE/(label+'_COMPILE_FAILURE_001.txt')).write_text(receipt[label+'_compile']['error'],encoding='utf-8')
    receipt['source_files_unchanged']=all(not r['exists'] or sha(r['path'])==r['sha256'] for r in source['source_files'])
    assert receipt['source_files_unchanged']
    (HERE/'DERIVATION_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    with (HERE/'BODY_MCI_TABLE.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['usd_body','old_body','old_mass_kg','new_mass_kg','old_com_x_m','old_com_y_m','old_com_z_m','new_com_x_m','new_com_y_m','new_com_z_m','new_ixx','new_iyy','new_izz','new_ixy','new_ixz','new_iyz'])
        for ch in changes:
            n=ch['usd_body'];old=oldbody[ch['old_mjcf_body']];t=targets[n];w.writerow([n,ch['old_mjcf_body'],old['mass_kg'],t['mass_kg'],*old['com_m'],*t['com_m'],*six(np.array(t['I']))])
    print(json.dumps({'primary':receipt['primary'],'diagnostic':receipt['diagnostic'],'primary_compile':{k:v for k,v in receipt['primary_compile'].items() if k not in ['body_com_inertia_max_errors','joint_table','actuator_table']},'diagnostic_compile':{k:v for k,v in receipt['diagnostic_compile'].items() if k not in ['body_com_inertia_max_errors','joint_table','actuator_table']},'flags':receipt['critical_flags']},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--roller-damping-source',choices=['usd','contract'],default='usd');a=p.parse_args()
    try:main(a.roller_damping_source)
    except Exception:
        (HERE/'DERIVATION_FAILURE_001.txt').write_text(traceback.format_exc(),encoding='utf-8')
        raise
