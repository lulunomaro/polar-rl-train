# 全九专家MOD4v2迁移：原失败保留，新A3共享native门控

用户已授权全部正式旧专家（含H1）独立迁移至MOD4v2-HW300N60，寻找86之外两张空闲卡；不是只E3、不是九个20k硬塞一张卡，也不是混合normalizer/共享策略。Goal `goal-66401185-a681-4648-bbf9-a61b6c33d704` active，整体迁移/技能评测尚未完成。

## 正式源与硬边界

[源计划](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/SOURCE_NINE_PLAN_V1.json>)来自当前九源selection/Registryv12 scoped best：E0/C878/C113/S135取已选20-PPO候选，E2/E3/W35/S50保母版，H1取typed71db。E3不是未晋升Fudan8e；H1本轮新迁移候选不覆盖母版。所有源尚未成功读入本轮learner，无新模型/Registry毕业。E0与S50完整接受grader缺项仍null，不能编通过。

实际D0目标为USD2237070d…/contract00199c26…：四主动+四跟随连续、CAD单侧等效止挡、气簧140～200mm/300N；k2000/d3仍未实测工程近似，不把旧400N环境态恢复进新v2。原35/38/6与各族PPO/奖励/命令/N20000×24保持。兼容完整learner/STD/normalizer/Adam17/LR/iter继承，全部未知和旧env/phase/RNG/terrain/history/queues仅CPU历史保留；新v2用原类原规则sole fresh reset。C113新spawn后原bind生成inward，H1新Step270相位。跨D0不称整环境exactresume。

## 已发生的独立尝试

1. 首目的 `MOD4V2_NINE_FULL_LEARNER_MIGRATION_20261105_203701_1793882221738932800`：源stage成功但owner import缺`SCHEDULE_PUBLIC.json`，controller1672459/owner1672466实际wait rc1；OWNER_STARTED/GO/SDK/PT/learner/更新均无。原error和实际owner源码保留，[首失败真相](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/ADMISSION1_PREIMPORT_FAILURE_TRUTH.json>)；不是训练失败或0%技能。
2. Admission2 `MOD4V2_NINE_FULL_LEARNER_MIGRATION_ADMISSION2_20261105_204602_1793882762331398200`：新增源schedule（不是账本/预算）、GO原max_parent_seconds3900，原门控双卡实际6个GO。E0/C878/W35/E2/E3缺各族launcher JOB_ROOT提前失败；H1已实际构造原生环境，PT前在`left_rocker_pin`机械限位读回校验失败，v1未保存原生数值，原因仍未证实。六角色新PPO0、源PT未载；其余3个E1同族被阻未启动。H1 rc0也被真实FINAL/error/actualwait资格拦截，非成功。controller1672920/owner1672927实际outerwait1793883836.6168563 rc0；原owner全childrenwait/costsettled/authority-private-finite释放均true，errors保留。[A2闭合真相](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/ADMISSION2_CLOSED_FAILURE_TRUTH.json>)及[H1本次SDK日志尾](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/attempts/admission2_H1_startup_tail.log>)。

## 新A3，不改已运行尝试

- [v2迁移worker](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/worker_mod4v2_expert_migration_v2.py>) SHA `3b14cdc1804ac6169d49644691c73dd2de6dba876465564fd4c22946fc607991`：补全原launcher全部私有job/kit/warp路径与真实v2asset alias；对已读取的同一native limits tensor，在断言前被动保存20轴expected/first4/minmax/非有限分类。没有改变1e-6门限、native值、资产或原PPO，不吞实际失败。
- 新owner [原资源账本继承+共享native gate](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/source_owner_v2_native_gate/migration_nine_original_owner_v1.py>)：原gpu/account/authority/实际wait/清理路径保持，仅先H1；只有真实`V2_NATIVE_INITIALIZED`（20000环境、PT0、sole reset后1zero-control=8physics/2feedback及limit/gas/closure通过）才放其余8角色进入原双slot队列。若H1共享native尚失败，本轮其余全部不启动，避免同D0错误重复耗卡。
- A3 stage `MOD4V2_NINE_FULL_LEARNER_MIGRATION_ADMISSION3_20261105_213427_1793885667132871000`：九角色完整非PT runtime/lib/staticNPZ/NPY与v2package，295共享上传文件；Linux原owner import-only预检rc0（非main，不动lock/SDK/model/C），并非native PASS。
- A3已一次dispatch：controller1675216，1793885852.3897357；唯一observer **pwsh-2217adb149594efd**。首metadata1793885856全部GO/native/learner null，原1800资源等待可继续；没有当前PPO证据。不得重放stage/dispatch/collector；后续以同job实际输出为准。
- 冻结N80独立原scope worker也仅源码准备完（SHA4dad61fe…），未调度。必须全训练cohort实际close/wait/costsettle/release后原eval独立资源准入，候选顶层actor不从historical子树偷取旧策略，原E3 74/6、E2同UID、H1Step270、E1端点、W35moving/stand语义不变。

## 源工具失败/资源/Git

本轮还保留：owner生成器初版terminal anchor AssertionError；v2缺源换行SyntaxError；v3通过后补H1集合/原GO3900与production路径/semanticclose；A3 generator在已产owner+stager后遇局部archive行缩进定位ValueError，仅余3CLI由AST行坐标finish生成，未重放原训练。所有本地prepublication失败与源码均在根目录保留，SDK/PT/C0。

原single canonical/charge_values、两authorityEX/privateGPU_EX/finiteSH、reserve86412.86069250107、3900/save3600/headroom300/preGO1800、实际GO到SDKclose+innerouterwait全尾计费不变。只用72两个授权4090UUID，不接86、不发foreign signal、不清锁、不复制账本/退款/扩预算。空闲快照不是lease。

本阶段已feature-only一次归档并真实远端核验：commit **3703a54b2c27d2aa941243d41353d0839ef196f5**，tag **trial-20261105-mod4v2-nine-initial-migration-attempts**，annotated对象 **38f4e461261f4971ddaacbe3b48a303c6873d2bf**；59索引条目/clean/remote branch-tag-peeled一致；当前main只读 **af2ffca10d123a4e1f3643c1d497544f46b53fa0**，未push/reset。原validation/redaction/hash/exact2scoped stagedset保留，不为Git重开PT/raw或重放旧once。archive jobe9fe4b9c150f4d1f completed0/fulloutput collected，此推送后补记下一meaningful阶段捕获，不造无限验证链。

最新A3 own metadata（epoch1793886910.6902897）：controller1675216/owner1675223，原PREGO Err11/partial_locks_held0/SDK_PT_GO_or_canonical_writesfalse，全部GO/native/readback/learner/final仍null，outer未wait。唯一observer2217adb149594efd仍running；原1800窗不延长，未抢占/清锁/改账。没有v2候选成功/新PPO/原科目通过/毕业声明，整体goal仍active。
