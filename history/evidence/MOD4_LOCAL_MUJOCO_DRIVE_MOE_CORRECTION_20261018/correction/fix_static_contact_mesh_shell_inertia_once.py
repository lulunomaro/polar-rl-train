from pathlib import Path
import json,shutil,hashlib,xml.etree.ElementTree as ET,time
B=Path(__file__).resolve().parent;D=B.parent/'MOD4_LOCAL_MUJOCO_DRIVE_20261008';p=D/'rm7v7_latest_moe.xml'
original=B/'large_originals/rm7v7_initial_tiny_mesh_volume_rejected.xml';assert not original.exists();shutil.copy2(p,original)
root=ET.parse(p).getroot();count=0
for mesh in root.find('asset').findall('mesh'):
    if mesh.get('name','').startswith('rm_col_'):mesh.set('inertia','shell');count+=1
ET.ElementTree(root).write(p,encoding='utf-8',xml_declaration=True)
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(B/'reports/STATIC_CONTACT_MESH_SHELL_INERTIA_FIX_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),
    original=dict(path=str(original),bytes=original.stat().st_size,SHA=H(original)),corrected=dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)),
    static_contact_meshes=count,mesh_positions_faces_dimensions_unchanged=True,
    static_world_mass_inertia_not_robot_inertia=True,reason='MuJoCo compiler rejected negligible solid volume of tiny contact skins; shell convention for static meshes'),indent=2),encoding='utf-8')
s=(B/'compile_fullmap_local_mujoco_once.py').read_text(encoding='utf-8').replace('FULL_RM7V7_MODEL_COMPILED_ACTUAL.json','FULL_RM7V7_MODEL_COMPILED_V2_ACTUAL.json')
with (B/'compile_fullmap_local_mujoco_V2_once.py').open('x',encoding='utf-8') as f:f.write(s)
