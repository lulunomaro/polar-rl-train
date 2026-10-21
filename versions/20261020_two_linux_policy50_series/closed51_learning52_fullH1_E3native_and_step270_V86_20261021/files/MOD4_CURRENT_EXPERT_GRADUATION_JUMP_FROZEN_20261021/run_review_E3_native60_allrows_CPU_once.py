from pathlib import Path
import json,runpy,sys,time,traceback
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B))
try:runpy.run_path(str(B/'review_E3_native60_all104_rows_CPU_once.py'),run_name='__main__')
except BaseException:
 (B/'reports'/('run_review_E3_native60_allrows_CPU_once_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8').write(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay=True),indent=2));raise
