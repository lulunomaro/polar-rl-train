# 200mm单台阶实际基线与训练决定

2026-11-04 19:36–19:39在实际空闲72 GPU1运行80首局/newDR/seed9137/400Hz，来源为小阶梯final `f6b6b649b78752a89c0688850ae89e93afd0a87fe21eb6b6705f9b02ecf81da4`。0optimizer/0ledgerwrite，原owner1613410/create1793792185.63已ownwait/released，正式NPZ传回均SHA核验。当前没有本聊天活controller，原once不重跑。

原生mesh读回只有0与.2m两种高度、台沿x=.8m，一块水平台顶。80局全部有实际raycast阶跃→JumpTakeoff请求并进入push/tuck阶段，说明新增路径在真实SDK中执行；但源策略仍贴地向前，0真正向上飞行、0轮后缘离地越沿、0台顶触点、0落台或成功。78局原接触终止、2局原任务8s timeout，平均132.9375controls=2.65875s；闭链、mimic、数值、raw异常重置均0。

终态主要为导轮04撞台沿（77个接触终止），导轮06也出现在9局终态，集合有重叠；不能把它说成碰撞求解器错误。env0起跳请求.92s，env40为.94s，env41为.86s，实际进入push/tuck但目标hip仍大多+.5，无跳跃加速；这是已有行驶策略对新任务的基线，不是新增PPO训练失败。新增三项上游起跳reward types实际非零执行，未使用力或速度助推。

当前模型已审看原侧顶2图及轮廓纠正后2图。首次top图误带旧1m中心方框，保留原图/回执，并另出仅x=.8实际台沿的纠正图；没有改pose、mesh或评测。四个选例都在壁前地面运动/接触后结束，不能称200mm跳跃。完整WORKER.log15,610B SHA `64257c36d078285d6e8563107179fe64f07c94d795eeffdae5c22ecab50aa61a`，0实际errors。

决定：已明确修复任务选择，下一步是以单台阶起跳/落地奖励训练新策略，保持现完整学习状态与资产nominal保护；不原样续小阶梯任务。候选以same20,000的FULL_V4来源恢复actor/critic/STD/Adam/LR/iteration与RNG/队列，显式source_profile=scut_stairs→target_profile=jump200，再一次freshphysicalreset。合成真实RSL rollout/update/fullsave/跨任务restore检查已通过，0生产PT/physics；不能称原生训练FIRST。

原attempt08的18:52:48绝对保存窗已结束，本次评测不另产生一小时。修正后20,000环境/3600save+300exit训练窗口已获人类明确批准：“批准200mm跳台阶训练一小时”；同一原canonical余额、不grant/退款/延长旧窗，不重复询问已给出的授权。按此批准继续fresh四卡与原锁准入，冻结仅变更module/control；FIRST验证通过才绑定唯一回传。最终必须独立80、实际回放并据证据决定接续。

19:59实际接续：launch首次被standingV30本地FIRST读者在网络前拒绝，生产once与namespace均未消费。当前从V30真实FIRST回执确认其共享锁窗口至20:56:35；准备唯一localtimer于20:57:35后核原owner释放和原锁，再刷新四卡与launch。原20,000环境新小时尚未开始，所有等待不计训练；不能以空卡绕canonical共享锁。
