"""New original-eval purpose ONLY after actual first attempt expired without any child/model."""
from pathlib import Path
import ast,json,time
D=Path(__file__).resolve().parent
closed=D/'FDNLOWSTD005_FROZEN_CLOSED_RESULT.json';v=json.loads(closed.read_bytes());m=v['metadata'];e=m['PARENT_EXIT_SCOPE.json'];o=m['FDNLOWSTD005_FROZEN_PARENT_WAITED_ACTUAL.json']
assert v['closed']is True and e['all_own_children_waited']is True and e['child_waits']==[]and e['original_single_GPU_private_EX_released']is e['original_global_finite_EX_released']is True and e['SDK_PT_opens_by_parent']==e['canonical_writes']==0 and e['no_foreign_scope_touched']is True
assert o['actual_parent_p_wait_returned']is o['original_parent_reaped']is True and o['returncode']==0 and o['errors']==[]and o['parent']['pid']==1636788 and o['controller']['pid']==1636781
assert all(m[k]is None for k in('CHILDREN.json','ACTUAL_GROUP_ADMISSION.json','GROUP_EVAL_START.json','FINAL.json','TERMINAL_ROWS.json'))and all(x is None for k,x in m.items()if k.startswith('cases/'))and 'Originalresourcewait1800sexpiredwithoutSDK/model/foreignactions'in json.dumps(e['errors'])
names=('stage_fudan_lowstd005_eval_admission2_once.py','dispatch_fudan_lowstd005_eval_admission2_once.py','collect_fudan_lowstd005_eval_admission2_once.py','publish_fudan_lowstd005_admission2_eval2_closed_quality_once.py');assert all(not(D/n).exists()for n in names)
def ns(s):return s.replace('FDNLOWSTD005_FROZEN_','FDNLOWSTD005_FROZEN_ADMISSION2_').replace('fdn_lowstd005_frozen_outer_wait.py','fdn_lowstd005_eval2_frozen_outer_wait.py')
s=ns((D/'stage_fudan_lowstd005_frozen_original_once.py').read_text(encoding='utf8'));needle='    closed_path = Path(args.closed)';assert s.count(needle)==1
guard='''    prior=json.loads((D/"FDNLOWSTD005_FROZEN_CLOSED_RESULT.json").read_bytes());pm=prior["metadata"];pe=pm["PARENT_EXIT_SCOPE.json"];po=pm["FDNLOWSTD005_FROZEN_PARENT_WAITED_ACTUAL.json"]
    need(prior["closed"] is True and pe["all_own_children_waited"] is True and pe["child_waits"]==[] and
         pe["original_single_GPU_private_EX_released"] is pe["original_global_finite_EX_released"] is True and
         pe["SDK_PT_opens_by_parent"]==pe["canonical_writes"]==0 and po["actual_parent_p_wait_returned"] is
         po["original_parent_reaped"] is True and po["returncode"]==0 and po["errors"]==[] and
         po["parent"]["pid"]==1636788 and po["controller"]["pid"]==1636781,
         "Actual first original-eval wait/reap/release without any model required")
    need(all(pm[k] is None for k in ("CHILDREN.json","ACTUAL_GROUP_ADMISSION.json","GROUP_EVAL_START.json","FINAL.json","TERMINAL_ROWS.json")) and
         all(x is None for k,x in pm.items() if k.startswith("cases/")) and
         "Originalresourcewait1800sexpiredwithoutSDK/model/foreignactions" in json.dumps(pe["errors"]),
         "Original eval1 actual unstarted resource expiry only; never rerun physical execution")
'''
s=s.replace(needle,guard+needle);files={D/names[0]:s}
for old,new in(('dispatch_fudan_lowstd005_frozen_original_once.py',names[1]),('collect_fudan_lowstd005_frozen_original_once.py',names[2])):files[D/new]=ns((D/old).read_text(encoding='utf8'))
s=(D/'publish_fudan_lowstd005_admission2_closed_quality_once.py').read_text(encoding='utf8');needle="original=D/'FDNLOWSTD005_FROZEN_ORIGINAL_SCOPE_RESULT.json'";assert s.count(needle)==1;s=s.replace(needle,"original=D/'FDNLOWSTD005_FROZEN_ADMISSION2_ORIGINAL_SCOPE_RESULT.json'")
needle="outputs[0].write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf8')";assert s.count(needle)==1;s=s.replace(needle,"result['prior_unstarted_original_eval1']=json.loads((D/'FDN_LOWSTD005_N80_EVAL1_RESOURCE_WAIT_CLOSED_TRUTH.json').read_bytes())\n"+needle)
s=s.replace('原N80 V6_LOWSTD005真实父及collector全qualified','原N80 EvalAdmission2/V6_LOWSTD005真实父及collector全qualified');files[D/names[3]]=s
for path,s in files.items():ast.parse(s);compile(s,str(path),'exec')
for path,s in files.items():path.write_text(s,encoding='utf8',newline='\n')
truth=D/'FDN_LOWSTD005_N80_EVAL1_RESOURCE_WAIT_CLOSED_TRUTH.json';assert not truth.exists();truth.write_text(json.dumps(dict(kind='ORIGINAL_E3_N80_RESOURCE_EXPIRY_BEFORE_ANY_CHILD_OR_MODEL_NOT_SKILL_FAILURE',epoch=time.time(),closed_source=str(closed),root=v['root'],original_parent_pid=1636788,outer_controller_pid=1636781,parent_exit=e,outer_actual_wait=o,actual_child_count=0,actual_SDK_model_control_count=0,original_recovery_credit=None,original_request_denominator=None,normal_physical_termination=None,execution_qualified=False,original_first_failed_scope_report_preserved=True,no_samepurpose_replay=True,new_eval_purpose_prepared_source_only=True,source_modules_resource_gates_scope_and_acceptance_unchanged=True,model_raw_SDK_GPU_C_operations=0),indent=2),encoding='utf8')
print('Prepared new original N80 admission2 stage/dispatch/collector/actual publisher; previous real unstarted expiry preserved; same ten sources/resource gates/physics/scope; one source AST; no model/SSH/SDK/GO/C')
