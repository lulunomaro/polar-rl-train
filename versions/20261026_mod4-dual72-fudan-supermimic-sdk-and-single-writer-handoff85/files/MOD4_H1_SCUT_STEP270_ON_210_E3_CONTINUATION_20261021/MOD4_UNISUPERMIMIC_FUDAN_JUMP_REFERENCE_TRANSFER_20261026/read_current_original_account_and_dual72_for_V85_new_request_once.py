from pathlib import Path
import importlib.util,json,socket,time,traceback
J=Path(__file__).resolve().parent;T=J.parent;W=T.parent;N=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_RESOURCE_V85_20261026';R=N/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 R.mkdir(parents=True,exist_ok=True);put('DUAL72_V85_NEW_HUMAN_START_REQUEST_FRESH_PREFLIGHT_STARTED_ACTUAL.json',dict(epoch=time.time(),new_human_request='continue SuperMimic on dual4090',read_only=True,no_old_once_repeat=True,no_training_or_account_mutation=True))
 sp=importlib.util.spec_from_file_location('defs',T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83_20261026/relocate_minimal_closed81O_82Q_NPZ_for83_TLS_V5_unused_once.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);d=m.d
 q=json.loads((T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026/reports/THREE_EXPERT_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes())
 ms=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');mem=importlib.util.module_from_spec(ms);ms.loader.exec_module(mem);secret=mem.recover();c=None;result={}
 try:
  c=d.connect72(secret);secret=None
  src="from pathlib import Path;import json,shutil,subprocess,psutil,time;B=Path('/home/lc01/Zonglin Li/zonglin2/staging/MOD4_SINGLE4090_DISCONNECT_HANDOFF_20261026');r=json.loads((B/'HANDOFF_COMPLETE_ACTUAL.json').read_bytes());assert r['passed'];gpu=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True);print(json.dumps(dict(epoch=time.time(),host72_authenticated=True,free_disk=shutil.disk_usage(B).free,available_RAM=psutil.virtual_memory().available,GPU_UUID_freeMiB_utilization_only=gpu,staged_handoff_original_receipt=r,not_current_source_admission_or_GPU_process_identity_query=True)))"
  result['72']=d.code(c,d.PY72,src,{},timeout=30);c.close();c=None;put('DUAL72_V85_HOST72_FRESH_RESOURCE_AND_STAGED_RECEIPT_ACTUAL.json',result['72'])
  try:
   with socket.create_connection(('10.24.5.27',4090),timeout=5):pass
  except (OSError,TimeoutError):
   result['210']=dict(epoch=time.time(),TCP_original_forwarded_route_reachable=False,error=traceback.format_exc(),no_authentication_attempt_no_password_failure=True,original_canonical_unread_no_writer_or_GO=True)
  else:
   try:
    c=d.t.connect()
    source="from pathlib import Path;import json,psutil,time;C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');b=C.read_bytes();a=json.loads(b);assert a['active_segment'] is None and a['authorized_training_seconds']==2268000 and len(a['budget_extensions'])==9 and a['remaining_training_seconds']==595256.8240613937;B=Path(v['owner_root']);assert json.loads((B/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled'];i=v['owner_identity'];alive=False\ntry:\n p=psutil.Process(i['pid']);alive=abs(p.create_time()-i['creation'])<.01\nexcept psutil.NoSuchProcess:pass\nassert not alive and C.read_bytes()==b;print(json.dumps(dict(epoch=time.time(),original_pin_and_password_authenticated=True,canonicalNone=True,remaining=a['remaining_training_seconds'],previous_owner_actual_out=True,canonical_unchanged=True)))"
    result['210']=d.code(c,d.t.PY,source,dict(owner_root=q['owner_root'],owner_identity=q['owner_identity']),timeout=30)
   except BaseException:result['210']=dict(epoch=time.time(),original_account_read_passed=False,error=traceback.format_exc(),no_new_writer_or_GO=True)
   finally:
    if c:c.close();c=None
  put('DUAL72_V85_NEW_REQUEST_ORIGINAL_ACCOUNT_FRESH_RESULT_ACTUAL.json',dict(epoch=time.time(),hosts=result,source_canonical_usable=result['210'].get('canonicalNone',False),no_GPUload_training_or_budget_mutation=True));print(json.dumps(result))
 except BaseException:
  put('DUAL72_V85_PREFLIGHT_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),partial=result));raise
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':main()
