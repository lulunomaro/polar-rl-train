"""Unique actual79 stage, only after three GO/PPO and target diagnostic CPU/runtime evidence."""
from pathlib import Path
import json, time, tomllib, traceback
N = Path(__file__).resolve().parent
T = N.parent
W = T.parent
G = W / 'polar-rl-train'
R = N / 'reports'
P = T / 'H1_STEP270_THREE_EXPERTS_RESOURCE_V78_20261026'
M = T / 'H1_STEP270_FULL_PATH_CLEARANCE_CARRY_V9_MATH_PREPARATION_20261026'
engine = T / 'MOD4_SAMPLING_THROUGHPUT_OPTIMIZATION_PREPARATION_20261025/archive_current_implementation_and_MOE_preparation_stages_unique_once.py'
s = engine.read_text('utf8')

def patch(old, new):
    global s
    assert s.count(old) == 1, old
    s = s.replace(old, new, 1)
patch("'t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation'", "'t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation','stage79c':'mod4-three4090-qualified78-byte-exact-metadata-fix79c'")
patch("nr=(S if kind=='performance' else T/'MOD4_MOE_RL_T2Z_TRANSFER_PAPER_PREPARATION_20261025')/'reports'", "nr=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V79C_20261026'/'reports'")
patch("TAG='trial-20261025-'+ID;D=G/('versions/20261025_'+ID)", "TAG='trial-20261026-'+ID;D=G/('versions/20261026_'+ID)")
patch("'--kind','diagnostic'", "'--kind','training'")
ns = {'__name__': 'archive79_utilities_only', '__file__': str(engine)}
exec(compile(s, str(engine), 'exec'), ns)
git = ns['git']

def main():
    assert len(git('tag', '--list').splitlines()) == 1450 and (not git('status', '--porcelain'))
    prior = G / 'versions/20261026_mod4-three4090-v8-readonly-lifetime-diagnostics78'
    assert git('show', 'HEAD:' + str((prior / 'ordinary_closed78_models_cost_saved_motion/ACTUAL_RESULT_NOTE.md').relative_to(G)).replace('\\', '/'))
    for p in (prior / 'COMPLETE_FILE_CAPTURE_INDEX.json', prior / 'ordinary_closed78_models_cost_saved_motion/ORDINARY_CAPTURE_INDEX.json'):
        ns['prior'](p)
    first = json.loads((R / 'THREE_EXPERT_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes())
    assert first['passed'] and first['actual_finite_returned'] and first['all_three_actual_GO_and_positive_PPO']
    cpu = json.loads((R / 'H1_FULL_INSTALLED_SOURCE_SDK_RSL_CPU_ACTUAL.json').read_bytes())
    assert cpu['new_reward_integration_CPU']['actual_installed_sampled_excess_SDK_compute_tested'] and cpu['sampling_acceleration_CPU']['lifetime_goal_diagnostic_CPU']['passed']
    diag = first['source210']['lifetime_goal_diagnostic_first_snapshot']
    assert diag['present'] and diag['value']['diagnostic_valid'] and (diag['value']['complete_control_rows'] >= 24)
    proof = json.loads((P / 'reports/THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())
    assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled'] and all((x['actual_cost']['duration_bound_passed'] for x in proof['models'].values()))
    a = tomllib.loads((Path.home() / '.codex/automations/mod4-10/automation.toml').read_text('utf8'))
    assert a['status'] == 'ACTIVE' and a['target_thread_id'] == '01a07a2d-9036-7531-a012-692df9f56353'
    assert a['prompt'] == (R / 'CURRENT_ACTUAL79C_THREE4090_V8_LIFETIME_DIAGNOSTIC_MONITOR_SOURCE_V2.txt').read_text('utf8')
    summary = {k: dict(updates=v['updates'], Adam=v['Adam'], SHA=v['final']['SHA']) for k, v in proof['models'].items()}
    note = 'Continue all three4090 experts from full78 models and original fees/allout, preserving the same V8 reward, actual78 readonly lifetime trace/counter/sampling checker, actor/PPO/commands/physics/save/success.78 completed3216 controls across20k counted29480 original takeoffs,32 original top landing events and0 stable recoveries, with full row coverage and no invalid/negative deltas. This is completed stochastic control-record scope, not all callback replay, frozen skill qualification, or causal improvement over older retained snippets. The last48 saved controls/current episode have separate scopes and cannot erase32. V9 math/SDK-source CPU and79b conditional protocol remain unselected/uninstalled.\n\nThe initial79 preGO recovery-source guard correctly rejected a metadata helper whose builder normalized CRLF to LF, changing2536 to2499bytes. No owner/node/GO or fee was created; exact own partial noNODE/GO/out receipt retained. New unused79c directly inherits exact qualified78 metadata bytes and asserts the full SHA; original strict inventory/guards/controllers are not relaxed. New guard differs79 only AUTH filename, E2 installer only new owned namespace/previous78 paths, E3 only exact source Adam assertion. Fresh real target SDK/RSL/full-source CPU, copied-payload resource guards/valid_ready, actual threeGO/firstPPO/UUIDs and valid runtime counter passed. Original failed source/error/partial and all corrections retained in the same unique phase. All budget/canonical/private/shared/secret/no-subagent protections remain. Source78 stays latest qualified until complete79c models/CPU/cost/allout; current79c fees pending. No oldonce retry or extra record/tag. Binary originals only actualpath/bytes/existingproducerSHA; later supplements ordinary.\n' + json.dumps(dict(complete78_sources=summary, original78_fee=proof['actual_cost_sumonce'], closed78_remaining_snapshot=proof['remaining_actual_snapshot'], closed78_events=proof['models']['h1']['lifetime_goal_event_diagnostic'], first79c_runtime_diagnostic=diag), ensure_ascii=False, indent=2) + '\n'
    ns['run_stage']('stage79c', [N, M, T / 'H1_STEP270_THREE_EXPERTS_RESOURCE_V79_20261026'], [T / 'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v123.py', engine], note, 'Continue three experts from78 with byte-exact metadata inheritance after preGO refusal')
if __name__ == '__main__':
    try:
        main()
    except BaseException:
        with (R / ('ARCHIVE79C_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json')).open('x', encoding='utf8') as f:
            json.dump(dict(epoch=time.time(), error=traceback.format_exc(), actual_HEAD=git('rev-parse', 'HEAD'), resume_existing_objects_if_record_started=True, no_repeated_record_tag_or_training=True), f, indent=2)
        raise
