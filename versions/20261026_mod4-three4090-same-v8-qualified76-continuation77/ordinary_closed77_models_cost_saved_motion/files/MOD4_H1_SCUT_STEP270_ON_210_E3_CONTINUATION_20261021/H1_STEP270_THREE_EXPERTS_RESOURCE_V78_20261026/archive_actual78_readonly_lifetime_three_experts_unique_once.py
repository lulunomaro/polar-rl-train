"""Unique actual78 stage, only after three GO/PPO and target diagnostic CPU/runtime evidence."""
from pathlib import Path
import json,time,tomllib,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports'
P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V77_20261026'
M=T/'H1_STEP270_LIFETIME_GOAL_ACCOUNTING_DIAGNOSTIC_PREPARATION_20261026'
engine=T/'MOD4_SAMPLING_THROUGHPUT_OPTIMIZATION_PREPARATION_20261025/archive_current_implementation_and_MOE_preparation_stages_unique_once.py'
s=engine.read_text('utf8')
def patch(old,new):
 global s
 assert s.count(old)==1,old
 s=s.replace(old,new,1)
patch("'t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation'", "'t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation','stage78':'mod4-three4090-v8-readonly-lifetime-diagnostics78'")
patch("nr=(S if kind=='performance' else T/'MOD4_MOE_RL_T2Z_TRANSFER_PAPER_PREPARATION_20261025')/'reports'", "nr=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V78_20261026'/'reports'")
patch("TAG='trial-20261025-'+ID;D=G/('versions/20261025_'+ID)", "TAG='trial-20261026-'+ID;D=G/('versions/20261026_'+ID)")
patch("'--kind','diagnostic'", "'--kind','training'")
ns={'__name__':'archive78_utilities_only','__file__':str(engine)}
exec(compile(s,str(engine),'exec'),ns);git=ns['git']
def main():
 assert len(git('tag','--list').splitlines())==1449 and not git('status','--porcelain')
 prior=G/'versions/20261026_mod4-three4090-same-v8-qualified76-continuation77'
 assert git('show','HEAD:'+str((prior/'ordinary_closed77_models_cost_saved_motion/ACTUAL_RESULT_NOTE.md').relative_to(G)).replace('\\','/'))
 for p in (prior/'COMPLETE_FILE_CAPTURE_INDEX.json',prior/'ordinary_closed77_models_cost_saved_motion/ORDINARY_CAPTURE_INDEX.json'):ns['prior'](p)
 first=json.loads((R/'THREE_EXPERT_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes())
 assert first['passed'] and first['actual_finite_returned'] and first['all_three_actual_GO_and_positive_PPO']
 cpu=json.loads((R/'H1_FULL_INSTALLED_SOURCE_SDK_RSL_CPU_ACTUAL.json').read_bytes())
 assert cpu['new_reward_integration_CPU']['actual_installed_sampled_excess_SDK_compute_tested'] and cpu['sampling_acceleration_CPU']['lifetime_goal_diagnostic_CPU']['passed']
 diag=first['source210']['lifetime_goal_diagnostic_first_snapshot']
 assert diag['present'] and diag['value']['diagnostic_valid'] and diag['value']['complete_control_rows']>=24
 proof=json.loads((P/'reports/THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())
 assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled'] and all(x['actual_cost']['duration_bound_passed'] for x in proof['models'].values())
 a=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))
 assert a['status']=='ACTIVE' and a['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
 assert a['prompt']==(R/'CURRENT_ACTUAL78_THREE4090_V8_LIFETIME_DIAGNOSTIC_MONITOR_SOURCE.txt').read_text('utf8')
 summary={k:dict(updates=v['updates'],Adam=v['Adam'],SHA=v['final']['SHA']) for k,v in proof['models'].items()}
 note='Continue all three4090 experts from fully qualified77 sources, preserving H1 V8 reward/actor/PPO/commands/physics/save/success standards and E2/E3 tasks. The only H1 integration is a readonly diagnostic of original completed-control event-counter deltas across selected resets, reusing existing copied CPU rows with one initial counter snapshot. Exact import and three trace hooks, source hashes, AST normalization against embedded original bytes, meaningful20k CPU forwarding/reset/persistence/failure fixtures and actual target SDK/source admission passed. Original actions object/values, output tuple, reward, RNG, physics, critical persistence and error paths are retained. Optional diagnostic I/O failures are recorded without replacing original training errors; invalid diagnostic data does not alter model qualification or success criteria. The strict guard admits one exact H1 counter module and exact reviewed trace/checker files, preserving all other protected code/approvals. Both failed local AST candidates and corrected candidateV3 are retained.\n\nAll three actual GO/positive PPO and expected GPU UUID/process identities passed. The first actual runtime counter JSON is present and valid; it describes only completed stochastic training controls up to that snapshot, not full78 totals or frozen-policy graduation. Complete77 remains the production continuation source until complete78 FINAL/wholeCPU/originalfee/allout; current78 fees pending. No automatic T2-z, new weights, subagents, new budget, refunds, ledger copy or second writer. All sources/errors/full reports and prior ordinary references are retained; binary originals are indexed only by true path/size/existing producer SHA. One unique actual78 trial, later additions ordinary only.\n'+json.dumps(dict(complete77_sources=summary,original77_fee=proof['actual_cost_sumonce'],closed77_remaining_snapshot=proof['remaining_actual_snapshot'],first78_runtime_diagnostic=diag),ensure_ascii=False,indent=2)+'\n'
 ns['run_stage']('stage78',[N,M],[T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v120.py',engine],note,'Continue three experts with readonly completed-control lifetime event diagnostics')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('ARCHIVE78_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_if_record_started=True,no_repeated_record_tag_or_training=True),f,indent=2)
  raise
