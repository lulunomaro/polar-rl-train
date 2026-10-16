"""Independent height27p5 derived CURB geometry, preserving the four background families."""
from pathlib import Path
import hashlib, json
import numpy as np
import trimesh
PROFILE = Path(__file__).with_name('curb35_profile.json')

def profile():
    p=json.loads(PROFILE.read_bytes())
    assert p['height_m']==.0275 and p['strip_width_m']==.150
    assert p['strip_continuous_with_upper_platform'] and p['vertical_riser_unsmoothed']
    assert p['derived_not_actual_RM_geometry'] and p['not_stair_flight']
    return p

def make_mesh(size, mirrored=False):
    p=profile(); assert tuple(map(float,size))==(9.,9.)
    v=np.array(p['vertices'],dtype=np.float64)
    f=np.array(p['triangles'],dtype=np.int64)
    if mirrored:
        v[:,0]*=-1; f=f[:,::-1]
    # TerrainGenerator receives coordinates in [0,size] before its own offset.
    v[:,:2]+=np.asarray(size)*.5
    mesh=trimesh.Trimesh(v,f,process=False)
    assert len(mesh.faces)==8 and np.ptp(v[:,2])==.0275
    horizontal=np.ptp(v[f,:,] if False else v[f][:,:,2],axis=1)==0
    assert (mesh.face_normals[horizontal,2]>0).all()
    assert np.allclose(abs(mesh.face_normals[~horizontal,0]),1.)
    return mesh,np.array([4.5,4.5,.0275])

def curb_mesh(difficulty,cfg):
    # The unchanged intro range is [0,.25]. Its lower/upper twenty rows mirror
    # the curb. The frozen route independently reads the authored ground sign.
    assert 0. <= difficulty <= .25
    mesh,origin=make_mesh(cfg.size,mirrored=difficulty>=.125)
    return [mesh],origin

def configure_curb(cfg):
    from e1_scene_query_resource import configure_intro
    from isaaclab.terrains.sub_terrain_cfg import SubTerrainBaseCfg
    from isaaclab.utils.configclass import configclass
    recipe=configure_intro(cfg)
    @configclass
    class CurbCfg(SubTerrainBaseCfg):
        function=curb_mesh
    gen=cfg.scene.terrain.terrain_generator
    assert gen.difficulty_range==(0.,.25) and tuple(gen.size)==(9.,9.)
    old=gen.sub_terrains['random_uniform_for_rm']
    gen.sub_terrains['random_uniform_for_rm']=CurbCfg(proportion=old.proportion,size=gen.size)
    recipe['profile']='mod4_CURB_derived27p5mm_strip150_mirrored_v1'
    recipe['CURB_geometry_change']=dict(revision='MOD4-MOE-TERRAIN-SUBEXPERT-REVISION-004',
        height_m=.0275,strip_width_m=.150,profile_sha256=hashlib.sha256(PROFILE.read_bytes()).hexdigest(),
        vertical_riser_unsmoothed=True,strip_continuous_with_upper_platform=True,
        mirror_threshold_within_unchanged_difficulty_range=.125,
        old_random_height_family_replaced_only=True,other_four_families_unchanged=True,
        proportions_unchanged=True,derived_not_actual_RM002_height=True,not_stair_flight=True)
    return recipe
