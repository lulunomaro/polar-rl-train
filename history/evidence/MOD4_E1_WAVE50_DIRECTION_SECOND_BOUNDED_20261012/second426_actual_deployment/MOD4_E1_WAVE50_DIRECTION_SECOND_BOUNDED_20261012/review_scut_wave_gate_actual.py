"""Read pinned public sources and saved full150 results; no physical replay or gate edit."""
from wave_direction_second_io import *

def main():
    scut=W/'MOD4_E1_G3_MATCHED_REVIEW_20261010'
    audit=json.loads((scut/'reports/SCUT_SOURCE_AUDIT_1791633510.json').read_bytes())
    pin='1a26356d6f591734d4f6f666f5cead1a6925da67';assert audit['commit']==pin
    wanted=('scripts/rsl_rl/train.py','source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py','source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env.py','pretrained/26_infantry/rough_rotation_stair/2026-07-30_09-16-27/params/env.yaml')
    sources=[];texts={}
    for name in wanted:
        row=next(x for x in audit['files'] if x['path']==name)
        p=Path(row['local']);raw=p.read_bytes();assert H(raw)==row['sha256'] and len(raw)==row['bytes']
        texts[name]=raw.decode('utf8')
        sources.append(dict(path=str(p),bytes=len(raw),sha256=H(raw),official_pinned_url=row['url']))
    train,base,v14,cfg=(texts[x] for x in wanted)
    assert 'runner.learn(num_learning_iterations=agent_cfg.max_iterations' in train
    assert 'delayed_terminate = self._apply_termination_duration(delayed_terminate)' in base
    assert 'immediate_terminate' in base and 'return terminate, time_out' in base
    assert 'rough_height_offset_curriculum_cfg:\n  enabled: false' in cfg
    assert 'termination_duration_steps: 20' in cfg and 'dt: 0.005' in cfg and 'decimation: 4' in cfg
    assert 'capped_iteration // max(interval, 1)' in v14
    plan=W/'polar-rl-train/history/plans/MOD4_RM_TERRAIN_TRAINING_REVISION.md';ptext=plan.read_text(encoding='utf8');assert '不造90/95/100晋级线' in ptext
    first=PRIOR/'reports/CANDIDATE150_COMPLETE_SCOPE_DECISION.json';decision=json.loads(first.read_bytes())
    direct=Path(decision['direct149_pair_review']);d=json.loads(direct.read_bytes())
    assert decision['all_four_actual_complete_errorfree_fullraw_reviewed'] and decision['candidate_forward_complete']==12 and decision['candidate_reverse_complete']==25
    assert decision['original1N_contact_matches_position'] and d['original1N_contact_matches_position_completions']
    value=dict(epoch=time.time(),passed=True,review_kind='pinned_source_and_saved_actual_contract_comparison_only',SCUT_pin=pin,pinned_local_sources_all_original_audit_SHA_exact=sources,official_web_primary_sources_also_read=True,
      SCUT_public_training=dict(continuous_runner_learn=True,ordinary_done_per_environment=True,numerical_safety_immediate=True,July30_ordinary_duration_control_steps=20,July30_control_seconds=.02,July30_ordinary_duration_seconds=.4,rough_height_schedule_available_in_code=True,July30_saved_height_schedule_enabled=False,no_MOD4_27_each_15s_tenwave_1N_200mm_graduation_contract_found_in_inspected_entry_config_done_paths=True,private_author_acceptance_unknown=True),
      MOD4_approved_plan=dict(path=str(plan),bytes=plan.stat().st_size,sha256=H(plan.read_bytes()),explicit_no_artificial_90_95_100_progression_line=True),
      MOD4_actual150=dict(decision_path=str(first),decision_SHA=H(first.read_bytes()),direct_path=str(direct),direct_SHA=H(direct.read_bytes()),forward_complete=12,forward_total=27,reverse_complete=25,reverse_total=27,ordinary=decision['terrain']['ordinary'] if 'terrain' in decision else 0,contact_position_completions_exact=True,forward_valid_incomplete_envs=d['pairs']['forward']['all_candidate_valid_incomplete_envs'],reverse_valid_incomplete_envs=d['pairs']['reverse']['all_candidate_valid_incomplete_envs'],not_qualified50=True),
      correction=dict(previous_assistant_27_each_as_hard_gate_overstated=True,all_samples_complete_is_strong_observed_evidence_not_automatic_universal_progression_gate=True,no_new_percentage_threshold_invented=True,whole_route_test_and_valid_failed_prefixes_retained=True,contact_required_before_after_not_every_control=True,initial_end_support_data_not_causal_training_proof=True),
      assessment=dict(mechanical_perfect_batch_progression_would_be_over_strict=True,latest_major_forward_residual_not_explained_solely_by_contact_threshold=True,15s_at_03_command_is_project_test_not_SCUT_standard=True,nominal_3_006422727m_path_over_03m_s_seconds=3.006422727/.3,nominal_time_not_dynamic_feasibility_certificate=True,training2m_route_vs3_006m_test_exposure_mismatch_previously_observed=True,performance_should_consider_directional_prefix_failure_severity_progression_and_use_case_not_single_percent=True),
      no_training_reward_DR_health_geometry_protocol_budget_or_old_result_mutation=True,no_new_GPU_evaluation_or_oldonce_replay=True)
    out=save('SCUT_WAVE_GATE_SOURCE_AND_ACTUAL_COMPARISON.json',value)
    report=D/'SCUT_WAVE_GATE_COMPARISON.md'
    with report.open('x',encoding='utf8') as f:
        f.write('''# 华南虎与当前起伏验收的对照

结论：把正向27/27和倒退27/27当成继续训练或晋级的机械硬门槛，确实过严，也不符合本项目已批准RM003“不造90/95/100晋级线”的规定。此前助手把全部样本完成的强证据说成了硬门槛，现明确纠正；旧话与旧结果保留，不改原false，不新增另一条百分比线。

本次逐字SHA核验华南虎公开固定提交1a26356的训练入口、V14、父任务dones及July30实际保存env参数；官方固定版本网页也读取。公开入口持续runner.learn，普通失败逐环境reset。July30配置普通终止有20个20ms控制步、即0.4s过滤；数值非有限/异常立即处理。公开路径没有我们的固定27+27、15秒十波、前后1N与200mm退出合同。不能由此推断作者私下没有最终考核，更不能虚构其成功率。源码有按iteration推进的高度课程，但该July30保存配置enabled=false，不能当作该模型实际自动调档证据。

当前完整150仍正向12/27、倒退25/27，全部四case原始数据已审；15个正向和2个倒退有效失败样本保持。位置完成和原1N前后两轮接触支撑完全一致，所以本轮没完成不是只被1N数值拦下。支撑判定没有要求整个波形每个控制步双轮都着地；不能凭该规则宣布正常瞬间卸载失败。原.4m接近、2.406422727m十波与.2m后支撑约3.006m，按.3m/s名义需要约10.02s，15秒有名义余量，但这不保证每个DR动力学样本可行，也不是华南虎标准。训练原2m route与全测试3.006m的暴露不匹配是已记录问题，不靠缩测试或延原窗口造成功。

必要保留：真实完整路线的能力定义、同一physicalepisode的有效进度、排除reset瞬移、真实前后轮支撑，以及ground/contact积分/COMlink/hardware/非有限/回调覆盖等数据与物理自洽合同。性能晋级综合正反方向、失败严重程度、有效前缀、实际任务用途与是否存在系统性残差；普通失败不能自动上升为整批学习故障。当前healthv3已经允许ordinary reset继续PPO，旧20261007全批零普通失败问题不能冒称仍在当前生效。

本次只做源码与已保存结果审查，没有修改活跃训练、DR/reward/健康阈值/几何/评测协议/预算，未重跑GPU。50mm当前仍存在明显正向残差；不因纠正100%硬门槛便称其合格或升70mm。官方RM70mm是峰谷高差，完整真实CAD范围另验收；50mm派生测试不替代全RM/MoE或永久抗遗忘。

完整路径、大小、SHA、固定版本URL及逐项事实见reports/SCUT_WAVE_GATE_SOURCE_AND_ACTUAL_COMPARISON.json。所有旧失败、成本和本次通信纠正与读者误目录查询保留；随本真实第二方向900s部署阶段归档，后续回执普通补充。
''')
    print(json.dumps(dict(report=str(report),evidence=str(out),mechanical27_each_hard_gate_overstated=True,current_forward12_reverse25_not_qualified=True,no_active_training_edit=True)))

if __name__=='__main__':
    try:main()
    except BaseException:save('SCUT_GATE_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),reader_only_no_GPU_or_budget_replay=True));raise
