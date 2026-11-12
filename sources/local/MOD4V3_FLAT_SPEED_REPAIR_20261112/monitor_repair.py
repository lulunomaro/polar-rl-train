"""Finite local checkpoint consumer; no scheduler and no training restarts."""
from pathlib import Path
import json,subprocess,time,sys
T=Path(__file__).resolve().parent;J=T/'training_round';E=T/'evidence/repair_checkpoint_evals';E.mkdir(exist_ok=True);done=set();python=str(T.parents[3]/'.venv/Scripts/python.exe');start=time.time()
while time.time()-start<5400:
 for p in sorted(J.glob('model_*.pt')):
  if p.name in done or p.name=='model_final.pt' and not (J/'FINAL.json').exists():continue
  if p.name=='model_first_complete.pt' and not (J/'FIRST_UPDATE.json').exists():continue
  if p.name not in ('model_first_complete.pt','model_final.pt') and not (J/('PERIODIC_'+p.stem[6:9]+'M.json')).exists():continue
  out=E/p.stem;log=E/(p.stem+'.log')
  with log.open('w',encoding='utf8') as f:
   result=subprocess.run([python,'-X','utf8','-B',str(T/'evaluate_repair.py'),'--model',str(p),'--out',str(out)],stdout=f,stderr=subprocess.STDOUT)
  done.add(p.name);(E/'MONITOR_STATE.json').write_text(json.dumps(dict(epoch=time.time(),consumed=sorted(done),last=p.name,returncode=result.returncode)))
 if (J/'SAFE_CLOSED.json').exists() and ((J/'ERROR.json').exists() or 'model_final.pt' in done):break
 time.sleep(5)
(E/'MONITOR_FINISHED.json').write_text(json.dumps(dict(epoch=time.time(),consumed=sorted(done),training_safe_closed=(J/'SAFE_CLOSED.json').exists())))
