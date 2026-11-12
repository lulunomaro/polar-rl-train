"""Rebuild the saved SCUT Rough-v1 terrain recipe locally, without training."""
from pathlib import Path
import sys,json,traceback,hashlib,time
import numpy as np
B=Path(__file__).resolve().parent
S=Path(r'D:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_SCUT_ROUGH_V1_2H_20261112/support')
app=None
try:
 from isaaclab.app import AppLauncher
 launcher=AppLauncher(headless=True,device='cpu')
 app=launcher.app
 sys.path.insert(0,str(S))
 from rough_scut_v1_terrain import generator,FAMILIES,COUNTS
 from isaaclab.terrains import TerrainGenerator
 import trimesh
 cfg=generator()
 np.random.seed(66)
 (B/'tiles').mkdir(exist_ok=True)
 records=[]
 class Capture(TerrainGenerator):
  def _add_sub_terrain(self,mesh,origin,row,col,sub_cfg):
   family=next(k for k,v in self.cfg.sub_terrains.items() if v is sub_cfg)
   name=f'r{row:02d}_c{col:02d}'
   np.savez_compressed(B/'tiles'/(name+'.npz'),vertices=np.asarray(mesh.vertices,dtype=np.float32),faces=np.asarray(mesh.faces,dtype=np.int32),origin=np.asarray(origin),row=row,col=col)
   records.append(dict(name=name,row=row,col=col,family=family,vertices=len(mesh.vertices),faces=len(mesh.faces),origin=np.asarray(origin).tolist()))
   if len(records)%25==0: print('TILES',len(records),flush=True)
   super()._add_sub_terrain(mesh,origin,row,col,sub_cfg)
 start=time.time()
 gen=Capture(cfg,device='cpu')
 np.savez_compressed(B/'FULL_MAP.npz',vertices=np.asarray(gen.terrain_mesh.vertices,dtype=np.float32),faces=np.asarray(gen.terrain_mesh.faces,dtype=np.int32),origins=gen.terrain_origins)
 manifest=dict(scope='Local reconstruction using saved actual Rough-v1 generator, seed66; not a byte-identity claim for target-machine random tiles',rows=cfg.num_rows,cols=cfg.num_cols,tile_size=list(cfg.size),families=list(FAMILIES),counts=list(COUNTS),source=str(S/'rough_scut_v1_terrain.py'),source_sha256=hashlib.sha256((S/'rough_scut_v1_terrain.py').read_bytes()).hexdigest(),elapsed=time.time()-start,tiles=records)
 (B/'MAP_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
 print('MAP_EXPORT_READY',json.dumps({k:manifest[k] for k in ['rows','cols','elapsed']}),flush=True)
except Exception:
 (B/'export_error.log').write_text(traceback.format_exc(),encoding='utf8')
 traceback.print_exc()
finally:
 if app is not None:app.close()
