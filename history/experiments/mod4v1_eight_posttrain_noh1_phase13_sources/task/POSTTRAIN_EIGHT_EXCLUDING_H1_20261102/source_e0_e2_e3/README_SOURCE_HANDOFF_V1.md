# E0 / E2 / E3 有限原 PPO 完整状态接续：SOURCE_ONLY 交付

**本包是源码准备与 stdlib AST/MOCK 审查。实际新训练、GPU、SDK、模型文件访问、canonical、GO、SSH、Git 写入均为 0。H1 严格冻结排除。** 原 canonical owner 负责真实资源/预算准入、GO、持续计账、完整保存、App close、child wait、终末结算。

## 立即可审查的入口

- [共用完整 worker](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_e0_e2_e3/posttrain_fullstate_common_v1.py>)。
- 三条入口：[E0](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_e0_e2_e3/worker_posttrain_e0_v1.py>)、[E2](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_e0_e2_e3/worker_posttrain_e2_v1.py>)、[E3](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_e0_e2_e3/worker_posttrain_e3_v1.py>)。
- 三条固定 metadata、原方法精确路径/签名/行号及旧 actual proof：[E0 descriptor](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_e0_e2_e3/E0_POSTTRAIN_DESCRIPTOR_SOURCE_ONLY_V1.json>)、[E2 descriptor](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_e0_e2_e3/E2_POSTTRAIN_DESCRIPTOR_SOURCE_ONLY_V1.json>)、[E3 descriptor](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_e0_e2_e3/E3_POSTTRAIN_DESCRIPTOR_SOURCE_ONLY_V1.json>)；总入口为[API/proof 索引](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_e0_e2_e3/SOURCE_API_AND_ACTUAL_PROOF_INDEX_V1.json>)。
- [完整父输入字段合同](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_e0_e2_e3/PARENT_REQUIRED_FIELDS_SOURCE_ONLY_V1.json>)与[pure-stdlib Task/GO 字典构造函数](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_e0_e2_e3/construct_source_task_go_v1.py>)。函数只返回字典，原父负责真实 admission 与发布；[MOCK 样例](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_e0_e2_e3/MOCK_SOURCE_CONSTRUCTION_EXAMPLE_V1.json>)显式标注虚拟、epoch=0、owner PID=-1，未创建真实 Task/GO/Ready。

## 原加载/保存调用链

| 角色 | 当前 sealed MOD4v1 trainer（原 trainer 也在机器索引中） | 原 fullstate 方法 | 原 live save installer |
|---|---|---|---|
| E0 | [train_mod4v1_e0](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/E0_MOD4V1_SOURCE_FINAL/runtime/isaac/mod4/train_mod4v1_e0.py#L228-L267>) | `chassis_pd_checkpoint.resume_chassis_pd_new_episode(runner, env, path, log_dir)` | `install_chassis_pd_save_contract(runner, env)` |
| E2 | [train_mod4v1_e2](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/E2_MOD4V1_SOURCE_V1/runtime/isaac/mod4/train_mod4v1_e2.py#L232-L271>) | `e2_command_checkpoint_v1.resume_e2_new_episode(runner, env, path, log_dir)` | `install_e2_save_contract(runner, env)` |
| E3 | [train_mod4v1_e3](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/E3_MOD4V1_SOURCE_FINAL/runtime/isaac/mod4/train_mod4v1_e3.py#L235-L274>) | `e3_fullstate_checkpoint_v1.resume(runner, env, path, log_dir)` | `install(runner, env)` |

每条 `main()` 使用原 `build_env()`、原 `runner_config()` 与原 `OnPolicyRunner`。三条原/派生 `runner_config()` AST 逐节点相同：A0 [256,128,64] ELU、35/38/6、原 scalar STD、5 epochs×4 minibatches、原奖励与 command/task。installed RSL 的源码文件本次未导入；原 live actor/critic/STD/17Adam/iter 恢复的实际依据是原 SENSOR helper/whole20k actual proof，而非本包 mock。

原链为 D7 COM/PD → D6 gas damping → D5 pressure → D4 action queue → D3 feedback queue → sensor/global/named RNG → **ONE 原 startup reset**。E2 再含 nine-field command/private mode RNG，E3 含 seven-field phase/private command RNG、原 fixed13 fall placement。**先新构造器的 nominal mass/COM/inertia，后全20k状态恢复验证，再原 reset；不是切片20k，不是 fresh D0 替代恢复，也不是 PhysX 位姿 exactresume。** 原 reset 按协议清/重采 episode histories，与“保留原全状态进行恢复验证”并不冲突。

## PPO 窗口与完整保存

1. 子包只读父新的 `ROOT_MOD4V1_EIGHT_POSTTRAIN_ACTUAL_ADMISSION_V1` admission/hash、GO、actual install manifest；保原 path/generation、direct parent PID、privateEX/finiteSH、预算 owner 绑定。旧 E0/E2/E3 admission validator 留原字节，未伪造其旧 Ready。
2. Task/GO 明确绑定 `seed=20260928`、`steps_per_env=24`、`num_envs=20000`、integer `max_additional_updates<=20`。原完整源 loader 的 private/global RNG 恢复仍权威；constructor seed 不等于技能 acceptance cohort。
3. 新 live whole20k core/17Adam/source LR/iter、原6/7 helper receipt 与 nominal guard 精确检查后，先保存自己的完整 startup0。旧 native24 proof 只复用引用，本窗口没有额外24步 deterministic 前段。
4. 实际 learn 调用原 `rescue_training.learn(runner, limit, log_dir)`；该原源码调用 `install()`，再调用原 `runner.learn(..., init_at_random_ep_len=True)`。只叠加透明计数/complete-save/finite cap，不替代 PPO 或 BPTT，不改奖励、STD、优化器或 LR schedule。
5. `alg.update`/`optimizer.step` 返回后计数，20/minibatch 一致性仅作核对。原 next-new-update label 约定在 learn 前将实际 live iteration 加1；保存字典的 iter/Adam/LR 全取原 runner/save 实值，**未按算术回填**。deadline/STOP 延续原 finish-update→complete-save 停点，可能 n<20；完整退出前禁止第21次 update/额外 rollout。
6. 先原所有 save contracts 生成 live 完整 artifact；必须已有所有 known live core/history/queue/RNG roots，再 union 保留 source 未知 root/嵌套 dict entries。live cache 赢过 source；list/tuple/tensor 作为完整叶子，无 slice/repeat。新派生 artifact 完整 disk roundtrip+core/cache核验后发布，母本从不覆盖。
7. 失败半个 update 时保留最后 complete artifact 与原错误，不将部分 Adam 进度算作完整 update，不重试/回滚/另开窗口。原 CLOCK health、STOP 原因、stdout 的 capacity/integrity 仍由父独立审查；保存成功和技能通过是不同事实。

## CPU Adam step alias 风险已核源码

三条 [cache helper E0](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/E0_MOD4V1_SOURCE_FINAL/runtime/isaac/mod4/source_cache208_v3.py#L34-L41>) / [E2](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/E2_MOD4V1_SOURCE_V1/runtime/isaac/mod4/source_cache208_v3.py#L34-L41>) / [E3](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/E3_MOD4V1_SOURCE_FINAL/runtime/isaac/mod4/source_cache208_v3.py#L34-L41>) 均是 3873B、SHA `4047d6769fa2e10174e58addeeafeb533e71aed4b1fc018d76448b0f21c5952b`。

- L39 返回 `copy.deepcopy(self.state)`，保完整 root，不把 immutable truth 直接传给 runner/DR helper。
- `runner_source_load_scope` L88–100 在 L93–94 将 exact 源路径的 runner `torch.load` 路由该 deepcopy；其余 own artifact 走原 loader。
- 新 worker 另做全 root RAM deepcopy 快照，startup/每次 complete save/训练后比较 cached truth 不变。保存未知 root 的底本一直是 immutable cache truth，审计不额外开/解码母本。
- [最终 AST/MOCK 报告](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_e0_e2_e3/AST_MOCK_REVIEW_V2_WITH_CACHE_ALIAS_AND_CONSTRUCTOR.json>)用实际 cache helper 代码 + `FakeMutable` 模拟17个原地 step 与未知 root/cache 修改，runner/DR工作副本均隔离；没有导入真实 Torch，不冒称 Torch/SDK 实测。

## Stage 要点

- 使用每条原完整20k runtime + sealed MOD4v1 overlay；历史实际 remote 根路径和 local collection 已放 descriptor。只复制非模型 runtime 与 immutable metadata，换新 unused owner 根，跳过旧 consumed Kit/production/Task/GO/once。
- `MOD4V1_ASSET_DIFF.json` 必须在新 **job owner 根**，与原 derivation index/manifest 一起；helper 本来就在此读它。
- Kit storage 严格为 owner 根下 `kit_isolation`，由 worker SDK前建立，沿原 launcher 20行源码；不是 eval 子目录。
- 继续原 .0025/TGS32,4/50Hz policy/100Hz feedback、10mm closure、.01 mimic、400N/k2000/d3，绑定 2c421a8e/bae3203a。没有 N80 small-GPU PhysX capacity preset。
- 只用真实 `FeedbackDelay.delay`。本三条没有 G4 import；四 E1 的 G4 依赖闭合由相应负责者处理，不混入本 package。

## 技能与证据边界

- E0：N80诊断普通跌倒/闭链/mimic reset0，vxMAE .03950337、yawMAE .10586448；缺原整体毕业规则。
- E2：原世界2pi联合谓词0/187 与 body-vx误差约 .0455 分开保留；world getter 时序/参考点独立验证 gap 不改写成新奖励/目标。
- E3：初始跌倒74、stable credited0/74，normal6不入分母；stable50 public100Hz age units=.5s，request300=3s，13fixedrecipes。`delta>0` 不是 stable credit。
- 本次授权目标是尽量保持/恢复技能，不宣原三条均已毕业。新 checkpoint 之后的原谓词独立回放由父负责。

## 审查与归档

[AST/mock 测试源码](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_e0_e2_e3/check_ast_mock_v1.py>)当前8组全过，包含原 bounded-learn source 的纯虚拟路径 mock、20/3-deadline/1 update、完整 live-save roots 检查、未知字段保留与 cache alias 回归。历史第一轮6组报告保留为[初轮审查](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_e0_e2_e3/AST_MOCK_REVIEW_V1.json>)。mock不是SDK通过。

所有修改均在本 child 根。catalog 只有 Office/ACL，无 RL/SSH 匹配技能；使用 host FS 和 `-S -B` stdlib Python，没有无关插件/子 agents。失败/修复与补充均有局部索引，供父统一 Git 归档；child 没有 commit/push 或编辑父/他 child/旧 sealed/once。
