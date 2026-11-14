"""Independent nominal whole-two-step, oblique, original flat60 and descent tests."""
from pathlib import Path
import sys,json,subprocess,time,hashlib,shutil
T=Path(__file__).resolve().parent;R=T.parents[2];model=Path(sys.argv[1]);out=T/'evidence/checkpoint_evals'/model.stem;out.mkdir(parents=True,exist_ok=False);start=time.time();digest=hashlib.sha256(model.read_bytes()).hexdigest()
if model.stem=='model_final':
 previous=T/'evidence/checkpoint_evals/model_040m/EVALUATION.json'
 if previous.exists():
  old=json.loads(previous.read_text())
  if old.get('complete') and old['sha256']==digest:
   shutil.copytree(previous.parent,out,dirs_exist_ok=True);old.update(model=str(model),reused_from_identical_full_PT_sha256=str(previous),additional_simulation=False);(out/'EVALUATION.json').write_text(json.dumps(old,indent=2)+'\n');print(json.dumps(old),flush=True);raise SystemExit(0)
commands=[('low_speed',[sys.executable,str(T/'fixed_low_speed_eval.py'),'--model',str(model),'--out',str(out/'low_speed')]),('stairs',[sys.executable,str(T/'fixed_stair_eval.py'),'--model',str(model),'--out',str(out/'stairs'),'--highest-command-only']),('flat60',[sys.executable,str(R/'sources/local/MOD4V3_FLAT_SPEED_REPAIR_20261112/fixed_60_eval.py'),'--model',str(model),'--out',str(out/'flat60')]),('descent',[sys.executable,str(T/'descent_eval.py'),'--model',str(model),'--out',str(out/'descent'),'--highest-command-only'])]
results={}
for name,cmd in commands:
 with (out/(name+'.log')).open('wb') as log:r=subprocess.run(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 results[name]=dict(exit_code=r.returncode)
 if r.returncode:break
result=dict(model=str(model),sha256=digest,complete=len(results)==4 and all(x['exit_code']==0 for x in results.values()),wall_seconds=time.time()-start,results=results)
if result['complete']:
 low=json.loads((out/'low_speed/RESULT.json').read_text());result.update(low_whole_passed=low['whole_passed'],low_whole_requested=low['whole_requested'],supported_first_passed=low['assisted_first_passed'])
 j=json.loads((out/'stairs/RESULT.json').read_text());flat=json.loads((out/'flat60/RESULT.json').read_text());down=json.loads((out/'descent/RESULT.json').read_text());ob=[x for x in j['rows'] if x['case'].startswith('whole_oblique_')];result.update(straight_passed=j['summary']['whole_h420']['passed'],straight_requested=5,oblique_passed=sum(x['success'] for x in ob),actual_oblique_passed=sum(x['actual_oblique_success'] for x in ob),oblique_requested=20,flat60_passed=sum(x['passed'] for x in flat['rows']),flat60_requested=len(flat['rows']),descent_passed=down['summary']['descent']['passed'],descent_requested=5,summary=j['summary'])
(out/'EVALUATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if not result['complete']:raise SystemExit(1)
