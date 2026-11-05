# MOD4v2 全部传统LQR调参：沿用原36项能力台账

2026-11-06用户直接撤回上一条双GPU/RL专家迁移请求，改为MOD4v2全部LQR并设置goal。

| 恢复字段 | 当前值 |
|---|---|
| Goal | goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d，revision29 active/armed，cap40（旧20轮保留计数） |
| 总体能力进度 | v2新资产尚未正式收口：0/36；T01进行中，T02–36共35项待处理；不是旧成果归零 |
| 当前模型 | P0 MOD4v2-HW300N60；300N/60mm/孔距140–200mm；主动hip/crank连续、实际CAD相对硬域[-1.0863195404360622,+.49192233306644084] |
| 表示差异 | P0 MJCF原生主胎为r=.0625/半宽.01圆柱，guide为r=.015/friction=.9；不是v1全胎网格/.0637/.016/.02，不能混称同碰撞版本。原资产未写，未静默换轮胎 |
| 时钟配置 | 源P0 .0025/Newton32；独立LQR运行副本明确.0005 implicitfast/Newton100，控制100Hz，IMU(.03,0,.04) |
| 当前动作 | 两个新版名义case均收妥：站立过，低速非接触门全过但主轮承载/无支持门未过；先保留首败并归档，暂停四个TRAIN DR例 |
| 新case | [名义低速结果](<T01_V2/runs/v2_t01_nominal_slow_520111_001/result.json>)，12s/1200控制/24000物理；完整执行但case_screen_pass=false；不以rc0冒充通过 |
| 当前物理job | 无。pwsh-66769c4fbd0943b2与pwsh-2b4184183f0b454f均已收exit0；两例共2400控制/48000物理，旧case不重跑 |
| 下一实质动作 | 仅基于新版首败已有trace做一次控制/承载时序归约后选择至多一个有依据的窄机制；不再微间隙探针，不搬旧v1失败轴向D反复试，不降低原95%承载/零全机无支持门 |
| 子代理 | 仅复用abf2088f-af10-479a-9108-202785031447：v2静力/14state DARE，0mj_step；另一个旧代理未启动 |
| 代码接线 | model_builder_v2.py保留完整P0机构+真实最新版47289静态CAD；DR/命令整形/协同轮腿LQR/接触评分直接迁移现有源码，替换真实机械域与.0625半径，不搬旧K |
| 旧历史 | [v1冻结台账](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>)全部保留；v1 C2非接触通过/支持失败、3/3机制和420152已测间隙不重开或重评分 |
| Git | 本阶段待实际结果截止归档；此前c0fe82d7保留，不为归档重读大raw/CAD/ZIP或重跑QA |

## 执行约束

- 仍沿原36项ID/行为，先T01后T02，当前不并开多技能参数网格。此表只是同一清单的新模型验证列，不抹旧历史。
- 仅IMU/编码器/电机反馈与公开计划入控制；root/contact仅私有评分。无root扶正、复位冒充恢复、DR抵消。
- 原逆名义PD→新机械目标投影→D4→当前随机PD→signed DC→gain→同DC保留；新300N springref .1706394410901294不被旧DR的400N guard退回。
- 完整P0机器人31body+world/nq37 nv36 nu6/6connect4mimic；公开新资产气弹簧k2000/d3仍未标定，非实测完整力曲线。
- 新gain来自v2动力学、静力和DARE；旧结构/公开控制设置可沿用，不用旧K/旧平衡力矩或旧成绩充新结果。
- 物理CPU总计<=4，本轮父1+子1，Python314-B/BLAS OMP MKL1；无GPU/SSH/PPO/专家Registry/刷写或真实电机发送。
- 每case独占ID/目录，失败prefix保留；先收job再决定窄修，不盲重跑。工程筛选不是独立可靠性/实机资格。

## 原36项：新增v2状态列

| ID | 任务 | 同一验收行为 | v2状态 | v1历史 |
|---|---|---|---|---|
| T01 | 真实 CAD 定点/低速平衡 | 定点不漂、底盘平稳，低速走后能停稳，主轮真实承载 | 进行中：v2站立过；低速承载未过，DR暂停 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T02 | 正反 2m/s 与操纵 | 起步、急刹、换向、弯道和快速命令不失稳 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T03 | 连续变高 | 低/中/高姿态及行驶中升降、下蹲与恢复 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T04 | 正反上下坡 | 上下坡、驻停、起步、急刹、防后溜 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T05 | 横坡/斜向坡 | 左右高度差下维持姿态与抓地，抑制侧滑 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T06 | 坡面过渡 | 坡脚/坡顶、凸脊/凹谷、坡转平不甩机身 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T07 | 平地 ±4π 自旋 | 持续每秒两转、启动、停止、换向、中心漂移受控 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T08 | 坡面 ±4π 自旋 | 朝向周期变化时姿态、载荷与中心保持 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T09 | 自旋切换与组合 | 平移/变高/制动进入退出自旋，按轮速力矩包络调度 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T10 | 连续小坎/起伏 | 正反起伏、搓衣板、凸包与连续小高度变化 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T11 | 单侧/不同高 | 单轮先过坎、过坑、短时失去一侧支持仍稳定 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T12 | 竖直阶沿全过程 | 接触受阻→机身越沿→低处轮腿跟进→重心转移→站稳 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T13 | 高姿态上台 | 底盘净空后，整机及轮腿完成上台并稳定 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T14 | 单侧/斜向上阶 | 左右轮腿接触时序不同仍抑制侧翻 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T15 | 连续阶与平台边缘 | 连续多阶、窄台面、跨沿后维持有效支持 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T16 | 下阶与落差 | 下台、驶出阶沿后的缓冲，抑制俯冲和硬接触 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T17 | 原地跳基线 | 真实起跳、落地、抑制反弹并恢复平衡 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T18 | 正反移动跳 | 不先刹停，压腿/起跳/飞行/落地保留速度，随后继续跑 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T19 | 坡面/斜向跳 | 不同起跳姿态和坡向下可控起跳与回落 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T20 | 飞坡与跨沟 | 原 CAD 正反/镜像飞坡、间隙跨越的轨迹和能量可行 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T21 | 对称落地 | 双轮缓冲、抑制反弹、快速复稳并接回行驶 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T22 | 非对称落地 | 单轮先落、斜坡/不同高/带水平速度落地 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T23 | 接触抖动/二次腾空 | 飞行禁用轮速平移观测，着地窗口平滑重接 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T24 | 支持模式识别 | 主轮/guide/单侧支持/全机离地正确区分和切换 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T25 | 救姿态 | 前倾/后仰/侧倾后救回，稳定后继续走 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T26 | 摊卧起立/倒地恢复 | 前趴、后躺、侧倒自然恢复 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T27 | 常规外扰 | 站立/行驶时多方向、不同高度与冲量推击后稳定 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T28 | 复合外扰 | 高姿态、过阶、跳跃、落地、自旋中受撞和二次接触 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T29 | 摩擦与打滑 | 低/异摩擦、摩擦突变、空转/抱死后重获抓地 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T30 | 缩腿通行 | 狗洞/镜像、窄通道/窄平台低姿态通过与出口变高 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T31 | 受阻与脱困 | 卡轮、顶阶/墙、近限位/奇异区的检测、退让和重试 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T32 | 模型变化 | 载荷、质心、质量惯量和弹簧变化仍维持任务 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T33 | 观测退化 | 噪声/偏置/延迟/丢帧/异步/撞击尖峰下估计与降级 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T34 | 执行退化 | 力矩轮速饱和、功率降额、通信异常时姿态优先 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T35 | 连续混合任务 | 坡→坎→移动跳→落地→转弯/自旋→停车，无逐段人工复位 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |
| T36 | 独立全 DR 验证 | 完整 D0–D7，冻结后新 seed holdout 和不确定性报告 | 待处理：v2未验证 | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |

## 本轮case与软件记录

- [新版增益](<nominal_gain_v2.json>)已由原代理一次实际生成exit0，0mj_step；delta=-.2，hip=.2503281103649727，tau6约[3.021463,-4.065098,0,3.001951,-4.049372,0]Nm。full投影静力残差1.66141e-9，DARE残差1.035e-15，闭环局部谱半径.992779681593；是线性化/静力证据，尚非闭环技能。
- [生成源码](<v2_linearization.py>)真正调用P0绝对hip/crank set_configuration；558次新P0 setter/1716次forward/0积分，不读取或复跑旧case。
- [首个冻结协议](<T01_V2/T01_PROTOCOL_V1.json>)原姿态/速度/2kHz承载gate不变；先只执行nominal_stand，其余case不自动启动。
- [台账生成软件错误](<PREP_T01_LEDGER_ATTEMPT001.json>)保留：首次把4条历史复用行算进36主表，runner和protocol已创建/0物理；只限定主表区恢复台账，不重写已生成prefix。
- 首个[名义站立结果](<T01_V2/runs/v2_t01_nominal_stand_520110_001/result.json>)已收exit0，12s/1200控制/24000物理步，15项case筛选均过。评分2–12s：pitch峰.000565434rad、roll峰.00522610rad，漂移.0101575m、站立vx RMS.000880657m/s；两主轮各100%承载、guide/hard/全机无支持均0（20000个2kHz评分点）。fresh model与DR构造各1，wall39.2952s。只完成六例中的首例，非整项T01或可靠性毕业。
- 第二个[名义低速结果](<T01_V2/runs/v2_t01_nominal_slow_520111_001/result.json>)已收exit0且完整执行12s/1200控制/24000物理，wall43.5892s。非接触门全部过：pitch峰.0170887rad、roll峰.0298455rad、速度RMSE.0406789m/s、前进1.622586m、横偏.0410681m、停车vx RMS.0193254m/s。
- **低速接触门失败保留**：2–12s的20000个2kHz点，左/右主轮>1N承载91.570%/98.035%，左未达95%；全机总正常力<=1N有92点，最长连续.0005s，仍未达原零次门。guide/hard均0。主轮正常力峰约2363.21/235.60N（仿真，非硬件冲击资格）。圆柱胎下仍出现此类低支持，不能把v1的24面胎当已证实唯一原因；也不由0.5ms无支持点宣称宏观腾空。
- 同一gain/控制器/筛选线未改，两个名义case累计2400控制/48000物理。四个新TRAIN DR例520112–520115尚未启动，因名义首败暂停；T01未收口、总进度仍0/36。只保存既有新raw，不为归档读/hash大payload；下一步一次新trace归约，不重复物理case或旧QA。
