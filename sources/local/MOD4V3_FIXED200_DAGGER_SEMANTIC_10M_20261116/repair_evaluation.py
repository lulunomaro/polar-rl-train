"""Repair only unexecuted regression tests; original failure report remains immutable."""
from pathlib import Path
import sys,json,subprocess,time,concurrent.futures
T=Path(__file__).resolve().parent;R=T.parents[2];name=sys.argv[1];out=T/'evidence/checkpoint_evals'/name;model=T/'weights'/(name+'.pt');old=json.loads((out/'EVALUATION.json').read_text());jobs=[];started=time.time()
for task,script,args in [('pitch','fixed_pitch_eval.py',[]),('stairs','fixed_stair_eval.py',['--highest-command-only']),('descent','descent_eval.py',['--highest-command-only'])]:
 assert old['results'][task]['exit_code']!=0
 dst=out/(task+'_r2');assert not dst.exists();jobs.append((task,script,args,dst))
def execute(job):
 task,script,args,dst=job
 with(out/(task+'_r2.log')).open('wb')as log:p=subprocess.run([sys.executable,'-X','utf8','-B',str(T/script),'--model',str(model),'--out',str(dst),*args],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 return task,p.returncode,dst
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:results=list(pool.map(execute,jobs))
new=dict(old);new['previous_attempt']=str(out/'EVALUATION.json');new['previous_attempt_unchanged']=True;new['results']=dict(old['results']);new['additional_training_seconds']=0;new['single_step_and_flat_not_repeated']=True
for task,code,dst in results:
 new['results'][task]=dict(exit_code=code,result_directory=str(dst),repaired_missing_dependency='manual_replay copied byte-identical from prior experiment')
 if code==0:
  d=json.loads((dst/'RESULT.json').read_text())
  if task=='pitch':new['pitch_summary']=d['summary']
  if task=='stairs':
   ob=[x for x in d['rows']if x['case'].startswith('whole_oblique_')];new.update(straight_passed=d['summary']['whole_h420']['passed'],straight_requested=5,actual_oblique_passed=sum(x['actual_oblique_success']for x in ob),oblique_requested=20)
  if task=='descent':new.update(descent_passed=d['summary']['descent']['passed'],descent_requested=5)
new['complete']=all(x['exit_code']==0 for x in new['results'].values());new['repair_wall_seconds']=time.time()-started;(out/'EVALUATION_REPAIRED.json').write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('REPAIRED_EVALUATION',name,new['complete'],[(t,c)for t,c,d in results],flush=True)
