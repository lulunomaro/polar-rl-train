from pathlib import Path
import os,sys,subprocess
from concurrent.futures import ThreadPoolExecutor
P=Path(__file__).resolve().parent
def one(row):
 name,speed=row
 with(P/(name+'.log')).open('w',encoding='utf8')as log:
  r=subprocess.run([sys.executable,'-X','utf8','-u','-B',str(P/'capture_source_motion.py'),'--name',name,'--speed',str(speed)],stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
 print(name,r.returncode,flush=True)
with ThreadPoolExecutor(max_workers=2)as pool:list(pool.map(one,[('source_player_v030',.3),('source_reference_v047',.47)]))
