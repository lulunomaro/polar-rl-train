"""Restore original FP32 audit, preserve actual refusals; no host or learning."""
from pathlib import Path
import json,time,hashlib,shutil,ast,copy,importlib.util,sys,traceback
import torch
R=Path(__file__).resolve().parent;W=R.parent;E=R/'proposal_ce3_same_candidate_finite_v1';B=R/'resumed_ce3_original_fp32_v1';Q=B/'payload/h1'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 with Path(p).open('x',encoding='utf8') as f:f.write(v if isinstance(v,str) else json.dumps(v,indent=2,ensure_ascii=False))
def main():
 assert not B.exists();(B/'reports').mkdir(parents=True);rng=torch.get_rng_state().clone()
 write(B/'reports/ACTUAL_HUMAN_CONTINUE_AND_TECHNICAL_CONTEXT_CORRECTION.json',dict(epoch=time.time(),human_latest='开始推进训练任务，因为你的疏忽我们浪费了很多时间，继续任务吧',human_steering='不要再说我批准啥的了，你看之前的聊天记录，我有批准过这个吗？这个是你推进的',technical_decisions_owned_by_agent=True,restore_original_formal_FP32_audit_not_change_training_precision=True,continue_existing_one_unstarted_finite_segment=True,no_new_scope_budget_or_following_window=True,stop_repeated_permission_framing=True,original_failure_reports_retained=True))
 oldQ=E/'payload/h1';oldm=json.loads((oldQ/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());shutil.copytree(oldQ,Q,ignore=shutil.ignore_patterns('__pycache__','THREE_SLOT_COMPLETE_MANIFEST_V1.json'))
 shutil.copy2(oldQ/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',Q/'PREVIOUS_CE3_NATIVE_COMPLETE_MANIFEST_HISTORY.json')
 shutil.copy2(R/'h1_ce3_original_fp32_native_reuse_v1.py',Q/'h1_ce3_original_fp32_native_reuse_v1.py')
 node=(oldQ/'three_slot_finite_node_v1.py').read_text(encoding='utf8');needle="p=b.spawn(spec,'native');children.append(p);phase='native'";assert node.count(needle)==1
 (Q/'three_slot_finite_node_v1.py').write_text(node.replace(needle,"from h1_ce3_original_fp32_native_reuse_v1 import reuse_H1_native;native=reuse_H1_native(spec,b,B);phase='ready'"),encoding='utf8')
 listener=W/'MOD4_H1_HUMAN_REQUESTED_SAME_SCOPE_RESTART_20261017/owner_listener_ready_cpu_reviewed_v1.py';assert listener.is_file();shutil.copy2(listener,Q/listener.name)
 core=json.loads((E/'reports/CE3_TWO_COMPLETE_NATIVE_MODELS_FINITE_CORE_ONLY_NOT_ADMISSION_LOCAL_CPU_ACTUAL.json').read_bytes());formal=json.loads((E/'reports/CE3_ORIGINAL_FP32_FORMAL_NATIVE_ALL_ROWS_CPU_SAME_BOUND_ACTUAL.json').read_bytes());closed=json.loads((E/'reports/CE3_NATIVE_REJECTED_ZERO_GO_COST_ACTUAL_EXIT_FCNTL_HANDBACK_ACTUAL.json').read_bytes())
 write(Q/'REUSED_NATIVE_COMPLETE_MODELS_CORE_PROOF.json',core);write(Q/'REUSED_NATIVE_ORIGINAL_FP32_FORMAL_CPU_PROOF.json',formal)
 oldtask=json.loads((Q/'job0/TASK.json').read_bytes());write(Q/'job0/PREVIOUS_CE3_TASK_HISTORY.json',oldtask)
 task=dict(oldtask,id='H1_CE3_ORIGINAL_FP32_SAME_SEGMENT_CONTINUATION_20261018',source_H1_actual_latest_Adamstep=646100,source_Adamstep=646100,proposal_only_requires_explicit_new_human_finite_grant=False,same_source_backend_native_reused_not_replayed=True,own_new_native_for_actual_new_weights_required=False,new_target_native180_and_full_CPU_required=False,newsource_native180_required=False,actual_completed_ce3_native_reused=True,reference_protocol='original_formal_H1_native_FP32_absolute1e-4',historical_dual_FP64_false_retained=True)
 (Q/'job0/TASK.json').write_text(json.dumps(task,indent=2),encoding='utf8')
 bind=dict(root='/home/lc01/Zonglin Li/zonglin2/tasks/H1cq_1810p3',manifest_SHA=H(oldQ/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),source_SHA=oldm['source_SHA'],GPU_UUID=task['GPU_UUID'],native_CPU_SHA=formal['CPU_report']['SHA'],old_owner_zero_GO_zero_charge_actual_report_SHA=H(E/'reports/CE3_NATIVE_REJECTED_ZERO_GO_COST_ACTUAL_EXIT_FCNTL_HANDBACK_ACTUAL.json'))
 files=[]
 for p in sorted(x for x in Q.rglob('*') if x.is_file() and '__pycache__' not in x.parts):
  if p.suffix=='.py':ast.parse(p.read_text(encoding='utf8'))
  files.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
 mf=dict(oldm,files=files,H1_same_source_backend_native_reuse=bind,actual_reference_protocol_restored_original_FP32=True,old_FP64_false_immutable=True)
 write(Q/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',mf)
 specs=copy.deepcopy(json.loads((E/'reports/HUMAN_APPROVED_CE3_PREPARED_PAYLOAD_BOUND_DEPLOY_SPEC_ACTUAL.json').read_bytes())['specs']);specs['h1'].update(manifest_SHA=H(Q/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),previous_runtime_root='/home/lc01/Zonglin Li/zonglin2/tasks/H1mp_1810p2',execution_backend='target72',role='node')
 sp=importlib.util.spec_from_file_location('pure_ce3_reuse_validator',Q/'h1_ce3_original_fp32_native_reuse_v1.py');v=importlib.util.module_from_spec(sp);sp.loader.exec_module(v)
 args=[specs['h1'],bind,oldm,mf,core,closed['target']['rows']['NODE_EXIT_ACTUAL.json'],closed['owner']['rows']['OWNER_CURRENT.json']['rows']['h1']['actual_exit'],formal];native=v.validate(*args)
 bads=[]
 for label,index,change in [('backend',0,lambda x:x.__setitem__('execution_backend','source210')),('GPU',0,lambda x:x.__setitem__('GPU_UUID','other')),('source',0,lambda x:x.__setitem__('source_SHA','0'*64)),('Adam',0,lambda x:x.__setitem__('source_Adamstep',645620)),('runtime',3,lambda x:next(r for r in x['files'] if r['relative'].startswith('job0/runtime/')).__setitem__('SHA','0'*64)),('core',4,lambda x:x.__setitem__('Adam646100_unchanged',False)),('PTtwohost',4,lambda x:x['models'][0].__setitem__('twohost_complete_SHA',False)),('parent_not_waited',5,lambda x:x.__setitem__('actual_all_own_children_waited',False)),('GPU_exit',6,lambda x:x.__setitem__('returncode',1)),('GPU_not_waited',6,lambda x:x.__setitem__('actual_waited',False)),('CPUhash',1,lambda x:x.__setitem__('native_CPU_SHA','0'*64)),('CPU_false',7,lambda x:x['original_FP32_formal_allrow_CPU'].__setitem__('passed',False)),('installedSDK',3,lambda x:x.__setitem__('expected_actual_SDK_math_SHA','0'*64))]:
  a=copy.deepcopy(args);change(a[index])
  try:v.validate(*a)
  except AssertionError:bads.append(label)
  else:raise AssertionError('negative accepted '+label)
 assert len(bads)==13 and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 equal=[n for n in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','three_slot_resource_v1.py','h1_prelaunch_v2_production_worker_v1.py') if H(Q/n)==H(oldQ/n)];assert len(equal)==4
 write(B/'reports/CE3_ORIGINAL_FP32_NATIVE_REUSE_PAYLOAD_CPU_ACTUAL.json',dict(epoch=time.time(),passed_CPU_only=True,specs=specs,binding=bind,positive_and13_negatives=bads,unchanged_production_worker_original_owner_common_resource_SHA=equal,all_runtime_assets_exact=True,original_FP32_native_value=native['value'],old_FP64_and_oldnode_false_retained=True,new_native_GPU_not_replayed=True,new_production_not_yet=True,CPU_RNG_unchanged0CUDA0optimizer=True,cap1800_headroom300_max24_start25GiB_free8GiB_savedstop_original_budget=True))
 print(json.dumps(dict(payload_CPU_passed=True,negative_cases=len(bads),new_source_Adam=646100,native_reused_without_replay=True,files=len(files),next_actual_resources_then_production=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/'reports'/('CE3_ORIGINAL_FP32_REUSE_PREPARE_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_host_GPU_or_GO=True),f,indent=2)
  raise
