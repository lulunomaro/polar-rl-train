# T01：当前 C1/C2 参考生成的 C99 组件

这次是现用算法的实现迁移，不是第四个物理控制候选，也不是新地形参数组。**T01 原接触筛选仍失败**；机器人、K、估计器、PD/D4/DC、接触模型和已消费试验均保持原样。

## 直接复用

- [C1 原算法](<../RM_ROBUSTNESS_V1/controller_roll_follow_v1.py>)：传感状态计算左右轮中心投影差、8/100s 滤波、0.18m/s 高差限速、最多4次 Newton/每次最多5次缩步、相反关节参考、0.8rad/s 参考限速。
- [C2 原算法](<../RM_ROBUSTNESS_V1/controller_heading_follow_v2.py>)：捕获操作意图航向，3/s 外环，±1.5rad/s；调用方已有 FPS 航向环时关闭此环，避免双环。
- [已有 CTK](<../SPR_AUDIT/portable_core_v2_kinematics/ct_kinematics.h>)：原机构正解和 Jacobian；未重新编写连杆几何或改旧 CTK/C3 源码。
- [生产接口](<pc2_reference.h>)、[实现](<pc2_reference.c>)只有参考生成；无 MuJoCo、堆分配、BSP 或 CAN 调用。

## 接口与接线边界

1. 用明确机构参数初始化 `ctk_geometry`，共同名义参考 `q0=[hip,crank]` 是**绝对主动轴角**。host 仅用现有 nominal 几何 fixture，不等于实机标定。
2. `pc2_reference_init(..., heading_enabled)`：独立 C2 命令为1；FPS 已经闭环航向时为0。
3. 100Hz 填入传感器估计的 `state14`、roll、omega、年龄、有效位和原始 yaw-rate 命令；不接 root/contact 真值。`state14[4/6]` 为 crank-minus-hip，非被动膝角。
4. `PC2_OK && result.valid` 后取 `reference_state4=[Lhip,Lcrank-Lhip,Rhip,Rcrank-Rhip]` 与 `corrected_yaw_rate`，供正确的 coord_soft 力矩后端使用。相反参考保持共同绝对 hip/crank 不变。
5. **这里没有完整 coord_soft 力矩后端、K/估计器、输出保护、时钟、arming 或驱动。旧 `pc3_p25_step` 不是当前 coord_soft 的即插即用后端**；后者还需共同 sagittal K＋左右差分 PD，勿把参考块直接接电机。当前未接入试玩或固件。

几何投影使用双侧接地先验，不是接触检测或真实地形高度。输入/输出/状态/几何不得重叠；非 OK 不提交状态，输出失效，NULL/alias 前置错误不触碰对象。实际时间戳/重复包/调度截止、故障闭锁与电机停机仍归调用方。年龄负值/非有限值等错误采用更严格的显式验证；不宣称与 Python 所有错误路径逐位相同。航向累加用 double，其余数学使用 binary32；ARM ABI、栈峰、WCET、硬件和全域稳定性未验。

## 唯一新组件验证

- [预声明协议](<validation002/protocol.json>)与[结果](<validation002/result.json>)；4段新合成输入，共 **1080 次**；直接对照原 Python C1/C2 的参考和航向输出，非机器人轨迹回放。
- GCC `-std=c99 -O2 -Wall -Wextra -Werror -fno-fast-math` 编译 exit0，native exit0；**16项**非有限值/年龄/周期/有效位/域/几何/alias/未初始化等故障合同通过。inverse 接受状态无不一致。
- 最大参考误差 **5.99370e-7rad**；delta误差4.43404e-7rad；原始投影差1.20720e-7m；滤波差4.14056e-8m；航向误差1.23354e-7rad；修正 yaw-rate 误差2.99653e-8rad/s。共同角均值误差1.51195e-8rad；实测每次 delta 变化峰0.00390238rad，在原0.008rad上限内；没有用该序列证明所有限速边界覆盖。
- host `sizeof(state/input/output)=64/88/52B`。native 0.24169s 含进程启动、ASCII读写和故障检查，**不是 ARM WCET、单次控制 deadline 或整机加速倍数**。
- **0物理步、0旧case/holdout读取**，没有T01新成败、独立DR验证或实际电机结果；未操作V3观看进程。

首次 [validation001](<validation001/result.json>) 因测试脚本误读不存在的 `pack['K']` 在编译前停止；原[脚本](<revisions/verify_component_before_pack_key001.py>)及失败结果保留。仅修正为实际 `K_6x14` 后，用[独立002入口](<verify_component_retry002.py>)、相同输入配方和预声明容差验证。001/002目录均 `exist_ok=False`，避免覆盖或误复跑。
