# 同步取消站跑和自转的未经标定滑移硬否决

用户2026-10-04指出“不是说取消0.15这条未经标定的硬否决了吗”。此前v1只取消自转承重滑移否决，而原站跑admission仍有两个网格支撑点滑移0.15条件。本次补齐该遗漏。

只新增版本化验收/监督器：flat和spin都把有限滑移数值作为诊断，所有旧raw报告/原flat admission/mesh/legacy/loaded015布尔保留。速度跟踪、姿态/真高、漂移/停车、承重/卸载、网格间隙、闭链、动作平滑、硬件限幅、严重个体与接触数据完整性仍否决；非有限或缺失滑移读回仍否决。奖励、PPO、white_v2、网络观察35/38、6动作、资产/物理/reset不变。

新版本scut_style_nonslip_gate_v2_flat_and_spin，唯一代码root仍MOD4_SPIN_ROLLING_REPAIR_20261004，status/log/canonical owner仍MOD4_scut_spin_rate_20261002。新入口supervise_scut_style_continue_v2.py与migrate_flat_gate_v2.py各只执行一次；已有v1 entry、预算/迁移/恢复不得重跑。

先CPU逐条件合同和19575/19732真实既有报告版本审查，再独立watchdog保护、精确核验旧父/guardian/trainer的/proc身份，暂停旧父启动权限，trainer自己run STOP_AFTER_SAVE完整退出和CPU68浮点完整有限后，记录退出观察边界，结束旧父/guardian，等候实际锁释放再结清未计账尾段一次。安装新文件时132原源全部不变，仍唯一252000秒/三已应用扩展。释放锁后启动新父独立session，进行自己最新正式源真实flat/spin和双seed nominal/white_v2八份15秒配对。不是只按旧数据改布尔就开8。

既有19575/19732两份完整正式策略重分类记录注明复用真实证据而非新回放。最新源固定为真实迁移trainer自己的完整退出保存；失败保留源/现场和预算。当前paired成熟回滚仍17196/5white_v2，直到新版本最新6完整配对通过；8/10/4π需各自物理/128完整PPO预检、完整暖启动、有界试训、两策略/多seed验收。只改rate，不混DR/奖励/物理/移动/FPS/地形，120rpm仍目标。

每2h线程巡检，健康无实质变化静默，用户本次主动要求纠正的检查不改变巡检频率。预算耗尽或目标实际完整验收后完整保存/final flat/DRspin/nominalspin、AUTONOMY_FINISHED，旧滑移布尔并列；终验后才删除mod4-10，不自动加时。


## 实际完成接管

详见REPORT_V2.md和HEALTH_V2_INSTALLED.json：迁移已completed，固定19975完整源、68浮点有限；parent17344/start26974951和guardian17379/start26975017独立会话实际核验。最新源真实站跑/自转和双seed配对正在既有流程中，尚未6成熟或8生产。未读到已回收trainer数值退出码，receipt保留null；实际退出、完整保存和正常日志已核验。未计账尾段307.9612023830414秒只结一次，冻结余26691.911346912384秒，预算总252000不变。132原候选源未改、新增两源后134全部一致。所有entry/migration/stage_and_launch已执行，勿重跑。
