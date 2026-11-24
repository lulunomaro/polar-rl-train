"""Publish measured stage-two acceptance, retaining every failed requirement."""
from collections import defaultdict
from datetime import datetime,timezone
import json
import numpy as np
from pathlib import Path
from fsm_paths import HERE,ROOT,E0_SHA,E0_BASE_SHA
from fsm_io import put,sha256


def read(name):return json.loads((HERE/name).read_text(encoding='utf-8'))


def main():
    stamp=datetime.now(timezone.utc).isoformat();base='evidence/stage2_final'
    candidate=read('CANDIDATE.json');stair=read(base+'/stair/RESULT.json');rows=stair['rows']
    assert len(rows)==320 and sum(not r['dr'] for r in rows)==80
    for r in rows:
        r['evidence_case']=f"{base}/stair/cases/{r['id']}.json"
        r['evidence_trace']=f"{base}/stair/traces/{r['id']}.npz"
        with np.load(HERE/r['evidence_trace']) as raw:
            physical=raw['physics'];reference=raw['reference_trace']
            body_edge=physical[:,11] if physical.shape[1]>11 else reference[:,11:13].max(1)
            body_crossed=bool((physical[:,10]>body_edge).any())
        r['body_first_edge_crossed']=True if body_crossed else (False if physical.shape[1]>11 else None)
        r['body_first_edge_crossing_proved']=body_crossed
        r['passed']=bool(r['passed'] and body_crossed)
        r['strict_support_400hz']=r['passed']
        r['physical_body_crossing_confirmed']=bool(r['physical_crossed'] and body_crossed)
    unforced=[r for r in rows if r.get('force_at_s') is None]
    violations=[dict(id=r['id'],samples=r['precontact_active_samples'],trace=r['evidence_trace'])
        for r in unforced if r['precontact_active_samples']]
    per_course=[]
    for course in sorted({r['course'] for r in rows}):
        for dr in (False,True):
            group=[r for r in rows if r['course']==course and bool(r['dr'])==dr]
            per_course.append(dict(course=course,full_dr=dr,total=len(group),
                strict_passed=sum(r['passed'] for r in group),
                physical_without_fall=sum(r['physical_crossed'] and not r['failure'] for r in group),
                physical_without_fall_or_slip=sum(r['physical_crossed'] and not r['failure'] and not r['slipped_from_tread'] for r in group),
                raw_substep_passed=sum(r['raw_contiguous_2p5ms_substeps']['passed'] for r in group)))
    window_audit=read(base+'/stair/WINDOW_RECONSTRUCTION_AUDIT.json')
    benchmark=dict(utc=stamp,physics_hz=400,policy_hz=50,force_threshold_n=5.,
        support_contract='Signed raw 400 Hz normals, independent L/R arithmetic means in 8-substep nonoverlapping 20 ms windows; each >5 N; first tread >=5 windows; final deck >=20 windows after E0 handoff; body and both wheels on final deck; no fall or slip.',
        raw_substep_metric_role='Transparent diagnostic; not the formal acceptance threshold.',
        total=320,passed=sum(r['passed'] for r in rows),
        nominal_passed=sum(r['passed'] for r in rows if not r['dr']),nominal_total=80,
        full_dr_passed=sum(r['passed'] for r in rows if r['dr']),full_dr_total=240,
        physical_no_fall=sum(r['physical_crossed'] and not r['failure'] for r in rows),
        physical_body_crossing_confirmed_no_fall=sum(r['physical_body_crossing_confirmed'] and not r['failure'] for r in rows),
        physical_no_fall_no_slip=sum(r['physical_crossed'] and not r['failure'] and not r['slipped_from_tread'] for r in rows),
        raw_contiguous_2p5ms_substep_passes=sum(r['raw_contiguous_2p5ms_substeps']['passed'] for r in rows),
        independent_force_window_reconstruction=window_audit['passed'],
        body_crossing_independently_rebuilt_from_raw_traces=True,
        closure_diagnostic='Legacy max_closure_mm in per-case evidence is the final control-boundary sample, not a 400 Hz maximum.',
        unforced_precontact_violations=violations,per_course=per_course,rows=rows,
        source_checkpoint=candidate['checkpoint'],source_sha256=candidate['sha256'],
        e0_base_sha256=E0_BASE_SHA,e0_sha256=E0_SHA,
        overall_requirement_passed=all(r['passed'] for r in rows) and not violations and window_audit['passed'])
    put(HERE/'FSM_STAIR_BENCHMARK.json',benchmark)

    flat60=read(base+'/flat60/RESULT.json');flat=read(base+'/flat/RESULT.json')
    premature=read(base+'/premature/RESULT.json');holdout=read(base+'/holdout/RESULT.json')
    cruise=[r for r in premature['rows'] if r['course'] in ('flat','rough_L9')]
    hold_bad=[r['id'] for r in holdout['rows'] if r['precontact_active_samples']]
    delays=[r['trigger_delay_ms'] for r in unforced if r['first_face_contact_s'] is not None]
    detected=sum(v is not None for v in delays)
    recall_by_dr={}
    for name,dr in (('nominal',False),('full_dr',True)):
        values=[r['trigger_delay_ms'] for r in unforced if bool(r['dr'])==dr and r['first_face_contact_s'] is not None]
        recall_by_dr[name]=dict(contact_cases=len(values),detected=sum(v is not None for v in values),
            within_40ms=sum(v is not None and 0.<=v<=40. for v in values),
            within_100ms=sum(v is not None and 0.<=v<=100. for v in values),
            within_400ms=sum(v is not None and 0.<=v<=400. for v in values),
            negative_latency_cases=sum(v is not None and v<0. for v in values))
    zero_leak=all(r['stair_active_fraction']==0. for r in cruise)
    audit=dict(utc=stamp,flat60=dict(passed=flat60['passed'],total=flat60['total']),
        ordinary_flat=dict(passed=sum(r['passed'] for r in flat['rows'] if r['course']=='flat'),total=16),
        ordinary_rough=dict(passed=sum(r['passed'] for r in flat['rows'] if r['course']=='rough_L9'),total=16),
        fullspeed_cruise=dict(passed=sum(r['passed'] for r in cruise),total=len(cruise),
            stair_leak_fraction=max(r['stair_active_fraction'] for r in cruise),structural_zero_leak=zero_leak,rows=cruise),
        early_arm_holdout=holdout,holdout_preactivation_violations=hold_bad,
        wider_stair_matrix_unforced_violations=violations,
        contact_recall=dict(contact_cases=len(delays),detected=detected,missed=len(delays)-detected,
            by_dr=recall_by_dr,
            within_40ms=sum(v is not None and 0.<=v<=40. for v in delays),
            detector_trace_note='Negative latency is preserved; geometry-contact labeling and the 10 cm precontact audit are distinct measurements.'),
        zero_false_positive_full_coverage_passed=not violations and not hold_bad and zero_leak,
        e0_base_sha256=E0_BASE_SHA,e0_sha256=E0_SHA,detector=read('DETECTOR.json'))
    audit['overall_requirement_passed']=audit['zero_false_positive_full_coverage_passed'] and flat60['passed']==60
    put(HERE/'PREMATURE_SQUAT_AUDIT.json',audit)
    jump=read(base+'/jump/RESULT.json')
    jump.update(utc=stamp,functional_integration_passed=jump['passed']==jump['total']==5,
        criterion='Real articulation CoM key speed within .15 m/s (stationary <.10); required bilateral clearance; direct first landing on top; no >5 N riser assistance; return to cruise without timeout.',
        source=base+'/jump/RESULT.json')
    put(HERE/'FSM_JUMP380_CHECK.json',jump)
    video=read('evidence/videos_final/FRAME_DECODE_AUDIT.json')
    smoke=read('evidence/PLAYER_SMOKE.json');protected=read('evidence/PROTECTION_VERIFICATION.json')
    closure=[]
    for tag in ('fsm_r10','fsm_r10b','fsm_r10c','fsm_r10d_finalgate'):
        folder=HERE/'evidence'/tag
        if not folder.is_dir():continue
        entry=dict(tag=tag)
        for name in ('probe/PROBE.json','probe/SAFE_CLOSED.json','probe_EXIT.json','train/FINAL.json',
                     'train/SAFE_CLOSED.json','train_EXIT.json','train/TRAIN_START.json'):
            if (folder/name).is_file():entry[name]=read(str((folder/name).relative_to(HERE)))
        closure.append(entry)
    successful=[r for r in closure if 'train/FINAL.json' in r]
    training_closed=bool(successful) and all(r['train/SAFE_CLOSED.json']['scene_closed'] and
        r['train_EXIT.json']['own_gpu_process_released'] and not r['train_EXIT.json']['hard_kill'] for r in successful)
    put(HERE/'evidence/TRAINING_CLOSURE_STAGE2.json',dict(rounds=closure,training_safely_closed=training_closed))
    gate_probe=next((r for r in closure if r['tag']=='fsm_r10d_finalgate'),{})
    gate_probe_closed=bool(gate_probe.get('probe/PROBE.json',{}).get('passed') and
        gate_probe.get('probe/SAFE_CLOSED.json',{}).get('scene_closed') and
        gate_probe.get('probe_EXIT.json',{}).get('own_gpu_process_released'))
    videos_pass=video['passed'] and video['all_representative_cases_passed'] and video['every_frame_physics_telemetry_passed']
    accepted=bool(benchmark['overall_requirement_passed'] and audit['overall_requirement_passed'] and
        jump['functional_integration_passed'] and flat['passed']==32 and sum(r['passed'] for r in cruise)==10 and
        videos_pass and smoke['passed'] and protected['passed'] and training_closed and gate_probe_closed)
    candidate.update(status='accepted' if accepted else 'experimental_not_graduated',
        strict_stair_acceptance_passed=benchmark['overall_requirement_passed'],
        stage2_final_acceptance_passed=accepted,final_stair_passed=benchmark['passed'],
        final_stair_total=320,zero_preactivation_passed=audit['zero_false_positive_full_coverage_passed'],
        final_report='FINAL_FSM_REPORT.md')
    source_metadata=HERE/Path(candidate['source_checkpoint']).with_suffix('.json')
    if source_metadata.is_file():
        candidate['selected_snapshot_active_dr']=json.loads(source_metadata.read_text()).get('active_dr')
    candidate['selected_actor_updates_after_critic_warmup']=max(0,candidate['selected_round_ppo_updates']-3)
    put(HERE/'CANDIDATE.json',candidate)
    detector=read('DETECTOR.json');detector.update(formal_closed_loop_verification_pending=False,
        formal_matrix_cases=320,formal_unforced_precontact_violations=len(violations),
        heldout_precontact_violations=len(hold_bad),formal_contact_recall=audit['contact_recall'])
    put(HERE/'DETECTOR.json',detector)
    text=["# MOD4v3 手工 FSM 第二阶段实测报告",'',
        f"**{'第二阶段完整验收通过' if accepted else '第二阶段完整验收未通过；候选保持实验状态'}。** UTC：{stamp}。",'',
        f"第一阶段完整报告保留于 `STAGE1_R9_REPORT.md`（SHA256 `{sha256(HERE/'STAGE1_R9_REPORT.md')}`），根文件及视频历史保存在 `evidence/stage1_r9_archive/`、`evidence/videos_stage1_r9/`。",'',
        '正式承载合同采用原始 400 Hz 有符号法向力，每 8 子步构成一个不重叠的 20 ms 窗口；左右轮分别均载 >5 N。双阶一级至少 5 窗口，末段顶面接回 E0 后至少 20 窗口；双轮及车身真正进入最终顶面，全程无摔倒或滑落。原始 2.5 ms 连续计数并列保留，未作为正式门槛。', '',
        '| 验收 | 实测 |','|---|---:|',
        f"| flat60 | {flat60['passed']}/60 |",f"| flat / rough L9 | {audit['ordinary_flat']['passed']}/16 / {audit['ordinary_rough']['passed']}/16 |",
        f"| 0.8–3.0 m/s 关 C 巡航 | {sum(r['passed'] for r in cruise)}/10；台阶泄漏 {100*audit['fullspeed_cruise']['stair_leak_fraction']:.3f}% |",
        f"| 20 ms 窗口严格上阶 | {benchmark['passed']}/320；0-DR {benchmark['nominal_passed']}/80；Full-DR {benchmark['full_dr_passed']}/240 |",
        f"| 物理越阶无摔 / 无摔且无滑落 | {benchmark['physical_no_fall']}/320 / {benchmark['physical_no_fall_no_slip']}/320 |",
        f"| 原始子步诊断通过 | {benchmark['raw_contiguous_2p5ms_substep_passes']}/320 |",
        f"| 未按 V 的矩阵提前激活违规 / 留出违规 | {len(violations)} / {len(hold_bad)} |",
        f"| 实速跳跃 | {jump['passed']}/5 |",f"| 四支原速视频 | 通关全部通过={videos_pass}；逐帧解码={video['passed']} |",
        f"| 启动器 12 图 / 受保护资产 | {smoke['passed']} / {protected['files']} 份通过={protected['passed']} |",'',
        '| 地形 | DR | 窗口严格通过 | 无摔物理越阶 | 原始子步诊断 |','|---|---|---:|---:|---:|']
    for r in per_course:
        text.append(f"| {r['course']} | {'Full' if r['full_dr'] else '0'} | {r['strict_passed']}/{r['total']} | {r['physical_without_fall']}/{r['total']} | {r['raw_substep_passed']}/{r['total']} |")
    for entry in successful:
        final=entry['train/FINAL.json']
        text += ['',f"受控训练 `{entry['tag']}`：{final['elapsed_s']:.3f} 秒，{final['ppo_updates']} PPO / {final['optimizer_steps']} Adam；末段 target DR={final['target_dr']}，实际启用完整 DR 的环境 {final['active_dr']}/2048。所选快照本轮计数为 {candidate['selected_round_ppo_updates']} PPO / {candidate['selected_round_optimizer_steps']} Adam，未将末轮或目标 DR 标签当作独立毕业。",
            '前 3 次完整更新只预热 critic；actor 从第 4 次更新开始变化，首次真实变化证据见 `evidence/FIRST_R10_ACTOR_UPDATE.json`。',
            f"原生轮中心粗边界提前激活计数为 {final['premature_activation_frames']}，原始值完整保留；CPU 全几何预接触矩阵另列，二者不混为同一个指标。"]
    text += ['',f"最终入口：`{ROOT/'Run_MOD4v3_ManualFSM_Unified_WASD.bat'}`。候选 `{candidate['checkpoint']}`，SHA256 `{candidate['sha256']}`。选择依据见 `evidence/STAGE2_CHECKPOINT_SELECTION.json`，没有把最后保存自动当作最优。",'',
        'E0 现完整加载冻结 `c874a1af` 与 `b271cafb`，按 0.32–0.40 m 混合并左右对称化。160 个正反标定点的最大拟合误差为 0.0248 m/s。高速低姿会平滑升至 0.32 m，高速倒车会平滑降至 0.32 m，避开已测出的倒车折返；因此高速下的有效站高与滑杆站高可能不同。DECK_SETTLE 为 0.31 m，阶面腿目标只在 50 Hz 策略侧平滑。物理 400 Hz、腿 PD 100 Hz、轮 400 Hz、电机包络、六维动作和机器人资产均未更改。', '',
        '完整 RM 原图仍用于 CPU 验收。GPU 精修采用原图走廊的离线碰撞剖面，不向 FSM/actor 输入地图位置、射线或真值；FSM 仅使用 obs35 和操作者意图，actor 仅使用 obs35+420 历史。', '',
        '首次高密度训练网格预检烘焙失败，零更新记录和显存释放证据保留；后续合格的 600 步零更新预检及受控训练分别记录。`evidence/TRAINING_CLOSURE_STAGE2.json` 列明真实 PPO、Adam、时长及关闭状态，不能将失败预检算作训练。', '',
        f'首轮完整 CPU 矩阵为 60/320，保留在 `evidence/stage2_full_before_integral_gate_fix/`；其中唯一 dr1729 提前激活有 14 个原始子步。随后将受阻积分的平均俯仰下限由 -0.02 收紧到 +0.02，重新比较受影响的 Full-DR 检查点，并重新模拟最终整套验收。最终门控另做 600 步、零优化器的 GPU 复核，通过且已关闭={gate_probe_closed}；未追加 PPO。', '',
        f"训练安全关闭={training_closed}。原始窗口重算 {window_audit['cases']}/{window_audit['cases']} 通过={window_audit['passed']}。", '',
        '完整 RM 名义六点的出生航向未见错误；中心一级踏面长度西/东约 0.730/0.736 m，短于 A–A 的 1.20 m。原图采用分块高度场。多例二次触阶时 E1 已激活，东入口 1.2 m/s 的 TREAD_BRIDGE→E1 重接手约 45 ms；仍出现转向漂移、二级越阶不足或上台后没有恢复 E0 承载。不能统一归因于“未二次触发”。逐点证据见 `evidence/STAGE2_RM27_FAILURE_DIAGNOSIS.json`。', '',
        '原始 2.5 ms 连续性诊断仍为 0/320，真实高频腿颤的彻底消除尚未验收通过。', '',
        '详见 `FSM_STAIR_BENCHMARK.json`、`PREMATURE_SQUAT_AUDIT.json`、`FSM_JUMP380_CHECK.json`、`evidence/videos_final/VIDEO_MANIFEST.json` 及全部逐点原始轨迹。']
    if not accepted:
        text += ['',f"尚未达成：严格上阶失败 {320-benchmark['passed']} 例，矩阵提前激活违规 {len(violations)} 例，留出违规 {len(hold_bad)} 例；四视频全部通过={videos_pass}。具体失败保留，未宣布毕业。"]
    (HERE/'FINAL_FSM_REPORT.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    put(HERE/'evidence/STAGE2_FINAL_ACCEPTANCE.json',dict(passed=accepted,strict_stair=benchmark['passed'],
        nominal=benchmark['nominal_passed'],full_dr=benchmark['full_dr_passed'],zero_preactivation=audit['zero_false_positive_full_coverage_passed'],
        flat60=flat60['passed'],jump=jump['passed'],videos=videos_pass,training_closed=training_closed,
        assets=protected['passed'],smoke=smoke['passed']))
    put(HERE/'evidence/STAGE2_PROGRESS.json',dict(active_phase='final evaluation closed',acceptance_passed=accepted,
        training_closed=training_closed,final_gate_zero_update_probe_closed=gate_probe_closed,
        selected_checkpoint=candidate['checkpoint'],final_report='FINAL_FSM_REPORT.md'))
    print('Stage-two acceptance',accepted,'stairs',benchmark['passed'],'/320',flush=True)


if __name__=='__main__':main()
