from pathlib import Path
import os,sys,json,time,traceback,importlib.util
HERE=Path(__file__).resolve().parent;W=HERE.parents[2];L=HERE.parent;R=HERE/'reports'
CODE=r"""from pathlib import Path
import json,time,psutil,hashlib,fcntl,subprocess
r=v['request'];owner=Path(r['owner_root']);job=Path(v['W35_job']);node=Path(r['node_roots']['w35']);C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json')
def read(p):return json.loads(p.read_bytes()) if p.is_file() else None
def own_state(identity):
 assert identity and identity['pid']>0 and isinstance(identity['creation'],(int,float))
 try:
  p=psutil.Process(identity['pid'])
  if p.create_time()!=identity['creation']:return dict(out=True,reason='original own PID reused; no unknown identity queried')
  status=p.status();dead=status in (psutil.STATUS_ZOMBIE,psutil.STATUS_DEAD)
  return dict(out=dead,pid=p.pid,creation=p.create_time(),status=status,exe=None if dead else p.exe(),argv=None if dead else p.cmdline())
 except psutil.NoSuchProcess:return dict(out=True,reason='original owned PID absent')
started=time.time()
while True:
 go=read(job/'GO_PRODUCTION.json');assert go['source_SHA']=='36825921fb3e4a368791be7802c8ff16977e899240ac21ed2c067b2287bb9393' and go['run_id']==r['run_id'] and go['original_owner_pid']==553988
 terminal=read(node/'NODE_TERMINAL_ACTUAL.json');exit=read(node/'NODE_EXIT_ACTUAL.json');current=read(owner/'OWNER_CURRENT.json') or {};raw=C.read_bytes();c=json.loads(raw);a=c['active_segment']
 assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and a and a['owner_parent_pid']==553988
 x=(a.get('experts') or {}).get('w35') or {};row=(current.get('rows') or {}).get('w35') or {}
 if terminal and exit and x.get('ended_epoch') is not None:
  assert terminal['row']['terminal_all_own_children_waited'] is True and exit['actual_all_own_children_waited'] is True and row['terminal_all_own_children_waited'] is True
  assert x['started_epoch']==go['learning_started_epoch'] and x['ended_epoch']==row['owner_received_terminal_epoch'] and x['actual_returncode']==terminal['row']['returncode']
  assert abs(x['charged_seconds']-(x['ended_epoch']-x['started_epoch']))<1e-5 and x['duration_bound_passed'] is True
  ns=own_state(read(node/'NODE_IDENTITY.json'));ws=own_state(read(job/'production_STARTED_ACTUAL.json'));assert ns['out'] and ws['out']
  break
 if time.time()-started>75:
  print(json.dumps(dict(passed=False,terminal_or_owner_fee_pending=True,go=go,terminal=terminal,node_exit=exit,owner_current_row=row,W35_active_fee=x,no_clearactive_or_kill_or_H1_stop=True)));raise SystemExit(0)
 time.sleep(3)
out=job/'adaptation';assert not (out/'PPO_POSITIVE_CURRENT.json').exists() and not (out/'FINAL.json').exists() and not (out/'SOURCE_FULLRESTORE_ZERO_VERIFIED.json').exists()
errors=[dict(path=str(p),text=p.read_text()) for root in (node,out) for p in sorted(root.glob('*ORIGINAL_ERROR*.json'))]
assert errors and terminal['row']['returncode']!=0 and terminal['row'].get('original_error')
lock=Path('/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_GPU-16828f91-2b45-b646-8dc0-9481138e2842.lock')
with lock.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
with Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock').open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
gpu='GPU-16828f91-2b45-b646-8dc0-9481138e2842';line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();apps=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
print(json.dumps(dict(passed=True,scope='failedW35 resource and original active-segment cost only; not model or skill source',go=go,node_terminal=terminal,node_exit=exit,worker_out=ws,node_out=ns,APP_CLOSING=read(out/'APP_CLOSING.json'),APP_CLOSED=read(out/'APP_CLOSED.json'),original_errors=errors,original_W35_fee_seconds=x['charged_seconds'],W35_expert_original_fee=x,canonical_SHA=hashlib.sha256(raw).hexdigest(),canonical_H1_still_active=True,active_owner=553988,remaining_snapshot=c['remaining_training_seconds'],H1_active_expert=a['experts'].get('h1'),W35_private_and_brief_shared_lock_free=True,selected_GPU_line=line,selected_compute_UUID_rows=sum(gpu in z for z in apps.splitlines()),unknown_PID_not_inspected=True,no_refund_rearm_C_write_or_H1_stop=True)))
"""
def save(n,value):
 with (R/n).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def main():
 assert len(sys.argv)==1;save('W35_V91_FAILURE_TERMINAL_FEE_ENTERED_ACTUAL_V1.json',dict(epoch=time.time(),own_pid=os.getpid(),script=str(Path(__file__).resolve())))
 r=json.loads((L/'H1_W35_next_mixed72_owner_deployment_source_v2/ACTUAL_MIXED72_OBSERVER_REQUEST_POSIX_SEALED_V3.json').read_bytes())
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('same_authorized72_memory_failedW35_fee_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec)
 secret=sec.recover();c=None
 try:
  c=d.connect72(secret);secret=None;result=d.code(c,d.PY72,CODE,dict(request=r,W35_job='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_PPO50_GAS400_2610v91/w35'),timeout=90);save('W35_V91_FAILURE_TERMINAL_ACTIVE72_ORIGINAL_FEE_RETURNED_ACTUAL_V1.json',result);print(json.dumps(result))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:save('W35_V91_FAILURE_TERMINAL_FEE_ORIGINAL_READER_ERROR_ACTUAL_V1.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry_or_account_mutation=True));raise
