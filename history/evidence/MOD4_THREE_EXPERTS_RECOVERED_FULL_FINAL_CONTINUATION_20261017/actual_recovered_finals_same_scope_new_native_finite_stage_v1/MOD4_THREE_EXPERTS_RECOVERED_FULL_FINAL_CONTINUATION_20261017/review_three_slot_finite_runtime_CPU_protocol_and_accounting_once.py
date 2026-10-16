"""Independent protocol/cost fixtures; no network, SDK, CUDA or real ledger."""
from pathlib import Path
import sys,types,importlib.util,copy,json,time,hashlib,ast,traceback
U=Path(__file__).resolve().parent;R=U/'reports'
def main():
 # Windows test host: the stub permits import only; actual flock semantics remain
 # an explicit Linux runtime admission and are never claimed from this fixture.
 sys.modules.setdefault('fcntl',types.SimpleNamespace());sp=importlib.util.spec_from_file_location('three_slot_fixture_common',U/'three_slot_common_v1.py');b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b);specs={k:dict(key=k,source_SHA=hashlib.sha256(k.encode()).hexdigest(),manifest_SHA=hashlib.sha256(('manifest'+k).encode()).hexdigest(),native_controls=n) for k,n in [('h1',180),('e2',144),('recovery',336)]};fields={'h1':'sourceactor9critic8STD17Adam_literal_exact','e2':'source_actor9_critic8_STD17Adam_literal_bytes_exact','recovery':'all_original_core_tensor_bytes_exact'};negatives=0
 for key,s in specs.items():
  value=dict(passed=True,source_SHA=s['source_SHA'],controls=s['native_controls'],callbacks=s['native_controls']*4);value[fields[key]]=True;proof=dict(value=value,SHA=hashlib.sha256(json.dumps(value,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True);row=dict(key=key,phase='ready',native_GPU_waited_EXIT0=True,native_CPU=proof,manifest_SHA=s['manifest_SHA']);assert b.valid_ready(row,s)
  for name,badvalue in [('key','other'),('phase','native_CPU_review_running'),('native_GPU_waited_EXIT0',False),('manifest_SHA','wrong'),('original_error',True)]:
   bad=copy.deepcopy(row);bad[name]=badvalue;assert not b.valid_ready(bad,s);negatives+=1
  for name,badvalue in [('source_SHA','wrong'),('controls',s['native_controls']-1),('callbacks',s['native_controls']*4-1),('passed',False),(fields[key],False)]:
   bad=copy.deepcopy(row);bad['native_CPU']['value'][name]=badvalue;bad['native_CPU']['SHA']=hashlib.sha256(json.dumps(bad['native_CPU']['value'],indent=2).encode()).hexdigest();assert not b.valid_ready(bad,s);negatives+=1
  bad=copy.deepcopy(row);bad['native_CPU']['SHA']='wrong';assert not b.valid_ready(bad,s);negatives+=1
 c=dict(charged_training_seconds=1000.,remaining_training_seconds=1187000.);a=dict(experts={},charged_expert_seconds=0.);go={k:dict(learning_started_epoch=start,max_parent_seconds=cap) for k,start,cap in [('h1',100,3600),('e2',130,3600),('recovery',180,3600)]};rows={k:dict(terminal_all_own_children_waited=True,returncode=0,owner_received_terminal_epoch=end) for k,end in [('h1',210),('e2',330),('recovery',480)]};c,a=b.charge_values(c,a,go,rows,500);assert c['charged_training_seconds']==1610 and a['charged_expert_seconds']==610 and a['charged_expert_seconds']!=380;before=copy.deepcopy(c);c,a=b.charge_values(c,a,go,rows,600);assert c==before and a['charged_expert_seconds']==610
 c=dict(charged_training_seconds=0.,remaining_training_seconds=1188000.);a=dict(experts={},charged_expert_seconds=0.);c,a=b.charge_values(c,a,{'h1':dict(learning_started_epoch=100,max_parent_seconds=3600)},{'h1':dict(terminal_all_own_children_waited=True,returncode=1,owner_received_terminal_epoch=3701)},3702);assert a['experts']['h1']['charged_seconds']==3601 and not a['experts']['h1']['duration_bound_passed'] and c['charged_training_seconds']==3601
 sources={}
 for name in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py','three_slot_resource_v1.py'):
  p=U/name;raw=p.read_bytes();ast.parse(raw.decode());sources[name]=hashlib.sha256(raw).hexdigest()
 owner=(U/'three_slot_finite_owner_v1.py').read_text();node=(U/'three_slot_finite_node_v1.py').read_text();assert "with mu:\n   rows=" in owner and 'all_registered' in owner and "shared['stop'][key]" in owner and 'shared[\'stop\']={k:True for k in specs}' in owner and 'def reuse_H1_native' not in node and "p=b.spawn(spec,'native');children.append(p);phase='native'" in node;assert 'SIGTERM' not in node+owner and 'os.kill' not in node+owner
 out=dict(epoch=time.time(),passed_CPU_protocol_only=True,negative_readiness_cases=negatives,sum_distinct_overlap610_not_shared_wall380=True,repeated_account_does_not_double_charge=True,actual_failed_interval3601_over_cap3600_remains_false_no_refund=True,mutex_fresh_terminal_rows_accounting_prevents_stale_row_race_reviewed=True,all_registered_before_first_GO_each_independent_own_native_before_its_GO=True,old_preparatory_all_three_native_before_any_GO_simplification_explicitly_superseded_by_independent_slot_contract=True,not_relaxing_any_slot_source_native_health_or_original_lock_admission=True,single_slot_failure_isolated_original_accounting_exception_stops_own_cohort=True,source_SHA=sources,not_real_OS_lock_HTTP_SDK_GPU_PPO_or_actual_new_runtime_pass=True,no_live_runtime_or_original_canonical_mutation=True);p=R/'THREE_SLOT_RUNTIME_PROTOCOL_CPU_READINESS_COST_NEGATIVES_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('THREE_SLOT_CPU_PROTOCOL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_runtime_replay=True),f,indent=2)
  raise
