"""Finish this authorized40m experiment without any automatic next training window."""
from pathlib import Path
import json,subprocess,sys,time,traceback
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
try:
 while not (E/'MONITOR_COMPLETE.json').exists():time.sleep(10)
 monitor=json.loads((E/'MONITOR_COMPLETE.json').read_text());assert not monitor['training_has_error'];assert all(x['exit_code']==0 for x in monitor['evaluations'])
 for name,args in [('select_student.py',[]),('run_post_evaluations_r2.py',[]),('finalize_run.py',[]),('archive_run.py',['--phase','complete'])]:
  print('PIPELINE_STAGE '+name,flush=True);r=subprocess.run([sys.executable,'-X','utf8','-B','-u',str(T/name),*args],cwd=R);assert r.returncode==0,name+' failed; original evidence retained'
 (E/'PIPELINE_COMPLETE.json').write_text(json.dumps(dict(epoch=time.time(),bounded40m_complete=True,no_more_training=True),indent=2)+'\n');print('BOUNDED40M_COMPLETE',flush=True)
except BaseException:
 (E/'PIPELINE_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),traceback=traceback.format_exc()),indent=2)+'\n');raise
