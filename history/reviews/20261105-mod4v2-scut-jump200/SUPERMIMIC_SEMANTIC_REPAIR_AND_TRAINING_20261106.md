# SuperMimic语义修复与实际训练

2026-11-06，北京时间。人类最新明确“修复完就开始训啊”。已完成本聊天独立修复、CPU回归、真实Newton四环境迁移/恢复测试，并在真实空闲RTX4090启动20,000环境一小时。原final5936和所有失败保留；共享vendor、foreign和mod4v3未修改。

## 已实际运行

当前A=`N/supermimic_final5936_semantic_repair_1h`。来源为完整final5936，SHA `f671aaf7f7bc694b1264143e5a7f71cced25cf06d67432786b1fdc7a55b70d0d`。GPU私有EX实际准入，canonical读写0。

- GO：2026-11-06 14:21:45.610874；原保存截止15:21:45.610874；名义退出上限15:26:45.610874，包含初始化，不延长。
- 原owner18276/create1793946104.6，worker18286/create1793946104.92。唯一localcollector62016/parent63356/create2026-11-06T14:24:32.319686+08，负责SAVE+45正式回传；launch63356已退出，SSHclosed/SESSIONrestored/FREE有回执。
- 实际FIRST5968：从5936新增32完整轮，先64controls补新上下文，再32轮模型/价值校准，最后第1次新H32策略更新。新真实control samples2,880,000，不能把32轮都说成32次策略更新。
- 四Adam源pi5904/WM23744/aux23744/critic23616，首存pi5905/WM23872/aux23872/critic23744。新首存2,708,309,851B，SHA `f5b06cad575bec6659ff1b6588dfbc2e9d6e71aec7f2d780e9e5e64e289487e6`。
- H32跨时梯度.009668408、WM路径.004456302、参数梯度.122192159、参数变化.000014052；有限且确有更新。FIRST不是技能证明。
- FIRST实际本批真实轨迹critic目标均.758375585、value均.754892170、MAE.066412650，0个超宽松±80；想象即时折扣和.243020654、bootstrap.517260671。仅早期buffer内校准，不是heldout评测或长期稳定证明。
- 首批继承累计数值1232/约束1555→1243/1557，即本段新增11数值、2约束重置；solver32警告仍有，不能说数值全部健康。
- 首个有BPTT单轮总16,092.88 controlstep/s，采样86,305.87；含前32校准轮窗口18,194.90。H32闭环模型拟合增加成本，非旧k8同状态ABBA，不称整小时收益或十万总训练step/s。

以上为14:24首次正式回读快照，不冒当前瞬时或最终结果。完整机器回执为A/reports/SEMANTIC_REPAIR_FIRST5968.json、FIRST_VALIDATION.json和FIRST_ACTUAL_RETURNED.json。

## 明确修复与迁移

实现位于CODE/supermimic_semantics.py、supermimic_repaired.py；原supermimic_train/newton/evaluate只接入显式候选，未改共享固定vendor。

1. schema从139维改176维，固定外部命令及episode常量，统一actor/critic重复动作、轮位置占位和模式字段。命令不再从已预测命令复制回自身。
2. 补明确气弹簧压力2、阻尼2、COM3、motor_gain6、encoder_bias4、100Hz中点clean sensor16、相对台沿/横向位置/heading4。给WM和critic训练特权条件，actor仍35维部署接口。
3. 想象观测从预测physicalstate计算clean角速度/重力/关节位置速度，再按实际均匀噪声幅度、episode偏置与0/10ms延迟生成。10ms中点在真实physics tick4记录，训练为clean head；它仍为学习模型，并非Newton子步可微重建。真实采样不二次加噪。
4. 已知动作队列按原机械投影/动作尺度解析推进；每control8physics而lag最多2ticks，endpoint pending_valid为false。部分接触/任务状态等仍为learned动态量，不宣称全部上下文解析可知。
5. WM+aux改为同H32自回归联合拟合，监督state/context/reward/done；不再每步输入真实xi而只在actor处递推。真实奖励标签仍原复旦16项，没有增加或替换奖励。
6. critic训练目标改为真实replay状态、真实奖励和真实done的有限nstep/λ回报，真实bootstrap仍存在。新增PopArt统计完整保存恢复；输出层与Adam相应moments按坐标变化更新。actor读取value另受有限剩余时长的宽松奖励上界约束，不能把这个约束单独当修复证据。
7. 已确认旧critic失真，迁移仅对其末层及相关moments显式乘.001，保留其余模型、四Adam步数和状态；这是恢复处理，不能冒称原value/策略逐值等价。先32轮真实校准才新策略更新。
8. 允许靠近episode末尾的想象起点，精确timeout可到达，结束后bootstrap为0；不再用motionclip完整H32帧过滤跳过全部终点。
9. teacher先clip6再加.25残差后clip6，消除rawteacher>6.25时残差无法向内退的条件死区；旧检查点评测默认仍按旧policy_mode，新检查点明确保存新mode。源teacher自身未改。
10. 有限worker维护pending_iteration阶段/剩余collect与WM数/采样余数；部分optimizer轮检查点明确unsafe。保存异常与bridge/env关闭分别执行并保留错误，不能保存抛错后跳过清理。

迁移使用具体tensor插入映射及strict加载，不使用strict=false。新增输入权重与moments零初始化，旧完整学习状态先恢复；旧replay缺新增DR与中点真实值，不能补造，因此原件保留在source，先64freshcontrols填完整新ring再训练。新增checkpoint包含新契约、完整PopArt、warmup计数和迁移来源。

## 验证及失败

- N/supermimic_repair_cpu01/RESULT.json：合成H32命令/DR固定、重复槽一致、物理观测梯度、相对台沿可区分、finite终点、联合更新、四Adam及PopArt恢复、部分轮unsafe、save失败仍close、teacher饱和后能向内退通过。此项0生产PT/0physics。
- N/supermimic_repair_native01/RESULT.json：仅新随机PPO的4个真实Newton环境，旧139学习状态→176迁移，四Adam步数保留，完整新H32更新后保存、恢复再次H32通过，0数值/约束重置；不是生产策略独立80。末批真实value目标均-.401597、预测-.127484、MAE.329953，仍有误差，不称校准完美。
- 正式20k FIRST5968和新2.71GB首存通过，原full5936没有为审计重复decode；本次生产旧PT仅正式worker必要恢复一次。
- 首次本地启动失败：旧进程regex清单漏掉相对路径调用的本进程，exact own assertion拒绝于SSH前，0远端启动；CONTROL_ERROR_1793946026460954600.json与原日志保留。shared_control_access对清单缺自身时补精确自身CIM，ADMISSION02才真实连接启动，不重旧once。
- 读取时若干Windows路径/glob错误仅为本地读者；原工具记录保留。已有原抽象审计的false与否定假设继续保留。

## 收尾与边界

健康期间只本地核exact62016及children、stdout/stderr、CONTROL_ERROR、POSTROUND_FULL_RETURNED、FORMAL_TRANSFERS、COMPLETED；不第二SSH/probe/PTdecode或热改冻结包。原owner每300s原子完整保存，小时末完整保存/安全退出后立即独立80。reader失败且退出才有限恢复同一窗结果，不重launch或evalonce。

新final正式返回后使用N/review_supermimic_closed.py一次完整诊断，已补176schema/PopArt/warmup检查；核四Adam/模型teacher/replayinvalidstreamcut/7组件RNG/完整logs。复用returned完整logSHA，不另SSH读全文。然后原render_saved生成全部4张新early/late侧顶actualpose图并以当前模型原生视觉审阅，savedwxyz不再换序。80核真实起跳/整轮越沿/双轮台顶稳定、commands16terms/perbodydones与数值约束；若400Hz缺逐tickphysicalvalid则如实标并保守排除reset整episode。没有新final或80结果前不称已掌握技能。

真实Newton/HW300N60/原DR/400-100-50Hz/10mm闭链与.01radmimic/单200mm最终验收保持。累计100h本段前保守上界71,437.705711秒，含旧重启未知时长上界而非实际GPU成本；本段结束按owner真实elapsed追加。原3600save+300exit含初始化，不退款延窗。mod4-10原ACTIVE30分钟任务已更新，无新Goal/chat/重复automation。已有Newton唯一trial普通补充，不重record/retag，所有实际测试/失败及sourceSHA归EVIDENCE_INDEX。
