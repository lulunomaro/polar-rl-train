# 公开配方最终评测与关节目标限位漏项

2026-11-04，20,000环境公开trained_stair配方窗已完成。46次PPO、22,080,000实际样本、920次Adam更新；FULL_V3 final为37,849,417B，SHA `a8b954f378940421a5e9860faddf80c4575ae98ee062dddd1d60513de5a31aab`。原owner1565189/worker1565206已ownwaited、settled、released，独立评测与正式传回完成，receiver12564已退出。FIRST和全部launch/bind/return/train/eval once均为历史消费状态。

独立80首局仍是0strict、0整轮越沿、0leading、0台顶接触。32局按原20连续门槛终止；48局达到8秒评测上限，实际任务20秒，故这些不是timeout。51–400controls，平均287.0125即5.74025秒；闭链、mimic、数值、raw异常重置均0。全部3200个400Hz callback、首局mask和台顶manifold已重核。

新增逐body数据把终止路径核清了：32局最后20controls每步都有chassis或guide接触>1N，计数恰为1到20，姿态均未达到40°。终态27局chassis>1N，其余可见guide04–07接触；具体逐环境/逐body窗口在 `ACTUAL_PUBLISHED_RECIPE_FINAL_REVIEW.json`，不靠图猜导轮接触。不能通过排除导轮或放松终止掩盖。

当前模型原生view_image审看早晚侧顶4图：所选0/1/40/41约0.2秒降入中央低位；0于1.10秒、41于2.70秒结束，之后重复的是终态；1和40到8秒仍在低地，无真实台顶支撑。整个80局最大水平位移距首callback约0.331m。公开配方恢复后仍失败，不能继续用“奖励公式已对齐”当技能证明。

这次追到明确执行漏项：固定SCUT `base_env._apply_action` 第2868–2878行在缩放后对腿位置目标clamp；本适配沿用的MOD4 `DelayedJointPositionAction` 只有scale/default offset和crank−hip差值投影，缺少四个独立motor位置区间。±6策略裁剪不等于±0.5rad的hip目标限位。这轮前20controls左/右hip均值0.8384/0.4938rad，超上界比例85.125%/55.8125%；源E0以前也有超界，不把它称为本轮训练新造成的退化。

修复在新环境构造前替换腿action class：使用新contract按名字取crank[-1.2,.9]、hip[-.5,.5]；先限制位置，再把原CAD差值[-1.0843,.85]投影到motor区间交集，之后进入原D4物理目标队列。原PD/DC、400N弹簧、物理关节限位、solver、D0–D7、奖励和原终止均保留。实际policy sample/logprob及±6历史仍沿原逻辑，不重写策略样本。

新完整保存接口为FULL_V4；旧FULL_V3只有显式 `--repair-target-limits` 可迁移。旧V2仍需显式动作修复，两类历史文件均保留。actor35/critic78和完整Adam/LR/iteration/RNG/队列恢复语义保持，不能把执行接口变化称为同物理续态。

新增4项CPU检查通过，包括记录目标反例、12,000组按名字打乱的极端目标，以及原D4队列实际代码在合成articulation上的提交/应用；另5项动作/RSL采样检查和4项启动/完整学习状态检查通过。合计13项CPU检查，0生产PT读取、0新physics；它们不代表目标SDK原生通过。

有限对照位于已关闭attempt02下 `target_limit_eval1`，仅6个改动模块加owner/plan，共8个source-only文件；引用原共享树与同final，不复制模型资产。80首局、400controls、seed9137、新DR、实际400Hz、0optimizer、0账本写入。07:43首次本地准入遇另一已知collector，网络前拒绝，原false/once保留；该collector结束后仅恢复未执行的准入与首次launch。后续状态以此目录reports的原生回执为准，不能在原生结果前宣称限位修好即可跳台阶。

07:45–07:48，限位对照已实际完成：所有活动首局目标满足四motor限位及原CAD差值，0闭链/mimic/数值/raw重置，35局接触终止、45局8秒cap，平均5.8195秒；仍0top/strict，第一轴100%饱和。早晚4图当前模型已view_image；所选0/41终止1.38/3.44秒，1/40到8秒仍低地。这证明执行限位漏项已原生修复，也否定“只加限位即可恢复台阶能力”的推断。

接续采用显式单轴初始化修复：从同一公开配方final保留其余actor权重/STD及critic78，仅将left_crank输出行、偏置置0，该轴STD由23.454372置1；新Adam/iteration0。源文件不改，不声称这是原SCUT逐字微调方式。6项CPU检查通过，包含逐张量确认其它输出行/隐藏层/STD及critic完全保留、合成来源字节不变和freshAdam。

07:58–08:01，单轴对照在同诊断目录的新overlay_first_axis/evaluation_first_axis完成，0optimizer/0ledgerwrites。80首局第一轴确定性raw全0、无裁剪饱和，实际目标仍全部合规；33接触终止、47个8秒cap，平均5.77525秒，0top/strict，0闭链/mimic/数值/raw异常。当前模型审完早晚4图：0于1.02秒、40于6.44秒终止，1/41到8秒仍低地。它验证初始化执行正确，并非技能改善证明。

决定：按原授权20,000环境一小时接续学习，保留公开配方reward/PPO、270mm场地/出生、全部物理/DR/终止，只带入已原生验证的目标限位和明确单轴初始化修复。新任务 `env20000_target_axis_repair_1h_20261104` 仅7改动module+owner/entry/plan，共10文件、21共享SHA引用。原canonical/reserve准入保持，首次实际PPO完整保存和后续技能均以新回执为准；不把计划或launch当成功。
