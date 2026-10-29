# FROZEN / UNUSED — W35新profile诊断的210安装、metadata准入与有限detached启动源

本轮仅LOCAL SOURCE派生与stdlib合成Task检查。没有执行本目录installer、任何remote CODE或新worker/supervisor，没有连接SSH、输入凭据、查询GPU、启动SDK/仿真、读取模型/PT/NPZ/raw/USD内容、改H1/107或任何owner/账本。旧source目录完全不改。所有新准入与运行结论仍pending；完成本次交接后idle。

**根下一步审核/实际入口**：`install_admit_detach_W35_profile_domain_panel210_UNUSED_once_v1.py`。调用者是Windows原Python314，必须先由root协调global serial SSH lease和fresh LOCAL exactCIM：

```text
C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe -B <本目录>/install_admit_detach_W35_profile_domain_panel210_UNUSED_once_v1.py [--known72-binding-json <当前真实绑定JSON>]
```

当前active72时绑定JSON必须是精确`{owner, run_id, go}`，其中owner含pid/create/exe/argv/root、go含真实learning_started_epoch。**没有历史owner/CNone/balance默认值**。参数缺失只在实时AUTH读到CNone时可能通过；active但未提供known则原AUTH拒绝。源码没有填107当前状态。全程只读原72 finite authority，不拿owner写锁、不Cwrite、不新GO/第二writer、不复制canonical或恢复旧210 budget。

目标未创建：`/mnt/mod4_linux_durable_20261013/MOD4_W35_PROFILE_ENV_DOMAIN_PANEL_20261029v1/w35`。PRE要求其parent不存在，expanded mount UUID `EF3105C85DD986BD`且rw；不是空目录覆盖规则。若目标已存在或任何guard失败，保留原错误/partial并停止，不重跑本once、不cleanup。入口消费marker在网络前独占创建，失败不重置。

源与部署图：

- `TARGET_INSTALL_INPUT_MANIFEST_UNUSED_v1.json`：469静态输入。465项从已成功210 V3旧namespace复制；4项小overlay为新worker、新supervisor、未改telemetry组件和新静态Task输入。**不从本机上传模型/NPZ/USD**。完整local_path/bytes/producerSHA在manifest。
- `LOCAL_TARGET_INSTALL_CONFIG_UNUSED_v1.json`：精确CODE SHA、manifestSHA、新旧root、旧closure/witness模型索引与pending规则；所有CODE在调用前本地SHA+AST核对。
- 旧成功root：`/mnt/mod4_linux_durable_20261013/MOD4_W35_ADAPTED92_FULL_PROFILES_OWN_STORAGE_20261029v3/w35`。COPY先绑定其完整原terminal SHA、sup1595689/worker1595703的记录创建时间/身份与原wait0/private-release/1200完整执行，读这些**已知own**的proc stat判断out，PID复用不查其argv。没有unknown PID调查或信号。
- 源SDK报告SHA `18e1c1e3048cc1fb34818add290159f2fdb43fc4da6db3a5e42317bb3484b1bf`；原wholeCPU witness SHA `c633a5eb9f091c6d6b2327ae86b3d0b61d25c1b43964b20d875567f97c692442`。witness中的`model.SHA`才是adapted92 final78：`ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f` /17619013B/17Adam648360；witness的顶层source_SHA368259…是原PPO源，不混用为本新模型SHA。
- 小输入逐字SHA+size复制；PT/NPZ/source700USD只建新readonly input hardlink、核same inode/size/mtime和既有producerSHA/旧完整资格，不重读/rehash大内容。RUN再次核这些inode/stat、small source SHA及exact wholeCPU witness。原GPUworker的H(source)==modelSHA与完整CUDA runner restore依然保留，不能用本metadata阶段替代实际模型内容/状态验证。

严格静态/动态分离：旧600-source包中的Task映射在本NEW安装manifest明确修正为静态`PANEL_SOURCE_TASK_TEMPLATE_UNUSED_UNADMITTED.json`（三准入布尔false、known72=null）。CPU metadata通过后，从它构造**新的**动态`FROZEN_CASE_TASK_TEMPLATE.json`；supervisor拿privateEX后写**新的**`FROZEN_CASE_TASK.json`。静态manifest/Task bytes不改写。不能把旧未执行manifest V2的Task部署basename拿来覆盖此选择。

已复用的原成功守护：

- `AUTH72_CURRENT_KNOWN_OWNER_READONLY_CODE_v1.py` 与 `PRE210_UNUSED_MOUNT_LIGHT_RESOURCE_CODE_v1.py` 为实际成功V3原literal逐字相同。原generation/finite mode/strict remaining>86412.86069250107、2268000s/9历史/newextensions[]、真实active known owner/GO绑定保持；不写账。
- GPU937 light policy：free>15669MiB、util<=30，compute apps仅query gpu_uuid，第三方保持；privateEX、RAM32GiB、disk25GiB、mount/free重新实际读。PRE不宣称拿到privateEX，只有原supervisor实际取得原GPU私锁后才置private字段。
- 同一已有授权compressed-memory/strict210 transport、原host pins不改。凭据只恢复到内存、不argv/文件/报告。72连接关闭后才开210；结束finally关闭当前连接并还原transport session。local进度线程25秒只输出本finite阶段，不新开watcher。各phase原cap30/30/90/120秒，caller总300秒边界前不足就拒绝进入后续phase；不自动retry。
- RUN的exact Torch2.10.0+cu128/Sim6.0.1.0/Lab6.1.14/RSL5.0.1、全部RSL source SHA、SDK math SHA、asset/import_contract路线、USD400N对应stiffness2000/damping3/upper limit等原guard保留。没有CPU模型decode：报告scope明确“source/SDK/USD metadata + exact historical wholeCPU witness”，不是一次新全模型CPU证明。
- CPU阶段HOME/TMP/XDG/cache/state/Torch/CUDA cache均只指向NEW root；原库路径不改。原worker的N1成功Kit datastore/user.config新自有路径与cooking布尔/worker16原样；不删改旧cache或全球配置。没有pip/安装/软件升级。
- 原supervisor只再次替换worker basename，privateEX/轻占用/资源/own1800s wait/30s terminate/15s exit及noCwrite均保留。原worker1680s、mean、N20K/G3、独立nearest250 bank34、D1-D7/RNG/queue、STD/17Adam648360/LR `.00011390625000000003`、400N/2.5ms/TGS32/4/50Hz×8/feedback100Hz及模型/norm/optimizer literal检查保持。

新实际first24正证明：选定worker是`evaluate_W35_adapted92_profile_env_domain_panel_UNUSED_once_v2_queue_receipt.py`。相对上一已冻结worker只多记录adapter.calls baseline、在control24核实际delta并发布独立`frozen_regression/ACTUAL_NATIVE24_W35_PROFILE_PANEL_CLOCK_QUEUE_ACTUAL.json`：

- controls24 /physics192 /feedback48；原每control8/2的真实计数assert照旧。
- `queue_apply_calls_per_group == {'legs':192,'wheels':192}`，保留真实start/end累计值。
- `actual_first24_trace_controls == [1..24]`；原telemetry每control对两个group真实tick序列各0..7已核，不只由源clock公式代算。
- 绑定source模型SHA、新worker/component SHA，继承真实fullrestore/D1-D7与无optimizer/norm更新约束。

**任何first-reader必须同时要求这个新panel回执、旧原fullrestore/native24回执以及无原error。只有旧native24或detached返回不能判新telemetry通过。** 本轮没有执行first-reader。新600controls/100warmup/500steady覆盖与逐profile/逐env统计仍需实际窗口；未覆盖/无原技能阈值保持pending，不能把600覆盖当毕业。trace不是pack127/完整force/torque转移集，`complete_WM_dataset=False`；没有旧模型来源提升。

实际入口返回（未来才存在）：

- `reports/PANEL210_SOURCE_SDK_METADATA_AND_FINITE_DETACHED_RETURNED_ACTUAL.json`，只表示metadata准入+detached身份，actualGPU/native24/profile coverage仍pending。
- target `ACTUAL_SOURCE210_SOURCE_SDK_CPU_NO_MODEL_ADMISSION.json`、`ACTUAL_FROZEN_W35_FINITE_SUPERVISOR_DETACHED.json`、原stdout/ownidentity/error/terminal。新first24路径如上；正常终态仍为`FROZEN_W35_ORIGINAL_WAITED_TERMINAL_ACTUAL.json`，原`frozen_regression/BOUNDED_FROZEN_W35_N20K_PROFILES_ACTUAL.json`的requested_controls改为600。
- 未来要新purpose只读first/terminal reader绑定该次实际sup/worker身份，不能复用旧consumed once或5分钟反复poll；本轮不提前做未知身份reader。

本轮验证：source builder返回0；9个Python/remote snippets AST通过；5个stdlib Task正负例通过（原模板、wrong model、两种authority false、wrong worker source），只执行抽出的纯Task构造段，未调用AUTH/PRE/COPY/RUN、SDK、网络或worker。synthetic authority明确不是canonical。静态source bytes不变、未写动态grant文件；模板仍false/null。源/回执在`SOURCE_AST_AND_SYNTHETIC_TASK_BINDING_ACTUAL.json`与`SOURCE_DERIVATION_EXACT_INVERSE_AND_METADATA_MAPPING_ACTUAL.json`。

所有上轮错误保留并通过前scope INDEX `377ae5af5bc78d1117b61f1339b14ef7343f3dc884438a504698bb05b3ea0ada` 引用，不复制成成功或覆盖原V1。本轮source无新失败。全部文件由root普通Git补档，未创建trial/tag，未声称已remote记录。当前目录source冻结；实际reports未来只能追加并普通补档。本任务到此idle，不拿lease、不执行下一项。
