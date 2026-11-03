# Lifecycle SOURCE 独立复核 V1

## 结论

**SOURCE_STATIC_PASS_WITH_REVIEW_HARNESS_FAILURE_NOT_NATIVE_QUALIFIED**。

固定源码的完整性与静态接线检查通过，未确认生产 SOURCE hard bug；本轮独立运行是 **40 cases / 39 pass / 1 failure / 0 errors / 0 skips，执行一次，未重跑**。该 failure 属于本复核自身的 profile 布局断言，不属于封件测试断言或 native 失败。另保留一个未归因的白名单探测及 profile 后半程覆盖缺口，故本轮不是全绿回执。

完整的 104 项实际 bytes/SHA 清单、全部 case 名、原始 failure traceback、metadata closure receipt、审计与缺口见 [机器报告](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_parent_review_v1/SOURCE_REVIEW.json>)：**78897 B / SHA256 `2788eeab799000d21b3dc1db75306a88b916b3063175e01410452fdaa7a349ff`**。

## 固定封件与分层库存

[封件](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/SOURCE_SEAL.json>)：2748 B / `55b4be771d2c50065bd5b95480e296bdbb456d683ca885607cfc61f7c8b37d0c`；12-member root 为 `a41453e48df40880a66c7afb9644698df528f6f26d5da062a1ce5e10ad23d2c8`，成员与 root 均实际匹配。

| 实际成员 | Bytes | SHA256 |
|---|---:|---|
| [contract](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/good_holdout_contract.py>) | 16229 | `cf86b390bb5b627a0b1ed58c7d26e94cc245097aee45be650220894d74d733bd` |
| [controller](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/good_holdout_parent_actual_wait_controller_v1.py>) | 5170 | `4cb6994a9afa0b399598f9af012529c9cd06bf6a8ad2e91c7d34f1c8496399c0` |
| [reader](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/good_holdout_remote_reader.py>) | 30182 | `714e6def3ec9e128a5f31dae1de529d25ed86a59c33112b968b9d7ff15c6a7f6` |
| [collector](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/collect_good_holdout_result.py>) | 15045 | `988f4fcce7f58fe33c105e86e2f1028c9b37ded7696bba00250d02b0359d3eab` |
| [source pins](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/source_pins.py>) | 9576 | `91d8adcaf84b5d6ae4bdf9f5da049fbab70932ff0f7da6ce2572ffe460bd4979` |
| [完整 sealed test](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/test_good_holdout_routes_source.py>) | 41531 | `9b9d780c4281ba3a6462972525509d704d8d2bea6cdb1a3f766387d92560a2c0` |
| [seal builder（未执行）](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/seal_source.py>) | 6276 | `f752a52d3ae001c6a5028d4f6d33481002387c8079c2952065dfd3bae4c9a8ba` |
| [README](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/README.md>) | 10327 | `4ea7496386fb6b73382d9970200a35ba37590f4c9a78099d3680dd9b5cd6cf57` |
| [SOURCE inventory](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/SOURCE_PINS.json>) | 62926 | `b3234e94af04699b30a16f8517b0a54d801b217d5c0a143af323d6c6ff090f0e` |
| [既有 test log](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/SOURCE_TEST_LOG.txt>) | 6206 | `c265cd1ecd488f1f8f4059cf21d390dd801afb43f27128a134901a3fac7ce92f` |
| [既有 test receipt](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/SOURCE_TEST_REPORT.json>) | 769 | `dcd6cb4318eaa9b459cf14b362e3a61de68a1615ca39a683980dddcda8cf6478` |
| [SOURCE receipt](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/SOURCE_RECEIPT.json>) | 5263 | `11733a8457828b935c2625c64ce662febb87b210b41e31a4ea633456b3b248ed` |

- 当前全文核验 **104 unique small SOURCE inputs / 68 Python AST / 28 JSON**；这些分层有重叠，不作加法宣称。
- good20 全部实际 bytes/PIN，19 Python AST；完整 AppV6/Base/runtime/E1/reference/guard metadata closure，不是 AST crop 或 stub。
- mirror79 为 **78 当前 SOURCE 全文 + 1 固定旧 GROUP_PLAN 元数据声明**。旧 actual-plan 本轮 stat/read 均为零，绝未计为第79项当前全文。以前 V3 的90项全文是历史证据，不替代本轮限制。
- good14 / V3-final10 / V2-nine 各完整 seal 与成员核验通过。
- 104项前、后、报告库存再核 digest 相同：`b513c45e1380ffb4200d8a4d208870a2f3b1cfaf4a98b15d4f9ba09d8db4f5a0`。算法为排序的 workspace-relative、TAB、bytes、TAB、SHA、LF 记录之 SHA256。全部旧源码与 sealed test 未变。

## 静态 readiness

1. [contract:92–197](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/good_holdout_contract.py#L92-L197>)：要求已 materialize 的既存 own root；无 PREFIX 新约定；显式 seed29/30、GPU 与 group 绑定。SOURCE receipt 的 `staged=False` 与 runtime plan 的 `enabled=True/staged=True` 分开；完整 raw plan bytes/SHA 绑定 seed/GPU/parent/full20，不发明 receipt 顶层 GPU 字段。
2. [controller:35–72](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/good_holdout_parent_actual_wait_controller_v1.py#L35-L72>)：单次接线到原 parent，只有一个 Popen AST site；identity 与完整 Try/wait/except/finally 在路由字面量归一后与旧9595 controller相同。未另建资源准入、SDK close、信号或 EX owner。
3. [reader:54–91](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/good_holdout_remote_reader.py#L54-L91>)：四个 BIG terminal JSON 均整文件至多一次 open/hash/decode；之后只 stat signature，变更/消失 sticky ERROR，绝非 rehash repair。case/plan 262144 B、group 8388608 B、export 16777216 B，四个 log tail 各16384 B。未知字段保留。
4. [reader:193–359](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/good_holdout_remote_reader.py#L193-L359>) 与 [collector:23–145](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/collect_good_holdout_result.py#L23-L145>)：保留原始 GRADE、error、App-close、inner waits、两个 EX release 与外层 actual wait 的独立门；good `FINAL.rows` 不是 Phase1 terminal 投影。仅使用缓存与原 pure predicates，不重跑 producer I/O graders。缺失计数/RC 为 null；whole90/relative/causal quality 保持 null。
5. [SOURCE guard:28–50](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/source_pins.py#L28-L50>) 先排除 reports/model/raw，再 stat/read；test37用阻断 Path.stat 的负例覆盖该顺序。

原 parent `9679/fc4458431d375c2b44c063b3f5a8d4ad83ecc6e21d6684625898f7991c51f0ff`、原 runtime `56370/4ea1470d0255bf172a8bc2e16ce70ceae45a91e32ad622e8df6119f4f8ba0c9f` 保留。仍仅 CURB_PROTECTED878/SLOPE135，N80、每环境750控制步，原6000 physics/1500 feedback是协议而非本轮实跑数；full8 catalog、六项 deferred、H1排除、fullDR、原物理/接受阈值/预算锁及 private GPU_EX/finite EX/C-readonly 均不变。原 wait1800/ready900/deadline2400 不变。teacher mean 与零更新不称训练收益。

## 唯一 NEW40：真实结果与故障归属

Python314 `-I -S -B`，完整 PIN raw compile/exec 为非 main 模块；只在内存中将 test.HERE/tempdir 指向自有 NEW 输出。为 test27/28 创建的 byte-identical controller副本与所有临时 fixture均已清理；未执行 sealed main/reportwriter、旧 suites 或生产入口。

**40 / 39 pass / 1 failure / 0 errors / 0 skips，1.7877695999995922s，一次。**

[test25:302](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/test_good_holdout_routes_source.py#L300-L306>) 调用完整 watch，在 [watch:362](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/good_holdout_remote_reader.py#L362-L373>) 的 call-profile、函数体之前，被**自身 inline driver profile:74**错误断言阻断：

- driver expected `lambda:0.__code__.co_consts == (None, 0)`；
- 同一固定 whole sealed test 只编译、不 exec 的 nested CodeType 检查得到 **actual `(0,)`**，`co_names=()`、`co_freevars=()`；
- 本轮记录是 `AssertionError`，不是生产断言；未修改 test/生产以迁就 driver。

CPython 在 profile callback 抛错后卸载 profile。独立 stdlib-only 最小诊断验证了 `sys.getprofile() is None`；未执行项目模块、原 case 或 suite。**本次未重新安装 profile**，所以 entry-profile 仅覆盖 test01–24 和 test25 的上述边界；test26–40及 teardown 的动态入口见证有缺口。

- profile成功记录的 watch provenance 为0，不等于 synthetic watch为0。
- test25 完整 watch体未执行；test26 PASS + 固定完整源码证明一次自有 fake-root/fake-clock 的 watch cap分支执行，但没有该次 profile见证；不宣称本轮 synthetic=2。
- 生产 watch/actual network 为0的判断依赖固定 test/source call graph 与持续独立 audit/FS guards，不冒充完整 profile 证明。

## 持续审计与未恢复证据

| 独立计数 | 实际值 |
|---|---:|
| native imports | 0 |
| model/raw/reports/budget/lock accesses | 0 |
| process/network/signal/lock | 0 |
| writes outside NEW | 0 |
| nonwhitelisted read-or-stat attempts | **1** |

封件 test 自带三项 audit 均0；它不替代独立五项结果。外层 `sys.addaudithook` 与 open/io.open/os.stat/os.lstat wrappers 与 profile 分离，持续到完整40及 teardown 返回；profile失效未移除它们。

**白名单 miss 的具体目标、path对象类型与原调用栈为 UNKNOWN。**原 driver 只累加计数，在 guard 判定后、底层原始文件操作之前阻断，但未保存 target/stack；进程已退出，现有证据未恢复该信息。已知操作类别仅为 read/open 或 stat/lstat 白名单尝试；model/raw/reports/budget/lock计数仍0。未以猜测补出路径，也未导出用户资料或扫描 R 外目录。

stdlib-only 异常格式化诊断未复现白名单 miss，故尤其**不把原 miss 归因为 traceback 或 `<string>` 探测**。原 failure traceback与原 miss不是同一证据。保留此缺口，而不是把五项写成全0。

## 交接与界限

- [既有封件40/0/0 receipt](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/SOURCE_TEST_REPORT.json>) 仅只读核对，未改写成当前回执。封前35-case KeyError历史同样单列，未重跑。
- 当前 SOURCE static PASS 与本复核 driver failure分别记录；没有确认 SOURCE hard bug，也没有 native/quality 合格结论。
- 本轮无 SSH/SDK/Torch/PT/raw/actual good report/GPU、实际 stage/dispatch/parent/controller/collector CLI、C/锁/账本/Git、旧 sealed修改。无 actual SDK close 或 parent wait证明。`native=UNKNOWN`、`quality=null`、`Phase1 Gate1=UNKNOWN`、`stage2_GO=false`。
- V1在此固定，39/1、未归因1与覆盖缺口永久保留。未来 driver只能由父另定 NEW purpose：持久化自身代码，记录阻断前的最小允许路径/操作/栈，使用同次 whole compilation 的 nested code identity 与固定 caller/root/clock绑定，不猜 co_consts 布局；不能通过修改生产或旧 test来修复本复核。后续独立工作不覆盖此V1结论。
