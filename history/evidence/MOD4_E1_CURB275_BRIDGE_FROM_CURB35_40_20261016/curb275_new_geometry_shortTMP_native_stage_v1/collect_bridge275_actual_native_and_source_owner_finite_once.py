from pathlib import Path
import os,sys,json,time,traceback
P=Path(__file__).resolve().parent;D=P.parent/'MOD4_THREE4090_CURB_DIRECTION_AND_E3_RECOVERY_20261016';R=P/'reports';sys.path.insert(0,str(D))
from deploy_V9_actual_CPU_status_fix_E2_E3_CURB_deferred_once import code,H,t,ROOTS
from collect_first_two_native_and_E2_handoff_actual_readonly_once import READ
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 root=ROOTS['curb'];case=root+'/curb275_bridge_case_v1';put('BRIDGE275_NATIVE_READER_FINITE_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport_owner=True,max_same_connection_wait_seconds=240,readonly=True));c=None;v={}
 try:
  c=t.connect();begin=time.time()
  while True:
   s=code(c,t.PY,"from pathlib import Path;import sys,json,time;A=Path(sys.argv[1]);B=Path(sys.argv[2]);cur=json.loads((A/'OWNER_CURRENT.json').read_bytes());o=B/'job0/native20k_then_production';print(json.dumps(dict(epoch=time.time(),phase=cur['rows']['curb']['phase'],original_error=cur['rows']['curb'].get('original_error'),CPU_pass=(o/'INDEPENDENT_NATIVE_CPU_ADMITTED.json').exists(),native_final=(o/'FINAL.json').exists(),error_files=[str(p) for p in o.glob('*ORIGINAL_ERROR*')],GO=cur['go'].get('curb'))))",root,case)
   if s['CPU_pass'] or s['error_files'] or s['original_error'] or time.time()-begin>=240:break
   time.sleep(12)
  v['last_wait_actual']=s;v['owner']=code(c,t.PY,READ,root,'curb');v['case']=code(c,t.PY,READ,case,'curb');rows=code(c,t.PY,"from pathlib import Path;import sys,json,hashlib;B=Path(sys.argv[1]);O=B/'job0/native20k_then_production';names=['own_restored0.pt','own_native144.pt'];out=[]\nfor n in names:\n p=O/n\n if p.is_file():out.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()))\nprint(json.dumps(dict(models=out)))",case);v['models']=[];folder=P/'actual_native_models';folder.mkdir();sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:
   for row in rows['models']:
    p=folder/Path(row['path']).name;q=p.with_suffix('.pt.partial');assert not p.exists() and not q.exists();sf.get(row['path'],str(q));assert q.stat().st_size==row['bytes'] and H(q)==row['SHA'];q.replace(p);v['models'].append(dict(**row,local_path=str(p),twohost_complete_SHA=True))
  finally:sf.close()
 finally:t.close(c)
 v['epoch']=time.time();put('BRIDGE275_ACTUAL_NATIVE_OR_PENDING_OWNER_BOUND_COLLECTION.json',v);print(json.dumps(dict(last_wait_actual=v['last_wait_actual'],models=v['models'],case_actual_processes=[dict(pid=x['pid'],creation=x['create_time'],entry=next((a for a in x['cmdline'] if a.endswith('.py')),None)) for x in v['case']['actual_own_processes']])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('BRIDGE275_NATIVE_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_once_replay=True));raise
