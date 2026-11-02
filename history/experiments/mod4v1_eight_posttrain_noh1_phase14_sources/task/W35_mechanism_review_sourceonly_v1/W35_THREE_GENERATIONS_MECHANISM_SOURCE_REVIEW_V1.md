# W35三代失败机制审查（SOURCE_ONLY）

## 源码carrier说明
安装源mod4_task的原remote SHA为`30ce41126a1a9b78a1c2b446281b28f4555c28052bfaa7c0e9a76079cf561fc5`。本地collector carrier为108499B/SHA`2e8037bf470800c7be671af3f33542a8ff1e69358674dba16c35e815327c848c`，含1896处CRCRLF；原AST错误完整保留。仅在reader内存恢复CRLF即得106603B和精确安装SHA，AST通过；原carrier/receipt/运行源均未修改，这不是SDK运行错误。[完整ledger](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/W35_mechanism_review_sourceonly_v1/SOURCE_READER_EOL_AND_LOOKUP_LEDGER_V1.json>)。

## 结论
1. **目标不等价已由源码确认**：原训练是20%站立、BODY vx[-.3,.3]、vy/yaw=0、12–16s自然重采样；固定opposite-end catalog goal仅observer，不在actor输入、命令或当前奖励。goal0不是单独的演员/执行器故障证明。
2. **高命令持续跟踪短板仍在**：三代高档完整interval8836→9122→8948，原boundsmet均0；最新高档为.1–.2的4433与.2–.3的4515。moving3955个met均来自低于.1档，不增总体毕业率。
3. **未证固定.04cap/轴反/STD错/障碍卡住**：历史89aca32witness的1s高cmd7/7同向、bodyvx均值.24697，与最新8d全32s未配对，不可拿瞬时小样本或均值差当因果。
4. **首要测量缺口是同源同帧getter/phase**：begin用root_pos_w/heading_w，terrain termination后clone root_state_w作为终帧；control*.02、+8物理回调无直接8倍语法错。SDK rootlink/COM/packedcache实现及timestamp尚未join；xyzw是已部署source合同，不是本轮同帧heading实测验证。
5. **下一步仅一项新purpose observer**，不空泛续训、不预先改geometry/reward/STD/limits/植物。

## 源码钉明的结构与数值
- COURSE_X=[5.5,9.5]、Y=[5.4050269442,7.4958804143]；原旧2m边界确已被wholecourse boundary替换。偶数从5.85/yaw0，奇数从9.15/yawπ，外端余量仅.35m；signed负BODY命令在这些初态朝外。
- 在first-reset、axis=x、v≥.1、自然T≥12s的明确前提下，原沿向容差至少要求(.1-.03)*12=.84m，但外向最多.35m。因此“留在场内且自然完整且满足沿向bounds”的部分命令有结构冲突/选择偏差；不把此推至全部8948，也不编未观测cohort数。
- 反例：理想向内.3m/s到对侧目标中心3.3m约11s，到.35m目标圆入口约9.833s，20s单episode内可达；不存在已证全体不可达。
- 当前original_reason_counts：time_out14749、rough_route_boundary25520、base_contact88、closure/mimic0；timeout union40256保留，不直接求和。16个processed route例缺对应command history与yextrema，不泛化全部60335路线。
- 原velocity reward确对匹配有正压力：wide exp(-e²/.25)+.2 tight exp(-e²/.01)-(.25e)²-I(e²>.5)，e=BODYvx-rootvBx*cosPitch；不能因huge_gap对静止.3不触发，就称整个速度奖励无效。实际per-UID竞争/动作/接触尚缺。
- 父单读训练scalar的81条32562..32642并非82全KL历史；rolling/coldstart下reward/episode_length上涨不当能力因果。generic success1只看到alias，不从comment编阈值。最终8d32643/17Adam654500、自身cached LR1e-5与末log float32 LR.000113906...并列保留，不按parent89aca重置。

## 最小下一observer（未执行、非GO）
建议独立18s/900control/7200physics/1800feedback、全20k完整源state+ONEfreshreset，16个按原自然命令/奇偶确定的witness；覆盖原12–16s首自然命令，截断/重置与缺bin照存。旧32s once/raw均不再读。
- 钉实际SDK getter实现/point-of-reference/cachetimestamp；只tap已自然读取值，不额外compute、刷新query、采RNG或第二actor调用。
- 记录每个sameUID的B_i=root_pos_before、T_i=frame_root_terminal、下一B_(i+1)。纯代数 D_obs=Σ(T_i-B_i)，G=Σ(B_(i+1)-T_i)，D_endpoint=T_last-B_first=D_obs+G；跨reset不拼。G显著承载位移时优先查混合getter/phase，不把旧along乘8或翻quat。
- 同frame q分别离线算xyzw/wxyz yaw，对照同phase自然heading_w及tick；不自动换order。
- 将同一点的world速度积分/或R(q)v_body与位移对照；link/COM须用已知ω×Rr修正，400Hz自然缓存可用性未证时只标100Hz采样近似与缺字段，不新增微米级门槛。
- 原boundary函数返回时tap xlow/xhigh/ylow/yhigh和localxy/timer/episode_age；同UID对齐actor→processed→delay→actualtarget→轮速/力矩/接触→bodyv/pose→自然reward term，区分策略后段停/轮动不走/坐标时序/出界censor。
保持2c/bae、closure.01/mimic.01、400N/2000、50/100Hz、.0025/TGS32/4；原预算lastsnapshot仅说明历史，非当前admission。无任何新PPO授权/预算/GO；后续若另有原owner批准训练，完整存、原LR/STD17Adam/RNG/queue、wait/release边界照旧。

## 完整参考（路径/SHA；JSON与原函数见机器报告）
- **THREE32** [W35_THREE_GENERATIONS_FULL32_DECISION_V1.json](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports/W35_THREE_GENERATIONS_FULL32_DECISION_V1.json>) `481e39afc78ff8824229759953080ae7e1ff8c151adeaf3024c1112205e61560`
- **NEW8D_PROCESSED** [W35_after_resume89aca_own_raw_CPU_20261102_080042.json](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports/W35_after_resume89aca_own_raw_CPU_20261102_080042.json>) `87d730c2a973c88000349a974417f9fbc136435d701184bbfbeef82f522da11d`
- **NEW8D_TERMINAL** [W35_after_resume89aca_eval_terminal_watch_20261102_080039.json](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports/W35_after_resume89aca_eval_terminal_watch_20261102_080039.json>) `9c323db4d9ba6eaed4a326f7d20d7eefd8ab8664306256b78716de5b34ae1586`
- **TWO32HIST** [W35_FULL32_BEFORE_AFTER_PPO80_DECISION_V1.json](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports/W35_FULL32_BEFORE_AFTER_PPO80_DECISION_V1.json>) `a3e8da421c65b1ccb8b936fcc1e4d242e7d0bdc4bc70601716a95c6329bdae05`
- **SIGNED_TRACE** [W35_MOTION_TRACE_SIGNED_CHECK_V2.json](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports/W35_MOTION_TRACE_SIGNED_CHECK_V2.json>) `ffa1416514585f07f2199a75d20fc8d36150eff24d1dfda038abcb017c06594f`
- **MECHANISTIC_TRACE** [W35_MOTION_TRACE_MECHANISTIC_ANALYSIS_V1.json](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports/W35_MOTION_TRACE_MECHANISTIC_ANALYSIS_V1.json>) `d8eae348097b456f28013a5e4c8038ede23f7daec1f1bad9cf7308dd7096701c`
- **TB_PROCESSED** [W35_RESUME82_OWN_TB_SCALARS_CPU_20261102_074555.json](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports/W35_RESUME82_OWN_TB_SCALARS_CPU_20261102_074555.json>) `165cda78a54e26d358254b9cfbd325e637f25f9ae84b871710f45a40546eed2c`
- **TB_SCOPE** [W35_RESUME82_TRAINING_SCALAR_SCOPE_NOTE_V1.json](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports/W35_RESUME82_TRAINING_SCALAR_SCOPE_NOTE_V1.json>) `79a4c3d0ddad99e08629cb5700080960422108f1f40ba1846d4d13da540983b1`
- **MOTHER_MANIFEST** [INSTALL227_SOURCE_ROWS_FROZEN.json](<C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/W35_RM70_QUALIFIED_CONTINUATION_AND_LOSSLESS_EVAL_SOURCE_V227_20261101/A_PPO_SOURCE/reports/INSTALL227_SOURCE_ROWS_FROZEN.json>) `a98d311a76054fde66798b6ab0134a02ece8b1c6c132e8351d4c26a99ec61cad`
- **V4_SOURCE_INDEX** [MOD4V1_DERIVATION_INDEX.json](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/W35_MOD4V1_RESUME89ACA_SOURCE_V4/MOD4V1_DERIVATION_INDEX.json>) `32fc98c8c78e43846780fb33d822459c6d34f60c38b68bda50b6c3975adfb0f7`
- **OVERLAY_MAP** [INSTALL_OVERLAY_SOURCE_MAP.json](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/W35_MOD4V1_RESUME89ACA_SOURCE_V4/INSTALL_OVERLAY_SOURCE_MAP.json>) `f395d1c0bfb7b464ee859cb7fd5ea2ac965a722b50ea1c6f7e0c9a9624c456fc`
- **ANCESTRY_V2** [MOD4V1_DERIVATION_INDEX.json](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/W35_MOD4V1_SOURCE_V2_FINAL/MOD4V1_DERIVATION_INDEX.json>) `1fbf489facb03e470c175fde8b2182c5a45a54b5978c117d16074d2fee69c6a0`
- **EVAL_SOURCE_INDEX** [SOURCE_ONLY_INDEX.json](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/W35_MOD4V1_AFTER_RESUME89ACA_EVAL_V2/SOURCE_ONLY_INDEX.json>) `9753891f9ad3fedb7363ff93b496e1dfe04bfa8803d1e23903fb5738ed29900b`
- **ORIGINAL_ENV** [W35_original_run_manifest_frozen_v1.json](<C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/W35_PPO50_gas400_source_preparation_20261027/W35_original_run_manifest_frozen_v1.json>) `0543b0c47c53e15da0d7d017693d2b69f7f6354ef088c3a1b8ed2b9cc56e2beb`
- **TRAIN_ENTRY** [train_mod4v1_w35.py](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/W35_MOD4V1_RESUME89ACA_SOURCE_V4/runtime/isaac/mod4/train_mod4v1_w35.py>) `bbda08da09bbb12cae8b80e8ff9be2b7a1f19dddd42200d5ec2bdfb6bca45ee2`
- **TRAIN_WORKER** [worker_mod4v1_w35.py](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/W35_MOD4V1_RESUME89ACA_SOURCE_V4/worker_mod4v1_w35.py>) `2c72efeafc2873c46f4ffd6c748587721fe65187f3a917269c5a85c70702dd07`
- **EVAL_WORKER** [evaluate_mod4v1_w35.py](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/W35_MOD4V1_AFTER_RESUME89ACA_EVAL_V2/evaluate_mod4v1_w35.py>) `0091a0a4147154c5167be5a7aa4df6c165e4e8e9c56141db05f7494e8af5f637`
- **INTERVALS** [rm70_intervals227.py](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/W35_MOD4V1_AFTER_RESUME89ACA_EVAL_V2/rm70_intervals227.py>) `d84182d3675f41d53d35da54c4d80519b9b2280ccb6d3f47f33cfff64029d609`
- **CONFIG** [config_mod4v1_w35.py](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/W35_MOD4V1_RESUME89ACA_SOURCE_V4/runtime/isaac/mod4/config_mod4v1_w35.py>) `f29bad90424486c1f88c4567e0a8180516d30e6bb01e411c9846dfdcee94488f`
- **RESET** [reset208_v3.py](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/W35_MOD4V1_RESUME89ACA_SOURCE_V4/runtime/isaac/mod4/reset208_v3.py>) `f4d4812ceb8b3bf13b3febe6df3ee397b484824c6bc2b3b64b966f6ce91d390b`
- **CURRENT_HEALTH** [e1_terrain_training_health.py](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/W35_MOD4V1_RESUME89ACA_SOURCE_V4/runtime/isaac/mod4/e1_terrain_training_health.py>) `deaacba91ac74a44c9a73381babecb2a89745eda6e14ea053982d0e75355cddc`
- **COURSE** [course_math208.py](<C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/W35_FULL_RM70_EXPERT_NORMALIZATION_SOURCE_V208_20261031/source/course_math208.py>) `19013a43708197cf5dd6b944b22c25edd53b1562c670afbb22f75cee0e18e606`
- **COMMAND** [command208_v3.py](<C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/W35_FULL_RM70_EXPERT_NORMALIZATION_SOURCE_V208_20261031/adapter_v3/command208_v3.py>) `8ba19772a2d8b0c9a5082d2bfb21f58a74bb000ab4ef34899f7f2428eea05e30`
- **TERRAIN** [terrain208_v3.py](<C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/W35_FULL_RM70_EXPERT_NORMALIZATION_SOURCE_V208_20261031/adapter_v3/terrain208_v3.py>) `5f6abfdc4b2f72c9c960df27107e0aae746eb3498693b663addc5782d85d17dc`
- **LEARNING** [learning208_v3.py](<C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/W35_FULL_RM70_EXPERT_NORMALIZATION_SOURCE_V208_20261031/adapter_v3/learning208_v3.py>) `a278e3839513f2b592e840afc07bbc94ea24263fe802a1ba5b5375aaaf06b335`
- **BASE_LEARN** [base_learning208_v3.py](<C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/W35_FULL_RM70_EXPERT_NORMALIZATION_SOURCE_V208_20261031/adapter_v3/base_learning208_v3.py>) `634d9b83a0c45382871ef43f25d4e2a50a8df8f7192a5a1fd1e865adbb6531d9`
- **EVIDENCE** [evidence208_v3.py](<C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/W35_FULL_RM70_EXPERT_NORMALIZATION_SOURCE_V208_20261031/adapter_v3/evidence208_v3.py>) `a1a2a57329d06805ee1b14cd96f902a22ba94a0292c2f1305e7316747eba53aa`
- **INSTALLED_MOD4_TASK** [mod4_task.py](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/diagnostics/W35_RESUME82_SCALAR_EMITTER_SOURCE_V1/runtime/isaac/mod4/mod4_task.py>) `2e8037bf470800c7be671af3f33542a8ff1e69358674dba16c35e815327c848c`
- **REWARD_FORMULAS** [scut_flat_rescue.py](<C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/W35_PPO50_gas400_source_preparation_20261027/runtime_candidate_v1/isaac/mod4/scut_flat_rescue.py>) `f547175ed1f46c3eb546507b1eff634ecfd757de62bbe1e72387fbf0c98e34ef`
- **DIRECTIONAL_ANCESTOR** [directional_spin_runtime.py](<C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/W35_PPO50_gas400_source_preparation_20261027/runtime_candidate_v1/isaac/mod4/directional_spin_runtime.py>) `8fed717b0d2ba77491c252b183f9462f49457402d96927cc441c88ecd36b1cd8`
- **ACT_DELAY** [action_delay_sdk_adapter.py](<C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/W35_PPO50_gas400_source_preparation_20261027/runtime_candidate_v1/isaac/mod4/action_delay_sdk_adapter.py>) `ecd1db05a0dfe215cdf089ccf346aea1a5c51d7974a2bcd6e486dff66b7f5494`
- **QUEUE** [action_delay_physics_queue.py](<C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/W35_PPO50_gas400_source_preparation_20261027/runtime_candidate_v1/isaac/mod4/action_delay_physics_queue.py>) `a4238c581611ef7cdb710692291ddac48e076364b0587f631eb71fd6a7d15eb8`
- **EXPLICIT_PD** [explicit_pd_sdk_adapter.py](<C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/W35_PPO50_gas400_source_preparation_20261027/runtime_candidate_v1/isaac/mod4/explicit_pd_sdk_adapter.py>) `e9995ecd802f26cae1061a9540efdea1b34ae143bdfc9c8619508c560b438ae3`
- **MOD4_ENV** [mod4_env.py](<C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/W35_PPO50_gas400_source_preparation_20261027/runtime_candidate_v1/isaac/mod4/mod4_env.py>) `b7dede4c8f587b0b69d1b56e125a9e544045da66a50660be9861daeb5fccb307`
