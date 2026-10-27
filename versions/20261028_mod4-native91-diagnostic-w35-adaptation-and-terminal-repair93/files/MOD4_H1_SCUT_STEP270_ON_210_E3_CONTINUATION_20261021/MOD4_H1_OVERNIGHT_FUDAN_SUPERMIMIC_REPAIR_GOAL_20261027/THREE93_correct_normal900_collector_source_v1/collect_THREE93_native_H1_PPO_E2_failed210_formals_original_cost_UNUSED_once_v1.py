"""UNUSED normal93 collector; serial original72 then original210, no control writes."""
from pathlib import Path
import sys,time,json,hashlib,base64,zlib,importlib.util,traceback,threading
HERE=Path(__file__).resolve().parent;L=HERE.parent;T=L.parent;W=T.parent;N=T/'MOD4_H1_FLAT05_TERMINAL_EXPOSURE_RESOURCE_V93_20261028';R=N/'reports'
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def decode_texts(value,target):
 target.mkdir();rows=[]
 for row in value.pop('texts'):
  raw=zlib.decompress(base64.b64decode(row.pop('zlib_base64')));assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['SHA']
  path=target/(hashlib.sha256(row['relative'].encode()).hexdigest()[:20]+'_'+Path(row['relative']).name)
  with path.open('xb') as f:f.write(raw)
  rows.append(dict(**row,local_path=str(path)))
 return rows
def main():
 started=time.time();first=json.loads((R/'THREE93_ALL_FIRST_POLICY_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json').read_bytes());go=first['go'];assert set(go)=={'h1','h1_210','e2'}
 assert max(g['nominal_end_epoch'] for g in go.values())-time.time()<=900,'original local normal900 earliest2026-10-28 03:04:49.189934BJT'
 marker='THREE93_NORMAL900_CLOSING_CONSUMED_ACTUAL_V1.json';assert not (R/marker).exists();put(marker,dict(epoch=time.time(),maxsignednominalend_minus_now_le900=True,original_owner850_node180_SSH1140=True))
 request=json.loads((R/'THREE93_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json').read_bytes());actual=json.loads((R/'THREE93_ACTUAL_OWNER_AND_THREE_NODES_DETACHED.json').read_bytes());failed=json.loads((R/'THREE93_FAILED210_ORIGINAL_FEE_OWNOUT_ALL_TEXT_RETURNED_ACTUAL.json').read_bytes());assert failed['passed'] and failed['cost']['original_fee']['charged_seconds']==51.172107219696045
 identities=actual['identities'];bound=dict(owner=identities['owner']['exact_identity'],nodes={k:identities[k]['exact_identity'] for k in go})
 code=module('three93_exact_explicit_CODE',HERE/'THREE93_natural_closing_remote_CODE_v1.py')
 wrapper=module('three93_same_authorized_compressed_memory_install_only',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrapper.install()
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sec=module('three93_authorized_password_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();c=None;stop=threading.Event()
 def progress():
  while not stop.wait(25):print(json.dumps(dict(stage='SAME_HANDLE_THREE93_ORIGINAL_NORMAL_CLOSE',epoch=time.time())),flush=True)
 thread=threading.Thread(target=progress,daemon=True);thread.start()
 try:
  c=d.connect72(secret);secret=None
  v=d.code(c,d.PY72,code.CODE72,dict(go=go,actual=bound,h1_job=request['experts']['h1']['job_root'],e2_job=request['experts']['e2']['job_root'],owner_root=request['owner_root'],h1_node_root=request['node_roots']['h1'],e2_node_root=request['node_roots']['e2']),timeout=1140)
  v['all_original_72_texts_full_case_safe']=decode_texts(v,N/'closed93_actual_72_text')
  for key,pub in v['published'].items():
   assert key in ('h1','e2');target=N/'current_closed93_models'/key/'formal/model_final.pt';target.parent.mkdir(parents=True);assert not target.exists()
   sf=c.open_sftp();sf.get_channel().settimeout(180)
   try:a=sf.stat(pub['path']);sf.get(pub['path'],str(target));b=sf.stat(pub['path'])
   finally:sf.close()
   assert a.st_size==b.st_size==pub['bytes'] and a.st_mtime==b.st_mtime
   with target.open('rb') as f:SHA=hashlib.file_digest(f,'sha256').hexdigest()
   assert SHA==pub['SHA'];pub.update(local_path=str(target),twohost_complete_SHA=True,NEW_formal_transfer_count=1)
  c.close();c=None;put('THREE93_PRIMARY72_FORMALS_OR_PARTIAL_ORIGINAL_COST_RETURNED_ACTUAL_V1.json',v)
  assert time.time()-started<1140,'original bounded whole collection envelope'
  c=route.connect();s=request['experts']['h1_210']
  value=d.code(c,route.PY,code.CODE210,dict(go=go['h1_210'],job=s['job_root'],node=request['node_roots']['h1_210'],private_lock=s['private_lock'],node_identity=bound['nodes']['h1_210']),timeout=min(180,1140-(time.time()-started)))
  c.close();c=None;value['all_original_failed210_texts_full_case_safe']=decode_texts(value,N/'closed93_actual_failed210_text');v['failed210_original_outcome_and_resources']=value
  v['all_original_texts_full_case_safe']=v['all_original_72_texts_full_case_safe']+value['all_original_failed210_texts_full_case_safe'];v['all_three_original_nodes_workers_owner_out']=True;v['original_owner_private_shared_locks_free']=True
  v['actual_serial_twohost_transport_returned']=True;v['failed210_original_fee_already_in_sum_not_charged_again']=51.172107219696045
  put('THREE93_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL_V1.json',v)
  print(json.dumps(dict(passed_collection=True,published={k:dict(SHA=p['SHA'],bytes=p['bytes']) for k,p in v['published'].items()},formal_keys=list(v['published']),original_fee_by_slot=v['original_fee_by_slot'],original_fee_seconds=v['original_fee_seconds'],closing=v['closing_remaining_snapshot'],NEW_formal_CPU_still_pending=list(v['published']))))
 finally:
  secret=None;stop.set();thread.join(timeout=1)
  if c:c.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('THREE93_NORMAL_CLOSING_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry_kill_refund_model_promotion_or_secondwriter=True));raise
