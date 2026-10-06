# 浅地形完整预检成本规则修复与正式45分钟训练

用户明确“修复问题后开始训练”，此前授权“你自己调好，差不多了就继续推进”。R更细分块实际没有明显改善PPO吞吐：auto0318两万环境四轮23.76/21.45/21.49/21.62秒，21739.130环境策略步每秒，较之前M21702.272只约高0.17%。原23000准入条件仍false，旧repair_hold、Traceback、全部原raw和冻结保持。物理错误与完成但较慢的PPO执行分别审查，没有把引擎计算变快或达到旧门槛作为本次结果。

auto0315十环境300步、0316两万环境120步实际任务失败0/nonfinitefalse；closure分别.074858/.184838mm、mimic.001691456/.001826981rad，完整30q误差0、ground/reward同tick误差0、6001/2401物理接触回调和实际参数初末通过。实际全部三角面世界float32按序SHA81348d8b3be401698b7c6b5ca5aecbc95372741ddc051e99b5d2c0df2877c8d5、522个最多25000面精确碰撞分块，无隐藏Plane或简化几何。两份physical raw仅SHA索引，完整证据见ROUGH_COMPLETE_PREFLIGHT_REUSED。

auto0317的128×2及0318的20k×4完整PPO已执行，实际总策略样本6144/1920000，PID500016/500311绑定保存23510/23512均CPU68浮点完整有限、精确来源23509、完整配置和R180运行冻结一致、正常退出且无引擎/PPO异常。两份权重丢弃不用作来源。真实加载/执行/保存/退出43.264833/306.875092秒已在同canonical各结一次，总350.139925秒；新复核不重跑probe/PPO，不重复计账。

新隔离S=/home/egde/rl_candidates/MOD4_ROUGH_INTRO_ADMISSION_REVIEW_20261006从R180源字节完全相同重基，仅新增rough_saved_preflight_review.py和supervise_rough_intro_admission_review.py，共182文件。新rough限定准入按精确命名的完整保存预检审查，吞吐作为耗时诊断而非硬否决，没有换成另一条更低的数值门槛。原P training函数及旧吞吐assert完全不改，其他任务规则未改。完整次数、source、PID、样本、normal shutdown、CPU有限、参数/运行冻结、预算唯一结清及600秒预检上界继续检查。目标CPU13项有意义错误数据拒绝合同通过，复核期间canonical整字节exact。

2026-10-06T13:57:41.804271+08:00真实核验新parent513081/start42110116、guardian513124/start42110184各独立session，父PPID1，唯一正式trainer513125/start42110195与canonical.active_segment、实际/proc cwd/argv及实际run_name一致。实际run=/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/logs/2026-10-06_13-55-24_auto_0319_rough_admission_stage1_learning_cap12.5664_white_v3。精确23509 SHA2f82374fe07a849dbbaeabbf8dd34b20d0df8da789f2ebc2be3e688a1b24498a完整actor/critic/optimizer/std/iter KEEP_STD1暖启动；已实际完成PPO轮次6。该PID自己的首次完整checkpoint和父监督器rolling_source_freeze尚待定期保存；实际run_manifest及runtime src_snapshot已精确核验，不把来源23509当成新PID已训练后的保存或冒称182run freeze已经生成。源23509的CPU68完整有限证明明确复用。已执行轮次只证明正式开始，不代表浅地形能力改善或毕业。段截止2026-10-06T14:37:03.156889+08:00，加载/学习/保存/退出在同预算内。随后既有rough10env15秒和两个seed三profile flat/spin/world18份回归，最终review_ready父guardian计划退出；该审查边界不是故障或全课程finished。

保持gentle五类浅地形、站20%/BODY直线±.3/vy-yaw0、每tick真实地面查询/完整30q复位、35actor38critic6action网络、white_v3、cycle_v1与其他奖励、physics/PPO、torque-speed硬件限幅及真实任务/模型/数据否决。实际源F23509的完整18份旧技能基线按精确SHA复用，新学习保存后另做既有保留回归。未混地形4π/world.5、大台阶、cliff、airborne/跳跃、自救、洞、云台或MoE。原平地4π与世界方向/DRcloseout证据不改，不称实车认证。

唯一canonical仍468000有效PPO秒130小时与五已登记扩展各一次。实际读取charged295904.284153秒、扣当前active尾段剩余172092.520884秒；无追加、复制/清账本、重复扩展或旧尾段结账。原M/R/F/旧预算/安装/恢复入口不可重跑。S新入口已唯一执行，后续只读真实receipt和phase；实际故障保留全部权重及预算，健康两小时巡检。单科review_ready/hold不删监控，不自动加时。
