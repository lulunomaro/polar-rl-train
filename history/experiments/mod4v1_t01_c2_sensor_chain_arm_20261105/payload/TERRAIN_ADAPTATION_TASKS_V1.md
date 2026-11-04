# MOD4v1 传统控制：36 项顺序适配任务表

更新：2026-11-05。直接指令：按照完整适配清单列任务表，一个一个解决。

## 恢复入口：上下文压缩/重连/自动续轮后先读这里

**本文件是36项执行状态的唯一真源，不凭聊天记忆重启任务。** 先读本节、当前任务行和末尾历史复用台账；只在缺必要细节时读取对应协议/小结果，不重新扫描旧raw。

| 恢复字段 | 当前值 |
|---|---|
| 唯一当前任务 | **T01：真实CAD定点/低速平衡** |
| 本表新场图完整工程筛选已通过 | 暂无；这不是此前成果归零，旧能力见历史复用台账 |
| 当前复用控制器 | 基线/C1/C2冻结。已接实际试玩：[runtime c2_fps](<RM_FPS_PLAYER_V1/runtime.py>)复用C1腿调平＋[现有FPS航向环](<RM_FPS_PLAYER_V1/player.py>)，避免再套C2内部航向环造成双环。可切回coord_soft对照；Engine默认coord_soft，旧formal适配器行为保留。公共K、KF/DR/PD/DC和门槛不改；新UI接线不等于全域C2验证 |
| 当前机制候选计数 | **3/3已实测；C3轴向D未改善支持，不采用。保留C2：所有非接触gate通过，仅支持仍失败**。[420131结果](<RM_ROBUSTNESS_V1/heading_follow_v2/runs/t01_c2_nominal_slow_420131_001/result.json>)：roll峰.0280186rad=1.61°/RMS.0131449，pitch峰.0187347/RMS.00795324；速度RMSE.0412814，行程1.62363m，横偏.0468113m，停车RMS.00554225m/s。支持89.855/95.515%、wholeunsupported165点未过；guide/hard0。其余5例暂停。C3已实测未采用 |
| 已消费新自动case | t01_latest_cad_stand_nominal_420101_pilot001，已完成并收集，禁止重启 |
| 已收集原job | pwsh-c75e8938e8d14f1b，exit0，800控制/16000物理步 |
| 新自动case证据 | [pilot结果](<RM_ROBUSTNESS_V1/runs/t01_latest_cad_stand_nominal_420101_pilot001/result.json>)；8s，wholecase25.7646s；接触身份null，完整T01=false |
| 当前物理后台job | **父代理无后台批次；pwsh-356277d708544ecb已收exit0**；[420152结果](<RM_ROBUSTNESS_V1/contact_distance_probe_v2/runs/t01_c2_contact_distance_420152_probe002/result.json>)：12s/1200控制24000物理/20000点，model/DR各1，55.4069s。原C2/全部gate不变。44799次原生距离查询，覆盖全47282静态碰撞几何的保守AABB，候选最大左29/右11、无截断。空档左1257/右808在1μm容差内，其余左772/右89正间隙；最大4.77544/3.04452μm，无负重叠例。不是独立样本/第四控制；停止同类诊断扩展。原420151已收保留 |
| 已完成正式case | [nominal_stand 420110](<RM_ROBUSTNESS_V1/runs/t01_formal_nominal_stand_420110_001/result.json>)通过：1200控制/24000物理，接触20000点，双轮各100%，guide/hard/无支持0；[nominal_slow 420111](<RM_ROBUSTNESS_V1/runs/t01_formal_nominal_slow_420111_001/result.json>)机器人筛选失败：同1200/24000步完整执行，roll峰.425702rad=24.39°/RMS.273224rad，主轮支持.87535/.92525，无支持370点、最长单段.5ms，guide/hard0；进度1.50339m、速度RMSE.04355m/s、停车RMS.00787m/s |
| 正式进度 | **基线收2/6；C1、C2、C3各收1/6，T01仍进行中。三机制已实测，保留C2；C3未改善接触，不采用；其他定点/DR暂停**。已消费420110_001、420111_001、420121_001、420131_001、420141_001；五formal共6000控制/120000物理（pilot另计），旧失败保留，不改gate、不复跑 |
| 已冻结正式协议 | [T01协议](<RM_ROBUSTNESS_V1/T01_PROTOCOL_V1.json>)保持不变；基线低速未过，先定位横滚和支持抖动，不扩大DR |
| 下一唯一动作 | **当前继续T01 C实现接线：本轮估计器→C2请求力矩和M4/M7对象已通过接口/编译检查，先完成该实际阶段Git收口；驱动/BSP/硬实时仍未接，不发送电机命令，不复跑旧case或开启第四盲调。** 以下为用户观看的历史交付，本轮未操作窗口。**22:21用户直接要求看V3起跳，已实际打开V3保存轨迹供观看，不是采用新版控制。** [回放](<JUMP200_REPLAY_V1/README.md>)22:31曾核实PID10548/窗口1120612/Responding=True（本轮未查询持续存活），attitude/0.5倍循环、1000完整37维pose、从记录2.4s开始（起跳前1.11s），镜头跟随，画面标明V3落地失败；仅显示记录，无mj_step/新控制case/原结果改写。首次spawn001到READY后进程已不在、stderr空、退出原因未确认，日志保留；spawn002已核实命令行/窗口正常，前次pwsh-bcc2767d51a248cc已收exit0，不重收。先保持用户观看，不抢前台或重跑已消费试验。T01原严格门仍失败，同类微接触探针/盲参数循环停止；T01旧退出缺陷的源码/错误备份保留；本轮主线程入口及隐藏暂停验证见本行后段。21:34机身稳定窄改V3与全部归约已收，落地更差/仅稳1.34s，冻结失败，不再补跑/扩DR。回放交付与V3正负结果合并Git收口后回主线；T01已写[主线程Tk入口](<RM_FPS_PLAYER_V1/player_main_tk_v1.py>)，复用原布局/绘制/控制，只把Tk/变量留主线程，GLFW/Engine归工作线程，值/状态通过普通数据队列交换。**main_tk_lifecycle001已完成并收集exit0**（job pwsh-6fa0199ec9db4ebe，PID69912）。真实latest_rm/c2_fps，47600geoms/37nq；主Tk线程69916、GL工作线程70356，隐藏暂停3s后Worker关闭→主Tk关闭，stderr空；**0控制/0物理步/sim_time0**，不是新机器人试验。原启动器现指向新入口，桌面wrapper不变；当前J200回放未动。只证明这一隐藏暂停打开/退出路径，不宣称全GUI交互或T01物理毕业。勿重开同类探针/盲参数循环 |
| 本轮T01组件迁移 | 已写[T01 C2参考生成C99](<T01_C2_REFERENCE_C99_V1/pc2_reference.h>)，直接调用旧CTK公开FK，不重写机构/不改旧C3。范围仅C1腿参考＋可选C2航向保持；FPS已做航向时须关闭本组件外环。不是完整力矩控制器/新物理候选/T32–34退化测试/整机部署，当前pc3_p25_step也不是coord_soft的即插即用后端。固定100Hz、传感器/年龄/域/alias验证，失败不提交状态。**新组件数学对照已收集：validation002 exit0，job pwsh-d4f913e5e5d14080**。[预声明协议](<T01_C2_REFERENCE_C99_V1/validation002/protocol.json>)和[结果](<T01_C2_REFERENCE_C99_V1/validation002/result.json>)：GCC C99/Wall/Wextra/Werror编译0，1080个新合成输入＋16项故障合同通过，inverse接受状态无不一致；reference4最大误差5.99370e-7rad、yaw-rate2.99653e-8rad/s、共同角1.51195e-8rad。host state/input/output=64/88/52B，native全流程0.24169s含读写/启动，非ARM WCET。首次001因测试脚本读错K键在编译前失败（pwsh-45e781b4340042f0已收exit1）；原脚本/错误保留，仅修正实际K_6x14后以相同预声明阈值独立002验证，不重跑001。**0物理/无旧case与holdout读取，未操作V3观看进程**。T01原接触失败、3/3机制计数和所有冻结记录保持不变 |
| 本轮T01力矩C99 | 已写[当前C2力矩数学链](<T01_C2_TORQUE_C99_V1/pc2_balance.h>)：复用上一轮PC2参考、CTK 6×14 LQR/FK、冻结P25数据和PC3行映射；共同sagittal反馈保留、左右差分PD、低速park积分、原coord_soft整形、yaw防积分饱和及两次限幅顺序按原Python迁移。**新组件验证C2_TORQUE_NATIVE_MATH_001已收exit0**，job pwsh-ab5c35f1536a442d。[协议](<T01_C2_TORQUE_C99_V1/validation001/protocol.json>)在执行前声明门槛，[结果](<T01_C2_TORQUE_C99_V1/validation001/result.json>)：GCC C99/Wall/Wextra/Werror编译0/原生0，2300新合成输入与33故障断言通过；力矩最大绝对差8.8702421e-5Nm（门2e-3），无无效行/界限超差，1040行请求限幅/386行速度包络；host状态192B，整批原生0.493328s含进程/I/O/断言，不是ARM WCET。ref14含混合SI单位，最大逐元素差3.54679e-5不是姿态跟踪误差；详见[说明](<T01_C2_TORQUE_C99_V1/README.md>)。只检查所选nominal算法的requested torque数学；0物理、无旧轨迹/holdout/新K，不改试玩/BSP。pc3_cycle不是该状态类型的直接调用者，arming/driver/内PD-D4-DC/硬实时/实机仍未接通，T01原严格接触失败和3/3计数不变 |
| 本轮T01传感链接线 | 已写[C3估计器→C2请求力矩接口](<T01_C2_SENSOR_CHAIN_C99_V1/pc2_sensor_chain.h>)：只调用现有estimator_update和pc2_balance_step；显式估计先验初始化，不是电机arming；错误贯穿锁存/估计器退出armed状态，NULL/alias前提错误不改对象。无driver回调或发送，不额外加外环DC预裁剪，原PD目标-D4-当前PD-DC执行顺序留给实际驱动。**新接口＋M4/M7对象构建已收exit0**，job pwsh-ab81a67ad6204bd5。[协议](<T01_C2_SENSOR_CHAIN_C99_V1/build001/protocol.json>)与[结果](<T01_C2_SENSOR_CHAIN_C99_V1/build001/result.json>)：256个新合成mean窗口/2个held view/258次正常控制，与同一C3→C2直接两步调用state14/torque差为0（接线检查，不是独立算法oracle）；7001断言，host状态904B/结果368B/整批原生0.174722s。合成count20是元数据声明，不是采集5120次实物创新。新增3个C TU各M4/M7、6/6实际armclang编译exit0，52字节头确认ELF32小端/ET_REL/EM_ARM。对象文件大小M4=2068/8672/6516B、M7=2072/8668/6516B，不是Flash或栈量；没有最终ARM链接/运行/WCET/BSP/HIL。详见[接口边界](<T01_C2_SENSOR_CHAIN_C99_V1/README.md>)。0物理/旧case，T01原失败不变 |
| Git已同步截止点 | **最新commit 6ee0c1dc2b1944e43ff8a00236ae28aab290e600**；tag trial-20261104-mod4v1-t01-c2-torque-c99，object d788f31712980ac560eb4568dae1213469727d33。含C2请求力矩C99数学后端/复用参考-FK-LQR-P25依赖/原Python对照/预声明协议/2300新合成输入与33故障断言结果；33个selected＋record=34，原helper一次，atomic非force push，remote ownbranch/tag/peeled已核一致。pwsh-a03997a6698740cd已收exit0，后到通知不重收；本阶段0物理、无旧case/holdout/新K/BSP/UI变更，不是T01/ARM/HIL毕业。合成输入/原生输出/exe仅实际路径/大小/未知SHA索引，未为归档读payload/hash；后补回执不循环归档。前序 **commit c8720a0a2d98c46c85781595f998e70e852b3089**；tag trial-20261104-mod4v1-t01-c2-reference-c99，object 826d45504554f944f98cf9aa258dcc793ecad869。含T01 C99参考组件/复用FK依赖/原Python参考/预声明协议/1080新合成输入对照与16故障合同结果、001编译前软件错误和原脚本；32个selected＋record=33文件，原helper一次，atomic非force push，remote ownbranch/tag/peeled实核一致。pwsh-02d62b6f58b64716已收exit0，后到完成通知不重收。0新物理、不改变T01原失败、不宣称整机C2/ARM/HIL；合成输入/原生输出/exe只作真实路径/大小/未知SHA索引，不为归档读payload/hash。后补receipt不循环归档。前序 **commit 905d81bb80f02a3a9f64e00bf4f5596dde29df70**；tag trial-20261104-mod4v1-fps-main-tk-v3-view，object e5000783f09818d7e5a3ce2bc8dd930a5ff3e033。含主线程Tk入口/原布局依赖/启动器/一次隐藏暂停生命周期exit0、V3用户观看入口/两个实际spawn日志/任务截止点，19个selected+record，原helper一次调用，单次atomic非force push，remote ownbranch/tag/peeled均实核一致；pwsh-0fca4bbaa6084144已收exit0。无新机器人物理case；回放不等于采用V3。后补receipt不另造循环归档。前序独立mod4v1-lqr-mpc-robust分支**commit b954dc0e5e5f16d73400a6c2d1c34144c3079725**；tag trial-20261104-mod4v1-j200-replay-attitude-v3，object 42610c743828a066c4641078b6488af01c1779e5。原helper一次调用，28个selected+record，单次atomic非force推送；remote分支/tag/peeled均实核一致；pwsh-2663a539c75749e2已收exit0。含独立无Tk的J200已存轨迹回放代码/入口/实际启动日志、旧FPS退出错误及源码备份、V3源码/配置/1000ctrl20000PHY失败结果/完整分段姿态归约。V3起跳/预测air改善但落地22.95°和末端1.34s整体失败，不采纳/不换回放。两大新raw仅路径/大小/生产者既有SHA索引，不读payload/hash作归档；不重跑物理。前序c1b883a7/7d7efa8c/c3839048/829b7dca/5779f03e/4e491636保留，历史PH12仍pending |
| Git续记pending | 此回执之后的实际工作随下一阶段提交；历史PH12单独pending。原record helper每stage仅调用一次，既有commit只续推原objects。本次回执不触发新归档 |
| 暂不开的事项 | T02–T36；不接/测移动跳，不扩大rough/DR批次，不重做旧K/QA/holdout/归档 |

### T01只读根因诊断420151：已收集，不是第四控制候选

[探针源码](<RM_ROBUSTNESS_V1/run_t01_contact_geometry_probe_v1.py>)直接继承原AuditedPlant、复用正式runner和C2；[结果](<RM_ROBUSTNESS_V1/contact_geometry_probe_v1/runs/t01_c2_contact_geometry_420151_probe001/result.json>)与[在线几何归约](<RM_ROBUSTNESS_V1/contact_geometry_probe_v1/runs/t01_c2_contact_geometry_420151_probe001/contact_geometry_summary.json#L1-L89>)已生成。12s/1200控制/24000物理、model/DR各1、20000诊断点；nominal确定性复现原C2，新增观测不是独立鲁棒样本。

- 左2029低力点全部没有接触点/有效约束，法向恰为0；右897点同样如此；whole165点同样如此。并非有几何接触但力落在0–1N。
- 有支持点全部有负接触距离和有效约束；左最深约51.11μm、右48.84μm。空档没有接触记录，距离为null，尚未量到有限正间隙；不将“无记录”直接写成已证明有限几何分离或24棱面因果。
- 低力单轮实际ctrl峰值左1.75153Nm/右0.608125Nm，post轮速峰值6.26999/5.28266rad/s；不是完整DC限幅占比。**whole子表的torque/speed=0只是未采集的初始化值，应视为unavailable，勿当零扭矩/零轮速测量。** 原生成文件保持原样并在此勘误。
- 俯仰/横滚/速度/行程/横偏/停车门仍过，主轮支持89.855/95.515%、whole165点仍失败；guide/hard0。没有额外mj_step/mj_forward，原审计与新增逐点法向和已交叉核对；不更改gate。
- 本机现成MuJoCo API已读docstring：mj_geomDistance(m,d,geom1,geom2,distmax,fromto)返回smallest signed distance，可在缓存几何上补缺失量，不新写碰撞器。这是420151截止时的缺口；后续420152已执行signed-distance只读诊断并收集，见恢复栏，不再重复同类探针。

### 已交付实际试玩：C2腿调平＋既有FPS航向

- [运行入口](<RM_FPS_PLAYER_V1/Start_RM_FPS.bat>)默认最新CAD/c2_fps；可在面板切回coord_soft作对照。普通/Shift=2m/s指令范围保留，明确仅0.3m/s名义低速有既有工程证据，高速/全DR/跳跃未验；不是全功能毕业。
- 首接线进程18668真实运行至52.65sim秒后，Python3.14在Tk.update出现PyEval_RestoreThread原生崩溃，不归为机器人失败。[错误日志](<RM_FPS_PLAYER_V1/player_c2fps_20261104_204056.stderr.log>)和[崩溃前源码](<RM_FPS_PLAYER_V1/revisions/player_c2fps_before_tk_thread001.py>)保留。
- 线程版曾分离Tk/GLFW消息线程、去掉嵌套update；进程**51820**启动时实核Responding=True/窗口3028168，持续BALANCE及实际用户操作到约666sim秒。但退出后[stderr](<RM_FPS_PLAYER_V1/player_c2fps_tkowner_20261104_205204.stderr.log>)出现`Tcl_AsyncDelete: async handler deleted by the wrong thread`，进程现已结束；**并未修好退出生命周期，不重开旧版冒充已修复。** [退出前源码备份](<RM_FPS_PLAYER_V1/revisions/player_c2fps_before_main_tk001.py>)已留；这是21:22前的历史状态；后续已交付主线程Tk入口并完成一次隐藏暂停生命周期exit0/0物理验证，见恢复栏。旧线程实现冻结，不重开冒充已修复。本机全CAD约10–11FPS，不称实时/60FPS；历史[stdout](<RM_FPS_PLAYER_V1/player_c2fps_tkowner_20261104_205204.stdout.log>)保留。

### 人类优先委派例外：J200 跳上200mm台阶

2026-11-04 20:06用户明确要求派一个子代理专做轮腿机器人LQR/MPC跳上200mm台阶，并多看开源。本节是最新明确顺序例外，覆盖后文“只T01/不并开技能”的局部限制；其余36项与270mm长期目标保持不变。

| 字段 | 当前状态 |
|---|---|
| 负责代理 | 仅复用原跳跃代理 **abf2088f-af10-479a-9108-202785031447**。**21:34用户新指令：跳台全过程机身尽量稳、少倾斜，已send_message恢复**，覆盖此前停在两例等指令的局部状态。两版冻结；只允许一个有据窄改＋1个新nominal，先按阶段归约pitch/roll/角速，再比较改善量；不网格/不扩DR/不降台阶或暗减速/不root扶正，保住实际200mm越沿及台顶双主轮稳定>=2s。**新case j200_attitude_v3_nominal_200003已执行并收完**（job pwsh-5875f26e3f544f72，rc0/collected）：10s/1000控制/20000物理，launch3.51s、完整胎网格越沿3.91s；末端稳定仅1.34s<2s，guide43tick/hard0，MPC approach351接受/0回退、landing537/67。**分段归约已收、V3整体失败并冻结，不采用为控制版本、不补长尾、不再补跑；22:21用户要求观看V3保存记录，仅供显示，不等于采用。** 已读[最小结果](<JUMP200_LQR_MPC_V1/ATTITUDE_V3_MINIMUM.json>)：对captureV2→V3，push pitch峰16.69→3.40°、预测air15.21→6.52°，但landing17.79→22.95°/RMS3.99→7.28°，全程peak22.95°更差；guide峰23.354kN。launch真值vx1.36557/估计1.49277m/s、世界x=-.56565；精确2k脱地速度未存，不伪造。MPC回退67含迭代19/小角域48，仍是地面MPC。跑道-2.5/2.0及时程10s是输入/时程变化，不称与原8s同工况单变量证明；新1000trace与2kcontact各一次归约、无二次旧raw扫描/DR/新代理；代理已停 |
| 状态/证据 | **两例名义完整上台＋台顶双主轮站稳已达成；洁净落地失败，DR未验**。[基线](<JUMP200_LQR_MPC_V1/runs/j200_nominal_baseline_200001_attempt002/result.json>)800/16000、末端稳定3.01s、guide13tick/hard0；[早capture](<JUMP200_LQR_MPC_V1/runs/j200_capture_v2_nominal_200002/result.json>)800/16000、3.86s、guide36/hard0。真实胎网格越沿/顶面全足迹＋20子步主轮承载，非仅root升高或guide挂台。基线guide峰20.36kN，第二方案未证实碰撞改善；不抹掉动作成果，也不称洁净/软落地通过。job pwsh-542f71521320484a、pwsh-447adc8aa9f1447c均已收exit0；首遥测软件错20PHY/0完整ctrl单列保留，合计32020PHY。以上为前两例冻结截止；21:34授权的[第三例](<JUMP200_LQR_MPC_V1/runs/j200_attitude_v3_nominal_200003/result.json>)现已执行并收完（见负责代理行），J200累计52020物理步。其末端稳定1.34s未过2s，未采纳/不替换回放；分段归约已收并读小结果：起跳和预测空中更平，但落地pitch峰22.95°>17.79°且仅稳1.34s，**V3整体失败/冻结，不采纳为控制；22:21用户改为观看V3保存记录**。完整数据见[最小结果](<JUMP200_LQR_MPC_V1/ATTITUDE_V3_MINIMUM.json>)与[比较](<JUMP200_LQR_MPC_V1/ATTITUDE_V3_COMPARISON.json>)。代理在提交全部结果/冻结消息后closing异常；已落盘的物理与归约结果不因服务closing重跑 |
| 源码优先 | 用户SPR/7z的跳跃FSM、腿长F/Tp、过阶；本机MiniHop/270mm原型、QP/MPC、传感/接触审计；再看最多2个真实相关外部开源仓库 |
| 第一交付 | [运行说明](<JUMP200_LQR_MPC_V1/README.md>)与[分级结果](<JUMP200_LQR_MPC_V1/STAGE_RESULT.json>)已冻结：run_case.py/run_capture_v2.py、两配置、bridge200.py。实际LQR跳跃阶段＋approach/定时恢复阶段15步8+lag标量box QP，**非空中/接触MPC**。基线MPC接受139+549/回退30+0；机制2接受139+558/回退30+28，含QP迭代上限14，solver峰6.5975ms不是硬实时资格。两个名义例已收停；baseline的buffered trace误标streamed/phase遥测标签在README勘误，原分数/失败不改 |
| 完整行为 | 明确额外200mm竖阶fixture；起跳前进→机身越沿→双轮腿跟进→200mm顶面稳定≥2s；真胎网格净空、顶面/竖面/guide/hard与接触时序分别评分 |
| 资源/边界 | 子代理最多2物理CPU，父代理继续T01最多1；BLAS/OMP/MKL1。机器人/PD/D4/DC/电机/闭链冻结，传感器控制，无root助力/瞬移/DR抵消；站姿初始化只用于跳台，不算自然起立；子代理不Git，父代理收完成截止点 |

### 每次状态落盘的硬规则

1. **启动前查表和输出目录。** 已有完整result/已消费case不再启动；已有ERROR/部分trace也先调查，不通过换名偷偷重跑。
2. 启动新case后立即在本节记case ID、实际job ID、输出目录与“运行中”。已有job先收集，不凭估算补结果、不并行复制同一case。
3. 收集后马上记“已完成并收集/软件失败/机器人失败”、实际控制/物理步、关键指标和结果链接；失败保留prefix。清除已结束job的“运行中”标记。
4. 修复后若确需再测，使用新case ID，记清修复和前次失败的关系；重复运行必须有具体理由，不重跑整批冒充验证。
5. **干完一项立即改该行状态**为“本项工程筛选通过”，填写通过代码/参数版本、冻结协议、实际结果、遗留限制；表头移到下一T编号，同时更新可见todo。没有证据链接就不打勾。
6. 本项通过时保留通过版本，后续不就地覆写该版本。后项改动影响前项时，仅做受影响的最小回归并另记结果，不把全部已完成项重置为待办。
7. 任务完成不等于整机独立可靠性或实机资格；T36和实机绑定缺口单独保留。旧冻结H1/H2/H4/H5不为回归重跑或调参。
8. 上下文压缩只压缩聊天，不改变本表状态。恢复时从表头“下一唯一动作”继续，不重新立36项清单、不从历史模块零开始。
9. **Git是每项收口条件。** 本项成功/失败、代码/参数/协议/结果及任务状态一起记录到独立传统控制分支，使用项目record_experiment.py和唯一annotated trial tag；核验remote分支、tag和peeled commit后才写“已同步”。只提交实际截止点，活跃未完成源码/后续报告如实pending。
10. 只用独立repo-lqr-robust工作树/mod4v1-lqr-mpc-robust分支；不碰RL专家工作树/index/main，不force push、不删除旧失败。已commit但push失败只续推原objects，不重record。
11. 大型轨迹/CAD/ZIP/模型留在来源，Git只放已有真实路径/大小/SHA索引；SHA未知照实未知，不为归档重读巨raw。后补内容随下一实际阶段提交，不制造无限回执→验证→回执循环。

## 执行规则

- 唯一当前项：**T01**。T01 完成本阶段验收后才启动 T02，依次至 T36；测试骨架和只读审计属于当前项，不另外展开其他运动项目。
- 每项闭环：冻结本项筛选线 → 实际 CAD 基线 → 定位具体失败 → 最多 3 个有机制依据候选 → 新 TRAIN 对照 → 保住前项功能 → 留证据并更新本表。
- 状态区分：待处理、进行中、候选失败待修复、本项工程筛选通过、最终独立验证通过。未跑、软件失败、个别成功均不算通过；本项筛选不等于整体可靠性证明。
- 控制仅传感器/电机反馈、公开地图计划和操作命令；真值只评分。无 root 扶正、无自动传送、无人工复位冒充恢复。
- 主线为用户指定最新版 CAD 全场，不用旧简图/平地取代；额外坡角、摩擦、外力、竖阶均标为附加 fixture。
- 已有 H1/H2/H4/H5 与旧模型/增益/once/失败记录冻结；新结果不重写旧结论。
- 2m/s、持续 ±4πrad/s、270mm 越台为既有目标。平移和自旋组合服从实际电机包络，不同时硬顶两个满指令。

## 任务与验收行为

| ID | 任务 | 本项要解决的行为 | 状态 | 当前证据/后续证据 |
|---|---|---|---|---|
| T01 | 真实 CAD 定点/低速平衡 | 定点不漂、底盘平稳，低速走后能停稳，主轮真实承载 | 进行中：C2非接触门通过，接触待解 | [基线定点通过](<RM_ROBUSTNESS_V1/runs/t01_formal_nominal_stand_420110_001/result.json>)、[基线低速失败](<RM_ROBUSTNESS_V1/runs/t01_formal_nominal_slow_420111_001/result.json>)、[C1失败](<RM_ROBUSTNESS_V1/roll_follow_v1/runs/t01_c1_nominal_slow_420121_001/result.json>)均保留。[C2](<RM_ROBUSTNESS_V1/heading_follow_v2/runs/t01_c2_nominal_slow_420131_001/result.json>)：roll峰1.61°、行程1.62363m、横偏.04681m、停车RMS.00554m/s，非接触门全过；支持89.855/95.515%、无支持165点未过，guide/hard0。五formal和两只读诊断各1200控制/24000物理、20000接触评分点；诊断不是新独立样本，定点回归/DR暂停，原支持严门留缺口；停止同类探针，C2式腿调平已接实际FPS试玩 |
| T02 | 正反 2m/s 与操纵 | 起步、急刹、换向、弯道和快速命令不失稳 | 待处理 | 历史平地 90s TRAIN 有部分证据，待同图复验 |
| T03 | 连续变高 | 低/中/高姿态及行驶中升降、下蹲与恢复 | 待处理 | 高姿态旧失败保留，不以升高底盘当过障 |
| T04 | 正反上下坡 | 上下坡、驻停、起步、急刹、防后溜 | 待处理 | island_ramp_up/down、trapezoid |
| T05 | 横坡/斜向坡 | 左右高度差下维持姿态与抓地，抑制侧滑 | 待处理 | 原 CAD + 明确附加姿态/方向 fixture |
| T06 | 坡面过渡 | 坡脚/坡顶、凸脊/凹谷、坡转平不甩机身 | 待处理 | 原 CAD 坡面连接区域 |
| T07 | 平地 ±4π 自旋 | 持续每秒两转、启动、停止、换向、中心漂移受控 | 待处理 | 冻结 H2 部分能力不等于当前控制器全部通过 |
| T08 | 坡面 ±4π 自旋 | 朝向周期变化时姿态、载荷与中心保持 | 待处理 | slope_spin 原范围仅 ±4rad/s，需扩展至 ±4π |
| T09 | 自旋切换与组合 | 平移/变高/制动进入退出自旋，按轮速力矩包络调度 | 待处理 | 不把 2m/s+4π 满值硬相加 |
| T10 | 连续小坎/起伏 | 正反起伏、搓衣板、凸包与连续小高度变化 | 待处理 | rough_forward/reverse；SCUT 配方另标来源 |
| T11 | 单侧/不同高 | 单轮先过坎、过坑、短时失去一侧支持仍稳定 | 待处理 | 必须区分左右承载与 guide 支持 |
| T12 | 竖直阶沿全过程 | 接触受阻→机身越沿→低处轮腿跟进→重心转移→站稳 | 待处理 | central_lip、central_upper；270mm 独立目标保留 |
| T13 | 高姿态上台 | 底盘净空后，整机及轮腿完成上台并稳定 | 待处理 | 明确机械可达性、关节限位与载荷分配 |
| T14 | 单侧/斜向上阶 | 左右轮腿接触时序不同仍抑制侧翻 | 待处理 | 偏置/方向为明确附加测试 |
| T15 | 连续阶与平台边缘 | 连续多阶、窄台面、跨沿后维持有效支持 | 待处理 | 不以挂在阶沿/guide 支撑当正常通过 |
| T16 | 下阶与落差 | 下台、驶出阶沿后的缓冲，抑制俯冲和硬接触 | 待处理 | central_upper_down 及明确落差 fixture |
| T17 | 原地跳基线 | 真实起跳、落地、抑制反弹并恢复平衡 | 待处理 | 已有单次 6s 原地跳；root 升约 .166m 不是轮胎净空/270mm |
| T18 | 正反移动跳 | 不先刹停，压腿/起跳/飞行/落地保留速度，随后继续跑 | 待处理 | jump_moving_v2.py 仅未执行候选；移动 physics=0 |
| T19 | 坡面/斜向跳 | 不同起跳姿态和坡向下可控起跳与回落 | 待处理 | T18 和落地切换稳定后验证 |
| T20 | 飞坡与跨沟 | 原 CAD 正反/镜像飞坡、间隙跨越的轨迹和能量可行 | 待处理 | fly_jump/mirror，不凭 root 高度判越障 |
| T21 | 对称落地 | 双轮缓冲、抑制反弹、快速复稳并接回行驶 | 待处理 | 实际接触冲击与恢复时间，非仅定时 phase |
| T22 | 非对称落地 | 单轮先落、斜坡/不同高/带水平速度落地 | 待处理 | 真实左右落地时序 |
| T23 | 接触抖动/二次腾空 | 飞行禁用轮速平移观测，着地窗口平滑重接 | 待处理 | 不用空转轮做 ZUPT，不用 timer 冒充接触确认 |
| T24 | 支持模式识别 | 主轮/guide/单侧支持/全机离地正确区分和切换 | 待处理 | 审计真值只评分，不喂控制器 |
| T25 | 救姿态 | 前倾/后仰/侧倾后救回，稳定后继续走 | 待处理 | 有界轮矩/腿伸缩，不持续外力扶正 |
| T26 | 摊卧起立/倒地恢复 | 前趴、后躺、侧倒自然恢复 | 待处理 | 旧失败完整保留；禁站立先验、禁人工 R 算成功 |
| T27 | 常规外扰 | 站立/行驶时多方向、不同高度与冲量推击后稳定 | 待处理 | 外力为有记录短时扰动，非辅助 |
| T28 | 复合外扰 | 高姿态、过阶、跳跃、落地、自旋中受撞和二次接触 | 待处理 | 分别继承对应动作已冻结版本 |
| T29 | 摩擦与打滑 | 低/异摩擦、摩擦突变、空转/抱死后重获抓地 | 待处理 | 不抵消实际抽样参数 |
| T30 | 缩腿通行 | 狗洞/镜像、窄通道/窄平台低姿态通过与出口变高 | 待处理 | tunnel/mirror，真实碰撞/限高 |
| T31 | 受阻与脱困 | 卡轮、顶阶/墙、近限位/奇异区的检测、退让和重试 | 待处理 | 禁饱和顶死、积分堆积、无限重试 |
| T32 | 模型变化 | 载荷、质心、质量惯量和弹簧变化仍维持任务 | 待处理 | 模型 fresh，DR once；附加载荷另标 |
| T33 | 观测退化 | 噪声/偏置/延迟/丢帧/异步/撞击尖峰下估计与降级 | 待处理 | 通道窗口与年龄明确，不伪装瞬时同步 |
| T34 | 执行退化 | 力矩轮速饱和、功率降额、通信异常时姿态优先 | 待处理 | 电气/热 fixture 与既有 DR 分开；无硬件资格冒称 |
| T35 | 连续混合任务 | 坡→坎→移动跳→落地→转弯/自旋→停车，无逐段人工复位 | 待处理 | 长时漂移、切换瞬间和连续任务评分 |
| T36 | 独立全 DR 验证 | 完整 D0–D7，冻结后新 seed holdout 和不确定性报告 | 待处理 | 不调 holdout，不把小样本训练成功当可靠性证明 |

## T01 预先冻结的工程筛选线 v1

这是本项功能适配筛选，不是全地形/实机可靠性资格；最终独立统计验证在 T36。pilot 仅确认能运行与耗时，不作为正式验收。

- 场景：latest_rm 的 flat_run 原始起点/实际 CAD 碰撞。0.5ms 物理、100Hz 控制、原 PD/D4/DC、原机器人/闭链/电机上限。
- pilot：nominal、seed 420101、8s、定点；保留真实耗时和新 trace。
- 正式：12s nominal 定点与 +0.3m/s 低速各一例；四个新 TRAIN DR case（定点/低速交替），每例独立进程/新 model，DR 仅一次。seed 420110–420115。
- 定点目标全程 0；低速 0–2s 静止、2–8s +0.3m/s、8–12s 停车。评分窗口预先定义于 T01_PROTOCOL_V1.json。
- 所有正式例完整结束、finite、无自动复位，闭链≤0.01m，mimic≤0.01rad；根姿态/速度按当前 freejoint 评分，碰撞/约束缓存阶段明确标记。
- 2s 后俯仰/横滚绝对峰值各≤0.10rad、RMS 各≤0.035rad。
- 定点：XY 漂移≤0.20m，前向速度 RMS≤0.05m/s；低速 3–7s 速度 RMSE≤0.10m/s，前进至少1.2m，横偏≤0.20m，9–12s 前向速度 RMS≤0.05m/s。
- 2s 后两个主轮各承载正常力>1N 的占比≥95%；guide 支持占比≤1%且连续≤20ms；硬接触>1N 与全机无支持均为0。需逐2kHz审计；未采集字段写 unavailable，不填0。
- 冲击峰值/功率/饱和占比照实报告；未标定硬件冲击上限不硬宣称软落地或实机可用。
- 第一候选失败时保留失败和 trace，定位后只改有依据的机制，新 case ID 重测；不回改本筛选线以制造通过。

## 证据边界

原 CAD 的 15 条 route 是几何路线，不是通过记录。旧平地训练、原 H1/H2/H4/H5、未执行的移动跳源码均只作既有背景。每项后续通过需在其行填入新的配置、结果与失败对照路径，再更新状态。

## 历史复用台账：这些不是从零开始

2026-11-04 用户明确要求 Stop That Shit，并问哪些以前已做。主表的“待处理”指本清单完整工况/新 CAD 的剩余验收，不是旧工作全部作废。历史有证据的功能直接复用，失败保留；本节不新增物理、不重跑旧 QA/holdout。

| 对应任务 | 之前已做的内容 | 现在只补什么 |
|---|---|---|
| T01–T02 | 原平地定点/2m/s；旧 H4 实际 C 闭环驻车60/64、速度姿态64/64，但横向漂移未合格。最新 coord_soft 已做12条新 TRAIN，共920s，70s姿态峰值由19.03°降至1.65°；90s名义稳态约2.03m/s，另3个DR TRAIN。 | 直接用现有控制器，仅补最新版 CAD 的接触/定点/低速及操纵验收，不重造K、KF或DR。旧H4不能冒充当前版本已通过。 |
| T03 | 已有名义不同腿姿/高度增益库和高姿态粗糙路试验；单纯升高没有解决4–6cm路障。 | 连续变高、工作点调度、姿态与接触协同，不再盲增腿高。 |
| T07 | 旧 H2 持续4π角速度/姿态64/64、综合56/64，保留漂移/速度失败；启停换向另有失败。 | 复用自旋核心，补启停、反向和当前版本接线；不重跑/调H2。 |
| T08–T09 | 已有基础自旋和命令包络代码。 | 坡4π、变高/平移切入自旋的完整物理工况尚未验收。 |
| T10–T11 | 真实SCUT 2–6cm条栅试过；后续R42名义4cm单例通过，R43新DR仅1/8；6cm与非对称支持仍有缺口。 | 复用已写地形/姿态机制，在新CAD定位具体失败，不重复所有高度/参数盲扫。 |
| T12–T16 | 270mm定时移动越台/轮腿姿态/roll VMC原型及高姿态试验做过，记录了guide/阶面/硬接触与失败。 | 完成可靠的过沿→轮腿跟进→平台承载；旧clear或短暂站稳不算完整270mm成功。 |
| T17 | 原地MiniHop、主动落地已做；H5独立40/64，轮胎峰值净空.176–.267m；当前UI另有6s单例。 | 复用动作，补当前CAD与接地稳定，不用root上升替代270mm轮胎净空。 |
| T18–T20 | 早期有移动越台原型；新jump_moving_v2.py仅源码，当前候选移动物理0。 | 将已有动作真正接成跑动起跳、落地继续跑；坡跳/真实飞坡与跨沟待实测。 |
| T21–T24 | 已有观测隔离、落地过渡、contact proxy、FSM、2kHz main/guide/hard审计。H5仍24失败，不是落地鲁棒毕业。 | 复用模块，补全CAD world接触覆盖、可靠切换和非对称落地集成。 |
| T25–T26 | 多版自然摊卧起立和救姿态原型实际试过，仍未解决自然起立。 | 沿已有失败定位继续，不再把人工站姿reset或同一失败重跑当进度。 |
| T27–T28 | 有姿态/限幅基础，但未形成这两项完整外扰验收证据。 | 新增有边界的碰撞扰动验证，不先做大型扰动框架。 |
| T29 | 原D0–D7已含轮胎摩擦随机。 | 专门低/左右异摩擦、失滑与重新抓地尚待闭环验收。 |
| T30–T31 | 原CAD狗洞/台阶几何已导入，有输出保护/限位故障处理。 | 真正缩腿通行、卡轮/顶阶后的退出和脱困行为待做。 |
| T32–T34 | 完整DR、IMU/KF、C观测器/控制、QP/MPC、功率分配、ARM数学对象已有。BSP与DM3519单电机测试镜像已有，非整机平衡。 | 直接复用；补新工况适配与端到端集成，电热/硬件标定未绑定的不冒称完成。 |
| T35–T36 | 已有多个独立冻结holdout及其失败统计。 | 新控制器连续整图与最终新seed验证；旧holdout不再调、不覆盖、不为“复验”重跑。 |

已有摘要证据：[R47](<CONTINUATION_R47.md#L15-L57>)、[H5](<CONTINUATION_H5.md#L12-L24>)。最新平地稳定控制直接使用 [coord_soft](<FLAT_STABILITY_FIX_V1/controller_v2.py>)。

## 两份用户开源的复用清单：2026-11-04 19:34追加

来源是用户指定SPR Balanced-infantry (2).zip和chassis.7z的已选源码。优先直接迁移函数/状态与调度结构，按MOD4机构/电机替换参数；不再为同一功能另造框架。标记“可移植”不是已完成新CAD验收。

| 模块 | 已实际读取的源码位置 | 复用方式与当前状态 | 对应任务 |
|---|---|---|---|
| 轮/腿共同LQR、低速局部停车积分 | [SPR Task:582–745](<SOURCE_REUSE_20261104_1542/spr2_selected/chassis/Task/chassis_task.c#L582-L745>) | 已用于coord_soft：恢复腿平衡通道、单独停车I；当前C2保留，不再重写 | T01–02 |
| PID：测量微分、带内积分、积分/输出限幅 | [7z PID:63–93](<SOURCE_REUSE_20261104_1542/chassis7z/readable/chassis/algorithm/PID.c#L63-L93>) | 函数与结构可移植；保留真实dt，避免目标微分kick。源码注释明确D低通未实现，不虚称已有 | T01–06、T17–26 |
| 轴向腿长力环与独立角力矩 | [SPR get_F:898–973](<SOURCE_REUSE_20261104_1542/spr2_selected/chassis/Task/chassis_task.c#L898-L973>)、[7z力映射:103–111](<SOURCE_REUSE_20261104_1542/chassis7z/readable/chassis/algorithm/leg_force.c#L103-L111>) | 复用F/Tp分通道和J转置方法；旧机构生成系数替换。C3只加D、未叠P/I，已实测但未改善支持，封存不默认启用 | T01、T03–06、T12–24 |
| 随腿长的LQR调度 | [7z实际else分支:181–218](<SOURCE_REUSE_20261104_1542/chassis7z/readable/chassis/algorithm/LQR_K.c#L181-L218>) | 复用腿长多项式调度/导出格式，替换为本机增益表；不搬旧车6状态12系数进本机14状态 | T03、T12–16 |
| 支撑力估计中的轮惯性项/滤波 | [SPR Fn:537–569](<SOURCE_REUSE_20261104_1542/spr2_selected/chassis/Task/chassis_task.c#L537-L569>) | 可复用计算结构，轮质量/重力/坐标/采样周期换本机值。原注释承认Fn偏小及阈值−20；不直接当可靠离地判据 | T21–24、T33 |
| 收腿→伸腿→空中收腿→落地准备→恢复 | [SPR jump:827–894](<SOURCE_REUSE_20261104_1542/spr2_selected/chassis/Task/chassis_task.c#L827-L894>) | 复用已有动作状态机，不另造跳跃框架；腿长门限换可达域，220次计数换明确时间；定时flag不是实测接触确认 | T17–22 |
| 机身倒下→摆腿→收腿→起立的协调 | [SPR climb:977–1061](<SOURCE_REUSE_20261104_1542/spr2_selected/chassis/Task/chassis_task.c#L977-L1061>) | 复用状态/轮腿先后关系和关节角速串级；姿态/腿长、方向和限位换本机。不是把旧0.4m/1.4rad直接设给MOD4 | T12–16、T25–26 |
| 平衡优先的功率分配 | [SPR power:1070–1165](<SOURCE_REUSE_20261104_1542/spr2_selected/chassis/Task/chassis_task.c#L1070-L1165>) | 复用平衡/平移/转向分量优先级，接既有本机power allocator。旧3508电流/损耗、Right_Leg与右轮字段混用、分母为零口先修，不整段照搬 | T09、T28、T34 |

本轮不重造BSP/CAN、KF、DR、MPC/QP、接触FSM；这些已有自己的实测/编译资产，直接接现有模块。新移植只补实际接口差异。所有开源方法仍须在本机新case验证，源码存在不等于已通过。

## Stop That Shit 本轮执行边界

- 只让 T01 进行中；其余任务不并行开跑。两个现有子代理只做当前项必要 runner/审计，不新建代理。
- 复用已有控制/估计/DR/接触/FSM/功率模块；有新场景缺口才最小修改。
- 一次小pilot后先收集真实结果，才开正式case；失败保留prefix，不一边跑一边重复启动。
- 最多3个有具体失败依据的机制候选；相同错误反复出现就停止扩张并只定位该错误，不做长链预检/审查/归档。
- 旧单测、旧holdout、旧大raw不为凑新证据重跑/重读/重hash；当前代码确有影响的必要检查另论。
- 输出区分源码完成、物理执行、工程筛选通过、独立验证；计划/编译/跑完均不自动等于能力通过。
- 本地Stop That Shit指令手动应用并查询状态；自动宿主动作拦截效果未验证，原生硬Token上限未验证，不宣传为已生效保险。

