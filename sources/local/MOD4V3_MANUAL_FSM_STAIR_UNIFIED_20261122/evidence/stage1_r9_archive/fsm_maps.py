"""Independent terrain cache. The robot subtree is copied without physical edits."""
from copy import deepcopy
import os
from pathlib import Path
from xml.etree import ElementTree as ET
from fsm_paths import HERE, donor_imports

donor_imports()
import eval_silky_rm27 as reference

MAPS = (
    ('平地', 'flat'), ('L9 崎岖', 'rough_L9'), ('110 mm 坎', 'curb_11'),
    ('200 mm 单阶', 'step_20'), ('200 mm 正斜沿', 'oblique_20'),
    ('200 mm 反斜沿', 'oblique_20_negative'), ('RMUC2027 西入口', 'rm27_west'),
    ('RMUC2027 东入口', 'rm27_east'), ('A–A 西入口 400/360 mm', 'rm27_west_400'),
    ('A–A 东入口 400/360 mm', 'rm27_east_400'), ('380 mm 实体高台', 'platform_380'),
    ('360 mm 实体高台', 'platform_360'))

def metadata(course, cache=None):
    cache = Path(cache or HERE/'maps'/f'cpu_{os.getpid()}')
    cache.mkdir(parents=True, exist_ok=True)
    maps = reference.legacy.maps
    maps.CACHE_DIR = cache
    if course.startswith('platform_'):
        tree, root = maps._load_base_robot_tree()
        maps._add_checker_sky_and_floor(root, floor_size='30 30 .1')
        height = int(course.split('_')[1])*.001
        ET.SubElement(root.find('worldbody'), 'geom', name='fsm_jump_platform', type='box',
            size=f'2.5 11 {height/2}', pos=f'5.8 0 {height/2}', contype='1', conaffinity='2',
            friction='.9 .005 .0001', rgba='.30 .56 .73 1')
        path = cache/f'{course}.xml'
        tree.write(path, encoding='utf-8', xml_declaration=True)
        return dict(xml_path=str(path), spawns=[dict(x=-5., y=0., yaw_deg=0., name='全速助跑起点')],
                    course=course, hide_group5=False)
    if course in reference.RM:
        # Read the original full-field fixture; never create cache files beside it.
        original = reference.MAP_CACHE/'scene_rmuc2027_mod4v3_v1.xml'
        if not original.is_file():
            source = maps.build_rmuc2027()
            original = Path(source['xml_path'])
        tree = ET.parse(original)
        # Relative compiler asset paths become absolute when the fixture is relocated.
        for field in ('meshdir', 'texturedir'):
            compiler = tree.getroot().find('compiler')
            value = compiler.get(field)
            if value and not Path(value).is_absolute():
                compiler.set(field, str((original.parent/value).resolve()))
        path = cache/'rmuc2027.xml'
        tree.write(path, encoding='utf-8', xml_declaration=True)
        x,y,sign = reference.RM[course]
        return dict(xml_path=str(path), spawns=[dict(x=x, y=y, yaw_deg=0. if sign == 1 else 180.,
                    name='高地入口')], course=course, hide_group5=True)
    meta = deepcopy(reference.metadata(course, cache))
    if course in reference.AA:
        from fsm_geometry import rm27_profile
        tree=ET.parse(meta['xml_path']);root=tree.getroot()
        old_lip=reference.rm27_profile('west' in course)[2]
        new_lip=rm27_profile('west' in course,aa=True)[2]
        shift=new_lip-old_lip
        mesh=root.find("asset/mesh[@name='aa_tread']")
        points=list(map(float,mesh.get('vertex').split()))
        for i in range(0,len(points),3):
            if abs(points[i]-old_lip)<1.e-8:points[i]+=shift
        mesh.set('vertex',' '.join(map(str,points)))
        for name in ('aa_lip','aa_deck'):
            geom=root.find(f"worldbody/geom[@name='{name}']")
            pos=list(map(float,geom.get('pos').split()));pos[0]+=shift
            geom.set('pos',' '.join(map(str,pos)))
        path=cache/f'manual_{course}_tread120.xml'
        tree.write(path,encoding='utf-8',xml_declaration=True)
        meta['xml_path']=str(path)
        meta['center_tread_length_m']=1.20
    if course == 'rough_L9':
        tree = ET.parse(meta['xml_path'])
        root=tree.getroot()
        world=root.find('worldbody')
        for geom in list(world.findall('geom')):
            if geom.get('type') == 'hfield':
                pos=list(map(float,geom.get('pos','0 0 0').split()))
                for i in (-3,-2,-1,1,2,3):
                    clone=deepcopy(geom)
                    clone.set('name',geom.get('name','rough')+f'_repeat_{i:+d}')
                    clone.set('pos',f'{pos[0]+9.*i} {pos[1]} {pos[2]}')
                    world.append(clone)
        path=cache/'manual_long_rough_L9.xml'
        tree.write(path,encoding='utf-8',xml_declaration=True)
        meta['xml_path']=str(path)
        meta.pop('mjb_path',None)
    if course in ('curb_11', 'step_20'):
        # Preserve the riser at x=1 and its height/material. Give the driver a
        # full-width long tread so continued WASD travel cannot run off a tiny
        # demonstration box or bypass an inclined-entry test laterally.
        tree = ET.parse(meta['xml_path'])
        root = tree.getroot()
        for geom in root.findall('.//worldbody/geom'):
            if geom.get('name','').startswith('serial_step_'):
                old_size = list(map(float,geom.get('size').split()))
                geom.set('size',f'10 11 {old_size[2]}')
                geom.set('pos',f'11 0 {old_size[2]}')
        path = cache/f'manual_{course}.xml'
        tree.write(path,encoding='utf-8',xml_declaration=True)
        meta['xml_path'] = str(path)
    meta['course'] = course
    for sp in meta['spawns']:
        sp['name'] = '起点'
    if course == 'step_20':
        for angle in (-25., 25.):
            meta['spawns'].append(dict(meta['spawns'][0], yaw_deg=angle, name=f'斜入 {angle:+.0f}°'))
    return meta

