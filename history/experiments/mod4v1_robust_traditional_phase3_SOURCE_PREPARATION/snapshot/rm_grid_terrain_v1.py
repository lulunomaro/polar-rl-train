"""Exactboxgeometry adapter for ONE pinnedSCUT RMrough family (tiny_step).
NotofficialCADarena/notall11families. Selectedpinnedpurefunctionsarehashchecked;
Trimeshboxcreationisrecordedasitsidenticalsize/translation, noSDK/GPU/importsideeffects.
"""
from pathlib import Path
import ast,hashlib,json,types
import numpy as np
ROOT=Path(__file__).resolve().parent
AUTH=ROOT.parent/'mod4v1_experts_fulldr_rm70_20261101/E1_actual_qualification_v1/SLOPE135_ACTUAL_TYPED_SOURCE_V1/runtime/isaac/mod4'
PIN_SHA='5f444236205f6ab4a56e0c76387b388d5d2d5a7a83ab63386f5cf15ae5b68d0e'
CFG={'seed':9001,'difficulty':1.};LAST={}
def configure(seed,difficulty):
 assert 0<=float(difficulty)<=1;CFG.update(seed=int(seed),difficulty=float(difficulty))
def translation(pos):
 T=np.eye(4);T[:3,3]=pos;return T
def box(dims,T):
 assert np.allclose(T[:3,:3],np.eye(3));return {'size_m':list(map(float,dims)),'position_m':np.asarray(T[:3,3],float).tolist()}
def authored_boxes():
 raw=(AUTH/'pinned_source/height_field.py').read_bytes();assert hashlib.sha256(raw).hexdigest()==PIN_SHA;recipe_raw=(AUTH/'ROUGH_V1_RESOLVED_RECIPE.json').read_bytes();recipe=json.loads(recipe_raw);definition=next(x for x in recipe['active_terrain_definitions']if x['key']=='tiny_step');names={'_resolve_fixed_or_difficulty_value','_resolve_fixed_or_difficulty_int','_resolve_int_bounds','_force_even_count','_symmetric_bar_centers','_centered_fraction_span','_resolve_grid_bars_params','mesh_grid_bars_terrain'};tree=ast.parse(raw);nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names];assert {n.name for n in nodes}==names
 module=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)]+nodes,type_ignores=[]);ast.fix_missing_locations(module);env={'np':np,'trimesh':types.SimpleNamespace(transformations=types.SimpleNamespace(translation_matrix=translation),creation=types.SimpleNamespace(box=box))};exec(compile(module,str(AUTH/'pinned_source/height_field.py'),'exec'),env)
 cfg=types.SimpleNamespace(size=(9.,9.),num_horizontal=None,num_vertical=None,bar_width=None,bar_height=None,bar_length_ratio=.95,ground_thickness=.05,**definition['parameters']);previous=np.random.get_state()
 try:np.random.seed(CFG['seed']);boxes,origin=env['mesh_grid_bars_terrain'](CFG['difficulty'],cfg)
 finally:np.random.set_state(previous)
 for b in boxes:b['position_m'][1]-=4.5
 return boxes,dict(kind='EXACT_PINNED_SCUT_TINY_STEP_BOX_GEOMETRY_ONE_OF11_NOT_CAD_ARENA',upstream_commit=recipe['commit'],pinned_source=str(AUTH/'pinned_source/height_field.py'),pinned_SHA=PIN_SHA,recipe_SHA=hashlib.sha256(recipe_raw).hexdigest(),family='tiny_step',original_parameters=definition['parameters'],defaults_source_lines='598-643:bar_length_ratio.95/ground_thickness.05',scene_config=CFG.copy(),origin_authored=origin.tolist(),coordinate_translation_m=[0.,-4.5,0.],full_bar_height_range_m=[.02,.06],actual_bar_height_m=.02+.04*CFG['difficulty'],boxes=boxes,infinite_plane=False,other10families_present=False,Isaac_PhysX_runtime_equivalence_claim=False,full_CAD_package_not_found_in_workspace_search=True)
def adapt_xml(xml):
 import xml.etree.ElementTree as ET
 global LAST
 boxes,receipt=authored_boxes();wb=xml.find('worldbody');ground=wb.find("geom[@name='ground']");assert ground is not None;wb.remove(ground)
 for i,b in enumerate(boxes):ET.SubElement(wb,'geom',name='ground'if i==0 else f'rm_bar_{i:03d}',type='box',pos=' '.join(map(str,b['position_m'])),size=' '.join(str(v*.5)for v in b['size_m']),contype='1',conaffinity='2',friction='1 .003 .0001',rgba='.42 .46 .52 1')
 receipt['effective_scene_xml_SHA']=hashlib.sha256(ET.tostring(xml,encoding='utf-8')).hexdigest();LAST=receipt

def receipt():return json.loads(json.dumps(LAST))
