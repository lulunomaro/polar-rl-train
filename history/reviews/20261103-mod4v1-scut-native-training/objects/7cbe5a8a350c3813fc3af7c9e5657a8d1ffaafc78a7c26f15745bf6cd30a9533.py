"""Verify the actual heightfield failure and the target SDK right-angle generator."""
from pathlib import Path
from types import SimpleNamespace
import ast
import copy
import functools
import hashlib
import json
import time
import numpy as np
import trimesh

N=Path(__file__).resolve().parent
P=N/'env20000_scut_stairs_1h_20261104';B=P/'attempt07';A=P/'attempt08';R=A/'reports'
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda b:hashlib.sha256(b).hexdigest()
def put(p,v):
    with Path(p).open('x',encoding='utf8')as stream:json.dump(v,stream,ensure_ascii=False,indent=2)
sources=read(R/'ACTUAL_TERRAIN_GENERATOR_SOURCE.json')['files']
def functions(key,names,namespace):
    raw=sources[key]['text'];tree=ast.parse(raw)
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names]
    assert len(nodes)==len(names)
    for node in nodes:node.decorator_list=[]
    unit=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0),*nodes],type_ignores=[])
    ast.fix_missing_locations(unit);exec(compile(unit,sources[key]['path'],'exec'),namespace)
    return namespace
def border(outer_size,inner_size,height,position):
    ox,oy=outer_size;ix,iy=inner_size;x,y,z=position
    parts=[((ox,(oy-iy)/2,height),(x,y+(oy+iy)/4,z)),
           ((ox,(oy-iy)/2,height),(x,y-(oy+iy)/4,z)),
           (((ox-ix)/2,iy,height),(x+(ox+ix)/4,y,z)),
           (((ox-ix)/2,iy,height),(x-(ox+ix)/4,y,z))]
    return [trimesh.creation.box(size,trimesh.transformations.translation_matrix(pos))for size,pos in parts]
ns=functions('trimesh/mesh_terrains.py',['inverted_pyramid_stairs_terrain'],
             dict(np=np,trimesh=trimesh,make_border=border))
hf=functions('height_field/hf_terrains.py',['pyramid_stairs_terrain'],dict(np=np))
utils=functions('height_field/utils.py',['height_field_to_mesh','convert_height_field_to_mesh'],
                dict(np=np,trimesh=trimesh,copy=copy,functools=functools))
oldfunc=utils['height_field_to_mesh'](hf['pyramid_stairs_terrain'])
rows=[]
for difficulty in [0.,.5,1.]:
    common=dict(size=(9.,9.),border_width=1.,step_height_range=(.025,.04),step_width=.1,platform_width=1.)
    oldcfg=SimpleNamespace(**common,horizontal_scale=.1,vertical_scale=.005,slope_threshold=.5,inverted=True)
    oldmeshes,oldorigin=oldfunc(difficulty,oldcfg)
    meshes,origin=ns['inverted_pyramid_stairs_terrain'](difficulty,SimpleNamespace(**common,holes=False))
    mesh=trimesh.util.concatenate(meshes)
    def orientations(mesh):
        t=mesh.vertices[mesh.faces];normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
        area=np.linalg.norm(normal,axis=1);z=abs(normal[:,2])/np.maximum(area,1.e-20)
        valid=area>1.e-12
        return dict(horizontal=int(((z>1-1.e-7)&valid).sum()),vertical=int(((z<1.e-7)&valid).sum()),
                    sloping=int(((z>=1.e-7)&(z<=1-1.e-7)&valid).sum()))
    before=orientations(oldmeshes[0]);after=orientations(mesh)
    assert before['sloping']>0 and before['vertical']==0
    assert after['vertical']>0 and after['horizontal']>0 and after['sloping']==0
    # Intersections at z levels along a centre-line show vertical rises and.1m treads.
    z=mesh.vertices[:,2];x=mesh.vertices[:,0]
    top_levels=np.unique(np.round(z,9));positive=np.diff(top_levels)
    step=.025+difficulty*.015
    assert np.isclose(np.median(positive[positive>1.e-6]),step,atol=1.e-7)
    assert np.isclose(origin[0],4.5)and np.isclose(origin[1],4.5)
    rows.append(dict(difficulty=difficulty,nominal_rise=step,old=before,repaired=after,
        old_origin=oldorigin.tolist(),repaired_origin=origin.tolist(),faces=len(mesh.faces)))
    if difficulty==.5:
        np.savez_compressed(A/'RIGHT_ANGLE_GEOMETRY_CPU.npz',vertices=mesh.vertices,
                            faces=mesh.faces,origin=origin)
with np.load(B/'evaluation/selected_actual_poses.npz')as data:
    actual=[]
    for eid in [0,1,40,41]:
        vertices=data['terrain_vertices_'+str(eid)];faces=data['terrain_faces_'+str(eid)]
        mesh=trimesh.Trimesh(vertices,faces,process=False)
        counts=orientations(mesh);assert counts['vertical']==0 and counts['sloping']>0
        actual.append(dict(env=eid,actual_saved_pose_mesh_orientation=counts))
plan=read(A/'PLAN.json')
put(R/'CONTINUATION_PLAN_BEFORE_HUMAN_GEOMETRY_CORRECTION.json',plan)
put(R/'HUMAN_RIGHT_ANGLE_STAIRS_CLARIFICATION.json',dict(epoch=time.time(),
    question='按华南虎方式上真实直角台阶，允许轮子保持接触 或 必须明显起跳？',
    human_answer='按华南虎方式上真实直角台阶，允许轮子保持接触',
    new_hour_still_authorized=True,production_started=False,PT_reads=0,new_physics=0))
plan.update(run_id='MOD4V1_SCUT_RIGHT_ANGLE_STAIRS_FULLSTATE_20000ENV_1H_'+str(time.time_ns()),
    module_overlay=plan['remote_root']+'/overlay',
    module_overlays=[plan['remote_root']+'/overlay']+plan['module_overlays'],
    human_geometry_clarification='真实直角台阶，允许轮子保持接触',
    geometry='Target SDK MeshInvertedPyramidStairsTerrainCfg; horizontal treads/vertical risers',
    repair='Replace0.1m heightfield interpolation with explicit SDK box-mesh stairs; original nominal25-40mmrise/.1mtread/1mplatform/9mtile/border preserved',
    initialization='Full same20000 PPO/Adam/STD/RNG/queue/counter continuation from ffce; one fresh physical reset on repaired right-angle stair geometry',
    previous_final_qualification='Valid completed slope-locomotion PPO; not a true-stair or jump expert',
    stair_origin='New SDK explicit mesh generator native origin; recorded inSTARTUP/evaluation',
    source_geometry_was_slope=True,course_changed=True)
(A/'PLAN.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8',newline='\n')
prepared=read(A/'SOURCE_ONLY_PREPARED.json')
for name in ['stairs.py','train.py']:
    path=G/'project/isaac/mod4v1_scut'/name;raw=path.read_bytes();ast.parse(raw)
    prepared['files'].append(dict(path=str(path),relative='overlay/'+name,bytes=len(raw),SHA=H(raw)))
prepared.update(changed_files=['overlay/stairs.py','overlay/train.py','PLAN.json','owner.py','entry.py'],
    geometry_repair=True,original_saved_recipe_geometry_not_byte_identical=True)
(A/'SOURCE_ONLY_PREPARED.json').write_text(json.dumps(prepared,ensure_ascii=False,indent=2),encoding='utf8',newline='\n')
report=dict(epoch=time.time(),passed=True,
    human_correction='Old nativecourse was a slope; no jump or rightangle stair skill demonstrated',
    actual_saved_meshes=actual,target_sdk_CPU_geometry=rows,
    source_report=str(R/'ACTUAL_TERRAIN_GENERATOR_SOURCE.json'),
    geometry_change_explicit=True,physics_steps=0,SDK_imports=0,PT_reads=0,
    native_stair_execution_not_yet_verified=True,
    source_checkpoint=plan['source_checkpoint'])
put(R/'ACTUAL_SLOPE_CAUSE_AND_RIGHT_ANGLE_GEOMETRY_REPAIR.json',report)
print(json.dumps(report))
