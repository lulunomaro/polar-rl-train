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
patch("'t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation'", "'t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation','stage79b':'mod4-three4090-h1-full-path-clearance-carry-v9-training79b'")
patch("nr=(S if kind=='performance' else T/'MOD4_MOE_RL_T2Z_TRANSFER_PAPER_PREPARATION_20261025')/'reports'", "nr=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V79B_20261026'/'reports'")
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
    assert a['prompt'] == (R / 'CURRENT_ACTUAL79B_THREE4090_V9_LIFETIME_DIAGNOSTIC_MONITOR_SOURCE.txt').read_text('utf8')
    summary = {k: dict(updates=v['updates'], Adam=v['Adam'], SHA=v['final']['SHA']) for k, v in proof['models'].items()}
    note = 'Continue all three4090 experts from fully closed78 qualified models and original independent fees. H1 V9 changes only the reward recipe version and one clearance-carry potential denominator: continue rewarding simultaneous forward transport and wheel clearance until the already-existing path target=.60, instead of saturating the joint potential at leading edge=.35 before full wheel footprint arrival. Same signed bounded potential total scale8, all prior V5/V6A/V7/V8 terms/weights, actor/commands/actions/PPO/STD/physics and real270mm contact/stable success standards retained. Actual78 readonly trace/counter/sampling checker bytes and original critical persistence/error paths are exact; only reward/checker and source guard role/auth adapt. Original controller valid_ready logic is unchanged and uses its existing reward-migration contract. Local20k algebra/source/saved-SDK and22 original source/controller cases were followed by actual target full-source SDK/RSL checks, resources, valid_ready and actual threeGO/firstPPO/runtime TaskV9 plus valid counter evidence. This establishes execution, not causal rootcause, speed gain or learned step success. Same79 alternative was source-only unused. All oldauth/source/errors and conditional preparation retained. No subagents, new budget/refund/copiedledger/secondwriter, new inputs, physics, weights or automatic T2-z. Source78 stays qualified until full79b models/CPU/cost/allout, current79b original fees pending. Binary only actualpath/bytes/existingproducerSHA. One unique79b stage; later supplements ordinary.\n' + json.dumps(dict(complete78_sources=summary, original78_fee=proof['actual_cost_sumonce'], closed78_remaining_snapshot=proof['remaining_actual_snapshot'], first79b_runtime_diagnostic=diag), ensure_ascii=False, indent=2) + '\n'
    ns['run_stage']('stage79b', [N, M], [T / 'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v122.py', engine], note, 'Continue three experts with H1 full-path clearance carry V9 reward')
if __name__ == '__main__':
    try:
        main()
    except BaseException:
        with (R / ('ARCHIVE79B_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json')).open('x', encoding='utf8') as f:
            json.dump(dict(epoch=time.time(), error=traceback.format_exc(), actual_HEAD=git('rev-parse', 'HEAD'), resume_existing_objects_if_record_started=True, no_repeated_record_tag_or_training=True), f, indent=2)
        raise
