# MOD4v1 单个200mm直角台阶跳跃待办

2026-11-04人类最新：“我说的是跳台阶，机器人跳上去200mm的台阶不是这个碎台阶”“你设置todolist去做”。本清单覆盖此前inverse-mid小阶梯和“允许轮子保持接触”的任务选择。历史270mm、斜坡、小阶梯原始试验与false保留，不当作200mm跳跃完成。

- [x] 固定目标：从低地自主起跳，越过单个200mm竖直台沿，双主轮落在真实水平台顶并稳定恢复；爬坡、小阶梯、顶着台沿爬不计跳跃。
- [x] 核对固定华南虎源码的高台阶场地、起跳与落地控制；区分保存模型配方与源码可选分支。
- [x] 完成小阶梯attempt08最终运动评审；完整结果与原false随本阶段Git补充提交。
- [x] 新增独立jump200任务：200mm单台阶、接近/起跳/落台后的命令与奖励、400Hz真实离地/越沿/台顶支持评测，旧冻结包不改。
- [x] 完成针对200mm真实几何、起跳与爬台反例、落台稳定的必要CPU检查（8项通过，原false保留）。
- [x] 在原资源/预算/保存边界内做有限实际模型评测；立即原生审图与回放，按结果决定定向修复或训练（80局基线已回传并审完4图，0起跳越沿/0触台/0成功）。
- [x] 四卡/原canonical/authority/finite实际准入通过；22:11选择72GPU1启动原授权窗，首attempt恢复失败已关闭，attempt02在同一原绝对窗口内修复接续。
- [x] attempt02真实FIRST通过：iteration81、480,000样本、20新Adam、非零actor/critic梯度、FULL_V4首存；完整日志0实际错误。完整恢复source80/17Adam状态条目/step1600，并绑定唯一postround61924。
- [x] 原训练完整保存退出后立即独立80局评测与实际回放已完成：70新PPO/final150，80局均7.98s timeout，0地面向上起跳/越沿/落台/成功；全部4幅actualpose已审。
- [x] 截至200mm基线与授权自动接续的全部试错、失败、源码、回放与决定纳入本阶段Git补充；CURRENT_STATE/WORK_ORDER/现有mod4-10已更新。
- [x] 根据实际停滞定向修奖励：接近阶段五项正奖励按实际前进门控、push增加原源码向上速度奖励；12项jump200及8项旧阶梯CPU回归通过，候选5小文件/55sharedrefs已准备。
- [x] 最终80/全部回放/读者false/奖励修复与新候选纳入本次普通Git补充；实际提交与远端核验以工具输出为准。
- [x] 人类2026-11-05明确“允许100小时”：后续按每小时完整保存/独立80/实际回放与定向修复接续，累计不超过100小时且受原canonical实际余额/reserve约束，不再逐小时询问。
- [x] 接近/上推修复版原生FIRST151通过：24controls、480,000样本、20新Adam、完整FULL_V4首存；完整恢复source150/17项Adam/step3000，完整首轮日志0实际错误。
- [x] 接近/上推segment已完整保存退出、独立80和4图原生审看：113新PPO/54.24M样本/final263/Adam5260，完整日志0实际错误；80/80各请求一次，0起跳越沿/落台。
- [x] 修复实际单次请求缺口与起跳静止正奖励：持续真实200mm扫描允许冷却后重试、active tracking按向上速度门控；15项jump200＋8项旧阶梯CPU检查通过。
- [x] 原peerE3W8已提前02:09:09退出释放，fresh四卡/原锁/余额通过，空闲GPU1新owner1628379实际启动；仅sole4416观察FIRST，100h持续授权。
- [x] 重试/上升修复版真实FIRST264与完整首存通过：480,000样本/20新Adam/actorcritic梯度1.0，完整恢复source263/17Adam5260，完整首轮日志0实际错误。
- [x] retry-ascent原窗完整关闭/正式回传/fullfinal376/17Adam7520；独立80、全部4新图已审：69requestenvs/300requests，0flight/wholeclear/top/landing，原70820退出。

- [x] 针对两hip持续上限增加不可执行leg请求投影奖励惩罚，保留原scale/offset/动作/限位/CAD/D4；19jump200＋8旧阶梯CPU通过，4module/59refs候选已准备。
- [x] 唯一16444/create04:40:09.633017本地接续已绑定；100h授权下等待真SSH39496，不第二SSH/重bind。
- [x] 原16444已补齐final376完整日志并核0实际errors/ownerrelease、原SCUT32释放；四卡准入被新真SSH17256在网络前拒绝，原false保留，0新GO。
- [x] 只恢复未消费准入：唯一72460/create05:31:34.958986已绑定，等待真实17256退出及当前E3W11 exactrelease，原source/PLAN/所有once保持。
- [x] sole72460核实际E3W11提前释放/outerreaped、fresh四卡/原余额后唯一新GO05:36:14.384236；FIRST377/完整恢复source37617Adam7520/FULL_V4/完整首轮0errors已通过，唯一collector69168绑定。
- [x] 原target-projection权重-2版完整保存退出/独立80/4图审看/fullmodel诊断1次/全文errors0：112PPO53.76M/final48817Adam9760，79局362请求但0flight/wholeclear/top/landing。旧69168退出，reader网络前false保留。
- [x] 仅将projection惩罚权重-2→-10；19CPU通过、旧stairs8复用，旧轨迹counterfactual核算不当新motion；1module63refs候选与唯一67764已绑定，先补齐全文再等actualSCUT33释放。
- [ ] sole67764核SCUT33exactownerdead/ownwaitsettledreleased/canonicalNone/原锁与fresh四卡/余额后唯一新launch/FIRST489/fullrestore48817Adam9760，保存退出立即独立80和新actualpose审看；当前新GO未发生。

当前证据：固定SCUT commit `1a26356d6f591734d4f6f666f5cead1a6925da67` 的terrains.py有STAIR_FOR_RM 200–220mm/1.5m踏面，以及HIGH_STAIR_FOR_RM 150–350mm/1.25m踏面。当前误选inverse-mid为25–40mm/0.1m踏面。公开rough_rotation_stair保存YAML关闭Airborne/JumpTakeoff/Stair，不能把小阶梯保存配方称作200mm起跳配方；须进一步核对应源码分支。

当前attempt08已完整关闭：49新PPO、23.52M样本、980新Adam、final iteration80/FULL_V4，SHA `f6b6b649b78752a89c0688850ae89e93afd0a87fe21eb6b6705f9b02ecf81da4`。独立80小阶梯43双轮升阶/56单轮升阶/0连续.5s稳定，5导轮持续接触终止；全部4张新实际图已当前模型查看。此为小阶梯试验，不是200mm技能。

19:39实际覆盖：独立`jump200_step_eval1_20261104`已完整关闭回传/审图，remote owner1613410/create1793792185.63已ownwait/released。真实200mm单台阶mesh只有0和.2m高度，80局全部触发起跳请求但0实际向上起跳/0越沿/0触台。78接触终止、2原8秒timeout，平均2.65875s，无closure/mimic/数值异常。来源小阶梯策略未学会跳跃，不能继续用小阶梯结果冒称成功。人类已明确“批准200mm跳台阶训练一小时”，本轮20,000环境/3600save+300exit使用同一原canonical余额；原attempt08窗口不延长。已有有限评测once全部消费，禁止重跑。

19:59接续：修正版已获批准，PLAN及7module+3control准备完成，尚无INDEX/LAUNCH_ONCE/生产GO。首轮准入在网络前遇standingV30实际controller而拒绝，原false保留。V30真实GO19:51:35、SAVE20:51:35、NOMINAL20:56:35；唯一localtimer将在20:57:35后freshLOCAL核exactowner1614229/create1793793094.65已ownwait/settled/released、canonicalNone/原锁，并刷新四张4090后自动launch。等待不计入新小时，不再询问相同授权。

20:01实际：唯一localtimer67488/create2026-11-04T20:01:12.771869+08已绑定且stderr为空，RESOURCE_TIMER_BIND_ONCE/RESOURCE_TIMER_ONCE均消费。首次bind被另一聊天E3正式回传21548在网络前拒绝，原false保留；仅把本地等待的bind改为允许记录外部controller，所有网络前freshLOCAL原gate不变。不得再bind/timer/探卡或重复launch；等待程序自己负责原锁释放后的有限准入与FIRST→唯一postround。

20:38最新覆盖：人类指出端口转发单4090可以用Windows盘，实际独立210只读核GPU空闲23890MiB、Windows NTFS挂载`/mnt/mod4_expanded_original_EF3105C85DD986BD_20261026`可写剩694,983,204,864B（约695GB），第二别名是同一块盘，不重复加容量。HOME0不能再称无可用数据盘；当前MemAvailable43,310,092,288B仍低于既有20k的64GiB准入。旧67488在网络/生产前按exactCIM停止，其once全保留。新唯一35308/create20:36:24.331634运行`jump200_forwarded_windows.py resume`，先等另一聊天72只读observer52216结束，再fresh四卡/Windows盘/原exactV30释放及原canonical锁；取消额外固定20:57等待，原生产launch仍未消费，新授权小时仍未开始。首Windowsfourread被52216网络前拒绝false保留；210单独host只读已完成并SSHclosed/SESSIONrestoredFREE，没有碰72现有连接。

21:11实际覆盖：35308在20:52完成四卡读回后，进入原releaseSSH前因新CPU/MuJoCo播放器51820/create20:52:04.522469被broadgate误判而退出，原错误/false完整保留，0INDEX/0LAUNCH/0GO/0PPO。已读player/runtime并按exactPID/parent/creation/exe/argv/sourceSHA仅排除该CPU播放器，真实66124远程collector仍被gate拦住，不kill/宽泛忽略。另聊天E3W5已20:54:24取得原canonical，owner1616384、worker1616433/create1793796864.67，SAVE21:54:24/NOMINAL21:59:24；这是新actualowner，不能再称V30当前占锁。唯一恢复63556/create见PENDING_ADMISSION_RECOVERY_EXACT_CIM，只恢复未执行准入；等其原localcollector退出，核exactE3W5ownwaitsettledrelease与outerreaped/canonicalNone/原锁后同一原launch。不重baseline或任何生产once，新人类一小时尚未开始。

22:12实际覆盖：63556仍在本地等待，新54056/create21:28:37.339365的savedpose播放器被误列控制器导致已释放后仍等待；已读完整play.py确认只mj_forward回放，按exactPID/parent/exe/creation/argv/SHA7620b17b…仅分类此播放器。63556在任何网络和生产前exact停止、旧once保留，恢复未消费finish_pending。原finite22:11核E3W5exit/outerreaped真实释放、canonicalNone和原两authority/finite锁全free；原fresh四卡72两4090均24203MiB/empty，RAM532GB/disk252GB；选GPU1。INDEX10smallfiles/46sharedrefs与LAUNCH/FIRSTonce已消费，owner1619104/create1793801493.89 launch，唯一68796/create22:10:55.334107原FIRST读者/toolsession35418。FIRSTpending，不能称有效PPO或技能；不第二SSH、launch或hotpatch。

22:23实际覆盖：原200mm窗口GO22:11:34.580026，SAVE23:11:34.580026/NOMINAL23:16:34.580026。首attempt在完整actorcritic/Adam恢复后命令字段_mode_enabled形状与新任务不兼容，0FIRST/0PPO/无FINAL/无独立80，原owner1619104已22:18:40.004524 ownwaitsettledreleased，worker1619120结束；rc0/errornull不是成功。已定向修复仅显式scut_stairs→jump200时_mode_enabled使用新constructor禁specialmode向量，其它命令形状仍strict，学习/AdamLR/RNG/队列及freshreset保持；9CPU检查通过。attempt02仅checkpoint/train两module+owner/entry/plan共5smallfiles/53sharedrefs，新原owner1619885/create1793802140.07于22:22启动，唯一local73240/create22:21:59.398676/toolsession31861观察FIRST。只用本小时剩余，不延期退款/新一小时；同原f6b6来源，不采用失败权重。

22:32最新覆盖：attempt02已返回有效FIRST，iteration80→81，1新PPO/24controls/480,000样本/192physics/20新Adam，actor梯度1.0、critic1.000000119。完整首存40,556,699B，SHA `96b9ff560d0e158ca9495e0907cf1eec254adc1c8b76d1b3bb0be8125612a531`。FULL_STATE_RESTORE确认source80/17optimizerentries/Adam1600/LR0.000170859375，_mode_enabled从原3项显式保留新任务单false配置，其它兼容状态恢复及一次freshreset。完整首轮日志0实际错误。73240/session31861已结束；唯一collector61924/create22:29:46.362550运行`repaired_training_control.py collect --root attempt02`，stderr空。原SAVE23:11:34.580026/NOMINAL23:16:34.580026不延长，SAVE+45=23:12:19.580026正式回传。FIRST是有效训练证据，最终跳跃技能仍待独立80与actualpose审看。

23:15实际覆盖：原SAVE已到，唯一61924仍健康、stdout/stderr均0，尚未消费POSTROUND_FINITE_READ_ONCE。它在网络前等待另一聊天真实SSH/SFTP元数据collector36120/create23:11:52.584390（parent62684）；该读者不是本地GUI，不能忽略或停止。另一聊天本地FIRST显示E3W6实际GO23:13:09.621059、SAVE2026-11-05 00:13:09.621059、NOMINAL00:18:09.621059，但不能据此推断本聊天最终保存、退出或评测成功。本聊天原23:11:34保存/23:16:34退出边界保持，尚未取得FINAL或80局回执；不新开训练、不重bind、不第二SSH。原sole61924会在对方读者真实退出后继续有限正式回传，再立即审图和all80分析。
