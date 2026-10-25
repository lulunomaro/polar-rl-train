"""Unique actual80 training/readonly landing journal phase. Later additions ordinary only."""
from pathlib import Path
import json,time,tomllib,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;G=W/'polar-rl-train';R=N/'reports';P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V79C_20261026';M=T/'H1_STEP270_READONLY_LANDING_JOURNAL_PREPARATION_20261026'
engine=T/'MOD4_SAMPLING_THROUGHPUT_OPTIMIZATION_PREPARATION_20261025/archive_current_implementation_and_MOE_preparation_stages_unique_once.py';s=engine.read_text('utf8')
def patch(a,b):
 global s
 assert s.count(a)==1,a
 s=s.replace(a,b,1)
patch("'t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation'","'t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation','stage80':'mod4-three4090-v8-readonly-landing-event-journal80'")
patch("nr=(S if kind=='performance' else T/'MOD4_MOE_RL_T2Z_TRANSFER_PAPER_PREPARATION_20261025')/'reports'","nr=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V80_20261026'/'reports'")
patch("TAG='trial-20261025-'+ID;D=G/('versions/20261025_'+ID)","TAG='trial-20261026-'+ID;D=G/('versions/20261026_'+ID)")
patch("'--kind','diagnostic'","'--kind','training'")
ns={'__name__':'archive80_utilities_only','__file__':str(engine)};exec(compile(s,str(engine),'exec'),ns);git=ns['git']
def main():
 assert len(git('tag','--list').splitlines())==1451 and not git('status','--porcelain')
 prior=G/'versions/20261026_mod4-three4090-qualified78-byte-exact-metadata-fix79c';assert git('show','HEAD:'+str((prior/'ordinary_closed79c_models_cost_saved_motion/ACTUAL_RESULT_NOTE.md').relative_to(G)).replace('\\','/'))
 for p in (prior/'COMPLETE_FILE_CAPTURE_INDEX.json',prior/'ordinary_closed79c_models_cost_saved_motion/ORDINARY_CAPTURE_INDEX.json'):ns['prior'](p)
 first=json.loads((R/'THREE_EXPERT_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes());assert first['passed'] and first['actual_finite_returned'] and first['all_three_actual_GO_and_positive_PPO']
 cpu=json.loads((R/'H1_FULL_INSTALLED_SOURCE_SDK_RSL_CPU_ACTUAL.json').read_bytes());assert cpu['sampling_acceleration_CPU']['landing_event_journal_CPU']['passed'] and cpu['sampling_acceleration_CPU']['lifetime_goal_diagnostic_CPU']['passed'] and cpu['new_reward_integration_CPU']['actual_installed_sampled_excess_SDK_compute_tested']
 proof=json.loads((P/'reports/THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled'] and all(x['actual_cost']['duration_bound_passed'] for x in proof['models'].values())
 a=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'));assert a['status']=='ACTIVE' and a['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353' and a['prompt']==(R/'CURRENT_ACTUAL80_THREE4090_V8_LANDING_JOURNAL_MONITOR_SOURCE.txt').read_text('utf8')
 summary={k:dict(updates=v['updates'],Adam=v['Adam'],SHA=v['final']['SHA']) for k,v in proof['models'].items()}
 note='Continue H1/E2/E3 on all three4090 cards from complete79c sources and original single-writer closure. H1 V8 reward, actor/PPO/commands/physics/save/success and trace bytes are unchanged. A readonly optional CPU journal now references16 existing complete rows and copies selected env arrays at the first64 landing-positive control/env records plus up to64 following controls, with reset/episode censoring, explicit cap/skips and immutable small NPZ versions/fullSHA. Original lifetime counts remain uncapped. No per-step GPU read, actor forward, RNG, model tensor or original retention change. The old counter AST is exact except three hooks; original critical persistence and error handling remain, optional journal failures are diagnostic and do not become model/skill gates.20k forwarding/reset/cap/IO/persistence source tests, four negative counter mutations and13 guard/metadata-byte cases were followed by actual target SDK/RSL/full-source admission, original resources/valid_ready and actual three GO/positive PPO/UUID identities. First optional journal runtime status is recorded without promoting it to frozen success.78 first full record diagnostic had32 original landing and0stable recovery; different scopes cannot be compared as causal gains. The new journal targets landing-to-stability evidence, not a new reward or success criterion. V9 and old79b remain unused. All source/errors/reports/provenance retained, including the old79c prompt Q8-size text substitution correction from an existing producer index with no weight reread. No new budget/refund/ledgercopy/secondwriter/subagents/T2-z/model downloads. Source79c remains qualified until full80 closure; current80 fees pending. One unique80 phase; later supplements ordinary.\n'+json.dumps(dict(complete79c_sources=summary,original79c_fee=proof['actual_cost_sumonce'],closed79c_remaining_snapshot=proof['remaining_actual_snapshot'],completed79c_events=proof['models']['h1']['lifetime_goal_event_diagnostic'],first80_lifetime=first['source210']['lifetime_goal_diagnostic_first_snapshot'],first80_journal=first['source210'].get('landing_event_journal_first_snapshot')),ensure_ascii=False,indent=2)+'\n'
 ns['run_stage']('stage80',[N,M],[T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v124.py',engine],note,'Continue three experts with readonly landing-to-recovery event trajectories')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('ARCHIVE80_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_if_record_started=True,no_repeated_record_tag_or_training=True),f,indent=2)
  raise
