# 阶段1 V3：已进入原step之后，因episode-boundary接口报错而失败闭合

## 实际结果

本次为全新 `MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_RESET_BINDING_V3_20261103_223416_1793716456364954400`；完整原静态树3592件、实际物化3839件，3处旧alias冲突原字节保留。V3 worker、materializer、collector父回归分别44/42/43项通过，仅为SOURCE证据。

原parent1547517、controller1547510、SDK worker1547526实际获得本项目原资源准入；原group记录E3 `ready:true/started:true`。运行越过B2安装与共同GO，到了原bridge.step返回后的处理，随后报：

```text
worker_passive_interface_v1.py:159
boundary.after_original_step(state.terminated,state.truncated)
_phase1_capture_pinned_a1_core.IntegrationError:
separate original bool term/trunc N80 required
```

[实际失败/闭合摘要](<reports/PHASE1_CAPTURE_V3_CLOSED_BOUNDARY_FAILURE_FACTS_V1.json>)保留原完整error、实际outer wait与父退出范围。[原collector结果](<reports/PHASE1_E3_CAPTURE_RESET_BINDING_V3_ACTUAL_CLOSED_20261103_224036/CLOSED_RESULT.json>)为 `FAIL_CLOSED_CAPTURE_EXECUTION`；原SDK快速退出使worker RC0，但有WORKER_ERROR、没有合格FINAL，原parent与outer wait均RC1，未将RC0冒成功。

- 父实际wait了唯一worker，原private GPU EX和global finite EX均已释放；父退出wall20.373003244400024s，errors[]，无外国scope操作，canonical写0。
- `controls:null`：缺合格producer计数，不填0、不从失败行数反推完成control数。
- 原SDKwall不是PT0就零成本；C-readonly验证原协议和外部结算范围保持原样，不新建账本或声称新增成本收据。
- 这不是技能评测，更不是0%技能或训练失败率；母本/H1/Registryv12保持。

## 已发现的源码候选问题，尚未native定因

[worker:126](<source_phase1_capture_worker_v3/worker_passive_interface_v1.py#L126>)把 `env.device`直接传入原boundary；[原boundary:286–299](<source_a1_frozen_eval_integration_v2/a1_frozen_eval_runtime_v2.py#L286-L299>)不做设备规范化，并要求每个bool N80 Tensor的 `value.device == self.device`。另一方面，[原bridge:86](<source_runtime/native_supermimic_bridge.py#L86>)已经用 `torch.device(env.device)`保存了规范化 `bridge.device`，step144显式返回bool flags。

若env.device是字符串，原比较会区分字符串与torch.device。这是强源码假设；本次error没有记录实际flags的dtype、shape或设备对象类型，因此尚未把该假设写成实测原因。已读SDK env.device属性只返回sim.device，未取得实际返回类型证据。

下一步先用原完整canonical boundary做小真实TorchCPU合同试验，覆盖字符串/规范设备与shape/dtype/mask负例；候选NEW V4仅将boundary构造改为已有 `bridge.device`，不改变flags、不放松原bool/N80/device谓词、不改原boundary类或任何SDK/物理/DR/step/reset行为。所有旧封件和这次失败原件保留，新窗口另purpose，非同root重放。

## 仍缺的阶段1证据

本次没有合格原whole worker FINAL可用于100Hz MID/END、noise-used、执行队列与reset闭环检查；保留数据缺口，不借SOURCE/CPU回归或collector projection补齐。独立pure/application仍不放行exact/Stage2。好专家holdout新stagerV2已SOURCE封存、18项新回归，但尚无真实preflight/stage/native评测。整体Goal继续阶段1。

本报告和V3最终源/回归/实际预检-物化-准入-失败-双层wait待Phase34归档；Git无物理重跑，main仅读。
