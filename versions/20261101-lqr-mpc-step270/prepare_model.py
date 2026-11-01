"""Create a fresh self-contained model copy without changing any source artifact."""
from pathlib import Path
import hashlib,json,shutil,tarfile,xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
SRC=Path(r'C:\Users\lulu\Desktop\claude\mjcf\mod4-onnx-mujoco-launcher\model\source_rolling_model.xml')
PKG=Path(r'C:\Users\lulu\Desktop\claude\mjcf\chassis_mod4')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
modeldir=HERE/'model';modeldir.mkdir(exist_ok=True)
shutil.copy2(SRC,modeldir/'source_rolling_model_original.xml')
root=ET.parse(SRC).getroot();root.find('compiler').set('meshdir','assets')
wb=root.find('worldbody')
removed=[]
for geom in list(wb.findall('geom')):
    if geom.get('name')!='ground':removed.append(geom.attrib);wb.remove(geom)
for side in ('left','right'):
    gas=root.find(".//joint[@name='%s_gas_slide']"%side)
    gas.set('stiffness','2000');gas.set('range','-0.0267046843609 0.020639440248416612')
# Keep original MuJoCo contact solver; PhysX TGS counts are not MuJoCo parameters.
ET.indent(root)
ET.ElementTree(root).write(modeldir/'mod4_400N.xml',encoding='utf-8',xml_declaration=True)
assets=modeldir/'assets';assets.mkdir(exist_ok=True)
for mesh in root.findall('.//asset/mesh'):
    shutil.copy2(PKG/'assets'/mesh.get('file'),assets/mesh.get('file'))
shutil.copy2(PKG/'kinematics.py',HERE/'kinematics.py')
shutil.copy2(PKG/'model_parameters.json',HERE/'model_parameters.json')
(HERE/'reports').mkdir(exist_ok=True)
shutil.copy2(PKG/'reports/model_manifest.json',HERE/'reports/model_manifest.json')
manifest={'source_xml':str(SRC),'source_xml_sha256':digest(SRC),'derived_xml_sha256':digest(modeldir/'mod4_400N.xml'),'source_unchanged':True,'model_robot_bodies':31,'closure_terminate_m':.01,'mimic_terminate_rad':.01,'task_height_m':.27,'changes':{'meshdir':'relative assets','remove_legacy_tunnel':removed,'gas_stiffness_N_m':2000,'gas_limits_m':[-.0267046843609,.020639440248416612],'original_springref_retained':True},'actuator_order':['left_hip','left_crank','left_wheel_spin','right_hip','right_crank','right_wheel_spin'],'files':{str(p.relative_to(HERE)).replace('\\','/'):{'bytes':p.stat().st_size,'sha256':digest(p)} for p in modeldir.rglob('*') if p.is_file()}}
(HERE/'MODEL_PROVENANCE.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
archive=HERE/'model_bundle.tar.gz'
with tarfile.open(archive,'w:gz') as t:
    for rel in ['model','kinematics.py','model_parameters.json','reports/model_manifest.json','MODEL_PROVENANCE.json']:t.add(HERE/rel,arcname=rel)
print(json.dumps({'bundle_bytes':archive.stat().st_size,'source_sha256':manifest['source_xml_sha256'],'derived_sha256':manifest['derived_xml_sha256']}))
