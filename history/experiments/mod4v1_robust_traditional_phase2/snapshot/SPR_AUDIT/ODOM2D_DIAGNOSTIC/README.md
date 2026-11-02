# R04 Spin — 只读2D里程计与侧向伪观测诊断

**结论：补上FK/gyro推导的body-y项可以让2D里程计看见大部分漂移，但不是独立侧滑观测或可靠位置闭环。当前四例中forward速度估计误差的贡献很显著，单改yaw并未解决问题。**

本轮只解析既有202/203/205/208四例，每例800条记录；原trace bytes/SHA与其result一致，使用的4个producer源码SHA逐一匹配SOURCE_MANIFEST。没有新仿真、MjData、physics step、controller replay、训练、Git或父/旧包修改。已有MuJoCo记录不是本轮新增物理/硬件资格。

## 1. 最先给父的小表

0→8s采用当前估计yaw/vx与同包proxy held到控制时刻，每个已记录10ms区间进行因果ZOH世界速度积分。所有odom从零位移开始，没有用真值回正、拟合旋转/比例或调参。

| seed | 真root xy位移 0→8s(m) | vx-only端误差(m) | 加pseudo-vy端误差(m) | 同包vy RMSE(m/s), active | 同包vy相关系数, active |
|---:|---:|---:|---:|---:|---:|
| 202 | .270804 | .144962 | .138397 | .031862 | .9643 |
| 203 | .808704 | .492991 | .308942 | .034724 | .9803 |
| 205 | .597869 | .357800 | .300150 | .042285 | .9774 |
| 208 | .501975 | .260734 | .207697 | .030381 | .9726 |

active为**1→7.99s**，不是整个8s。表中8s ZOH与下节7.99s trapezoid是不同求积/区间，已分别保存在[summary_table.csv](<summary_table.csv>)和[metrics.json](<metrics.json>)，不混作同一个验收数字。producer result原xy位移起点口径与本表0s起点略有不同，原值也保留，未修改raw。

## 2. 伪观测与时序方法

用**同一个D3包**的 `raw_gyro` 与 `encoder4`，按指定neutral pins闭链FK计算左右轮心body坐标，中点r_mid取两者均值：

```text
pseudo_vy = -(gyro × r_mid_FK)_y
          = -gyro_z*r_mid_x + gyro_x*r_mid_z
world_vxy = Rz(estimated_heading_yaw) * [estimated_vx, pseudo_vy]
```

这来自轮中点近似无横向滑动约束；不是量到了真实body-vy。FK-y对关节角恒定，故中点相对y速度为零。FK/gyro主侧向项可以很大：原点与轮轴中点有x/z偏置，自转并不意味着body-vy=0；`∫body_vx dt`只是前向gauge，不等于世界x或自转中心xy。

- `encoder4`是Lhip/Lcrank/Rhip/Rcrank，绝不把state14的crank-minus-hip delta当被动膝角；遵循父的[state14勘误](<../../reports/STATE14_SCHEMA_ERRATUM.md>)。FK内部shin-minus-hip仅用于轮运动学。
- 直接用raw encoder/gyro计算同包proxy，不拿当前真值或外推后的state14关节角混进旧包。前向估计直接取该记录estimated14[7]，不重标定或替换radius。
- 当前时刻积分用estimated14[1]的**heading yaw**；真实比较用logged yaw_true；body gyro_z与Euler heading rate分别记录。没有把gyro_z直接冒充world yaw/rate。
- body-vy主比较将packet timestamp精确配到已有ground_truth_before快照（误差阈值1e−7s，无插值/回放）。全部4例D3为首包0、随后10ms，799个唯一packet timestamp，第一包重复一次。
- 同包版本另把已知线性age预测退回：`yaw_sample = estimated14[1] − age*estimated14[8]`，去重后在**0→7.98s**积分，和相同sample时刻的真root xy对照；没有用真yaw校正估计yaw。

| seed | 严格packet-time加proxy端误差(m), 0→7.98s |
|---:|---:|
|202|.104648|
|203|.214971|
|205|.219889|
|208|.154092|

这个表和0→8s表的horizon/age处理不同，不能把两者差额全解释成某一个传感器改进。

## 3. ground_truth_before、boxcar与0.5ms阶段差

producer先取packet/estimate，之后grade_before，再推进20个physics ticks，记录grade_after；见[producer:22–29](<../../run_ground_case_v5.py#L22-L29>)。raw顶层time是after，estimated14对应estimate_time/ground_truth_before，二者相差10ms。解析器逐条验证这些恒等式与after→next-before位置连续性。

更细的时序差没有被掩盖：

1. [BufferedImuPlant:15–25](<../../physics_bridge_v3.py#L15-L25>)对前20个0.5ms步的gyro/encoder rates做boxcar，encoder position则是window末端；因此“同包”不等于所有通道同一个瞬时采样，滤波窗额外群延迟并未包含在D3的10ms字段中。
2. [grade:40–42](<../../physics_bridge.py#L40-L42>)混合qvel与缓存xmat、sensor；[health:163–167](<../../../traditional_control_20261101/control_core.py#L163-L167>)的xyz来自qpos、wheel_xyz来自缓存xpos。最后一次mj_step之后没有重新同步这些字段，本报告明确保留**0.5ms阶段混采**标记，未调用mj_forward/step制造“修正真值”。
3. 一个诊断oracle将logged true body velocity经同一logged完整RPY矩阵还原world velocity后积分，作为当前采样/阶段/求积floor，而不是传感器输入。

FK独立重表达[Sensor Core v4:34–59](<../../sensor_core_v4.py#L34-L59>)，pins来自指定[neutral manifest:120–205](<../../../traditional_control_20261101/reports/model_manifest.json#L120-L205>)，该JSON当前SHA为 `238b5ef9986b743e0642d2f97217e225179a0050ba7d2269c24d7ffad18e7f5e`。producer loader路径可证，但它的SOURCE_MANIFEST没有单列这个pin JSON；不把“4个源码SHA匹配”扩大成未记录的所有运行期几何文件都获独立producer哈希证明。

## 4. 误差消融：主要问题不只是heading

下表均在**1→7.99s**重置相对位移并用trapezoid求积；`TRUE*`只用于事后诊断，绝不是可部署输入。

| seed | estYaw+estVx+proxy端误差 | TRUEyaw+estVx+proxy | estYaw+TRUEvx+proxy | estYaw+TRUEvx+TRUEvy | 完整R/真速度floor | 单位 |
|---:|---:|---:|---:|---:|---:|---|
|202|.143163|.140347|.049242|.002415|.000721|m|
|203|.309167|.319870|.112011|.012653|.001607|m|
|205|.291530|.307746|.090014|.016509|.000347|m|
|208|.203145|.206056|.071726|.002436|.001058|m|

active forward估计RMSE依次为 **.1202/.1081/.0860/.0753m/s**；wrapped heading误差RMSE仅 **.0102/.0129/.0246/.00786rad**。换成true heading基本没有改善，而换true forward velocity显著降低端误差。这是受控“替换一个已记录通道”的误差消融，不是单因素DR因果实验；各seed的摩擦、gain、mass、delay等一起变化，不能单按mu解释漂移。

## 5. 可观测性与剩余风险

- active加proxy后估计漂移长度约 **.278/.858/.653/.476m**，可以看出203/205/208存在大位移；但与真漂移方向仍相差约 **31°/21°/26°/25°**。这不是已经获得精确自转中心位置约束。
- tail(6→7.99s) proxy-vy相关系数仍为 **.915/.970/.959/.956**，RMSE为 **.0373/.0428/.0474/.0305m/s**。主要几何侧向项确实在数据中可见，但残差包含包龄、boxcar、FK/encoder偏置、阶段差以及潜在滑动；不把它全叫“真侧滑”。
- 仅作分析分箱，重算两轮forward差<0.05m/s的active点有 **47/51/44/41个（各700点）**；这些点的vy残差RMSE仍 **.0213/.0307/.0183/.0180m/s**。样本不多，阈值也非验收标准；**两轮一致不证明共同侧滑为零**。
- 固定yaw/encoder/gyro运动学加一个“轮侧向无滑”假设，本身没有独立测量共同横向滑动或世界平移常速度。当前结果支持补几何项，不支持宣称侧滑已可辨识或漂移已闭环消除。
- 若继续估计器设计，需要显式二维/三维IMU速度及bias传播，body系满足 `dv_body/dt = a_origin_body − omega×v_body`，重力/倾角/杆臂和时间窗均对齐；无侧滑作为可降权的软约束，以innovation记录不一致。长期世界位置/侧滑仍需合适的外源或已验证初始条件/接触信息约束。本报告只提出需求，没有修改父估计器或选择最终架构。

## 6. 文件与复现

- [analyze_odom.py](<analyze_odom.py>)：只读raw验证、同包FK、窗口/时序/里程计指标；[原日志](<analysis_attempt_01.log>)。
- [refine_diagnostic.py](<refine_diagnostic.py>)：只导入本目录自己的数学函数，做消融、方向与路径导出；[原日志](<refine_attempt_01.log>)。
- [TIMING_AND_ABLATIONS.json](<TIMING_AND_ABLATIONS.json>)、[metrics.json](<metrics.json>)：全部窗口/age/误差消融。
- [world_paths.csv](<world_paths.csv>)：3200个当前before时刻的真/估计世界相对路径；[202样本](<samples_202.csv>)、[203样本](<samples_203.csv>)、[205样本](<samples_205.csv>)、[208样本](<samples_208.csv>)保留同包timestamp/gyro-FK proxy及比较通道。
- [输入/输出哈希索引](<INDEX.json>)、[验证](<VALIDATION.json>)记录原件只读不变、QP等封存物未变。没有复制完整raw或原模型大件，没有parent source import/exec。

```powershell
# 仅离线读数据/FK求积，不加载MuJoCo或生成任何新物理步。
& 'C:\Users\lulu\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe' .\analyze_odom.py
& 'C:\Users\lulu\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe' .\refine_diagnostic.py
```
