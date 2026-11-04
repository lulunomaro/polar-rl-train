# 2026-11-04：取消270mm要求，回到华南虎保存配方的台阶分支

人类最新明确：“跳台阶不再强求270mm 按照华南虎的来就行”。此前固定270mm、首次飞行整轮越沿及原地停稳不再作为后续训练硬门槛。历史试验按原协议保留；增强MOD4v1物理、D0–D7、唯一canonical、原reserve与完整保存边界不变。使用Stop That Shit技能：以当前失败和实际消费者为依据，直接修具体缺口，不用反复审计或无变化失败小时替代技能推进。

## 已完成这一轮

`env20000_target_axis_repair_1h_20261104` 完整结束，final SHA `0fdd9463205f739daff8713ade26d937846c832fba25392af4e515edc8904f86`，37,849,545B，FULL_V4。59次PPO、28,320,000实际样本、1180次Adam；owner1570673/worker1570691及独立eval1572599均已ownwaited、settled、released。唯一receiver45436于09:06完成正式传回并退出，旧launch/FIRST/bind/postround/评测均不能重放。

本次为诊断实际学习状态仅解码final一次，17个Adam条目均step1180，actor/critic有限，STD为[.846733,.079610,.074791,.131713,.105527,.106199]，LR=1e-5。完整actor/critic/STD/Adam/LR/iteration、组件RNG、全局计数和队列相关字段均存在；原新constructor nominal保持。不是为了Git读PT，也未执行优化器或新physics。

独立80首局仍0真实台顶接触、0越沿、0strict；28局原20连续接触终止、52局达到8秒cap，原任务20秒所以不是timeout。平均303.15controls=6.063秒。全部3200个400Hz回调及首局mask核对；closure/mimic/nonfinite/raw重置均0。28局最后20controls接触>1N，计数1..20，roll/pitch未超过40°。

四个关节目标及CAD差值全部合规，第一轴不再clip；左右hip实际目标仍分别92.149%/73.854%顶在+.5rad。所有活动callback机身相对出生xy最大坐标仅.24345m，最大水平位移.32596m；没有到.5m台沿。原生审完早晚侧顶4图：env0于1.16秒接触终止，后图为terminal clamp；env1/40/41至8秒仍在中央低地。限位与单轴初始化已验证执行正确，但不能说它们单独修复了技能。

## 华南虎实际公开了什么

固定来源为`scutrobotlab/wheeled-legged_RL@1a26356d6f591734d4f6f666f5cead1a6925da67`，原SHA/Git blob和路径见`project/isaac/mod4v1_scut/SOURCES.json`及extension，复用已有原文。

| 证据 | 公开保存配方/源码 | 对本项目的含义 |
|---|---|---|
| 作者明确推荐的上阶模型 | `rough_rotation_stair/2026-07-23_16-23-21`；README列平地`2026-07-19_09-14-50`到该模型的链路 | 有上阶相关模型证据，不等于270mm首次飞行专项 |
| 初始化 | agent.yaml launch_checkpoint=`flat_direct/model_8000.pt`，resume_training=false；source train.py249–265做weights-only | 依靠已学好的平地技能；同维加载不能证明MOD4原E0已有同等能力 |
| PPO | 普通PPO、256/128/64 ELU、24rollout、5epochs/4batch、LR1e-4/adaptiveKL.01、gamma.99/lambda.95、entropy.005/value2/grad1 | 当前基础PPO超参相符，未发现本轮GAE/update链新错误；先前真实RSL合成证据复用 |
| 奖励 | 保存配方26项非零，速度/角速度/姿态/高度跟踪、动作和碰撞代价 | `scut_stairs`继续原权重，不凭空加入跳跃奖励 |
| 状态机 | 该保存配置enable_state_machines=false，Airborne/JumpTakeoff/Stair/前扫辅助均false | 不能用后来stair.py的存在解释这份模型如何上阶 |
| 地形 | 保存YAML阶梯每级.005–.015m或.025–.04m，踏面.1m；generator10rows/14cols，difficulty0..1，水平.1/垂直.005m离散 | 过去固定.27m一刀台阶与该训练分布差异很大 |
| 当前另一个Rough-v1 | 当前cfg另一分支启用腾空/轮前扫描；StepUp按高度时间差抬高height command；当前min.12/max.14/wall.14m | 是另一套任务，不能与七月保存配方混称；不直接复制该阈值到任意阶高 |
| 轮腿执行 | base_env2774–2779按scale/default解码，2871–2878先限位再delay | MOD4现补齐contract限位；原PD/DC/队列保留 |

来源视频1:55–2:08以前已经原生审看，表现为台沿附近轮腿协调；没有视频与checkpoint一一绑定或270mm标尺。既有报告`20261102-scut-standing-step-video-115-128/REVIEW.md`和帧索引保留，不重复下载/识图，也不把攀爬强称首次飞行。

## 当前问题判断

确认的问题是执行漏项曾经存在、任务分布不一致和原平地来源在此场地尚未证明可用；不是“每行追溯完成所以没问题”。本轮奖励方程、动作限位和PPO链有具体检查，仍不足以证明技能。当前还不会有效接近台沿，先查基础高度/轮腿控制，再谈起跳。59次更新也不等于公开保存目录的model1000或配置max_iterations20000；20,000环境只是并行数量，不能把样本数直接等同于已训练收敛。

新原生诊断增加实际motor angle/velocity/torque、observed/ground height和weighted reward曲线。旧记录仅有target，不能据此断言PD反向或某关节真实卡死。新记录将直接比较hip+.5目标对应的实际角度/支撑/高度，不为缺证据先改物理或随意翻电机符号。

## 本次已落地的接续

新增`scut_stairs` profile：只选保存YAML的`inv_stair_slope_for_rm_mid`，使用SDK原`pyramid_stairs_terrain`与原.025–.04m/.1m/1m平台/9m场地/1m边框/离散分辨率、difficulty及原generator出生origin，保留原多级梯形；其它rough地形不恢复。原生成器垂直离散会把连续配置量化，实际mesh与支撑高度以原生回读为准。

该inverse-mid保存键没有单独height覆盖，V13回退全局.2–.42m；初次fixture错误取不存在键的false已保留，已修为真实回退并通过attempt2。此前口述.24–.38属于其它分支，现明确纠正。原速度/heading/standing/special命令、20秒episode/随机初始clock、奖励和PPO保持。

新增上阶指标按真实400Hz水平接触点判断越出中央平台后的双轮升阶、无非轮支撑、roll/pitch<=10°且abs(vz)<=.1连续.5秒；允许继续水平行驶，不要求第一次飞行或yaw锁出生。这是本项目的运动恢复观测指标，不能冒充华南虎原作者成功判据；原270指标始终另列0/不作新目标。

3项新CPU检查通过，另6项原target/init回归通过，0生产PT/0physics。新samefinal有限80对照位于旧已关闭A下`scut_stairs_eval1`；只有7个source/control文件，模型/资产/共享代码按SHA引用。原prelaunch因standingV25控制器活跃在网络前拒绝，false/once保留；未启动native。

唯一计时器58540/create2026-11-04T09:48:09.899519+08，等待原peerV25 owner1576385/create1793756526.71。peer原SAVE10:42:07.432175、NOMINAL10:47:07.432175；timer11:02:07.432175之后才freshLOCAL并核exact peer ownrelease、canonicalNone、原authority/private/finite锁及目标GPU实测容量。仍锁住就拒绝，不绕卡/kill/clearactive。REV2冻结INDEX和timer SHA为实际入口，旧未执行INDEX保留。新对照回传后审所有实际图、80首局及新增motor/reward曲线，再决定20k一小时；不重放旧270mm小时。

该阶段仍用既有trial，只ordinary supplement，所有false/reader/patch错误与上述证据进入Git。凭据不输出/不归档，大型PT/NPZ/media只路径/字节/SHA。
