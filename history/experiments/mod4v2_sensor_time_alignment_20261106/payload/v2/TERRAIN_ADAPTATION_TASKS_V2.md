# MOD4v2 全部传统LQR调参：沿用原36项能力台账

2026-11-06用户直接撤回上一条双GPU/RL专家迁移请求，改为MOD4v2全部LQR并设置goal。

| 恢复字段 | 当前值 |
|---|---|
| Goal | goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d，revision29 active/armed，cap40（旧20轮保留计数） |
| 总体能力进度 | v2新资产尚未正式收口：0/36；T01进行中，T02–36共35项待处理；不是旧成果归零 |
| 当前模型 | P0 MOD4v2-HW300N60；300N/60mm/孔距140–200mm；主动hip/crank连续、实际CAD相对硬域[-1.0863195404360622,+.49192233306644084] |
| 表示差异 | P0 MJCF原生主胎为r=.0625/半宽.01圆柱，guide为r=.015/friction=.9；不是v1全胎网格/.0637/.016/.02，不能混称同碰撞版本。原资产未写，未静默换轮胎 |
| 时钟配置 | 源P0 .0025/Newton32；独立LQR运行副本明确.0005 implicitfast/Newton100，控制100Hz，IMU(.03,0,.04) |
| 当前动作 | **最近物理M1接触门仍失败，保留且不采用**；本轮新[有界历史对齐接口](<signal_alignment_v1.py>)已实现并以224条新合成断言通过，0真实物理/旧raw/力模型调用。实际值插值而非只改epoch；alpha/标定未知仍None，force_input_ready始终false。E4已交[默认OFF生产时间旁路](<SENSOR_TIME_METADATA_V1/publisher.py>)及14新stub/83断言/30fake source调用结果并停止，父已读源码/结果。两组件分别测试，尚无实际Plant端到端/Schema归一化，未接旧runtime/控制器；筛选门/碰撞/四TRAIN DR暂停均未变，无M2 |
| 新case | [M1完整结果](<T01_ROLL_FORCE_V1/runs/v2_t01_roll_force_nominal_slow_520121_001/result.json>)：12s/1200控制/24000物理/46.004s墙钟；非接触检查仍全过，左/右支持91.64%/98.16%，全机法向和≤1N共84点，guide/hard=0；原两项接触门仍false |
| 当前物理job | 无；**pwsh-2f7ccdc478744c93已收exit0**，仅表示完整执行。v2三名义例合计3600控制/72000物理；任何旧例均未重跑 |
| 下一实质动作 | 两个新接口及既定stub结果均收妥，不再循环其QA/3姿态。下一轮先核公开flat_run反向低速段边界，做最小可选旁路/Schema归一化，再仅1个全模型新名义逆向慢速只读观测case，记录真实2kHz两级DC及source时刻；不重演520111/520121、不调新K/PD/physics、不增加控制机制，不把旁路值回流。原正向gate/失败保留，诊断新profile不冒充整项T01/可靠性。source/alpha/力矩标定不全仍unknown，proxy/FSM不自动接入，3ms/.55/.8不改；当前尚无该物理job、M2或DR |
| P0力模型已封存 | [模型](<CONTACT_PROXY_V2/nominal_model.py>)、[输入门](<CONTACT_PROXY_V2/contact_proxy.py>)及[RESULT](<CONTACT_PROXY_V2/RESULT.json>)：1个公开名义模型compile、恰3次forward、0积分尝试、时间均0；纯FK45/source kin54/static sensor3次，不重算K/trim。body/COM/inertia最大9.72e−17m/1.71e−16m/5.56e−17kgm²，Jacobian最大2.61e−11，gravity投影5.26e−11Nm。已有trim自然解得Fn_Z=[70.057416,70.168100]N、轴向[69.348215,69.457779]N、Tp_y=[2.396131,2.399917]Nm；不是独立力传感通道或接触身份，静态fixture第三样本conf约.49，cap硬限.55，未知None；[契约](<CONTACT_PROXY_V2/README.md>) |
| 本轮对齐代码 | [stdlib接口](<signal_alignment_v1.py>)＋[check001](<SENSOR_ALIGNMENT_V1/check001/result.json>)：224条新合成断言，仿射最大差2.77556e−17、D3 10ms到达延迟保留为age15.25ms；恒加速位置用解析曲率界对照，20点曲率gyro仍有8.3125e−7窗口偏差。保留两端原时刻/窗口/权重，无外推；缺界None、同epoch改内容/回退锁存、held不生成新导数样本。解析界另带1e−11算术比较容差，不是已认证硬件/浮点总界；force/alpha/同步资格均未制造。[契约](<SENSOR_ALIGNMENT_V1/README.md>)；不重跑check001 |
| 时间输入门已核对 | [新边界check001](<PROXY_INPUT_TIME_V1/check001/result.json>)：6个新元数据例/18断言，真实model/forward/FK/物理/旧raw均0。调用封存step的原时间门、force model为惰性stub不求力；源名义5.25ms skew和整体10ms D3平移都被原3ms门挡住，未知时刻仍None。假设填同一epoch仅进入warmup，不构成真实对齐证明；未创建生产resampler/packet adapter，未改默认门或confidence |
| 新可选执行链记录 | [纯记录mixin](<actuation_telemetry_v1.py>)＋[默认OFF adapter](<bridge_motor_telemetry_v2.py>)，当前runtime未接入。只旁观原两次DC clip和功率阶段后保持值，私有诊断不得回流控制/proxy/FSM。新[check001结果](<ACTUATION_TELEMETRY_V1/check001/result.json>)：6预设干运行profile/761断言、三路保持力矩差0Nm、380个stub时钟调用、真实model/物理/旧case读取均0；不等于全车接入/执行器标定/WCET。M1旧2kHz实际饱和占比依旧未知；[用法及限制](<ACTUATION_TELEMETRY_V1/README.md>)，不重跑check001 |
| v2失败驱动机制计数 | **M1/最多3已消费且未采用：IMU横滚PD→有界左右力偶→本机Jacobian关节映射**。SPR:919/972–973只复用结构；自有名义点质量近似h=.2385432、Kp=66.8997/Kd=7.30249，非实测COM/惯量。横滚峰值.0298455→.0220729rad/RMS.00941665→.00734366有改善，支持91.570%→91.640%、92→84点仍未过。一次名义对照不是可靠性/唯一根因证明 |
| M1遥测/软件prefix | [一次新遥测归约](<T01_ROLL_FORCE_V1/M1_REDUCTION001.json>)：1200行含packet/gyro、0旧raw；请求力偶峰值6.28299N，额外关节峰值1.11153Nm，余量缩放0次，不是实测支持力。2kHz实际饱和占比仍未记录。首次生成器3空格vs实际2空格锚点失败、0model/物理；[原prefix](<T01_ROLL_FORCE_V1/PREP_ATTEMPT001.json>)与[原脚本](<prepare_roll_force_v1.py>)保留，[单次恢复](<prepare_roll_force_retry001.py>)仅修正确切根因后跑上述唯一case；不重跑生成器/归约 |
| 一次归约证据 | [reduction001](<T01_SUPPORT_TIMING_V1/reduction001/RESULT.json>)：1200控制+20000接触各读一遍、0新model/物理、0旧case。新轨迹请求力矩重现最大差0；左低支持1686点，仅68点前后正力接触环境集合有变、非几何间隙结论；子步分布分散。旧差分PD等效轴向K约2294–2538N/m，不支持臆测超高刚度；7–8s集中79/92无支持点。motor2kHz饱和占比原本未记录，仍标未知 |
| 子代理 | C已完成v2静力/DARE且停止。E4的CONTACT_PROXY_V2/3姿态封存结果不重开，旧child job已由其收妥。Round22新[SENSOR_TIME_METADATA_V1](<SENSOR_TIME_METADATA_V1/CONTRACT.md>)源码/14测试/83断言结果已收、父读review并核桥字段，E4已正常完成停止；新代理0。两代理现均闲置，不因旧通知重启；均未改P0/v1/父控制或跑本轮模型/forward/积分/旧QA/raw/Git/硬件 |
| 代码接线 | model_builder_v2.py保留完整P0机构+真实最新版47289静态CAD；DR/命令整形/协同轮腿LQR/接触评分直接迁移现有源码，替换真实机械域与.0625半径，不搬旧K |
| 旧历史 | [v1冻结台账](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>)全部保留；v1 C2非接触通过/支持失败、3/3机制和420152已测间隙不重开或重评分 |
| Git | 新名义力模型/私有执行观察器/原时间门阶段已同步[commit 489236bc](<https://github.com/lulunomaro/polar-rl-train/commit/489236bc0bc0aa6c8e53a1e2c0cd48b636ec1bed>)；tag `trial-20261106-mod4v2-force-model-observer-static` / object `7d35e9a0b0a8a08fa4b8bf3adc5f0a8a92e800ba`；40 selected+record共41项，原helper一次、atomic nonforce、ownbranch/tag/peeled远端一致，job pwsh-b53dd3930b534f94已收exit0，不重收完成通知。原f4a6bcca/a362ef38/c0fe82d7及历史pending保留；main新值79ea28c7只读观察，未回滚/推送。此stage仅小源码/公开constants/结果/prefix/log；原P0 XML仅真实path/size/既有SHA索引，未作归档payload hash；无旧raw/物理重跑。此postreceipt行随下一实际阶段归档，不新建回执循环 |

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
