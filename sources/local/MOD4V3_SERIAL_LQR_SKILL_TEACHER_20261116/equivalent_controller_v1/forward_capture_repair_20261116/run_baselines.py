from pathlib import Path
import json,subprocess,sys,concurrent.futures,os
P=Path(__file__).resolve().parent
profile=json.loads((P/'BASELINE_PROFILE.json').read_text(encoding='utf8'))
def one(mm):
 case=dict(profile,name=f'baseline_v2_{mm:+04d}mm',start_x=mm/1000.)
 proc=subprocess.run([sys.executable,'-X','utf8','-u','-B',str(P/'run_case.py'),json.dumps(case)],capture_output=True,text=True,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
 (P/(case['name']+'.log')).write_text(proc.stdout+'\n'+proc.stderr,encoding='utf8')
 print(json.dumps(dict(case=case['name'],exit=proc.returncode,result=json.loads((P/case['name']/'RESULT.json').read_text())if (P/case['name']/'RESULT.json').exists()else proc.stderr[-1500:])),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:
 list(pool.map(one,[-60,-30,0,30,60]))
