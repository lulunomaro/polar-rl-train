"""Finish this authorized40m experiment without any automatic next training window."""
from pathlib import Path
import json,subprocess,sys,time,traceback
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
try:
 while not (E/'MONITOR_COMPLETE.json').exists():time.sleep(10)
 monitor=json.loads((E/'MONITOR_COMPLETE.json').read_text());assert not monitor['training_has_error']
 resolved=[]
 for failed in [x for x in monitor['evaluations']if x['exit_code']!=0]:
  mapping=json.loads((E/'EVALUATION_RECOVERIES.json').read_text());replacement=mapping[Path(failed['evaluation']).parent.name];report=E/replacement['result'];value=json.loads(report.read_text())
  assert value['complete']and value['sha256']==replacement['sha256']and str(Path(value['model']).resolve())==str(Path(failed['model']).resolve()),'A failed evaluation requires a complete same-checkpoint recovery'
  resolved.append(dict(original=failed,replacement=str(report),sha256=value['sha256'],original_failure_retained=True))
 (E/'EVALUATIONS_RESOLVED.json').write_text(json.dumps(dict(resolved=resolved),indent=2)+'\n')
 for name,args in [('select_student.py',[]),('run_post_evaluations_r2.py',[]),('finalize_run.py',[]),('archive_run.py',['--phase','complete'])]:
  print('PIPELINE_STAGE '+name,flush=True);r=subprocess.run([sys.executable,'-X','utf8','-B','-u',str(T/name),*args],cwd=R);assert r.returncode==0,name+' failed; original evidence retained'
 (E/'PIPELINE_COMPLETE.json').write_text(json.dumps(dict(epoch=time.time(),bounded40m_complete=True,no_more_training=True),indent=2)+'\n');print('BOUNDED40M_COMPLETE',flush=True)
except BaseException:
 (E/'PIPELINE_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),traceback=traceback.format_exc()),indent=2)+'\n');raise
