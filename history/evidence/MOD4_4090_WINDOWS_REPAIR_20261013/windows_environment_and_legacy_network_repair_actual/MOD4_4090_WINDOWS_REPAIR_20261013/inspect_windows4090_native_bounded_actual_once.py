from pathlib import Path
import time,json,traceback
import inspect_windows4090_actual_once as reader
from windows4090_native_transport import connect,powershell
D=Path(__file__).resolve().parent
def bounded(session,code,timeout):
 attempts=[]
 for i in range(6):
  try:
   out=powershell(session,code,timeout);attempts.append(dict(attempt=i+1,epoch=time.time(),passed=True))
   (D/'reports'/('WINDOWS4090_NATIVE_METADATA_CONNECT_ATTEMPTS_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(attempts=attempts,read_only_no_GPU=True,bounded_not_periodic=True),indent=2),encoding='utf8');return out
  except RuntimeError as e:
   attempts.append(dict(attempt=i+1,epoch=time.time(),passed=False,error=str(e)))
   if not any(s in str(e) for s in ('kex_exchange','banner exchange','MaxStartups')):raise
   if i<5:time.sleep(5)
 (D/'reports'/('WINDOWS4090_NATIVE_METADATA_CONNECT_ATTEMPTS_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(attempts=attempts,read_only_no_GPU=True,bounded_not_periodic=True),indent=2),encoding='utf8');raise RuntimeError('Six bounded metadata connections rejected by SSH startup limit')
reader.connect=connect;reader.powershell=bounded
if __name__=='__main__':
 try:reader.main()
 except BaseException:
  (D/'reports'/('WINDOWS4090_NATIVE_BOUNDED_READONLY_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_OS_mutation=True)),encoding='utf8');raise
