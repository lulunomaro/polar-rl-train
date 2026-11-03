# Phase1 capture worker V3：最终 B2 依赖闭环 SOURCE 派生

`source_version=3`；typed/wire task、plan、sourceIndex kind、purpose 与安装 aliases 保持 V1。此包只交付 SOURCE 封件，不创建 materializer/dispatcher，不授予 native admit。最终结果以 [SOURCE receipt](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v3/SOURCE_RECEIPT.json>) 和 [SOURCE seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v3/SOURCE_SEAL.json>) 为准。

## 最窄差异：五份 candidate 全部不变

已完整验证 [V2 seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v2/SOURCE_SEAL.json>) 全13成员：2815 bytes / `caacf07e8bc46bd2cc5f4fa14138782430d86de4f6382bbb35adcdcde5d469d5`，content root `83cb35d61298fdac4d2c720d1322ada0fbfa43b866709b4e5958b99ac82b62d2`。下列完整 candidate 与 V2 **逐 bytes 一致**，logic/main diff=0：

| 来源 | bytes | SHA256 |
|---|---:|---|
| [contract](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v3/phase1_capture_contract.py>) | 9518 | `7910d7f3378923275b430b7960ed833f79b394feb3317c857d3a98c501729a0a` |
| [observer](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v3/phase1_capture_observer.py>) | 10438 | `8a6faa66d55d4498fd1249aaabfeb9dfd7bb9e0b01013137adce3756b3c9004c` |
| [runtime](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v3/phase1_capture_runtime.py>) | 19145 | `490dcb8fd561b8db3af78db29db59d28b6dea33e7a8026609f3d1ddb62a93017` |
| [worker](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v3/worker_passive_interface_v1.py>) | 16323 | `f2b7326efb546f0a274c978aa69c126506ed0d3c3a8a1792d80893fa9f163b0b` |
| [parent](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v3/single_gpu_passive_capture_parent_v1.py>) | 9336 | `d5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41` |

只在 [index](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v3/CAPTURE_SOURCE_INDEX.json>) 改三条 sensor dependency 来源、完整 sensor seal13、manifest及其原 pin 闭包，并增加只读诊断 references。五个 dependency 安装 aliases 不变；C8、adapter10、partition9、原17 aliases、C182原 pins、bootstrap原完整两模块均保留并实核。index 逆投影回 V2 相等，禁止扩大候选逻辑差异。

既有 [worker127–138](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v3/worker_passive_interface_v1.py#L127-L138>) / [runtime60–63](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v3/phase1_capture_runtime.py#L60-L63>) 按 fixed index 加载 B2 API、tap、manifest。同一原 env/bridge 实例，原安装签名不变；没有复制或另造 reset verifier。

## 最终 B2：完整 package 与原来源闭包

读取并逐成员核验 [B2 seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v2/SOURCE_SEAL.json>) 全13：2909 bytes / `be538a07c8ccfb785023422ace6985e1fde0bd5b885266124e430527c1ec558a`。完整13 pins保存在本包 index/dependency_seals，不只核三份运行文件。关键 runtime 来源：

- [B2 source API](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v2/source_api.py>)：31456 / `a334766d6a9ca88d02d682e73d70a15e9098f1e77d1aa7a45e6d0154a4b73b62`。
- [B2 passive capture](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v2/passive_capture.py>)：26599 / `4e05fe172068f8ed3e1f438ec73b57e89986e7da8316d16fd764026c8f53da9b`。
- [B2 manifest](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v2/SOURCE_API_MANIFEST.json>)：336133 / `2801135d1ff028f09a5eb7cd571cc3ca90694b60340d17e62374a42cbe60eaca`。

完整 B2 `build_manifest()` 以原整模块 SOURCE metadata import 重建并与冻结 manifest dict 相等；遍历 **435 source-pin引用 / 155个唯一完整 .py**，逐文件 bytes/SHA/AST 实核，不执行 plant modules。8 role 均 `SOURCE_CONFIRMED_LIVE_UNKNOWN`。B2 内严格4层原 wrapper composition、class descriptor、module/code/closure/self、adapter/MRO 校验由原 B 作者实现；本包仅传递固定依赖，未放宽或另造校验器。完整原 runtime/static banks/vendor7 要求仍继承；本SOURCE原文件闭包不是实际 staged inventory 的替代资格。

只读引用 [diagnostic audit](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_sensor_reset_identity_diagnosis_v1/SOURCE_EVIDENCE_AUDIT.json>)、[final handoff](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_sensor_reset_identity_diagnosis_v1/FINAL_SOURCE_HANDOFF_RECEIPT.json>) 及其完整4份来源 pins；诊断代码不作为 runtime 模块安装。已读 [父独立 B2 SOURCE 回执](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/PHASE1_B2_PARENT_SOURCE_VERIFY_V1.json>)：28/28与旧B1/runtime-only继承边界。冻结 B2 `parent_review:PENDING` 原字不改；此回执也不是新的资源审批 Bool。

## SOURCE 测试范围与继承边界

[test suite](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v3/test_capture_worker_source.py>) 本轮实跑 **44项**：12个新 V3 完整依赖/闭包/API/metadata/负 pin审计，复用冻结 V2 **完整测试模块**中的32项 stdlib close/bootstrap回归，仅将metadata HERE指向逐bytes相同的V3来源。V2 source_version==2的单项断言由明确V3 wire断言替代；没有裁取原模块半个函数。完整原Base/AppV6/core真实导入校验、真实own临时FS fast/nonfast close往返、重注入V1 binding epoch错误负例、bootstrap来源/缓存污染负例仍实跑。仅SDK对象/env/App binding是显式synthetic metadata fixture，不是实际SDK binding。

历史 V2 96项、B2上游28项/21 composition负例未计入本轮44，也未重复无关物理测试。B1历史TorchCPU25bitwise/50identity仅原runtime范围继承；B2 preflight及V3没有新TorchCPU、SDK或实际reset verifier执行。实际own临时FS SOURCE/metadata读写、replace、清理单列计数，未伪称所有文件操作0。

原E3 N80、64默认/128可选、zero6/PT0/teacher=None、无learner/optimizer/replay；原reset53→E3fall/publish55→既有compute66完整保留。same-tick cache可能复用，initial clean0仍UNKNOWN，已有initial memory保留trace；100Hz global slot计数不是per-row episode freshness。原动作/物理/DR/命令/phase/speed/acceptance不变，不额外reset/step/compute/getter/RNG，不失效cache或主动tick++。V2 bootstrap及两个close fixes原样继承，不改fast mode/完整AppV6→Base/原env与App各一次/实际wait与EX释放闭包，不加budget writer或人工approved门。

## 现场事实与未来门

[V2 actual closed result](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ACTUAL_CLOSED_20261103_210748/CLOSED_RESULT.json#L62832-L62837>) 已越过bootstrap，到B1 sensor preflight报 `ValueError: Function identity mismatch: RecoveryEnv._reset_idx`；真实outer callable身份没有输出，仍UNKNOWN。child fast-close RC0带WORKER_ERROR；parent/outer实际wait RC1，原双EX释放。GO/READY/FINAL/controls缺失为null，不改成技能0%或capture PASS，不重放旧root。

未来 `RESET_BINDING_V3` 唯一root、完整materializer/collector传播、真实资源准入/SDK/native capture、per-row episode/untapped actor35 bitwise/partialreset/SDK物理readback/原cost结算证据均由父后续处置。本child没有SSH/PT/raw/SDK/native/GPU/resource/canonical/EX/Git/stage/dispatch，旧封件编辑0。`Gate1=UNKNOWN`；capture_interface_passed/exact/paper_ready/stage2_GO=false。SOURCE封件不是native授权。
