"""Drain existing checkpoint evaluations, report results, and archive; never train."""
from pathlib import Path
import sys,time,json,subprocess,traceback
T=Path(__file__).resolve().parent;E=T/'evidence';R=T.parents[2]
while not(E/'MONITOR_COMPLETE.json').exists():time.sleep(20)
try:
 subprocess.run([sys.executable,'-X','utf8','-B',str(T/'select_student.py')],cwd=R,check=True)
 subprocess.run([sys.executable,'-X','utf8','-B',str(T/'finalize_run.py')],cwd=R,check=True)
 print('FINAL_EVALUATIONS_AND_REPORT_COMPLETE',flush=True)
 subprocess.run([sys.executable,'-X','utf8','-B',str(T/'archive_run.py'),'--phase','complete'],cwd=R,check=True)
 print('TRAINING_FINAL_REPORT_FULL_PT_ARCHIVED',flush=True)
except Exception:
 (E/'PIPELINE_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),traceback=traceback.format_exc(),automatic_new_training=False),indent=2)+'\n');raise
