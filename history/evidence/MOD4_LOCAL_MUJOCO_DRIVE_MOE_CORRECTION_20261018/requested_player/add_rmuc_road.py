"""Build RMUC2026 V2.0.0 CAD road with true vertical surface sampling, no convex hull."""
from pathlib import Path
import hashlib,json,math,shutil,xml.etree.ElementTree as ET
import numpy as np,trimesh
from scipy.signal import find_peaks
D=Path(__file__).resolve().parent;SOURCE=D.parent/'rmuc2026_training'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def configure_floor_visual(root):
    # A separate, noncolliding visual plane removes coplanar z-fighting on
    # the zero-height CAD apron; the collision floor stays exactly at z=0.
    world=root.find('worldbody');floor=world.find("geom[@name='play_floor']")
    floor.attrib.pop('material',None);floor.set('rgba','0 0 0 0')
    ET.SubElement(world,'geom',name='play_floor_visual',type='plane',size='20 15 .1',pos='0 0 -.0002',material='playground',contype='0',conaffinity='0')

def main():
    backup=D/'original_mild_playground'
    if (D/'RMUC_ROAD_BUILD_RECEIPT.json').exists():raise RuntimeError('Road already built; inspect the existing receipt instead of replacing it.')
    if not backup.exists():
        backup.mkdir()
        for name in ('playground.xml','terrain.npz','BUILD_RECEIPT.json','SMOKE_REVIEW.json','INTERACTIVE_STARTED.json'):
            if (D/name).exists():shutil.copyfile(D/name,backup/name)
    assert (backup/'playground.xml').is_file() and (backup/'terrain.npz').is_file()
    raw=np.load(SOURCE/'data/arena_collision.npz')
    vertices=raw['vertices'].astype('float64');faces=raw['faces'];tri=vertices[faces]
    # Crop collision triangles with overlap, then level the *coordinate frame*.
    # Original road plane has a 1.5 degree global CAD inclination; this rigid
    # transformation preserves each bump's physical shape and dimensions.
    keep=(tri[:,:,0].max(1)>5.75)&(tri[:,:,0].min(1)<9.25)&(tri[:,:,1].max(1)>5.25)&(tri[:,:,1].min(1)<7.65)
    mesh=trimesh.Trimesh(vertices,faces[keep],process=False)
    origin=np.array([5.9,6.45,.031169367472250853]);theta=math.radians(1.5)
    rotation=np.array([[1,0,0],[0,math.cos(theta),-math.sin(theta)],[0,math.sin(theta),math.cos(theta)]])
    mesh.vertices=(mesh.vertices-origin)@rotation.T
    nx,ny=641,201
    x=np.linspace(0,3.2,nx);y=np.linspace(-1,1,ny);xx,yy=np.meshgrid(x,y)
    origins=np.c_[xx.ravel(),yy.ravel(),np.ones(xx.size)]
    directions=np.tile([0.,0.,-1.],(xx.size,1));height=np.full(xx.size,np.nan)
    # Bound ray batches so the original CAD's many facets cannot inflate memory.
    for start in range(0,len(origins),8000):
        pts,indices,_=mesh.ray.intersects_location(origins[start:start+8000],directions[start:start+8000],multiple_hits=False)
        height[start+indices]=pts[:,2]
    assert np.isfinite(height).all(),int(np.isnan(height).sum())
    height=height.reshape(ny,nx)
    # Preserve the supplied mesh's sampled heights. Its source tessellation
    # deflection is 1 mm; use the actual maximum for hfield normalization.
    assert height.min()>-1e-5 and .069<height.max()<.072, (height.min(),height.max())
    height=np.maximum(height,0.)
    zscale=float(height.max())
    center=height[ny//2];peaks,_=find_peaks(center,prominence=.025,distance=30)
    assert len(peaks)==10,(x[peaks],center[peaks])
    pitch=np.diff(x[peaks]);assert np.all(abs(pitch-.24)<.011),pitch
    tree=ET.parse(backup/'playground.xml');root=tree.getroot();asset=root.find('asset');world=root.find('worldbody')
    old=asset.find("hfield[@name='ripples']");old.set('name','mild_ripples')
    mild=world.find("geom[@name='ripple_lane']");mild.set('name','mild_ripple_lane');mild.set('hfield','mild_ripples');mild.set('pos','6 -3 0');mild.set('rgba','.57 .49 .68 1')
    ET.SubElement(asset,'hfield',name='rmuc2026_road',nrow=str(ny),ncol=str(nx),size=f'1.6 1 {zscale:.15g} .02')
    ET.SubElement(world,'geom',name='rmuc2026_ripple_lane',type='hfield',hfield='rmuc2026_road',pos='2.6 0 0',rgba='.45 .63 .45 1',contype='1',conaffinity='2')
    # Low paint markers identify the real-sized 3.2 x 2 m road without obstacles.
    for xmark in np.arange(1.,4.21,.4):
        for ymark in (-1.04,1.04):
            ET.SubElement(world,'geom',type='box',pos=f'{xmark} {ymark} .001',size='.11 .028 .0007',rgba='.94 .72 .24 1',contype='0',conaffinity='0')
    configure_floor_visual(root)
    ET.indent(tree,space='  ');tree.write(D/'playground.xml',encoding='utf8',xml_declaration=True)
    old_data=np.load(backup/'terrain.npz')
    np.savez(D/'terrain.npz',mild_ripples=old_data['ripples'],gentle_ramp=old_data['gentle_ramp'],rmuc2026_road=(height/zscale).astype('float32'))
    report=dict(source='User-supplied RMUC2026_V2.0.0.stp, delivered collision mesh',source_STEP_sha256=json.loads((SOURCE/'reports/source.json').read_text())['sha256'],source_collision_sha256=sha(SOURCE/'data/arena_collision.npz'),source_part_id=181,source_geometry_frame_origin=origin.tolist(),rigid_leveling_rotation_x_degrees=1.5,sampled_source_length_m=3.2,sampled_width_m=2.,heightfield_grid=[ny,nx],grid_step_x_m=.005,grid_step_y_m=.01,ray_missing=0,bump_count=10,measured_bump_height_mm=float(height.max()*1000),centerline_peak_heights_mm=(center[peaks]*1000).tolist(),measured_peak_pitches_mm=(pitch*1000).tolist(),nominal_RM_bump_height_mm=70,nominal_RM_pitch_mm=240,terrain_npy_sha256=sha(D/'terrain.npz'),adapted_xml_sha256=sha(D/'playground.xml'),robot_and_actor_changed=False,only_local_playground=True,later_rulebook_CAD_equivalence_claimed=False,official_dimension_reference='https://bbs-web-static.robomaster.com/96d4042cd8cc4a5aad10c31c9b028e5b1767087205729/RoboMaster%202026%20%E6%9C%BA%E7%94%B2%E5%A4%A7%E5%B8%88%E8%B6%85%E7%BA%A7%E5%AF%B9%E6%8A%97%E8%B5%9B%E6%AF%94%E8%B5%9B%E8%A7%84%E5%88%99%E6%89%8B%E5%86%8CV1.2.0%EF%BC%8820251230%EF%BC%89.pdf')
    (D/'RMUC_ROAD_BUILD_RECEIPT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:report[k] for k in ('bump_count','measured_bump_height_mm','measured_peak_pitches_mm','heightfield_grid','ray_missing')},ensure_ascii=False))
if __name__=='__main__':main()
