# E3复旦历史编码PPO：W2原准入超时已闭环，等原owner真实释放

## 当前直接目标
- 继续E3起身质量训练，对齐已核实的复旦五帧监督速度编码PPO；不是恢复旧SuperMimic/20步PPO任务。goal-c490e4cc-b28b-440e-bde6-30ee956813f0 revision2仍active/armed，max14；尚未完成。
- H1、其他专家、Registry v12与E3已选1cd母模型保持不变。现无本任务原生GPU worker。
- 保留原2c/bae模型、D0–D7、原关节范围/400N-k2000-d3、原C单写计账和全部资源/期限门槛。合法低趴子任务不是视频中整条腿在同一端的完整动作。

## 已有实际结果，不重跑
- FDN W1确已GO，但OrderedDict全根不变性检查在首个control/PPO之前报错。native controls、PPO与双Adam全0；inner/outer wait、原账、leases均结清，实际95.008821 expert-seconds不退款。详细见[W1闭环](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/reports/FDN_W1_20261104_175106/CLOSED_RESULT.json>)。
- 新V2只修Mapping识别和父进程semantic失败传播，唯一小CPU回归PASS；旧core合成测试和新的冻结mean合成测试也均已运行一次并保留结果，全部不再重跑。CPU测试不是原生学习或技能通过。
- W2非PT stage/dispatch/collector均已消费，450文件封装，原始1800秒preGO等待最终实际超时。没有worker身份/GO/新候选；producer更新计数null，阶段证据为未进入原生学习，不伪造生产计数或0%技能分数。

## W2实际闭环（已收集）
- remote root `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_SEQ_PPO_LOWRise_W2_MAPPING_20261104_180245_1793786565596043500`。
- outer controller1610275、original owner1610282。原父error为`TimeoutError: Original preGOresourcewait1800expired`，不是策略/奖励失败；外层actual child.wait RC0且original_owner_reaped=true不代表开训成功。
- 原父terminal epoch1793788425.5115132，outer actual wait1793788425.5198138；all_own_children_waited、original_cost_settled、original_leases_released均true。
- [W2原始闭环报告](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/reports/FDN_W2_20261104_180353/CLOSED_RESULT.json>)。原observer `pwsh-43cf684a498c4a05`已完成且output已收集，禁止重放W2 stage/dispatch/collector/root。

## 等待原因与唯一新观察者
- 18:22按原schema精化的只读快照显示C.active_segment由`MOD4V1_SCUT_RIGHT_ANGLE_STAIRS_FULLSTATE_20000ENV_1H_1793785460959945700`持有，PID1609081。GPU0空闲也未绕过该owner。该owner快照是历史，不当作当前锁/显卡证明。
- W2已经闭环后，另起一个纯metadata只读观察者`pwsh-f15e356bfa1f4250`，[源码](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/watch_original_authority_after_w2_once.py>)；30秒间隔、最多1800秒，观察原canonical owner=None。它不延长/重开W2、不加锁、不查GPU、不读模型、不写C、不创建SDK/训练。
- 预期结果文件为`FDN_AFTER_W2_ORIGINAL_AUTHORITY_WATCH_RESULT.json`（完成前不宣称存在）。收集此job后若观察到C owner=None，仍须全新purpose/root的原父fresh gates重新验证authority/private GPU/finite-env和余量；不能仅凭观察者直接认定准入。

## 推理/测评接线
- [冻结pi-only适配器](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/source_fudan_frozen_mean_v1/README.md>)定稿，whole N4096训练根只留CPU身份缓存，部署actor+encoder14张量、82,505参数，无critic/Adam或训练态切片。initialize(raw35)→act→observe(returned noisy raw35,done)。唯一N80×9合成mean误差全0；默认正native/bothAdam验证会排除零更新fixture。
- 唯一子agent3b92c2b6-8850-4ad3-857f-77fc0e518590继续一个明确源码实现子任务：source_fudan_frozen_native_eval_v1（尚未完成/未staged），保持原N80/160 controls/seed20260928/74首episode+6normal，不加PoseV4、不改原物理/DR/控制/分母，只接新的FDN cache/mean与必要close证据；无SSH/PT/SDK/GPU/新CPU测试/Git。父需审最小diff再新purpose实际测评。
- 目前没有成功FDN新训练保存或独立技能结果；新增合法低趴8秒和31体MuJoCo实际行为评估也待候选产生后进行。

## Git（本阶段源码、失败与旧演示已同步）
- feature `mod4v1-experts-fulldr-rm70`，commit `9e11cc7039bbc4a027f022193d09e02dad825dd3`。
- annotated trial `trial-20261104-e3-fudan-sequence-lowrise-native-w1-fix-w2-admission`，tag object `4837188598edf56438fb84a0cabf80bf26be2953`；远端branch/tag/peeled tag均实际匹配，main仅只读。
- 原archive已创建commit后首次push RC1；其stderr被原wrapper遮蔽，具体原因未知。只重推了同一已建commit/tag并成功，未重跑record/tag/任何物理任务。
- [同步真值回执](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/GIT_FIRST_NATIVE_STAGE_SYNC_RECEIPT.json>)、W2超时闭环、这个handoff、新只读watch和后续评测接线等为9e11之后的新文本，待下一个实际阶段合并归档，避免为健康回执反复造trial。大模型/旧raw/media/geometry仍skip-before-stat/read/hash，main从不push/reset。

## 继续顺序
1. 不新增重复观察者；收集现有纯metadata release watch，期间接收并审唯一agent的新原74评测代码。
2. 原owner实际释放后，以新Admission purpose/root派生已修V2的stage/dispatch/collector，源worker/owner物理与账本逻辑不改；原父fresh gates最终决定GO。W2模板要先读再派生，确保所有FDN_W3/Admission输出命名隔离，禁止覆盖W1/W2。
3. 只报告实际GO、native counters与完整保存；完成原actual waits/成本/释放后，独立原74和新增合法低趴/31体行为评测，依据实际质量决定保留，不以CPU/PID/更新数冒充站起。
