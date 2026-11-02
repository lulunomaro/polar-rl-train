# 当前状态与CPU fixture V2增补：算法不变，真实teacher schema修正

本增补是本交付件的**当前CPU状态入口**。[V1设计文档](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_reference_v1/EMBEDDED_TEACHER_REFERENCE_SOURCE_V1.md>)、[V1 API](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_reference_v1/API_CONTRACT_EMBEDDED_TEACHER_REFERENCE_V1.json>)及[V1本地测试历史](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_reference_v1/CPU_TEST_EXECUTION_HISTORY_V1.json>)保留其创建时状态；其中“未来/未执行CPU”和V1 fixture命令已由本增补更新。算法/actor API没有变化。native reference、实际paired效果仍为null。

## 1. 保留失败，而非把schema缺项解释为restore失败

父端[V1实际CPU回执:5–19](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/EMBEDDED_TEACHER_REFERENCE_CPU_V1.json#L5-L19>)绑定了adapter 16333B、SHA256 `400e06ea2c04edaab8330022a53455e13629b7f35d3ac7066f51df1acfcd0407`以及旧fixture 11051B、SHA256 `aa982495175d694b8327a545d4291f4bc8f0760d8a18df0fe0234c2d44a78d83`，returncode=1。

失败精确位于旧fixture第105行：`assert std_names and norm_names`；实际全state只有`distribution.std_param`和四层MLP的八个weight/bias，共9键。原RSL默认identity normalization没有teacher持久norm/buffer是有效配置。**这是fixture对真实schema的错误假设，不是已严格装载teacher丢层。** 原adapter按实际所有state键比较，既不选择性丢norm/std，也不为通过测试新增norm层。

[旧adapter](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_reference_v1/embedded_teacher_reference_v1.py>)与[旧fixture](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_reference_v1/remote_cpu_embedded_teacher_synthetic_v1.py>)逐字节保留。新[fixture V2](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_reference_v1/remote_cpu_embedded_teacher_synthetic_v2.py>)只修schema/负向用例隔离和V2输出标识；[完整小diff](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_reference_v1/REMOTE_CPU_FIXTURE_V1_TO_V2.patch>)、[可复核构建器](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_reference_v1/build_remote_cpu_fixture_v2.py>)及[构建回执](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_reference_v1/BUILD_CPU_FIXTURE_V2.json>)一并封存。

V2 PIN：16128B，SHA256 `246f8a305d0fed032da964c92b899d731bc81cab61804d901558d1be01dd8a2c`。

## 2. V2具体修正与独立负向证据

1. [schema:102–110](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_reference_v1/remote_cpu_embedded_teacher_synthetic_v2.py#L102-L110>)保留actual all teacher keys；norm存在则完整比较，缺失明确标`identity_no_persistent_teacher_norm_state_observed`。
2. [STD负向:132–156](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_reference_v1/remote_cpu_embedded_teacher_synthetic_v2.py#L132-L156>)是第一个mutation。要求独立全值比较精确报`full embedded teacher value differs: distribution.std_param`；再要求原mean守卫首次失败不是sticky消息；最后单独确认sticky。没有用前一个buffer错误污染STD检测。
3. [teacher buffer:158–179](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_reference_v1/remote_cpu_embedded_teacher_synthetic_v2.py#L158-L179>)不存在则`not_applicable`且检测值null，并附实际state/buffer名单；有floating persistent buffer时使用独立新case。**本次实际teacher无buffer，没有声称实测teacher-buffer变异。**
4. [残差buffer:181–193](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_reference_v1/remote_cpu_embedded_teacher_synthetic_v2.py#L181-L193>)单独新case变更`residual.obs_norm.mean`，验证保留的whole-mean guard，不冒充teacher norm测试。
5. 原cache的build是one-shot，没有重开关。每个隔离negative [另造本fixture自己的synthetic full root并各build一次:112–130](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_reference_v1/remote_cpu_embedded_teacher_synthetic_v2.py#L112-L130>)；没有旧模型、母PT、optimizer/count切片或故障fallback。总fixture可有多个**新造**synthetic checkpoint；“one read/hash/decode”是每个独立cache各一次，不是整个程序只序列化一个文件。

## 3. 父端已完成的真实软件CPU验证

已读父提供的[V2 CPU回执](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/EMBEDDED_TEACHER_REFERENCE_CPU_V2.json>)；本child没有重跑Torch/fixture，也没有native操作。

| 项目 | 实际结果与来源 |
|---|---|
| PIN与returncode | [5–15行](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/EMBEDDED_TEACHER_REFERENCE_CPU_V2.json#L5-L15>)与上列PIN完全一致，RC0 |
| teacher数学对齐 | [21–29行](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/EMBEDDED_TEACHER_REFERENCE_CPU_V2.json#L21-L29>)：4×N80；maximum original RSL teacher error=0.0 |
| candidate鉴别数学量 | 同处maximum difference=0.1559954136610031；这是刻意非零残差的动作数学差，**不是技能、reward或提升效果** |
| schema与teacher-buffer | [30–62行](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/EMBEDDED_TEACHER_REFERENCE_CPU_V2.json#L30-L62>)：9 state keys、norm为空、named_buffers为空、N/A/null |
| STD与残差buffer负向 | [63–73行](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/EMBEDDED_TEACHER_REFERENCE_CPU_V2.json#L63-L73>)：独立STD全值、首次原guard及隔离residual.obs_norm.mean均detected |
| RNG/sticky | [95–96行](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/EMBEDDED_TEACHER_REFERENCE_CPU_V2.json#L95-L96>)：RNG不变、sticky后测通过 |
| actor与真实boundary记账 | [234–263行](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/EMBEDDED_TEACHER_REFERENCE_CPU_V2.json#L234-L263>)：4 actions/4 transitions，candidate/residual forward 0，history null，update/RNG 0 |
| 限制与unknown | [285–292行](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/EMBEDDED_TEACHER_REFERENCE_CPU_V2.json#L285-L292>)：仅policy semantic true，native qualification/paired UID/effect仍null，SDK/GPU/old original PT/native 0 |

回执中的E3、role_key/run、bootstrap SHA和producer guard标明**OWN SYNTHETIC**；它们不是实际训练producer、独立母PT等价证明或已执行reference。每case全A1 CPU cache与whole-state保护仍在。此前42/42 stdlib fake PASS仍有效，见[V1最终回执](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_embedded_teacher_reference_v1/CPU_TEST_RESULTS_HARDENED_V1.json>)，没有为本delta重复运行。

## 4. 稳定命令及后续边界

已完成的父端V2使用下面入口；今后若要复验必须另建输出目录，保留当前结果：

```bash
python -B remote_cpu_embedded_teacher_synthetic_v2.py \
  --new-output NEW_UNUSED_OWN_SYNTHETIC_CPU_ROOT
```

PYTHONPATH依赖仍是原已封full-cache helper、original-boundary core、reviewed bridge/vendor以及实际Torch/RSL/TensorDict。这是CPU软件fixture，不是native母本参考入口。

下一native最小入口由405在NEW版本实现；本child不在旧module重造，也不改现存wait中的parent/root/index。后续仅在父给出新source路径后独立短只读review。原资源准入、actual wait/完整FINAL/error/env/App close、原74救援分母/normal6隔离、W35原standing/moving分组、原阈值、physics/DR均保留；任何未qualified窗口只作诊断，保母、不promote。
