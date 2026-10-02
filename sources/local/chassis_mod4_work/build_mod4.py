"""Build a separate MOD4 package from its audited source occurrences."""
from pathlib import Path
from collections import defaultdict
import json,sys,shutil,hashlib
import numpy as np
import trimesh
import xml.etree.ElementTree as ET
from geometry import PARTS,ROT,O,PINS,configuration,angle,cylinder
sys.stdout.reconfigure(encoding='utf8')
WORK=Path(__file__).parent;ROOT=WORK.parent/'chassis_mod4'
for folder in ['assets','reports','tools','isaac']:(ROOT/folder).mkdir(parents=True,exist_ok=True)

def ry(q):
    c,s=np.cos(q),np.sin(q);return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def pt(v,y=0.):return np.array([v[0],y,v[1]])
def fmt(v):return ' '.join(f'{float(x):.12g}' for x in np.asarray(v).ravel())
def el(parent,tag,**attrs):return ET.SubElement(parent,tag,{k.rstrip('_'):str(v) for k,v in attrs.items()})

# This is an operating envelope, not a claim that all CAD joints can move 360 degrees.
# It stays within the continuous source branch, the 150-200 mm gas envelope,
# and the CAD stop clearance. The stronger limits are on knee/rocker/slide,
# present in both MJCF and USD; no tendon is needed for the training envelope.
DIFF0=.45;DIFF_RANGE=[-.25,.85];HIP_RANGE=[-.50,.50]
_,q=configuration(0.,DIFF0)
HIP0=angle(q['W'],np.array([0.,-np.linalg.norm(q['W'])]))
NEUTRAL={};OFFSETS={}
for side in ['left','right']:OFFSETS[side],NEUTRAL[side]=configuration(HIP0,DIFF0,side)

# Bearing visuals are assigned as rigid packages; races are not separate DOFs.
groups={
 'thigh':[104,107,108,114,144,145,159,161,164,165,166],
 'input':[105,106,109,110,111,112,119,122,123,128],
 'coupler':[120], 'rocker':[121,124,126,127,131,132,133],
 'distal':[129], 'shin':[125,130,134,160,162,163],
 'gas_inner':[146,148], 'gas_barrel':[147,149],
 'drive_hip':[142], 'drive_input':[143],
 'wheel':[168,172,173,178,181,183],
}
# The stationary carrier, mounting plate, motor stator and bearing seats attach
# to the shin. Internal gearing is abstracted at the wheel output interface.
groups['shin'] += [167,169,170,171,174,175,176,177,179,180,182,184,185]
group_for={}
for side,delta in [('right',0),('left',91)]:
    for kind,ids in groups.items():
        for i in ids:
            j=i+delta
            if side=='left' and i==183:j=276
            elif side=='left' and i in [184,185]:j=i+90
            assert j not in group_for,(j,kind)
            group_for[j]=side+'_'+kind
for i in range(len(PARTS)):group_for.setdefault(i,'chassis')

ANCHORS={'thigh':('O','K'),'input':('O','A'),'coupler':('A','B'),
 'rocker':('P','C'),'distal':('C','D'),'shin':('K','W'),
 'wheel':('W','K'),'gas_inner':('S','T'),'gas_barrel':('T','S')}
REPS={'thigh':144,'input':119,'coupler':120,'rocker':124,'distal':129,'shin':134,
      'wheel':183,'gas_inner':148,'gas_barrel':149,'drive_hip':142,'drive_input':143}
ORIGINS={'chassis':np.zeros(3)};POSE={}
for side,delta in [('right',0),('left',91)]:
    for kind,i in REPS.items():
        i=276 if side=='left' and i==183 else i+delta
        name=side+'_'+kind;y=-(PARTS[i]['com_mm'][0]-O[0])*.001
        if kind=='wheel':
            # Tire centre is the middle of the 20 mm contact annulus, not the
            # combined aluminum-hub/rubber centre of mass.
            y=-(.5*(PARTS[i]['bbox_mm'][0]+PARTS[i]['bbox_mm'][3])-O[0])*.001
        if kind.startswith('drive_'):
            c=cylinder(i,41);c[0]=PARTS[i]['com_mm'][0]
            center=ROT@(c-O)*.001
            ang=OFFSETS[side]['hip' if kind=='drive_hip' else 'crank']
            R=ry(ang);t=center-R@center;ORIGINS[name]=center
        else:
            a,b=ANCHORS[kind];p=PINS[side];q=NEUTRAL[side]
            R=ry(angle(p[b]-p[a],q[b]-q[a]));t=pt(q[a])-R@pt(p[a])
            ORIGINS[name]=pt(q[a],y)
        POSE[name]=(R,t)
POSE['chassis']=(np.eye(3),np.zeros(3))

old=json.loads((WORK.parent/'rm2025_fixed/model_parameters.json').read_text())
leg=old['leg_motor'].copy();wheel=old['wheel_motor'].copy()
leg['status']='User explicitly confirmed all four MOD4 leg motors are DM8009P, 24 V on 2026-09-10; STEP labels DM8009. Dynamic armature/envelope remain estimates.'
wheel.update(visual_geometry_status='This MOD4 STEP contains the replacement P15.8 gearbox and DM3519 motor.',
    assembly_mass_status='New CAD gearbox mass is computed part by part, not replaced with the stock 0.396 kg gearbox mass.')
wheel.pop('assembly_mass_each_kg',None)
# The bare motor CAD has no material/winding data. Do not use the stock gearbox
# assembly mass, and do not count the old wheel-hub motor a second time.
wheel['bare_motor_mass_assumption_kg']=.16
wheel['bare_motor_mass_status']='Provisional bare motor mass; replacement gearbox is counted separately from CAD solid integrals.'
gas={'force_extended_n':700.,'extended_eye_length_m':.200,'compressed_eye_length_m':.150,
     'nominal_stroke_m':.050,'force_ratio':1.25,'stiffness_n_m':3500.,'damping_n_s_m':3.,
     'status':'Adjustable simulation candidate retained from the earlier design, NOT a verified MOD4 hardware spring. Calibrate preload/stroke before sim-to-real.'}
params={'model':'MOD4','leg_motor':leg,'wheel_motor':wheel,'gas_spring':gas,
        'source_hip_rotation_rad':HIP0,'source_input_difference_rad':DIFF0,
        'operating_source_difference_rad':DIFF_RANGE,'hip_range_rad':HIP_RANGE,'limits':{},
        'joint_offsets_from_cad':OFFSETS,'payload_mass_kg':0.,
        'payload_status':'Only components present in this STEP; battery/gimbal/ammunition not silently added.',
        'physics_dt_s':.0005,'mass_status':'Geometric mass integrals with documented material/motor assumptions; not a weighed competition mass.'}
for side in ['left','right']:
    samples=[configuration(0.,d,side)[0] for d in np.linspace(*DIFF_RANGE,151)]
    lim={}
    for k in ['knee','rocker_pin','coupler_pin','distal_pin','gas_pin','gas_slide']:
        values=[v[k]-OFFSETS[side][k] for v in samples]
        # hip-relative joints already contain the source hip at neutral; the
        # source values here are independent of whole-leg hip rotation.
        lim[k]=[float(min(values)),float(max(values))]
    lim['input_difference_rad']=[d-DIFF0 for d in DIFF_RANGE]
    lim['knee_rad']=lim['knee'];params['limits'][side]=lim

colors={'carbon':[.08,.09,.11,1],'rubber':[.035,.038,.043,1],'steel':[.57,.60,.64,1],
        'polymer':[.15,.17,.19,1],'electronics':[.17,.28,.30,1],'motor':[.22,.24,.26,1],
        'aluminum':[.68,.71,.75,1]}
def material(i):
    n=PARTS[i]['name'].replace('Mirror','')
    if n.startswith(('大腿_MOD','小腿_MOD','小腿连杆')):return 'carbon',1600.
    if '包胶轮' in n:return 'rubber',1250.
    if n.startswith('圆柱齿轮') or any(x in n for x in ['轴承','680','71811','碗组','螺栓','螺母','螺丝','销轴','氮气弹簧内杆','扁头','铜柱']):
        if any(x in n for x in ['轴承座','轴承内座','内圈压片']):return 'aluminum',2700.
        return 'steel',7800.
    if any(x in n for x in ['RM2019','达妙-','继电器','MT2042']):return 'electronics',1500.
    if any(x in n for x in ['DM 8116','3510','MOTOR']):return 'motor',2700.
    if any(x in n for x in ['保护','防护','垫高','顶盖','限位块','玻纤']):return 'polymer',1300.
    return 'aluminum',2700.

SOLIDS=json.loads((WORK/'reports/source_audit.json').read_text())['wheel_solids']
inertial_parts=defaultdict(list);membership=[];assets=[];mesh_hashes={}
for i,p in enumerate(PARTS):
    name=group_for[i];R,t=POSE[name];mat,rho=material(i)
    entries=[(p['volume_mm3']*rho*1e-9,np.array(p['com_mm']),np.array(p['inertia_mm5'])*rho*1e-15)]
    basis=f'assumed density {rho:g} kg/m3, exact B-Rep volume/inertia'
    if i in [135,136,137,138,226,227,228,229]:
        mass=.87 if p['volume_mm3']>1e5 else .06
        entries=[(mass,np.array(p['com_mm']),np.array(p['inertia_mm5'])*mass/p['volume_mm3']*1e-6)]
        basis='DM8009P 0.93 kg/assembly apportioned 0.87/0.06 across its two CAD occurrences; rotor inertia is armature'
    if i in [184,185,274,275]:
        other=(185 if i==184 else 184) if i<200 else (275 if i==274 else 274)
        mass=.16*p['volume_mm3']/(p['volume_mm3']+PARTS[other]['volume_mm3'])
        entries=[(mass,np.array(p['com_mm']),np.array(p['inertia_mm5'])*mass/p['volume_mm3']*1e-6)]
        basis='0.16 kg estimated bare motor shared across two CAD occurrences; NOT the stock gearbox assembly mass'
    if i in [183,276]:
        entries=[]
        for s in SOLIDS:
            den=1250. if s['bbox_mm'][4]-s['bbox_mm'][1]>124. else 2700.
            com=np.array(s['com_mm']);I=np.array(s['inertia_mm5'])*den*1e-15
            if i==276:
                mirror=np.diag([-1.,1.,1.]);com[0]=2*O[0]-com[0];I=mirror@I@mirror.T
            entries.append((s['volume_mm3']*den*1e-9,com,I))
        basis='Two separate B-Rep solids: rubber annulus 1250 kg/m3, aluminum hub 2700 kg/m3'
    transformed=[]
    for mass,c,I in entries:
        com=R@(ROT@(c-O)*.001)+t;inertia=R@ROT@I@ROT.T@R.T
        inertial_parts[name].append((mass,com,inertia));transformed.append((mass,com,inertia))
    membership.append({'id':i,'cad_name':p['name'],'cad_path':p['path'],'body':name,'material':mat,
        'mass_kg':sum(v[0] for v in transformed),'mass_basis':basis,
        'transform_rotation':R.tolist(),'transform_translation_m':t.tolist()})
    mesh=np.load(WORK/f'reports/cad_cache/part_{i:03}.npz')
    vertices=((mesh['vertices']-O)@ROT.T*.001)@R.T+t-ORIGINS[name]
    tm=trimesh.Trimesh(vertices,mesh['faces'],process=False)
    blob=tm.export(file_type='stl');digest=hashlib.sha256(blob).hexdigest()
    if digest not in mesh_hashes:
        asset='part_'+str(i).zfill(3);(ROOT/'assets'/f'{asset}.stl').write_bytes(blob);mesh_hashes[digest]=asset
    assets.append((f'visual_{i:03}',mesh_hashes[digest],name,mat))

INERTIAS={}
for name,items in inertial_parts.items():
    mass=sum(m for m,c,I in items);c=sum(m*c for m,c,I in items)/mass
    I=sum(I+m*((p-c)@(p-c)*np.eye(3)-np.outer(p-c,p-c)) for m,p,I in items)
    eig=np.linalg.eigvalsh(I);assert eig[0]>0 and eig[-1]<=eig[:2].sum()+1e-12,(name,eig)
    INERTIAS[name]=(mass,c-ORIGINS[name],I)
params['total_cad_assembly_mass_kg']=sum(v[0] for v in INERTIAS.values())
params['wheel_tire_track_m']=abs(ORIGINS['left_wheel'][1]-ORIGINS['right_wheel'][1])
(ROOT/'model_parameters.json').write_text(json.dumps(params,indent=2,ensure_ascii=False),encoding='utf8')

def build(visual,ground=True):
    root=ET.Element('mujoco',model='MOD4 six-bar serial wheel-legged chassis')
    el(root,'compiler',angle='radian',meshdir='assets',autolimits='true',inertiafromgeom='false',balanceinertia='false')
    opt=el(root,'option',timestep=params['physics_dt_s'],integrator='implicitfast',solver='Newton',iterations='100',tolerance='1e-10',cone='elliptic',gravity='0 0 -9.81',jacobian='dense')
    el(opt,'flag',multiccd='enable')
    default=el(root,'default');el(default,'joint',armature='.0002',damping='.025',frictionloss='0',
       solreflimit='.001 1',solimplimit='.999 .9999 .0001')
    el(default,'geom',friction='.9 .003 .0001',solref='.0012 1',solimp='.99 .999 .0001',margin='0',condim='3')
    vd=el(default,'default',class_='visual');el(vd,'geom',type='mesh',contype='0',conaffinity='0',group='2',density='0')
    cd=el(default,'default',class_='collision');el(cd,'geom',contype='2',conaffinity='3',group='3',rgba='.2 .6 .8 .2',density='0')
    vis=el(root,'visual');el(vis,'global',offwidth='1440',offheight='1000',azimuth='135',elevation='-20')
    el(root,'statistic',center='0 0 .32',extent='1.2')
    asset=el(root,'asset')
    if visual:
        for mat,rgba in colors.items():el(asset,'material',name=mat,rgba=fmt(rgba),specular='.3',shininess='.4')
        for n in mesh_hashes.values():el(asset,'mesh',name=n,file=n+'.stl')
    world=el(root,'worldbody')
    el(world,'light',pos='0 -1 2',dir='0 0 -1',ambient='.35 .35 .35',diffuse='.8 .8 .8')
    el(world,'light',pos='1 1 2',dir='-1 -1 -2',diffuse='.7 .7 .7')
    if ground:el(world,'geom',name='ground',type='plane',size='10 10 .1',rgba='.21 .25 .28 1',contype='1',conaffinity='2')
    height=-ORIGINS['right_wheel'][2]+.0625+.002
    chassis=el(world,'body',name='chassis',pos=fmt([0.,0.,height]));el(chassis,'freejoint',name='floating_base')
    bodies={'chassis':chassis};eq=el(root,'equality');act=el(root,'actuator');contact=el(root,'contact')
    def body(name,parent,joint,**atts):
        b=el(bodies[parent],'body',name=name,pos=fmt(ORIGINS[name]-ORIGINS[parent]));bodies[name]=b
        el(b,'joint',name=joint,type=atts.pop('type','hinge'),axis=atts.pop('axis','0 1 0'),**atts);return b
    def site(b,name,xyz):return el(b,'site',name=name,pos=fmt(xyz-ORIGINS[b.get('name')]),size='.0025',rgba='1 .3 .1 1',group='4')
    def collision(b,name,kind,**atts):return el(b,'geom',name=name,type=kind,class_='collision',**atts)
    def capsule(b,name,a,c,r):collision(b,name,'capsule',fromto=fmt(np.r_[a-ORIGINS[b.get('name')],c-ORIGINS[b.get('name')]]),size=r)
    site(chassis,'imu',np.zeros(3))
    collision(chassis,'chassis_core','box',pos='0 0 -.067',size='.167 .121 .077')
    collision(chassis,'chassis_belly','box',pos='0 0 -.157',size='.073 .121 .010')
    collision(chassis,'chassis_front','box',pos='-.268 0 -.043',size='.015 .109 .070')
    collision(chassis,'chassis_rear','box',pos='.244 0 -.043',size='.025 .109 .070')
    for side in ['left','right']:
        n=lambda k:side+'_'+k;q=NEUTRAL[side];lim=params['limits'][side]
        p=lambda key,kind:pt(q[key],ORIGINS[n(kind)][1])
        thigh=body(n('thigh'),'chassis',n('hip'),range=fmt(HIP_RANGE),armature=leg['output_armature_kg_m2'],damping='.2')
        inp=body(n('input'),'chassis',n('crank'),range=fmt([HIP_RANGE[0]+lim['input_difference_rad'][0],HIP_RANGE[1]+lim['input_difference_rad'][1]]),armature=leg['output_armature_kg_m2'],damping='.2')
        co=body(n('coupler'),n('input'),n('coupler_pin'))
        rock=body(n('rocker'),n('thigh'),n('rocker_pin'),range=fmt(lim['rocker_pin']))
        shin=body(n('shin'),n('thigh'),n('knee'),range=fmt(lim['knee']),damping='.08')
        distal=body(n('distal'),n('rocker'),n('distal_pin'))
        wh=body(n('wheel'),n('shin'),n('wheel_spin'),limited='false',armature=wheel['output_armature_kg_m2'],damping='.015')
        for tag,b1,b2,key in [('proximal',co,rock,'B'),('distal',distal,shin,'D')]:
            point=pt(q[key],ORIGINS[b2.get('name')][1])
            site(b1,n(tag+'_a'),point);site(b2,n(tag+'_b'),point)
            el(eq,'connect',name=n(tag+'_closure'),site1=n(tag+'_a'),site2=n(tag+'_b'),solref='.001 1',solimp='.9999 .99999 .0001')
        gin=body(n('gas_inner'),n('thigh'),n('gas_pin'),armature='.00005',damping='.005')
        direction=pt(q['T']-q['S']);length=np.linalg.norm(direction);direction/=length
        force=gas['force_extended_n']+gas['stiffness_n_m']*(gas['extended_eye_length_m']-length)
        gb=body(n('gas_barrel'),n('gas_inner'),n('gas_slide'),type='slide',axis=fmt(direction),
                range=fmt(lim['gas_slide']),armature='.002',damping=gas['damping_n_s_m'],
                stiffness=gas['stiffness_n_m'],springref=force/gas['stiffness_n_m'])
        end=pt(q['T'],ORIGINS[n('gas_inner')][1]);site(gb,n('gas_end'),end);site(shin,n('gas_mount'),end)
        el(eq,'connect',name=n('gas_closure'),site1=n('gas_end'),site2=n('gas_mount'),solref='.001 1',solimp='.9999 .99999 .0001')
        for drive,target in [('drive_hip','hip'),('drive_input','crank')]:
            rng=HIP_RANGE if target=='hip' else [HIP_RANGE[0]+lim['input_difference_rad'][0],HIP_RANGE[1]+lim['input_difference_rad'][1]]
            body(n(drive),'chassis',n(drive+'_spin'),range=fmt(rng),armature='.0001',damping='.005')
            el(eq,'joint',name=n(drive+'_chain'),joint1=n(drive+'_spin'),joint2=n(target),polycoef='0 1 0 0 0',solref='.001 1',solimp='.9999 .99999 .0001')
        for j,limit in [('hip',leg['peak_torque_nm']),('crank',leg['peak_torque_nm']),('wheel_spin',wheel['peak_torque_nm'])]:
            el(act,'motor',name=n(j+'_motor'),joint=n(j),gear='1',ctrlrange=fmt([-limit,limit]),forcerange=fmt([-limit,limit]))
        capsule(thigh,n('thigh_collision'),p('O','thigh'),p('K','thigh'),.012)
        capsule(shin,n('shin_collision'),p('K','shin'),p('W','shin'),.012)
        capsule(shin,n('shin_tip_collision'),p('K','shin'),p('D','shin'),.008)
        capsule(inp,n('input_collision'),p('O','input'),p('A','input'),.008)
        capsule(co,n('coupler_collision'),p('A','coupler'),p('B','coupler'),.003)
        capsule(rock,n('rocker_lower_collision'),p('B','rocker'),p('P','rocker'),.005)
        capsule(rock,n('rocker_upper_collision'),p('P','rocker'),p('C','rocker'),.005)
        capsule(distal,n('distal_collision'),p('C','distal'),p('D','distal'),.003)
        collision(wh,n('tire'),'cylinder',size='.0625 .010',quat='.7071067811865476 .7071067811865476 0 0',condim='4')
        site(wh,n('wheel_center'),ORIGINS[n('wheel')])
        internals=['thigh','input','coupler','rocker','distal','shin']
        for ai,a in enumerate(internals):
            for b in internals[ai+1:]:el(contact,'exclude',body1=n(a),body2=n(b))
        sign=1 if side=='left' else -1
        collision(chassis,n('side_armor'),'box',pos=fmt([0,sign*.274,-.007]),size='.067 .018 .061')
        collision(chassis,n('motor_bay'),'box',pos=fmt([0,sign*.121,-.060]),size='.136 .027 .060')
    for name,b in bodies.items():
        mass,c,I=INERTIAS[name]
        el(b,'inertial',mass=f'{mass:.12g}',pos=fmt(c),fullinertia=fmt([I[0,0],I[1,1],I[2,2],I[0,1],I[0,2],I[1,2]]))
        if visual:
            for vn,asset,g,mat in assets:
                if g==name:el(b,'geom',name=vn,mesh=asset,material=mat,class_='visual')
    sens=el(root,'sensor');el(sens,'framequat',name='base_orientation',objtype='site',objname='imu')
    el(sens,'gyro',name='base_gyro',site='imu');el(sens,'accelerometer',name='base_acceleration',site='imu')
    for side in ['left','right']:
        for j in ['hip','crank','knee','wheel_spin']:
            el(sens,'jointpos',name=side+'_'+j+'_pos',joint=side+'_'+j)
            el(sens,'jointvel',name=side+'_'+j+'_vel',joint=side+'_'+j)
    ET.indent(root,space='  ')
    path=ROOT/('robot_hifi.xml' if not ground else ('scene.xml' if visual else 'scene_headless.xml'))
    ET.ElementTree(root).write(path,encoding='utf8',xml_declaration=True)
    return height

height=build(True);build(False);build(True,False)
# The default training entry retains HiFi visuals as the user requested.
shutil.copyfile(ROOT/'scene.xml',ROOT/'scene_training.xml')
manifest={'source':json.loads((WORK/'reports/cad_source.json').read_text(encoding='utf8')),
 'cad_to_model_rotation':ROT.tolist(),'cad_origin_mm':O.tolist(),
 'frame_convention':'right handed: model x=-CAD Z, y=-CAD X, z=CAD Y; left/right follow source assembly names',
 'source_skeleton_xz_m':{s:{k:v.tolist() for k,v in p.items()} for s,p in PINS.items()},
 'neutral_skeleton_xz_m':{s:{k:v.tolist() for k,v in p.items()} for s,p in NEUTRAL.items()},
 'body_origins_m':{k:v.tolist() for k,v in ORIGINS.items()},'part_membership':membership,
 'body_masses_kg':{k:v[0] for k,v in INERTIAS.items()},'total_mass_kg':params['total_cad_assembly_mass_kg'],
 'measured_lengths_m':{a+b:float(np.linalg.norm(PINS['right'][a]-PINS['right'][b])) for a,b in [('O','K'),('K','W'),('O','P'),('P','K'),('O','A'),('A','B'),('P','B'),('P','C'),('C','D'),('K','D')]},
 'neutral_base_height_m':height,'visual_occurrences':len(assets),'unique_meshes':len(mesh_hashes),
 'gearbox_reduction':'Internal gear meshes fixed to carrier for rendering; output gear/case/hub/tire rotate with wheel. Motor rotor reflected to output armature; gear spin inertia needs identification.',
 'limitations':['Mass/material assumptions are not measured competition mass.','Hidden STEP internals are not removed automatically.','Internal wheel gearbox tooth contacts/gear spins are not simulated.','Gas force is a configurable candidate, not a measured component.']}
(ROOT/'reports/model_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf8')
for filename in ['cad_source.json','source_audit.json']:
    shutil.copyfile(WORK/'reports'/filename,ROOT/'reports'/filename)
print(json.dumps({'mass_kg':manifest['total_mass_kg'],'body_masses':manifest['body_masses_kg'],
 'source_hip':HIP0,'source_difference':DIFF0,'neutral_base_height':height,'track':params['wheel_tire_track_m'],'limits':params['limits']},indent=2))
