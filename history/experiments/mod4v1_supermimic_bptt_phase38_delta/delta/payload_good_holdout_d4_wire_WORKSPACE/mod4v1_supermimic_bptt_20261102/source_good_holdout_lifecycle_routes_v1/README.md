# Good holdout lifecycle routes V1 — SOURCE-only

## 交付边界

本包仅补齐两个独立 seed 的生命周期 SOURCE 路由：**薄 outer actual-wait controller + 每 seed 的 C878/S135 双角色元数据 collector**。本轮只使用 stdlib、文本 SHA/AST 和自有 synthetic 元数据 fixture。未运行 SSH、真实 materializer/stage、controller、collector、native parent/worker、SDK、Torch、GPU、模型/回放/实际 reports、C 预算账本、锁、信号或 Git；没有 dispatcher、plan activation 或 trainer。

- seed 精确为 `20260929`、`20260930`；每 seed 各自独立 group。
- 只请求 `CURB_PROTECTED878`、`SLOPE135`，各 `N80 / 750 controls`。
- 完整 8 角色只是原 catalog；6 个角色 deferred；原 materializer 选择 **两个 E1 runtime trees**，不是复制 8 个 runtime。H1 不纳入。
- 原 teacher mean、whole-checkpoint cache、完整参数和 buffer/normalization STD、DR、D0/D7、物理/PD/气弹簧/噪声/延迟和原接受条件均保持。
- 原 parent 独占资源 admission、SDK children、canonical readonly、1800/900/2400 秒原等待，以及 private GPU EX / global finite EX 的释放。本 controller/collector 没有替代资源路径。
- SOURCE 测试不是 actual SDK、真实 wait 或质量通过。Phase1 Gate1 仍 `UNKNOWN`，exact/interface false，stage2 GO false。

## 固定 SOURCE 来源

`good_holdout_contract.py` 是完整固定合约；`source_pins.py` 独立验证所有允许的文本字节及 Python AST，而不导入 native 源码执行体。

| 固定来源 | bytes | SHA256 |
|---|---:|---|
| 原 good20 index | 21075 | `6f2fb9a4c3ad145620e1bb1b9748ae3848ef1287129aa5970dacee22502a128e` |
| 原 good parent | 9679 | `fc4458431d375c2b44c063b3f5a8d4ad83ecc6e21d6684625898f7991c51f0ff` |
| 原 good runtime | 56370 | `4ea1470d0255bf172a8bc2e16ce70ceae45a91e32ad622e8df6119f4f8ba0c9f` |
| D664 V3 materializer | 53062 | `a7eca32d8efc510ba4529b8be7c2b64d7de936f110a4eff4d847925024f43b11` |
| D664 V3 index | 24749 | `cdc0b918df0be5d1e4e3b4d008f21491446659f30146d490edff68c1df7b61df` |
| D664 V3 mirror | 20429 | `1e0f1ac5e2c95ff097001553138c8d8bcad54134a814535cce3c31224918aebf` |
| D664 V3 seal | 2034 | `0777c2e284d339ffc9c658a92188ee8c2ebb491c82d4124330a794f68654f426` |
| 新 thin controller | 5170 | `4cb6994a9afa0b399598f9af012529c9cd06bf6a8ad2e91c7d34f1c8496399c0` |

D664 10-member root 为 `1cdd8c72dfdc9fbb3b75f4068f53e8f489d7d558c79a637f39597efae8e765cd`。新包同时完整验证原 good14 seal 和旧 stage V2 九成员 seal；各集合有重叠，**不把 20+14+10+78+9 宣称为互斥文件总数**。

### Mirror79 的明确例外

D664 mirror 的 79 个声明中，78 个允许的 SOURCE 文本被完整读字节、校验 SHA，所有 Python 文本另做 AST parse。唯一旧 actual `reports/.../GROUP_PLAN.json` 只比较已发布 SOURCE 中的声明：`14385 / 54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0`。本包在任何 stat/read 之前拦住该路径，**没有打开或 stat 旧 actual plan**。库存明确 `all79_full_bytes_read=false`，不是 79 项全文件验证通过。该旧 SHA 不是新 runtime plan 的 SHA。

## D664 实际 materialization 与 SOURCE 状态分层

未来 controller 只接收已经实际 materialized 的自有根：

1. 没有自创 `ROOT_PREFIX`。root 必须为项目 tasks 下的显式绝对非链接路径，group 等于 basename，满足原 `[A-Za-z0-9_]+`、带对应 seed、不是旧 V8 group；GPU 遵循原 UUID 字符规则。
2. 完成文件固定为 `STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json`，kind 为 `SOURCE_MATERIALIZED_GOOD_EXPERT_HOLDOUT_NOT_NATIVE_STAGE_V3`，derivation version 3，materialized true，parent_launches 0。
3. **完成 receipt 的 SOURCE staged/source_native_enabled/dispatched=false 是有效状态**，不是 copy 失败；实际 runtime plan 的 enabled/staged 必须 true。
4. 完成 receipt 的严格整数 `GROUP_PLAN_bytes` 和 `GROUP_PLAN_SHA256` 绑定实际完整新 plan 原字节；parent 原字节精确匹配 good parent pin。GPU、seed、目的和 full20 来源通过 hash-bound plan 校验；不发明 receipt 顶层 GPU/parent pin 字段。
5. D664 在真实 copy/hash/fsync、origin-retained-observed preservation 和完整 metadata closure 后，才发布只改变 enabled/staged 的 runtime plan；本 controller 不生成或修改该 plan。
6. 本 controller 在一次未来 Popen 之前检查 raw receipt/plan/parent、actual good20 全字节、自己 SOURCE pin、root 状态和旧生命周期文件不存在。

`identity(pid)` 和原9595 controller 的完整 Popen/wait/except/finally AST 保持，仅类型/文件名路由变化。异常保留原 traceback；finally 的实际 `p.wait()` 路径没有换成 PID 消失、循环轮询或 finally 达成推断。

## 整体元数据及三层关闭证据

collector 的 SOURCE API：

- `summarize(dispatch, packet)`：分列原 producer grade、两子进程实际 wait、两 EX 释放、独立 outer actual `Popen.wait()`、完整 SOURCE closure、完整一次缓存字节和原 ERROR。
- `collect(dispatch, output_root, *, connector=None, packet_reader=None, cap_seconds=6000, interval_seconds=20)`：未来只读采集，自有新本地结果根 atomic 输出。
- `conditional_two_seed_summary(results, original_runtime)`：只对两个独立、外部证据全部合格的 seed group 调用原 runtime 170–219 的 conditional summary。

原 good FINAL 使用 **rows**，不是 Phase1 `terminal`。原 `REFERENCE_GROUP_CLOSED_SOURCE_GRADE_V1.json` 的 kind、passed、original_error、reasons、checked_roles、group/purpose 保留，collector 不重写原 grade、ERROR、fast-intent SHA 或 helper binding。

完整 `good runtime → core → AppV6/Base → guard/reference` 源模块按 fixed good20 从实际自有根导入，校验实际模块 origin 和 App/Base 对象身份；没有 cropped AST 或 stub。只有完整模块中的 pure metadata predicates 对一次缓存执行。会重开 FINAL/旧 producer 目录的 `select_requested_roles`、`evaluate_waited_eval_case`、`grade_closed_reference_group` 和 producer I/O guard 不被 collector 再跑；原 parent 的公开 grade 作为独立必要证据保留。

四份 whole terminal JSON：group FINAL、TERMINAL_ROWS、两角色 case FINAL。每份在 terminal/cap 时最多一次完整 read/hash/parse，并保留全部 metrics、source_cache 和未知字段。后续观察只 stat 检查签名；变更或消失明确记 ERROR，不重读或悄然替换缓存。没有部分镜像冒充 whole SHA，也没有 trace/metrics projection。

- 原 case / plan bound `262144 bytes`；原 group metadata bound `8 MiB`。
- 完整导出 `16 MiB`；超界明确失败，不退回裁剪投影。
- 4 个自有 log tail 各最多 `16 KiB`。
- collector poll 20 秒、cap 6000 秒只是观察上限；没有延长原 native waits。
- secondary worker ERROR 文件的存在本身阻止资格，保留 bounded 名称清单。
- 缺少 controls/physics/feedback/actor_calls 或 parent returncode 时是 null，不补 0。

仅 RC0、finally、materialization、producer source-grade 或 PID 消失均不达成全部 gates。两 seed summary 仍只有 ascending/descending conditional counts 与站立无失败统计；pooled whole skill、whole90、matched improvement、noninferiority 和 UID/cache 效果声明保留 null。

## 自有 SOURCE 测试与封件

本包最终完整 suite **40 项**，不是上游 D664 32 项或原 good subset 测试的重命名。测试用本目录下自有临时文本 import-layout fixture 完整复制 good20/校验19个 Python，加载真实完整 metadata 模块；不创建实际 task、执行 parent、模型或 SDK。自有 audit 验证 native/model/raw/reports/network/process/signal/lock 访问计数为零。production read-only audit hook 仅在此 fixture 中被捕获用于负例检验，方便清理自有临时文件；production 路由本身仍安装真实 hook。

覆盖双 seed、SOURCE false/runtime true、raw SHA/bytes/原 parent、完整 good20、两种原 App close、fast hash gap、错误 seed/purpose/GPU/source cache、RC0+ERROR、缺 inner wait / 任一 EX / outer wait、null counts、whole once-cache、immutable change、边界、原完整 Try/identity AST、双 seed 原 summary 限制、独立 SOURCE 库存和 actual plan 的 pre-stat guard。

历史保留：首轮35项中34项成功，唯一错误为**新测试**误用 `whole_skill_rate` 输出键（原接口为 `pooled_whole_skill_rate`）；只修新断言键，没有修改原 summary。随后35/35通过，再加5项独立库存/guard/AST测试组成最终40。终件 stat-only immutable 检查是本包封前自审加固。

只运行本地 SOURCE 验证的命令：

```powershell
& 'C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe' -B './mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/test_good_holdout_routes_source.py'
& 'C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe' -B './mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_routes_v1/seal_source.py'
```

封后第二条只读验证；不覆盖 receipt/log/inventory/seal。封件包含12个自有成员；自己的 seal 不递归纳入自己的 root。

## 未来 caller 接口模板 — 本轮未执行

以下仅说明固定 CLI；实际 root/dispatch 必须由父流程既有 materializer 和实际执行观察给出，不在本包中伪造。

```text
# 每 seed 独立一次，原 materialization 已真实完成之后；不是启动 stager 的命令。
python -u -B good_holdout_parent_actual_wait_controller_v1.py \
  --root [EXPLICIT_ACTUAL_MATERIALIZED_ROOT] --group-id [EXACT_ROOT_BASENAME_WITH_SEED] \
  --seed 20260929 --gpu-uuid [EXACT_ORIGINAL_GPU_UUID] --stage-sha [ACTUAL_WHOLE_STAGE_RECEIPT_SHA256]

# seed 20260930 必须另一个显式 group/root，不能复用前一个。
python -B collect_good_holdout_result.py \
  --dispatch [ABSOLUTE_OWN_ACTUAL_GOOD_DISPATCH_JSON] \
  --output-root [ABSOLUTE_NEW_ABSENT_LOCAL_RESULT_ROOT]
```

SOURCE_READY_FOR_PARENT_REVIEW 不代表 actual native admission、实际 closed reference 或训练 GO；最终实际状态以父流程的真实 materialization、原资源/child wait/EX、外部 actual wait 和完整一次缓存原 metadata 为准。
