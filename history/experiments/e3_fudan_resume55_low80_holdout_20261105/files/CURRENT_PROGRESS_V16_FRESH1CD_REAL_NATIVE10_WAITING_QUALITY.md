# V16 — fresh1cd N20000已经真实开训；首次固定证据10轮；独立质量仍待实测

## 当前事实

仅E3，goal `goal-c490e4cc-b28b-440e-bde6-30ee956813f0` revision3 active/armed/max14。H1/其它专家/Registryv12/1cd母版均未变。原0/74与旧3e64/8af4名义低位漂移结论仍成立，未据此推广本次新分支，未完成目标。

本次是1cd actor8+critic8 MLP warm，**encoder fresh随机、新latent列0、STD.5、两Adam/LR/private generator/计数全fresh**，不是继续旧205。N20000/T48/最大25，base四项0/window==本分支计数，inherited_old_iterations0/bad_candidate_reads0/full_learner_resume=false。相同低8s/400timeout、Fudan core、物理/fullDR/commands/acceptance均保持。

## W7终态和实际释放

W7原1800s authority EX忙，01:27自然超时，0GO/worker/SDK/PT/PPO/候选；parent1625509/controller1625502实际全部wait/结清/释放。错误原文保留，不将RC0当训练通过。旧observer8166已completed0/output collected，旧root和入口不重放。只读watch **pwsh-ddb393298cab4501 completed0/output collected**，epoch1793814056.4740443确见canonical ownerNone/reader gaps0；这是只读释放而非GPU资格。详见[V15闭环交接](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/CURRENT_PROGRESS_V15_W7_ZERO_GO_CLOSED_W8_STAGED_RELEASE_WATCH.md>)。

## W8原门控实际GO

- root `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_FRESH1CD25_W8_ADMISSION2_20261105_013118_1793813478778262400`。
- source-only stage450/preflight0；新dispatcher一次执行epoch1793814087.6205213/controller1626919。短暂preGO后**真实GO1793814178.5811079 / 01:42:58.581**，parent**1626926**，worker**1627057**；不是第二份bash进程，启动器exec原PID成为glibc/Python。见[首次实际admission](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/reports/FDN_N20000_W8_FRESH1CD_ADMISSION2_20261105_014143/FIRST_ACTUAL_ADMISSION.json>)。
- 原authority2EX/privateGPU0EX/finiteSH/继承FD3,4,5,6/canonical solewriter全部实际true；4090 GPU-16828f91-2b45-b646-8dc0-9481138e2842、free24203MiB/util0/noapps、RAM532246949888/disk250367475712。不旁路锁/改账/扩预算/退款/外部signal。
- 固定save deadline1793817778.5811079 / 02:42:58，nominal end1793818078.5811079 / 02:47:58，都是原上界，不是ETA；Task/pilot cap25未改。OWNER_CURRENT通用描述仍显示max_new_policy_iterations300，并非该Task的25上限，不据此改密封运行源。
- native初始化fresh20000已实际发生；首次正更新epoch1793814604.5198047 / 01:50:04.519观察到。旧PREGO Errno11 epoch1793814148早于GO，不是当前仍等资源。

## 一次冻结的真实10轮证据

[首个固定实训proof](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_N20000_W8_FRESH1CD_FIRST_REAL_TRAINING_EVIDENCE.json>)由[metadata-only处理器](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/freeze_fudan_fresh1cd_w8_first_real_metadata_once.py>)一次创建，绝不随健康进度重写：

- 新PPO **10**、两Adam各**200**、优化转移**9,600,000**；base全0，本分支累计也是10，不拼旧205/43090。
- 原1cd实际源14715029B/SHA1cd…/source_iter43090仅历史标签；physical_byte_opens/SHA_calculations/CPU_decodes各1，整源CPU/raw强保留、版本未变、MLP-only/未应用旧optimizer/DR/iter均true；bad candidate reads0。训练读取mother1与未来评测不重开mother0分别记账。
- 当前native480控制/9,600,000真实转移/3840physics/960feedback/480termination，与N20000、8/2物理链一致。
- 实际本次梯度finite=true、分组separated=true；该轮参数L2变化actor .0068446095、critic .0311394402、encoder .7995062997、log_std .0001195716。实际adaptive main LR1e-5、encoder_loss .28373497、KL .00693987仅描述，不在本次run中改算法/超参。
- 内部functional_metrics.native_training_evidence=false是core功能层的原边界；外层actual_native_training_update/真实SDK callback链为true，不冒称CPU fixture原生训练。
- global episode20.0 + 已绑定低位8s/time_outTrue/400controls实际配置保持；training_task_summary不是独立技能分数。window仍在运行，尚无本分支完整收口/评测结果，不据10轮晋升。

## 唯一后续执行路径

**唯一活跃host job pwsh-91f1d23a513944ec**，[W8 collector](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/collect_fudan_fresh1cd_w8_admission2_window_once.py>)6000s/15s own metadata；不要另开PPO/collector/Cwatch/model/raw状态检查。

等新候选完整保存、原inner/outer actualwait、结清释放、无错误资格后，用已备妥Root4：[N80 stage](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/stage_fudan_fresh1cd_frozen_original_once.py>)、[pi-only导出](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/export_fudan_fresh1cd_pi_for_mujoco_once.py>)、[N80 dispatcher](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/dispatch_fudan_fresh1cd_frozen_original_once.py>)、[匹配V4_FRESH1CD的collector](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/collect_fudan_fresh1cd_frozen_original_once.py>)、[同五姿MuJoCo](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/evaluate_fudan_fresh1cd_pi_mujoco31_lowrise_once.py>)。这些物理后续尚未执行；仅14pi，完整20k源CPU缓存，原N80/160/seed20260928/74+6/fullDR/一fresh reset/0optimizer，评测不装低8timeout。名义MuJoCo仍非硬件或fullDR验收，不以双方0/5抹平身体高度与漂移差异。

## Git边界

最新核验7ee034128525a83dc3a33284bfe219eece934e26/trial-20261105-e3-fudan-fresh1cd25-original-admission/annotated486f39ce9db04c9fde78d211119be0875d328637，423source entries，原feature/tag/peel一致、main只读；它是前期W7原提交，不是本次native证据。W7真实timeout、释放watch、W8新stage/GO与本固定10proof暂待下一有意义闭环合并archive，优先实际有限训练和质量，不给健康每5轮造tag。原record_experiment全校验＋短2pathspec/full staged-set核对；所有模型/raw/JSONL/geometry在stat/read/hash前跳过，不为Git重跑物理或旧once。
