# PC3IO version1 — 本机逐行ASCII协议

仅local stdin/stdout，无socket/CAN。不是C struct内存dump，不依赖32/64位padding或wire endian。payload小数是finite IEEE754 binary32：parse时round到float32，reply用9有效数字roundtrip；内部printf的double promotion不是wire double。时间戳u64、seq/count/u32、turns/i64均按十进制**整数**传输，不经过double。

完整field名/type/count/offset由[PROTOCOL_SCHEMA.json](<PROTOCOL_SCHEMA.json>)与[io_protocol.h](<io_protocol.h>)定义；不是凭本说明猜字段顺序。

## Framing

```text
request: PC3IO 1 I|S|Q WIRE_SEQUENCE PAYLOAD_COUNT PAYLOAD...\n
reply:   PC3IO 1 R WIRE_SEQUENCE STATUS 71 PAYLOAD...\n
```

LF或CRLF；每个request一个完整line，一个reply，stdout无banner/日志。stderr是诊断。INIT=51字段，STEP=51，QUIT=0；reply固定71。header与实际token count、operation的已知count都检查。

wire seq从1开始，严格每个成功request+1，无wrap。它与packet sequence/command sequence是三件事：同一个delayed packet重复到达时packet seq必须保留，wire/command seq仍可增。Q是清理操作，在fault后仍可用任意正seq关闭，不重新arming。

I每process仅成功一次，profile必须25，binding mode必须1=LOCAL_STDIO_MOCK_ONLY。此mode的binding mask511只是本机软件接口声明，不是实板/电机ID/协议资格。I成功reply STATUS0但VALID0，全payload0，不是actuation。

任何protocol/C kernel fault锁存；全部71个payload字段置0，VALID0，不泄漏上一个good torque/debug。后续S只回LATCHED。重新初始化也硬错；新process是显式reset，不静默重启。

无LF的短截断EOF：回1008并exit2；超长无LF满buffer：回1009并退出，不等待drain。普通clean EOF退出。保持pipe开放却不送完整line属于framing阻塞，Python客户端的timeout会停止它自己拥有的child，而不是无限等候。

## INIT字段组（51）

| 起点 | 字段 | 类型/count |
|---:|---|---|
|0|PROFILE=25|u32|
|1|BIND_MODE=1 local mock|u32|
|2|BIND_MASK=511|u32|
|3|DRIVE_MAX_AGE，1..50000us|u32|
|4|ARM，1 supported-upright /2 static-gravity|u32|
|5|ACC_REF，0 chassis /1 wheel-midpoint|u32|
|6..10|ACC_CORR,WHEEL_STD,ACC_STD,INNOV_LIMIT,MAX_RATE|5×f32|
|11..12|MAX_GAP,MAX_AGE microseconds|2×u32|
|13..15|TRACK,RADIUS,EPS|3×f32|
|16|OFFSET body origin→IMU meters|f32×3|
|19|PINS left then right，O/K/P/A/B/C/D/W各x/z|f32×32|

K、PID、yaw/shaping/profile均由冻结V3 P25编译源提供，不允许通过wire更换K或H2 profile。[DEFAULT_INIT_P25.json](<DEFAULT_INIT_P25.json>)是nominal数学参数/显式先验，非真实rolling radius/IMU/BSP标定。

## STEP字段组（51）

|起点|字段|类型/count|
|---:|---|---|
|0..2|NOW,CLOCK_BEFORE,CLOCK_AFTER|u64×3|
|3..4|SAMPLED,ARRIVAL|u64×2|
|5|4个channel queue-epoch标签|u64×4|
|9..10|WINDOW_BEGIN,WEIGHT_SUM|u64×2|
|11..15|packet SEQ/FLAGS/EXPECTED/VALID_COUNT/DROPPED|u32×5|
|16..19|COHERENT/MEAN_VALID/WEIGHTS_VALID/MEAN_MODE|u32×4，严格byte/enum域|
|20|gyro body rad/s|f32×3|
|23|proper accel body m/s²|f32×3|
|26|q4 Lhip,Lcrank,Rhip,Rcrank|f32×4|
|30|dq4，同顺序 rad/s|f32×4|
|34|wheel spin L/R rad/s|f32×2|
|36..37|command issued/expires|u64×2|
|38..40|command seq/flags/enable|u32×3|
|41..42|forward m/s,yaw rad/s|f32×2|
|43|drive feedback sampled|u64|
|44|drive feedback flags|u32|
|45|drive measured velocity row6 LH,LC,LW,RH,RC,RW|f32×6|

flags继承V3：VALID=1，packet overrun/clipped/driverfault等都失效。epoch是一个immutable queue packet的末端标签，不说明mean gyro/rates与窗末q瞬时同步。本adapter不生成mean、不补丢样、不重写年龄或宣称real-CAN 2kHz。驱动velocity必须保留自己的原stamp；复用packet rates也不能把它冒成现在测得。

CLOCK_BEFORE/AFTER是调用者给的**logical simulation clock**。正常可等于NOW，测试可显式模拟callback迟到/倒退。它们不测host实际耗时、ARM deadline或WCET。NOW以10000us tick前进，遵守冻结V3 controller pacing；非负共同时间原点。若外层浮点秒有负prehistory，应明确统一time-origin offset，不能夹成0伪造age。

## Reply字段组（71）

|起点|字段|含义|
|---:|---|---|
|0..7|VALID,NOW,SAMPLED,ESTIMATED,AGE,EXPIRES,ENQUEUE_DELTA,DISABLE_DELTA|typed integer时间/状态；成功STEP enqueue delta=1|
|8|MATH_TAU×6|P25 controller effort-bounded、**前point-DC guard** Nm，row LH,LC,LW,RH,RC,RW|
|14|GUARDED_TAU×6|V3 cycle最终signed-DC point-guarded Nm，同row|
|20|GUARDED_WHEEL_FIRST×6|显式数学视图 LW,RW,LH,LC,RH,RC，不是物理bus绑定|
|26|STATE14×14|V3 age view；delta=crank−hip，不是FK passive knee|
|40..44|ROLL,LATERAL_PROXY,ATTITUDE_CONF,WHEEL_INNOV,CONTACT_PROXY|raw-sample frame诊断/proxy，不是世界位置/接触真值|
|45|COV4|Joseph v/b covariance|
|49|REF14|P25 reference|
|63..66|SHAPER_V,W,A,YAW_I|原shaper内部状态；effective v/w看REF14[7/8]|
|67..68|HEADING_PHASE,HEADING_TURNS|**raw sample**phase/int64 turns一对；view heading另见STATE14[1]|
|69..70|APERTURE,MEAN_COUNT|上游mean声明元数据|

前DC数学τ与guardedτ差值不是float误差。软件fixture上两者最多差4.53119Nm；原parent inverse-PD/driver还会限制实际输出，所以NEW-scene比较必须标注消费哪一组，不能把guarded当成原Python请求逐点相同。

## Status

0=OK。1..23直接来自[冻结V3 enum](<../portable_control_v3_current/pc3_control.h>)：常用5 LATCHED、7 TIME、8 AGE、9 MEAN、10 COHERENCE、11 OVERRUN、17 UNBOUND、21 PERIOD、22 DEADLINE、23 CLOCK。

1001 FORMAT，1002 VERSION，1003 OPERATION，1004 COUNT，1005 NUMBER（finite/range/parse），1006 WIRE_SEQUENCE，1007 INIT/STATE，1008 TRUNCATED_EOF，1009 TOO_LONG，1010 PROFILE。

fault不是“用零当正常控制继续仿真”的许可。父闭环应记录fault并按自己的case/stop策略处理；本工具不回退Python控制器、不在episode内重置来隐藏失败。
