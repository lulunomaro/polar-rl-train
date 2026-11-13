# 下位机和上位机协议

## 电机

标准 CAN，1 Mbit/s，六个电机均使用 MIT 模式。每个驱动使用独立的 `PMAX/VMAX/TMAX`，这些量是协议的编码范围，不等于额定转矩。

| 电机 | PMAX | VMAX | TMAX | 备注 |
|---|---:|---:|---:|---|
| 四个 DM8009 | 12.5 | 45 | 54 | 配置方案，必须与实车回读一致 |
| 两个 DM3519/DM3520 | 12.5 | 50 | 10 | VMAX=50 是本工程建议设置，不宣称为出厂值 |

控制器只发送读参数请求，在未使能时轮询寄存器 21/22/23 和 10；只有回读匹配且控制模式为 MIT=1 才接受 ARM。驱动参数需要通过厂商工具设置并保存，本固件不自动写参数或零位。

MIT 报文的 Kp、Kd 都为 0，发送软件计算的转矩；位置/速度占位值为 0。关节 PD 为 kp60/kd2，轮速度 PD 的 kd 为 0.6，保留冻结交付策略的目标映射和原标称转矩包络。最终报文另有各电机输出轴峰值限制，3519 为 7.8 N·m，DM8009 关节限制为模型的 40 N·m。

3519 手册 V1.2 第 8 页明确：位置为转子侧 rad，速度为输出轴 rad/s，转矩为输出轴 N·m。手册第 20 页额定数据与参考源码保存在 `reference/damiao`；本工程使用独立驱动协议，不使用“一拖四”的组报文。

## USB CDC 流

所有多字节整数和 IEEE754 float32 使用小端。头部 12 字节：

```text
offset 0:  4 bytes  ASCII M4RL
offset 4:  uint8    version = 1
offset 5:  uint8    type
offset 6:  uint16   payload length, maximum 160
offset 8:  uint32   sequence
offset 12: payload
tail:      uint16   CRC16-CCITT-FALSE, little-endian
```

CRC 初值 `0xffff`，多项式 `0x1021`，无反射，覆盖头和 payload。接收器处理分包、粘包、错误 CRC 和重新同步。

type=1：20 字节控制命令：`float vx, vy, wz, height; uint32 flags`。vx m/s，wz rad/s，height m；vy 必须为 0。范围沿用策略合同：vx±2.2、wz±14.137168、height[0.2,0.4]。flags bit0=ARM，bit1=ESTOP，其他位为 0。

type=2：128 字节遥测：

| payload 偏移 | 数据 |
|---:|---|
| 0 | uint32 board_ms |
| 4 | uint32 status |
| 8 | float q[6] |
| 32 | float qd[6] |
| 56 | float gyro[3] |
| 68 | float gravity[3] |
| 80 | float action[6] |
| 104 | float model_requested_torque[6] |

最后六项是模型请求的转矩，尚未乘方向、除外置传动比或经驱动限幅，不是实测转矩。

状态位：1未标定，2电机超时，4电机错误，8 IMU无效/超时，16上位机命令超时，32配置错误，64急停/未允许，128 IO错误，256策略错误，512驱动参数未验证，1024已发使能请求。1024 包含等待驱动使能回包的阶段；不能单凭此位推断已经输出转矩。

上位机命令和电机反馈超时均为 100 ms，IMU 为 20 ms。ARM 必须先为 0 再为 1；超时或异常后不能靠持续 ARM=1 自动恢复。IO/策略错误在本次启动内保持故障状态，需定位原因后重启。使能等待上限为 100 ms，确认后才开始策略推理。
