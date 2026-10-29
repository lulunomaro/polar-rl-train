from pathlib import Path
import ast,hashlib,json
S=Path(__file__).resolve().parent;T=S.parent;D=S/'display';V=T/'H1_USER_MUJOCO_REAL_BLUE_IMAGINATION_V115_20261029'
def read(p):return json.loads(Path(p).read_bytes())
N=T/'MOD4_H1_FUDAN270_DIRECT_COMMAND_RESOURCE_V116_20261029/payloads/seed27';O=T/'MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029/payloads_v2/seed27'
new={r['relative']:(r['bytes'],r['SHA']) for r in read(N/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')['files'] if '/assets/' in '/'+r['relative']}
old={r['relative']:(r['bytes'],r['SHA']) for r in read(O/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')['files'] if '/assets/' in '/'+r['relative']}
assert new==old and new,'source asset manifest metadata changed'
proof=read(D/'reports/USER_DISPLAY_DATA_COMPLETE.json');assert proof['passed'] and proof['display_is_latest_qualified116'] and proof['actual_controls']==431
src=(V/'view_real_and_blue.py').read_text(encoding='utf8')
for a,b in [('recorded112','recorded118'),('frozen111','frozen116'),('USER_ACTUAL112_AND_BLUE111_DISPLAY_POSES.npz','USER_ACTUAL118_AND_BLUE116_DISPLAY_POSES.npz'),('checkpoint111 / case112','LATEST checkpoint116 / actual118'),('actual_case112=True','actual_case118=True'),('blue_model111=True','blue_model116=True'),('Checkpoint111 / actual case112 / 20s / 270mm platform','LATEST116 / actual118 / {duration:.2f}s / 270mm platform; END: closure protection'),('MUJOCO_ACTUAL_BLUE_INITIAL_FRAME.png','LATEST116_REAL_BLUE_INITIAL_FRAME.png'),('MUJOCO_ACTUAL_BLUE_LOW_HOP_FRAME.png','LATEST116_REAL_BLUE_2P7_FRAME.png'),('DISPLAY_ONLY_REAL_AND_BLUE.xml','DISPLAY_LATEST116_TRUE_MOD4_REAL_BLUE.xml'),('cam.distance=1.65;cam.azimuth=130;cam.elevation=-18','cam.distance=1.85;cam.azimuth=55;cam.elevation=-17'),('speed=.25','speed=1.'),('min(19.99,','min(duration-.01,'),("%20","%duration"),('k=min(1999,','k=min(len(actual_p)-1,')]:src=src.replace(a,b)
assert src.count(',scn,cam)')==3;src=src.replace(',scn,cam)',',cam)')
a="bottom=packet['actual_wheel_bottom']";assert src.count(a)==1;src=src.replace(a,a+";duration=len(actual_p)*.01")
src=src.replace("while not glfw.window_should_close(window) and time.monotonic()-started<7200:","while not glfw.window_should_close(window) and time.monotonic()-started<7200 and not (R/'REPLACED_BY_NEWER_OWN_DISPLAY.json').exists():")
needle="if __name__=='__main__':";assert src.count(needle)==1
injected='''
from copy import deepcopy
original_collision_scene_builder=make_scene
def make_scene(render):
    root=ET.fromstring(original_collision_scene_builder(render));asset=root.find('asset');world=root.find('worldbody')
    for m in list(asset.findall('mesh')):asset.remove(m)
    visual_base=Path('''+repr(str(V/'actual_training_USD_visuals'))+''')
    base=ET.parse(visual_base/'live_display.xml').getroot();body={b.attrib['name']:b for b in base.find('worldbody').findall('body')}
    assert set(body)==set(render['body_names'])
    meshes=base.find('asset').findall('mesh')
    for m in meshes:
        x=deepcopy(m);x.set('file',str((visual_base/'meshes'/x.attrib['file']).resolve()));asset.append(x)
    count=0
    for layer in ('actual','blue'):
        for name in render['body_names']:
            target=world.find("body[@name='"+layer+'_'+name+"']")
            for child in list(target):target.remove(child)
            for geom in body[name].findall('geom'):
                x=deepcopy(geom);x.set('name',layer+'_'+x.attrib['name']);x.set('density','0')
                if layer=='blue':x.set('rgba','.08 .48 1 .42')
                target.append(x);count+=1
    assert len(meshes)==277 and count==554
    (R/'LATEST116_TRUE_MOD4_VISUAL_MAPPING_ACTUAL.json').write_text(json.dumps(dict(actual_visual_meshes=277,rendered_geoms=count,source_asset_manifest_bytes_SHA_metadata_matches111_and116=True,no_baked_mesh_recreation=True,source_actual116=True,gray_actual118_PhysX_recording=True,blue_same116_policy_WM=True)),encoding='utf8')
    return ET.tostring(root,encoding='unicode')

'''
src=src.replace(needle,injected+needle);ast.parse(src)
target=D/'view_latest116_true_MOD4_gray_blue.py';assert not target.exists();target.write_text(src,encoding='utf8',newline='\n')
with (S/'reports/LATEST118_116_VISUAL_SOURCE_AND_IMMUTABLE_ASSET_REUSE_ADMITTED.json').open('x',encoding='utf8') as f:json.dump(dict(viewer=str(target),viewer_SHA=hashlib.sha256(src.encode()).hexdigest(),source_asset_rows=new,all_asset_metadata_same=True,no_USD_STL_model_or_raw_content_read_for_this_source_audit=True,current116_model_SHA=proof['actual_source_SHA'],new_visual_checkpoint_decodes=1,new_controls_reads=1,actual_duration_s=proof['actual_duration_s'],actual_termination='closure',actual_100Hz_endpoint_bothwheel_peak_m=proof['actual_both_wheel_peak_m']),f,indent=2)
print(json.dumps(dict(viewer=str(target),true_MOD4_meshes=277,actual_seconds=proof['actual_duration_s'],end='original closure protection',source='latest116')))
