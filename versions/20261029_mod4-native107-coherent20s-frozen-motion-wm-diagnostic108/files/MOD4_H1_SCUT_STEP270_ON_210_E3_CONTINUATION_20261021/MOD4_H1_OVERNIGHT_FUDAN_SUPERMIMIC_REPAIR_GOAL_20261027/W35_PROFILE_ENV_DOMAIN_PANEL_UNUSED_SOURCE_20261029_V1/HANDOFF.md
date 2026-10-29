# FROZEN / UNUSED — W35 profile×env与实际domain诊断源

本目录只完成LOCAL SOURCE准备、AST与合成CPU统计检查。没有连接服务器、查询GPU、加载/解码/forward任何旧模型或NPZ/raw、执行仿真/评测/PPO、修改107或任何owner/账本。所有旧false、旧1200结果及毕业标签保持原样。新源尚未实际评测、未source-admit、未毕业；交接后idle。

下一项具体用途是W35 adapted92正式78-update模型的600 controls（12s）：100 warmup/500 steady（2s/10s），原N20K、五G3、retained命令、mean策略、重置步骤与独立nearest250 bank34保留。目标是补上逐profile/逐env分母、moving与standing分开误差、实际命令/动作/队列/DR/reset边界；不是盲重原1200窗，也不是延长同一PPO学习窗。未强制重分配命令/terrain，未新增RNG draw；某profile没有曝光时明确pending，不强造数据。

选定文件：

- `evaluate_W35_adapted92_profile_env_domain_panel_UNUSED_once_v1.py`：真正GPU评测worker候选。SHA `6d4f20fdddd963434c63a4990e320930a980d5774c8bd9344d30c2a3e1a1cf94`。
- `w35_profile_env_domain_panel_v1.py`：统计与只读hook组件。SHA `4e2f4b92786e1987cdd843be7252d81e8cedb91ca28a32f3675976c5ec75e5c4`。
- `detached_W35_profile_domain_panel_private210_UNUSED_supervisor_v1.py`：原210有限supervisor只替换worker basename。SHA `320fd64ebe0c8fc2162d8dac7054259de87adea2b286acdfbf64c8111854e66b`。原privateEX、UUID-only/light利用率<=30且free>15669MiB、RAM32GiB、disk25GiB、1800s own wait与30/15退出、noCwrite全部保持；没有第二writer。
- `SELECTED_DEPLOYMENT_INPUT_MANIFEST_UNUSED_V2.json`：选定469项source/input metadata，排除旧1200 worker/supervisor。大模型、bank、USD等只用既有真实producer metadata，未打开、rehash或重复制。
- `FROZEN_CASE_TASK_TEMPLATE_UNUSED_UNADMITTED.json`：部署目标basename为`FROZEN_CASE_TASK_TEMPLATE.json`。三项实际准入布尔值均false、known72只读绑定null，禁止拿历史balance/CNone或旧owner当当前授权。

拟用全新目标root（本轮未创建）：`/mnt/mod4_linux_durable_20261013/MOD4_W35_PROFILE_ENV_DOMAIN_PANEL_20261029v1/w35`。仅适配source210/GPU937，86跨host并未伪装包含。下一执行须先root协调global serial lease、fresh LOCAL exactCIM、真实source/SDK/manifest/新Task与资源准入。下一purpose入口命令将是原210 python运行新supervisor `--job-root <新root>`，由parent拿原privateEX；不能重跑旧install/launch/first once。当前目录没有自动联网入口。

源保真：`WORKER_EXACT_SOURCE_OVERLAY_AND_INVERSE_ACTUAL.json` 证明逐项移除新overlay后旧worker字节完全相同，旧SHA `ff8399b8e8969afd27e7c95bf1def43319c311f6a69d0fbd9cd7cb024ad66bfb` 与原467输入manifest逐项匹配。模型SHA `ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f` / 17619013B来自既有正式producer/wholeCPU索引，未本轮读取。原actor35/critic38/STD6、17Adam648360、算法/optimizer LR `.00011390625000000003`、D1-D7/RNG/queue、400N each与2000N/m工程recipe、2.5ms/TGS32/4/50Hz×8/100Hz feedback、nearest250独立bank34和原全部termination/模型与norm/optimizer不变检查保持。既有wholeCPU witness可按原SHA `c633a5eb9f091c6d6b2327ae86b3d0b61d25c1b43964b20d875567f97c692442` 引用；本轮没有为指标/Git再load模型。

统计输出（实际运行后才存在）：

- `W35_PROFILE_ENV_DOMAIN_PANEL_ACTUAL.json`：whole/warmup/steady ×42 profiles，以及all/gentle/standing/straight/moving_world_yaw/eligible_other分组。每组给实际population-control分母、独立暴露环境数、MAE、终止/timeout mask事件及独立环境数、原reason事件/独立环境数、signed cycle事件/独立完成环境数。whole unique按env集合OR，不相加phase unique。
- `W35_profile_phase_env_fresh_denominators_sums_events.npz`：新产生的稀疏phase/profile/env记录，保留每env真实曝光分母、误差sum、termination/truncation/reasons、cycle事件与最长live连续时长；没有曝光的profile不能给0误差当通过。此NPZ不会从旧raw补造。
- `W35_selected_profile_domain_before_terminal_reset.jsonl.gz`：每个trace control按实际profile取前4个当前env ID，无RNG。trace controls为最初24个及steady每10个（最多74个control）；选择随当前真实profile变化，记录实际env ID，不假称固定cohort。
- trace记录原actor输出、原actor接收的policy35/critic38、action_manager实际入口、两个动作group各8个物理回调的queue-selected processed target及issue/lag/applied tick receipt、root13/q30/dq30、原command3/world direction、现有D1-D7状态/private RNG快照、实际cached stiffness/damping与nominal2000、terminal-before-autoreset、原reset IDs、成功reset后local episode UID、post-reset和returned done。

trace是选定环境的domain-labelled诊断，不是全20K转移集。queue目标是在原articulation apply之前的processed position/velocity target；原adapter后续真实articulation-target断言照旧，但不能把queue目标称实际力矩或contact groundtruth。root13/q30/dq30不是pack127，未给完整force/torque/xi31规范，因此`complete_WM_dataset=False`。保存上限为512MiB未压缩trace；到界保留已有记录并显式`trace_retention_limited=True`、后续trace不写，统计仍继续，绝不静默声称完整。原selected32 trace继续保留，不能因新trace改原输出/RNG/异常路径。

连续时长定义为实际完成的live interval；phase/profile/episode切换或done打断，terminal失败interval不计live持续时长。cycle只在steady、live及对应signed moving上计；事件数与unique env分开，unique env又不等于unique episode或全技能成功率。没有新增数值技能pass阈值：原完整legacy graduation阈值/每profile持续误差门槛在允许文本中未给出，必须显式pending，不把本12s诊断当最终验收。

已做：合成CPU（显式device=cpu）12项统计检查全部通过，未SDK import或actor/WM forward；覆盖moving分母、standing不适用world误差、重复失败/timeout事件与unique区分、重复cycle与unique区分、phase/episode/profile边界、whole unique OR。AST证明queue原apply只调用一次且返回原对象、原reset只调用一次且原env_ids实参对象保留、没有新simulation/RNG draw/state load/optimizer调用。原source错误与metadata V1 unmatched-parenthesis在`ORIGINAL_LOCAL_SOURCE_ERRORS_AND_V2_MINIMAL_REPAIR_ACTUAL.json`及拒绝V1源码保留；SELECTED metadata builder为V2。V1旧overlay manifest不是部署selected，保留历史。

尚缺的实际准入（不能用source检查替代）：

1. 新unused目标静态source/SDK/math/原全部input/Task/sourceSHA与sourceCPU witness绑定；真实当前known72 owner/模式或CNone只读证据，由root当时提供，不能照搬历史字段。无C写、无第二writer。
2. 实际资源、可用GPU、原privateEX、project-only隔离cache/config和真实sup/worker exe/argv/create；不查或动其他任务。
3. 本新purpose首次GPU模型fullrestore、全部原D1-D7/STD/17Adam/LR/norm/source guards通过。遥测objects/API/selected slices必须实际验证，原 `_reset_idx` 的运行时env_ids契约为Tensor；没有从synthetic CPU假称SDK兼容。
4. 实际24 controls=192 physics callbacks、48 feedback samples；每group恰192 queue callbacks，记录tick单调、前后时钟和真实100Hz样本计数。遥测不多call actor/physics/reset/apply、不推进私有RNG或改变source行为；原异常不吞掉。原fullsave/retention与进程收尾路径保留。
5. 新600有限窗真实执行、walltime/overhead/存储容量与trace retention核验、模型/critic/STD/norm/全部17Adam literal unchanged。覆盖和技能结论依各profile实际曝光/分母，未覆盖/无阈值保持pending；不能自动宣布毕业或WM数据ready。

所有本轮source/CPU诊断/原错误与未执行候选交root普通Git补档，未创建trial/tag、未宣称已remote记录。冻结INDEX给完整字节SHA；本轮交接后停止，不自动申请lease或执行下一项。
