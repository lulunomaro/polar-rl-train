# 当前SuperMimic抽象、训练闭环与开源差异检查

2026-11-06，北京时间。用户要求“全面检查当前supermimic训练是否还有别的抽象问题”，追加“还有你是照着开源抄的吗？开源有这个问题吗？”。本次是检查和归因，生产训练源码、共享vendor、奖励/物理/DR与旧检查点均未改。

## 结论和检查边界

当前实现是本地固定vendor主干加MOD4任务适配，并非论文作者官方原版的完整移植。命令漂移之外，还确认了context内部不一致、缺少明确地形和部分DR条件、一步含噪context训练与H32展开分布不一致，以及中断检查点事务标注/异常清理错误。价值失真沿用final5936既有实测，未重复读取生产PT。

当前本聊天仍停在已完整保存退出的final5936。真实owner退出、三原件SHA、独立80和全部实际回放的结论不改；本次0新增SSH/生产PTdecode/物理步/优化器更新/训练重启。下面的CPU注入与合成反例证明实现行为，不代表新策略效果或实际错误出现频率。

阅读范围：supermimic_newton.py、supermimic_train.py、supermimic_evaluate.py、newton_env.py、newton_checkpoint.py、继承ctx_reward_learner.py/vendor learner/networks/replay/geometry、真实Fudan奖励和采样替换调用。当前本地八份vendor文件与生产SUPERMIMIC_BINDINGS逐项bytes/SHA一致；核心实际源码SHA保留在N/supermimic_abstraction_audit_cpu/ABSTRACTION_CPU_REPROS.json。

## 确定错误与已测失真

### A1：固定外部命令进入了可预测context，投影没有固定它

位置：CODE/supermimic_newton.py:39–55；ctx_reward_learner.py:395–398。

真实命令固定(.6,0,0)，但default mask为全1；learner先context+delta，再传给projector。赋值value[:3]=context[:3]只复制已预测的新命令，随后goal也读新命令。旧CPU复现H32中每步注入+.001，vx从.600到.632；固定两组命令delta的对照保持.600。问题属于本地任务适配；没有宣称量到了生产实际漂移。旧证据IMAGINED_COMMAND_HOLD_CPU_REPRO.json继续有效。

### A2：同一个动作在actor和critic上下文中可变成两套值，常量DR也可漂移

位置：CODE/supermimic_newton.py:51–56/218–228；newton_env.py:528–566。

真实context139由actor35、critic78、Fudan10及action queue16组成，许多槽具有确定约束。当前仅actor14:16轮位置占位归零、22:28动作历史强制写入新action；critic对应的49:51和57:63却继续依赖aux预测。critic质量尺度106、材料107:113及action lag也跟着delta递推。

对真实projector注入+.01后，actor动作历史严格等于新action，critic动作历史仍是另一组值；actor轮位置为0而critic占位为.01，mass_scale1→1.01、material.9→.91、lag2→2.01。新旧状态可因此变成真实环境不可能出现的组合。确定性字段应按语义统一构造，episode常量应固定；不能依赖网络“尽量学会不漂移”。完整数字在ABSTRACTION_CPU_REPROS.json/context_projection。

### A3：当前critic已失真，新增开源对照证实它不是上游原样逻辑

位置：ctx_reward_learner.py:416–420/459–489；vendor Critic.forward。

本地critic只有输入归一化，输出直接加到真实单位的折扣回报；目标来自想象轨迹和自身bootstrap，未做return目标归一化。既有final5936校准128真实buffer端点125个超过真实宽松±80，均值−374.461；32条保存动作展开即时折扣reward均−.011586，bootstrap均−754.288。这是已有实测，不能用“value是归一化单位”解释。

固定公开Uni版本ac19b73有_v_mean/_v_std的目标归一化、归一化target的±20裁剪，并在bootstrap还原真实单位；本地没有这些。缺少这一层不是单独的数学必错证明，已测实际失真才是阻止原样续训的直接证据。应查真实return/想象分布/常量一致性和有限episode边界，不能只给输出加clamp称根因已修。

### A4：有限worker绕过事务进度，中途异常仍可把部分轮更新标safe

位置：CODE/supermimic_train.py:146–164/209–217；ctx_reward_learner.py:493–510/580–601。

原learner有pending_iteration、collect_left、wm_left和phase。正式有限worker另写collect→4WM/aux→policy循环，未设置pending_iteration，只在整轮结束后更新collect_fraction/iteration。异常路径调用原_checkpoint时，pending=None直接得到update_boundary_safe=true。

CPU实际执行该main的AST，注入“第一项模拟WM计数已加后异常”，未执行任何真实优化器：中断元数据为iteration0、WMcount1（计划4）、collect_fraction0（本轮实际2controls）、pending=None、safe=true。恢复无法识别还欠几次WM/aux/policy或采样余数。属于本地有限worker错误；正常整轮边界的final5936未因此判坏。

### A5：异常保存失败会跳过worker自身清理

位置：CODE/supermimic_train.py:211–217。

finally先保存model_interrupted，再bridge.close/env.close。如果保存本身抛错，后续close和APP_CLOSE_INTENT均不会执行。CPU运行真实finally AST、注入保存OSError，三项close标志均false。原owner超时兜底可能仍回收进程，本次也未实际制造资源泄漏；问题是worker自身不能保证该失败路径清理。修复需要让保存异常与close各自完成并保留原错误。

## 确认的建模缺口与结构风险

### B1：平地平移不变特征丢掉单台阶所需信息

位置：vendor geometry.invariant_features、networks.WorldModel.inputs；CODE/supermimic_newton.py:44–46/218–228。

物理state保存root xyz，但WM、aux和critic使用去掉x/y/yaw的invariant_features。context中没有显式台沿距离、平台几何或ray信息；状态机只提供间接模式/高度信号。对相同q/qd/速度/姿态/context的状态平移x+.8，WM输入和critic输入差严格为0，物理上相对固定x=.8台沿的位置已变。这是输入可识别性反例；未模拟这两状态、未声称原生产频繁出现完全相同context。

应给特权世界模型/critic当前相对地形信息，或采用含地形的状态表示。actor是否加传感通道属于单独部署接口设计，不必把所有训练特权量塞给actor。不能把平地对称假设直接当台阶条件成立。

### B2：部分真实随机物理参数未进入WM条件

位置：newton_env.py:285–311/412–425；supermimic_newton.py:218–228。

质量、摩擦、部分PD/lag已在critic/context里；气弹簧压力factor、gas damping、chassis COM偏移、motor_gain没有明确输入。CPU调用真实context函数，在保持瞬时state/obs/queue一致时将这些参数分别改成1.1/.9/.01m/.9，得到同一139维context。

真实动力学依赖这些值，WM却只能拟合条件平均或靠不充分的瞬时torque/反馈间接推断。不能宣称完整D0–D7在真实sim开启，就代表模型已经正确条件化全部DR。保留真实DR，补充模型可用的episode常量；这不是关闭随机化的理由。证据DR_CONTEXT_VISIBILITY.json。

### B3：训练使用真实动态context，想象使用预测动态context；aux只有一步训练

位置：vendor learner._wm_rollout:244–261；ctx_reward_learner.aux_update:337–353、policy_update:388–408。

state WM的k8展开每步喂真实xi[:,j]。reward/context/done head在真实s、真实s1、真实xi上独立做一步监督；H32 actor却连续递推预测s、预测xi和带噪raw35。CPU用记录WM确实收到逐步真实context0/1/2，aux函数没有对应多步展开。

xi原本是episode物理常量时，固定使用不会产生该差别；我们的xi含观测、队列、contact、模式/时间等动态量，于是新增一条未在同种闭环上训练的反馈。需要在自回归窗口联合对齐state/观测/reward/done，或者把已知确定部分解析推进，不能只把WM window或H32调小声称已修。

### B4：actor看到的观测与预测物理状态可以彼此脱节，想象缺真实噪声/延迟生成

位置：supermimic_newton.py:36–38/218–228；ctx_reward_learner.py:152–175。

obs直接返回context[:35]且add_noise为identity。合成反例固定context、物理jointpos改+.5rad，actor输入完全不变，obs对该物理joint梯度为None；其它reward/WM路径仍有梯度，不能误报“BPTT全被切断”。实际raw35已含100Hz噪声/延迟，aux用确定性MSE预测其变化，相当于拟合随机结果后递推；预测后的物理状态和传感状态不强制一致。

learned observation head本身是论文允许的选择，问题是本地一步含噪目标及闭环一致性/时序。公开G1例子从预测state解析构造clean obs，每步另加sensor noise。修复不能只把identity改成随机加噪，那会给真实采样二次加噪，而且没有恢复100Hz/50Hz的原延迟语义。

### B5：全部想象起点都避开8秒真实终点，精确timeout规则无法约束价值尾部

位置：supermimic_newton.py:47–50。

frames<399−32使最大起点366、H32最大终点398；imagination_timeout在399才触发。CPU枚举证明所有允许轨迹都到不了精确timeout。critic输入最多训练到397，398只作为尾部bootstrap出现，真实已知terminal边界未进入目标。

这是把motion clip“保证足够参考帧”的过滤直接用于有限8s任务产生的缺口。当前aux把done=term|trunc学为结束，不能同时假定这些timeout是一个无限继续任务却不记录区别。应明确finite/continuing语义并覆盖边界，不是笼统要求所有timeout都不bootstrap。本条未证明单独造成−374。

### B6：teacher加小残差可能让饱和通道没有直接可学空间

位置：supermimic_newton.py:75–80。

当前是raw teacher + .25*tanh(residual)后clip6。若teacher某轴>6.25，小残差无法拉回；CPU teacher=7时动作恒6、该轴残差直接梯度0，其他轴仍.25。真实teacher881的实际饱和比例尚未测，本次未重读PT；不能套用旧E0的比例。teacher自己0跳台成功，作为冻结基线不等于良好跳跃专家。后续要从现有轨迹/一次必要新评测量实际范围，再决定架构，不盲目重新放大残差。

## “照开源抄了吗”与上游问题

本次通过GitHub API取得Motphys/Uni-SuperMimic固定commit ac19b73a4f919fb2ea37dbad860b012315497139（提交时间2026-11-02T14:09:15Z）的README、learner、networks、replay和G1 mdp，原始bytes/SHA/Git blob与URL保存在N/supermimic_audit_sources/PRIMARY_SOURCE_DOWNLOADS.json。代码仅作文本读取，未运行下载代码，也未做上游完整训练。不是声称检查了所有版本或最新main。

README第15行明确称independent downstream reproduction，不能叫论文作者官方实现。本地Policy和Critic类AST与固定版相同；WorldModel有30DOF/6act适配及算子差别；learner和任务闭环有明显改造。本地SUPERMIMIC_BINDINGS只绑定8个文件的当前SHA，没有原始upstream commit和完整diff链，因此不能事后补造“完整原版移植”的谱系。SOURCE_COMPARISON.json保留匹配与缺口。

| 范围 | 本地当前实现 | 核对的公开固定版 |
|---|---|---|
| WM与H32/λ-return主思路 | 有 | 有 |
| 任务 | MOD4v2、Fudan16、固定200mm台阶 | G1 motion tracking |
| 观测 | 预测带噪raw35动态context | state解析clean obs后另加noise |
| 命令/goal | context预测后重读，可能漂移 | reference motion按frame给goal，无本地命令projector |
| critic目标归一化 | 无 | 有mean/std及归一化target裁剪 |
| PPO teacher+有界residual | 本地自定义 | 核对的Policy没有该包装 |
| finite worker/事务 | 本地自定义 | 无同一有限worker |
| return归一化恢复 | 本地不存在该归一化字段 | 固定版自身遗漏mean/std/init保存恢复 |

上游也有真实问题：该版learner.py:166–169创建_v_mean/_v_std/_v_init，525–531还原bootstrap，594–607更新目标归一化；但_checkpoint:642–666/load:676–697没有保存恢复这三个普通属性。CPU AST检查已确认遗漏，scalar例子网络输出3/mean−10/std2对应return−4，恢复默认mean0/std1后变3。这个上游问题不解释本地final5936的错误，因为本地从未启用该归一化；也不能未经复核宣称上游最新版仍如此。

basic_loco_lib固定e4181af主要用于之前采样/执行速度比较。它已有不同的value clip和任务接口，并未原样移植成当前算法。旧OFFICIAL_SAMPLING_OPTIMIZATION.md中的“官方”指当时对照仓库的原实现，应理解为公开来源，不能据此称SuperMimic论文作者官方。

## 核清的正确部分与否定假设

- 实际H32通过learned WM/reward/critic反向传播；frozen_parameters冻结权重但保留输入梯度，clip norm1/value.1在，不能把裁剪前梯度大误称没有裁剪。
- 真实step动作/上一步动作/奖励时序已追查；rawaction在送物理前clip6，bridge存实际传入的clip后动作，腿位置/轮速单位仍.5rad/10rad_s和实际机械投影。
- bridge在reset前保存物理s1、原reward和done；终止后的xi1归零且xi1_valid=false，不把reset观测当原终态训练目标。数值无效样本排除、streamcut存在。
- 我曾怀疑数值reset后ep_step1导致历史跨段，CPU泛化反例能产生该行为；追完整step后发现hard在endpoint再次reset，实际返回ep_step0，会正确padding。该假设已否定，不列当前新增bug；原反例、纠正报告和修正fixture全部保留。
- 正常完整final保存/四Adam/replay/RNG和freshphysicalreset仍有实际回执。没有把solver warmstart当完整恢复，也不把中断异常路径错误推广为所有保存损坏。
- 只缺due_tick不能单独证明动作队列Markov缺口：当前lag<=2physics，而每control有8physics，正常policy端点pending已消费。传感队列/DR/动态状态不足按B2–B4明确范围处理，不再虚增一个问题。
- 无EMA target critic不是独立bug；论文和公开主式本就采用同一critic的λ-return。学习reward/done也不是自动违反方法。

## 修复顺序及本次未执行范围

1. 先修context确定语义：常量命令/DR固定、重复观测一致、物理state与clean观测/延迟生成有明确关系；保留真实DR，不随意关噪声或缩物理难度。
2. 补WM需要的相对地形与episode物理条件，按同一闭环对齐多步模型拟合；验证reward/done/context/state各项，而非仅平均state loss。
3. 同时隔离critic真实单位、有限episode尾部和bootstrap；归一化若采用必须完整保存恢复。沿既有校准证据修，不能仅clamp/EMA掩盖。
4. 修有限worker事务进度和save失败清理，再证明完整恢复边界。候选改变mask/输入维数会改变契约，必须显式迁移，不能strict=false假称完整同契约恢复。
5. 同plant平地基础技能和实际动作响应作真实对照，再决定接回BPTT或普通PPO；本次不启动原样失败小时。

此处是检查结果及修复优先级，未声称上述修复已实施或能保证200mm成功。当前单200mm真实自主起跳/双轮越沿/台顶稳定验收保持。累计100h保守上界71437.705711秒未追加，foreign/mod4v3与账本未动。

## 复现与错误保留

- N/audit_supermimic_abstractions.py → supermimic_abstraction_audit_cpu/ABSTRACTION_CPU_REPROS.json：context一致性、输入别名、观测脱节、真实训练context、finite终点过滤、饱和条件、中断事务、上游统计保存。
- N/audit_supermimic_dr_context.py → DR_CONTEXT_VISIBILITY.json：真实context打包的缺失参数。
- N/audit_supermimic_save_cleanup.py → SAVE_FAILURE_CLEANUP.json：真实finally AST的save失败路径。
- N/audit_supermimic_history_boundary.py → HISTORY_BOUNDARY_CORRECTED.json：否定跨段假设；最初NUMERICAL_RESET_HISTORY_CROSSING.json和HISTORY_HYPOTHESIS01_REACHABILITY_CORRECTION.json并列，不将原错误覆盖成通过。
- 原CPU harness缺residual_scale、sample_device两个metadata依次失败，均在目标注入点之前，原source和错误JSON保留；补齐fixture metadata后才真正复现。模拟WM计数不冒充实际优化器更新，model_interrupted.pt只为元数据目标名，未写PT。
- 公开raw.githubusercontent.com下载超时，改GitHub contents API成功；下载错误和最终原字节索引保留。Windows初次路径/glob/访问错误只属读者，原工具输出保留。

报告作为已有Newton唯一trial的普通检查补充归档，不重record/retag。所有本次实验源/报告/参考文本SHA进EVIDENCE_INDEX；PT/NPZ/媒体不重解码或重评测。
