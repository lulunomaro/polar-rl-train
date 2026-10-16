from pathlib import Path
import sys,os,time,json,traceback
P=Path(__file__).resolve().parent;D=P.parent/'MOD4_THREE4090_CURB_DIRECTION_AND_E3_RECOVERY_20261016';R=P/'reports';sys.path.insert(0,str(D))
from deploy_V9_actual_CPU_status_fix_E2_E3_CURB_deferred_once import code,H,t
from collect_first_two_native_and_E2_handoff_actual_readonly_once import READ
ROOT='/mnt/mod4_linux_durable_20261013/C275_1610v2'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 put('SHORT_TMP_ACTUAL_NATIVE_READER_STARTED.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport_owner=True,max_one_connection_wait_seconds=240,readonly=True));c=None
 try:
  c=t.connect();beg=time.time()
  while True:
   s=code(c,t.PY,"from pathlib import Path;import json,sys,time;B=Path(sys.argv[1]);p=B/'PARENT_CURRENT.json';v=json.loads(p.read_bytes()) if p.exists() else {};print(json.dumps(dict(epoch=time.time(),current=v,native_CPU=(B/'OWN_NATIVE_CPU_ADMITTED_ACTUAL.json').exists(),error=(B/'PARENT_ORIGINAL_ERROR.json').exists(),exit=(B/'PARENT_EXIT_ACTUAL.json').exists())))",ROOT)
   if s['native_CPU'] or s['error'] or time.time()-beg>=240:break
   time.sleep(15)
  v=code(c,t.PY,READ,ROOT,'curb');v['last_wait_actual']=s;rows=code(c,t.PY,"from pathlib import Path;import sys,json,hashlib;B=Path(sys.argv[1]);O=B/'job0/native20k_then_production';out=[]\nfor name in ('own_restored0.pt','own_native144.pt'):\n p=O/name\n if p.is_file():out.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()))\nprint(json.dumps(dict(models=out)))",ROOT);v['models']=[];folder=P/'actual_short_TMP_native_models';folder.mkdir();sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:
   for row in rows['models']:
    p=folder/Path(row['path']).name;q=p.with_suffix('.pt.partial');assert not p.exists() and not q.exists();sf.get(row['path'],str(q));assert q.stat().st_size==row['bytes'] and H(q)==row['SHA'];q.replace(p);v['models'].append(dict(**row,local_path=str(p),twohost_complete_SHA=True))
  finally:sf.close()
 finally:t.close(c)
 put('SHORT_TMP_ACTUAL_NATIVE_FULL_MODEL_CPU_OR_PENDING_BOUND_COLLECTION.json',v);print(json.dumps(dict(last_wait_actual=s,models=v['models'],errors=[x for x in v['files'] if 'ORIGINAL_ERROR' in x['path']],own_processes=[dict(pid=x['pid'],creation=x['create_time']) for x in v['actual_own_processes']])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put('SHORT_TMP_NATIVE_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_once_replay=True));raise
