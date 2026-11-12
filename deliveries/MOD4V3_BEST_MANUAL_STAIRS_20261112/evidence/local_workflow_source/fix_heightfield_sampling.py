from pathlib import Path
b=Path(r'D:/claude2/fangzhen/tmp/rough_v1_local_showcase_20261112');p=b/'showcase.py';s=p.read_text(encoding='utf8')
s=s.replace("cache=B/(tile+'_hf.npz')", "cache=B/(tile+'_hf_v2.npz')")
s=s.replace("p[:2]=x,y;dist=mujoco.mj_ray(m,d,p,vec,None,True,-1,gid);h[iy,ix]=10-dist if dist>=0 else 0.", "p[:2]=np.clip([x+1.7e-5,y+2.9e-5],-4.5+1e-4,4.5-1e-4);dist=mujoco.mj_ray(m,d,p,vec,None,True,-1,gid)\n   if dist<0:raise RuntimeError(f'Ground-ray miss: {tile} {x} {y}')\n   h[iy,ix]=10-dist")
s=s.replace('self.viewer.cam.azimuth=115.', 'self.viewer.cam.azimuth=150.')
p.write_text(s,encoding='utf8')
p=b/'capture_clips.py';s=p.read_text(encoding='utf8').replace('cam.azimuth=105.','cam.azimuth=150.');p.write_text(s,encoding='utf8')
