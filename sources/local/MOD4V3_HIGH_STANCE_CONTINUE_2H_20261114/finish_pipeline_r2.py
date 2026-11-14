"""Finish only this authorized2h round; no automatic extension or further training."""
from pathlib import Path
import sys,time,subprocess,json,traceback
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
def run(name,*args):
 print('PIPELINE_STAGE '+name,flush=True)
 result=subprocess.run([sys.executable,'-X','utf8','-B','-u',str(T/name),*args],cwd=R)
 assert result.returncode==0,name+' failed; original evidence retained'
try:
 while not (E/'MONITOR_COMPLETE.json').exists():
  if (E/'LAUNCH_RECOVERY_R2_ERROR.json').exists():raise RuntimeError('Repair launch failed; inspect preserved launch error')
  time.sleep(10)
 monitor=json.loads((E/'MONITOR_COMPLETE.json').read_text());assert not monitor['training_has_error']
 assert all(x['exit_code']==0 for x in monitor['evaluations'])
 run('select_student.py');run('run_post_evaluations_r2.py');run('finalize_run.py');run('archive_run.py','--phase','complete')
 print('BOUNDED2H_PIPELINE_COMPLETE_NO_FURTHER_TRAINING',flush=True)
except BaseException:
 (E/'PIPELINE_RECOVERY_R2_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),traceback=traceback.format_exc()),indent=2)+'\n',encoding='utf8');raise
