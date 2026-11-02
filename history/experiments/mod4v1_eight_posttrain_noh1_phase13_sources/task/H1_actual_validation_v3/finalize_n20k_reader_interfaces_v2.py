"""Unconsumed N20k interface/reader correction only. No PT/SDK/remote calls."""
from pathlib import Path
import ast
B=Path(__file__).resolve().parent
s=(B/'prepare_n20k_case_dispatch_v1.py').read_text(encoding='utf-8')
# Gate on actual complete/wait/release reconciliation, not old malformed FINAL=true.
a="assert final['passed'] is True and closed['all_own_children_waited'] and closed['original_private_lock_released'] and closed['original_shared_lock_released'],'Actual fresh80 PASS + original release required before N20k'"
z="reconciled=json.loads((S/'H1_FRESH80_ACTUAL_READER_RECONCILIATION_V1.json').read_bytes());actual=json.loads((S/'gpu1/H1_FRESH80_COMPLETE.json').read_bytes());assert final['passed'] is False and reconciled['original_parent_false_preserved'] and reconciled['passed_actual_fresh_worker_and_clean_release'] and actual['passed'] is True and closed['all_own_children_waited'] and closed['original_private_lock_released'] and closed['original_shared_lock_released'],'Actual workerPASS+RC0+cleanrelease reconciliation required; originalreaderfalse not relabelled'"
assert s.count(a)==1;s=s.replace(a,z,1)
s=s.replace("supervisor=B/'supervise_h1_71db_noupdate_v1.py'","supervisor=B/'supervise_h1_71db_noupdate_v2.py'",1)
anchor=" s=s.replace('E3_1CD_N20K_NATIVE34_NOUPDATE_FINISHED','H1_71DB_N20K_NATIVE24_NOUPDATE_FINISHED')"
addition='''
 expected_names=['GPU_OWN_WORKER_IDENTITY.json','H1_CORE_AND_DR_BEFORE.json','MOD4V1_NORMAL_H1_FULLRESTORE_BEFORE_MEAN_ACTION.json','H1_CORE_AND_DR_AFTER.json','MOD4V1_NORMAL_H1_NATIVE24_192PHYSICS_48FEEDBACK_NOUPDATE.json','SOURCE_FINAL_READ_COUNTS.json','ENV_CLOSE_RETURNED.json','APP_CLOSING.json','NORMAL_H1_NATIVE24_ORIGINAL_EXCEPTION_BEFORE_APP_CLOSE.json']
 old="        data=json.loads((d/'control_out/MOD4V1_NORMAL_H1_NATIVE24_192PHYSICS_48FEEDBACK_NOUPDATE.json').read_bytes())"
 new="        diagnostics={}\\n        for name in "+repr(expected_names)+":\\n            path=d/'control_out'/name\\n            if path.exists():diagnostics[name]=json.loads(path.read_bytes())\\n        put('H1_ACTUAL_CHILD_OUTPUTS_COLLECTED.json',diagnostics)\\n"+old
 assert s.count(old)==1;s=s.replace(old,new,1)
 s=s.replace("passed=passed)","passed=passed,child_output_diagnostics=diagnostics)",1)
 # Interface table generated BEFORE SSH/stage/dispatch. Filename matching only, no newphysicsgate.
 worker_tree=ast.parse((B/'evaluate_h1_71db_native24_noupdate_v1.py').read_text(encoding='utf-8'))
 actual_put={n.args[0].value for n in ast.walk(worker_tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='put' and n.args and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str)}
 assert set(expected_names)<=actual_put
 table=[]
 for name in expected_names:
  table.append(dict(worker_actual_put=name,parent_expected_read='control_out/'+name,collector_expected_read='gpu1/control_out/'+name,basename_equal=True,required_absent_if_success=name.startswith('NORMAL_H1_NATIVE24_ORIGINAL_EXCEPTION')))
 proof=dict(kind='H1_N20K_OUTPUT_BASENAME_STATIC_INTERFACE_REVIEW',all_basenames_equal=True,table=table,parent_read_exact_names=expected_names,worker_actual_const_puts=sorted(actual_put),no_global_E2_E3_role_replace=True,no_PT_or_SDK_operation=True)
 with (B/'H1_N20K_OUTPUT_BASENAME_INTERFACE_V1.json').open('x',encoding='utf-8') as f:json.dump(proof,f,indent=2)
'''
assert s.count(anchor)==1;s=s.replace(anchor,anchor+addition,1)
ast.parse(s)
with (B/'prepare_n20k_case_dispatch_v2.py').open('x',encoding='utf-8') as f:f.write(s)
# Collector explicitly gets the same nine named main outputs (in addition to originalhelper JSONs).
c=(B/'collect_h1_case_v1.py').read_text(encoding='utf-8')
a=" walk('gpu1')"
z=""" if a.mode=='n20k':
  interface=json.loads((B/'H1_N20K_OUTPUT_BASENAME_INTERFACE_V1.json').read_text(encoding='utf-8'))
  for row in interface['table']:get(row['collector_expected_read'])
 walk('gpu1')"""
assert c.count(a)==1;c=c.replace(a,z,1);ast.parse(c)
with (B/'collect_h1_case_v2.py').open('x',encoding='utf-8') as f:f.write(c)
print('N20k unconsumed supervisor/collector exactfilename interface generation prepared; original workerfor24 unchanged.')
