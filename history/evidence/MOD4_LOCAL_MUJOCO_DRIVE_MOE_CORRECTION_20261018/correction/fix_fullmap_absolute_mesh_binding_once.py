from pathlib import Path
import shutil,json,hashlib,xml.etree.ElementTree as ET,time
B=Path(__file__).resolve().parent;D=B.parent/'MOD4_LOCAL_MUJOCO_DRIVE_20261008';p=D/'rm7v7_latest_moe.xml'
out=B/'large_originals';out.mkdir(exist_ok=True)
original=out/'rm7v7_initial_relative_mesh_binding.xml';assert not original.exists();shutil.copy2(p,original)
root=ET.parse(p).getroot();fixed=[]
for mesh in root.find('asset').findall('mesh'):
    if mesh.get('file','').startswith('rm7v7_assets_20261018/'):
        mesh.set('file',str(D/mesh.get('file')));fixed.append(mesh.get('name'))
assert fixed
ET.ElementTree(root).write(p,encoding='utf-8',xml_declaration=True)
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(B/'reports/FULLMAP_ABSOLUTE_MESH_PATH_FIX_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),
    initial=dict(path=str(original),bytes=original.stat().st_size,SHA=H(original)),corrected=dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)),
    fixed_visual_meshes=fixed,reason='Original robot compiler uses an absolute chassis meshdir; new map visual paths must also be absolute',
    no_geometry_or_robot_or_physics_change=True),indent=2),encoding='utf-8')
