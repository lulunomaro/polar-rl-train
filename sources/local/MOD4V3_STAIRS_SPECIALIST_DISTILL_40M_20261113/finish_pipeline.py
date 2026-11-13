"""Finish this one authorized student round; no new training or automatic extension."""
from pathlib import Path
import sys,subprocess,time,json,traceback
T=Path(__file__).resolve().parent;R=T.parents[2]
def run(name,*args):
 print('PIPELINE_STAGE '+name,flush=True)
 result=subprocess.run([sys.executable,'-X','utf8','-B','-u',str(T/name),*args],cwd=R)
 if result.returncode:raise RuntimeError(name+' exited '+str(result.returncode))
try:
 print('WAITING_FOR_COMPLETE_STUDENT_CHECKPOINT_EVALUATIONS',flush=True)
 while not (T/'evidence/MONITOR_COMPLETE.json').exists():time.sleep(10)
 monitor=json.loads((T/'evidence/MONITOR_COMPLETE.json').read_text());assert not monitor['training_has_error'],'Student training error preserved in evidence/training/ERROR.json'
 run('select_student.py')
 run('run_post_evaluations.py')
 run('finalize_run.py')
 (T/'evidence/PIPELINE_PRE_ARCHIVE.json').write_text(json.dumps(dict(epoch=time.time(),bounded_training_and_all_evaluations_closed=True,all_result_reports_written=True,next='Archive complete source, actual PT files, failures and reports; final verification printed to the tool'),indent=2)+'\n')
 run('archive_run.py','--phase','complete')
 print('STUDENT_PIPELINE_COMPLETE_NO_FURTHER_TRAINING',flush=True)
except BaseException:
 (T/'evidence/PIPELINE_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),traceback=traceback.format_exc()),indent=2)+'\n');raise
