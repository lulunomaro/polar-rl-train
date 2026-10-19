"""Retain a zero-GO failure, keep healthy slots running, and prepare a safe next handoff."""
from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;W=B.parent;P=W/'MOD4_SCUT_FUDAN_TENTH_HOUR_20261019';R=B/'reports'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,v):
 with (R/name).open('x',encoding='utf8') as stream:json.dump(v,stream,ensure_ascii=False,indent=2)
t=json.loads((R/'THREE_REAL_LEARNING_TARGET72_NATIVE_OR_PRODUCTION_BOUND_METADATA_ACTUAL.json').read_bytes());o=json.loads((R/'THREE_REAL_LEARNING_ONE_ORIGINAL_OWNER_ACTUAL_CURRENT.json').read_bytes());d=json.loads((R/'THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json').read_bytes());h=t['experts']['h1'];row=h['rows']['NODE_TERMINAL_ACTUAL.json']['row'];go=o['rows']['OWNER_CURRENT.json']['go']
assert row['original_error'] and row['phase']=='admission' and row['worker'] is None and row['returncode']==1 and not h['own_processes'] and set(go)=={'e2','recovery'}
put('H1_SHARED_RESOURCE_OVERWRITTEN_BY_CONTROLLER_COPY_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),trial_id='eleventh-hour-H1-zero-GO-resource-inheritance-failure',original_H1_node_error=h['rows']['NODE_ORIGINAL_ERROR.json'],actual_H1_terminal=row,actual_owner_GO_keys=list(go),H1_no_GO_no_worker_no_production_charge=True,cause='The preparer first copied the previous H1 payload, then copied every controller file over it. The old controllers/three_real_gpu_resource_v1.py replaced the previous payload H1 sharing-aware file. The deploy INSTALL allowed sharing but node acquire used the overwritten exclusive check.',original_sources_and_false_first_metadata_retained=True,unrelated_local_lookup_error=dict(wrong_filename='THREE_NEXT_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json',actual_filename='THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json',original_Get_Content_missing_path_retained=True,not_a_remote_or_GPU_failure=True),safe_current_state='Original owner318576 continues independent E2/E3. It latched stop[h1]=True before H1 GO; no supported authenticated failed-slot replacement was prepared. Do not patch live owner, stop healthy workers, recover HMAC from memory, add a writer or bypass canonical locks. Prepare a separate corrected cohort after natural two-slot closure.',no_peer_interference_or_old_GPU_Task_replay=True))
F=B/'future_partial_hour_repair_templates';F.mkdir()
# Closing reads all original terminal metadata, but downloads only the two genuine finals.
s=(P/'collect_next_hour_missing_closed_finals_bounded_owner_wait_V2_once.py').read_text('utf8').replace('306868','318576')
s=s.replace('THREE_HOUR_MISSING_CLOSED_FINAL_COLLECTION_ACTUAL.json','PARTIAL_HOUR_MISSING_CLOSED_FINAL_COLLECTION_ACTUAL.json').replace('THREE_HOUR_FINAL_COLLECTOR_STARTED_ACTUAL.json','PARTIAL_HOUR_FINAL_COLLECTOR_STARTED_ACTUAL.json').replace('THREE_HOUR_FINAL_COLLECTION_ORIGINAL_ERROR_','PARTIAL_HOUR_FINAL_COLLECTION_ORIGINAL_ERROR_').replace("len(out['models'])==3","len(out['models'])==2")
needle=" put('PARTIAL_HOUR_MISSING_CLOSED_FINAL_COLLECTION_ACTUAL.json',out);print"
replacement=" assert set(out['owner']['rows']['COHORT_FINAL.json']['go'])=={'e2','recovery'};hr=out['experts']['h1']['rows']['NODE_TERMINAL_ACTUAL.json']['row'];assert hr['original_error'] and hr['phase']=='admission' and hr['returncode']==1 and hr['worker'] is None and not out['experts']['h1']['actual_own_processes'];out.update(actual_original_GO_experts=['e2','recovery'],H1_failed_preGO_zero_charge_not_a_new_final=True)\n put('PARTIAL_HOUR_MISSING_CLOSED_FINAL_COLLECTION_ACTUAL.json',out);print"
assert needle in s;s=s.replace(needle,replacement);ast.parse(s)
with (B/'collect_current_two_GO_finals_and_original_account_bounded_once.py').open('x',encoding='utf8',newline='\n') as stream:stream.write(s)
# Two actual new finals plus the explicitly retained healthy H1 source from hour10.
s=(P/'review_next_closed_hour_finals_whole_model_original_cost_CPU_once.py').read_text('utf8').replace('306868','318576')
s=s.replace('THREE_HOUR_MISSING_CLOSED_FINAL_COLLECTION_ACTUAL.json','PARTIAL_HOUR_MISSING_CLOSED_FINAL_COLLECTION_ACTUAL.json').replace("set(seg['experts'])=={'h1','e2','recovery'}","set(seg['experts'])=={'e2','recovery'}").replace("for key in ('h1','e2','recovery'):","for key in ('e2','recovery'):")
needle=" out=dict(epoch=time.time(),passed_all_three_whole_final_models_CPU=True,experts=results,"
replacement=" prior=json.loads((W/'MOD4_SCUT_FUDAN_TENTH_HOUR_20261019/reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());h=prior['experts']['h1'];hs=B/'payload/h1/job0/source'/d['specs']['h1']['source_filename'];assert H(hs)==h['final']['SHA']==d['specs']['h1']['source_SHA'];hv=torch.load(hs,map_location='cpu',weights_only=False);hc=[0,0];tensors(hv,hc);assert hc==h['whole_tensor_counts'] and {int(x['step']) for x in hv['optimizer_state_dict']['state'].values()}=={h['all17Adam_after']};assert 'h1' not in seg['experts'];results['h1']=dict(final=h['final'],whole_tensor_counts=hc,all_model_runtime_finite=True,updates=h['updates'],all17Adam_before=h['all17Adam_after'],all17Adam_after=h['all17Adam_after'],retained_previous_healthy_final_hour=10,current_hour_actual_GO=False,current_hour_production_updates=0,current_hour_charged_seconds=0.,previous_healthy_full_CPU_proof=str(W/'MOD4_SCUT_FUDAN_TENTH_HOUR_20261019/reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json'))\n out=dict(epoch=time.time(),passed_all_actual_GO_final_models_CPU=True,passed_next_three_sources_whole_model_CPU=True,actual_owned_new_final_experts=['e2','recovery'],H1_failed_admission_zero_GO_retains_hour10_source=True,experts=results,"
assert needle in s;s=s.replace(needle,replacement).replace('THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json','PARTIAL_HOUR_ACTUAL_GO_FINALS_AND_NEXT_SOURCES_CPU_ACTUAL.json')
# Undo only the prior proof paths; never invent an hour10 partial report.
s=s.replace('MOD4_SCUT_FUDAN_TENTH_HOUR_20261019/reports/PARTIAL_HOUR_ACTUAL_GO_FINALS_AND_NEXT_SOURCES_CPU_ACTUAL.json','MOD4_SCUT_FUDAN_TENTH_HOUR_20261019/reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json')
s=s.replace('THREE_HOUR_FINAL_CPU_ORIGINAL_ERROR_','PARTIAL_HOUR_FINAL_CPU_ORIGINAL_ERROR_').replace('all_three_closed_final_CPU=True','actual_two_GO_finals_and_retained_H1_source_CPU=True')
ast.parse(s)
with (B/'review_current_two_GO_finals_and_retained_H1_source_CPU_once.py').open('x',encoding='utf8',newline='\n') as stream:stream.write(s)
# Repaired H1 resource admission must also prove the failed admission root remains exited.
shared=(P/'payload/h1/three_real_gpu_resource_v1.py').read_text('utf8')
assert "spec.get('human_explicit_GPU_sharing') is True" in shared
needle=" assert not own,own;lock="
replacement=" failed=spec.get('previous_failed_preGO_runtime_root')\n if failed:\n  q=Path(failed);assert q.resolve().is_relative_to(owned.resolve());fe=json.loads((q/'NODE_EXIT_ACTUAL.json').read_bytes());fr=json.loads((q/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert fe['actual_all_own_children_waited'] and fe['validation_fcntl_released_if_acquired'] and fr['phase']=='admission' and fr['original_error'] and fr['worker'] is None and not (q/'job0/GO_PRODUCTION.json').exists() and not (q/'GO_PRODUCTION.json').exists() and not (q/'job0/production').exists()\n  for p in psutil.process_iter(['pid','cmdline']):\n   try:\n    if p.pid!=os.getpid() and any(x.startswith(str(q)+'/') for x in p.info['cmdline'] or []):own.append(p.info)\n   except psutil.Error:pass\n assert not own,own;lock="
assert needle in shared;shared=shared.replace(needle,replacement);ast.parse(shared)
(F/'three_real_gpu_resource_shared_user_v2.py').write_text(shared,'utf8')
s=(B/'prepare_next_three_closed_sources_one_hour_CPU_once.py').read_text('utf8')
s=s.replace("T=W/'MOD4_SCUT_FUDAN_TENTH_HOUR_20261019'","T=W/'MOD4_SCUT_FUDAN_ELEVENTH_HOUR_20261019'").replace('reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json','reports/PARTIAL_HOUR_ACTUAL_GO_FINALS_AND_NEXT_SOURCES_CPU_ACTUAL.json').replace("f['passed_all_three_whole_final_models_CPU']","f['passed_next_three_sources_whole_model_CPU']")
s=s.replace('T3sf11_1910v16','T3sf12_1910v17').replace('THREE_GPU_SCUT_FUDAN_HOUR16_','THREE_GPU_SCUT_FUDAN_HOUR17_')
needle="  m=dict(oldm,source_SHA="
replacement="  if key=='h1':\n   resource=B/'three_real_gpu_resource_shared_user_v2.py';shutil.copy2(resource,dest/'three_real_gpu_resource_v1.py');assert H(dest/'three_real_gpu_resource_v1.py')==H(resource) and old['specs']['h1'].get('human_explicit_GPU_sharing') is True\n  m=dict(oldm,source_SHA="
assert needle in s;s=s.replace(needle,replacement)
needle=";assert proofmod.validate(proof,spec,m)"
replacement="\n  if key=='h1':spec.update(previous_runtime_root='/home/lc01/Zonglin Li/zonglin2/tasks/T3sf10_1910v15/h1',previous_failed_preGO_runtime_root=old['roots']['h1'],human_explicit_GPU_sharing=True)\n  assert proofmod.validate(proof,spec,m)"
assert needle in s;s=s.replace(needle,replacement);ast.parse(s)
(F/'prepare_next_three_closed_sources_one_hour_CPU_once.py').write_text(s,'utf8')
s=(B/'deploy_three_next_closed_source_hours_once.py').read_text('utf8')
s=s.replace('T3sf11_1910v16','FUTURE_ROOT').replace('T3sf10_1910v15','T3sf11_1910v16').replace('FUTURE_ROOT','T3sf12_1910v17').replace('306868','318576')
s=s.replace("set(rows[0]['experts'])=={'h1','e2','recovery'}","set(rows[0]['experts'])=={'e2','recovery'}")
s=s.replace("locks=[]\nfor p in", "assert set(final['go'])=={'e2','recovery'} and final['rows']['h1']['phase']=='admission' and final['rows']['h1']['original_error'] and final['rows']['h1']['worker'] is None;locks=[]\nfor p in")
needle="p['passed'];put('THREE_NEXT_HOUR_DEPLOY_STARTED_ACTUAL.json'"
replacement="p['passed'];assert p['specs']['h1'].get('human_explicit_GPU_sharing') is True;assert (Path(p['payloads']['h1'])/'three_real_gpu_resource_v1.py').read_bytes()==(B/'three_real_gpu_resource_shared_user_v2.py').read_bytes();put('THREE_NEXT_HOUR_DEPLOY_STARTED_ACTUAL.json'"
assert needle in s;s=s.replace(needle,replacement);ast.parse(s)
(F/'deploy_three_next_closed_source_hours_once.py').write_text(s,'utf8')
for name in ('closed_production_continuation_CPU_v2.py','collect_next_three_actual_learning_metadata_finite_once.py'):(F/name).write_bytes((B/name).read_bytes())
for q in F.glob('*.py'):ast.parse(q.read_text('utf8'))
put('H1_PREGO_FAILURE_SAFE_REPAIR_AND_PARTIAL_CLOSING_PREPARED_CPU_ACTUAL.json',dict(epoch=time.time(),prepared_only=True,actual_original_owner=318576,healthy_current_GO_experts=['e2','recovery'],failed_H1_actual_GO=False,H1_current_production_charge=0.,future_root_only_reserved='T3sf12_1910v17',future_templates=str(F),repair='Override H1 resource helper after the controller-copy loop, verify its exact sharing-aware bytes before manifest creation and again before deployment; add fresh previous failed-admission exit/noGO/no-production proof.',H1_next_source_is_retained_healthy_hour10_not_a_new_hour11_final=True,no_live_owner_or_healthy_worker_patch_stop_or_new_writer=True,no_HMAC_readback_or_secret_recovery=True,original_canonical_accounting_and_two_locks_unchanged=True))
print(json.dumps(dict(partial_closing_bound318576=True,repair_prepared_not_deployed=True,keep_current_E2_E3_healthy=True)))
