"""Deliver exact worker bytes and independently admit a new stopped-fault namespace."""
from slope_io import *
sys.path.insert(0,str(W/'MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011'))
from curb_io import WIN
import traceback

def main():
 source=(W/'MOD4_E1_G3_35MM_SCOPE_PREPARE_20261010/eval_worker_e1_g3_package_review.py').read_bytes();assert H(source)=='d2ee915a043b39bfe63dc50f0e84e85576ee295b15b619bf5331f918a301a316'
 text=source.decode().replace('E1_G3_PACKAGE_REVIEW','E1_SLOPE8_QUERY_REVIEW')
 anchor="PAUSED_SHALLOW_JOBS=";idx=text.index(anchor)
 text=text[:idx]+"RETIRED=RETIRED+('clk2500-closure-episode-d3-136-e1-slope8-source404-mirrored-fullroute-flat',)\n"+text[idx:]
 compile(text,'eval_worker_e1_slope8_query_review.py','exec');worker=D/'eval_worker_e1_slope8_query_review.py';assert not worker.exists();worker.write_bytes(text.encode())
 result=(R/'failed136/result.json').read_bytes();error=(R/'failed136/probe.json.error.txt').read_bytes()
 expected=dict(epoch=time.time(),old_worker_SHA=H(source),new_worker_SHA=H(worker.read_bytes()),result136_SHA=H(result),error136_SHA=H(error),
  namespace_only_and_exact_failed136_exclusion=True,no_base_bridge_lock_or_JSON_retry_change=True)
 ep=save('SLOPE8_QUERY_WORKER_EXPECTED.json',expected);save('SLOPE8_QUERY_WORKER_DEPLOY_STARTED.json',dict(epoch=time.time(),once=True))
 n,w=connect_both()
 try:
  with w.open_sftp() as f:
   for local,remote in ((worker,worker.name),(D/'admit_slope8_query_worker_once.py','admit_slope8_query_worker_once.py'),(ep,'SLOPE8_QUERY_WORKER_EXPECTED.json')):
    raw=local.read_bytes();put(f,WIN+'/'+remote,raw)
  _,o,e=w.exec_command('D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe -X utf8 '+WIN+'/admit_slope8_query_worker_once.py',timeout=60);out=o.read();err=e.read();rc=o.channel.recv_exit_status()
  p=R/'SLOPE8_QUERY_WORKER_DEPLOY_OUTPUT.txt';assert not p.exists();p.write_bytes(out+err);assert rc==0,(out+err).decode(errors='replace')
  with w.open_sftp() as f:
   for name in ('ADMISSION','STARTED','ADMITTED'):
    raw=f.open(WIN+'/E1_SLOPE8_QUERY_REVIEW_WORKER_'+name+'.json').read();p=R/('E1_SLOPE8_QUERY_REVIEW_WORKER_'+name+'.json');assert not p.exists();p.write_bytes(raw)
  print(out.decode())
 finally:cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:save('SLOPE8_QUERY_WORKER_DEPLOY_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_blind_replay=True));raise
