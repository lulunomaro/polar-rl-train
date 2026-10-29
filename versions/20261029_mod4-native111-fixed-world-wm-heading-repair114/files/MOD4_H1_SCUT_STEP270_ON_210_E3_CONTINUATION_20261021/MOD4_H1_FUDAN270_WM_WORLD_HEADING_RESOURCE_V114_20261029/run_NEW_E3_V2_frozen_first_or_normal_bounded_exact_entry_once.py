"""Exact new E3V2 read-only finite entry; stdout full local file, compact result."""
from pathlib import Path
import json,hashlib,subprocess,sys,time,argparse,traceback
N=Path(__file__).resolve().parent;R=N/'reports';L=N.parent/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
D=L/'E3_97_Q34_INITIAL24_DEVICE_ROUTING_CASE_SOURCE_20261029_V2'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main(mode):
 assert H(D/'FROZEN_E3_Q34_INITIAL24_DEVICE_ROUTE_COMPLETE_SOURCE_INDEX_V2.json')=='69cf20f50225cb1a7ded3f79bcc53b357bd8a10a70139eb3c77ff54c98b4e719'
 index=json.loads((D/'FROZEN_E3_Q34_INITIAL24_DEVICE_ROUTE_COMPLETE_SOURCE_INDEX_V2.json').read_bytes())
 startup=D/'reports/E3_SOURCE210_ACTUAL_METADATA_CPU_AND_FINITE_DETACHED_RETURNED_ACTUAL.json';v=json.loads(startup.read_bytes());assert v['passed_source_CPU_and_detached_only']
 if mode=='normal':assert v['detached']['identity']['creation']+1800-time.time()<=900,'LOCAL900 gate closed, rootmarker unused'
 name='read_E3_source210_FIRST_native24_recipe_queue_UNUSED_once_v4.py' if mode=='first' else 'collect_E3_source210_TERMINAL_recipe_fulltext_UNUSED_once_v4.py'
 assert H(D/name)==index['local_source_SHAs'][name]
 marker='ROOT_E3_V2_'+mode.upper()+'_EXACT_ENTRY_CONSUMED.json';assert not (R/marker).exists()
 put(marker,dict(epoch=time.time(),entry=str(D/name),entry_SHA=H(D/name),startup_SHA=H(startup),no_model_GPU_query_or_account=True))
 args=[sys.executable,'-u','-B','-X','utf8',str(D/name),'--actual-startup-json',str(startup),'--actual-startup-SHA',H(startup)]
 with (R/('ROOT_E3_V2_'+mode.upper()+'_COMPLETE_STDOUT_STDERR.log')).open('xb') as out:
  p=subprocess.Popen(args,cwd=D,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT)
  try:rc=p.wait(timeout=500 if mode=='first' else 1020)
  except subprocess.TimeoutExpired:
   p.terminate();rc=p.wait(timeout=20);raise
 result=dict(epoch=time.time(),returncode=rc,actual_local_child_waited=True,entry=str(D/name))
 put('ROOT_E3_V2_'+mode.upper()+'_LOCAL_WAIT_RETURNED_ACTUAL.json',result);print(json.dumps(result),flush=True)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--mode',choices=('first','normal'),required=True);mode=a.parse_args().mode
 try:main(mode)
 except BaseException:put('ROOT_E3_V2_'+mode.upper()+'_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_automatic_retry=True));raise
