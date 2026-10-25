"""Finish unused69 source/config; payload/model/GO still require closed68."""
from pathlib import Path
import ast,hashlib,json,shutil,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;R=S/'reports'
P=T/'H1_STEP270_REWARD_SAGITTAL_TUCK_V6A_RESOURCE_V68_20261025'
N=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V1_RESOURCE_V69_20261025'
V=S/'your_agent/implementation_v1/revision_v2';A=S/'root_admission_review_agent'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,value):
 with p.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def replace_one(text,before,after):
 assert text.count(before)==1,(before,text.count(before));return text.replace(before,after)
try:
 v1=json.loads((S/'your_agent/implementation_v1/reports/INTEGRATED_H1_E3_REAL_BANK_CPU_V1_ACTUAL.json').read_bytes());assert v1['status']=='CPU_source_and_real_bank_checks_passed_not_installed_SDK_validation'
 v2=json.loads((V/'reports/V2_CONTEXT_AST_SYNTHETIC_CPU_READERFIX3_ACTUAL.json').read_bytes());assert v2['status']=='V2_context_AST_and_synthetic_inference_checks_passed'
 review=json.loads((A/'SOURCE_PATCH_REVIEW_ACTUAL.json').read_bytes());assert review['target_AST_exact_except_two_inserted_nodes_each'] and review['recovery_guard_reads_saved_CPU_receipt_never_reruns_bank_checker']
 checker=V/'verification/sampling_acceleration_installed_CPU_v2.py';assert H(checker)=='256f803270d8ec6702e0d120670d57bf79c9145c169a71bc4742dad7ac0dcf15'
 auth=json.loads((A/'SAMPLING_OPTIMIZATION_HUMAN_AUTH_AND_CPU_SCHEMA_TEMPLATE.json').read_bytes())
 auth.update(status='HUMAN_AUTHORIZED_IMPLEMENTATION_SOURCE_CPU_PREPARED_NOT_INSTALLED',approved=True,human_authorization_source='Human: 开始提速方案实施; current round continues, then temporary subagent ban',epoch=time.time(),source_only_no_GO=True,original_reward_retention_physics_PPO_guards_retained=True,actual_local_CPU_evidence=dict(real_bank=v1['trial_id'],context=v2['trial_id']),installed_new_payload_checks_pending=True)
 stage=N/'sampling_repair_sources';assert not stage.exists();shutil.copytree(V/'payloads',stage/'payloads');shutil.copytree(A/'copies_69_ready',stage/'admission')
 shutil.copy2(checker,stage/checker.name)
 put(stage/'SAMPLING_OPTIMIZATION_HUMAN_AUTH_AND_CPU_ACTUAL.json',auth)
 for row in review['source_files']:
  assert H(P/'payloads'/row['relative'])==row['original_SHA'] and H(stage/'admission'/row['relative'])==row['candidate_SHA']
 for key,slot in auth['slots'].items():
  for relative,digest in slot['candidate_SHA'].items():assert H(stage/'payloads'/key/relative)==digest
 # Preserve all actual68 source guards/targets/auth as immutable references.
 for key in ('h1','recovery'):
  ref=stage/'original_admission_sources'/key;ref.mkdir(parents=True)
  for name in (('closed_production_continuation_CPU_v2.py','target_H1_step270_closed_source_sdk_cpu_review_v1.py') if key=='h1' else ('original_account_policy50_source_CPU.py','target_two50_source_sdk_cpu_review.py')):shutil.copy2(P/'payloads'/key/name,ref/name)
 # Derive new preparer from actual68 recipe. No execution of preparer now.
 text=(P/'prepare_next_latest_sources_after_actual_H1_closed_resource_CPU_once.py').read_text('utf8')
 text=text.replace('H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025','H1_STEP270_REWARD_SAGITTAL_TUCK_V6A_RESOURCE_V68_20261025')
 old="closing=read(T/'MOD4_MIXED_PRECISION_MISSING_HALF_RSL_V4_AFTER67_20261025/reports/BENCHMARK_TEXT_CANONICAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json');assert closing['owner_node_workers_all_actual_out'] and closing['original_canonical_cost_settled']"
 text=replace_one(text,old,"closing=read(P/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');assert closing['passed'] and closing['all_owner_nodes_children_actual_out'] and closing['original_canonical_cost_settled']")
 text=text.replace("closing['original_remaining_closed_snapshot']","closing['remaining_actual_snapshot']").replace('latest_M4_benchmark_original_cost_closure=closing','latest68_original_cost_closure=closing')
 text=text.replace('H1step270_reward_sagtuck6a_2510v68','H1step270_sampling_opt1_sagtuck6a_2510v69')
 text=replace_one(text,"previous_owner_root=read(T/'MOD4_MIXED_PRECISION_MISSING_HALF_RSL_V4_AFTER67_20261025/reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')['owner_root']","previous_owner_root=read(P/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')['owner_root']")
 needle="  task=read(dest/'job0/TASK.json')"
 extra="""  acceleration=N/'sampling_repair_sources'
  for p in (acceleration/'payloads'/key).rglob('*'):
   if p.is_file():
    target=dest/p.relative_to(acceleration/'payloads'/key);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
  for p in (acceleration/'admission'/key).glob('*.py'):shutil.copy2(p,dest/p.name)
  for name in ('sampling_acceleration_installed_CPU_v2.py','SAMPLING_OPTIMIZATION_HUMAN_AUTH_AND_CPU_ACTUAL.json'):shutil.copy2(acceleration/name,dest/name)
  shutil.copytree(acceleration/'original_admission_sources'/key,dest/'sampling_original_admission_sources',dirs_exist_ok=True)
"""
 text=replace_one(text,needle,extra+needle)
 ast.parse(text)
 with (N/'prepare_next_latest_sources_after_actual_H1_closed_resource_CPU_once.py').open('x',encoding='utf8') as f:f.write(text)
 # Source68 proof closes both actual costs; resource-only reader stays fresh.
 text=(P/'read_E3_resource_only_after_actual_H1_closed_CPU_once.py').read_text('utf8')
 text=text.replace('H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025','H1_STEP270_REWARD_SAGITTAL_TUCK_V6A_RESOURCE_V68_20261025')
 old=" closure=json.loads((N.parent/'MOD4_MIXED_PRECISION_MISSING_HALF_RSL_V4_AFTER67_20261025/reports/BENCHMARK_TEXT_CANONICAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes());assert closure['owner_node_workers_all_actual_out'] and closure['original_canonical_cost_settled']"
 text=replace_one(text,old," assert proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled']")
 ast.parse(text)
 with (N/'read_E3_resource_only_after_actual_H1_closed_CPU_once.py').open('x',encoding='utf8') as f:f.write(text)
 rows=[]
 for p in sorted(stage.rglob('*')):
  if p.is_file() and '__pycache__' not in p.parts:
   if p.suffix=='.py':ast.parse(p.read_text('utf8'))
   rows.append(dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)))
 assert not (N/'payloads').exists() and not (N/'controllers').exists()
 result=dict(epoch=time.time(),passed=True,no_live68_source_change=True,future69_source_only=str(N),qualified_future_source='Only actual closed68 complete FINALs after whole CPU and original independent costs/allout, never benchmark or older67',scope='H1 lossless trace deflate1/field streaming/full SHA + E3 immutable fixed recipe reset cache; V6A reward and physical learning unchanged',source_files=rows,new_payload_installed_CPU_pending=True,no_future69_payload_Task_GO_fee=True,normal_current68_save_request_now_source_ready=True,original_guard_values_unchanged=True,after_this_round_subagents_temporarily_prohibited=True)
 put(R/'OPTIMIZED_NEXT69_IMPLEMENTATION_SOURCE_CPU_READY_ACTUAL.json',result)
 put(N/'reports/OPTIMIZED_NEXT69_IMPLEMENTATION_SOURCE_CPU_READY_ACTUAL.json',result)
 print(json.dumps({k:v for k,v in result.items() if k!='source_files'}))
except BaseException:
 put(R/('NEXT69_INTEGRATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_remote_mutation=True));raise
