"""Publish actual same-run CLOSED metadata only; never opens a checkpoint or starts evaluation."""
from pathlib import Path
import json, time

D = Path(__file__).resolve().parent
ROOT = '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V2_E0_SCUT_HOUR_FULL_LEARNER_MIGRATION_20261106_062902_1793917742719982000'
FORMAL = '6cdac1e4b84df407d41a38444b87eaa91309ed898af05fe95a6c80f6ac3fd693'
EXACT7 = ('actor_exact', 'critic_exact', 'normalization_exact', 'learned_STD_exact', 'Adam17_exact', 'LR_exact', 'iteration_exact')

def read(path):
    return json.loads(Path(path).read_bytes())

def link(path, label):
    return '[' + label + '](<' + Path(path).as_posix() + '>)'

def main():
    outputs = [D/'SCUT_E0_HOUR_ACTUAL_OUTCOME_V1.json', D/'SCUT_E0_HOUR_ACTUAL_OUTCOME_V1.md', D/'CURRENT_PROGRESS_V12_SCUT_HOUR_ACTUAL_QUALITY.md']
    assert not any(p.exists() for p in outputs), 'Keep all earlier publications; no overwrite'
    pointer = read(D/'E0_SCUT_HOUR_CLOSED_RESULT_PATH.json')
    train_path = Path(pointer['path']); train = read(train_path)
    assert train['closed'] is True and pointer['root'] == train['root'] == ROOT
    meta = train['metadata']; case = train['cases']['E0']
    end = meta.get('OWNER_EXIT_ACTUAL.json') or {}; outer = meta.get('OUTER_OWNER_WAIT_ACTUAL.json') or {}
    wait = case.get('PARENT_WAITED_ACTUAL.json') or {}; qual = wait.get('semantic_qualification') or {}
    final = case.get('V2_MIGRATION_FINAL.json') or {}; full = final.get('fullsave') or {}
    initial = case.get('SCUT_INITIAL_CHECKPOINT_ACCEPTANCE.json') or {}
    checks = {
        'actual_owner_waits_cost_and_leases': all(end.get(k) is True for k in ('all_own_children_waited', 'original_cost_settled', 'original_private_finite_authority_leases_released')),
        'owner_errors_empty': end.get('errors') == [],
        'outer_actually_reaped_rc0': outer.get('original_owner_reaped') is True and outer.get('actual_wait_returncode') == 0,
        'actual_child_semantic_qualification': qual.get('qualified') is True and bool(qual.get('checks')) and all(qual['checks'].values()),
        'worker_ERROR_absent': case.get('ERROR_JSON') == {},
        'actual_final_execution': final.get('passed_execution') is True and final.get('completed_requested_update_window') is True and final.get('error') is None and final.get('close_errors') == [],
        'actual_SCUT_hour_mode': final.get('window_mode') == 'SCUT_V14_ORIGINAL_FINITE_WALL_CLOCK_HOUR' and final.get('requested_update_quota') is None and final.get('hour_not_started') is False,
        'initial_seven_exact': initial.get('passed') is True and initial.get('source_SHA') == FORMAL and all(initial.get(k) is True for k in EXACT7),
        'latest_is_FINAL_fullsave': bool(final.get('latest_complete_save')) and final.get('latest_complete_save') == full.get('latest_complete_save'),
    }
    train_ok = all(checks.values())
    u = final.get('completed_actual_updates'); adam_calls = final.get('actual_optimizer_steps'); controls = final.get('actual_rollout_controls')
    if train_ok:
        assert type(u) is int and u > 0 and adam_calls == 20*u and controls == 24*u
        assert len(full['live_core']['Adam17_steps']) == 17
        assert final['source_once1'] is True and final['source_env_state_applied'] is False
        assert all(final['source_IO'][k] == 1 for k in ('physical_byte_opens', 'SHA_calculations', 'CPU_decodes'))
    evaluation = None; eval_path = None; eval_pointer = D/'SCUT_E0_HOUR_FROZEN_CLOSED_RESULT_PATH.json'
    if eval_pointer.exists():
        ep = read(eval_pointer); eval_path = Path(ep['path']); evaluation = read(eval_path)
        assert evaluation['closed'] is True and evaluation['root'] == ep['root']
        if evaluation.get('execution_qualified') is True:
            assert train_ok
            task = evaluation['cases']['E0']['task.json']; latest = final['latest_complete_save']
            assert task['checkpoint_path'] == latest['path'] and task['checkpoint_SHA'] == latest['sha256'] and task['checkpoint_bytes'] == latest['bytes']
            assert evaluation['skill_grader'] is evaluation['full_skill_graduation'] is None
    metrics = (evaluation or {}).get('normal_metrics')
    eval_ok = (evaluation or {}).get('execution_qualified') is True
    health = None
    if eval_ok:
        assert metrics['controls'] == 1000 and metrics['physics_callbacks'] == 8000 and metrics['feedback_samples'] == 2000
        health = (metrics['unique_envs_terminated'] == 0 and metrics['max_current_mimic_rad'] <= .01 and metrics['max_current_closure_m'] <= .01)
    if not train_ok:
        decision = 'KEEP_FORMAL_E0_TRAINING_EXECUTION_NOT_QUALIFIED_NO_PROMOTION'
    elif evaluation is None:
        decision = 'PRESERVE_COMPLETE_SCUT_E0_CANDIDATE_PENDING_INDEPENDENT_EVALUATION'
    elif not eval_ok:
        decision = 'PRESERVE_SCUT_E0_EVALUATION_EXECUTION_FAILURE_NO_SKILL_CLAIM'
    elif not health:
        decision = 'KEEP_FORMAL_E0_NO_PROMOTION_FINITE_SCOPE_HEALTH_NOT_RETAINED'
    else:
        decision = 'RETAIN_SCUT_E0_CANDIDATE_PENDING_DEFINED_PROFILE_AND_MULTISEED_GRADER'
    result = dict(kind='ACTUAL_SCUT_E0_HOUR_AND_INDEPENDENT_EVAL_METADATA_NOT_GRADUATION', epoch=time.time(),
        training_root=ROOT, training_closed_path=str(train_path), training_execution_qualified=train_ok, training_reader_checks=checks,
        training_owner_exit=end, training_outer_actual_wait=outer, training_child_wait=wait,
        actual_new_updates=u, actual_optimizer_step_calls=adam_calls, actual_rollout_controls=controls,
        optimized_transitions=(20000*controls if train_ok else None), training_timing=final.get('training_timing'),
        requested_hour_wall_window_elapsed=final.get('requested_hour_wall_window_elapsed'), stop_reason=final.get('stop_reason'),
        source_IO=final.get('source_IO'), initial_checkpoint_acceptance=initial,
        latest_complete_save=final.get('latest_complete_save'), same_FINAL_live_core=full.get('live_core'), recipe_binding=final.get('recipe_binding'),
        independent_eval_closed_path=(str(eval_path) if eval_path else None), evaluation_execution_qualified=(eval_ok if evaluation else None),
        evaluation_metadata=evaluation, normal_metrics=metrics, finite_scope_health=health,
        health_rule_scope='Conservative retention prerequisite only: no physical termination and original mimic/closure thresholds; NOT a new complete profile grader',
        full_skill_graduation=None, missing_profile_grader_not_invented=True, decision=decision,
        exact_upstream_entire_environment_resume_claimed=False,
        explicit_MOD4_adaptations=['A0 actor35/critic38/action6 versus upstream35/78/6', 'MOD4 feasible closed-chain reset bank and original fullDR', 'MOD4 bodies, actuators, gas and D6 native transmission', 'complete inherited learner, learned STD and mutable LR retained'],
        old_formal_source_and_Registry_unchanged=True, other_experts_scheduled=False, goal_complete=False,
        publisher_model_raw_SDK_GPU_C_or_remote_operations=0)
    text = '# E0 SCUT有限小时窗：真实关闭与独立评测\n\n'
    text += f'训练执行资格：**{train_ok}**。决策：`{decision}`。总技能目标尚未完成；不自动晋升。\n\n'
    text += f'实际新增 PPO：{u}；实际 Adam step calls：{adam_calls}；实际 rollout controls：{controls}；优化 transitions：{result["optimized_transitions"]}。\n\n'
    text += '## 真实计时\n\n以下来自同一 FINAL；GO到退出不等于有效PPO一小时。\n\n```json\n' + json.dumps(final.get('training_timing'), indent=2, ensure_ascii=False) + '\n```\n\n'
    text += f'原窗 deadline 是否到达：{final.get("requested_hour_wall_window_elapsed")}；停止原因：`{final.get("stop_reason")}`。原始3900/save3600/headroom300未扩展；没有退款或重放。\n\n'
    text += '## 完整候选（只读producer元数据，无checkpoint重开）\n\n```json\n' + json.dumps(final.get('latest_complete_save'), indent=2, ensure_ascii=False) + '\n```\n\n'
    text += f'独立评测执行资格：{result["evaluation_execution_qualified"]}；有限scope健康前提：{health}。缺失的完整二元/profile grader保持 `null`。\n\n'
    text += '```json\n' + json.dumps(metrics, indent=2, ensure_ascii=False) + '\n```\n\n'
    text += '物理终止的环境数与终止事件数分开；不拼接reset，不放宽原closure/mimic门。执行合格、无摔倒或运行时长均不等于技能毕业。未做配对原生母版多seed比较，不作因果改善宣称。\n\n'
    text += '参考任务为 Robotics-Wheelbipe-V14-Flat-v0 的源映射；MOD4 A0 critic38、原resetbank/fullDR、形态执行器及完整learner兼容均为明确适配，不称上游critic78或整环境数值全等。正式母版、旧Registry、其余八专家及86未动。\n\n'
    text += '证据：' + link(train_path, '实际训练关闭') + (' / ' + link(eval_path, '独立评测关闭') if eval_path else '；独立评测尚无关闭结果') + ' / ' + link(outputs[0], '完整结果JSON') + '。\n\n本报告和新增观测/接线/失败待下一有意义feature-only唯一annotated归档；main只读，不为Git重开模型或重放物理。\n'
    for p, value in ((outputs[0], json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False)), (outputs[1], text),
                     (outputs[2], '# SCUT E0实际结果交接\n\n' + f'源于同一真实CLOSED，训练资格{train_ok}，PPO {u}，评测资格{result["evaluation_execution_qualified"]}，grader=null，决策{decision}。Goal664仍active，其余八专家不自动开。\n\n' + link(outputs[1], '主报告') + '\n')):
        with p.open('x', encoding='utf8', newline='\n') as handle:
            handle.write(value)
    print(json.dumps(dict(report=str(outputs[1]), training_qualified=train_ok, new_updates=u, evaluation_qualified=result['evaluation_execution_qualified'], health=health, decision=decision, goal_complete=False), ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
