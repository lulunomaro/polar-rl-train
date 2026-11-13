"""One CPU evaluation consumer for a saved complete checkpoint; no training."""
from pathlib import Path
import sys,json,subprocess,time,hashlib
T=Path(__file__).resolve().parent;R=T.parents[2];model=Path(sys.argv[1]);label=model.stem;out=T/'evidence/checkpoint_evals'/label;out.mkdir(parents=True,exist_ok=False)
commands=[('stairs',[sys.executable,str(T/'fixed_stair_eval.py'),'--model',str(model),'--out',str(out/'stairs')]),('flat60',[sys.executable,str(R/'sources/local/MOD4V3_FLAT_SPEED_REPAIR_20261112/fixed_60_eval.py'),'--model',str(model),'--out',str(out/'flat60')])]
results={};started=time.time()
for name,cmd in commands:
 with (out/(name+'.log')).open('wb') as log:r=subprocess.run(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 results[name]=dict(exit_code=r.returncode,result_file=str(out/name/'RESULT.json'))
 if r.returncode:break
summary=dict(model=str(model),sha256=hashlib.sha256(model.read_bytes()).hexdigest(),wall_seconds=time.time()-started,results=results,complete=len(results)==2 and all(v['exit_code']==0 for v in results.values()))
if summary['complete']:
 stairs=json.loads((out/'stairs/RESULT.json').read_text());flat=json.loads((out/'flat60/RESULT.json').read_text());summary.update(whole_stair_passed=stairs['whole_passed'],whole_stair_requested=stairs['whole_requested'],stair_summary=stairs['summary'],flat60_passed=sum(x['passed'] for x in flat['rows']),flat60_requested=len(flat['rows']))
(out/'EVALUATION.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(summary),flush=True)
