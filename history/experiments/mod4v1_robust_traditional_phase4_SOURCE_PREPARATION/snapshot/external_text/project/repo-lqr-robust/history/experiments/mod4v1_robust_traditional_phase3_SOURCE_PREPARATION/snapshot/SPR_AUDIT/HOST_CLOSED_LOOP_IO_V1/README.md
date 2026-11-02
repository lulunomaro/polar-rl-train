# HOST_CLOSED_LOOP_IO_V1 — resident C P25 stdio adapter

**本机host可执行adapter已交付：Python64 subprocess → MinGW32 PE32 → 冻结V3 current C估计器/P25/抽象gate。** 长驻、一process一init/profileP25，stdout仅协议，stderr日志。无网络/CAN/BSP/ARM运行或新physics，PH3闭环物理仍pending，不扩PH2截止结论。

## 打开哪些文件

- [p25_host_adapter.exe](<p25_host_adapter.exe>)：实际PE32/i386 host程序，不是板固件或BIN。
- [p25_stdio.py](<p25_stdio.py>)：stdlib-only Python64薄封装，非ctypes32 DLL。
- [PROTOCOL.md](<PROTOCOL.md>)与[机器schema](<PROTOCOL_SCHEMA.json>)：逐行ASCII v1；request I/S各51字段，reply71字段；明确f32/u64/u32/i64，不dump C struct。
- [默认init](<DEFAULT_INIT_P25.json>)：nominal数学/geometry参数及local mock声明，非硬件校准。K/PID等来自[冻结V3](<../portable_control_v3_current/README.md>)，wire只支持P25，不支持H2。
- [SELFTEST_RESULTS.json](<SELFTEST_RESULTS.json>)：41,632检查/0失败；[原日志](<selftest_01.log>)、[往返逐点记录](<ROUNDTRIP_01.jsonl>)与[测试源](<selftest_io.py>)保留。

## Python接口

从本目录导入，先一次initialize，然后每个完整100Hz packet调用step。示意代码没有plant创建或physics：

```python
from p25_stdio import P25Local, DEFAULT, from_v4_packet

with P25Local(stderr_path="case_C_backend_stderr.log") as c:
    c.initialize(DEFAULT)  # 显式支持upright先验、local mock gate；每process一次
    # 每tick由调用者提供 sensor_packet / epoch_quality / sequence / now_us
    p = from_v4_packet(
        sensor_packet,
        sequence=packet_sequence,  # 同一D3旧epoch重发时保持，不用wire seq冒充
        window_begin_us=epoch_quality["begin_us"],
        mean_weight_sum_us=epoch_quality["weight_sum_us"],
        expected_count=epoch_quality["expected_count"],
        valid_count=epoch_quality["valid_count"],
        dropped_count=epoch_quality["dropped_count"],
        mean_mode=epoch_quality["mean_mode"],
        mean_valid=epoch_quality["mean_valid"],
        mean_weights_valid=epoch_quality["weights_valid"],
    )
    command = dict(issued_us=now_us, expires_us=now_us+10000,
                   sequence=command_sequence, flags=1, enable=1,
                   forward_m_s=requested_v, yaw_rad_s=requested_w)
    drive = dict(sampled_us=drive_sampled_us, flags=1,
                 velocity_row6=measured_dq_LH_LC_LW_RH_RC_RW)
    result = c.step(p, command, drive, now_us)
    tau_guarded = result["GUARDED_TAU"]
    tau_math = result["MATH_TAU"]
```

这是packet converter，不是collector。quality/weight/count/drop来自调用者证据。uniform simulator可按source epoch保存bootinstant count1/window0，20×.5ms窗完结后再保存新epoch元数据；D3返回旧stamp时选回旧quality/sequence。不能在重复首包上伪换count20或新seq。这里尤其不宣称real-CAN encoder 2kHz。

mean/gyro/rate aperture与窗末q的时间语义沿用V3，不偷偷当全部瞬时同步。drive速度用自己的stamp；如复用同packet qd/spin，就保留其旧sampled时间，不伪装成current measurement。SDK没有root/contact/world-position输入项。

SDK每次完整line等待有timeout，fault/EOF/坏reply会抛明确异常；不静默restart/rearm/fallback Python。C错误回包所有payload0并锁存，父闭环应保留失败并处理停止策略，不将“零回包”当正常good control继续跑。

## 必须区分两种τ

- `MATH_TAU` / `tau_math_row6`：冻结P25 controller的effort-bounded数学τ，**前point-DC guard**。
- `GUARDED_TAU` / SDK默认`tau_row6`：V3 cycle最终signed-DC point-guardedτ。
- 两者row均`Lhip,Lcrank,Lwheel,Rhip,Rcrank,Rwheel`。`GUARDED_WHEEL_FIRST`显式`[2,5,0,1,3,4]`，不是硬件bus/front-rear绑定。

软件fixture上math/guarded最多差**4.53119170666Nm**，这不是float误差。原Python inversePD/processed-target/driver链还会作原DC限制；所以parent新场景应分开MATH_TAU送原driver链与GUARDED_TAU送同链的cohort，不能偷换两者名称后称逐点等价。任何物理对照都属于新的待验证cohort，不继承旧holdout成功率。

## Clock/期限与绑定

传入NOW/CLOCK_BEFORE/CLOCK_AFTER是明确的logical simulation µs；默认before/after等于NOW。C检查逆行、期限、packet/drive age与10000us control tick，但这**不测host RPC walltime/ARM deadline/WCET**。若父另测RPC walltime，单独记录，不能冒成板上时序。

u64不经过double，已测`2^53+1024`完整往返。`from_v4_packet`由原float秒round到µs；极大绝对时钟请直接用整数packet接口并保持共同time origin。

所有callback在本程序里仅copy/清除本机pending结构；`BIND_MODE=1`和mask511不是硬件验证，没有DM3519 codec、CAN ID、真实enqueue或板级寄存器访问。

## 软件测试结果与限制

- Python64 pointer64实际启动PE32/i386（machine0x14c、optional magic0x10b），不是把32DLL直载进64Python。
- 9个独立process/init场景共3200fixture，均完整往返。C state14、前DC P25τ对V3直接C replay **float32 bit mismatch=0**；serializer没有偷改算法。
- final guardedτ对独立原signed-DC double数学max差**1.64470e−6Nm**；strict原f32绝对峰值检查全部通过。
- bad seq、二次init、init前step、invalid mean、unknown op、wrong field count、NaN、logical clock rollback、截短EOF共9类：全零fault payload；锁存后无新normal输出。截短EOF返回1008后exit2，未挂。
- 所有3200是软件fixtures：固定TRAIN raw packet和synthetic数学向量，没新建/step任何plant，也未跑H1/H2或选择参数。用相同fixture往返仅资格新transport layer，不重新宣称旧机器人episode结果。

[错误/尝试说明](<ERROR_REPORT.md>)、[BUILD_RECEIPT.json](<BUILD_RECEIPT.json>)、[INDEX](<INDEX.json>)、[VALIDATION](<VALIDATION.json>)、[MANIFEST](<MANIFEST.json>)列出源/编译命令/二进制与全部小产物SHA。[DEPENDENCY_FREEZE](<DEPENDENCY_FREEZE.json>)冻结377个旧依赖；V3没有改动。父archive只需小manifest/文档/exe/source引用和SHA，不必为了归档重读raw数值大表。
