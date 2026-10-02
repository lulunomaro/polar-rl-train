"""Sequential, checkpoint-frozen candidate evaluations; never trains."""
from pathlib import Path
import argparse,subprocess,json,sys,hashlib,fcntl
from acceptance import compare
r=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--checkpoint',required=True);p.add_argument('--output-dir',required=True);p.add_argument('--seeds',default='20260926,20260927');p.add_argument('--speed',type=float,default=1.5);p.add_argument('--steps',type=int,default=1500);a=p.parse_args()
out=Path(a.output_dir).resolve();out.mkdir(parents=True,exist_ok=False)
lock=open(r/'paired.lock','w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
checkpoint=Path(a.checkpoint).resolve();digest=hashlib.sha256(checkpoint.read_bytes()).hexdigest()
results=[]
for seed in map(int,a.seeds.split(',')):
    reports=[]
    for name in ['nominal','mild_mass_effort']:
        target=out/f'{name}_{seed}.json'
        args=[sys.executable,str(r/'isaac/mod4/candidate_entry.py'),'--profile',str(r/'profiles'/f'{name}.json'),
          '--headless','--checkpoint',str(checkpoint),'--num_envs','80','--steps',str(a.steps),'--speed_limit',str(a.speed),
          '--ramp_suite','--seed',str(seed),'--output',str(target)]
        with target.with_suffix('.log').open('w') as f:
            subprocess.run(args,cwd=r,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=1800)
        if hashlib.sha256(checkpoint.read_bytes()).hexdigest()!=digest:raise RuntimeError('Checkpoint changed during pair')
        reports.append(json.loads(target.read_text()))
    results.append({'seed':seed,**compare(*reports)})
(out/'comparison.json').write_text(json.dumps({'checkpoint':str(checkpoint),'sha256':digest,'results':results},indent=2))
print(out/'comparison.json')
