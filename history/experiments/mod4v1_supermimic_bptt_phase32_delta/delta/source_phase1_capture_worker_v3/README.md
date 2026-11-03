# Phase1 capture worker V3：未封件派生模板

状态：`UNSEALED_TEMPLATE_WAITING_PARENT_FINAL_B2_RECEIPT`。这是新 SOURCE lineage 的准备目录，目标 `source_version=3`；typed/wire V1、purpose、安装 aliases 保持原状。没有生成 V3 source index、pins、receipt 或 seal，也没有执行 worker/main、SDK 或任何资源入口。

## 已验证的复用依据

基线为已冻结的 [V2 SOURCE seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v2/SOURCE_SEAL.json>)：2815 bytes，SHA256 `caacf07e8bc46bd2cc5f4fa14138782430d86de4f6382bbb35adcdcde5d469d5`，13 成员 content root `83cb35d61298fdac4d2c720d1322ada0fbfa43b866709b4e5958b99ac82b62d2`。复制前已验证全部 13 成员 bytes/SHA 及 content root。

以下五份完整来源逐 bytes 继承 V2，不裁函数，不重写 verifier：

| 完整继承来源 | bytes | SHA256 |
|---|---:|---|
| [contract](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v3/phase1_capture_contract.py>) | 9518 | `7910d7f3378923275b430b7960ed833f79b394feb3317c857d3a98c501729a0a` |
| [observer](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v3/phase1_capture_observer.py>) | 10438 | `8a6faa66d55d4498fd1249aaabfeb9dfd7bb9e0b01013137adce3756b3c9004c` |
| [runtime](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v3/phase1_capture_runtime.py>) | 19145 | `490dcb8fd561b8db3af78db29db59d28b6dea33e7a8026609f3d1ddb62a93017` |
| [worker](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v3/worker_passive_interface_v1.py>) | 16323 | `f2b7326efb546f0a274c978aa69c126506ed0d3c3a8a1792d80893fa9f163b0b` |
| [parent](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v3/single_gpu_passive_capture_parent_v1.py>) | 9336 | `d5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41` |

原 helper bootstrap、非 fast 真实 helper 第二参数、binding 写出 `add_capture_epoch=False` 三项 V2 修复完整继承。原 parent 的 privateGPU_EX / finiteEX / canonical 只读准入 / readiness / actual Popen.wait / 全 child wait 后双 EX release 原块保留。原 reset53→E3 fall/publish55→既有 compute66、物理/DR/命令/phase/speed/acceptance、zero6/PT0/teacher=None 不变。

## 本次 V2 现场事实，不重写历史

只读依据：[V2 closed result](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ACTUAL_CLOSED_20261103_210748/CLOSED_RESULT.json#L62832-L62837>) 的原 `published_metadata`：

- 已越过 bootstrap 并到达 sensor install；现场 traceback 为 worker138 → passive_capture.preflight173 → source_api.verify_callable176：`ValueError: Function identity mismatch: RecoveryEnv._reset_idx`。
- 现场实际 outer callable 身份没有输出，保持 UNKNOWN；不猜父指出的四个合法原 instance wrappers 中谁为本次 outer。
- child 1543111 fast-close RC0 但有 WORKER_ERROR；parent 1543101 / outer controller 1543093 的实际 wait RC1。原 child wait 与双 EX release receipts 均存在；collector 仍为 FAIL_CLOSED_CAPTURE_EXECUTION。
- controls / GO / READY / FINAL 缺失为 null，不转为 0% 技能或 capture PASS。已消费 V2 root 不重放。
- source-chain verifier 的严格实现归原 B 作者；此目录不复制或另造 reset verifier，不放松 module/code/closure/self，不改 D7 构造。

## B2 接线位置与当前 pending

既有 [worker127–138](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v3/worker_passive_interface_v1.py#L127-L138>) 从 index pins 加载 sensor `source_api.py`、`passive_capture.py` 与 manifest，并在同一 env/bridge 安装；[runtime60–63](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v3/phase1_capture_runtime.py#L60-L63>) 只按 index 的安装 alias 与完整 bytes/SHA 装载依赖。这是优先传递新 B2 paths/seal/manifest pins 的最窄接线点，而非重写 worker。

待父转交原 B 作者的最终 B2 API、13-member seal、manifest 全 pins 后，再逐文件核验、核 API 兼容性并完善 V3 index/source_derivation/tests/seal。B2 路径、SHA、root、exports 当前均 pending；没有用猜测值、旧 B pin 冒充 B2，也没有读取浮动 B2 API。若最终 API 与既有安装调用不相容，先形成源码差异证据交父，不静默猜补参数。

当前有意不复制 V2 preparer/sealer：其默认 sensor 指向旧 B，直接复用可误产旧依赖的 V3 封件。最终接线前不生成 packaging 输出。完整原 17 aliases、C8/182 source pins、adapter10、partition9、全 static/runtime banks/vendor7 的保留要求仍继承；typed task/plan/sourceIndex kind 与 V1 namespace 不变。未来 `RESET_BINDING_V3` 唯一 root 由父创建，本目录不做 materializer/dispatcher。

## 本地模板验证边界

[test_capture_worker_source.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v3/test_capture_worker_source.py>) 仅做 stdlib bytes/hash/AST 复用审计；不导入 worker、parent、SDK 或 B/B2，不调用 plant 或资源。V2 的历史 96 PASS 不挪作 V3 B2 集成通过。模板审计也不是新的 B2 qualification。

本轮 Python3.14.3 `-B` 模板审计实际 **6/6 PASS**（0 failures/errors，0.025s）：V2 全 13 成员/content root、五份完整继承来源、bootstrap/close 修复、原 parent 完整 lifecycle blocks、无新增 plant/install 调用、无提前 packaging/B2 声明。此结果只对应模板 SOURCE，不是 B2 集成合格。

本 child 此次实际 PT/raw/SDK/native/GPU/resource/canonical/EX/SSH/Git/stage/dispatch 均 0，旧封件编辑 0。Gate1=UNKNOWN；capture_interface_passed/exact/stage2_GO=false。等待最终 B2 收件，随后再完成 SOURCE 封件，不授予 native admit。
