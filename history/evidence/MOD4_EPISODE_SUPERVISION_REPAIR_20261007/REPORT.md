# 普通episode失败不再停止整批学习，20k恢复

用户在核实25525一次bad_orientation造成整批停止后明确要求“把这个问题解决了，别再出现这种一小点问题导致浪费一大堆时间停训的情况了”。新MOD4-EPISODE-SUPERVISION-REPAIR-001已登记为v1.5执行补充，主计划SHA和预算不变。

隔离新root MOD4_EPISODE_SUPERVISION_REPAIR_20261007，原213源中只修改clock_training_health.py，新增controller/目标CPU合同/SDK诊断/依赖guard等，共218份。原task/reward/DR/physics/PPO/reset/actor35-cleancritic38-action6/硬件文件逐字不变。普通bad_orientation、base_contact、low_base仍触发原episode结束/reset和原PPO反馈，只记累计/每原因/真实env与控制步，不停止其他19999环境。closure/mimic、未知终止、非有限、原因覆盖缺失和回调缺失仍完整保存停训；闭链2mm和mimic0.01rad不改，不将真实任务事件抹为0或改名timeout。

23项实际Torch CPU合同与25211完整sensor/global/命名RNG恢复9合同通过。真实SDK300控制步加24warmup、1296物理回调精确；在实际termination manager→环境reset路径中明确注入一次bad_orientation后确认继续，再注入一次closure标志确认STOP_AFTER_SAVE。两个是监督流程故障注入，非真实倾倒/闭链测量或策略能力证明。动态闭链最大0.558191mm/非有限false；SDK冻结不计PPO/预算字节exact。原已完成同范围128/20k PPO证明复用，没有重复学习预检。

另一个无关阻塞来自live terminal的tui_spin_rate.py和tui_rich.py编辑。新guard仍精确核验全部真实训练候选和全部非UI生产源；两个终端文件的原冻结副本仍逐字保留在候选，实际所有非UI Python模块无终端导入。于是独立live UI改动不再决定隔离训练是否可运行。没有热改原runtime或旧freeze，没有把其它来源差异一起豁免。预部署读者出现identifier子串、旧模块搜索路径及将其它tui_*误当非UI等误判均在GPU/PPO/账本前修正并保留；这不冒称物理故障修复。

确认旧父/guardian/trainer真实退出、own25525完整保存、2231.474350691秒既有唯一结账与active/Sactive空后，同两原锁用新唯一supervise_episode_repair.py接管。初始源选已45min健康且3060完整三类回放的25211，不预选尚未回放25525或测速权重。父/guardian/trainer分别独立session，15秒budget守卫，save25；每块最多2h，同范围健康保存后自动进入下一块，首审查窗最多6h，不等桌面巡检。块末完整源自动投递3060三类回放，普通失败率和旧技能分别审查，不伪造毕业。真实系统性能力退化仍由阶段评测处理；不能借此放任数值、硬件或数据故障。

被提前停下的25525完整权重没有丢弃，新增三份明确diagnostic_only的3060回放，原发布器拒绝记录保留。当前学习从25211开始，25525没有被称为健康final或直接用作来源。

新启动已经实际CPU/SDK/两锁/唯一PID/账段核验，实际PPO和自己首次定期完整保存以CURRENT_ACTUAL_VERIFIED.json为准，不借旧checkpoint证明新PID。维持2.5ms×4/TGS32-4/20k/100Hz/S2 E0 D1+D2，delay0，D3未部署，MoE gate未训，S8仍另需批准。总828000秒230h、六扩展各一次；本轮新增时间0，无重复尾段/清账本操作。全部旧权重/raw/flags保留，大权重仅SHA。归档与巡检记录实际进程，防止旧phase缓存冒充仍在训练。
