from pathlib import Path
import sys,json,time,subprocess
B=Path(__file__).resolve().parent;T=B.parent;P=json.loads((T/'PLAN.json').read_text(encoding='utf-8'));remote=P['support'].rsplit('/support',1)[0]+'/paired_rough_final_r1';sys.path.insert(0,r'D:/claude2/fangzhen/tmp');from step7_remote_access import connect
(B/'evidence').mkdir(exist_ok=True);start=time.time()
while time.time()-start<1200:
 c=connect();s=c.open_sftp()
 try:s.stat(remote+'/TERRAIN_MESHES_MANIFEST.json');ready=True
 except FileNotFoundError:ready=False
 if ready:
  for name in ['TERRAIN_MESHES_ALL_LEVELS.npz','TERRAIN_MESHES_MANIFEST.json']:s.get(remote+'/'+name,str(B/'evidence'/name))
 s.close();c.close()
 if ready:
  print('EXACT_TERRAIN_MESHES_FETCHED',flush=True);subprocess.run([sys.executable,'-X','utf8','-B',str(B/'render_all_terrains.py')],check=True);break
 time.sleep(20)
else:raise RuntimeError('Terrain export pending after20min; do not infer render success')
