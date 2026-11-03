# 恢复公开保存台阶配方的原生尝试

原E0同场地诊断已经完成并原生审看，80首局0台顶接触、0strict；前24步同端点非高度输入最大差4.77e-7，第一步动作误差1.20e-7，原输入下第一轴也100%裁剪。不能把失败继续仅归因于actor槽位错位，也不能假定原E0适用于新任务。

本次恢复现有trained_stair分支：公开保存的26个非零基础奖励及权重，额外Airborne/StepUp/Stair全部关闭，移除两项新增奖励；恢复原速度/转向/heading/standing/special命令、.2–.42m高度、20秒训练episode及随机初始时钟。8项CPU配置检查通过。修正train.environment_settings，使首次task导入前的constructor环境参数与profile一致；先前固定jump270值不再污染trained_stair。

增强资产/31body30DOF6act、400N/k2000/damping3、.0025TGS32-4/50-100-400/fullD0-D7、原PD/DC/队列与clip6不变；人类指定出生/相对台沿与固定270mm场地保持，不恢复rough课程。PPO原参数保持；源仍为原E0权重初始化，freshAdam/iteration0，不冒充原SCUT权重或完整续态。

补充pre-reset逐body接触力、roll/pitch、raw连续终止、实际命令与height记录；这只增加诊断，不放松原>1N/40deg/20controls终止。原E0诊断61终止环境终态最大roll1.715deg/pitch13.001deg，支持进一步查接触路径，但旧报告没有逐body完整manifold，不臆造某个导轮的接触证据。

新run位于同项目env20000_published_recipe_1h_20261104；仅3源码+3control共6文件，16条共享SHA引用，未复制整树/模型/资产。原canonical/authority/privateGPU/finite锁和reserve保持。原LAUNCH和FIRST观察已消费，当前唯一launcher等待实际首个PPO与完整保存；不是已完成训练或技能成功。完整保存退出后同owner独立80首局最多8秒评测，随后审实际姿态/全部400Hz接触再决策。

首次原生尝试在20k场景/恢复/STARTUP之后、首个rollout第1步报错：共享Mod4Env把RM_GYRO_CURRICULUM=0解释为禁止转向，拒绝公开SCUT非零yaw。原passed_execution=false、0FIRST/0PPO、owner已ownwaited/settled/released。已改trained_stair为yaw-capable模式，configure仍cfg.curriculum=None，不恢复旧gyro课程；train.close_application保持错误exit1。五项CPU检查通过。新attempt02仅2源码+3control，保持原06:42:51.270save和06:47:51.270exit绝对截止，不新开一小时、不退款或复制预算。

2026-11-04 06:02原生FIRST已通过：20000环境/24controls/480000samples/192physics/20Adam，actorgrad1、criticgrad1.000000119，FULLV3首存37,849,417B SHA36c18f96d290170098304564dd7ac315d5298baf1500364e27524f0ea5e38b8f。运行owner1565189/worker1565206，原06:42:51save与06:47:51nominal实际GO一致，未延长。FIRST不是final或技能成功。

首次本地bind漏传--root，子receiver误读旧A并因POSTROUND_ONCE已存在立即拒绝；无SSH/生产操作，旧失败保存。共享控制器已把root显式传给子进程，recover_bind仅首次创建正确receiver12564/create见POSTROUND_RECOVERY_EXACT_CIM，当前其POSTROUND_ONCE已消费，等待06:43:36save+45。原owner负责训练完整保存、安全退出及独立评测；alive期间仅本地检查，不重复bind或SSH。
