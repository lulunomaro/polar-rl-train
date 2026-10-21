from pathlib import Path
import runpy,json,time,traceback
B=Path(__file__).resolve().parent
try:runpy.run_path(str(B/'review_E3_native60_all104_rows_CPU_V2_once.py'),run_name='__main__')
except BaseException:
 (B/'reports'/('E3_NATIVE60_CPU_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8').write(json.dumps(dict(error=traceback.format_exc()),indent=2));raise
