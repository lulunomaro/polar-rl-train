"""Preserve completion, concrete source inventory and same-monitor handoff. No runtime launch."""
from pathlib import Path
import hashlib
import json
import time

D = Path(__file__).resolve().parent
W = D.parent
R = D / 'reports'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p, value):
    with Path(p).open('x', encoding='utf8') as f:
        json.dump(value, f, indent=2, allow_nan=False)


def main():
    hpath = R / 'NOMINAL_COMPLETE30_ACTUAL_CIM_HANDOFF_CPU.json'
    spath = R / 'NOMINAL_COMPLETE30_THREE_PROFILE_DEVSEEDS_TAIL_COST_CPU_ACTUAL.json'
    handoff, scope = (json.loads(p.read_bytes()) for p in (hpath, spath))
    assert handoff['actual_owner_absent'] and scope['actual_cases'] == 30 and scope['actual_initial_pairs'] == 18
    old = D / 'MONITOR_S5_NOMINAL_NATIVE_UNUSED29_STAGE_REMOTE_VERIFIED_ACTUAL_V2_20261015.txt'
    assert sha(old) == 'f82a12c0f17fa760e9ab42f46dc015e28cbfa2bad45c455c961c16c5f666f3ff'
    curb = W / 'MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011/implementation'
    plan = W / 'MOD4_S3_SCOPE_COST_S4_READINESS_AUDIT_20261014/actual_original_metadata/1791972851450503600/27_MOD4_MOE_MASTER_PLAN.md'
    q = W / 'MOD4_S4_E0_WAVE35_TRANSITION_RULE_QUERY35_V2_20261015/payload'
    files = [plan, *(curb / n for n in ('curb20_profile.json', 'curb20_geometry.py',
        'curb20_current_state.py', 'native_e1_curbscope_probe.py')),
        W / 'MOD4_E1_CURB20_133_COMPLETE_REVIEW_20261011/reports/CURB133_COMPLETE_SCOPE_DECISION.json',
        W / 'MOD4_E1_CURB20_133_COMPLETE_REVIEW_20261011/reports/CURB_TRAINING_RESET_ACTUAL_1791672164574719500.json',
        q / 'g4_worldmesh_query_contract.py', q / 'paired_full80_parameter_bound_v2.py',
        q / 's4_transition_rule_adapter_v1.py']
    inventory = [dict(path=str(p), bytes=p.stat().st_size, sha256=sha(p)) for p in files]
    put(R / 'S5_COMPLETE_NOMINAL_NEXT35_AND_LOW_STEP_SOURCE_SCOPE_INVENTORY_ACTUAL.json', dict(
        epoch=time.time(), read_only_saved_source_inventory=True, sources=inventory,
        low_step_existing_geometry=dict(height_m=.020, strip_width_m=.150, tile_m=[9., 9.],
            explicit_unsmoothed_vertical_riser=True, upper_platform_continuous=True, mirrored_available=True,
            derived_not_actual_RM002=True, not_stair_flight=True, not_airborne_hop=True),
        prior_CURB133=dict(ascending=22, ascending_total=27, descending=27, descending_total=27,
            previous_source_ascending=26, ordinary=0, selected_as_qualified=False,
            prior_rejection_and_prefixes_preserved=True, not_automatically_new_training_source=True),
        low_step_admission_still_required=['actual new mesh/query/source binding on chosen backend',
            'full collider/reset footprint and lower/upper approach placements in both directions',
            'own wheel-contact integration, hardware COM, physical prefix and no reset/teleport credit',
            'explicit source/fullstate migration, resources, lease, original budget and stage scope'],
        original35_next=dict(existing_seed02_whitev3_cell_only=True,
            missing_matrix='two development seeds x nominal/white_v2/white_v3 x A/B/C; reuse only actually matching completed cell',
            required_source_review='independent original g3_35 mesh reference, isolated nominal overlays where needed, unchanged shared35 and whole6; actual worker/profile/RNG/source bindings before own new unused native'),
        lookup_errors_preserved=[
            'Local rg wildcard passed as literal PowerShell path produced invalid filename; corrected with directory plus -g, no source mutation.',
            'polar-rl-train/runtime/isaac/mod4 absent; original durable payload runtime source was inspected instead.',
            'Unbounded rg file inventory printed duplicated captured source paths; no execution or GPU action resulted.'],
        no_CPU_physics_replay_target_import_GPU_PPO_or_budget=True,
        video_airborne_hop_requires_separate_takeoff_airborne_reset_landing_plan=True))
    work = dict(epoch=time.time(), stage='S5 frozen fair comparisons; nominal complete30 and three-profile descriptive review',
        completion=dict(cases=30, native=12, full=18, initial_pairs=18, retained_native_once=1,
            own_coordinator70456_CIM_absent=True, root_sequential_transport_reclaimed=True,
            original_each_parent_EXIT0_PIDout_and_shared_msvcrt_free=True,
            frozen_unique_parent_seconds=handoff['unique_frozen_parent_seconds'], no_canonical_charge=True,
            handoff_SHA=sha(hpath), scope_SHA=sha(spath)),
        observed_three_profile_world=scope['three_profile_world'],
        conclusion='B remains observed reference/fallback; frozen C has no demonstrated count gain and has world residuals. No global winner, statistical significance, allskills or S5 overall completion claimed.',
        next_concrete_work=[
            'Materialize independent original35 source/profile/seed adaptation with exact original geometry and same frozen A/B/C; only missing cell namespaces.',
            'CPU whole source/STD, shared35-last actual action-reset, worker inverse-AST, nominal D0 vs retained D1-D7 audits and negative tests before target admission.',
            'Then target sourcefreeze/SDK/native-resource/actual OS lock/own lease; new unused native only where matching source/backend admission cannot be reused; full physical and actual initial pairs before credit.',
            'Continue combinationDR boundaries and true within-episode task/terrain switching with separate actual scope; do not credit future cells.',
            'Use the read-only low-step geometry/reset/contact source inventory to prepare a concrete bounded admission proposal; do not replay CURB133 or assume it qualified.'],
        source_inventory_SHA=sha(R / 'S5_COMPLETE_NOMINAL_NEXT35_AND_LOW_STEP_SOURCE_SCOPE_INVENTORY_ACTUAL.json'),
        remaining_gaps=scope['remaining_gaps'], no_automatic_second_gate_PPO_or_jump_training=True,
        original_fixed30_None_reader_failure_not_reclassified=True,
        all_tasks_leases_cases_once_consumed=True, no_same_raw_recollection_for_repeated_hash=True,
        Git='Ordinary supplement to existing d48e16c trial stage. Do not repeat record/tag. Actual remote main, all1347 original tag objects/peels and tracked source hashes decide synchronization. Current reports remain pending until that verification.',
        budget='Sole1188000s330h sevenextensions unchanged. Native/frozen/CPU0PPO uncharged; firstgate2668.750717s already settled once. Historic localWindows9400.860692501068s matching still pending; unknown512 tail not guessed.')
    work_path = D / 'NEXT_S5_NOMINAL_COMPLETE30_ORIGINAL35_MATRIX_AND_LOW_STEP_ADMISSION_WORK_ORDER.json'
    put(work_path, work)
    text = f'''最新actual优先（2026-10-15）：N={D.as_posix()} nominal完整30已实际CPU闭合：12ownnative120+18full1500，18同kind/seed/profile A/B/C initialpair全部通过；其中首complete native1只复用CPU，余29unused由70456实际执行完成。原70456/create1792060426.803已实际CIMabsent，所有自身父孩子EXIT0/actualout/sharedmsvcrtfree及完整twohostSHA-source9或24-wholephysical/query/contactCOMhardware证据核通过，root收回唯一210/egde和249顺序transport。之后lateractual自己PID创建argv-root-current-save-EXIT/真实fcntl-msvcrt优先，不假永久idle/active。全30Task/lease/once已消费，禁止旧GPU/native/Task/batch重发或为重复hash再收raw。原missingEXIT_NATURAL仍missing，与wholedata+cleared+EXIT0+actualPIDout/锁free独立闭合并列，不伪marker。

先读NEXT_S5_NOMINAL_COMPLETE30_ORIGINAL35_MATRIX_AND_LOW_STEP_ADMISSION_WORK_ORDER.json、reports/NOMINAL_COMPLETE30_ACTUAL_CIM_HANDOFF_CPU.json、NOMINAL_COMPLETE30_THREE_PROFILE_DEVSEEDS_TAIL_COST_CPU_ACTUAL.json与S5_COMPLETE_NOMINAL_NEXT35_AND_LOW_STEP_SOURCE_SCOPE_INVENTORY_ACTUAL.json。nominal两个devseed world A127/128、B128/128、C126/128；seed02均64，seed03 A63失败20、B64、C62失败7/20。合nominal/white_v2/white_v3两seed world A377/384、B384/384、C378/384，只描述该scope，不是晋级线/统计显著/全球架构赢家。B保留observed reference/fallback，C冻结继续公平条件，无第二gatePPO。nominal pure正4pi A各7/8负各0/8，B/C两符号各8/8；原spin/legacyfalse与signedflat strictfalse全部保留，完整最坏尾部、failedvalidprefix、switch/action-effortjump/latency见报告。A为既有W35祖先范围对照，非同成本混训baseline或高速高yaw注册资格。30parent真实{handoff['unique_frozen_parent_seconds']!r}s frozen0PPO不扣canonical；首gate学习2668.750717163086s已唯一结清，祖先成本不假均衡。

下一积极补原35路线第二devseed与nominal/white_v2缺失matched A/B/C cell；现有原35仅seed02/white_v3已全27/27正倒ordinary0，不能冒其余已执行。先隔离完整source/profile/seed适配、原g3_35 geometry/reference绑定、nominal已核7overlay+helper、shared35/whole6原bytes和worker inverseAST/负例CPU；再targetCPU/sourcefreeze/SDK/实际资源OSlock/ownunusedlease/native，合法同source/backend原native才复用，完整full1500/6000cb/initialrootq30-params-staticrecipes-RNGqueues-loadedDLL严格pair后credit。然后组合DR边界与真实within-episode任务地形切换各新scope，heldout20261011/12不用于调参。准备/TaskRunning/native不等futurepass，不无限hold仅queue，不每阶段自造人类确认。

低台阶已实际只读定位原CURB20 profile/geometry/reset/source与旧scope：derived2cm、150mm strip、9m tile、直立未平滑riser/连续上平台、镜像可用，非真实RM002尺寸/完整梯段/腾空跳。旧CURB133上22/27下27/27较前源上26退化、未qualified、禁止直接重PPO或升高，所有原false/prefix/source保留。依工作单准备独立新geometry/query/contact/fullcollider reset/双向approach/sourcefullstate/resource/budget准入，不拿源码检查冒新native通过。人类video42168288822-1-192.mp4约42/50s是滚动接近-压腿-起跳-整机腾空越沿-轮着地屈腿缓冲；旧12-24h低台阶准备估计不适用该腾空动作日期，视频不能给力矩/高度/弹簧能量/接触力。问识别或y不授权E5/S8/newPPO；具体起跳-空中-reset-落地方案另批，无可靠日期。

原nominal fixed30 PID34592已失败退出，其可选MildDR None被V1读者下标TypeError/ORIGINAL_ERROR永留，不是GPU/PhysX失败；V2只读用actualfinal chassis_PD audit与initial/final完整witness、8savedmetadata负例通过，不造初始audit/改None或重首native。独立7candidate逆AST/四fixture60负例、white分支metadata/privateRNG/三hook输出exact、Spring父fixture边界保留。完整ZIP65521714B SHA6799d6021cf833d87934e2f1bd82956de71155077f79fa28252deeb7e6bf44b0/518package+476原shared/477ownfrozen/eightoverlay已actualtargetCPU/SDKbinding，本次native/全raw另证真实构造和物理。nominal仅D0白随机关闭，原D1-D7/noise/delay保留；gas→spring D6 damping overlay、D5-D7严格审不降。无fakeMildDR/mask/RNG，metadataNone/不存在generator缺席，COMframe1e-5/query1e-6保持。

所有source完整E0b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8/14028642B94float、W35b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd/17615538B102float、gate02718c74024508c50ff559be2fa6351b7f63046afeb4ee3fd7c51ad6160ae1f3/24031587B194tensor113float冻结。GPUeval A只actor9，B/C18expert+6gate，不冒20k环境DR GPUrestore。shared35一次/tick、22:28上一actualclipped6、28:35常normal[1,0,0,0,0,0,0]、selectedreset只清同行、whole6后clip6；无teacher/envID/地形真值/未来接触/liveheadingposition纠偏/actionweight平均/暗加hysteresis。CPUmeans非GPUbitexact/hostlatency非板deadline/参考publicsource非installedDLLbitexact/shapeLocal未directread/COM未实物标定保持。

首S4学习原148updates3552controls71.04M物理steps14208cb、gate6critic8变化14Adam2960/expert18stdduplicateexact、8typed/sourceepisode1/privateCUDA z-raw-jointlogp-disknextdraw/sourcefreeze/44inputtwohostCPU已passed；148更新前NPZ24796375544B与7physical2064031292B全durable消费、实际support梯度20167032而非71.04M全样本，151552概率抽查非allrow/replay，最长physicalprefix20s。原FINAL/PASSpidout/twofcntlFree/canonicalidle/2668.750717s once结清不再active；源0681初151tensor70float与final194113分列，旧Logger保存失败/zerohealthNaN/cacheCPUCUDA与各false不改PASS不重GPU。joint sampledz+conditional未clipGaussian+gatecat logp/KLentropy，supportlabel只训练筛完整24+bootstrap/优势标准化不供推理。

master812a4b+004005/RM003002001不变，当前S5 faircomparison未整体完成，S3整体/50或70/S5生产MoE架构未毕业。S3/E1_WAVE/G1 continuous10→20→35→50有限域，G2curb/G3slope/R1real70/R2连接/R3外缘另范围；原plan允许披露残差practicalcloseout，无27/27或90/95/100机械线，旧purefalse不无限否决限定域。保护50f5166509d297814e3c3fe4f457ae064d9b02a8bd62702914759dc430f20d2139正26/27倒26/27ordinary1及所有d05/1aa/2b/e3/cfce/E0/35/CURB/SLOPE原件，cfce22/26/world64不替代Wave优先，BODY/left两块已完不第三盲同轴duration/自动70。hardware未标定/S8另批/93-94paused/WASD不GUI/reset-stop-restart。

原训练20k/seed20260928/24controlupdate/LR1e-4adaptiveKEEPSTD1/2.5ms×4-TGS32/4-100Hz/history5msbin3/35actor38critic6action/fivefamilies/D0D7white_v3+noise/rewardhardware不混改。healthclosure2mm普通仅单envreset继续，mimic.01/nonfiniteunknownmissingcallbacks ownsave-stop不降guard。Wave原十波2.406422727m/.4approach15s80env1500/6000cb/>1N双轮before-after200mm/query1e-6/contactCOMhardware/allvalidprefix/noresetteleport/standing无需通行。115129flat/spin/world原fullsignedcircle沿横dedrift/±4pi/straightfalse/tolmax(.03,.1V)/yaw±.2/worldBODYvx2Vcos(theta-alpha)vy0不纠偏；rootcommandproxy非轮contact/fullroute/唯一因果。

005solecanonical1188000s330h/sevenextensions末USER_ADD100H_20261011_7TH早once，不加时/复制账/clearactive/refund/tail/recharge。learning每parent真实loadlearnsaveexit含failedstartup唯一扣；CPU/SDK/native/frozen/fullrestore0PPO不扣。localWindows7完整9400.860692501068s待原账匹配，未知512OS尾未知不猜wall/3600。S3原30+00575=105h仅规划上限不用花满，otherexpertgate min(18h,.13B)仅规划非reserve。LaptopGPU仍暂停/Linux4090正常修复训练原授权/3060evalonly/WindowsCreadonly-Ddurable。

Root唯一210/egde与249顺序boundedSSH/SCP；任何后来自己finite/collector actualCIMcreationargv真alive才独占两host，根/agent只本机reports+CIM，实际完成+退出handoff后收回。unknownmutation先actual只读不盲重once。无额外watcher/5minSSH-ping-Rich/密集SSH/旧RPCpoller-mirror-TUI-SCUT-main-resume-once/旧consumeGPU重跑/kill-delete/installedSDKdriver热改/他人AI-WASDGUI/双GPUworker，旧exact172447SIGTERM许可已消费不能挪用；锁看真实fcntl/msvcrt held-free非fileexists不删。

Git Nstage d48e16c6682ba19a724a0bbe0ca9938ee9beaf08/tagtrial-20261015-s5-nominal-absent-mild-audit-source-cpu/objectf56546ac90d1cb153d9c3b32b94dd75ee467af7f已唯一record并remote main/tag/peel核；ordinarya65958ef845173bf3adf24cfe043f41b475cffe1已remote/all1347tag原peel/tracked2302核。当前完成结果/所有rawindex/false/读者error/lookupmiss/source/成本/工作单/本monitor/Gitreceipt须ordinarysupplement，lateractualHEAD/remote/tracked工具优先不凭提示假已全补。不能重Nrecord/tag/commit；新ordinary仅首次生成，pushfail只现有objects续，不关证书/globalconfig/密集重试。原M e411 TLS及旧tagpeel误等ordinaryHEAD错误/V3恢复、5dc8同步全历史保留。大型PTNPZUSDZIPrawJSON视频仅真实path-size-SHA索引原件保留，credentials不输出Git，Git不阻runtime/改预算。

mod4-10同ACTIVE每1h同target01a07a2d-9036-7531-a012-692df9f56353。healthy unchanged/pending DONT_NOTIFY静默无commentary，不重复本轮nominal30complete/三profile计数；仅新实质结果/修复/重大退化/完成/必需人类动作NOTIFY，不第二monitor/自动预算。limitedreview非allcoursefinished不删，只有actualbudgetend+allfinal全部完才停。旧完整prompt {old.as_posix()} SHA{sha(old)}原件留追溯，其中70456active/remainderpending是历史，laterownactual/newhuman优先。'''
    prompt = D / 'MONITOR_S5_NOMINAL_COMPLETE30_THREE_PROFILE_AND_NEXT35_LOW_STEP_ACTUAL_20261015.txt'
    with prompt.open('x', encoding='utf8', newline='\n') as f:
        f.write(text)
    print(json.dumps(dict(workorder=str(work_path), prompt=str(prompt), prompt_SHA=sha(prompt),
                          no_GPU_network_PPO_or_budget=True)))


if __name__ == '__main__':
    main()
