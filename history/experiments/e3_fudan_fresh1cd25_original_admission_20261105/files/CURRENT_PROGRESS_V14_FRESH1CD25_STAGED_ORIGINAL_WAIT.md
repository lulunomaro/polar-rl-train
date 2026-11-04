# V14 — 1cd仅MLP warm / fresh Fudan / N20000×25 pilot，原父已提交

## 目标与已有质量结论

- 当前goal `goal-c490e4cc-b28b-440e-bde6-30ee956813f0` revision3 active/armed/max14；只推进E3起身质量，未完成，不按更新数毕业。H1/其它专家/Registryv12/冻结1cd保持。
- 上个W6实际N20000/T48 closed72、完整learner累计205已全部真实收口/结清/释放；原N80执行资格为true但0/74，normal物理终止0/6；名义MuJoCo五姿双方0/5，新候选高度.182897/速度.391495/位移3.020520，母版.241437/.038073/.639393。保留母版，不晋升3e64。
- 该闭环、reader仅kind版本误报+metadata纠正、完整MuJoCo与决定已Git推送核验：7ad15203471201e1534dbc82ba85ee6bfc99f69c，trial-20261105-e3-fudan-timeout8-closed72-quality-keep-mother，annotated222aa5c294f7d0117c0dbd1547940c1175da5002；main只读核验，未重放物理。详见[质量报告](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_TIMEOUT8_CLOSED72_QUALITY_RESULTS_V1.md>)。

## 本次单一干预（不是继续坏候选）

- 仅原1cd actor8＋critic8 MLP warm；encoder fresh随机、新latent列0、STD .5、LR/两Adam/private generator/计数全fresh。原43090只作来源迭代标签，继承迭代0；8af4/3e64模型、Adam、历史、计数读取/应用0。
- Schema4，branch `FRESH_FUDAN_MLP_WARM_FROM1CD_N20000_TIMEOUT8`，source_kind `fdn_fresh_mlp_warm_1cd_n20000_timeout8`，base四项0，window==本次counters，full_learner_resume=false；自身新保存仍是含完整learner/两Adam/RNG/typed环境的完整保存。
- 新真正N20000/T48，每PPO两Adam各20/960000优化转移；本pilot上限25（不是已完成25），保存后按原范围实测，不拼旧205。保持Fudan core、5帧175→latent3、actor38/critic41、物理/fullDR/50-100-.0025/400N-k2000-d3不改；复用既有8571B/386107…低位8s/400控制timeout。

## 已实际执行的stage与原父提交

- 新root：`/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_FRESH1CD25_W7_20261105_005638_1793811398919144400`。
- Stage完整nonPT runtime/lib/assets/staticNPZ，共450源文件；原owner source-only preflight RC0，模型/SDK/GPU/GO/C操作0。旧source静态`invalid escape \\S` warning保留，非本次native错误。
- [stage准备入口](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/prepare_stage_fudan_fresh1cd_w7_once.py>)、[原父dispatcher](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/dispatch_fudan_fresh1cd_w7_original_owner_once.py>)均已消费，不得重放。dispatcher epoch1793811419.9556985 / controller1625502，只是原父提交，不代表已GO或开训。
- 唯一observer **pwsh-8166db58c67945b0**，6000s/15s只看own metadata，不开模型/raw/旧JSONL/C，不发signal。最后公开输出epoch1793811436.6327488：原preGO Errno11资源等待、worker=null、init=false、updates=null。后一次job_output没有新phase；当前无本次实际PPO或质量证据。等待实际phase，不另启observer/parent或读取外国资源。
- 只原canonical authority2EX/privateGPU_EX/train finiteSH；原3900/3600/300、1800preGO、reserve86412.86069250107及charge_values从GO到保存/SDKclose/actual wait均保持。不因GPU空闲绕原owner；不改账/扩预算/退款/清锁/外部signal。

## 源与诚实检查范围

- [v5单worker](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/source_fudan_native_worker_v5_fresh1cd_timeout8/worker_fudan_sequence_ppo_native_v1.py>)743行/47257B/SHA e4d5df2827a2d07d7c880f72bd09e483d4987072c005253c7f93e6b2cccfdeb5。原MotherCache整类/13辅助/原采样update数学及guard保持。子agent单AST通过，20静态True；plant归一器把本应保留20000µs的queue误归一引发1项假阴性，FS逐行核对实际queue仍20000µs，未改源/重跑AST/CPUfixture。
- 新original_owner_v5仅Task/sourcekind/MLP provenance和25上限元数据适配，原gpu/account/environment/main资源等待/actual wait/结清释放AST保持（main只charge_contract描述变化）。新close gate保持原actual wait/typed fullsave/原Appclose所有条件，并核fresh zero-base/1cd一次IO/new25真实计数。新stager只role/sourcekind/max25，完整非PT复制不裁闭包。
- 本地首owner builder因3空格锚点匹配2空格body失败，发生在新目录/输出/SSH/SDK/GO前，旧失败源与[erratum](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_FRESH1CD_OWNER_BUILDER_V1_LOCAL_ANCHOR_ERROR.json>)保留。新v2仅按观察到的原行缩进提取，三新源单AST/compile通过；非native重试。

## 下一步与未执行部分

- child3b92已交付并冻结root4 fresh1cd的7＋3来源模块，单次AST/compile及12项限定静态差异全部通过；仅3份provenance变化，其余7份逐字节一致，14pi/history/clip6/原N80机制不改，无SDK/CPUfixture/PT/SSH。新mean 26412B/SHA b183b7d3b0e168220ffdbdfb9d25187266ee8e62e9b289ce41af59ebc405ea0f；safe21988B/9d3f5dfe1cbaf955670d87a4315d2c67f19d3c2bd638d175ec29e4cb54fb4e89；parent q30030B/206187777e83b6466e0ced15cbfbfb322112b8db71181b9ef937e686379bc785。训练warm mother读取1与评测不重开mother0分开；4个旧输入SHA/path在selected sole read前仅字符串排除，不虚构continuation祖先。child现已结束，未再派工。
- [fresh闭环N80 stage源码](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/stage_fudan_fresh1cd_frozen_original_once.py>)仅生成、未stage/执行，完整原materializer不裁剪。[四入口builder](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/prepare_fudan_fresh1cd_eval_followups_once.py>)已单次执行生成导出/dispatcher/collector/同五姿MuJoCo入口，outer+remote AST/compile通过；collector已显式同步完整kind `FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V4_FRESH1CD`，四个case物理函数AST保持。实际export/N80/MuJoCo均未发生。
- 等原父真实GO/构造/正更新后，只冻结一个首次真实proof；等own inner/outer actual wait＋完整保存/结清释放后，真实原N80/160/seed20260928/74+6与同五合法低姿MuJoCo。原分母/门限不改，0credit不是0reward，不以training描述代替独立质量。
- 7ad1520之后新warm worker、builder纯本地失败/修复、450stage/原父提交与本handoff尚待下一有意义合并archive。feature-only/唯一annotated trial；复用原record_experiment全部校验＋短精确git-add pathspec/full staged-set核对；跳模型/raw/media/geometry于stat/read/hash之前，不为Git重开或重跑，不造无限回执链。
