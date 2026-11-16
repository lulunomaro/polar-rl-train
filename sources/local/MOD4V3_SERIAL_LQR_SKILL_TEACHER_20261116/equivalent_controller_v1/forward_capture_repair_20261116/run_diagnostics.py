from pathlib import Path
import subprocess,json,sys,os,concurrent.futures
P=Path(__file__).resolve().parent
profile=json.loads((P/'BASELINE_PROFILE.json').read_text())
def one(mm):
 case=dict(profile,name=f'diagnostic_v2_{mm:+04d}mm',start_x=mm/1000.)
 p=subprocess.run([sys.executable,'-X','utf8','-u','-B',str(P/'run_case.py'),json.dumps(case)],capture_output=True,text=True,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
 (P/(case['name']+'.log')).write_text(p.stdout+'\n'+p.stderr,encoding='utf8')
 print(case['name'],p.returncode,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:list(pool.map(one,[0,-60]))
