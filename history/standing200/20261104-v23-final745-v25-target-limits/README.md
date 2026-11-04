# 华南虎原配方站爬：实际745轮失败与MOD4目标限位修复

人类要求按华南虎站着上台阶开源继续200mm科目。SCUT固定commit
1a26356d6f591734d4f6f666f5cead1a6925da67，原flat→rough的PPO配方保留。

V23最终745轮完整保存、安全退出、成本结清与锁释放均有原owner回执。
独立80个首episode评测：0/80严格成功，整轮越沿0，双轮台顶支持0。
68个实际终止全部有原机身/导向件接触超1N、duration20拍，roll/pitch
超限均false。不能再称这些是姿态超限，也不能把执行成功称技能成功。

V23原closed传输在43MB曲线触发32MiB上限，失败与once保留。V24只补传
7个既有文件，两端字节数/SHA通过，未重新运行评测。当前模型原生查看
四例八张侧/俯视图与400Hz曲线；模型落地后维持约.19–.22m低姿态，
没有上台阶。初始.38m无支撑下降仍与自由落体接近，不全归因主动蹲下。

15,471个实际首episode控制样本中，左右髋目标分别97.2788%、99.9030%
超过+.5rad，实际关节88.6821%、95.1393%落在上限1mrad内。原SCUT
_apply_action在缩放后裁剪关节目标；MOD4旧适配缺少各关节范围投影。
V25只在原decode/CAD投影后、原D4队列提交前约束四腿位置目标，
保留原曲柄角差窗口、raw Gaussian action/likelihood、轮控制、
PPO/奖励/命令、PD/DC/D0–D7、reset与2.5ms/TGS32/4。

CPU以原冻结MOD4方法、真实记录目标及极端输入验证新提交目标满足全部
关节/CAD范围；真实RSL合成20Adam全状态迁移通过，不读取生产PT。
新checkpoint显式V25格式，从final745完整恢复actor/critic/STD/17Adam、
LR、RNG、保存counter和组件队列，再一次fresh物理reset。
这不证明修复足以学会站立或200mm。flat仍朝8000推进，之后才原rough
weights-only/freshAdam；不能提前rough或引入自创奖励。

截至本阶段准备，V25为冻结未launch。已发现另一scope已知launcher占用
串行，仅读本地published metadata。释放后重新freshLOCAL/allfour4090/
原canonical/privateGPU/finite准入，不抢锁、kill、clearactive或复制预算。
原3900/save3600/exit300与strictreserve86412.86069250107保持。

大件仅保留实际路径/字节数/既有SHA索引，无整runtime副本，无归档验模。
旧失败/once、试验tag/peeled与lqr保护。本阶段结果以INDEX及实际ownreceipt
为准，后续报告追加，不重record或重标签。
