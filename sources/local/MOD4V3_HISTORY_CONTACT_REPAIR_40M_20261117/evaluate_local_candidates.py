"""Independent candidate replay; bound parallelism to avoid duplicate model memory exhaustion."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import argparse,sys,subprocess,json,time
T=Path(__file__).resolve().parent;p=argparse.ArgumentParser();p.add_argument('--profile',required=True);p.add_argument('--steps',nargs='+',type=int,default=[500,1000,2000,4000]);a=p.parse_args();out=T/'local_probes'/a.profile;start=time.time()
def run(n):
 f=out/f'model_fit_{n:05d}.pt';dest=out/f'eval_{n:05d}'
 with(out/f'eval_{n:05d}.log').open('xb')as log:r=subprocess.run([sys.executable,'-X','utf8','-B',str(T/'evaluate_student200.py'),'--model',str(f),'--out',str(dest)],stdout=log,stderr=subprocess.STDOUT)
 d=json.loads((dest/'RESULT.json').read_text())if(dest/'RESULT.json').exists()else{}
 row=dict(step=n,exit_code=r.returncode,strict=d.get('passed'),physical=d.get('physical_crossed'),stable=d.get('physical_stable_events'),rows=d.get('rows',[]));return row
rows=[]
with ThreadPoolExecutor(max_workers=2)as pool:
 for fut in as_completed([pool.submit(run,n)for n in a.steps]):
  r=fut.result();rows.append(r);print('CLOSED_LOOP',json.dumps({k:v for k,v in r.items()if k!='rows'}),flush=True)
(out/'CLOSED_LOOP_SUMMARY.json').write_text(json.dumps(dict(evaluations=rows,wall_seconds=time.time()-start),indent=2)+'\n')
