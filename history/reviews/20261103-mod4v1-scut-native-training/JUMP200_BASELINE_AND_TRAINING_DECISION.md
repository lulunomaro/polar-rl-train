# 200mm单台阶实际基线与训练决定

2026-11-05 00:44接续：人类已明确“允许100小时”，累计按每小时保存/评测/实际回放与定向修复接续，达到目标提前停止，不重复问同小时授权，原canonical余额/reserve保持。fresh四卡72两4090空闲24203MiB，已选GPU1启动接近/上推奖励修复版20,000环境；owner1624598/create1793810449.35、唯一local61200/create00:40:28.273021/session54368，INDEX5small55refs和launch/FIRSTonce消费，20,000scene完成，FIRST仍pending。上一final150/all80/4图已完成；当前新原生更新与GO/save绝对值以soleFIRST回执为准，不能把旧0起跳当新结果或再次启动。

2026-11-05 00:32最新：批准原hour已完整结束，70新PPO/33.6M样本/final150/Adam3000/fullfinald0735d97…；独立80=41起跳请求、0真实起跳/越沿/落台/成功，80局原7.98秒timeout，0闭链/mimic/数值异常。4张实际早晚图已审，完整训练/评测日志0实际错误。实际23:10:11保存、23:13:00原owner完整释放；00:13:43才因另一聊天读者退出而正式传回，延迟没有延长训练。策略退化成台沿前停滞，idle每步仍得.082479奖励。已修接近阶段五项正奖励按真实前进门控、push新增原源码向上速度奖励；12+8必要CPU检查通过，5小文件/55refs候选准备完成但0INDEX/LAUNCH/GO，新hour待人类批准。全部实测和决定见`JUMP200_FINAL150_AND_APPROACH_REPAIR.md`；下文旧pending均历史。

2026-11-04 19:36–19:39在实际空闲72 GPU1运行80首局/newDR/seed9137/400Hz，来源为小阶梯final `f6b6b649b78752a89c0688850ae89e93afd0a87fe21eb6b6705f9b02ecf81da4`。0optimizer/0ledgerwrite，原owner1613410/create1793792185.63已ownwait/released，正式NPZ传回均SHA核验。当前没有本聊天活controller，原once不重跑。

原生mesh读回只有0与.2m两种高度、台沿x=.8m，一块水平台顶。80局全部有实际raycast阶跃→JumpTakeoff请求并进入push/tuck阶段，说明新增路径在真实SDK中执行；但源策略仍贴地向前，0真正向上飞行、0轮后缘离地越沿、0台顶触点、0落台或成功。78局原接触终止、2局原任务8s timeout，平均132.9375controls=2.65875s；闭链、mimic、数值、raw异常重置均0。

终态主要为导轮04撞台沿（77个接触终止），导轮06也出现在9局终态，集合有重叠；不能把它说成碰撞求解器错误。env0起跳请求.92s，env40为.94s，env41为.86s，实际进入push/tuck但目标hip仍大多+.5，无跳跃加速；这是已有行驶策略对新任务的基线，不是新增PPO训练失败。新增三项上游起跳reward types实际非零执行，未使用力或速度助推。

当前模型已审看原侧顶2图及轮廓纠正后2图。首次top图误带旧1m中心方框，保留原图/回执，并另出仅x=.8实际台沿的纠正图；没有改pose、mesh或评测。四个选例都在壁前地面运动/接触后结束，不能称200mm跳跃。完整WORKER.log15,610B SHA `64257c36d078285d6e8563107179fe64f07c94d795eeffdae5c22ecab50aa61a`，0实际errors。

决定：已明确修复任务选择，下一步是以单台阶起跳/落地奖励训练新策略，保持现完整学习状态与资产nominal保护；不原样续小阶梯任务。候选以same20,000的FULL_V4来源恢复actor/critic/STD/Adam/LR/iteration与RNG/队列，显式source_profile=scut_stairs→target_profile=jump200，再一次freshphysicalreset。合成真实RSL rollout/update/fullsave/跨任务restore检查已通过，0生产PT/physics；不能称原生训练FIRST。

原attempt08的18:52:48绝对保存窗已结束，本次评测不另产生一小时。修正后20,000环境/3600save+300exit训练窗口已获人类明确批准：“批准200mm跳台阶训练一小时”；同一原canonical余额、不grant/退款/延长旧窗，不重复询问已给出的授权。按此批准继续fresh四卡与原锁准入，冻结仅变更module/control；FIRST验证通过才绑定唯一回传。最终必须独立80、实际回放并据证据决定接续。

19:59实际接续：launch首次被standingV30本地FIRST读者在网络前拒绝，生产once与namespace均未消费。当前从V30真实FIRST回执确认其共享锁窗口至20:56:35；准备唯一localtimer于20:57:35后核原owner释放和原锁，再刷新四卡与launch。原20,000环境新小时尚未开始，所有等待不计训练；不能以空卡绕canonical共享锁。

21:11当前覆盖：批准的新jump200hour仍未GO。20:52准入未能继续的实际原因是原本地gate将新开的FPS/MuJoCo51820误判；已按确切身份与源码SHA修复分类、保留原false，其它真控制器仍阻止第二SSH。当前共享owner已变为20:54:24启动的E3W5，保存21:54:24/nominal21:59:24，独立collector66124在读。唯一local63556恢复尚未消费的准入，释放后完整原检查与launch/FIRST/postround自动接续；不是新建授权或重复生产。

22:23原生训练纠错：首次生产已经actualGO但在checkpoint恢复时_mode_enabled命令模式schema不同而结束，0有效PPO/FIRST/FINAL/eval，owner已完整关闭释放。合成跨任务测试此前未覆盖真实specialmode全局向量，不能把其通过当原生恢复通过。现在仅显式跨profile迁移该配置向量为新constructor全关，保留actorcriticSTDAdamLR和兼容命令/命名RNG/组件队列/计数器；新增真实差异反例CPU检查已通过。attempt02保留原SAVE23:11:34.580026/NOMINAL23:16:34.580026，22:22于同GPU1启动，FIRST仍待原sole73240读者。

22:32实际训练通过：修复版attempt02已经完成首个真实PPO，iteration81/480,000样本/20新Adam，actor/critic梯度非零，FULL_V4完整首存SHA `96b9ff560d0e158ca9495e0907cf1eec254adc1c8b76d1b3bb0be8125612a531`（40,556,699B）。FULL_STATE_RESTORE回执确认source80/17optimizerentries/Adam1600/LR及组件RNG队列计数器恢复，明确记录_mode_enabled从3项到新任务1项false配置；STARTUP为真实0.2m单台阶。完整首轮WORKER日志0实际错误，原训练进程继续，唯一collector61924已绑定。批准原小时的保存/退出截止保持23:11:34.580026/23:16:34.580026。决定继续本轮剩余窗口，原owner完整保存退出后立即独立80和实际回放；首轮执行通过不代表已经跳上200mm。

23:15正式回传受阻：本地61924按原计划到SAVE+45后等待串行通道，原finite-read尚未开始，stderr为空。实际阻塞是另一聊天23:11:52启动的远程元数据collector36120及parent62684；源码确实持有72 SSH/SFTP，不能按GUI排除。已保存本地exact身份、源码path/bytes/SHA和该聊天本地FIRST证据，0新网络/模型/physics/账本写入。本轮原SAVE已过且不延长；FINAL、完整退出、独立80结果仍未知，不以另一owner已GO推断成功。保持唯一61924等待真实释放，结果到达后立即完整保存核验、实际回放/all80分析；当前不决定原样重训。
