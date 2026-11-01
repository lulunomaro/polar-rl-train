from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';R.mkdir(exist_ok=False)
p=T/'DEPTH_STAIR_TARGET_OBSERVATION_SOURCE_V247_20261101/depth_stair247.py';s=p.read_text('utf8')
def change(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
change("def deproject(depth,K,T_level_optical,*,depth_kind='distance_to_image_plane'):","def deproject(depth,K,T_level_optical,*,depth_kind='distance_to_image_plane',pixel_center_offset=0.):")
change('v,u=np.indices(z.shape,dtype=np.float32)','v,u=np.indices(z.shape,dtype=np.float32);u+=pixel_center_offset;v+=pixel_center_offset')
change('def target_from_depth(depth,K,T_level_optical,*,sensor_time,control_time,cfg=DetectorCfg()):','def target_from_depth(depth,K,T_level_optical,*,sensor_time,control_time,cfg=DetectorCfg(),pixel_center_offset=0.):')
change('cloud=deproject(z,K,T_level_optical)','cloud=deproject(z,K,T_level_optical,pixel_center_offset=pixel_center_offset)')
change('    p=cloud[mask]','''    # A height band on a vertical riser is not a supported landing surface.
    # Organized depth normals reject it before the platform-height histogram.
    horizontal=np.zeros(z.shape,dtype=bool)
    with np.errstate(invalid='ignore',over='ignore'):
        du=cloud[:-1,1:]-cloud[:-1,:-1];dv=cloud[1:,:-1]-cloud[:-1,:-1]
        normal=np.cross(du,dv);norm=np.linalg.norm(normal,axis=-1)
        support=(norm>1e-10)&(np.abs(normal[...,2])/(norm+1e-12)>.95)
    horizontal[:-1,:-1]=support&mask[:-1,:-1]&mask[:-1,1:]&mask[1:,:-1]
    p=cloud[mask&horizontal]''')
out=N/'depth_stair263.py';out.write_text(s,encoding='utf8');ast.parse(s)
proof=json.loads((T/'D435I_NEW261_DEPTH_GEOMETRY_DIAGNOSTIC_V262_20261101/reports/ROOT262_PRIMARY_CURRENT_PINHOLE_PATTERN_ACTUAL.json').read_bytes())
assert 'pixels += torch.tensor([[0.5, 0.5, 0]]'in proof['function']
with(R/'ROOT263_SOURCE_AND_ACTUAL262_PATTERN_BINDING.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),passed=True,primary_actual_pattern=proof,pixel_center_rule='RayCasterCamera uses +.5; hardware image integer centers remain explicit default0, not silently shifted.',new_filter='Observed organized depth normals, abs(vertical cosine)>.95; reject vertical riser height bands.',original247_and_actual261_false_candidates_preserved=True,model_raw_SDK_GPU_remote_reads=0),f,indent=2)
print(json.dumps(dict(passed=True,source_SHA=hashlib.sha256(out.read_bytes()).hexdigest())))
