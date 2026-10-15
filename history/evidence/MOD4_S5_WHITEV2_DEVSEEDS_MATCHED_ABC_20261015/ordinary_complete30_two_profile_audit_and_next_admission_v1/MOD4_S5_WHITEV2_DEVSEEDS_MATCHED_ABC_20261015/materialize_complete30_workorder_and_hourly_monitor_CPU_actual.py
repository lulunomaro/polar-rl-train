"""Save actual completion handoff and proposed same-hourly monitor text, CPU only."""
from pathlib import Path
import hashlib
import json
import time

D = Path(__file__).resolve().parent
R = D / 'reports'
W = D.parent


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    handoff_path = R / 'WHITEV2_COMPLETE30_ACTUAL_CIM_HANDOFF_CPU.json'
    summary_path = R / 'WHITEV2_COMPLETE30_TWO_PROFILE_DEVSEEDS_TAIL_COST_CPU_ACTUAL.json'
    handoff = json.loads(handoff_path.read_bytes())
    summary = json.loads(summary_path.read_bytes())
    assert handoff['actual_owner_absent'] and summary['actual_cases'] == 30 and summary['actual_initial_pairs'] == 18
    oldprompt = D / 'MONITOR_S5_WHITEV2_FIXED30_STAGE_REMOTE_VERIFIED_ACTUAL_UTF8_V3_20261015.txt'
    assert sha(oldprompt) == '8b234e31b79a3d74a008a7e0914153e77d000ee5af9718b84083cea9d83ee9e9'
    source_root = W / 'MOD4_3060_LEFT_REPAIR_FULL80_20261014/payload'
    nominal_files = [source_root / 'factor_runtime_3060_reference17b_v1.py', *[
        source_root / 'runtime/isaac/mod4' / name for name in
        ('mild_dr.py', 'spring_pressure_audit_runtime.py', 'gas_damping_sdk_adapter.py',
         'chassis_com_pose_roundtrip_sdk_adapter.py', 'explicit_pd_sdk_adapter.py',
         'chassis_pd_training_env.py', 'nominal_parameter_audit.py')]]
    source_evidence = [dict(path=str(p), sha256=sha(p)) for p in nominal_files]
    workorder = dict(epoch=time.time(), current_stage='S5 frozen matched A/B/C review; white_v2 fixed30 complete',
        actual_completion=dict(cases=30, native=12, full=18, initial_pairs=18,
            own_scope_parent_child_exit0_and_actual_msvcrt_free=True, own_finite_coordinator_CIM_absent=True,
            root_transport_reclaimed=True, frozen_parent_seconds=handoff['unique_frozen_parent_seconds'],
            no_canonical_charge=True, handoff_SHA=sha(handoff_path), full_summary_SHA=sha(summary_path)),
        observed_world_counts=summary['two_profile_world'],
        conclusion='Across the two development seeds and white_v2/white_v3 measured world scopes, B is256/256, C252/256, A250/256. C adds no count benefit over B, and signed flat errors are not uniformly better. Keep B the observed reference/fallback; C frozen. No significance, new graduation threshold, global architecture winner or allskill verdict.',
        nominal_source_evidence=source_evidence,
        nominal_not_admitted_or_dispatched=True,
        nominal_next_implementation_scope=[
            'Independent new source namespace only; no installed/shared-source hotpatch.',
            'Original nominal configure creates no _mild_dr. Do not fabricate a MildDR object, factor, nominal mask or generator.',
            'factor params/private_rng and chassis_pd_audit need explicit absent-MildDR metadata handling.',
            'SpringPressureSDK, GasDampingSDK, ChassisCOMSDK and ExplicitPDSDK constructors register MildDR audit hooks. Guard only absent hook registration; preserve original resets, setters, samplers, RNG order, physics and numerical thresholds.',
            'GasDampingSDK separately overlays spring audit to account for legitimate D6 damping; preserve this overlay even when MildDR is absent.',
            'Separate strict D0 nominal mass/inertia/material/output-scale checks from retained D1-D7 COM/PD pressure. Legacy uniform-COM rejection remains historical, strict COM frame and PD tensor audits remain.',
            'CPU original-white-branch equivalence, absent-MildDR old rejection/new behavior, gas-spring overlay and wrong mass/inertia/scales/COM/PD negative cases before any target admission.',
            'Actual sourcefreeze/targetCPU/resources/locks/new unused native scope and whole physical readback must pass before own nominal frozen full cases. CPU preparation is not future GPU pass.'
        ],
        remaining_S5_gaps=summary['remaining_gaps'],
        low_step='Prepare original-plan independent geometry/contact/reset/source/resource/budget admission. Previous12-24h estimate was engineering planning, not a deadline, automatic budget/PPO grant or S8 jumping approval.',
        airborne_jump='Separate E5/S8 executable takeoff/reset/landing plan approval remains required; no reliable date.',
        no_second_gate_PPO_or_third_blind_BODY=True,
        fixed_budget_and_sources_unchanged=True,
        tool_lookup_miss_preserved=dict(path=str(W/'MOD4_S5_DEVSEED03_WV3_MATCHED_ABC_20261015/append_complete15_scope_ordinary_actual_once.py'),
            result='Local Get-Content FileNotFound only; no source writes, network, GPU or budget. Existing actual archive helper was read instead.'),
        Git='Completion is an ordinary supplement to existing stage57acae/tag; do not record/tag/commit that stage again. New completion audit, all saved actual case data indexes/readers/receipts/monitor must be captured. Remote/tracked verification determines archive state.')
    work = D / 'NEXT_S5_WHITEV2_COMPLETE30_NOMINAL_AND_LOW_STEP_ADMISSION_WORK_ORDER.json'
    with work.open('x', encoding='utf8') as f:
        json.dump(workorder, f, indent=2, allow_nan=False)
    text = f'''最新actual优先（2026-10-15）：M={D.as_posix()} 的white_v2两开发seed20261002/03固定30已全actualcomplete：12ownnative120+18full1500，18完整三方initialpair CPU通过。原29884/create1792046882.973 coordinator已actualCIMabsent；全ownparent EXIT0/父子out/sharedmsvcrtfree/完整twohostSHA-source9或24-physical/query/contactCOMhardware通过。Root收回唯一210/249顺序transport；之后lateractual PIDcreationargv/root/current/save/EXIT/真实fcntl-msvcrt优先，不套永久idle或active。原30Tasks/leases/once均消费，不重GPU/native/旧scope或只为重复hash收raw。原missingEXIT_NATURAL仍missing，与wholedata+EXIT0+cleared+actualPIDout/OSlockfree独立闭合并列，不伪marker。

先读NEXT_S5_WHITEV2_COMPLETE30_NOMINAL_AND_LOW_STEP_ADMISSION_WORK_ORDER.json、reports/WHITEV2_COMPLETE30_ACTUAL_CIM_HANDOFF_CPU.json与WHITEV2_COMPLETE30_TWO_PROFILE_DEVSEEDS_TAIL_COST_CPU_ACTUAL.json。当前S5 fair A单W35/B规则E0+W35/C source148学习门控，两devseed×white_v2/white_v3的world描述性总数A250/256、B256/256、C252/256。white_v2 A125/128、B128/128、C126/128；seed02 C63失败49，seed03 C63失败20。B优先observed reference/fallback，C冻结继续公平条件，无第二gatePPO。原signedflat strictfalse、spin/legacyfalse、全部failed validprefix/连续最坏尾部/切换/action-effortjump/latency都保留，不拿count当新晋级线/统计显著/全球架构赢家。SingleA是既有W35祖先权重范围对照，非同成本混训baseline或高速/高yaw注册技能资格。30parent真实{handoff['unique_frozen_parent_seconds']!r}s frozen0PPO不扣canonical；gate首窗2668.750717163086s祖先成本另列不假均衡。

下一积极做nominal缺失的独立source/audit适配与CPU负例。Original nominal configure不建_mild_dr；factor params/private_rng/chassis_pd_audit以及spring/gas/COM/PD构造audit hooks均有实际该依赖。只新隔离源guard缺失MildDR hook注册并明确metadata absent，不造假_mild_dr/RNG，不改物理reset/setter/采样/DRdraw/command/reward/clock/hardware。特别gas audit同时还有合法D6→spring expected-damping overlay，nominal也必须保留。严格D0 nominal质量惯量材料unityoutput和D1-D7 COM/PD压力分列，旧uniformCOM false保留、原COMframe/PD严格阈值不降。源码检查或CPU fixture不冒target/native通过；实际sourcefreeze/targetCPU/resources/locks/newunusednative/wholephysical准入后才自己的nominal冻结fullscope。组合DR/真实任务切换/原35第二devseed-profile/matchedsingleancestry/硬件校准和deadline仍缺，不把S5整体写完成。

低台阶按原计划积极独立geometry/contact/reset/source/resource/budget准备，不必等50mm完美分数；先前12-24h只是工程排期估计非deadline/新预算/自动PPO保证。腾空jump E5/S8仍需具体起跳reset落地合同另批，无可靠日期；人类y只确认继续既有批准计划，不是新增S8或第二gate窗。master812a4b+004005/RM003002001、solecanonical1188000秒330h/sevenextensions不变，不第二账/clearactive/refund/tail/recharge/自动加时。所有祖先E0b109/W35b026/gate02718c及f51650mm26/26等源保护；S3整体/50或70/全skill毕业未声称。

当前新complete30审查/工作单/本monitor和原source/false/读者lookupmiss/rawindexes/cost/Gitreceipt必须普通补档至既有Mstage57acae/tagtrial-20261015-s5-two-devseeds-reviewed-whitev2-frozen-abc-started；不重复record/tag/commit。actualremote main/tag/peeled/alloldtags/tracked工具优先，本文不假全已Git。大原件真实path-size-SHA保留，credentials不输出Git，Git不阻runtime。旧stage已actualremote57acae/object0b9f7/all1345旧tag，ordinaryd3b0066已actualremote/all1346tag/tracked451源；后来ordinary实际优先。

Root唯一210/egde和249顺序boundedSSH/SCP；任何后来自己的有限collector/coordinator actualCIMcreationargv真alive才授它唯一两hostowner，根/agent只读本机，actual结束handoff后收回。不密集SSH/旧RPCpoller/mirror/TUI/SCUT/main/resume/once恢复/旧GPU重跑/kill-delete/installedSDKdriver热改/他人AI-WASDGUI/双GPUworker。LaptopGPU暂停，Linux4090正常修复训练原授权，3060仅评测，WindowsCreadonly/Ddurable；锁真实fcntl-msvcrt held/free不是fileexists不删。

mod4-10同ACTIVE每1h同target01a07a2d-9036-7531-a012-692df9f56353，healthy unchanged/pending DONT_NOTIFY静默无commentary，不重复本轮30complete与256/252通知；仅新实质阶段/修复/重大退化/完成/必需人类动作NOTIFY。无第二monitor/5minSSH-ping-Rich/额外驻守/自动预算。单limitedreview不是allcoursefinished，只有actualbudgetend与allfinal全完才停。后来ownactual/newhuman优先。

旧完整prompt {oldprompt.as_posix()} SHA{sha(oldprompt)}原件保留追溯；其中29884active/后casepending由上述及后来actual覆盖。'''
    prompt = D / 'MONITOR_S5_WHITEV2_COMPLETE30_NOMINAL_LOW_STEP_PREPARATION_ACTUAL_20261015.txt'
    with prompt.open('x', encoding='utf8', newline='\n') as f:
        f.write(text)
    print(json.dumps(dict(workorder=str(work), workorder_SHA=sha(work), prompt=str(prompt), prompt_SHA=sha(prompt), no_GPU_network_PPO_budget=True)))


if __name__ == '__main__':
    main()
