"""Fixed200 independent student plus original normal-mode regression suite."""
from pathlib import Path
import sys,json,subprocess,time,hashlib,shutil
T=Path(__file__).resolve().parent;R=T.parents[2];model=Path(sys.argv[1]);out=T/'evidence/checkpoint_evals'/(sys.argv[2]if len(sys.argv)>2 and sys.argv[2]!='midrun' else model.stem)
out.mkdir(parents=True,exist_ok=False);start=time.time();digest=hashlib.sha256(model.read_bytes()).hexdigest()
if model.stem=='model_final':
 previous=T/'evidence/checkpoint_evals/model_010m/EVALUATION.json'
 if previous.exists():
  old=json.loads(previous.read_text())
  if old.get('complete')and old['sha256']==digest:
   shutil.copytree(previous.parent,out,dirs_exist_ok=True);old.update(model=str(model),reused_from_identical_full_PT_sha256=str(previous),additional_simulation=False);(out/'EVALUATION.json').write_text(json.dumps(old,indent=2)+'\n');raise SystemExit(0)
midrun=(len(sys.argv)>2 and sys.argv[2]=='midrun');out_label=model.stem
commands=[('single_step',[sys.executable,str(T/'evaluate_student200.py'),'--model',str(model),'--out',str(out/'single_step')]+(['--video']if model.stem in ('model_005m','model_010m','model_final')else[])),('pitch',[sys.executable,str(T/'fixed_pitch_eval.py'),'--model',str(model),'--out',str(out/'pitch')]),('flat60',[sys.executable,str(T/'fixed_60_eval.py'),'--model',str(model),'--out',str(out/'flat60')]),('stairs',[sys.executable,str(T/'fixed_stair_eval.py'),'--model',str(model),'--out',str(out/'stairs'),'--highest-command-only']),('descent',[sys.executable,str(T/'descent_eval.py'),'--model',str(model),'--out',str(out/'descent'),'--highest-command-only'])]
if midrun:commands=[item for item in commands if item[0]in ['single_step','flat60']]
results={}
for name,cmd in commands:
 with(out/(name+'.log')).open('wb')as log:r=subprocess.run(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 results[name]=dict(exit_code=r.returncode)
result=dict(model=str(model),sha256=digest,complete=len(results)==(2 if midrun else 5) and all(x['exit_code']==0 for x in results.values()),wall_seconds=time.time()-start,results=results,native_full_DR_graduation=False,automatic_promotion=False,teacher_assistance=False,stair_mode=[0,1,0,0,0,1,0],retention_mode=[1,0,0,0,0,0,0],closure_guard_contract='SCUT_NO_2MM_RESET_V1')
for name in results:
 f=out/name/'RESULT.json'
 if f.exists():
  d=json.loads(f.read_text())
  if name=='single_step':result.update(single_step_qualified_passed=d['passed'],single_step_requested=d['requested'],single_step_by_height={'.20':dict(passed=d['passed'],requested=d['requested'])},pure_student=d.get('pure_history_student',d.get('pure_student35_to6',False)),physical_crossed=d.get('physical_crossed'),physical_stable_events=d.get('physical_stable_events'))
  if name=='pitch':result['pitch_summary']=d['summary']
  if name=='flat60':result.update(flat60_passed=sum(x['passed']for x in d['rows']),flat60_requested=len(d['rows']))
  if name=='stairs':
   ob=[x for x in d['rows']if x['case'].startswith('whole_oblique_')];result.update(straight_passed=d['summary']['whole_h420']['passed'],straight_requested=5,actual_oblique_passed=sum(x['actual_oblique_success']for x in ob),oblique_requested=20)
  if name=='descent':result.update(descent_passed=d['summary']['descent']['passed'],descent_requested=5)
(out/'EVALUATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result),flush=True)
if not result['complete']:raise SystemExit(1)
