from pathlib import Path
import subprocess,os,json,sys
from concurrent.futures import ThreadPoolExecutor
P=Path(__file__).resolve().parent
cases=[dict(name='step200_clean_start_minus60',kind='stair',height=.2,start_x=-.06,length=.3466,speed=.46,duration=10.),dict(name='step200_clean_start_plus60',kind='stair',height=.2,start_x=.06,length=.3466,speed=.46,duration=10.)]
def one(case):
 out=P/'tests'/case['name'];out.mkdir(parents=True,exist_ok=False)
 with (out/'process.log').open('w',encoding='utf8')as log:
  code=subprocess.call([sys.executable,'-X','utf8','-u','-B',str(P/'run_teacher.py'),'--case',json.dumps(case),'--out',str(out)],stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
 print(case['name'],code,flush=True)
with ThreadPoolExecutor(max_workers=4)as pool:list(pool.map(one,cases))
