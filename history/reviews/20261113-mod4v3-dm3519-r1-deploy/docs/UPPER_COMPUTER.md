# ROS 2 和 RMCS 上位机

新增包 `upper/ros2_ws/src/rmcs_mod4_chassis`。它可独立运行，也可由 RMCS executor 加载。`rmcs_auto_aim_v2` 的识别、跟踪、云台和发射逻辑保持其原实现；底盘以本包的速度/腿高接口接受命令。

## 构建

把 `rmcs_mod4_chassis` 放入机器人现有 ROS 工作区 `src`，先确保与本工程记录版本兼容的 `rmcs_executor`、`rmcs_utility` 已构建。使用支持 C++23 和 `std::format` 的 GCC 13 或更新工具链；Ubuntu22.04 默认 GCC11 无法构建所记录的当前上游 executor。

```bash
source /opt/ros/humble/setup.bash
colcon build --packages-up-to rmcs_mod4_chassis --cmake-args -DCMAKE_BUILD_TYPE=Release
source install/setup.bash
```

本机的实际构建使用独立 overlay 和私有解包的编译器，脚本 `tools/build_ros.py` 保留路径和构建日志；未更改系统 apt 源或全局编译器。

独立运行：

```bash
ros2 run rmcs_mod4_chassis mod4_chassis_node --ros-args -p device:=/dev/ttyACM0
```

与自瞄运行：把 `config/mod4_and_autoaim.yaml` 中底盘的 component 条目和 `mod4_chassis` 参数节加入你们**现有** RMCS 配置。自瞄所需的相机、云台 IMU、裁判数据和设备外参仍由完整机器人配置提供。示例 YAML 只展示两个组件共存，未编造实车相机参数。

## 实际 ROS 话题

| 话题 | 类型 | 单位/用途 |
|---|---|---|
| `/mod4/cmd_vel` | geometry_msgs/msg/TwistStamped | linear.x m/s，angular.z rad/s；其余分量为0 |
| `/mod4/height` | std_msgs/msg/Float32 | 0.2–0.4 m，默认0.28 |
| `/mod4/arm` | std_msgs/msg/Bool | false→true 请求使能 |
| `/mod4/estop` | std_msgs/msg/Bool | true 急停 |
| `/mod4/status` | std_msgs/msg/UInt32 | 下位机状态位 |
| `/mod4/state` | std_msgs/msg/Float32MultiArray | q6、qd6、gyro3、gravity3、action6、模型请求转矩6 |

上述确实由本包创建 ROS publisher/subscription，区别于上游自瞄源码中的 RMCS 内部类型接口。输入速度的保鲜时间按 steady 时钟的**接收时刻**计算，100 ms 无新速度则发送撤销使能；TwistStamped 的 header 不参与当前保鲜判断。命令源应以20–50 Hz持续发送并避免上游长队列。

接通后先保持速度流，再发送 ARM false→true。下面只演示原地零速度指令，物理 DT7 允许条件和下位机标定/参数验证仍需满足：

```bash
# 终端1：持续零速度
ros2 topic pub -r 50 /mod4/cmd_vel geometry_msgs/msg/TwistStamped '{twist: {linear: {x: 0.0}, angular: {z: 0.0}}}'

# 终端2：复位使能请求，再明确使能
ros2 topic pub --once /mod4/arm std_msgs/msg/Bool '{data: false}'
ros2 topic pub --once /mod4/arm std_msgs/msg/Bool '{data: true}'
ros2 topic echo /mod4/status
```

急停：

```bash
ros2 topic pub --once /mod4/estop std_msgs/msg/Bool '{data: true}'
```

解除时先发 estop=false，再 arm=false→true；持续 arm=true 不能自动恢复。USB 重连时先发送一帧撤销使能，插件丢弃连接丢失前的使能请求。串口采用 nonblocking 收发，保留未写完的字节，禁止把新帧拼在旧帧中间。

## 验证范围

`tools/test_upper.py` 使用 Linux PTY 测真实 POSIX 串口代码，不依赖 ROS 替身头文件。`tools/test_ros_loopback.py` 使用真实 ROS 2 发布器、订阅器和程序，连接临时 PTY，并可由真实 RMCS executor 加载插件。回环的遥测是明确标记的合成数据；它验证通信、话题和生命周期，不能代替实车电机试验。

本次未接入实物相机/云台；完整自瞄组件所需的 OpenVINO、相机 SDK 和目标机配置不在底盘通信测试中冒充通过。
