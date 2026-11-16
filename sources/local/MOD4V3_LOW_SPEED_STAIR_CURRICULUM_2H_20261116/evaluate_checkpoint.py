"""Same frozen45single-step cases plus retained pitch, flat60, legacy stairs and descent."""
from pathlib import Path
import sys,json,subprocess,time,hashlib,shutil,traceback
T=Path(__file__).resolve().parent;R=T.parents[2];model=Path(sys.argv[1]);out=T/'evidence/checkpoint_evals'/(sys.argv[2]if len(sys.argv)>2 else model.stem)
out.mkdir(parents=True,exist_ok=False);start=time.time();digest=hashlib.sha256(model.read_bytes()).hexdigest()
if model.stem=='model_final':
 previous=T/'evidence/checkpoint_evals/model_120m/EVALUATION.json'
 if previous.exists():
  old=json.loads(previous.read_text())
  if old.get('complete')and old['sha256']==digest:
   shutil.copytree(previous.parent,out,dirs_exist_ok=True);old.update(model=str(model),reused_from_identical_full_PT_sha256=str(previous),additional_simulation=False);(out/'EVALUATION.json').write_text(json.dumps(old,indent=2)+'\n');raise SystemExit(0)
commands=[('single_step',[sys.executable,str(T/'fixed_single_step_eval.py'),'--model',str(model),'--out',str(out/'single_step')]),('pitch',[sys.executable,str(T/'fixed_pitch_eval.py'),'--model',str(model),'--out',str(out/'pitch')]),('flat60',[sys.executable,str(R/'sources/local/MOD4V3_FLAT_SPEED_REPAIR_20261112/fixed_60_eval.py'),'--model',str(model),'--out',str(out/'flat60')]),('stairs',[sys.executable,str(T/'fixed_stair_eval.py'),'--model',str(model),'--out',str(out/'stairs'),'--highest-command-only']),('descent',[sys.executable,str(T/'descent_eval.py'),'--model',str(model),'--out',str(out/'descent'),'--highest-command-only'])]
results={}
for name,cmd in commands:
 with(out/(name+'.log')).open('wb')as log:r=subprocess.run(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 results[name]=dict(exit_code=r.returncode)
 # Keep independent task results even if one reader fails; never rerun PPO for an evaluator.
result=dict(model=str(model),sha256=digest,complete=len(results)==5 and all(x['exit_code']==0 for x in results.values()),wall_seconds=time.time()-start,results=results,native_full_DR_graduation=False,automatic_promotion=False)
for name in results:
 f=out/name/'RESULT.json'
 if f.exists():
  d=json.loads(f.read_text())
  if name=='single_step':result.update(single_step_by_height=d['by_height'],single_step_qualified_passed=sum(x['success']for x in d['rows']),single_step_requested=len(d['rows']))
  if name=='pitch':result['pitch_summary']=d['summary']
  if name=='flat60':result.update(flat60_passed=sum(x['passed']for x in d['rows']),flat60_requested=len(d['rows']))
  if name=='stairs':
   ob=[x for x in d['rows']if x['case'].startswith('whole_oblique_')];result.update(straight_passed=d['summary']['whole_h420']['passed'],straight_requested=5,actual_oblique_passed=sum(x['actual_oblique_success']for x in ob),oblique_requested=20)
  if name=='descent':result.update(descent_passed=d['summary']['descent']['passed'],descent_requested=5)
(out/'EVALUATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result),flush=True)
if not result['complete']:raise SystemExit(1)
