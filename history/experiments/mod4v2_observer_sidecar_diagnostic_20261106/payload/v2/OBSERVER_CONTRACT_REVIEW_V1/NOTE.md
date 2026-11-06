# Observer contract review — source-only, actor unchanged

1. 从[v1恢复入口](<../../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md#L5-L11>)转到[v2当前台账](<../TERRAIN_ADAPTATION_TASKS_V2.md#L12-L14>)：T01 DR未收口，3/3机制冻结；暂停seed不动。现catalog仅Office/ACL，无本工程匹配项，使用文件工具。
2. **确定的源码事实：Estimate是混合时刻view，不是所有字段同步于estimated_time_s。** [update:126–128](<../../mod4v1_lqr_mpc_robust_20261102/sensor_core_jump_v1.py#L126-L128>)先构造sample时刻的roll/pitch/速度；[_predict_view:129–133](<../../mod4v1_lqr_mpc_robust_20261102/sensor_core_jump_v1.py#L129-L133>)只做`x[:7]+=age*x[7:14]`并把view时间写成arrival。
3. 因而x[0:7]为arrival的一阶预测；x[7:14]、roll、body gyro、proper_acc、wheel-forward等仍为源样本保持值。age代表源样本至view的延迟，不把held量变成当前测量。包内通道自身的均值/异步误差也未被此操作消除。
4. 重复sample stamp走cached `self.last`再预测，不产生新KF/角加速度更新，也不是把上次arrival view再次积分；原update代码支持这一点。不要由重复view推导独立新样本。
5. **C1确实消费了混合量。** [roll控制:83–100](<../controller_roll_v2.py#L83-L100>)用held `e.roll`、predicted `x[2]`及predicted关节位置，拼`nB=[-sin(pitch),sin(roll)cos(pitch),cos(roll)cos(pitch)]`并算两轮中心高度差。nB仍单位长，但没有由此获得同一时刻真实重力方向的保证。
6. 这是明确的时标非对称/接口表达缺口；若把nB称为“已同步当前姿态”便超出契约。现有Estimate没有逐字段epoch，也没有已声明且被证伪的“所有字段严格同步”规格，因此不把它直接定性为新回归bug或DR失败唯一原因。
7. [heading:21–28](<../controller_heading_v2.py#L21-L28>)的外环用predicted yaw x[1]，super仍继承C1；[诊断:31–55](<../controller_heading_v2.py#L31-L55>)同时分解predicted pitch/positions与held yaw/pitch/关节rates。分解只是当前请求的代数诊断，不提供新时间同步/轮扭矩实测资格。
8. **一阶近似与确定事实分开：** 源sample→arrival的恒速外推、body-rate保持、Euler一阶预测都不是高阶姿态传播/数字误差界。ZYX的roll_dot=`omega_x+tan(pitch)*(omega_y*sin(roll)+omega_z*cos(roll))`，一般不等于omega_x；小角度下才近似。未给角加速度/偏置界，不出具补偿误差上界。
9. **10ms不是已证0.028rad偏差解释。** [已消费小结果9–12s](<../T01_NOMINAL_BAND_TRAIN_V1/DR_OBSERVATION_REDUCTION001/RESULT.json#L593-L643>)中pitch−command真值mean−.027385/RMS.027961rad，而held-roll−sensor同epoch真值mean−.026421/RMS.026556rad；roll这一残差已按源时刻对齐，不应全归给“roll未推到arrival”。
10. 仅尺度上，.028rad/.01s=2.8rad/s；这不是本case观测速率、确定延时误差界或因果证明。混合时刻可能额外影响C1，但这些输入没有量化它对Fn低支持点/停车误差的贡献，也未拆开动态加速度、融合/创新门、偏置、模型变化和包内采样孔径的整链贡献。
11. 父的同packet独立审计副路可记录source/arrival/view时刻、原held roll/pitch/rates与arrival姿态候选的差，清楚区分Euler近似和SO(3)传播；原估计器状态/输出、actor、K/M0及3/3不动。副路值、真值残差或均值修正绝不回控制，不把副路当接触/力许可。
12. 本次仅必要6个现有文本（两台账、三源码、一份已消费小结果）；写NOTE/RESULT，未执行Python/SDK/model/FK/forward/physics/统计或DR抽样/旧QA/raw/Git/Goal/新代理；不实现副路、不跑父case，完成停止。
