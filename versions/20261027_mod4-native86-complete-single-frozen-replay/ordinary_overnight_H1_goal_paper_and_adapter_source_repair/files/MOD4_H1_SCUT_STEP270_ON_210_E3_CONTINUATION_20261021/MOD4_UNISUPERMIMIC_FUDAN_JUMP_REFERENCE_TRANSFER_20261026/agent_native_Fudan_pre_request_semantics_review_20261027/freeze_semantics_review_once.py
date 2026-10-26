"""Freeze existing source-only audit; never invokes reference generation or models."""
from pathlib import Path
import hashlib, json, datetime

D = Path(__file__).resolve().parent
J = D.parent
T = J.parent
B = T / 'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/e2'
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, value):
    with (D / name).open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)

v = json.loads((D / 'reports/SELECTED_NATIVE_REFERENCE_PHASE_NUMBERS_V2_ACTUAL.json').read_bytes())
partial = D / 'reports/SELECTED_NATIVE_REFERENCE_PHASE_NUMBERS_ACTUAL.json'
try:
    json.loads(partial.read_bytes())
    partial_status = 'unexpectedly_valid'
except json.JSONDecodeError as e:
    partial_status = dict(error_type=type(e).__name__, message=str(e), line=e.lineno, column=e.colno)

save('reports/READER_FAILURES_AND_CORRECTIONS_ACTUAL.json', dict(
    source_only=True,
    V1=dict(status='failed_partial_report_preserved_byte_unchanged', script='reference_phase_numeric_table_once.py',
            output=str(partial), SHA=H(partial), failure='numpy.bool_ request value was not JSON serializable; TypeError during json.dump',
            traceback_note='Original terminal traceback belongs to the original tool history; this is a labeled diagnostic, not a recreated raw traceback.',
            partial_JSON_reader_result=partial_status),
    V2=dict(status='completed', script='reference_phase_numeric_table_V2_reader_fix_once.py',
            exact_reader_fix='request=100<=f<180 -> request=bool(100<=f<180)',
            report='reports/SELECTED_NATIVE_REFERENCE_PHASE_NUMBERS_V2_ACTUAL.json',
            no_original_overwrite=True),
    source_lookup_errors_preserved=[
        dict(kind='incorrect_guessed_source_path', path=str(J/'source/jump/envs/wheel_legged/wheel_legged_config.py'), resolution='Used existing source/jump/wheel_legged_gym/envs/base/legged_robot_config.py and actual capture source; no guessed file created.'),
        dict(kind='incorrect_guessed_source_path', path=str(J/'source/jump/envs/wheel_legged/wheel_legged.py'), resolution='No file found or used; no unsupported source claim.'),
        dict(kind='incorrect_reference_text_subdirectory', path=str(J/'actual_72_reference_text/upstream_actual_default_dt_standing_jump'), resolution='Located existing nested reference_capture/upstream_actual_default_dt_standing_jump; no original modified.')],
    no_new_physics_actor_training_or_model_failure=True))

paths = [
    B/'source/supermimic_reference_adapter_v1.py', B/'source/own_usd_closed_chain_ik_v1.py',
    B/'source/h1_supermimic_bridge_v1.py', B/'source/supermimic_vendor_v2/learner.py',
    B/'h1_step270_sdk_runtime_candidate.py',
    B/'reference/H1_PARTIAL_JUMP_NATIVE_REFERENCE_PACKED73_PHASE_V3.json',
    J/'agent_reference_retarget_cpu/retarget_saved_canonical_actual_Fudan_CPU_v2.py',
    J/'agent_reference_retarget_cpu/ACTUAL_FUDAN_CONSTRAINED_RETARGET_V2_1793005471832546700/ACTUAL_CONSTRAINED_RETARGET_CPU_RESULT.json',
    J/'agent_reference_retarget_cpu/ACTUAL_FUDAN_TO_OWN_STATIC_RETARGET_1793004790656605900/upstream_actual_default_dt_standing_jump_CANONICAL_TASKSPACE_DEMO.json',
    J/'root_Fudan_SuperMimic_objective_source_CPU_20261026/ACTUAL_SOURCE_TASK_DISTANCE_ALIAS_AND_HEIGHT_GRADIENT_CPU.json',
    J/'source/mujoco/python_tools/onnx_mj_chuanlian.py',
    J/'actual_72_reference_text/reference_capture/upstream_actual_default_dt_standing_jump/HEADLESS_REVIEWED_AST_SOURCE.py',
    J/'actual_72_reference_text/reference_capture/upstream_actual_default_dt_standing_jump/REFERENCE_CASE_SUMMARY_ACTUAL.json',
    T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026/payloads/h1/job0/assets/import_contract.json',
]
lineage=[]
for p in paths:
    if p.suffix.lower() not in ('.py','.json'):
        raise AssertionError('Only approved source/small JSON inputs may be hashed')
    lineage.append(dict(path=str(p), exists=p.is_file(), **(dict(bytes=p.stat().st_size, SHA=H(p)) if p.is_file() else dict(status='missing_path_not_substituted'))))
save('reports/SOURCE_LINEAGE_SHA_ACTUAL.json', dict(source_only=True, inputs=lineage,
    NPZ_PT_raw_USD_not_read_or_hashed=True, existing_reference_JSON_only=True,
    no_static261_fixture_rerun=True))

text = '''参考语义审计已冻结。只读取本机源码、既存参考 JSON 和旧报告，并对选定 20 个年龄行调用实际 NumPy reference adapter；没有读取 PT/raw/NPZ，没有 actor、物理、SDK、GPU、SSH、训练或 Git 操作。V1 的 NumPy bool 序列化错误、未完成 JSON 和 V2 修复后的 JSON/CSV 全部保留。未实施任何采样、奖励、输入、年龄、重置或动作改动。本交付是 source-audit，不是新算法或 PPO 辅助损失方案。

已排除的解释：

- 控制年龄映射为 reference_time = age*0.01-0.5；源片段从源时间 1.0s 开始，因此 age100 对应源 1.5s，age136 对应源 1.86s。这里只有平移，没有时间拉伸，导数缩放为 1。选定内点 Z/Vz 导数误差上界 3.91e-14，q/dq 为 8.74e-13。不能据此修一个并不存在的统一速度缩放错误。
- 90% attenuation 作用于 retarget 的相对轮端 task-space excursion，随后做非线性闭链 IK，最终 qd 从最终 q 对同一 0.01s 时间求导。它不是把 q 乘 0.1 却漏乘 dq。保留的左右轮高度差及 root 高度另由记录的轮底位移与本机碰撞 FK 重建；不应把这理解成所有自由度等比例缩小。
- age0..99 的受约束 q/qd 均为零，Z 约 0.337742m，未要求提前大幅下蹲或起跳。这个 Z 与 import_contract.spawn_height_m=0.337742301121 一致，不能从渲染 collider 中心反推初始 root 高度错误。age0..49 为端点保持，Vz 仍是约 0.000158m/s 的端点导数，存在小的 hold-position/hold-velocity 不一致；量级不足以作为严重失稳的单独解释。

有源码与数值支持的适配差异：

1. 源是零前进命令的平地 standing jump，源 jump policy 从 1.5s 持续 0.55s 后回到 recover policy。映射到本机是 age100..155；本机 public request 是 age100..179，且 vx 命令为 0.8m/s。源 recover/平地回落 q/dq 在本机 request 尚未结束时继续参与参考。这是部分参考的语义覆盖差异，不是已经证明的力学不可能性。
2. age110/120/130/136 的 Z 分别约 .346812/.389550/.645754/.698570m，对应 Vz .230808/.727098/1.765357/.170566m/s。age136 后 goal 的 Z/Vz 两槽变零；surrogate 同时关闭这两项 demo cost，因此并非把身体奖励目标拉到地面零高度。但原参考的平地返回 q/dq、姿态和角速度仍继续。age145 的受约束 qd 最大约 6.4663rad/s。
3. post-apex 本机落台高度目标为 .337742+.27=.607742m，仅在 root X>.35m 后按 .0637m 过渡带激活。还未到台沿的 post-apex 状态没有这项直接高度梯度。旧已保存 objective/alias CPU 报告提供独立数值反证/佐证，此处没有重跑。
4. 本机 forward surrogate 要求从 age100 到145 用 smoothstep 前进 .65m，平均 1.444m/s、曲线最大速度 2.167m/s；public vx 命令为 .8m/s。假设从 X=0 且恰好按 .8m/s 移动，age143.75 才到 .35m 台沿，晚于源 apex136。命令不是实际速度上限，不能据此宣称必败，但多套目标确有不同时间安排。
5. actor 的 observation 为 invariant_features73 + previous_action6 + context49，不直接提供世界 X 或年龄；critic 另有 age/200。PartialReference 的单帧 goal 替代本机 analytic goal，XY/水平速度及不可辨识轮/导轮槽被屏蔽，post-apex 高度两槽也屏蔽。故 surrogate 使用的本机距离、落台区域与部分阶段信息没有在参考 goal 中同义表达。history 仍包含真实运动，不能扩大成“任何状态都不可区分”，也不能说缺距离是唯一根因。
6. 0.1 limb excursion 后仍保留约 .36m 的 root 升高，现有 261 帧静态 IK 成功只证明姿态/几何可拟合，没有证明这个压缩/伸展与起跳冲量动态自洽。最初未衰减的版本已有 90/201 帧拟合失败；不能盲目将 .1 改回 1，也不能把静态成功升级为可执行起跳。

下一步应忠实对齐用户指定的论文和官方开源流程，先由根核清输入/上下文、目标、时间与更新协议；本审计不预设 PPO 混合损失。参考适配的最小修复方向是明确 pre/request/post 三阶段任务覆盖与同义的 goal/objective 合约，在保留真实参考来源的前提下解决本机前进/落台目标和源 standing-jump/recover 的安排；任何输入槽复用或目标变化都须作为新版本审核与重新准入，不能热改已训策略后称为相同模型。端点 hold 的微小 Vz 一致性可单独修正，但不应把它当主因修复。动态可实现性仍 pending。

拒绝条件与限制：不因单次约 .54s 失败就归因唯一根因，不声称已找到收敛方案，不改原成功标准/物理/事件，不造前进或强制轨迹，不把外来平地跳参考当 MOD4 上台成功。当前审计不检查模型参数、不评估动作或实际动态。根在并行核对的论文 ξ 与动态 context、官方配置差异属独立源码审查；本报告不替代该结论。

数值证据为 reports/SELECTED_NATIVE_REFERENCE_PHASE_NUMBERS_V2_ACTUAL.json 与对应 CSV；真实 adapter/retarget/runtime/原始 teacher 源码及旧报告 SHA 见 reports/SOURCE_LINEAGE_SHA_ACTUAL.json。具体接线位置：adapter.py:405 时钟，425 goal，628 objective，700 phase；bridge.py:56 obs、59 analytic goal、85 critic；runtime.py:120 public request、179 vx；retarget.py:42 attenuation、52 root 重建。完整 SHA 索引为 FROZEN_FUDAN_PRE_REQUEST_SEMANTICS_SHA_INDEX.json。
'''
with (D/'FROZEN_SOURCE_AUDIT_HANDOFF.md').open('x', encoding='utf-8') as f:
    f.write(text)

rows=[]
for p in sorted(D.rglob('*')):
    if p.is_file() and p.name != 'FROZEN_FUDAN_PRE_REQUEST_SEMANTICS_SHA_INDEX.json':
        rows.append(dict(path=p.relative_to(D).as_posix(), bytes=p.stat().st_size, SHA=H(p)))
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
index=dict(schema='mod4.frozen_source_audit.complete_SHA_index.v1', frozen_at_UTC=stamp,
    frozen_directory=str(D), source_only=True, all_files_except_this_index=rows,
    total_files_excluding_index=len(rows), old_frozen_directories_untouched=True,
    status='frozen_for_parent_ordinary_supplement_archive_not_archived_by_helper',
    no_pending_execution_or_candidate_implementation=True,
    pending=['Paper/upstream fidelity review owned by root', 'Dynamic feasibility and causal attribution not tested'])
save('FROZEN_FUDAN_PRE_REQUEST_SEMANTICS_SHA_INDEX.json', index)
print(json.dumps(dict(frozen_at_UTC=stamp, index=str(D/'FROZEN_FUDAN_PRE_REQUEST_SEMANTICS_SHA_INDEX.json'),
    SHA=H(D/'FROZEN_FUDAN_PRE_REQUEST_SEMANTICS_SHA_INDEX.json'), files_excluding_index=len(rows),
    source_lineage_missing=[r['path'] for r in lineage if not r['exists']]), ensure_ascii=False))
