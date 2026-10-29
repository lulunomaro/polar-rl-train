"""Finalize actual first-only snapshot and exact publication alias; no new SSH/model read."""
from pathlib import Path
import json,hashlib,time,datetime
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports'
C=L/'TWO114_WM_HEADING_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V1';Q=L/'TWO114_WM_HEADING_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
source=Q/'reports/TWO114_ALL_FIRST_POLICY_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json';raw=source.read_bytes();first=json.loads(raw)
assert first['actual_finite_returned'] and set(first['go'])==set(first['results'])=={'h1','h1_seed28'}
assert all(x['passed_first_NEW_native_policy'] for x in first['results'].values())
# Original frozen collector expects the main resource reports directory.
alias=R/source.name;assert not alias.exists()
with alias.open('xb') as f:f.write(raw)
assert alias.read_bytes()==raw
put(R/'ACTUAL114_FIRST_REPORT_BYTE_EXACT_RESOURCE_ALIAS_FOR_FROZEN_COLLECTOR.json',dict(epoch=time.time(),original_publication=str(source),expected_collector_alias=str(alias),bytes=len(raw),SHA=H(source),exact_original_bytes_preserved=True,no_reader_reexecution_source_hotpatch_model_or_host_read=True,scope='Report location alias only. Original Q publication remains unchanged; frozen collector FIRST directory resolves to resource reports.'))
actual=read(C/'reports/TWO114_ACTUAL_OWNER_AND_TWO_NODES_DETACHED.json');public=read(C/'reports/TWO114_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json')
roles={}
for key,v in first['results'].items():
 p=v['positive'];w=p['native88_migration_window'];cue=p['producer']['world_model_input_heading']
 assert cue==public['experts'][key]['fudan_step_task']['world_model_input_heading'] and p['producer']['world_model_source_SHA']==cue['candidate_WM_source_SHA']
 assert w['counters']['new_world_updates']==700 and w['counters']['new_policy_updates']==6 and w['counters']['completed_fresh_controls']==240
 roles[key]=dict(passed_first_NEW_native_policy=True,counters=w['counters'],events=p['original_task_events'],GPU_first_snapshot=v['GPU_snapshot'],worker=v['worker'],node=v['node'],actual_GPU_WM_input_readback_was_guard_checked_in_frozen_first_source=True,GPU_input_readback_raw_value_not_exported_by_first_reader=True,producer_world_model_source_SHA=p['producer']['world_model_source_SHA'],physical_seed=p['producer']['physical_initial_seed'],saved_learning_seed=p['producer']['native_learning_seed'])
g=first['normal_closing_gates'];tz=datetime.timezone(datetime.timedelta(hours=8))
iso={k:datetime.datetime.fromtimestamp(v,tz).isoformat() for k,v in g.items()}
out=dict(schema='mod4.actual114.two_NEW_native_WM_heading.first.v1',epoch=time.time(),run_id=first['run_id'],first_combined_report=str(source),first_report_SHA=H(source),resource_alias=str(alias),owner=actual['identities']['owner']['exact_identity'],owner_root=actual['owner_root'],node_roots=actual['node_roots'],actual_signed_go=first['go'],roles=roles,
 new_actual_learning=True,full_final_formals_and_original_cost_pending=True,not_continuous_alive_or_skill_or_causal_learning_gain=True,
 source111_input=dict(SHA='24f94861f17b05fa4abb959946822912f07e9b2b07a49461f79aa55739d5fa12',bytes=256235849,iteration=18597,world_updates=185970,policy_updates=17893),
 selected_WM_input_change='Only WM.inputs features1/3 bounded fixed-world heading .005*(cosyaw-1),.005*sinyaw. Reward111/physics/architecture/optimizer/norm state inherited. Current Pi/WM updates do not prove jump success.',
 actual_source_SDK_CPU_two_candidates_passed=True,source_CPU_newpurpose_model_loads=dict(native111_each_candidate=1,necessary_normal86_each_candidate=1),actual_CPU_report_SHAs=['cb8e63e23a13e794cd983dfe0b49de874743e6216c65614faaf03ff870abf40e','f6db5efea4ed086230e23a1a4e09852be82ba8e32d087175910e9e332916cac3'],actual_wait_proof_SHAs=['510cf5447e2e6feb049e3a0f0f786b6c5b92c53f3db69d6d88fe2b9951a254ac','23c48d54fdaf8f2460cdb64f6029dda298521e7971a9d4be1f657017353d4253'],
 normal_closing_gates=g,normal_closing_BJT=iso,normal_collector=str(Q/'collect_TWO114_fudan270_formals_original_cost_normal900_UNUSED_once.py'),initial_NEW_formal_CPU=str(Q/'review_TWO114_NEW_fudan270_formals_shared_witness_initial_CPU_UNUSED_once.py'),normal_sources_frozen_unused=True,
 next='Preserve healthy finite owner/jobs. Only normal900 local+remote/owner850/node180/1140 after freshLOCALCIM/globalseriallease and actualsignedmaxnominal-now<=900; then allout/CNone/locks/uniqueoriginalfees sumonce/twoNEWformal transfers/fulltwohostSHA before initialNEWformal2+ONEsharednormal86/input111PT0. No earlydownload/firstmetadata replay or identical extra learning window.',
 latest_qualified_native_METHOD_still111_until114_formals_and_initialCPU=True,real270_skill_achieved=False)
put(R/'CURRENT_ACTUAL114_TWO_WM_HEADING_FIRST_NEW_UPDATES_AND_NORMAL_CLOSING_WORK_ORDER.json',out)
put(R/'KNOWN_ACTIVE114_AUTHORITY_BINDING_FOR_SERIAL_EXPERT_EVALUATION.json',dict(owner=out['owner'],run_id=out['run_id'],go=out['actual_signed_go']))
put(R/'ROOT_LOCAL_METADATA_LOOKUP_AND_UNCONSUMED_GATE_ERROR_SCOPE_ACTUAL.json',dict(epoch=time.time(),local_metadata_only_errors=["Guessed E3 readonly filename run_E3_source210_readonly_once_v4_exactEntryReceipt.py absent; actual frozen run_E3_source210_readonly_v4.py discovered/read; no remote affected.","Guessed NEW111 reviewer filename containing fudan270 absent; selected actual review_NEW111_seed27_formal_initial_whole_CPU_UNUSED_once.py used.","E3V1 terminal reader attempted ~5sec before original900 gate; original guard refused before marker/network; exact unused entry executed later afterfreshCIM and actualgate. Original error file retained.","Looked for first114 aggregate in resource reports; actual source first writes Q/reports. Source first data existed and passed; exactbyte alias now created at frozen collector's expected resource reports path. No rerun or model/hostquery."],no_guard_relaxation_or_old_consumed_once_reexecution=True))
print(json.dumps(dict(actual_two_NEW_updates=True,roles={k:v['counters'] for k,v in roles.items()},normal_BJT=iso,collector_alias_exact=True),ensure_ascii=False))
