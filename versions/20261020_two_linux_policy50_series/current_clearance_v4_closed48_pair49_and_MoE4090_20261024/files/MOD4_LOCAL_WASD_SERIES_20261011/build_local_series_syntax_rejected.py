"""Build isolated local MuJoCo scenes; never touches training or previous player."""
from pathlib import Path
import hashlib,json,math,shutil,xml.etree.ElementTree as ET
import numpy as np

D=Path(__file__).resolve().parent; W=D.parent; OLD=W/'MOD4_LOCAL_MUJOCO_DRIVE_20261008'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if (D/'BUILD_RECEIPT.json').exists():raise RuntimeError('Already built; inspect existing receipt.')
    source=(OLD/'sim_runtime.py').read_text(encoding='utf8')
    revised=source.replace('from policy_runtime import OnnxPolicy','from policy_runtime import TorchPolicy').replace('OnnxPolicy(policy_path)','TorchPolicy(policy_path)')
    assert revised!=source and 'OnnxPolicy' not in revised
    (D/'sim_runtime.py').write_text(revised,encoding='utf8')
    (D/'src_snapshot').mkdir(exist_ok=True); (D/'scenes').mkdir(exist_ok=True)
    inputs=[]
    for name in ('reset_bank.json','import_contract.json'):
        src=OLD/'src_snapshot'/name; dst=D/'src_snapshot'/name
        shutil.copyfile(src,dst);inputs.append(dict(source=str(src),path=str(dst),bytes=dst.stat().st_size,sha256=sha(dst)))
    shutil.copyfile(OLD/'runtime_config.json',D/'runtime_config.json')
    profile=W/'MOD4_E1_G3_35MM_SCOPE_PREPARE_20261010/payload/g3_cad_profile.json'
    shutil.copyfile(profile,D/'g3_cad_profile.json')
    p=json.loads(profile.read_text(encoding='utf8')); px=np.asarray(p['profile_x_m']); pz=np.asarray(p['normalized_height'])
    root=ET.parse(OLD/'playground.xml').getroot()
    root.set('model','MOD4 local WASD spin and terrain series')
    root.find('compiler').set('meshdir',(W/'chassis_mod4/assets').as_posix())
    world=root.find('worldbody')
    # Preserve the complete robot, sensors, constraints, inertial parameters and drives.
    for geom in list(world.findall('geom')): world.remove(geom)
    asset=root.find('asset')
    for hf in list(asset.findall('hfield')):asset.remove(hf)
    # Remove unused externally referenced fields but preserve mesh assets/materials.
    root.find('statistic').set('extent','10');root.find('statistic').set('center','0 0 .25')
    ET.SubElement(world,'geom',name='local_floor',type='plane',size='12 8 .1',pos='0 0 0',material='playground',contype='1',conaffinity='2')
    for x in np.arange(-5,5.1,.5):
        ET.SubElement(world,'geom',name='mark_'+str(round((x+5)*2)),type='box',size='.01 .08 .0005',pos=f'{x} 1.2 .0007',rgba='.8 .85 .9 1',contype='0',conaffinity='0')
    scenes=[];fields={};builds=[]
    def add(id,label,kind,height=0.,spawn=(-1.,0.,0.),**extra):
        scene=dict(id=id,label=label,kind=kind,height=height,spawn=list(spawn),**extra)
        scenes.append(scene);return scene
    add('flat','平地 / 小陀螺','flat',spawn=(0.,0.,0.))
    for mm in (10,20,35):add('wave'+str(mm),f'起伏 {mm} mm · CAD 派生 / 全十波','wave',mm/1000,spawn=(-p['span_m']/2-.8,0.,0.),span=p['span_m'],period=p['period_m'],scope='derived RM003; not real RM70mm')
    add('rm70','RM V2 起伏约 70 mm · 未合格试玩','rm70',spawn=(-2.,0.,0.),scope='previous finite CAD crop, local leveling; not whole arena')
    for mm in (20,35,50):
        add('curb'+str(mm),f'跨坎 {mm} mm · 150 mm 条带接平台'+('' if mm==20 else ' / 未训练'), 'curb',mm/1000,spawn=(-.95,0.,0.),edge=-.075,strip_width=.15,scope='derived vertical curb; not actual RM002 height')
    for deg in (5,8,10):add('slope'+str(deg),f'坡面 {deg}° · 局部派生 / 未训练','slope',spawn=(-2.,0.,0.),angle_deg=deg,scope='local test only; not verified RM slope')
    add('stair20','台阶 20 mm × 3 · 派生 / 未训练','stair',.02,spawn=(-1.3,0.,0.),scope='local synthetic staircase; not real RM staircase or E1_STAIR trained weights')
    rm_fields=np.load(OLD/'terrain.npz');rm=rm_fields['rmuc2026_road'].copy()
    oldroot=ET.parse(OLD/'playground.xml').getroot();oldhf=next(x for x in oldroot.find('asset').findall('hfield') if x.get('name')=='rmuc2026_road')
    for scene in scenes:
        sr=ET.fromstring(ET.tostring(root));sw=sr.find('worldbody');sa=sr.find('asset');kind=scene['kind'];height=scene['height']
        floor=sw.find("geom[@name='local_floor']")
        floor.set('pos','0 0 -.0002' if kind in ('wave','rm70','slope') else '0 0 0')
        # No overlapping flat contacts beneath heightfields.
        if kind in ('wave','rm70','slope'):floor.set('contype','0');floor.set('conaffinity','0')
        if kind=='wave':
            xs=np.linspace(-4.5,4.5,9001);zs=np.interp(xs+p['span_m']/2,px,pz,left=0.,right=0.)*height
            hf=np.tile(zs/height,(3,1)).astype(np.float32)
            sa.append(ET.Element('hfield',name=scene['id'],nrow='3',ncol='9001',size=f'4.5 1 {height} .05'))
            ET.SubElement(sw,'geom',name='terrain',type='hfield',hfield=scene['id'],rgba='.24 .56 .48 1',contype='1',conaffinity='2')
            fields[scene['id']]=hf
            densex=np.linspace(-p['span_m']/2,p['span_m']/2,20001)
            orig=np.interp(densex+p['span_m']/2,px,pz)*height;sample=np.interp(densex,xs,zs)
            scene['local_sampling_max_vertical_error_m']=float(np.max(np.abs(orig-sample)))
        elif kind=='rm70':
            hf=ET.fromstring(ET.tostring(oldhf));hf.set('name','rm70');sa.append(hf);fields['rm70']=rm
            ET.SubElement(sw,'geom',name='terrain',type='hfield',hfield='rm70',pos='0 0 0',rgba='.48 .60 .28 1',contype='1',conaffinity='2')
            scene['actual_hfield_size']=list(map(float,hf.get('size').split()))
            scene['spawn']=[-float(hf.get('size').split()[0])-.8,0.,0.]
        elif kind=='curb':
            edge=scene['edge'];length=4.5-edge
            ET.SubElement(sw,'geom',name='upper_platform',type='box',pos=f'{edge+length/2} 0 {height/2}',size=f'{length/2} 4.5 {height/2}',rgba='.35 .51 .77 1',contype='1',conaffinity='2')
            ET.SubElement(sw,'geom',name='strip_marker',type='box',pos=f'0 0 {height+.0007}',size='.075 4.5 .0005',rgba='.9 .73 .30 1',contype='0',conaffinity='0')
        elif kind=='slope':
            a=math.radians(scene['angle_deg']);xs=np.linspace(-4.5,4.5,1801);zs=np.clip(xs+1.,0.,2.)*math.tan(a);height=float(max(zs));scene['height']=height
            fields[scene['id']]=np.tile(zs/height,(3,1)).astype(np.float32)
            sa.append(ET.Element('hfield',name=scene['id'],nrow='3',ncol='1801',size=f'4.5 1 {height} .05'))
            ET.SubElement(sw,'geom',name='terrain',type='hfield',hfield=scene['id'],rgba='.46 .49 .76 1',contype='1',conaffinity='2')
        elif kind=='stair':
            for i in range(3):
                left=i*.35;right=(i+1)*.35 if i<2 else4.5;top=(i+1)*height
                ET.SubElement(sw,'geom',name=f'step{i+1}',type='box',pos=f'{(left+right)/2} 0 {top/2}',size=f'{(right-left)/2} 1 {top/2}',rgba=f'{.3+i*.08} .47 .65 1',contype='1',conaffinity='2')
        target=D/'scenes'/(scene['id']+'.xml');ET.ElementTree(sr).write(target,encoding='utf8',xml_declaration=True)
        scene['xml']=str(target);builds.append(dict(path=str(target),bytes=target.stat().st_size,sha256=sha(target)))
    np.savez_compressed(D/'terrain.npz',**fields)
    (D/'SERIES.json').write_text(json.dumps(dict(scenes=scenes,spin_rad_s=[1,2,4,6,8,10,4*math.pi],spin_labels=['1','2','4','6','8','10','4π'],learned_gate=False),ensure_ascii=False,indent=2),encoding='utf8')
    receipt=dict(source_robot_scene=dict(path=str(OLD/'playground.xml'),sha256=sha(OLD/'playground.xml')),source_runtime=dict(path=str(OLD/'sim_runtime.py'),sha256=sha(OLD/'sim_runtime.py')),new_runtime_sha256=sha(D/'sim_runtime.py'),inputs=inputs,scenes=builds,terrain_sha256=sha(D/'terrain.npz'),profile_source=dict(path=str(profile),sha256=sha(profile)),local_MuJoCo_nominal=True,training_or_budget_mutations=0,policy_hz=100,local_physics_dt_s=.0005,PhysX_exact=False,teacher=False,yaw_assist=0)
    (D/'BUILD_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8')
    print('Built',len(scenes),'scenes; original robot/closed chain retained.')

if __name__=='__main__':main()
