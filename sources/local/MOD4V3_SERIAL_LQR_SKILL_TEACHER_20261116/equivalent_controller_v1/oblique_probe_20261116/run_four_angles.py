from pathlib import Path
import json,subprocess,sys,os,concurrent.futures
P=Path(__file__).resolve().parent;profile=json.loads((P/'FROZEN_PROFILE.json').read_text())
def one(deg):
 case=dict(profile,name=f'oblique_{deg:+04d}deg_v1',yaw_deg=deg)
 p=subprocess.run([sys.executable,'-X','utf8','-u','-B',str(P/'run_case.py'),json.dumps(case)],capture_output=True,text=True,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
 (P/(case['name']+'.log')).write_text(p.stdout+chr(10)+p.stderr,encoding='utf8')
 f=P/case['name']/'OBLIQUE_EVAL.json'
 print(json.dumps(json.loads(f.read_text())if f.exists()else dict(case=case,exit=p.returncode,error=p.stderr[-1800:]),ensure_ascii=False),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:list(pool.map(one,[-20,-10,10,20]))
