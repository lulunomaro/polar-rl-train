# 2026-11-04 真实直角台阶纠正与20,000环境续训

人类要求“打开mujoco让我看看后继续找4090训练一个小时20000环境”，随后指出“你这不是爬坡吗”，并明确选择“按华南虎方式上真实直角台阶，允许轮子保持接触”。本轮不强求270mm或腾空；不能把斜坡行驶称为跳台阶或直角台阶能力。

已用MuJoCo打开attempt07 final `ffce8d5ad2662a8981d971906e4b30bba13da38debbf42b6bc68284345f66d8c`的实际保存pose，非新策略物理。查看窗口后，人类指出的地形问题经原始NPZ确认：4个保存tile均为7,140水平面/9,060斜面/0竖直面。横截面每0.1m升高25或30mm，原SDK heightfield采样间隔0.1m与踏面0.1m相同，且slope_threshold=.5没有将其转换为竖直面，实际形成坡面。旧53双轮更高表面/2稳定指标均保留为原始观测，纠正其技能解释为斜坡支持，不能称真实台阶通过。

目标SDK原始源码已用原传输有限读回，路径/字节/SHA见attempt08/reports/ACTUAL_TERRAIN_GENERATOR_SOURCE.json。修复采用其 `MeshInvertedPyramidStairsTerrainCfg` / `trimesh.mesh_terrains.inverted_pyramid_stairs_terrain`：显式box网格有水平踏面与竖直阶面，保留25–40mm阶高范围、0.1m踏面、1m平台、9m tile和1m子边框。此为明确的几何适配，不冒称保存heightfield配方的字节复现；新generator原点高度与量化方式也与旧heightfield不同，STARTUP/course将实际记录。奖励/PPO/增强MOD4v1物理/DR/目标限位/PD/DC/队列保持。

使用读回的目标SDK函数做CPU几何检查：difficulty0/.5/1分别25/32.5/40mm，每tile1,500面，500水平面/1,000竖直面/0斜面；旧函数同三个难度都产生斜坡。原奖励与命令、20k空间布局和singleton接触filter的3项回归通过。0生产PT读取、0SDK导入、0physics；原生新场地仍以本次FIRST及日志为准。

新attempt08只部署stairs/train两module及owner/entry/plan共5小文件、44 sharedSHA引用；未复制运行树/模型/资产。初始化为same20,000环境FULL_V4完整恢复，来源ffce final/37,849,545B/iteration31/620Adam；不重置输出STD或丢弃Adam。恢复组件/全局RNG/队列/计数器之后只做一次fresh physical reset，不恢复PhysX状态。原nominal由新constructor保护。train新增FULL_STATE_RESTORE回执只记录实际恢复结果，无奖励算法变化。

四卡于17:52实查：72 GPU0/GPU1各free24,203MiB、used13、util0、无compute，选GPU1 `GPU-c27eecbd-6838-7290-1cd2-37e34522213d`；210卡free23,890MiB但HOME磁盘0/RAM约43GB不满足；86卡used21,620MiB有compute。原canonicalNone、authority/finite/private锁实际通过，原余额239,555.85791754723，未增加预算/退款。17:52:47.910624实际启动owner1609081/create1793785967.67，唯一本地launcher60636/create2026-11-04T17:52:18.149113+08有限FIRST观察；当前是否FIRST/collector与actualGO/save/nominal以原reports实际回执为准。

三次网络前拒绝保留：另一聊天正式回传、短时本地MuJoCo pilot、另一聊天离线视频渲染被宽匹配拦住。没有kill其它进程或绕串行锁；对方实际结束后freshLOCAL准入启动。旧MuJoCo只显示NPZ，按确切PID/create/exe/argv/sourceSHA分类。所有旧once保留，原生产未重复启动。

本轮使用人类新授权的一小时，actualGO后3600s保存+300s安全退出，原owner完成后立即独立80与保存pose。FIRST必须480,000样本/24controls/20Adam非零actorcritic梯度/FULL_V4完整首存，恢复迭代31/Adam620核对且完整日志无实际cooking/pairs/patch/OOM错误后才绑定唯一postround。收尾时须审看所有新实际图和all80接触/targets/commands/height，再决定接续。

18:03实际更新：FIRST已成功返回，iteration32/本轮1PPO/24controls480,000samples/192physics/20新Adam，actorgrad.99999994/critic1.000000119，FULL_V4首存37,849,673B SHA `95622dde189483fcb3a844b228d2f482427d93c79bc97e011b88ab18550cf78f`。完整WORKER_COMPLETE.log没有实际error；仅有“大三角面建议细分”警告，无cooking失败/patch或pairs丢失/OOM。FULL_STATE_RESTORE确认原iteration31、17个optimizer状态、Adam均620、LR7.59375e-5，actor/critic/STD与组件/RNG/队列/计数器已恢复；新constructor nominal仍保护。STARTUP明确使用trimesh显式直角台阶。FIRST是实际训练执行证据，不是已学会技能。

actualGO为17:52:48.411679，SAVE18:52:48.411679、NOMINAL18:57:48.411679。唯一collector63276/create2026-11-04T18:02:35.938489+08已绑定，等待原save+45=18:53:33.411679正式回传；旧launcher60636已正常结束，原worker1609098/create1793785968.72由同owner负责。stderr空，无第二SSH/观察器或重复bind。
