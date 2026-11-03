# A1 LEGACY microtrain CPU V1：仅源脚本交接

本目录只新增自包含脚本和短交接件；作者端完成 stdlib AST/compile/import/`--help` 与输入源 PIN 核对，**未运行 Torch 测试**。父代理使用现有 remote CPU Torch/tensordict 执行。旧 13 件、diff、manifest、811 loader、旧 fixture、candidate/reference 冻结缓存均保持原字节；无 SDK/CUDA/native/原 selected PT/C/锁/Git 操作。

## 最短命令

下面 `SRC` 是父代理准备的已有七个小源文件所在目录，不是模型目录；`VENDOR_PARENT` 包含原完整 `supermimic_vendor_v2`（docstring-only init，五个实际 vendor 源 SHA 由脚本检查），`OUT` 必须全新。按实际布局分别指定路径即可，文件不必共目录。已有依赖不安装；tensordict 不在默认路径时重复 `--dependency-path EXISTING_DEPS`。

```bash
CUDA_VISIBLE_DEVICES='' python -B test_quality_microtrain_torch_cpu_v1.py \
  --vendor-parent "$VENDOR_PARENT" \
  --legacy-support "$SRC/test_resume_legacy_torch_cpu_v2.py" \
  --fixture "$SRC/synthetic_cpu_contract_check.py" \
  --bridge-source "$SRC/native_supermimic_bridge.py" \
  --payload-core "$SRC/ctx_reward_full_resume_candidate_v2.py" \
  --resume-contracts "$SRC/resume_runtime_contracts_v3.py" \
  --raw35-source "$SRC/command_tracking_torch_candidate_v1.py" \
  --microtrain-contracts "$SRC/quality_microtrain_contracts_v1.py" \
  --output-dir "$OUT"
```

输出 `QUALITY_MICROTRAIN_TORCH_CPU_RECEIPT_V1.json`；异常也保留 receipt 并非零退出。旧 support 只复用工具函数，`run/main`/旧 A0+A1 测试主体均不调用。只 AST 取旧 toy/bridge/policy 完整类；不导入原 native bridge 的顶层 native/teacher loader。自身生成的 synthetic PT 是唯一 checkpoint 输入。

## 实际要测的链

- 真实 vendor 小模型：hidden16、minibatch8、H16、hist10、原 raw35 bb75 + payload-core 811 + TeacherResidualPolicy `.05`。A1 LEGACY only；不引入 bound/H32/reward/command 改动。
- 已封 microtrain 合同仅接受 N512/1024/2048，因此**实际 toy 张量 N512**，只将旧 toy class 七个 batch-size 字面量 8 展开为 512；其他 toy 动力学不变。不是伪填 N512 跑 N8，不是 native batch/physics 证明。
- 原 `collect(10)`、WM/aux 20 次、3 次真实 verified policy update；生成带 run/role/key/九 counter 的完整自有 PT 与实际 synthetic FINAL JSON。此 FINAL 的成功域是 CPU software producer，非 native worker/owner/App 运行。
- 新合同对实际 FINAL 一次 byte read/hash；原 whole-own cache 对 PT 一次 read/hash/CPU decode；新 payload lineage 检查在原 full-loader 前。严格比较 4 models/4 optimizers、norm、完整 replay/仅 streamcut、九 counter、pending/iteration/sim/wall/collect_fraction、RNG；live history 清零后原 fresh padding，无第二次 init/reset。
- 用实际恢复值 3 计算 increment2→target5；调用原 `core.train`，不手改计数或补 policy 次数。核对 start3/delta2/total5、两条真实 verified VJP receipt、teacher 实际 weights + synthetic buffer、teacher 在继续训练期间的版本与 standalone CPU teacher root。
- **原 loader 直接接收 retained decoded root**。另留 diagnostic deepcopy 做比较，绝不将副本送入 loader。记录 load 后/训练后的 whole-root value digest、tensor identity/version、差异路径；区分 `raw bytes unchanged` 与 `decoded root changed`。原811的 pending dict/CPU Adam state 可能别名共享是待真实 CPU 测量的风险，不在本交接中声称已证实或修复。

## 负例与验证层

14 个预期负例：旧 JSON byte pin；重新自洽签定的 stale JSON counter 对真实 payload；FINAL run/role/key；decoded payload run/role/key；residual shape；额外 init/reset；fresh/nonzero 拼接；记录中的多次 checkpoint open；恢复计数换成 fresh0；实际 teacher buffer 损坏。原模型 strict shape load 的隔离负例允许先前模型已部分写入，**不声称事务回滚**。extra-reset 由 NEW toy lifecycle monitor 检测，非合同 boolean 的 native 拦截证明；open=2 是 receipt-consistency 负例，正例才有真实 reader/hash/decoder 调用计数。

先完成真实 3→5 与所有负例，最后 whole decoded CPU source 的值/版本必须同时不变才整体 PASS。若 3→5 成立但 decoded-root 变，receipt 保留两项事实并最终 RC1；不以 raw 不变代替 whole-root guard，不执行修复/复制入口，不自动生成 v3。父代理收到 V1 实测后另行决定 NEW erratum/v2。任何结果都不是 native 恢复、App/会计/等待、真实传感器或技能通过率证据；无50/300质量验收线。
