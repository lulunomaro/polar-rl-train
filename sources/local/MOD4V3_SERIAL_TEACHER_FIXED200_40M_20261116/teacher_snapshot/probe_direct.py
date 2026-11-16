from pathlib import Path
import subprocess,os,json,sys
from concurrent.futures import ThreadPoolExecutor
P=Path(__file__).resolve().parent
cases=[dict(name='step200_direct',kind='stair',height=.2,length=.3375,speed=.4,duration=10.,actuation='direct_torque'),dict(name='step070_first',kind='stair',height=.07,length=.3375,speed=.4,duration=10.),dict(name='step070_direct',kind='stair',height=.07,length=.3375,speed=.4,duration=10.,actuation='direct_torque'),dict(name='jump_direct',kind='jump',length=.25,duration=8.,actuation='direct_torque')]
def one(case):
 out=P/'tests'/case['name'];out.mkdir(parents=True,exist_ok=False)
 with (out/'process.log').open('w',encoding='utf8')as log:
  code=subprocess.call([sys.executable,'-X','utf8','-u','-B',str(P/'run_teacher.py'),'--case',json.dumps(case),'--out',str(out)],stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
 print(case['name'],code,flush=True)
with ThreadPoolExecutor(max_workers=4)as pool:list(pool.map(one,cases))
