# B4首次真实Sensor CPU：未观测基线路径的fixture dtype失败

[父实际CPU receipt](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/PHASE1_B4_ACTUAL_REAL_SENSOR_CPU_V1.json>)由NEW一次purpose产生；job `pwsh-c5c7ea1f96534c8c` RC1并已收取。完整原Sensor/Delay两math、B4/codec/fixture全部源码载入；41上传source bytes前后不变，Python/TorchCPU全局RNG不变；没有SDK/native binding/GPU/model/raw/C/资源操作。

```text
phase1_b4_real_sensor_cpu_program_v1.py:24 -> run_fixture
cpu_fixture.py:276 -> left = a.step(control, reset_rows=rows) # UNTAPPED baseline
cpu_fixture.py:173 / :140 / :92 / :81 -> original Sensor.apply
sensor_mild_math.py:36 -> noise[due] = (2*torch.rand(...)-1)*...
RuntimeError: Index put requires the source and destination dtypes match,
got Double for the destination and Float for the source.
```

## 证据范围

失败出现在首个untapped baseline的真实原Sensor调用；该次正常控制中的tapped `b.step` 尚未到达。fixture模板明确是float64，而原math内部rand使用默认float32，索引写入要求dtype相同。这里是软件fixture输入支持域问题，**不是已证明B4 tap、实际SDK或物理环节错误**。fixture_result为null，未导出完成控制数或callbacks，不补成0或640；原finally没有另报恢复错误也不等于新导出六项恢复计数。

原Source6项只是AST/metadata，作者actualCPU=null保持；本父实际失败单列且不覆盖。首次原数学/源码版本保持3733/aa853…、3031/90b339…，B4 guard9827/799569…、其他三生产源码与codec均不改。

## 最窄后续（仅NEW SOURCE，不重放V1）

565已接NEW `source_phase1_b4_real_sensor_cpu_fixture_v2`：只将实际供给Sensor的合成template改float32及对应期望dtype，记录原失败；不改生产Sensor/Delay/B4/codec、不设置全局default dtype、不cast生产noise、不改RNG流。fake-state/synthetic19、off identity和独立int64精度probe可保持原类型；其余完整断言/主64-640分母/probes/异常与reset范围不变，具体差分封后审阅。

旧fixture V1、其seal/报告/CPU程序和这次实际结果全保留。收到V2精确seal并审阅后父才建立另一个NEW CPU purpose。SOURCE或CPU结果不替代native；Gate1 UNKNOWN、Stage2 False，H1/母本/原physicsDR/接受门/预算不变。
