# attempt07完整保存、原生80评测与接续决定

2026-11-04 17:03已完成训练、安全退出、独立80首局及正式传回；当前已原生查看全部早晚侧顶4图，collector59804与原owner1605308均结束。当前没有本聊天活controller。

本轮20,000环境实际31次PPO、14,880,000 onpolicy样本、5,952physics ticks、620Adam；FULL_V4 final37,849,545B，SHA `ffce8d5ad2662a8981d971906e4b30bba13da38debbf42b6bc68284345f66d8c`。模型、actual400Hz和pose均由原collector核SHA后传回。完整WORKER.log115,474B与EVAL.log15,451B已有限读回，actualerrorlines均0，无production/evalERROR。原owner ownwait/settled/released，未增加预算或延长原SAVE17:02:25.845096/NOMINAL17:07:25.845096。FULL_V4原serializer保存完整学习/RNG/组件/队列/计数器；本次评审不为归档重读PT。

独立80为seed9137/newDR/最多400controls/8s/actual400Hz/0optimizer：53局至少一次双轮升阶、63局至少一轮升阶，只有2局满足连续.5s完整稳定观测指标（env49为1.8275s，env74为.675s）。78局8s评测cap、2局真实globalboundarytimeout、0接触姿态终止；closure/mimic/数值/raw异常重置均0，mean7.97975s。仅10局双轮更高支持连续.5s，说明短暂升阶接触不能替代持续支持。该指标是本项目观察，评测含standing/heading/special命令，不冒充上游毕业或270mm成功。

所有目标/CAD差值合规。四腿motor target MAE约.102/.076/.098/.082rad，左/右hip目标上限命中94.69%/59.47%。第一轴执行clip约.003%，此前100%饱和已不再是当前现象。height平方平均加权项-.01337与其它分项已完整记录；原SCUT的observed_height本来是world root z，再在奖励减raycast ground，不能仅因其负值误判高度错误。当前证据不足以把hip饱和或稳定不足归结为唯一奖励原因。

原生审图：env0命令全零，在出生中心附近停留；env1逐步驶向负x坡阶，连续双轮更高支持仅.0075s；env40在.8–2s驶向正x升阶后离开窄画框，all80确认连续双轮支持.3075s/稳定.1825s；env41至2s离框，6.48s触发globalboundarytimeout。离框不算成功，也不算无故消失。保存pose已是wxyz，未换序，渲染0NN/0新physics。

原有效0fdd来源诊断为56bothup/60anyup/2恢复，本轮53/63/2，没有明确技能提升；旧诊断尚无globalboundarytimeout，比较不当作完全匹配的因果实验。当前已解决20k原生碰撞缓存执行失败，不能因此宣布稳定上阶学成。保留本轮有效final与完整状态，下一步围绕既有400Hz支持中断、命令/高度与hip限位饱和定向分析后选择修复；不原样再开失败小时。人类本次一小时已消费完，新训练窗尚未获授权。

最终日志读者的两次错误均保留：新本地FPS MuJoCo viewer被RMPOLAR宽匹配在网络前拒绝；检查源码后只按确切PID/create/exe/argv/SHA分类。随后读者错误拿launch时bash身份与原owner exec后的Python比较而拒绝，改读returned OWNER_STARTED确切身份后成功。没有重启生产、重跑评测、改canonical或kill其它进程。详见ACTUAL_PATCH07_FINAL_NATIVE_REVIEW及原错误报告。
