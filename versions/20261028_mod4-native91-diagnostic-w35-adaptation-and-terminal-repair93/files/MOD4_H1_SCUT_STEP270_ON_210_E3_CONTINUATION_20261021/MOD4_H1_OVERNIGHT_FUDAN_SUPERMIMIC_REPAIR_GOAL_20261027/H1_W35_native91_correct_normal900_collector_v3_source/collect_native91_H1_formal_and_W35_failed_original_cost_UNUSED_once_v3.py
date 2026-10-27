"""UNUSED normal91 once: exact local+remote maxnominal-now<=900; no premature close."""
from pathlib import Path
import sys,time,json,hashlib,base64,zlib,importlib.util,traceback,threading
HERE=Path(__file__).resolve().parent;L=HERE.parent;T=HERE.parents[1];W=HERE.parents[2];N=T/'MOD4_H1_FLAT05_MASK_AWARE_MIXED72_RESOURCE_V91_20261027';R=N/'reports'
from native91_H1_W35_natural_closing_remote_CODE_v3 import CODE

def put(n,value):
 with (R/n).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
def main():
 first=json.loads((L/'H1_W35_next_mixed72_owner_deployment_source_v2/reports/COMBINED_TWO_SLOT_FIRST_OBSERVER_RETURNED_ACTUAL_V2.json').read_bytes());go=first['actual_GO']
 assert max(g['nominal_end_epoch'] for g in go.values())-time.time()<=900,'original local normal900 gate earliest2026-10-28 00:24:33.660105BJT'
 assert not (R/'NATIVE91_NORMAL_CLOSING_CONSUMED_ACTUAL_V3.json').exists()
 put('NATIVE91_NORMAL_CLOSING_CONSUMED_ACTUAL_V3.json',dict(epoch=time.time(),correct_local900_rule='max signed nominalend-now<=900',original_owner850_node180=True))
 request=json.loads((L/'H1_W35_next_mixed72_owner_deployment_source_v2/ACTUAL_MIXED72_PUBLIC_REQUEST_POSIX_SEALED_V3.json').read_bytes());actual=json.loads((L/'H1_W35_next_mixed72_owner_deployment_source_v2/reports/MIXED72_ONE_OWNER_TWO_NODES_LAUNCHED_ACTUAL_V4.json').read_bytes());h1=first['H1_first'];assert h1['passed_first_native_flat_policy']
 p=W/'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py';s=importlib.util.spec_from_file_location('same_authorized_zstd_memory_normal91close_only',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);transport,previous=m.install()
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('normal91close_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec);secret=sec.recover();c=None;stop=threading.Event()
 def progress():
  while not stop.wait(25):print(json.dumps(dict(stage='SAME_HANDLE_ORIGINAL_NORMAL_CLOSING_WAIT',epoch=time.time())),flush=True)
 thread=threading.Thread(target=progress,daemon=True);thread.start()
 try:
  c=d.connect72(secret);secret=None
  v=d.code(c,d.PY72,CODE,dict(go=go,actual=actual,h1_worker=h1['worker'],h1_job=request['h1_spec']['job_root'],w35_job='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_PPO50_GAS400_2610v91/w35',owner_root=request['owner_root'],h1_node_root=request['h1_node_root'],w35_node_root=request['w35_request']['node_root']),timeout=1140)
  target=N/'closed_actual_text';target.mkdir();rows=[]
  for row in v.pop('texts'):
   data=zlib.decompress(base64.b64decode(row.pop('zlib_base64')));assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['SHA']
   safe_name=hashlib.sha256(row['relative'].encode()).hexdigest()[:20]+'_'+Path(row['relative']).name;p=target/safe_name
   with p.open('xb') as f:f.write(data)
   rows.append(dict(**row,local_path=str(p)))
  v['all_original_texts_full_case_safe']=rows;published=v['published']
  if published:
   p=N/'current_native_flat_method_fullstate/formal/native_supermimic_H1_final.pt';p.parent.mkdir(parents=True);assert not p.exists();sf=c.open_sftp();sf.get_channel().settimeout(180)
   try:a=sf.stat(published['path']);sf.get(published['path'],str(p));b=sf.stat(published['path'])
   finally:sf.close()
   assert a.st_size==b.st_size==published['bytes'] and a.st_mtime==b.st_mtime
   with p.open('rb') as f:SHA=hashlib.file_digest(f,'sha256').hexdigest()
   assert SHA==published['SHA'];published.update(local_path=str(p),twohost_complete_SHA=True,NEW_formal_transfer_count=1)
  put('NATIVE91_COMPLETE_FINAL_OR_PARTIAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json',v)
  print(json.dumps(dict(actual_closed=True,H1_formal_collected=bool(published),W35_failed_noformal=True,fee=v['original_fee_seconds'],fee_by_slot=v['original_fee_by_slot'],closing=v['closing_remaining_snapshot'],only_NEW_H1_whole_CPU_still_required=True)))
 finally:
  secret=None;stop.set();thread.join(timeout=1)
  if c:c.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('NATIVE91_CLOSING_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_retry_kill_refund_or_secondwriter=True));raise
