import json,time,traceback
from pathlib import Path
import inspect_windows4090_actual_once as reader
from windows4090_native_transport import connect,powershell
reader.connect=connect;reader.powershell=powershell
if __name__=='__main__':
 try:reader.main()
 except BaseException:
  (Path(__file__).resolve().parent/'reports'/('WINDOWS4090_NATIVE_READONLY_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_OS_mutation=True)),encoding='utf8');raise
