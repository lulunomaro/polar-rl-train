"""Assemble reproducible acceptance evidence, including failed requirements."""
from datetime import datetime,timezone
from pathlib import Path
import json
import numpy as np
from fsm_paths import HERE,E0_SHA,JUMP_PATH
from fsm_io import put,sha256


def read(name):
    return json.loads((HERE/name).read_text(encoding='utf-8'))


def streaks(good):
    current=np.zeros(good.shape[1],dtype=int);best=current.copy()
    for sample in good:
        current=np.where(sample,current+1,0);best=np.maximum(best,current)
    return best.tolist()


def stair_rows():
    main='evidence/stair_r9_009m_contract'
    redo='evidence/r9_009m_stationary_restart'
    base=read(main+'/RESULT.json')['rows']
    replacements={r['id']:r for r in read(redo+'/RESULT.json')['rows']}
    out=[]
    for original in base:
        row=dict(replacements.get(original['id'],original))
        folder=redo if row['id'] in replacements else main
        with np.load(HERE/f'{folder}/traces/{row["id"]}.npz') as raw:
            physics=raw['physics'];trace=raw['reference_trace']
        stages=max(1,len(row['stage_crossed']))
        loaded=(trace[:,21:21+2*stages].reshape(-1,stages,2)>5.).all(2)
        recovered=np.isin(physics[:,1],(0,1,4))
        qualified=streaks(loaded & recovered[:,None])
        row['all_phase_support_passed']=bool(np.all(np.asarray(row['longest_bilateral_support_substeps'])>=row['required_support_substeps']))
        row['longest_e0_bilateral_support_substeps']=qualified
        row['passed']=bool(row['passed'] and np.all(np.asarray(qualified)>=row['required_support_substeps']))
        row['strict_support_400hz']=row['passed']
        row['evidence_case']=f'{folder}/cases/{row["id"]}.json'
        row['evidence_trace']=f'{folder}/traces/{row["id"]}.npz'
        # Historical summary field was sampled at the final control boundary.
        row['closure_at_final_control_boundary_mm']=row.pop('max_closure_mm')
        if row.get('restart'):
            assert row['restart_initial_state']['protocol']=='stationary settled-pose reset at riser'
            assert not any(row['restart_initial_state']['root_velocity'])
        out.append(row)
    assert len(out)==320 and len(replacements)==64
    return out


def main():
    stamp=datetime.now(timezone.utc).isoformat()
    candidate=read('CANDIDATE.json')
    rows=stair_rows()
    failures=[r for r in rows if not r['passed']]
    premature=[dict(id=r['id'],course=r['course'],speed=r['speed'],dr=r['dr'],
        precontact_active_samples=r['precontact_active_samples'],trace=r['evidence_trace'])
        for r in rows if r['precontact_active_samples'] and not r.get('force_at_s')]
    stair=dict(utc=stamp,overall_requirement_passed=False,physics_hz=400,force_threshold_n=5.,
        final_required_contiguous_substeps=160,post_handoff_support_required=True,
        continuous_double_final_deck_required=True,passed=sum(r['passed'] for r in rows),total=len(rows),
        nominal_passed=sum(r['passed'] for r in rows if not r['dr']),nominal_total=sum(not r['dr'] for r in rows),
        full_dr_passed=sum(r['passed'] for r in rows if r['dr']),full_dr_total=sum(bool(r['dr']) for r in rows),
        physical_no_fall=sum(r['physical_crossed'] and not r['failure'] for r in rows),
        failed=len(failures),unforced_precontact_violations=premature,rows=rows,
        source_checkpoint='evidence/fsm_r9/train/model_009m.pt',source_sha256=candidate['source_sha256'],
        export_identity='evidence/SELECTED_ACTOR_IDENTITY.json',
        reset_protocol='64 restart cases re-run from a settled pose at 2 mm riser clearance with exactly zero velocities; truth used only in reset.',
        full_dr_mapping='Full sampled ranges are ported to temporary MuJoCo parameters; material/restitution mappings are documented per row. This is not identical PhysX contact physics.',
        invalid_legacy_result='The old fixed-duration stop did not guarantee zero speed. Its one accepted case is retired; raw records remain archived.',
        closure_diagnostic='Control-boundary closure samples are reported honestly; they are not per-substep peak closure.')
    put(HERE/'FSM_STAIR_BENCHMARK.json',stair)

    flat60=read('evidence/flat60_r2/RESULT.json')
    ordinary=read('evidence/flat_r3/CORRECTED_SCORING.json')['rows']
    for folder in ('reverse_low_flat_fix','reverse_low_rough_fix'):
        replacement=read(f'evidence/{folder}/RESULT.json')['rows'][0]
        key=lambda r:(r['course'],r['height'],r['speed'],r.get('wz',0.))
        ordinary=[replacement if key(r)==key(replacement) else r for r in ordinary]
    cruise=read('evidence/cruise_fullspeed_r3/RESULT.json')
    hold=read('evidence/noise_filter_holdout_r2/RESULT.json')
    early=[r for r in hold['rows'] if r['course'] not in ('flat','rough_L9')]
    audit=dict(utc=stamp,overall_requirement_passed=False,
        cruise_structural_zero_leak=True,e0_sha256=E0_SHA,
        cruise_route_rule='CRUISE_E0 stair weight is exactly zero; operator veto is applied before action selection.',
        flat60=dict(passed=flat60['passed'],total=flat60['total'],source='evidence/flat60_r2/RESULT.json'),
        ordinary_flat=dict(passed=sum(r['passed'] for r in ordinary if r['course']=='flat'),total=16),
        ordinary_rough=dict(passed=sum(r['passed'] for r in ordinary if r['course']=='rough_L9'),total=16),
        ordinary_composition='30 unchanged retained cases plus two reverse-command repair rechecks; tracking and support metrics are separate.',
        fullspeed_cruise=dict(passed=cruise['passed'],total=cruise['total'],seconds_per_case=6.,
            stair_active_samples=cruise['precontact_active_samples'],rows=cruise['rows']),
        early_arm_holdout=dict(total=len(hold['rows']),zero_activation_cases=hold['zero_activation_cases'],
            initial_command_height_m=.39,seed=919,stair_approach_cases=len(early),
            minimum_stair_precontact_height_m=min(r['precontact_min_relative_height_m'] for r in early),
            precontact_active_samples=sum(r['precontact_active_samples'] for r in early),rows=hold['rows'],
            actor_independence='Before first stair activation, frozen E0 and the FSM are identical for the measured and selected stair actors.'),
        wider_stair_matrix_unforced_violations=premature,
        zero_false_positive_full_coverage_passed=not premature,
        contact_latency_requirement_passed=False,detector=read('DETECTOR.json'),
        native_probe_coarse_preactivation_count=read('evidence/fsm_r9/probe/PROBE.json')['premature_activation_frames'],
        native_audit_note='Native audit uses a coarse wheel-center boundary, not the CPU full-robot boundary. It is retained and is not a claim of native zero premature activation.')
    put(HERE/'PREMATURE_SQUAT_AUDIT.json',audit)

    jump_source='evidence/jump_20261122_131830/RESULT.json'
    jump=read(jump_source)
    for row in jump['rows']:
        with np.load(HERE/Path(jump_source).parent/(row['id']+'.npz')) as raw:
            samples=raw['jump_substeps']
        window=samples[:,0]<=row['main_flight_end_s']+.0001
        row['peak_riser_face_force_n']=float(samples[window,6].max())
        row['face_force_window']='Entire key press to first main-flight landing, including preparation.'
        row['passed']=bool(row['passed'] and row['peak_riser_face_force_n']<=5.)
    jump['passed']=sum(r['passed'] for r in jump['rows'])
    assert jump['passed']==5
    jump.update(utc=stamp,source=jump_source,jump_sha256=sha256(JUMP_PATH),
        criterion='Measured speed at key within 0.15 m/s; main-flight clearance; direct first landing; no >5 N front-riser assistance; cruise return without timeout.',
        evidence_runup='Start x=-5 m, platform front x=3.3 m, physical width=22 m.',
        functional_integration_passed=True,
        zero_microbounce_landing_proven=False,
        note='Earlier short-runup 2.8 command tests are not evidence of actual 2.8 m/s takeoff and are superseded.')
    put(HERE/'FSM_JUMP380_CHECK.json',jump)

    rounds=[]
    for tag in ('fsm_r2','fsm_r5','fsm_r9'):
        final=read(f'evidence/{tag}/train/FINAL.json')
        rounds.append(dict(tag=tag,ppo_updates=final['ppo_updates'],optimizer_steps=final['optimizer_steps'],
            seconds=final['elapsed_s'],target_dr=final['target_dr'],active_dr=final['active_dr'],
            safe_closed=read(f'evidence/{tag}/train/SAFE_CLOSED.json'),guard_exit=read(f'evidence/{tag}/train_EXIT.json')))
    from remote_manual_fsm import CODE
    inputs=read('evidence/fsm_r9/INPUTS.json')
    differences=[name for name in CODE if sha256(HERE/name)!=inputs[name]]
    assert not differences and sha256(HERE/'DETECTOR.json')==inputs['DETECTOR.json']
    training=dict(rounds=rounds,source_contract_differences=differences,
        latest_probe=read('evidence/fsm_r9/probe/PROBE.json'),latest_final=read('evidence/fsm_r9/train/FINAL.json'),
        final_gpu_inventory=read('evidence/GPU_FINAL_INVENTORY.json'),native_counters_are_not_cpu_acceptance=True)
    put(HERE/'evidence/TRAINING_CLOSURE.json',training)

    video=read('evidence/videos_final/FRAME_DECODE_AUDIT.json')
    smoke=read('evidence/PLAYER_SMOKE.json');layout=read('evidence/UI_LAYOUT_SMOKE.json')
    protection=read('evidence/PROTECTION_VERIFICATION.json')
    load=read('evidence/DECK_LOAD_SUBSTEPS.json')
    jump_details='\n'.join(f"| {r['course']} | {r['speed']:.1f} | {r['actual_speed_at_key_m_s']:.3f} | {r['peak_bilateral_tire_clearance_m']:.3f} | {'通过' if r['passed'] else '失败'} |" for r in jump['rows'])
    training_details='\n'.join(f"| {r['tag']} | {r['ppo_updates']} | {r['optimizer_steps']} | {r['seconds']:.3f} | {r['guard_exit']['own_gpu_process_released']} |" for r in rounds)
    wide=len(premature)
    report=f'''# MOD4v3 手工状态机统一控制实验报告

**总验收未通过，当前入口为实验候选，不能称为已毕业。** 生成时间：{stamp}。

已交付可运行代码、双启动器、12 图单窗口、确定性状态机、冻结 E0、专职上阶网络、两类大跳、GPU 训练与安全关闭记录、完整 CPU 证据以及四支原速视频。严格上阶为 **{stair['passed']}/{stair['total']}**，Full-DR 为 **{stair['full_dr_passed']}/{stair['full_dr_total']}**。连续双阶、全覆盖零提前下蹲、全部 20–40 ms 接手、台顶零微颤仍未达标。

## 实际入口与操作

- 根入口：`D:/claude2/fangzhen/Run_MOD4v3_ManualFSM_Unified_WASD.bat`
- 本目录入口：`Run_MOD4v3_ManualFSM_Unified_WASD.bat`
- W/S 前后，A/D 转向，Q/E 站高；1=1.2 m/s，2=2.8 m/s，滑杆最高 3.0 m/s。
- C 开关上阶；F 临时上阶；**W+V** 贴阶强起。松 W、按 S、关 C、松 F 均按同一个控制拍退出上阶。
- Space/J 大跳，R 复位。大跳建议站高 0.28 m，1.6 档距沿约 0.35 m、2.8 档约 0.70–0.85 m 按键。高台出生点已延长助跑。

## 可核验成绩

| 项目 | 结果 | 证据与限制 |
|---|---:|---|
| flat60 | {flat60['passed']}/60 | 独立完整轨迹；非承载指标替代 |
| flat / L9 常规跟踪 | {audit['ordinary_flat']['passed']}/16；{audit['ordinary_rough']['passed']}/16 | 30 例原轨迹 + 两例低姿倒车修复重检 |
| 0.8–3.0 m/s 关 C 巡航 | {cruise['passed']}/10 | 每例 6 s，上阶权重 0；平地 3.0 档末段实测约 2.997 m/s |
| 提前开 C 留出 | 40/40 触阶前零激活 | 其中 24 例上阶接近，初始站高指令 0.39 m，最低 {audit['early_arm_holdout']['minimum_stair_precontact_height_m']:.3f} m |
| 更宽矩阵防提前激活 | **未通过** | {wide} 例未按 V 的工况发生提前激活；见专项 JSON |
| CPU 严格上阶 | {stair['passed']}/320 | 80 名义 + 240 Full-DR；全阶面与 E0 接回后的连续承载分别核验 |
| CPU 物理越阶且无摔 | {stair['physical_no_fall']}/320 | 不能代替严格承载通过 |
| 大跳功能回归 | 5/5 | 实速、主腾空段、直接落台、无立面借力、交回巡航；不证明落地零微颤 |
| 启动器与窗口 | 12/12；布局通过={layout['passed']} | 实际 Tk 渲染 {layout['rendered_frames']} 帧；无越界控件；未用外部桌面工具逐个点击验证 |
| 原速视频 | {len(video['videos'])} 支，逐帧解码通过={video['passed']} | 1 帧对应 2 个 20 ms 控制拍；含失败，不能把有视频等同通关 |
| 受保护资产 | {protection['files']} 份哈希一致 | `evidence/PROTECTION_VERIFICATION.json` |

### 实速跳跃

| 地图 | 命令 m/s | 按键实速 m/s | 主腾空双轮净空 m | 功能结果 |
|---|---:|---:|---:|---|
{jump_details}

测试高台为 22 m 宽实体。起点 x=-5 m，平台前沿 x=3.3 m。旧短助跑的“2.8”只代表命令档，已明确废止其作为实速 2.8 的证据。新验收以按键时的真实 CoM 前速为准。跳跃在巡航→手工跳跃→巡航管线中验证；任意攀爬中打断跳跃没有被证明。

## 架构和合同

`ManualFSM` 只接收 obs35 和操作者意图，`StairExpert` 只接收 obs35+12×35 历史。没有运行期地图坐标、射线或台阶位置输入。世界真值用于复位、训练奖励、离线评分和 UI 提示。

巡航与上阶预备只调用冻结 SELECTED_E0；攀爬调用 100% E_stair；阶面过渡固定 8 拍/0.16 s；等待 0.40 s 后进入舒适站高。C 模式一直保留，避免自动在双阶中间关档。跳跃分别使用 R61 原地专家和 jump380_r10。左右对称化是精确 Z2 结构。E0 高度软限幅、速度校准保留在本目录。

共享 FSM、actor、GPU 环境、几何、探针与训练代码相对 R9 上传快照差异为 {differences}，DETECTOR 哈希一致。A–A 独立夹具踏面为 1.20 m，原完整 RM 地图保留测绘剖面。物理 400 Hz、腿 PD 100 Hz、轮 400 Hz、6 维 [-6,6] 动作以及原电机包络保留。移动跳复用发布版本的电机目标映射；原地跳与 E0/上阶使用各自已记录的映射。

## GPU 实际训练与关闭

| 轮次 | PPO | Adam | 实际秒 | 自身 GPU 进程已释放 |
|---|---:|---:|---:|---|
{training_details}

以上为各轮真实计数，不能把不同祖先快照的计数直接当作所选权重的训练步数。R9 前 3 轮仅预热 critic；每轮正式 PPO 前均有 600 步、0 优化器更新预检，守护与 SAFE_CLOSED 记录齐全。R6/R7/R8 是零更新预检，未作为 PPO 训练成绩。

R9 总预算 1200 s，实际 {rounds[-1]['seconds']:.3f} s。最终 target DR=1.0，实际 {training['latest_final']['active_dr']}/2048 个环境切入完整 DR，不能写成全部 2048 已完成 Full-DR 毕业。GPU 0/1 最终只读查询均为 13 MiB、0% 利用率。训练课程中的成功计数不是独立 CPU 成绩。原生粗边界提前激活计数：探针 {training['latest_probe']['premature_activation_frames']}，训练 {training['latest_final']['premature_activation_frames']}；它们未被隐藏，也不能与 CPU 完整几何边界指标混用。

## 失败定位及已纠正的评分问题

1. 400 Hz 接触中断是真实的：独立有符号法向载荷与评分器逐子步误差 {load['scored_normal_max_error']:.1f} N；台顶 {load['late_samples']} 样本中有 {load['late_load_missing_samples']} 个缺少双轮 >5 N，平均载荷约 70 N/轮。10 Hz 控制拍末取样会掩盖这些中断。高度 0.34/0.35/0.36 m 的对照未消除问题。
2. 旧 A–A 一例在 400 mm 窄沿驻住，却被“二级承载”记为通关。该结论已撤销；新评分要求进入 360/300 mm 末段顶面、足够承载并接回 E0。新原生完成条件也排除单纯驻沿。
3. 旧“零速重启”固定停车时长没有保证初速度为零，已重跑全部 64 例。新协议是复位专用的稳态姿态贴阶放置、2 mm 净距、全速度严格为零；不把运行中的状态改写交给策略。旧记录完整保留。
4. 最长任意相位承载与 E0 接回后的承载分列；深蹲专家长时间驻台不能冒充 E0 零微颤收官。四连杆 closure 字段为控制拍末诊断，未冒称 400 Hz 峰值。
5. 含噪传感下采用因果滤波与分支阈值，40 例留出清洁，但更宽矩阵仍有提前激活，部分接手超过 40 ms 或漏检。此问题尚未解决。
6. LQR/静态腿恢复教师、E0 恢复教师与 CPU 残差搜索均保留失败；这些控制器没有进入部署策略。

## 当前候选和交付状态

`weights/E_stair_r9_009m_selected.pt` 导出自 R9 九分钟快照，{candidate['selected_round_ppo_updates']} PPO / {candidate['selected_round_optimizer_steps']} Adam（本轮计数）。推理张量逐项位相等验证见 `evidence/SELECTED_ACTOR_IDENTITY.json`。原完整检查点 SHA：`{candidate['source_sha256']}`；轻量导出 SHA：`{candidate['sha256']}`。

选择该实验快照的依据是完整 CPU 矩阵中的相对表现；R9 最终快照的小对照仍未取得严格通过，未把最后保存等同最好。**当前 1/320 仍远低于要求，未达到或超越旧 83/308 基线；试验覆盖和评分协议也不完全相同。**

主要文件：`PREMATURE_SQUAT_AUDIT.json`、`FSM_STAIR_BENCHMARK.json`、`FSM_JUMP380_CHECK.json`、`evidence/videos_final/VIDEO_MANIFEST.json`、`evidence/TRAINING_CLOSURE.json`、`evidence/PROTECTION_VERIFICATION.json`。

继续工作需要优先解决：含 DR 的无误触/快速接触辨识、上阶后主动恢复直立、连续双阶末段推进，以及 CPU 刚性圆柱轮与箱面下的 E0 连续承载。当前不能标记总任务完成，也不宣称竞赛级毕业。
'''
    (HERE/'FINAL_FSM_REPORT.md').write_text(report,encoding='utf-8')
    put(HERE/'evidence/FINAL_DELIVERY_STATUS.json',dict(utc=stamp,overall_requirement_passed=False,
        stair_strict_passed=stair['passed'],stair_total=320,jump_functional_passed=5,jump_total=5,
        protected_assets_passed=protection['passed'],gpu_rounds_closed=all(r['guard_exit']['own_gpu_process_released'] for r in rounds),
        launcher_smoke_passed=smoke['passed'],ui_layout_passed=layout['passed'],all_video_frames_decoded=video['passed'],
        candidate=candidate,report='FINAL_FSM_REPORT.md'))
    print('Acceptance: stairs',stair['passed'],'/320; jump',jump['passed'],'/5; overall NOT GRADUATED')


if __name__=='__main__':main()
