# 2026-11-04 原华南虎阶梯回放与空卡开训

11:13的四卡实测选择72 GPU0 `GPU-16828f91-2b45-b646-8dc0-9481138e2842`：free24,203MiB/used13MiB/util0、无计算进程。GPU1为used6,650MiB，210机器HOME可用磁盘0且RAM43GB，86机器used21,620MiB。原peerV25已于10:44:29.094021完整ownwait/settled/released；原canonicalNone、两authority锁与finite锁均可用。选择另一张卡没有绕共享锁或更改预算。

原58540等待器11:02在网络前拒绝：宽泛RMPOLAR匹配误把其它聊天的本地MuJoCo CPU回放进程48084/4760当成远端控制器。检查其完整源码/argv/creation/exe/SHA后，只对这两个确切本地viewer身份分类；不停止回放、不放宽锁。一轮路径分隔符匹配false保留，之后未执行准入恢复成功。首次原GPU1资源拒绝发生在读模型/构建scene前，0PT/0physics/0optimizer，原RELEASE/ERROR/FULL_RETURNED保留。切空闲GPU0仅新增owner与plan两文件，在同一诊断目录保留独立once与结果；共用源码不复制。

`scut_stairs_eval1/reports_gpu0/FULL_RETURNED.json`为实际80首局结果，actual400Hz 3,200callbacks：79局达到8秒cap、1局原接触终止，mean7.98725s，closure/mimic/nonfinite/rawreset全0。关节目标和CAD差值全部合规，实际电机位置/速度/扭矩均已回传；四腿平均target tracking MAE约.111/.080/.100/.084rad，不支持“关节完全不动”的假设。左右hip目标+.5命中91.925%/61.598%，仍是可量化后续问题。

新场地56局出现双轮更高表面接触，60局有至少一轮越中心后升阶，2局满足本项目的连续.5秒恢复指标。这不是华南虎原作者的毕业标准，也不是270mm首次飞行成功。4幅早晚侧顶图已由当前模型原生视觉审看，使用原保存wxyz与实际地形mesh；env0在中心附近，env1逐步移动出中心，40/41至2秒超出窄画面视野而非terminalclamp。具体升阶结果仍以all80实际接触及轨迹为证，不能因离开画框就说完成。

本次实际暴露场地边界适配漏项：部分机器人跑出整个mesh后继续下坠，observedheight到-10.836m、height square代价受到污染。固定SCUT V14源码env.py541–571与保存YAML本来就启用了rough boundary timeout，margin.5/use_inner_terrain_area=false。本次只在scut_stairs补回原公式：整个mesh加原border后，abs(x)>49.5或abs(y)>67.5视为timeout；与closure/mimic/非有限同现时原hardreset仍清timeout。奖励、PD、solver及其它终止门槛不改。保存配置的边界CPU检查通过；不拿CPU当原生技能或无边界诊断当修复后结果。

新训练`env20000_scut_stairs_1h_20261104`已在11:14启动原owner1586264/create1793762067.77，GO与2万scene初始化在原FIRST有限reader内返回。9个source/control文件和28个sharedSHA引用，来源仍37,849,545B SHA`0fdd9463205f739daff8713ade26d937846c832fba25392af4e515edc8904f86`，weights-only/freshAdam，无输出/STD重置。训练完成首个PPO与完整首存后才确认FIRST，并绑定唯一postround；最终全部学习状态保存、原owner安全退出与独立80评测保持。actualGO/FIRST/save时间以原回执和WORK_ORDER为准。

## 后续实际容量失败及同窗修复

原20k首步PhysX实际报`foundLostAggregatePairsCapacity`至少269,692,772，否则会漏交互。虽然PPO已执行并保存首存，不能将该训练称为有效。给exact owner写入既有`STOP_AFTER_SAVE.json`后，原owner完整保存退出、计费结清、原生独立80评测并释放锁；没有signal/kill或修改canonical。关闭final为37,849,545B SHA`16eceb16104be358d35ab63c4c6396e9b922e3dbfed3a04dac313376d4d06b11`，3PPO/576physics/1.44M实际样本/60Adam；它与首存8a75都保留为失败来源，不用于修复后初始化。独立80、全部新4图也已审完，评测本身不能消除20k训练的容量错误。原生发生缓存不足的唯一深层原因尚未证明，早先把它直接称为出生重叠问题属于工作假设。

源码只对scut_stairs/20000设置`cfg.sim.physics.gpu_found_lost_aggregate_pairs_capacity=280000000`，超过实际所需值；此字段为GPU碰撞对存储，不是dt/solver/contact规则。其它容量无实际报错不预先追加。关闭完成后在同阶段`attempt02`新增sdk+owner/entry/plan四个小文件，其余共用SHA引用；按原有效0fdd权重重新微调。原绝对SAVE12:14:28.462118、NOMINAL12:19:28.462118不延长、不退款，剩余窗口含native初始化。11:32:58实际启动新owner1589912/create1793763178.46，唯一本地launcher50100/create2026-11-04T11:32:52.550226+08负责有限FIRST观察；实际FIRST及容量错误是否消失以新回执为准。

写早停时另一新本地NPZ/MuJoCo回放49288/25156被宽泛RMPOLAR匹配误拦的false也保留。检查完整源码确认其只读已有NPZ并本地显示，无网络、权重解码或canonical操作；只按确切PID/creation/pythonw/argv/scriptSHA分类，未停止或修改其它聊天。

## 容量扩大实际OOM与布局修复

attempt02在首次PPO更新前OOM：只剩63.06MiB，ELU还需118MiB，当前进程共占23.56GiB，随后PhysX状态损坏并报CUDAcode2。没有FIRST、没有有效FINAL，不将worker返回码0或owner errornull当成功。原owner1589912已ownwait/settled/released，production/ERROR与TRAIN_CLOSED.passed_execution=false完整保留，0有效PPO。

将280M缓冲回退后，attempt03保留10行原difficulty、将相同inverse-mid地形从14列复制为140列，约将每个origin同址actor密度降至原1/10。每级阶高、踏面、中央平台、边框、原generatororigin与奖励/PPO不变，未添加其它rough任务。相比原保存14列这是明确的空间布局适配，不称原字节复现；mesh总体y边界随列数扩展为634.5m，x仍49.5m。新增针对性CPU检查验证列数/边界及几何配置保持，0生产PT/physics。

11:46:30启动attempt03 exactowner1591175/create1793763990.63，solelocal29304/create2026-11-04T11:46:24.443816+08有限FIRST。仍用原有效0fdd权重，不用两次失败的部分权重，仍20,000环境，原SAVE12:14:28.462118/NOMINAL12:19:28.462118，不开新小时或退款。原生是否消除pair/OOM须看本次真实日志与更新，不以CPU检查作成功。

本阶段沿用既有annotated trial，全部false/reader错误与结果只追加普通Git提交；新训练不增加或复制canonical、不退款、不覆盖既有模型与冻结once。

## 12:12实际覆盖：碰撞网格失败与attempt05

attempt03的140列单一碰撞mesh约22.68M三角面，原生PhysX cooking失败，地形碰撞体未创建。因此即使FIRST和3次PPO存在，也不是有效训练。已通过原exact owner STOP_AFTER_SAVE完整保存、独立80并释放锁；final SHA7eaaddc6a21489fa07f9e7e25e24335574ff2a7433c8142e38fc980d1a82753c仅作失败证据，不续权重。新4幅早晚实际pose图已原生审看，80评测3恢复指标不能证明140列训练碰撞正常。

attempt04将相同mesh拆为10个物理碰撞条带，完整无碰撞raymesh保持扫描几何；接触读者支持多filter求和。原生在Vt.IntArray(np.ndarray)构造处拒绝numpy.int32，发生于模型与physics前，0FIRST/0有效PPO。完整ERROR/ownwait/settled/released保留。

attempt05仅将facecounts/indices改用Vt.IntArray.FromNumpy。12:07:14启动owner1593421/create1793765234.53，solelocal59228/create12:07:08.466793，session77440；12:11已建20,000环境scene，正在原生初始化，FIRST尚未出现。原始绝对SAVE12:14:28.462118/NOMINAL12:19:28.462118保持；不是新小时，若初始化耗尽原窗必须如实记录零更新。源仍有效0fdd，不采用此前失败权重。源码/物理/奖励边界保持。

## 12:24关闭结果与接触接口修复

attempt05在12:18:41.869608原owner ownwait/settled/released，actualPPO=0、无FIRST/FINAL/独立评测。模型初始化前，contactview创建失败：单个terrain_collision_*通配符匹配10个全局形状，既不是每sensor一个也不是可广播单形状，expected20000/found10。worker返回0被SDK关闭流程吞掉，TRAIN_CLOSED.passed_execution=false与production/ERROR为真实失败，不当成功。

已将10个碰撞条带改为10个显式单形状filter路径。针对原错误的1项CPU检查通过，0生产PT/physics；12:23使用原传输只读目标SDK api.py文档，确认single-prim exception可以对所有sensor广播，source SHA以CLOSED05_EXACT_SOURCE_READ报告为准。该读者首次inline argv没任务路径而被本地gate拒绝，换命名脚本后成功，原false保留；未绕gate。

原SAVE12:14:28.462118/NOMINAL12:19:28.462118均已结束，不自动延长或退款。NEXT_FILTER_FIX_PREPARED.json记录当前三文件SHA和正确源码方案；没有新生产namespace或启动。已向人类提出使用原canonical余额重新开20k一小时窗的问题，等待明确答案。当前没有live controller，不得以旧59228/50100/29304文字再等待或重放once。

## 15:23人类批准重新一小时与原锁等待

人类已明确回答“允许重新训练一小时”。attempt06引用原有效0fdd来源，20,000环境/3600s保存+300s安全退出，原canonical余额扣账；不是延长旧12:14窗口、退款或增加canonical。2个改动module（stairs/sdk）+owner/entry/plan共5个小文件，共用源码/资产按SHA引用；原失败与once保留。

15:20四卡实际：72 GPU1 c27e空闲free24,203MiB/used13MiB/util0无compute；GPU0由standingV28 exactowner1600690/create1793775370.32占用，used5,862MiB。210卡空但HOME磁盘free0且RAM43.29GB；86used21,620MiB。V28还持有原canonical及两authority/finite锁，不能因另一GPU空闲绕锁。原GO固定save15:56:11.035646、nominal16:01:11.035646，非过去V25。

唯一本地timer24412/create2026-11-04T15:22:46.230442+08已绑定，stderr/stdout空，RESOURCE_TIMER_BIND/ONCE均消费。等16:02:11.035646后freshLOCAL，再有限核exactV28 ownwait/settled/released、canonicalNone与锁，并实测选定GPU1容量；可用才冻结INDEX并调用原launch。原owner从实际准入GO计算新3600s，不占用等待时间。FIRST非零actorcriticgrad/480,000样本/FULLV4首存且无实际原生错误后自动bind唯一postround（带--root），完整保存退出后独立80与实际pose审看。当前只是等待资源，尚无GO或有效PPO。

## 16:10实际自动启动

不是继续等待：原peerV28已于15:58:39.303106完整ownwait/settled/released；16:02:19 fresh原canonicalNone、两authority/finite/privateGPU锁全部可用，GPU1 free24,203MiB/used13MiB/util0无compute，RAM532GB/disk262GB。原timer按计划冻结5个小source/control及共享SHA引用，于16:02:25启动owner1603578/create1793779345.12。16:09有限FIRST快照已有actualGO/worker，20,000场景在初始化；FIRST仍未返回，不能把launch或物理参数表当有效PPO。

本地唯一24412仍为原FIRST读者，stderr空；它将根据FIRST非零梯度/480,000样本/FULLV4首存且无实际错误自动bind唯一postround，后者按原actualGO截止回收完整final/独立80。没有第二SSH、资源探针、启动或timer，尚未从FIRST取得的绝对save时间不根据launch推算。

## 16:14 FIRST返回与新的patch stream实际溢出

attempt06已走过先前接触filter错误，实际FIRST1PPO/480,000样本/20Adam/非零actorcritic梯度/FULLV4首存c66ec8413f3e6a4ec0d0b062dd0a72e1fbd11fd343ca46f7a14177b46e0c14d8。但firstrollout实报Patch buffer overflow（FIRST所见最低需求峰值267,958），该训练不能算有效。原timer识别真实错误后未bind正常postround并退出；原exactowner于16:13:26收到STOP_AFTER_SAVE，完成保存退出再独立80，无signal/kill/canonicalwrite。唯一本地collector28756/session20365正式收回关闭与评测，alive只本地。

源码只对scut_stairs/20k将cfg.sim.physics.gpu_max_rigid_patch_count设为524,288，原pair容量、dt/solver/DR/reward/PPO保持；这次是实测patch stream溢出，不是先前aggregatepair280M扩容。未热改运行中冻结包，修复仍待下一smallsource原生。实际本轮GO16:02:25.845096、原SAVE17:02:25.845096/NOMINAL17:07:25.845096，同窗修复不新增/退款/再开一小时。先完整正式传回、原生4图审看后再接续。

## 16:21 同窗attempt07实际启动

attempt06完整final49e8abf1bf605537854f65f9ed4e4d447ffafefe4f696ad87e90615b3ec381f8/3PPO/1.44M样本/60Adam已传回，原owner1603578于16:17:11.986861 ownwait/settled/released，独立80的actual400Hz/poses和完整学习状态原件传回SHA核验。80为1接触终止/2边界timeout/77cap，mean7.94725s，0closure/mimic/nonfinite/rawoutlier，52双轮升阶/62任一升阶/2项目恢复指标。4幅早晚actualpose图已当前模型原生审：env0近中央，env1缓慢驶离，40/41出窄画面，41终态6.46s。评测指标不消除训练patch溢出，49e8和首存c66只作失败来源，不用于初始化。

attempt07仅sdk改动+owner/entry/plan共4文件，直接引用既有source，设置20k阶梯patchstream524288，未改变aggregatepair缓冲。两项针对性contact回归通过，0生产PT/physics。原owner1605308/create1793780417.59于16:20:17实际启动，唯一本地launcher24732/create16:20:11.490949（toolsession78449）有限FIRST观察。source始终有效0fdd weights-only/freshAdam，无轴/STD再重置。原绝对SAVE17:02:25.845096/NOMINAL17:07:25.845096保持，未新开一小时或退款。当前初始化，尚不能称修复原生通过。

16:28读者恢复：原launcher24732在16:24:55因SSH10054远端重置退出，原LAUNCH02_SSH_FREE已恢复FREE，未重复生产启动。首个读者恢复被新本地LQR/MuJoCo viewer3608/create16:21:45.322513误分类为remotecontroller而在网络前拒绝，原false保留。读其源码与直接依赖确认是本地交互物理/控制，无远端计账；只对确切PID/creation/exe/quotedargv/scriptSHA246fdac4…分类，不kill或修改其它聊天。当前唯一本地恢复reader53412/create16:28:02.182485（session81776）继续原owner1605308有限FIRST观察，0remote启动/0PT/0新physics/0canonicalwrite；真实FIRST过后核完整日志再bind一次原postround。

## 16:31有效FIRST与原收尾绑定

attempt07 FIRST已于16:30:08.857714返回：1PPO/24controls/480,000 onpolicy样本/192physics/20Adam，actor/critic norm均1.000000119，FULLV4首存37,849,545B SHA3a475d2b0909e6e07decceb77063c0fcff5c4a1008bb69ad9584a5e5bc5acfd0。对原exactowner有限读取完整WORKER.log，actual errorlines=0，无patchoverflow/原cookingfailure/droppedpairs/OOM/productionERROR，才将该FIRST标有效；仍不是最终技能。前次full-log读者与本聊天archive_stage短暂冲突，在网络前正确拒绝，原false保存后只恢复未消费读者。

同原owner1605308继续运行；恢复reader已结束，唯一postroundcollector59804/create2026-11-04T16:31:10.931640+08已正确带--root attempt07绑定，POSTROUND_BIND/ONCE消费，stderr空。等待原SAVE+45=17:03:10.845096正式传回；原SAVE17:02:25.845096/NOMINAL17:07:25.845096保持，不延长窗口。原owner完整保存后安全退出并立即独立80，之后回传实际pose图原生审看及all80接触/动作/命令评审。健康时不第二SSH、资源probe、权重解码或重复验模。
