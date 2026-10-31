"""Freeze necessary saved-cycle read counts after numerical parser source tests."""
from pathlib import Path
import hashlib, json, math, time
from w35_cycle_acceptance189 import CycleAccumulator

B=Path(__file__).resolve().parent;T=B.parent;R=B/'reports'
with (R/'W35_189_PARSER_SOURCE_CPU_STARTED.json').open('x',encoding='utf8') as f:
    json.dump(dict(epoch=time.time(),models=0,raw=0,network=0),f)

def row(env,progress,seconds,terminal=False):
    return dict(schema='W35_same_uid_sampled_signed_cycle_v1',complete_sampled_span=True,
                env_id=env,episode_uid=1,command_uid=1,profile=4,first_control=0,
                last_control=round(seconds/.02)-1,start_observed=True,controls=round(seconds/.02),
                seconds=seconds,actual_progress_m_s=progress,sampled_BODY_reference_progress_m_s=.5,
                sampled_signed_turn_rad=2*math.pi+.01,actual_projected_displacement_m=progress*seconds,
                nominal_world_progress_m_s=.5,terminal_non_timeout=terminal,terminal_timeout=False)
a=CycleAccumulator();a.add(row(0,.48,2));a.add(row(1,.6,4));a.add(row(2,.8,2,True))
a.add(dict(schema='W35_same_uid_sampled_signed_cycle_v1',complete_sampled_span=False))
value=a.finish();assert value['rows']==4 and value['partial_cycle_events']==1
assert value['all_complete']['events']==3 and value['nonterminal_complete']['events']==2
assert math.isclose(value['nonterminal_complete']['cycle_progress_event_MAE_m_s'],.06)
assert math.isclose(value['nonterminal_complete']['cycle_progress_duration_weighted_MAE_m_s'],.44/6)
assert value['all_complete']['along_only_within_original_point05_m_s_events']==1
assert value['skill_graduated'] is False
rejected=False
try:a.add(row(0,.48,2))
except AssertionError:rejected=True
assert rejected
with (R/'ROOT189_W35_PARSER_SOURCE_CPU_RETURNED_ACTUAL.json').open('x',encoding='utf8') as f:
    json.dump(dict(passed=True,epoch=time.time(),synthetic_complete=3,synthetic_partial=1,
                   aggregation_and_terminal_denominators_checked=True,duplicate_refused=True,
                   no_actual_W35_raw_read=True,actual_skill_not_yet_measured=True),f,indent=2)
producer_file=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/W35_UID_CYCLE_V2_FULL800_COMMAND_UID_CYCLE_SAVED_TEXT_REVIEW_20261030_V1/EXACT_SAVED_SMALL_UTF8_PUBLICATIONS/W35_OBSERVED_COMMAND_UID_AND_CYCLES_ACTUAL.json'
producer=json.loads(producer_file.read_bytes())['cycle_JSONL']
assert producer['rows']==5039 and producer['bytes']==2618543 and producer['SHA']=='f5f6cbd98259358b0755992e2393a8e63e1061fdf1789fbbdfc6dbfe7aa53561'
recover=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/W35_UID_CYCLE_V2_NORMAL_AST_ONLY_SECURE_WRAPPER_20261030_V1/run_W35_V2_NORMAL_exact_AST_recover_secure_ingress_UNUSED_once.py'
protocol=dict(schema='mod4.experts189.W35_first_cycle_content_purpose.v1',epoch=time.time(),
              purpose='Human authorized complete old-expert skill acceptance: resolve missing per-cycle MAE, true unique union and nonterminal denominator from exact existing producer; not statistics for Git',
              maximum_raw_opens=1,maximum_forward_byte_passes_including_EOF=1,
              maximum_model_opens=0,maximum_local_raw_reopens=0,
              maximum_SDK_GPU=0,maximum_remote_seconds=110,producer=producer,
              parser_SHA=hashlib.sha256((B/'w35_cycle_acceptance189.py').read_bytes()).hexdigest(),
              entry_SHA=hashlib.sha256((B/'run189_W35_saved_cycle_single_pass_once.py').read_bytes()).hexdigest(),
              secure_recover_wrapper_SHA=hashlib.sha256(recover.read_bytes()).hexdigest(),
              no_old_once_main_or_actor_calls=True,
              original_along_only_tolerance_m_s=.05,
              original_full_acceptance_remains_unknown_if_cross_or_yaw_not_saved=True,
              only_small_derived_JSON_returned_no_raw_download=True)
with (R/'W35_189_FIRST_SAVED_CYCLE_READ_PURPOSE_FROZEN.json').open('x',encoding='utf8') as f:
    json.dump(protocol,f,indent=2)
print(json.dumps(dict(passed_source_CPU=True,purpose_frozen=True,raw_opened=0,models=0)))
