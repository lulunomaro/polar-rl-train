# 公开上阶模型实际保存配置逐行讲解

对象是作者README明确称上阶表现好的2026-07-23_16-23-21。此处只使用已归档env.yaml原文，不加载模型。dt=0.005秒、decimation=4，所以控制step_dt=0.02秒；以下每项最终贡献还要乘0.02。模型保存配置关闭全部状态机，跳跃assist也关闭，push/tuck新增奖励为空。

对应尺度：lin_vel_err_constraint=1；lin_vel_xy_sigma=0.5；lin_vel_xy_square_sigma=0.25；ang_vel_err_constraint=0.8；ang_vel_z_sigma=0.25；ang_vel_z_square_sigma=0.5；height_err_constraint=0.15；height_tight_sigma=0.001；height_square_sigma=10；no_fork_distance=0.05；no_fork_square_sigma=5。姿态指数分母pitch0.02/roll0.01，速度相关姿态A=2、bias=2、sigma=3。vel_upright_gate、vel_height_gate、height_upright_gate均false；保存的pitch门控也false。静止死区开启且阈值0.1。

以误差5cm为例：紧高度原始分exp(-0.05²/0.001)=0.082085；高度平方代价原始值(10×0.05)²=0.25，最终这两个贡献之和0.02×(0.082085-0.25)=-0.0033583。这个例子只解释公式，未运行策略。

### 全部38行奖励配置

原文件 `history/reviews/20261102-scut-standing-step-video-115-128/primary/pretrained/26_infantry/rough_rotation_stair/2026-07-23_16-23-21/params/env.yaml`，L1925–L1962。注释中的行号对应本地原始字节，不使用网页渲染时压缩空行的行号。

```yaml
rewards:  # 原L1925：该公开预训练模型保存的完整最终权重字典；0权重项不贡献回报。
  termination: -200.0  # 原L1926：真实终止mask×-200，再乘dt；time_out不应自动当真实失败。
  leg_joint_acc: -5.0e-07  # 原L1927：腿关节加速度平方和代价，权重-5e-7。
  leg_joint_vel: -0.005  # 原L1928：腿关节角速度平方和代价，权重-0.005。
  leg_joint_pair_pos_diff: -0.0  # 原L1929：左右配对腿关节角差平方项权重为负0，实际关闭。
  joint_torque: -1.0e-05  # 原L1930：所有驱动关节实际扭矩平方和，权重-1e-5。
  wheel_acc: -1.0e-08  # 原L1931：轮角加速度平方和，权重-1e-8。
  wheel_vel: -1.0e-05  # 原L1932：轮角速度平方和，权重-1e-5，避免无意义高速。
  wheel_power: -1.0e-05  # 原L1933：轮扭矩×轮角速度只取正机械功率后求和，权重-1e-5；不是总电能模型。
  wheel_air_spin: 0.0  # 原L1934：空转项权重0关闭。
  lin_vel_z: -0.5  # 原L1935：身体坐标竖直速度平方，权重-0.5；此配置没有起跳状态豁免。
  ang_vel_xy: -0.05  # 原L1936：身体roll/pitch角速度平方和，权重-0.05。
  action_smoothness_leg: -0.05  # 原L1937：腿动作二阶差分平方和，权重-0.05，抑制来回抖动。
  action_rate: -0.01  # 原L1938：全动作一阶差分平方和，权重-0.01。
  action_smoothness_wheel: -0.01  # 原L1939：轮动作二阶差分平方和，权重-0.01。
  flat_orientation_y: -0.0  # 原L1940：固定系数pitch重力投影平方项关闭，下面另有随速度变化项。
  flat_orientation_y_v: -2.0  # 原L1941：随命令前进速度变化的pitch重力投影平方代价，权重-2。
  flat_orientation_y_exp: 1.0  # 原L1942：pitch重力投影指数奖励，权重+1；不是相对参考姿态geodesic。
  flat_orientation_x: -0.0  # 原L1943：固定系数roll项关闭。
  flat_orientation_x_v: -2.0  # 原L1944：随前进命令变化的roll重力投影平方代价，权重-2。
  flat_orientation_x_exp: 1.0  # 原L1945：roll重力投影指数分，权重+1。
  track_lin_vel_xy: 1.0  # 原L1946：实际前向水平速度追踪命令，指数项权重+1，名称xy但此实现用x误差。
  track_lin_vel_xy_tight: 0.0  # 原L1947：更紧前向速度指数项0关闭。
  track_lin_vel_xy_square: -0.1  # 原L1948：未截断前向速度误差乘0.25后平方，权重-0.1。
  track_ang_vel_z: 1.0  # 原L1949：身体z轴角速度追踪命令，指数项权重+1；是yaw rate，不是yaw角位置。
  track_ang_vel_z_square: -0.1  # 原L1950：未截断yaw rate误差乘0.5后平方，权重-0.1。
  stand_still_lin_vel: -1.0  # 原L1951：前进命令落入静止死区时，身体xy速度绝对值和代价，权重-1。
  stand_still: -0.0  # 原L1952：另一组静止速度/角速度平方项权重负0，关闭。
  track_height_exp: 0.0  # 原L1953：普通高度指数项关闭。
  track_height_exp_soft: 0.0  # 原L1954：宽高度指数项关闭。
  track_height_exp_tight: 1.0  # 原L1955：紧高度指数项+1；分母0.001，指数误差先截±0.15m。
  track_height_square: -1.0  # 原L1956：高度误差乘10后平方，权重-1；该平方代价未做±0.15m截断。
  track_height_exp_both_wheels_contact: 0.0  # 原L1957：双轮接触条件下的宽高度指数项0关闭，不能声称实际用双轮触地加分。
  no_fork: -1.0  # 原L1958：左右轮身体x错位>5cm的二值代价，权重-1。
  no_fork_square: -1.0  # 原L1959：左右轮身体x错位乘5后平方，权重-1；不是世界x前进距离。
  no_fork_exp: -0.0  # 原L1960：错位超阈值的平滑指数代价0关闭。
  no_fork_z_exp: -0.0  # 原L1961：左右轮z错位指数代价0关闭。
  undesired_contact: -2.0  # 原L1962：任一非期望部位历史力过阈值的二值接触代价，权重-2。
```
