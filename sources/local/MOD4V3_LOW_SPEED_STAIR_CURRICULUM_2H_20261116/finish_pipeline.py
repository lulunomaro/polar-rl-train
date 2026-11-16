"""Finish collection/report/archive after the finite job closes; never launch PPO."""
from pathlib import Path
import sys,time,json,subprocess,traceback
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
try:
 while not(E/'MONITOR_COMPLETE.json').exists():time.sleep(20)
 subprocess.run([sys.executable,'-X','utf8','-B',str(T/'finalize_run.py')],cwd=R,check=True)
 with(E/'ARCHIVE_COMPLETE.log').open('wb')as log:
  result=subprocess.run([sys.executable,'-X','utf8','-B',str(T/'archive_run.py'),'--phase','complete'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 if result.returncode:raise RuntimeError('Final Git archive pending; keep existing commit/tag and inspect ARCHIVE_COMPLETE.log')
 (E/'PIPELINE_COMPLETE.json').write_text(json.dumps(dict(epoch=time.time(),finite_training_closed=True,report_and_full_PT_archived=True,promoted=False,no_additional_PPO=True),indent=2)+'\n')
 with(E/'ARCHIVE_FOLLOWUP.log').open('wb')as log:
  result=subprocess.run([sys.executable,'-X','utf8','-B',str(T/'archive_run.py'),'--phase','followup'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 if result.returncode:raise RuntimeError('Closure receipt archive pending')
except Exception:
 (E/'PIPELINE_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),traceback=traceback.format_exc(),no_additional_PPO=True),indent=2)+'\n');raise
