# Round26：全车包络与原CAD固定横向走廊筛选——本轮未运行新物理例

## 结论与范围

在**原公开X端点 −9→−5.5m、同一源地面 rm_col_3553、固定Y、全高度障碍排除**这个受限路线族内，未取得覆盖所声明全车/姿态/横偏余量的候选走廊。因此预定520160 **未准备派生目录、未执行、未消费为物理例**。这不是“原CAD没有任何可行路线”，也不是控制器或整机能力通过/失败的新物理结论。其它地面、X段、朝向、曲线路径及有限高度通行未在本轮查询。

M1/M2/M3=3/3继续冻结、均未采用。未改M0、新v2 K、PD、命令整形、原接触门槛、原CAD/P0资产、默认UI/BSP；未新增M4、DR或T02–36。总正式资格仍0/36。

## 1. 真P0名义完整包络

现有C代理的新[源码](<NOMINAL_COLLISION_ENVELOPE_V1/compute_once.py>)仅1个原P0模型编译、1 MjData、真实setter内1次forward、0积分/静力/DARE/旧QA。原选项不改，只在内存绝对化meshdir。ROOT=chassis、名义q_eq、轮相位0；[结果](<NOMINAL_COLLISION_ENVELOPE_V1/RESULT.json>)：

| ROOT轴，m | min | max |
|---|---:|---:|
| X | −0.3100000034 | +0.2791517859 |
| Y | −0.2931349941 | +0.2931348980 |
| Z | −0.3061456911 | +0.0743630464 |

311个机器人geom全部有界，其中34个collision mask OR非零；world排除、几何unknown0。最大角点ROOT范数0.38733091645m。用已编译geom_aabb的中心/半长及实际geom姿态变换8角，保守包含几何；不是完整关节域、动态连续扫掠、实测制造尺寸或硬件通行资格。串行Python/BLAS/OMP/MKL1，psutil缺席，**没有声称测得OS硬亲和绑定**。

首次缺右括号导致整个模块parse失败，SDK/model/data/forward/积分均0；[坏源码](<NOMINAL_COLLISION_ENVELOPE_V1/compute_once_before_syntax001.py>)、[原日志](<NOMINAL_COLLISION_ENVELOPE_V1/compute_once_001.log>)与[回执](<NOMINAL_COLLISION_ENVELOPE_V1/ERROR_ATTEMPT001.json>)保留。父准许唯一括号修复/compile(text)，之后首次真正查询一次成功，不重查包络。

## 2. 一次原始源几何规划与有界结构诊断

[规划器](<plan_public_uniform_corridor_once.py>)功能性解析实际47282个碰撞凸体一遍，原transform/mask不改，候选199个凸包/393个LP，HiGHS线程1。没有SDK/model/物理/raw/hash归档读取，也没有用控制器分数搜索路线。

声明余量：每轴姿态±0.1rad，以Rmax×0.3保守膨胀0.116199275m；原横偏允许±0.2m；额外几何净距0.04m；纵向guard0.25m。完整X范围为[−9.6761992783,−4.8546489392]m，所需完整Y相对区间[−0.6493342691,+0.6493341729]m，即**1.298668442m宽**。地面仍是原约1.5°横坡，不是z=0替代板。名义固定关节加刚性姿态膨胀不构成完整关节扫掠保证。

[原结果](<PUBLIC_UNIFORM_CORRIDOR_V1/RESULT.json>)为NO_CONSERVATIVE_CORRIDOR。源floor在该X跨度的Y范围[−1.7343287145,−0.1720659674]m，literal 1mm判据的阻挡投影覆盖整宽。

[唯一结构高度检查](<PUBLIC_UNIFORM_CORRIDOR_V1/HEIGHT_INSPECT001/RESULT.json>)只取此前结果中整宽阻挡体（实际只有rm_col_43671），再功能性XML解析一次、floor凸包1/LP0/物理0。其顶点相对源参考面的高度[0.000959986264,0.00100000000120145]m；超过1mm的量仅1.20145e−12m。实际证据不是先前未验证的“高架遮挡”猜想。

## 3. 明示数值边界细化，仍无合格走廊

[细化源码](<plan_public_uniform_corridor_numeric_retry001.py>)保留几何1mm判据、全部车体余量和原T01门槛，只声明1e−8m（10nm）源数值比较容差。该容差**不是已认证原生浮点/接触总误差界**。原literal结果保留；不把源候选当原生接触/实际轨迹证明。

该新准备器首调用在3空格/实际2空格的精确锚点断言失败，发生于新prefix/功能性源解析/LP/SDK/物理之前；[原日志](<plan_public_uniform_corridor_numeric_retry001.log>)与[回执](<PUBLIC_UNIFORM_CORRIDOR_NUMERIC_PREP_ERROR001.json>)保留。[唯一AST恢复](<plan_public_uniform_corridor_numeric_prepare_recovery001.py>)只取实际语义行缩进，并同步该插入块缩进，其它逻辑不变，随后首次真正细化查询成功。

[细化结果](<PUBLIC_UNIFORM_CORRIDOR_V1/NUMERIC_BOUNDARY_RETRY001/RESULT.json>)：一遍源解析、191个凸包、380个LP，8个边界凸体逐一保留（literal超量约1.19–8.50e−12m），物理/raw/actor回流均0。数值细化后阻挡联合Y为[−0.9725199427,−0.1720659674]m；余下地面Y为[−1.7343287145,−0.9725199427]m，宽仅**0.761808772m**，小于所需1.298668442m。因此admissible_plan_choices为空，chosen_plan=null。未为过筛而继续缩小姿态/横偏/净距余量，未制造PLAN.json。

## 4. 执行与后续

[唯一新场景准备器](<prepare_uniform_corridor_case_once.py>)和[单次归档器](<archive_mod4v2_uniform_corridor_m0_v1.py>)已写，父最初三个新脚本做过一次语法检查，0 imports/model/物理；准备器**未执行**。预定520160无派生协议目录/新case/新raw。其原设想只在源走廊成立时用原M0及原gate，额外全311几何XY缓存诊断为PRE最后子步、age0.5ms/100Hz，不是连续物理扫掠或actor输入。

下一实质任务应另定**公开计划问题**（例如其它真实已发布路线/地面段的足迹范围），先冻结范围再作源几何判断；不是继续跑本路线同一规划器、放松旧筛选门、重置3/3、追加M4，或把换路线当旧路控制改善。本轮没有新的物理例：v2累计仍6个名义例、7200控制、144000真实物理步；四TRAIN DR暂停。全36资格、Fn/alpha/标定/同步及硬件资格均未新增通过。
