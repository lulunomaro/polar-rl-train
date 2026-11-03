# V3 独立 SOURCE 审阅

**结论：`SOURCE_REVIEW_PASS_NOT_NATIVE_OR_QUALITY_QUALIFIED`；已确认 SOURCE blocker 为 0。** 本轮仅准备 holdout SOURCE，不启动 native、不构成新 native 授权。完整机读证据及十成员 PIN 见 [SOURCE_REVIEW.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_v3_parent_review_v1/SOURCE_REVIEW.json>)。

## 固定输入与独立复核

| 实际文件 | bytes | SHA256 |
|---|---:|---|
| [SOURCE_SEAL.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v3/SOURCE_SEAL.json>) | 2034 | `0777c2e284d339ffc9c658a92188ee8c2ebb491c82d4124330a794f68654f426` |
| [stage_good_expert_holdout_v3.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v3/stage_good_expert_holdout_v3.py>) | 53062 | `a7eca32d8efc510ba4529b8be7c2b64d7de936f110a4eff4d847925024f43b11` |
| [test_good_holdout_v3_source.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v3/test_good_holdout_v3_source.py>) | 37330 | `faf1fa3b82e43083431e56f19fa08928cfab7d67dddacac5d6a8e70074e37c7e` |

- 十成员及 seal 共 11 文件实核通过；root 为 `1cdd8c72dfdc9fbb3b75f4068f53e8f489d7d558c79a637f39597efae8e765cd`。
- 79 mirror = 旧 67 原样 + V2 九成员及 seal 共 10 + operational-gap MD/JSON 两项；均为 WORKSPACE 下 R/T siblings 的限定小来源。连新 11 共 **90 输入**，全部 bytes/SHA 实核且测试前后相同；解析 **59 Python AST / 25 JSON**。
- 90 输入排序身份集合 SHA256：`e0678156caa350d2008dabdb5c4b716fe6f0fabb210f81cdb2faf5a8f0bbba71`；算法为 `SHA256(sorted workspace_relative TAB bytes TAB SHA256 LF)`。
- V2→V3 仅改 `preflight_summary/stage` 并新增一个纯 helper；其余 **28 完整函数 AST 及函数源码逐字相同**。V1 原有 **22 完整函数**亦逐字/AST相同。非函数差异仅模块说明与版本常量；上游 index 其余字段、完整 20 overlay、原 parent/runtime PIN 未动。

## 派生与发布：SOURCE 上成立的范围

- [纯派生 helper:630–687](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v3/stage_good_expert_holdout_v3.py#L630-L687>) 核对原 SOURCE 编码/262144B 上限、四标志严格 False、两独立 seed/purpose、完整八角色 catalog/两个 selected/六 deferred、固定 27 依赖、独立 original→retained→observed 身份、完整 observed 集合和 typed bytes/SHA。深拷贝只将 `enabled/staged` 置 True；复原两字段后必须与 SOURCE plan 完全相等。无 I/O、新 approval/GO、C 或隐式准入。
- [stage:690–737](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v3/stage_good_expert_holdout_v3.py#L690-L737>) 完整 copy/hash/flush/fsync loop 与 V2 AST 相同；实写流 observed→独立 retained 校验→sidecar→helper→原 root/group-id 校验→**完整 metadata_validate 成功后**才发布运行计划。沿用旧 V1 completion wire，receipt 仅新增 `GROUP_PLAN_bytes/SHA256`；其他值变化只有 kind/version 标签，原 original-plan SHA 与 SOURCE/receipt 的 False 标志保留。
- 上述 hash 是成功写入并 fsync 的流字节身份，非目的文件事后 readback。helper 接受的 observed 在本测试中是明确合成数据；其成功本身不是物理复制或原生运行证据。完整八 catalog 不等于复制八棵运行树：仅两选中 E1 要求完整树，六 deferred 不构造，H1 排除。
- [原 metadata_validate:526–605](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v3/stage_good_expert_holdout_v3.py#L526-L605>) 与 V1/V2 整函数相同：导入完整 AppV6/Base/运行时/E1 闭包，非 AST 裁剪或 stub；两任务/seed/pose/历史 seed 负例保持。`101/102` 仅内存 FD 占位符，不代表 EX 准入。
- [原 parent:79–86](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/single_gpu_good_expert_holdout_parent_v1.py#L79-L86>) 的 True/True 入口前提已与派生运行计划兼容；parent 仍 `9679/fc4458431d375c2b44c063b3f5a8d4ad83ecc6e21d6684625898f7991c51f0ff`，[原 runtime](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/good_expert_holdout_runtime_v1.py>) 仍 `56370/4ea1470d0255bf172a8bc2e16ce70ceae45a91e32ad622e8df6119f4f8ba0c9f`。原 OWN/tasks/root、完整文件 hash、private-GPU/finite EX、C 只读、容量/ready/deadline、actual p.wait、身份清理/close 次序均沿用；未增加 root PREFIX 或执行入口。

## 唯一 NEW32 执行与边界

- `C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe -I -S -B`，Python **3.14.3**；显式 `unittest.SourceTests` **一次，32/32，0 failures / 0 errors，9.954684699998325s**。未调用 test.main/report writer、旧测试模块、stager main/prepare/preflight_summary/stage、parent/worker/Popen。
- 先完整读测试。其默认 HERE/tempdir 指封后源目录，故仅在内存重定位二者至本 NEW review；R/WORKSPACE、测试体及全部 PIN 保留，使用逐字相同入口临时副本，结束已清除。第一次外层 loader 在任何案例/模块代码之前试探非白名单 pyc 缓存即停止，**0 cases**；随后从已核定完整 raw 编译非 main 模块，避开缓存，唯一 32 案例运行没有重放。
- sealed suite 自身五 audit **全 0**；独立外层五 audit **全 0**；profile 禁用入口实际调用 **0**。无 SSH/SDK/Torch/PT/raw/GPU/C/锁/Git 或旧封件修改。
- 完整 metadata 成功返回 **4 次**：两 seed 的 False SOURCE 计划各 41 worker_files；两 seed 的 True/True 派生计划各 43。每次均绑定真实完整 AppV6→Base、两任务和 cross-seed 负例；`actual_resource_admission=None`，实际 GROUP_PLAN 发布 0。两新增 asset 项仅固定元数据身份，实际资产/vendor/运行树用显式 fake marker，不冒充完整静态闭包字节。
- 父所述历史 31/32 是 SOURCE 负例 fixture 误设，不是 native 失败。现 test29 修改实际 producer checkpoint SHA 而非会被覆盖的冗余 row SHA；当前 32/32 独立通过，历史版本未重跑。旧已封测试 receipt 也保持原字节。

## 留给父的 readiness 边界

**SOURCE 修补与新运行计划入口兼容已通过；native binding 仍 UNKNOWN，native/quality qualification 为 null。** 本轮未执行真实 prepare/stage，未证明完整两选中静态树/assets/vendor7、目标 readback、实际 SDK/MRO/pose/cache、原资源准入/物理/DR/predicates/close，亦未产生 per-seed controller/collector/outer actual-parent-wait 证据。既有物理与接受阈值/预算锁不变，零更新与静态通过不作训练或新物理收益结论。最终本目录仅本 MD 与机读 JSON；未新建 builder 或运行框架。
