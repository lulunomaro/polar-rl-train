# MOD4v2 全部传统LQR调参：沿用原36项能力台账

2026-11-06用户直接撤回上一条双GPU/RL专家迁移请求，改为MOD4v2全部LQR并设置goal。

| 恢复字段 | 当前值 |
|---|---|
| Goal | goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d，revision29 active/armed，cap40（旧20轮保留计数） |
| 总体能力进度 | v2新资产尚未正式收口：0/36；T01进行中，T02–36共35项待处理；不是旧成果归零 |
| 当前模型 | P0 MOD4v2-HW300N60；300N/60mm/孔距140–200mm；主动hip/crank连续、实际CAD相对硬域[-1.0863195404360622,+.49192233306644084] |
| 表示差异 | P0 MJCF原生主胎为r=.0625/半宽.01圆柱，guide为r=.015/friction=.9；不是v1全胎网格/.0637/.016/.02，不能混称同碰撞版本。原资产未写，未静默换轮胎 |
| 时钟配置 | 源P0 .0025/Newton32；独立LQR运行副本明确.0005 implicitfast/Newton100，控制100Hz，IMU(.03,0,.04) |
| 当前动作 | **Round24唯一M2实际例已完成，接触门仍失败，未采用**：[M2接线/结果与限制](<T01_REFERENCE_STATIC_FF_V1/README.md>)、[独立控制器](<controller_reference_static_ff_v1.py>)。只补C1平滑reference名义静力变化的差分关节项，原共同LQR/120-4 PD/K/整形/PD-D4-DC/碰撞/gate不变。全12s两DC改写仍0，未知Fn/alpha/标定/误差预算不闭环；默认runtime/UI/BSP均未改，四TRAIN DR继续暂停 |
| 本轮M2唯一case | [520141结果](<T01_REFERENCE_STATIC_FF_V1/runs/v2_t01_reference_static_ff_nominal_slow_520141_001/result.json>)：原公开起点-9m、+.3m/s同正向profile，12s/1200控制/24000物理/65.8383s墙钟/fresh simulation model与FullDR各1。非接触检查全true，左/右支持92.210%/98.715%，whole低支持43个孤立.5ms点，guide/hard0；原两项接触门仍false。比原正向91.570%/98.035%、92点有所改善，但roll RMS .00941665→.0210572rad更差；不是通过/根因唯一证明 |
| 本轮FF代价/归档边界 | 额外关节峰1.9572/2.0121Nm、轮0，余量整体缩放1次/min0，额外关节共同和残差0；不承诺物理力零和。SDK-free terms1201/内部FK10809为本实际controller计算，不是独立物理例；FF求值总17.0882s/平均14.24ms/最大35.9062ms，未获100Hz墙钟实时/ARM WCET资格。三raw仅producer边写SHA/bytes索引，不读payload归档；本M2新trace尚未额外归约 |
| 新case | [逆向完整结果](<T01_OBSERVABILITY_V1/runs/v2_t01_reverse_observe_nominal_520130_001/result.json>)：12s/1200控制/24000物理/49.146s墙钟；非接触检查全true，左/右支持93.640%/98.540%，全机法向和≤1N共76个孤立.5ms点，guide/hard=0；原两项接触门仍false，case_screen_pass=false。公开flat_run另一端-5.5m初始化后-.3m/s，方向/位置均不同于旧正向，非等条件改善对照 |
| 当前物理job | **无；M2 pwsh-be15113556484a91已收exit0，不重复收完成通知**。5个v2名义例累计6000控制/120000物理；没有旧case/QA重跑或硬件发送。520141已消费，不重开准备/恢复/实际case。原逆向520130及[唯一一次归约](<T01_OBSERVABILITY_V1/REDUCTION001/RESULT.json>)封存；旧正向/M1的2kHz执行链改写占比仍未知 |
| 下一实质动作 | **M2接触失败且roll RMS变差，不扩FF系数/seed/DR，不采用；已消费M1+M2=2/最多3，仅余M3。** 先从既有小结果及必要时本新M2控制trace一次归约参考幅度/实际跟踪/相位，定位为什么参考FF峰达2Nm及横滚RMS升高，再给一个有物理依据的第三机制；不重扫旧raw、不微间隙探针或重复接口QA、不把9.51%耦合当巨大串扰或直接扫diag/K。原PD/D4/DC/模型/gate、3ms/.55/.8不改；未知Fn/alpha/标定不闭环。全36仍0/36、T01尚未毕业 |
| 新观测一次归约 | [REDUCTION001](<T01_OBSERVABILITY_V1/REDUCTION001/RESULT.json>)只顺序读本新control trace1200行，motor/contact/旧raw读0、新model/物理/控制重放/hash重读0；计数与流式记录一致。目标改写或共同分支抬升仅1次/control_index=1，类别不足以判作机械撞限位。共同时刻早于packet epoch5.25ms，实际后tick查询age15.25ms；1198帧中数字界/alpha/硬件同步/force资格全0 |
| P0力模型已封存 | [模型](<CONTACT_PROXY_V2/nominal_model.py>)、[输入门](<CONTACT_PROXY_V2/contact_proxy.py>)及[RESULT](<CONTACT_PROXY_V2/RESULT.json>)：1个公开名义模型compile、恰3次forward、0积分尝试、时间均0；纯FK45/source kin54/static sensor3次，不重算K/trim。body/COM/inertia最大9.72e−17m/1.71e−16m/5.56e−17kgm²，Jacobian最大2.61e−11，gravity投影5.26e−11Nm。已有trim自然解得Fn_Z=[70.057416,70.168100]N、轴向[69.348215,69.457779]N、Tp_y=[2.396131,2.399917]Nm；不是独立力传感通道或接触身份，静态fixture第三样本conf约.49，cap硬限.55，未知None；[契约](<CONTACT_PROXY_V2/README.md>) |
| 本轮对齐代码 | [stdlib接口](<signal_alignment_v1.py>)＋[check001](<SENSOR_ALIGNMENT_V1/check001/result.json>)：224条新合成断言，仿射最大差2.77556e−17、D3 10ms到达延迟保留为age15.25ms；恒加速位置用解析曲率界对照，20点曲率gyro仍有8.3125e−7窗口偏差。保留两端原时刻/窗口/权重，无外推；缺界None、同epoch改内容/回退锁存、held不生成新导数样本。解析界另带1e−11算术比较容差，不是已认证硬件/浮点总界；force/alpha/同步资格均未制造。[契约](<SENSOR_ALIGNMENT_V1/README.md>)；不重跑check001 |
| 时间输入门已核对 | [新边界check001](<PROXY_INPUT_TIME_V1/check001/result.json>)：6个新元数据例/18断言，真实model/forward/FK/物理/旧raw均0。调用封存step的原时间门、force model为惰性stub不求力；源名义5.25ms skew和整体10ms D3平移都被原3ms门挡住，未知时刻仍None。假设填同一epoch仅进入warmup，不构成真实对齐证明；该旧check阶段尚未创建生产resampler/packet adapter（现Round23新诊断已接归一化/真实插值，仍无force资格），默认门或confidence均未改 |
| 新可选执行链记录 | [纯记录mixin](<actuation_telemetry_v1.py>)＋[默认OFF adapter](<bridge_motor_telemetry_v2.py>)，默认runtime未接入，Round23新诊断Plant已显式组合启用并跑完整1例。只旁观原两次DC clip和功率阶段后保持值，私有诊断不得回流控制/proxy/FSM。新[check001结果](<ACTUATION_TELEMETRY_V1/check001/result.json>)：6预设干运行profile/761断言、三路保持力矩差0Nm、380个stub时钟调用、真实model/物理/旧case读取均0；不等于全车接入/执行器标定/WCET。M1旧2kHz实际饱和占比依旧未知；[用法及限制](<ACTUATION_TELEMETRY_V1/README.md>)，不重跑check001 |
| v2失败驱动机制计数 | **M1与M2共2/最多3已实测，均未采用**。M1横滚力偶：roll峰.0220729/RMS.00734366有改善，支持91.640/98.160%、whole84仍失败；M2参考静力差分：支持92.210/98.715%、whole43仍失败，roll RMS .0210572更差。C的名义对角化仅几何设计，rho=.0950714，不是额外已跑机制或充分根因证据，不采用/不强加。原默认控制保持，不能拿rc0或低支持点减半当通过 |
| M1遥测/软件prefix | [一次新遥测归约](<T01_ROLL_FORCE_V1/M1_REDUCTION001.json>)：1200行含packet/gyro、0旧raw；请求力偶峰值6.28299N，额外关节峰值1.11153Nm，余量缩放0次，不是实测支持力。2kHz实际饱和占比仍未记录。首次生成器3空格vs实际2空格锚点失败、0model/物理；[原prefix](<T01_ROLL_FORCE_V1/PREP_ATTEMPT001.json>)与[原脚本](<prepare_roll_force_v1.py>)保留，[单次恢复](<prepare_roll_force_retry001.py>)仅修正确切根因后跑上述唯一case；不重跑生成器/归约 |
| 一次归约证据 | [reduction001](<T01_SUPPORT_TIMING_V1/reduction001/RESULT.json>)：1200控制+20000接触各读一遍、0新model/物理、0旧case。新轨迹请求力矩重现最大差0；左低支持1686点，仅68点前后正力接触环境集合有变、非几何间隙结论；子步分布分散。旧差分PD等效轴向K约2294–2538N/m，不支持臆测超高刚度；7–8s集中79/92无支持点。motor2kHz饱和占比原本未记录，仍标未知 |
| 子代理 | Round24仅复用C/E4，现均已交付并正常停止，新代理0。C的[VMC_DIAGONAL_DESIGN_V1](<VMC_DIAGONAL_DESIGN_V1/FORMULAS.md>)1 operating Jacobian(内部9纯FK)+1tiny FK、0 SDK/model/forward/积分/旧QA，实际bridge API附加核对因SDK约束跳过，未冒充完成。E4的[REFERENCE_STATIC_FF_DESIGN_V1](<REFERENCE_STATIC_FF_DESIGN_V1/README.md>)2目标terms/18内部纯FK；基点trim回代2.67e−15Nm，±.02rad例差分修正约.21/.30Nm，多来自gas，非根因证明。解析草稿未执行；父只复用其static_ff.py做上述M2。原CONTACT三姿态与时间14stub/83断言不重开 |
| 本轮软件准备prefix | [原准备脚本](<prepare_reference_static_ff_v1.py>)3空格锚点和实际2空格不符，失败在派生runtime/目录/模型/物理之前，非robot failure；[原log](<prepare_reference_static_ff_v1_001.log>)保留。[唯一AST恢复](<prepare_reference_static_ff_retry001.py>)只改该call字符串/[回执](<REFERENCE_STATIC_FF_PREP_ATTEMPT001.json>)，成功后才运行唯一M2。原/恢复脚本与实际case均已消费，不再执行 |
| 代码接线 | model_builder_v2.py保留完整P0机构+真实最新版47289静态CAD；DR/命令整形/协同轮腿LQR/接触评分直接迁移现有源码，替换真实机械域与.0625半径，不搬旧K |
| 旧历史 | [v1冻结台账](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>)全部保留；v1 C2非接触通过/支持失败、3/3机制和420152已测间隙不重开或重评分 |
| Git | Round23唯一新逆向实际执行链/源时刻case及一次归约已同步[commit d8f6ef2a](<https://github.com/lulunomaro/polar-rl-train/commit/d8f6ef2a8077aa1cc5eaf6ba006efd39fb43cf79>)；tag `trial-20261106-mod4v2-reverse-actuation-observe` / object `3f0d6d098b1a3f7b7b38a37f0276ebcd9998f754`。44 selected+record共45项，原helper一次/in-memory sparse-add/atomic nonforce，ownbranch-tag-peeled远端完全一致；job pwsh-aa91095249c0472b已收exit0，不重收完成通知。三个新raw用实际bytes/行数及producer边写SHA索引，不归档重读/重hash；P0/CAD仅实际path/size/既有身份或未知SHA。main dadd48ee仅只读观察；未碰RL worktree/index/main/force，旧5659/4892/f4/a362/c0fe及历史pending保留。此postreceipt行随下一实际源码阶段归档，不新建回执循环 |
| 上次Git阶段（时间对齐历史） | [commit 5659f757](<https://github.com/lulunomaro/polar-rl-train/commit/5659f757ffba5f9670991606b16b9fa2ae2c1814>)，tag `trial-20261106-mod4v2-sensor-time-alignment` / object `5ce38a1bf73d1ee9834e6501b7c1e942292e7e12`，22 selected+record23；job pwsh-806a617aa71e4b1a已收，不再重收。该stage仅分别测试接口，后续Round23才接实际Plant；原14stub/83断言及224合成断言不循环QA |
| 上次Git阶段（历史） | 新名义力模型/私有执行观察器/原时间门阶段已同步[commit 489236bc](<https://github.com/lulunomaro/polar-rl-train/commit/489236bc0bc0aa6c8e53a1e2c0cd48b636ec1bed>)；tag `trial-20261106-mod4v2-force-model-observer-static` / object `7d35e9a0b0a8a08fa4b8bf3adc5f0a8a92e800ba`；40 selected+record共41项，原helper一次、atomic nonforce、ownbranch/tag/peeled远端一致，job pwsh-b53dd3930b534f94已收exit0，不重收完成通知。原f4a6bcca/a362ef38/c0fe82d7及历史pending保留；main新值79ea28c7只读观察，未回滚/推送。此stage仅小源码/公开constants/结果/prefix/log；原P0 XML仅真实path/size/既有SHA索引，未作归档payload hash；无旧raw/物理重跑。此postreceipt行随下一实际阶段归档，不新建回执循环 |

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
