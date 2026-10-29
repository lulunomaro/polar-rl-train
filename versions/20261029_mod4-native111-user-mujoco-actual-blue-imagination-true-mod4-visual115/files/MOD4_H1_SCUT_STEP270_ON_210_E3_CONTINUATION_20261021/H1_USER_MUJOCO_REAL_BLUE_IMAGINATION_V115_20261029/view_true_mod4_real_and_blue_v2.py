"""Use all original training USD visual meshes; retain exact recorded/imagined poses."""
from pathlib import Path
from copy import deepcopy
import json,hashlib,time,traceback,xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
old=(HERE/'view_real_and_blue.py').read_text(encoding='utf8')
a="cam.distance=1.65;cam.azimuth=130;cam.elevation=-18"
b="cam.distance=1.85;cam.azimuth=55;cam.elevation=-17"
assert old.count(a)==1
s=old.replace(a,b).replace('DISPLAY_ONLY_REAL_AND_BLUE.xml','DISPLAY_TRUE_MOD4_REAL_AND_BLUE.xml').replace('MOD4 | GRAY','MOD4 REAL MODEL | GRAY').replace('MUJOCO_ACTUAL_BLUE_INITIAL_FRAME.png','TRUE_MOD4_REAL_BLUE_INITIAL_FRAME.png').replace('MUJOCO_ACTUAL_BLUE_LOW_HOP_FRAME.png','TRUE_MOD4_REAL_BLUE_LOW_HOP_FRAME.png')
ns=dict(__name__='actual_visual_mesh_display_v2',__file__=str(HERE/'view_true_mod4_real_and_blue_v2.py'))
exec(compile(s,str(HERE/'view_true_mod4_real_and_blue_v2.py'),'exec'),ns)
original_make_scene=ns['make_scene']
R=HERE/'reports/true_visual_v2';R.mkdir(exist_ok=True)
(R/'USER_DISPLAY_DATA_COMPLETE.json').write_bytes((HERE/'reports/USER_DISPLAY_DATA_COMPLETE.json').read_bytes())
ns['R']=R
def make_scene(render):
    root=ET.fromstring(original_make_scene(render));asset=root.find('asset');world=root.find('worldbody')
    for mesh in list(asset.findall('mesh')):asset.remove(mesh)
    base=ET.parse(HERE/'actual_training_USD_visuals/live_display.xml').getroot()
    source_bodies={x.attrib['name']:x for x in base.find('worldbody').findall('body')}
    assert set(source_bodies)==set(render['body_names'])
    meshes=base.find('asset').findall('mesh')
    for mesh in meshes:
        c=deepcopy(mesh);c.set('file',str((HERE/'actual_training_USD_visuals/meshes'/c.attrib['file']).resolve()));asset.append(c)
    visuals=0
    for layer in ('actual','blue'):
        for name in render['body_names']:
            body=world.find("body[@name='"+layer+'_'+name+"']")
            for c in list(body):body.remove(c)
            for geom in source_bodies[name].findall('geom'):
                c=deepcopy(geom);c.set('name',layer+'_'+c.attrib['name']);c.set('density','0')
                if layer=='blue':c.set('rgba','.08 .48 1 .42')
                body.append(c);visuals+=1
    audit=json.loads((HERE/'actual_training_USD_visuals/DISPLAY_SOURCE_AUDIT.json').read_bytes())
    report=dict(epoch=time.time(),original_USD_visual_meshes=len(meshes),rendered_visual_geoms=visuals,actual_source_triangles=audit['triangles'],body_names_exact=True,actual_world_poses_not_changed=True,blue_policy_world_model_poses_not_changed=True,former_collision_only_display_rejected_by_user=True,collision_visuals_removed=True,source_asset='exact native111 job0/assets/robot.usd and original composed source_700N',physical_steps=0,new_checkpoint_decodes=0)
    (R/'TRUE_MOD4_VISUAL_MESH_MAPPING_ACTUAL.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    return ET.tostring(root,encoding='unicode')
ns['make_scene']=make_scene
if __name__=='__main__':
    try:ns['main']()
    except BaseException:
        (R/('TRUE_MOD4_DISPLAY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(traceback=traceback.format_exc()),indent=2),encoding='utf8');raise
