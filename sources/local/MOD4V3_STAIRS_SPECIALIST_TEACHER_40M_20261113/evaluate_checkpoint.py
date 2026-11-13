"""One CPU specialist evaluation consumer for a complete saved checkpoint."""
from pathlib import Path
import sys,json,subprocess,time,hashlib,shutil
T=Path(__file__).resolve().parent;R=T.parents[2];model=Path(sys.argv[1]);out=T/'evidence/checkpoint_evals'/model.stem;out.mkdir(parents=True,exist_ok=False);start=time.time()
if model.stem=='model_final':
 previous=T/'evidence/checkpoint_evals/model_040m/EVALUATION.json'
 if previous.exists():
  old=json.loads(previous.read_text());digest=hashlib.sha256(model.read_bytes()).hexdigest()
  if old.get('complete') and old['sha256']==digest:
   shutil.copytree(previous.parent,out,dirs_exist_ok=True);old.update(model=str(model),reused_from_identical_full_PT_sha256=str(previous),additional_simulation=False);(out/'EVALUATION.json').write_text(json.dumps(old,indent=2)+'\n');print(json.dumps(old),flush=True);raise SystemExit(0)
with (out/'stairs.log').open('wb') as log:r=subprocess.run([sys.executable,str(T/'fixed_stair_eval.py'),'--model',str(model),'--out',str(out/'stairs'),'--highest-command-only'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
result=dict(model=str(model),sha256=hashlib.sha256(model.read_bytes()).hexdigest(),complete=r.returncode==0,wall_seconds=time.time()-start,exit_code=r.returncode)
if r.returncode==0:
 j=json.loads((out/'stairs/RESULT.json').read_text());part=[x for x in j['rows'] if x['case'].startswith('whole_oblique_')];result.update(straight_passed=j['summary']['whole_h420']['passed'],straight_requested=5,oblique_passed=sum(x['success'] for x in part),actual_oblique_passed=sum(x['actual_oblique_success'] for x in part),oblique_requested=len(part),summary=j['summary'],protocol='Nominal MuJoCo specialist fixed25; no fullDR graduation claim')
(out/'EVALUATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if r.returncode:raise SystemExit(r.returncode)
