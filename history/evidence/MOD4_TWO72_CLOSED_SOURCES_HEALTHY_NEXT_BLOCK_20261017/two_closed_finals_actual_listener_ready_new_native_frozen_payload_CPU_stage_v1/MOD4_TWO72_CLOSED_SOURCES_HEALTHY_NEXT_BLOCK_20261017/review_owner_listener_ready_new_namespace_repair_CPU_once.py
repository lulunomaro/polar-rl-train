from pathlib import Path
import ast,time,json,copy,hashlib
G=Path(__file__).resolve().parent;R=G/'reports'
from owner_listener_ready_cpu_reviewed_v1 import validate_ready
root=Path('/fixture/owner');i=dict(pid=123,creation=time.time()-1,argv=['python',str(root/'three_slot_finite_owner_v1.py')]);c=dict(epoch=time.time(),rows=dict(h1={},e2={},recovery={}),go={},original_canonical_active=False,original_two_fcntl_held=False);assert validate_ready(root,123,i,c,i,[]);neg=[]
for name in ('missing_identity','wrong_PID','wrong_creation','wrong_argv','stale_current','premature_GO','unknown_node','owner_error'):
 a,b,d=copy.deepcopy(i),copy.deepcopy(c),copy.deepcopy(i);errors=[]
 if name=='missing_identity':a=None
 elif name=='wrong_PID':d['pid']=124
 elif name=='wrong_creation':d['creation']-=1
 elif name=='wrong_argv':d['argv']=['python','/different/owner.py']
 elif name=='stale_current':b['epoch']=i['creation']-1
 elif name=='premature_GO':b['go']={'e2':{'fake':True}}
 elif name=='unknown_node':b['rows']['unknown']={}
 elif name=='owner_error':errors=['OWNER_ORIGINAL_ERROR.json']
 try:validate_ready(root,123,a,b,d,errors)
 except AssertionError:neg.append(name)
 else:raise AssertionError(name)
s=(G/'deploy_two72_closed_sources_next_block_original_writer_once.py').read_text('utf8');assert s.count('T3_1710v4r72')==2;s=s.replace('T3_1710v4r72','T3_1710v5r72')
needle="assert B.resolve().is_relative_to(owned.resolve()) and not B.exists()";assert s.count(needle)==1
guard=""";rejected=owned/'T3_1710v4r72/owner';ex=json.loads((rejected/'OWNER_EXIT_ACTUAL.json').read_bytes());partial=json.loads((rejected/'NO_GO_PARTIAL_REGISTRATION_EXPIRED_ACTUAL.json').read_bytes());assert ex['original_cost_settled'] and partial['no_PPO_or_original_locks_or_canonical_write'] and not partial['observed'];ri=json.loads((rejected/'OWNER_IDENTITY.json').read_bytes())
if psutil.pid_exists(ri['pid']):
 rp=psutil.Process(ri['pid']);assert abs(rp.create_time()-ri['creation'])>.01 or rp.status()==psutil.STATUS_ZOMBIE
"""
s=s.replace(needle,needle+guard)
upload="for name in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py'):sf.put";assert s.count(upload)==1;s=s.replace(upload,"for name in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','owner_listener_ready_cpu_reviewed_v1.py'):sf.put")
hashlist="for n in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py')";assert s.count(hashlist)==1;s=s.replace(hashlist,"for n in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','owner_listener_ready_cpu_reviewed_v1.py')")
needle="put('TWO72_ONE_ORIGINAL_OWNER_ACTUAL_DETACHED_DISPATCH.json',dict(epoch=time.time(),owner=owner,only_two_72_GPU_targets_CPU_admitted=True,H1_no_worker_or_GO=True))";assert s.count(needle)==1
ready="\n  ready_code=\"from pathlib import Path;import sys,json;B=Path(\"+repr(SOURCE)+\");sys.path.insert(0,str(B));from owner_listener_ready_cpu_reviewed_v1 import wait_actual;print(json.dumps(wait_actual(B,\"+repr(owner['detached_pid'])+\",20.)))\";put('SOURCE_OWNER_ACTUAL_POST_LISTENER_READY_BEFORE_REGISTRATION.json',a.code(c,a.t.PY,ready_code,timeout=40))"
s=s.replace(needle,needle+ready);s=s.replace("put('TWO72_STORAGE_REJECTED_H1_FINITE_DEPLOY_STARTED_ACTUAL.json'","put('V2_TWO72_STORAGE_REJECTED_H1_FINITE_DEPLOY_STARTED_ACTUAL.json'")
# Reuse the already uploaded exact static/source payload in unused v4 node roots;
# new namespaces still take their actual prior completed source/OS-lock contract.
s=s.replace("put('SAFE72_'+n,v)","put('V2_SAFE72_'+n,v)")
s=s.replace("put('TWO72_OWNER_METADATA_ORIGINAL_LOCK_HANDOFF_ADMISSION_ACTUAL.json'","put('V2_TWO72_OWNER_METADATA_ORIGINAL_LOCK_HANDOFF_ADMISSION_ACTUAL.json'").replace("put('TWO72_CONTINUATION_H1_ACTUAL_STORAGE_REJECTION_CONTRACT.json'","put('V2_TWO72_CONTINUATION_H1_ACTUAL_STORAGE_REJECTION_CONTRACT.json'")
s=s.replace("R/'TWO72_CONTINUATION_H1_ACTUAL_STORAGE_REJECTION_CONTRACT.json'","R/'V2_TWO72_CONTINUATION_H1_ACTUAL_STORAGE_REJECTION_CONTRACT.json'")
s=s.replace("put('SOURCE_SMALL_OWNER_TWO_FILES_SHA_AST_ACTUAL.json'","put('V2_SOURCE_SMALL_OWNER_FILES_SHA_AST_ACTUAL.json'").replace("put('TWO72_ONE_ORIGINAL_OWNER_ACTUAL_DETACHED_DISPATCH.json'","put('V2_TWO72_ONE_ORIGINAL_OWNER_ACTUAL_DETACHED_DISPATCH.json'")
s=s.replace("put('H1_STORAGE_REJECTION_PREGO_TERMINAL_ACK_ACTUAL.json'","put('V2_H1_STORAGE_REJECTION_PREGO_TERMINAL_ACK_ACTUAL.json'").replace("put('TWO72_HEALTHY_NEW_NATIVE_FINITE_CHAINS_H1_STORAGE_REJECTED_DETACHED_ACTUAL.json'","put('V2_TWO72_HEALTHY_NEW_NATIVE_FINITE_CHAINS_H1_STORAGE_REJECTED_DETACHED_ACTUAL.json'")
ast.parse(s);p=G/'deploy_two72_new_namespace_actual_listener_ready_v2_once.py';assert not p.exists();p.write_text(s,encoding='utf8');v=dict(epoch=time.time(),passed_CPU_only=True,eight_negative_owner_publication_cases=neg,actual_listener_ready_before_signed_registration_new_scope=True,old_connection_refused_then_actual_empty_owner_snapshot_preserved=True,startup_race_diagnosis_is_code_and_later_snapshot_inference_not_unique_network_proof=True,old_owner_must_naturally_expire_and_actual_out_noGO_nolocks_before_newlaunch=True,unchanged_controller_and_GPU_workers=True,new_deployer=str(p),new_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),new_native_or_GPU_or_GO_not_yet=True)
with (R/'OWNER_POST_LISTENER_READY_STARTUP_REPAIR_CPU_V2_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
print(json.dumps(v))
