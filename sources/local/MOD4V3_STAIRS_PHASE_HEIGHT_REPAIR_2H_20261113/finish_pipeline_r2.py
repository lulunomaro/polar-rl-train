"""Recover failed post-evaluation; never replay the completed training budget."""
from pathlib import Path
import sys,subprocess,json,time,traceback
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
def run(name,*args):
 print('RECOVERY_STAGE '+name,flush=True)
 result=subprocess.run([sys.executable,'-X','utf8','-B','-u',str(T/name),*args],cwd=R)
 if result.returncode:raise RuntimeError(name+' failed with '+str(result.returncode))
try:
 monitor=json.loads((E/'MONITOR_COMPLETE.json').read_text());assert monitor['training_closed'] and not monitor['training_has_error']
 assert all(x['exit_code']==0 for x in monitor['evaluations'])
 run('run_post_evaluations_r2.py');run('finalize_run_r2.py')
 (E/'PHYSICAL_RECOVERY_R2_COMPLETE.json').write_text(json.dumps(dict(epoch=time.time(),physical_evaluations_closed=True,training_replayed=False,original_failure_preserved='PIPELINE_ERROR.json'),indent=2)+'\n')
 run('archive_run.py','--phase','complete')
 (E/'PIPELINE_RECOVERY_R2_COMPLETE.json').write_text(json.dumps(dict(epoch=time.time(),physical_evaluations_closed=True,complete_archive_verified=True,training_replayed=False),indent=2)+'\n')
 print('BOUNDED2H_RECOVERY_COMPLETE_NO_FURTHER_TRAINING',flush=True)
except BaseException:
 (E/'PIPELINE_RECOVERY_R2_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),traceback=traceback.format_exc()),indent=2)+'\n');raise
