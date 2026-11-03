# 增强MOD4v1实际SCUT训练与人类20000环境一小时切换

起始Git为`8654c630b403d717cc1cae707a7b7150946f9d9f`，SCUT源固定`1a26356d6f591734d4f6f666f5cead1a6925da67`。本阶段完成定制SDK实际启动、80环境短训/完整保存/独立80评测与原生审图，并按人类最新“20000环境一个小时来搞”实际启动20,000环境。模型/课程/接口适配不等于270mm技能已通过。

## 当前实际运行

- run：`MOD4V1_SCUT_STEP270_20000ENV_1H_1793711274668684600_env20000_1h`。
- 20,000真实环境；actor35/critic78；24controls首轮产生480,000条实际样本，PPO5epochs/4minibatches，20次Adam step。首轮actor梯度最大1.000000119/critic1.0；为clip后的梯度，并非未裁剪范数。
- 由旧完整iteration26接续至27；首完整checkpoint41,482,957B，SHA`1e44db9ebc7f3b86804e0a094713571d489abccb66564195cf41f74c2bad423e`。主卡为GPU-c27eecbd-6838-7290-1cd2-37e34522213d，actual资源准入无compute apps、24,203MiB free，沿用唯一canonical/原严格reserve。
- GO 2026-11-03 21:33:08.141129+08；原保存边界22:33:08.141129+08；安全退出上界22:38:08.141129+08。初始化约8分钟已计入原一小时账窗，不另增预算。首轮collection56.694s/update约.324s。
- 原owner1545304/create1793712787.43；worker1545321/create1793712788.48，后exec完整exe/argv/root见FIRST实际回执。local唯一receiver58792/create2026-11-03T21:43:08.364031+08，`postround.py collect`；健康等待期间不另开SSH。此receiver在原save+45后有限接收同owner自动评测结果，不控制或重放训练/评测。
- 当前状态是FIRST完整存储，最终270mm结果待本轮关闭后独立评测；不以loss/存活/状态事件作成功。

## 明确修改和沿用

奖励沿用8654的jump270配置与固定SCUT原AST：基础项、状态机、命令尾部时序、V13同步、V14导轮覆盖和critic字段次序保留。训练用普通RSL5 PPO而非旧H1 residual/WM。

人类只要求跳台阶出生/相对位置对齐。选择原反向阶梯`inv_stair_slope_for_rm_mid`的1m中心分支，中央低地1m见方、四边距中心.5m、外侧高台.27m；root(0,0,.38)，roll/pitch±.15、yaw±3.14、xy无偏移、初速0。MOD4约束可行关节姿态来自原库，库之后恢复root高度；不复制SCUT机器人关节姿态。原始多地形/多级台阶课程不启用，这不是整个rough训练的复现。

SCUT公开保存配置从flat `2026-07-19_09-14-50/model_8000.pt`以weights-only finetune开始，而非随机网络。最初80环境采用成熟增强MOD4 E0权重，actor严格加载35；critic38按字段含义和尺度映射到78，观测高度和特权新列首层系数为0，Adam/iteration新建。E0静态mode和SCUT aux语义差异明示，不称所有35维模式输入全等价。

人类改为20,000环境后，保留实际80环境final的actor/critic/STD/Adam/LR/iteration/globalRNG；80行物理DR状态和队列不能直接装进20,000行，因此新建物理population/DR/queue。旧完整文件保留；这是完整学习状态继续与新物理环境，不称逐env随机流或PhysX续态。

增强资产USD SHA`2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3`、contract SHA`bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755`。首次task导入前绑定。31body/30DOF/6action按名，.0025TGS32/4、400N/k2000/damping3、policy50/feedback100/physics400、fullD0white_v3/D1–D7、原PD/DC/queue、单envclosure.01m/mimic.01rad继续。未改关节限制或求解器来适应规模。

## 实际失败及修复

1. attempt01在USD mesh写点失败：NumPy scalar混入points，SDK要求GfVec3f数组。显式`Vt.Vec3fArray`转换。原失败关闭/结清，未读生产PT。
2. attempt02前扫访问旧RayCaster工厂字典失败。实际后端源码确认cache为`(path,device)`，改由实际sensor实例获取。原失败保留，未读生产PT。
3. attempt03第一次reset缺原E0资产差异声明。共享兼容验证器从jobroot读`MOD4V1_ASSET_DIFF.json`，改为引用共享原件的symlink。原失败保留。另核原consistent_reset会改root高度，适配层在原可行joint库后恢复指定.38m。
4. attempt04原生80环境成功FIRST。人类改规模后写完整保存请求，原owner自行等待更新完成、fullsave、退出并结清，没有kill/hotpatch或清canonical。
5. 第一次独立80评测在inference作用域外原地更新状态tensor失败；用单独新评测source修复整个env生命周期作用域，原失败不覆盖。修复后评测完整，0optimizer。
6. 合成检查首次读取未缓存STD属性错误，修复为严格参数state比较。所有错误报告保留。一次本地输出来自继承函数默认root未更新而拒绝已有报告名，未改旧报告；重绑put后，standing V17 CPU controller曾触发本地busy拒绝，无网络/GO；释放后正常启动。

只保存必要source overlay和固定来源文本，共享runtime/资产/模型按路径SHA引用。新attempt是实际原生失败的新试错配置，不重消费旧once，不整树复制。

## 80环境短训的独立评测与审图

80环境26PPO后完整final1,639,262B，SHA`d5dddb7a638fbc7de0152f8d383d818f4c5e794ada1829b9bdb89ab429e1a205`。owner1544176实际ownwaited/settled/released。独立80firstepisodes/seed9137/newDR/400Hz：0strict、0wholeclear、0leading、0top；全80于10–22controls结束，均值11.8625controls。短训11,658次训练episode事件不当独立评测成功数。

增强contract的真实collision box/轮圆柱按已存31body姿态重建，省略视觉mesh；0NN/0新物理。当前模型原生view_image审查侧/顶两张24格图，env0/1/40/41在中心起步后快速下降/收拢，未达沿。各自终态为.20/.28/.30/.24s，图中后几格明确END并clamp，不作后期存活。不能仅凭投影图断定所有body接触类型。NPZ/图片原件保留scope，Git仅索引与文字结论。

## 验证与后续

本阶段合成检查：STARTUP_CPU_ATTEMPT2三项、SPAWN_PARITY_REGRESSION16项、RESIZED20000_CPU_ATTEMPT1四项（含真实Adam moments跨population保留）、NATIVE_STARTUP_FULL_CPU_REGRESSION12项（含原状态机、RSL合成rollout/GAE/save/load及选env根高度恢复）通过。CPU不替代native；本次native FIRST另有实际回执。

20,000本轮完整保存安全退出后，同一owner自动独立80评测、保存400Hz数据和selected实际poses；唯一localreceiver正式传回。当前模型须再view_image并核all80，按真实结果决定。严格首次飞行整轮rear footprint越沿、双轮实际台顶支持、无地面/沿返回、速度<=.03、rollpitch<=10deg/yaw相对初始<=.2连续.5s。当前恒速.6奖励没有停稳阶段，近沿高度参考可能冲突，任务设计问题如实保留，不热改健康训练。

Git以本新native-training阶段唯一record；既有适配trial不重tag/record。后续实际结果用普通supplement。CURRENT_STATE和WORK_ORDER给出当前root/精确receiver/sourceindex，所有原false/raw/失败保留，旧H1不再写live或待评。
