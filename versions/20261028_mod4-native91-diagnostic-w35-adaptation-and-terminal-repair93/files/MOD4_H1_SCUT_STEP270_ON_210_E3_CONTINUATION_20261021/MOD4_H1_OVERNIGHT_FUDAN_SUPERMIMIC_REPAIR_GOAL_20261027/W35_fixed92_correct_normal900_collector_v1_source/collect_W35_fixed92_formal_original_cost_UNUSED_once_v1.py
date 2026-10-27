"""UNUSED correct signed normal900 collector. No training control or input model read."""
from pathlib import Path
import sys,time,json,hashlib,base64,zlib,importlib.util,traceback,threading
HERE=Path(__file__).resolve().parent;L=HERE.parent;T=HERE.parents[1];W=HERE.parents[2];R=HERE/'reports'
def put(n,value):
 R.mkdir(exist_ok=True)
 with (R/n).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
def load_module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def main():
 first=json.loads((L/'W35_fixed92_firstPPO_metadata_source_v1/reports/FIXED92_W35_FIRST_ACTUAL_FULLRESTORE_NATIVE24_PPO_RETURNED_ACTUAL.json').read_bytes());assert first['passed_first_W35_real_PPO'];go=first['go']
 assert go['nominal_end_epoch']-time.time()<=900,'original local normal900 earliest2026-10-28 01:39:50.600079BJT'
 assert not (R/'W35_FIXED92_NORMAL_CLOSING_CONSUMED_ACTUAL_V1.json').exists()
 put('W35_FIXED92_NORMAL_CLOSING_CONSUMED_ACTUAL_V1.json',dict(epoch=time.time(),correct_local900_rule='signed nominalend-now<=900',original_owner850_node180=True))
 request=json.loads((L/'W35_fixed92_single72_owner_source_v2/reports/W35_FIXED92_ACTUAL_PUBLIC_REQUEST.json').read_bytes());actual=json.loads((L/'W35_fixed92_single72_owner_source_v2/reports/W35_FIXED92_OWNER_NODE_LAUNCHED_ACTUAL.json').read_bytes())
 CODE=load_module('w35_fixed92_exact_closed_reader_CODE',HERE/'w35_fixed92_natural_closing_remote_CODE_v1.py').CODE
 p=T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py';m=load_module('w35_fixed92_same_session_memory_only',p);transport,previous=m.install()
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sec=load_module('w35_fixed92_normalclose_authorized_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();c=None;stop=threading.Event()
 def progress():
  while not stop.wait(25):print(json.dumps(dict(stage='SAME_HANDLE_ORIGINAL_NORMAL_CLOSING_WAIT',epoch=time.time())),flush=True)
 thread=threading.Thread(target=progress,daemon=True);thread.start()
 try:
  c=d.connect72(secret);secret=None
  v=d.code(c,d.PY72,CODE,dict(go=go,actual=actual,job_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_PPO50_GAS400_RETENTION_2610v92/w35',owner_root=request['owner_root'],node_root=request['node_root']),timeout=1140)
  target=HERE/'closed_actual_text';target.mkdir();rows=[]
  for row in v.pop('texts'):
   data=zlib.decompress(base64.b64decode(row.pop('zlib_base64')));assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['SHA']
   safe_name=hashlib.sha256(row['relative'].encode()).hexdigest()[:20]+'_'+Path(row['relative']).name;p=target/safe_name
   with p.open('xb') as f:f.write(data)
   rows.append(dict(**row,local_path=str(p)))
  v['all_original_texts_full_case_safe']=rows;published=v['published']
  if published:
   p=HERE/'current_qualified_candidate/formal/model_final.pt';p.parent.mkdir(parents=True);assert not p.exists();sf=c.open_sftp();sf.get_channel().settimeout(180)
   try:a=sf.stat(published['path']);sf.get(published['path'],str(p));b=sf.stat(published['path'])
   finally:sf.close()
   assert a.st_size==b.st_size==published['bytes'] and a.st_mtime==b.st_mtime
   with p.open('rb') as f:SHA=hashlib.file_digest(f,'sha256').hexdigest()
   assert SHA==published['SHA'];published.update(local_path=str(p),twohost_complete_SHA=True,NEW_formal_transfer_count=1)
  put('W35_FIXED92_COMPLETE_FINAL_OR_PARTIAL_ORIGINAL_COST_RETURNED_ACTUAL.json',v)
  print(json.dumps(dict(actual_closed=True,W35_formal_collected=bool(published),fee=v['original_fee_seconds'],closing=v['closing_remaining_snapshot'],only_NEW_formal_CPU_still_required=bool(published))))
 finally:
  secret=None;stop.set();thread.join(timeout=1)
  if c:c.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('W35_FIXED92_CLOSING_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_retry_kill_refund_or_secondwriter=True));raise
