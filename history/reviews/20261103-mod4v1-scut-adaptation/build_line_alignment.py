"""Append a current source-line disposition without rewriting historical evidence.

Only verified text is read. Source text already in Git is referenced, not copied.
The output is a traceability index, not a claim of native branch coverage.
"""
import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import yaml

REPORT = Path(__file__).resolve().parent
REPO = REPORT.parents[2]
CODE = REPO / 'project/isaac/mod4v1_scut'
SOURCE = json.loads((CODE / 'SOURCES.json').read_text(encoding='utf-8'))
SOURCE['files'].update(json.loads((CODE / 'SOURCES_EXTENSION.json').read_text(encoding='utf-8'))['files'])
BASE_METHODS = ast.literal_eval(next(n.value for n in ast.parse((CODE/'upstream.py').read_text()).body
    if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'BASE_METHODS' for t in n.targets)))
RULES = {}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def target(file, symbol=None, anchor=None):
    path = CODE / file
    text = path.read_text(encoding='utf-8-sig')
    start, end = 1, len(text.splitlines())
    if symbol:
        nodes = [n for n in ast.walk(ast.parse(text)) if isinstance(n, (ast.FunctionDef, ast.ClassDef))
                 and n.name == symbol]
        if len(nodes) != 1:
            raise ValueError(('ambiguous target', file, symbol))
        start, end = nodes[0].lineno, nodes[0].end_lineno
    if anchor:
        candidates = [i for i, line in enumerate(text.splitlines(), 1)
                      if start <= i <= end and anchor in line]
        if len(candidates) != 1:
            raise ValueError(('ambiguous anchor', file, symbol, anchor, candidates))
        start = end = candidates[0]
    return dict(path=path.relative_to(REPO).as_posix(), line=start, end_line=end, symbol=symbol,
                precision='exact_statement' if anchor else 'function_or_file')


def rule(name, disposition, reason, targets, tests=(), profiles='both', native='pending'):
    RULES[name] = dict(disposition=disposition, reason=reason, targets=targets,
                       cpu_checks=list(tests), profiles=profiles, target_native=native)
    return name


def setup_rules():
    rule('comment', 'non_executable', '原空白/注释/文档字符串保留在固定来源；不伪造目标执行语句。',
         [target('upstream.py', 'source_path')], native='not_applicable')
    rule('module', 'module_binding', 'SCUT导入由SHA校验的AST绑定或原命令模块加载替代；不实例化原机器人。',
         [target('upstream.py', 'load_functions'), target('commands.py', 'build_command_cfg')])
    rule('base_exact', 'exact_ast_reference', 'BASE_METHODS原AST函数体和原行号未改；输入由MOD4桥接，具体分支不等于均已动态执行。',
         [target('upstream.py', 'bind_base_functions')], ['validate.test_reward_formula_and_one_dt',
         'review_tests.test_all_26_enabled_base_terms_against_independent_numpy_equations'])
    rule('done_exact', 'exact_ast_plus_model_guards', '原>1N/40deg/连续20controls/max-1终止；V14无云台接触集合按MOD4替换，closure/mimic/非有限立即重置。',
         [target('upstream.py', 'bind_base_functions'), target('sdk.py', 'resolve_done')],
         ['parity_tests.test_contact_and_orientation_need_twenty_consecutive_controls',
          'parity_tests.test_duration_reset_is_per_environment_and_hard_guards_are_immediate',
          'parity_tests.test_timeout_uses_original_maximum_minus_one_and_wall_is_not_failure'])
    rule('state_exact', 'exact_ast_reference', '状态类原AST加载；trained_stair关闭状态机，jump270启用Airborne/StepUp/Stair；JumpTakeoff仅可选CPU分支。',
         [target('upstream.py', 'state_classes'), target('rewards.py', 'ScutRewards')],
         ['validate.test_all_optional_reward_types_execute', 'review_tests.test_scan_state_is_advanced_after_current_reward'],
         'trained_stair:disabled; jump270:Airborne/StepUp/Stair only')
    rule('state_visual', 'disabled_visual', '状态图标仅可视化，本入口未调用；不得标成原生执行。',
         [target('upstream.py', 'state_classes')], native='not_selected')
    rule('assist', 'disabled_assist', '外力/速度助推关闭，JumpTakeoff未选中；仅保留固定原函数来源。',
         [target('config.py', 'reward_config', "values['jump_takeoff_state_machine_cfg'].setdefault('assist', {})['enabled'] = False")],
         profiles='neither', native='not_selected')
    rule('motors', 'robot_semantics_replaced', 'SCUT rear2没有MOD4同义关节，按四crank/hip真实限位替换；基础normalized square与Airborne弧度L1分别保留。',
         [target('rewards.py', 'motor_stop_terms')], ['review_tests.test_airborne_limit_keeps_upstream_l1_units',
         'review_tests.test_base_limit_uses_configured_boundary_ratio'], 'CLI weights disabled; optional current V14 CPU candidate')
    rule('kinematic', 'robot_geometry_replaced', '轮半径.0625、宽.02、hip锚点/圆柱姿态使用增强MOD4v1契约；保留原公式定义。',
         [target('rewards.py', '_get_wheel_motor_z_axis_align_error_sq'), target('acceptance.py', 'wheel_bounds')],
         ['validate.test_joint_names_and_motor_stop', 'validate.test_cylinder_bounds_and_strict_first_flight'])
    rule('height', 'sdk_sensor_binding', '保存配方无左右轮scanner，轮下地面均取机身实际ray；原高度语义保留，不输入解析平台GT。',
         [target('sdk.py', 'read_reward_scans'), target('rewards.py', '_get_current_wheel_ground_z_raw')],
         ['review_tests.test_saved_recipe_wheel_ground_uses_chassis_scan_and_invalid_fallback'])
    rule('forward', 'sdk_lazy_raycast_binding', '按第一次helper请求延迟查询，缓存当步命令方向；+5m/原max_distance/漏扫回退，重置环境单独播种。',
         [target('rewards.py', 'forward_scan'), target('sdk.py', 'read_forward_scan'), target('sdk.py', 'raycast')],
         ['parity_tests.test_forward_scan_is_lazy_at_first_use_and_keeps_resampled_direction',
          'review_tests.test_reset_scan_reseeds_new_pose_without_erasing_peer_delta'])
    rule('obs', 'sdk_observation_binding', 'actor28+mode7，critic28+velocity3+height1+mode7+priv39；clip后scale。噪声/延迟按原MOD4 D0-D7。',
         [target('sdk.py', 'observations')], ['parity_tests.test_critic_slot_order_and_sanitize_match_source_lines_3262_3295',
          'review_tests.test_pd_privileged_fields_follow_named_action_order'])
    rule('obs_history', 'once_per_observation', '动作历史在返回观测入口推进一次；getter缓存避免重复推进。',
         [target('rewards.py', 'finish_observation'), target('train.py', 'get_observations')],
         ['review_tests.test_repeated_observation_read_does_not_advance_lifecycle'])
    rule('obs_height_order', 'ordered_endpoint_binding', '有效height与observed height在observation状态更新前捕获，mode在其后捕获。',
         [target('sdk.py', 'observations', 'height_cmd = r._get_effective_height_cmd().clone()[:, None]'),
          target('sdk.py', 'observations', 'r.state_machine_manager.on_observation_step(r)')],
         ['parity_tests.test_critic_slot_order_and_sanitize_match_source_lines_3262_3295'])
    rule('obs_critic_slots', 'ordered_endpoint_binding', '纠正相同78维却字段串位：前28后依次velocity3/height1/mode7/priv39。',
         [target('sdk.py', 'observations', 'critic_blocks.update(root_lin_vel_b=r.robot.data.root_lin_vel_b,')],
         ['parity_tests.test_critic_slot_order_and_sanitize_match_source_lines_3262_3295'])
    rule('obs_raw', 'raw_before_clip_binding', '原raw最大值和非有限缓存，在裁剪/缩放/sanitize前采集，供原_get_dones读取。',
         [target('rewards.py', 'cache_raw_observations'), target('sdk.py', 'observations', 'r.cache_raw_observations(policy_blocks, critic_blocks)')],
         ['parity_tests.test_raw_observation_outliers_before_clip_reset_after_warmup'])
    rule('scale', 'clip_then_scale', '原保存obs_input_clip_cfg/scale_cfg/scale_streams决定每个块，policy/critic分别处理。',
         [target('config.py', 'observation_component')], ['review_tests.test_observation_scaling_respects_stream_selection'])
    rule('command', 'source_command_timing', '完整SpecialModeUniformVelocityCommand原模块复用；奖励尾部推进一次，V13同步覆盖结果；height按counter增长采样。',
         [target('commands.py', 'RewardTailCommand'), target('rewards.py', '_resample_custom_cmd'),
          target('rewards.py', '_on_command_updated')],
         ['parity_tests.test_real_reward_tail_uses_old_command_then_advances_once_and_samples_height',
          'parity_tests.test_v13_inherited_hook_syncs_state_override_into_generator'])
    rule('command_exact', 'exact_module_reference', '原命令模块完整SHA/blob引用；selected SpecialMode类及SDK父类CPU时序测试，另一个LinearStanding类未选中。',
         [target('commands.py', 'build_command_cfg')], ['parity_tests.test_original_command_class_and_sdk_parent_methods_on_cpu'])
    rule('v13_sync', 'exact_ast_reference', 'V13实际继承的_sync_command_generator_command原AST载入，在状态机覆盖后调用。',
         [target('upstream.py', 'bind_base_functions'), target('rewards.py', '_on_command_updated')],
         ['parity_tests.test_v13_inherited_hook_syncs_state_override_into_generator'])
    rule('contact_base_overridden', 'superseded_by_v14', '基类contact集合不是最终集合；V13/V14再次覆盖。按V14含导轮语义映射MOD4实际body。',
         [target('rewards.py', 'ScutRewards', 'self._undesired_contact_link_idx = indices(robot.body_names, STRUCTURAL_BODIES+GUIDE_BODIES)')],
         ['parity_tests.test_v14_subclass_guide_contact_override_reaches_reward_and_strict_support'])
    rule('contact_v14', 'robot_contact_names_replaced', '最终V14有害接触含guide：MOD429个非轮body；无gimbal终止分支为chassis+8guides。原有gimbal rough仅gimbal终止不适用于本模型。',
         [target('rewards.py', 'ScutRewards', 'self._reset_contact_link_idx = indices(robot.body_names, (\'chassis\',)+GUIDE_BODIES)'),
          target('config.py', 'reward_config', "values['use_gimbal'] = False")],
         ['parity_tests.test_v14_subclass_guide_contact_override_reaches_reward_and_strict_support'])
    rule('construct', 'mod4_constructor_binding', '原SCUT资产/关节/actuator/DR构造替换为增强MOD4v1与原共享PD/DC/D0-D7；不是同物理MDP。',
         [target('train.py', 'main'), target('sdk.py', 'configure'), target('rewards.py', 'ScutRewards')],
         ['validate.test_joint_names_and_motor_stop'])
    rule('reset', 'mod4_ground_reset_and_state_reset', 'MOD4 ground-start重置；原状态窗口/duration/动作历史按env清理，实际reset后刷新扫描；无原air/predefined倒地重置。',
         [target('sdk.py', 'install_hooks'), target('rewards.py', 'reset'), target('rewards.py', 'refresh_reset_scans')],
         ['validate.test_termination_and_selected_reset', 'review_tests.test_reset_clears_episode_clock_only_for_selected_env'])
    rule('action', 'mod4_actuator_queue_binding', '六动作按名字绑定crank/hip/wheels；保留MOD4 .5rad腿/10rad_s轮目标、PD/DC/物理延迟队列；不是SCUT actuator等价。',
         [target('train.py', 'environment_settings'), target('train.py', 'main'), target('rewards.py', 'ScutRewards')],
         ['validate.test_joint_names_and_motor_stop'])
    rule('gimbal', 'absent_robot_mechanism', 'MOD4无gimbal；不绑定假关节，use_gimbal=False，V14 gimbal覆盖/控制/奖励不选中。',
         [target('config.py', 'reward_config', "values['use_gimbal'] = False")], profiles='neither', native='not_selected')
    rule('terrain', 'explicit_course_substitution', '原rough generator/按地形command-height覆盖/边界reset没有移植到单270mm场地。manager无generator元数据时禁用；按V13 fallback保留基础命令。不是完整rough训练。',
         [target('sdk.py', 'spawn_course'), target('config.py', 'command_recipe'), target('rewards.py', 'get_terrain_name_mask')],
         ['parity_tests.test_original_command_distribution_not_fixed_point_six_for_saved_recipe'])
    rule('height_special', 'disabled_height_mode_branch', '保存special velocity modes没有height_wave/height_step/height_range，jump permission关闭；仅基础height sampler与state override启用。',
         [target('rewards.py', 'resample_height'), target('rewards.py', '_get_effective_height_cmd'), target('config.py', 'command_recipe')],
         ['parity_tests.test_real_reward_tail_uses_old_command_then_advances_once_and_samples_height'])
    rule('unused_observations', 'unselected_observation_algorithm', '本配方是单帧普通PPO actor35/critic78；原history/NP3O/legacy/scan-dot等接口未选中。',
         [target('config.py', 'runner_config'), target('sdk.py', 'observations')], native='not_selected')
    rule('debug', 'diagnostics_replaced', 'SCUT debug/marker/trace输出未调用；本适配记录分项episode日志与独立strict快照，不当作算法等价证据。',
         [target('sdk.py', 'log_reset'), target('sdk.py', 'snapshot')], native='not_selected')
    rule('train', 'rsl5_training_adapter', '普通PPO配方由保存YAML读取，RSL5分离actor/critic与TensorDict；rollout→GAE→update，完整原子保存。CLI/日志/预算由本入口接入。',
         [target('train.py', 'main'), target('train.py', 'build_runner'), target('checkpoint.py', 'save')],
         ['validate.test_real_rsl_rollout_gae_update_save_restore'])
    rule('train_clocks', 'source_initial_episode_clock', '原learn(init_at_random_ep_len=True)映射到trained_stair首次随机clock；jump270显式从0开始。',
         [target('train.py', 'initialize_episode_lengths')], ['parity_tests.test_original_random_episode_clock_only_for_saved_training_profile'])
    rule('train_progress', 'source_iteration_binding', '原training iteration同步到special command scheduler；恢复时同步已保存iteration。rough height curriculum未启用。',
         [target('train.py', 'set_training_iteration'), target('checkpoint.py', 'restore')])
    rule('wrapper', 'source_timeout_semantics', '原wrapper返回timeout bootstrap保留；任务失败可与timeout共存，MOD4强制reset除外。返回观测只转换一次。',
         [target('train.py', 'ScutVecEnv'), target('sdk.py', 'resolve_done')],
         ['parity_tests.test_source_timeout_bootstrap_with_task_failure_but_not_mandatory_reset'])
    rule('restore', 'strict_new_interface_restore', '旧H1/V1输入或字段语义不兼容；不扩维/不丢Adam。FULL_V2完整恢复学习与随机流后一次fresh物理reset。',
         [target('checkpoint.py', 'restore')], ['validate.test_real_rsl_rollout_gae_update_save_restore'])
    rule('ppo', 'saved_ppo_recipe', '保存agent.yaml中的普通PPO配方映射RSL5，未选其它算法类；actor/critic各自读取hidden_dims。',
         [target('config.py', 'runner_config')], ['review_tests.test_runner_uses_separate_actor_and_critic_dimensions'])
    rule('saved_reward_config', 'saved_reward_recipe', 'trained_stair原权重/helper；jump270显式改state/scan阈值并加2项Stair奖励，不能称原配置不变。',
         [target('config.py', 'reward_config')], ['review_tests.test_reward_recipe_counts_are_explicit'])
    rule('saved_command_config', 'saved_command_recipe_with_task_override', 'trained_stair原ranges/heading/special/standing/resample，jump270恒速.6/0/0明确覆盖。',
         [target('config.py', 'command_recipe'), target('commands.py', 'build_command_cfg')],
         ['parity_tests.test_original_command_distribution_not_fixed_point_six_for_saved_recipe'])
    rule('current_config', 'separate_current_branch', '当前V14源码配置与公开已训练YAML不同；仅current_airborne_config抽取候选分支，未冒充两CLI profile启用。',
         [target('config.py', 'current_airborne_config'), target('config.py', 'reward_config')],
         ['validate.test_optional_current_config_is_separate'], 'optional CPU candidate')


def symbols(text):
    tree = ast.parse(text)
    nodes = sorted((n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))),
                   key=lambda n: n.end_lineno-n.lineno, reverse=True)
    result, docs = {}, set()
    for node in [tree, *nodes]:
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
            docs.update(range(node.body[0].lineno, node.body[0].end_lineno+1))
    for node in nodes:
        for line in range(node.lineno, node.end_lineno+1):
            result[line] = node.name
    return result, docs


def yaml_paths(text):
    result = {}
    def walk(node, prefix):
        if isinstance(node, yaml.MappingNode):
            for key, child in node.value:
                name = prefix+[key.value]
                for line in range(key.start_mark.line+1, child.end_mark.line+2):
                    result[line] = '.'.join(name)
                walk(child, name)
        elif isinstance(node, yaml.SequenceNode):
            for i, child in enumerate(node.value):
                walk(child, prefix+[str(i)])
    walk(yaml.compose(text), [])
    return result


def classify(key, line, name, config_path):
    if key in ('airborne', 'jump_takeoff', 'step_up', 'stair', 'state_base', 'state_manager'):
        if key == 'airborne' and name == '_get_rear2_rear1_joint_limit_terms': return 'motors'
        if 'marker' in name: return 'state_visual'
        if key == 'jump_takeoff' and 'assist' in name: return 'assist'
        return 'state_exact'
    if key in ('wheel_base', 'wheel_manager'): return 'module' if name == '' else 'state_visual' if 'marker' in name else 'state_exact'
    if key == 'commands': return 'command_exact'
    if key == 'terrain_commands': return 'terrain'
    if key == 'trained_agent': return 'ppo'
    if key == 'trained_env':
        top = config_path.split('.')[0]
        if top in ('commands',): return 'saved_command_config'
        if top in ('terrain','rough_terrain_generator_cfg','rough_terrain_command_overrides_cfg','rough_terrain_boundary_reset_cfg','rough_height_offset_curriculum_cfg'): return 'terrain'
        if 'gimbal' in config_path: return 'gimbal'
        if top in ('robot','events','sim','scene','decimation','action_scale','wheel_action_scale','action_space'): return 'construct'
        if 'scanner' in top: return 'height'
        if top in ('predefined_reset_air','predefined_reset_ground','reset_random') or top.startswith('reset_'): return 'reset'
        if 'obs' in top or top in ('state_space','observation_space'): return 'obs'
        return 'saved_reward_config'
    if key == 'current_cfg': return 'current_config'
    if key == 'ppo_cfg': return 'ppo'
    if key in ('train','cli'):
        if name == '_load_policy_for_finetune': return 'restore'
        if name == '_notify_env_training_progress': return 'train_progress'
        if key == 'train' and line == 275: return 'train_clocks'
        return 'train'
    if key == 'vec_wrapper': return 'wrapper'
    if key == 'parent_env':
        if name == '_sync_command_generator_command': return 'v13_sync'
        if 48 <= line <= 54: return 'contact_v14'
        if name == '_on_command_updated': return 'command'
        return 'debug' if 'marker' in name else 'terrain'
    if key == 'current_env':
        if name == '__init__':
            if 84 <= line <= 86: return 'train_progress'
            if 88 <= line <= 90: return 'terrain'
            if 118 <= line <= 145: return 'contact_v14'
            if 93 <= line <= 106 or 146 <= line <= 204 or line == 206: return 'gimbal'
            if line == 87 or line >= 207: return 'debug'
            return 'construct'
        if 'gimbal' in name or name == '_get_ctrl_mode_obs_raw': return 'gimbal'
        if 'rough_' in name: return 'terrain'
        if name in ('set_training_progress','_get_training_iteration','_sync_command_generator_training_iteration','get_extrapolated_training_iteration','get_training_progress_steps_per_iteration'): return 'train_progress'
        if name in ('_on_command_updated','_postprocess_reward_terms'): return 'gimbal'
        if name in ('_get_dones',): return 'terrain'
        if name in ('_get_observations','_reset_idx'): return 'debug'
        if name in ('_apply_action','_custom_reset_random'): return 'gimbal'
        if name == '_resolve_names_to_indices': return 'construct'
        if name == '_validate_v14_bookkeeping': return 'construct'
        return 'debug'
    if key != 'base_env': raise ValueError(('unknown source', key))
    if 2098 <= line <= 2110: return 'contact_base_overridden'
    if name == '_get_observations':
        if 3107 <= line <= 3108: return 'obs_history'
        if 3123 <= line <= 3131: return 'obs_height_order'
        if 3262 <= line <= 3295: return 'obs_critic_slots'
        if 3170 <= line <= 3185 or 3220 <= line <= 3241: return 'obs_raw'
        if line in (3296,3330,3331,3368): return 'obs'
        if line == 3363: return 'debug'
        if line >= 3297: return 'unused_observations'
        return 'obs'
    if name == '_get_rewards' and 4043 <= line <= 4051: return 'command'
    if name in ('_get_dones','_apply_termination_duration','_clear_termination_duration_buffers'): return 'done_exact'
    if name in BASE_METHODS: return 'base_exact'
    if name == '_get_rear2_rear1_joint_limit_terms': return 'motors'
    if name in ('_get_wheel_motor_z_axis_align_error_sq','_get_height_measure_wheel_radius'): return 'kinematic'
    if name in ('_get_dynamic_wheel_forward_scan_points','_get_wheel_forward_scan_points','_get_wheel_forward_stair_scan_points','_get_wheel_forward_spatial_height_diffs_raw','_get_wheel_forward_scan_cfg','_is_wheel_forward_scan_enabled'): return 'forward'
    if name in ('_get_scanner_ground_height','_get_current_wheel_ground_z_raw','_get_wheel_relative_ground_heights_raw','_update_ground_height_estimate','_get_wheel_body_height','_use_raycast_height'): return 'height'
    if name in ('_get_effective_height_cmd','_get_observation_height_cmd'): return 'height_special'
    if name in ('_on_command_updated','_resample_custom_cmd','_force_resample_commands','_before_state_machine_command_updated','_after_state_machine_command_updated'): return 'command'
    if name in ('_postprocess_reward_terms','_build_state_machine_manager','_update_height_reward_airborne_state'): return 'state_exact'
    if name in ('__init__','_setup_scene','_find_contact_sensor_indices','_init_static_index_layouts','_get_left_right_leg_joint_pair_indices'): return 'construct'
    if name in ('_get_dynamic_priv_obs','_get_static_priv_obs','_get_privileged_extra_obs','_init_privileged_extra_obs_layout','_build_material_mapping','_get_material_indices','_get_body_material_for_link','_get_wheel_contact_force_for_link','_get_body_mass_scale_tensor','_get_delay_time_lag_obs','_get_body_material_tensor','_get_body_masses_tensor','_get_body_inertias_tensor','_get_robot_physx_view','_get_privileged_extra_body_indices','_get_privileged_extra_inertia_body_indices','_resolve_name_patterns_to_indices','_select_entity_features','_get_policy_extra_obs_blocks','_get_critic_extra_obs_blocks','_get_jump_takeoff_extra_obs_raw','_encode_joint_pos_obs','_get_task_flag_obs_raw','_get_policy_task_flag_obs_raw'): return 'obs'
    if name in ('_clip_obs_component','_scale_obs_component','_clip_scale_critic_component','_get_scale_alias'): return 'scale'
    if name in ('_pre_physics_step','_apply_action','_update_obs','_decode_leg_policy_actions','_split_policy_actions','_low_pass_action_filter','_value_constrain','_inverse_kinematics','_apply_spring'): return 'action'
    if name in ('_reset_idx','_custom_reset_random','_apply_root_state_uniform_vel_b','_get_randomize_params','_init_episode_length','_range_pair_as_float') or 'reset' in name or 'heading_target' in name or 'axis_aligned' in name: return 'reset'
    if 'terrain' in name: return 'terrain'
    if 'height_wave' in name or 'special' in name or 'height_command' in name or 'permission' in name or 'jump_takeoff' in name or name == '_cfg_value': return 'height_special'
    if 'debug' in name or 'marker' in name or 'print' in name or name.startswith('fmt_') or name in ('_tensor_max_abs','_resolve_yaw_rate_to_arrow'): return 'debug'
    if 'legacy' in name or 'history' in name or 'frame_mask' in name or 'np3o' in name or name in ('get_privilaged_obs','_get_scan_dot_obs','_pad_flat_features'): return 'unused_observations'
    if name == '' or name.startswith('Wheelbipe'): return 'module'
    raise ValueError(('unclassified function', key, name, line))


def main():
    setup_rules()
    outputs = [REPORT/name for name in ('LINE_ALIGNMENT.jsonl','LINE_ALIGNMENT_RULES.json','LINE_ALIGNMENT_SUMMARY.json')]
    if any(path.exists() for path in outputs):
        raise FileExistsError('Append a new revision instead of replacing line evidence')
    records, by_rule, by_source = [], Counter(), {}
    for key, row in SOURCE['files'].items():
        raw = Path(row['path']).read_bytes()
        assert sha(raw) == row['sha256'], key
        assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'], key
        text = raw.decode('utf-8-sig')
        owner, docs = symbols(text) if row['path'].endswith('.py') else ({}, set())
        paths = yaml_paths(text) if row['path'].endswith('.yaml') else {}
        by_source[key] = dict(**row, physical_lines=len(text.splitlines()))
        for number, textline in enumerate(text.splitlines(), 1):
            name = owner.get(number, '')
            category = classify(key, number, name, paths.get(number,''))
            if not textline.strip() or textline.lstrip().startswith('#') or number in docs:
                category = 'comment'
            rec = dict(source=key, line=number, symbol=name, config_path=paths.get(number),
                       line_SHA256=sha(textline.encode('utf-8')), rule=category)
            if category in ('base_exact','done_exact','state_exact','v13_sync','command_exact'):
                # Executed code remains at this verified external source line;
                # the rule also points to its local loader and adapted callers.
                rec['referenced_implementation'] = dict(path=row['path'], git_path=row['git_path'], line=number)
            records.append(rec); by_rule[category] += 1
    # Validate check names as real test functions, without rerunning tests.
    for item in RULES.values():
        for check in item['cpu_checks']:
            file, name = check.split('.')
            target(file+'.py', name)
    outputs[0].write_text(''.join(json.dumps(r, ensure_ascii=False, separators=(',',':'))+'\n' for r in records), encoding='utf-8')
    outputs[1].write_text(json.dumps(RULES, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    summary = dict(captured_at=datetime.now(timezone.utc).isoformat(), source_commit=SOURCE['commit'],
        source_files=by_source, physical_rows=len(records), unique_source_line_keys=len({(r['source'],r['line']) for r in records}),
        by_rule=dict(by_rule), sources=20, every_physical_line_has_disposition=True,
        dynamic_line_coverage_claim=False, native_executed=False, source_text_copy=False,
        historical_LINE_MAP_preserved=True,
        files=[dict(path=str(p),bytes=p.stat().st_size,SHA256=sha(p.read_bytes())) for p in outputs[:2]])
    outputs[2].write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(rows=len(records), rules=len(RULES), by_rule=dict(by_rule))))


if __name__ == '__main__':
    main()
