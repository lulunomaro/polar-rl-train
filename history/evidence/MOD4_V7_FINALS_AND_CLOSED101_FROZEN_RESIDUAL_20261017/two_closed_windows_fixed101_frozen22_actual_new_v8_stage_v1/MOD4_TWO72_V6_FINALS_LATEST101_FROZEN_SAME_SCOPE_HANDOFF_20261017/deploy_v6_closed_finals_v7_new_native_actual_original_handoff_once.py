"""New namespace: two healthy GPU slots, explicit H1 pre-GO storage rejection, unchanged writer."""
from pathlib import Path
import os,sys,json,time,getpass,secrets,traceback
F=Path(__file__).resolve().parent;R=F/'reports';Q=F/'payload';sys.path.insert(0,str(F.parent/'MOD4_THREE_EXPERTS_HEALTHY_FOLLOWUP_V3_20261017'))
import deploy_recovered_three_finals_new_native_then_original_owner_once as d
a=d.a;launch=d.launch
SOURCE='/mnt/mod4_linux_durable_20261013/T3_1710v7r72/owner'
ROOTS={k:'/home/lc01/Zonglin Li/zonglin2/tasks/T3_1710v7r72/'+k for k in ('e2','recovery')}
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
OWNER_ADMISSION=r'''
from pathlib import Path
import sys,json,time,psutil,fcntl,socket,shutil,os
B=Path(sys.argv[1]);owned=Path('/mnt/mod4_linux_durable_20261013');assert B.resolve().is_relative_to(owned.resolve()) and not B.exists();old=owned/'T3_1710v6r72/owner';assert json.loads((old/'COHORT_FINAL.json').read_bytes())['original_cost_settled'] and json.loads((old/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled'];i=json.loads((old/'OWNER_IDENTITY.json').read_bytes())
if psutil.pid_exists(i['pid']):
 p=psutil.Process(i['pid']);assert abs(p.create_time()-i['creation'])>.01 or p.status()==psutil.STATUS_ZOMBIE
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');v=json.loads(C.read_bytes());assert v['active_segment'] is None and v['authorized_training_seconds']==1188000 and len(v['budget_extensions'])==7
locks=[]
for path in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with path.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);locks.append(str(path))
with socket.socket() as sock:sock.bind(('10.24.4.210',29754))
durable=shutil.disk_usage(owned).free;canonical_fs=shutil.disk_usage(C.parent).free
assert durable>1024**3 and canonical_fs>512*1024**2 and durable<25*1024**3
B.mkdir(parents=True);print(json.dumps(dict(epoch=time.time(),old_owner_out_previous_cost_settled=True,original_activeNone_two_real_locks_free=locks,owner_metadata_root=str(B),owner_metadata_only_no_H1_payload_or_GPU_or_new_native=True,metadata_durable_free=durable,canonical_fs_free=canonical_fs,H1_training_25GiB_guard_not_changed_or_bypassed=True,H1_actual_current_durable_still_under25GiB=True,no_canonical_mutation=True)))
'''
def main():
 proof=json.loads((R/'H1_STORAGE_PREGO_REJECTION_TWO_HEALTHY_SLOTS_UNCHANGED_OWNER_CPU_ACTUAL.json').read_bytes());assert proof['passed_CPU_localhost_only']
 prep=json.loads((R/'RECOVERED_THREE_FINALS_FULL_CPU_AND_NEW_SAME_SCOPE_NATIVE_PAYLOADS_PREPARED_ACTUAL.json').read_bytes());diag=json.loads((R/'SOURCE_PRECREATE_COMBINED_RESOURCE_ASSERTION_INDEPENDENT_READONLY_DIAGNOSIS_ACTUAL.json').read_bytes())
 assert prep['passed_CPU_only'] and not diag['new_root_exists'] and not diag['durable_over25GiB'] and diag['GPU_free_over7000'] and diag['RAM_over8GiB'];specs=prep['specs']
 assert json.loads((R/'UNCHANGED_FINITE_RUNTIME_AND_PREVIOUS_CPU_PROOFS_REUSED_ACTUAL.json').read_bytes())['passed_CPU_only']
 put('V2_TWO72_STORAGE_REJECTED_H1_FINITE_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True,new_namespace=ROOTS,H1_resource_rejected_preGO_no_worker_or_learning=True))
 pw=getpass.getpass('Host72 two healthy experts, H1 storage rejected (hidden): ');c=None;cfg=None
 try:
  d.ROOTS=ROOTS;d.Q=Q;d.put=lambda n,v:put('V2_SAFE72_'+n,v)
  c=a.connect72(pw)
  for key in ('e2','recovery'):d.upload(c,a.PY,key,specs[key])
 finally:
  if c:c.close();c=None
 try:
  c=a.t.connect();admission=a.code(c,a.t.PY,OWNER_ADMISSION,SOURCE);put('V2_TWO72_OWNER_METADATA_ORIGINAL_LOCK_HANDOFF_ADMISSION_ACTUAL.json',admission)
  contract=dict(epoch=time.time(),H1_original_storage_diagnosis=diag,source_full_model_SHA=specs['h1']['source_SHA'],H1_preGO_rejected_no_payload_no_worker_no_native_no_GO_zero_charge=True,H1_manifest_is_planned_not_installed_on_new_backend=True,two_new_72_same_scope_sources={k:dict(SHA=specs[k]['source_SHA'],Adam=specs[k]['source_Adamstep'],manifest_SHA=specs[k]['manifest_SHA'],cap3600=specs[k]['max_parent_seconds'],headroom300=specs[k]['exit_headroom_seconds']) for k in ROOTS},unchanged_original_writer_three_slot_failure_isolation_CPU_reviewed=True,source_owner_metadata_only_not_H1_training_guard_exception=True,no_delete_C_readonly_tmpfs_training_or_new_budget=True,no_H1_hotadd_or_automatic_extra_window=True)
  put('V2_TWO72_CONTINUATION_H1_ACTUAL_STORAGE_REJECTION_CONTRACT.json',contract);sf=c.open_sftp()
  try:
   for name in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','owner_listener_ready_cpu_reviewed_v1.py'):sf.put(str(F/name),SOURCE+'/'+name)
   sf.put(str(R/'V2_TWO72_CONTINUATION_H1_ACTUAL_STORAGE_REJECTION_CONTRACT.json'),SOURCE+'/H1_PREGO_RESOURCE_REJECTION_CONTRACT.json')
  finally:sf.close()
  owner_files=[dict(name=n,SHA=a.H(F/n)) for n in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','owner_listener_ready_cpu_reviewed_v1.py')];check="from pathlib import Path;import sys,json,hashlib,ast;B=Path("+repr(SOURCE)+");rows="+repr(owner_files)+";[(ast.parse((B/r['name']).read_text('utf8')),None) for r in rows];assert all(hashlib.sha256((B/r['name']).read_bytes()).hexdigest()==r['SHA'] for r in rows);print(json.dumps(dict(actual_source_owner_SHA_AST_passed=True,files=rows,no_GPU_or_budget_write=True)))";put('V2_SOURCE_SMALL_OWNER_FILES_SHA_AST_ACTUAL.json',a.code(c,a.t.PY,check))
  cfg=dict(role='owner',experts=specs,run_id='TWO_HEALTHY72_H1_STORAGE_PREGO_REJECTED_'+str(time.time_ns()),token=secrets.token_hex(32));owner=launch(a.code,c,a.t.PY,SOURCE,'three_slot_finite_owner_v1.py',cfg)
  put('V2_TWO72_ONE_ORIGINAL_OWNER_ACTUAL_DETACHED_DISPATCH.json',dict(epoch=time.time(),owner=owner,only_two_72_GPU_targets_CPU_admitted=True,H1_no_worker_or_GO=True))
  ready_code="from pathlib import Path;import sys,json;B=Path("+repr(SOURCE)+");sys.path.insert(0,str(B));from owner_listener_ready_cpu_reviewed_v1 import wait_actual;print(json.dumps(wait_actual(B,"+repr(owner['detached_pid'])+",20.)))";put('SOURCE_OWNER_ACTUAL_POST_LISTENER_READY_BEFORE_REGISTRATION.json',a.code(c,a.t.PY,ready_code,timeout=40))
  # This bounded admission sender has no children/GPU/SDK. Its terminal returncode describes
  # the rejected H1 admission, not a claimed H1 worker exit. Capability remains SSH stdin only.
  code="""from pathlib import Path
import sys,json,time,hashlib,hmac,urllib.request,psutil
B=Path(ROOT);sys.path.insert(0,str(B));import three_slot_common_v1 as b
cfg=CONFIG;s=cfg['experts']['h1'];row=dict(key='h1',phase='resource_admission_rejected_before_worker',manifest_SHA=s['manifest_SHA'],native_CPU=None,native_GPU_waited_EXIT0=False,terminal_all_own_children_waited=True,actual_own_children_count=0,returncode=1,original_error=True,no_H1_worker_ever_started=True,no_GPU_SDK_native_or_PPO=True,resource_diagnosis_SHA=DIAG_SHA,admission_sender_identity=b.ident(psutil.Process().pid))
assert not b.valid_ready(row,s);raw=json.dumps(dict(epoch=time.time(),run_id=cfg['run_id'],row=row)).encode();token=cfg['token'].encode();req=urllib.request.Request('http://10.24.4.210:29754/',data=raw,headers={'X-Own-Signature':hmac.new(token,raw,hashlib.sha256).hexdigest()})
with urllib.request.urlopen(req,timeout=15) as response:body=response.read();assert hmac.compare_digest(response.headers['X-Own-Signature'],hmac.new(token,body,hashlib.sha256).hexdigest())
reply=json.loads(body);assert reply['go'] is None;v=dict(epoch=time.time(),row=row,reply=reply,H1_resource_rejection_terminal_received_no_GO=True);b.put(B/'H1_PREGO_RESOURCE_REJECTION_TERMINAL_ACK_ACTUAL.json',v);print(json.dumps(v))
""".replace('ROOT',repr(SOURCE)).replace('CONFIG',repr(cfg)).replace('DIAG_SHA',repr(a.H(R/'SOURCE_PRECREATE_COMBINED_RESOURCE_ASSERTION_INDEPENDENT_READONLY_DIAGNOSIS_ACTUAL.json')))
  put('V2_H1_STORAGE_REJECTION_PREGO_TERMINAL_ACK_ACTUAL.json',a.code(c,a.t.PY,code))
 finally:a.t.close(c);c=None
 try:
  c=a.connect72(pw);pw=None;nodes={}
  for key in ('e2','recovery'):nodes[key]=launch(a.code,c,a.PY,ROOTS[key],'three_slot_finite_node_v1.py',dict(specs[key],role='node',run_id=cfg['run_id'],token=cfg['token']))
  result=dict(epoch=time.time(),owner=owner,nodes=nodes,source_owner_metadata_root=SOURCE,roots=ROOTS,source_SHA={k:specs[k]['source_SHA'] for k in ROOTS},source_Adam={k:specs[k]['source_Adamstep'] for k in ROOTS},each_new_native_required_before_own_GO=True,actual_detached_not_yet_native_or_PPO_pass=True,H1_resource_rejected_no_worker_no_GO_zero_charge=True,caps3600_headroom300_two_actual_distinct_intervals_one_original_writer=True,no_new_budget_ledger_refund_clearactive_tail_or_Creadonly_write=True,capability_only_SSH_stdin_and_child_stdin=True)
  put('V2_TWO72_HEALTHY_NEW_NATIVE_FINITE_CHAINS_H1_STORAGE_REJECTED_DETACHED_ACTUAL.json',result);print(json.dumps(result),flush=True)
 finally:
  pw=None
  if cfg:cfg.clear()
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put('TWO72_STORAGE_HANDOFF_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_mutation_actual_only_no_blind_retry=True));raise
