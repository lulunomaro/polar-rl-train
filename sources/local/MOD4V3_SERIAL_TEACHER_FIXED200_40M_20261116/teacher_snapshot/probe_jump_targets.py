from pathlib import Path
import subprocess,os,json,sys
from concurrent.futures import ThreadPoolExecutor
P=Path(__file__).resolve().parent
cases=[dict(name='jump_target006',kind='jump',target_height=.06,length=.25,duration=8.),dict(name='jump_target010',kind='jump',target_height=.10,length=.25,duration=8.),dict(name='jump_target014',kind='jump',target_height=.14,length=.25,duration=8.)]
def one(case):
 out=P/'tests'/case['name'];out.mkdir(parents=True,exist_ok=False)
 with (out/'process.log').open('w',encoding='utf8')as log:
  code=subprocess.call([sys.executable,'-X','utf8','-u','-B',str(P/'run_teacher.py'),'--case',json.dumps(case),'--out',str(out)],stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
 print(case['name'],code,flush=True)
with ThreadPoolExecutor(max_workers=4)as pool:list(pool.map(one,cases))
