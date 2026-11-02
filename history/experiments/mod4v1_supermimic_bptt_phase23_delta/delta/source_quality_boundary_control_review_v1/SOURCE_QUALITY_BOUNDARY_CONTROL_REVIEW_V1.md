# 质量优先的原完整保存边界：SOURCE-only 审阅 V1

**结论：源码具备这条条件控制链，但没有无 race 的原子暂停 API。** 若唯一一次 SIGINT 实际在原 owner 正常调度 try 内被外层 BaseException 捕获，且所有已启动孩子已登记到 slots，则走既有 STOP_AFTER_SAVE → 原全保存/关闭 → actual wait → account(end) → finally unlock。保留 KeyboardInterrupt、parent error 和异常分支 row.original_error=True；owner RC0 也不是 cohort execution success。本审阅未核验任何活进程、C 或信号投递；所有运行条件仍待父代理现场核验。

- catalog 已检查：Office/ACL 与本任务不匹配；仅 read/glob/grep/已有 Python stdlib，未装依赖。
- 仅写本新目录；旧封源/active owner 均未改。没有 SSH、C/PT/raw/SDK/GPU/Git 或实际信号操作。
- 父给出的目标条件为 PID=1490574、Linux startticks=137458072；它们是待复核输入，不是本审阅的 live 证据。

## 1. 可核对的原链

1. [owner:41–44](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/supermimic_original_owner_shared_app_close_candidate_v5.py#L41-L44>) 初始化与 stop helper；[owner:83–96](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/supermimic_original_owner_shared_app_close_candidate_v5.py#L83-L96>) 保存原 traceback，向全部当前 slots 写 STOP，等待每个原 Popen.wait，调用原 semantic，再结清、释放。except 不重新抛异常，所以自然进程 RC0 仍可带真实 KeyboardInterrupt。
2. [worker:89–108](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/worker_supermimic_bptt_app_close_candidate_v5.py#L89-L108>) STOP 文件仅在 before_action 检查；WindowSavedStop 被专项捕获，finally learner.save() 完整保存，再核验参数/teacher 后写真实 FINAL，走原 bridge/env/App 关闭。它不等价于直接打断孩子，也不承诺即刻响应。
3. [core:305–320](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/ctx_reward_full_resume_candidate_v2.py#L305-L320>) 的 hook 在下一 action 前、history/norm 更新之后；[core:563–616](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/ctx_reward_full_resume_candidate_v2.py#L563-L616>) 的 WM/policy/periodic-save 中没有该 STOP 检查。保存真实 pending_iteration 和计数，不宣称恰为整次 iteration 边界或 PhysX bitwise warmstart。
4. [owner:16–20](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/supermimic_original_owner_shared_app_close_candidate_v5.py#L16-L20>) 结清要求 set(go)==set(rows) 且全部 terminal，并把实际 rows 放入原 completed_segments.actual_terminal_rows。[common:23–33](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/three_slot_common_v1.py#L23-L33>) 对每个 GO 计费至 owner_received_terminal_epoch；没有取消训练量退款或提前停止计费。
5. [contracts:95–149](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/resume_runtime_contracts_v3.py#L95-L149>) 明确完整 finite save 可 target_reached=False；[App gate:413–467](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/app_close_semantics_v6.py#L413-L467>) 仅在 actual wait 后核验全部原 FINAL/error/close 条件；严格 fast-close intent 只替换唯一缺 post-close lifecycle 理由，不豁免其他错误。

## 2. Race、硬阻碍与停止条件

- **身份/范围 TOCTOU：** exact PID/startticks、argv/cwd/source SHA、C.active_segment.owner_parent_pid/owner_run_id/authority_generation、两名原 child PID/startticks/job/role_key/GO 必须最新一致。快照与 Python 接收信号之间仍有时间差；both alive、远 target/deadline 仅降低风险，不提供原子屏障。
- **GO→Popen→slots 未登记窗口：** [owner:71–77](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/supermimic_original_owner_shared_app_close_candidate_v5.py#L71-L77>) 先发布 GO，再 Popen，最后登记 slots。落在此处可能出现已启动却未登记的孩子；inner except 的 returncode=1/terminal 标志本身不是该潜在孩子 actual wait 的证明。出现新 GO、第三 child、GO/slots/terminal 集合不闭合即停本次计划及后续 eval。
- **正在异常/settle/finally：** 不向 83–96 清理段、81–82 正常结清段再次投 SIGINT；一次投递后不重发。第二次中断或 I/O/account/semantic 故障可能跳过后续 wait/结清；except 清理没有独立超时或升级 kill API。挂起则保持未结清/unknown，不释放后假称完成。
- **信号可被内层吸收：** [contracts:80–114](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/resume_runtime_contracts_v3.py#L80-L114>) 等 BaseException 保护可能把 SIGINT 记为 read/presence error，而非进入 owner 的 83 分支。需看到真实 owner traceback/STOP/terminal/结清链，不凭“已发送”推定成功。
- **保存时耗/状态未知：** 必须真实 startup 已到 learner、进度新鲜，且距 save_deadline、nominal_end、target 与 reserve 留出足够完整 save+close+wait 时间。源码没有“near”的数值定义，阈值需父用最新速率和实际保存耗时判定；陈旧/缺失数据、孩子正在 save/close、已有 worker error、非预期退出均停止计划。STOP 在下一 collect/action 才响应；SDK/WM/save 卡住仍可能永不返回。
- **清理标志分离：** OWNER_EXIT 的 all_own_children_waited/original_cost_settled/original_leases_released 三项必须同时为 True；仅 slots 为空或退出文件存在不够。原 finite/private 锁在新评测 admission 实际取得前，不宣称资源可用。
- **非指定父单 PID/信号：** 不向 process group、child、kill/terminate 路径发送本计划信号。原 Popen 使用 start_new_session=True（75）；PID 复用、身份不符、pending 六角色任何新 GO、评测入口未 ready 或 phase 不明，均保持当前任务自然路径。

## 3. 缺原 sidefile 时的 NEW 微批 admission 证据（只定义核验，不实现）

异常分支 88 **没有**写正常分支 65 的 PARENT_WAITED_ACTUAL，也不写 82 的 COHORT_FINAL。保持这些缺件，不合成、不回填。新 purpose 可写自己的 QUALITY_BOUNDARY_EVIDENCE，但不得给它旧 sidefile 的身份或声称旧 cohort 成功。

最低交叉核验：

1. 父保留投递前的计划控制事实、唯一目标 PID/startticks/run/source、一次信号时间、已知两个 GO/key/child 身份和六个未 GO 角色。此记录本身不是 actual wait 证据。
2. 原 OWNER_ORIGINAL_ERROR 真实包含 KeyboardInterrupt；所有其他 parent/child 错误原样保留。原 OWNER_EXIT.run_id 对应同一 run，三 closure 布尔项均 True。其 runtime 身份须绑定投递前 owner，而不是只有可复用 PID。
3. **原 canonical** active_segment 已空；同 owner_run_id/owner_parent_pid 的 completed segment 有真实 ended_epoch 和 actual_terminal_rows；rows key 集合等于该 run 的所有实际 GO 集合，且 pending 六角色仍未 GO。逐 row 核 terminal_all_own_children_waited=True、原 returncode=0、owner_received_terminal_epoch、role/key、semantic_result.actual_wait_returned=True/passed_execution=True/original_error=False/reasons=[]。
4. 异常分支 row.original_error=True 是原 owner 无条件赋值，必须保留；将它与 child semantic.original_error 分开，不擦成 False。逐 child 的原 FINAL passed_execution、A1 family/view/run/role/key、九 producer counts、own完整 checkpoint receipt、teacher/参数审计与原 close/严格 fast-intent hash 证据均匹配 rows.final。真实 child error、坏 close、无 FINAL、无实际 canonical terminal rows 一律不入评测。
5. 原 cost 按 GO→原 actual wait 的 terminal epoch 结清；started/ended/accounted_through/charged_expert_seconds/各 expert duration_bound_passed 与原 3900s 上限等一致。无退款、无暂停计费、无 C 改写。新评测另行取得原 finiteEX/privateEX、走新的 subset schema；只选择这两个真实完整 producer，不把未开始六角色写成 SDK0/count0，也不伪装八角色覆盖。
6. subset 证据仅表示“这两个真实 producer 已原样完整保存/关闭且可进入新效果验证”。**parent/cohort interrupted/error=True、execution success 不成立；skill pass/整体 8角色通过率仍 null。** checkpoint 本体由后续封版 cache 各角色一次 bytes/hash/decode 验证，本审阅没有打开 PT。

## 4. 本地静态验证

8 份小源码 SHA/bytes 与封版 PIN 一致；12 项原路径及7项 cooperative/zero-replay 分支的 stdlib AST/字符串结构核对 PASS，Torch 未 import。初版临时 checker 因 CRLF 分隔触发 `IndexError: list index out of range`，仅在内存规范换行并改用 AST 后全部通过；原源未改。这些结果不证明当前 owner 的 frame、信号交付或实际保存关闭。精确 PIN 与 runtime 必核字段见同目录 JSON。

## 附录 A：OWN-only STOP → 验证 → INT → CONT 的更强协调设计（未实现）

**改进仅有条件成立：** 已确认 parent 整个 thread-group 真正停止后，parent 不再向前走 GO→Popen；若此时能证明它在正常调度 sleep80，而不是启动/异常/结清段，再排队一次 INT 并 CONT，可让既有 Python handler 在恢复后走原清理。子进程持续运行，原绝对 deadline、成本时钟和锁持有均不暂停。

必核与剩余问题：

1. **停前身份与止损：** exact PID/startticks/Root/argv/exe/owner-source SHA/C generation+run+PID；唯一协调者，原父非 T/t；两名正确子 PID/startticks 状态非 Z/X、GO全集恰为2、六 pending 未 GO；原 latest_complete/fullsave 真实 metadata，已有 child FINAL/error/close 则退出本次 INT 计划。控制器须预先具备有界、独立的 exact-identity resume 保障；仅自己的 finally 覆盖不了控制器崩溃、断链或自身强制终止，缺保障则继续自然边界。
2. **停后真实观测：** 重新绑定 same PID/startticks（优先稳定进程句柄绑定，但不改变信号/调度策略）；所有 /proc/PID/task/TID 的 state 均 T，而非仅 leader。验证架构/ABI 后才解释 syscall：x86_64 的230=clock_nanosleep，35=nanosleep，不将35称为clock_nanosleep。SIGSTOP 后可能显示 restart_syscall(219)、-1、running 或访问错误；本轮不猜内核行为，任何这些结果均无可判定正常 sleep 证据。syscall snapshot、本机 monotonic 停止耗时和任务集合都需记录。
3. **定位原正常 sleep：** syscall 编号不证明 Python 源码位置；原57是 preGO30秒、80是正常3秒、90是异常清理3秒。结合正确 Root 下原 OWNER_ORIGINAL_ERROR 缺失、源 PIN、当前 active owner、全部两个已登记非 zombie 孩子/GO集合、真实新鲜状态来排除57/90；OWNER_CURRENT 的旧 slots 只是历史快照，不是内存 slots 或 Python frame 实证。位置排除仍有缺口，就只恢复，不排 INT。
4. **SIGINT disposition 是独立硬门：** 记录所有线程 SigBlk、SigPnd/ShdPnd，进程 SigIgn/SigCgt；排除继承后台启动 SIG_IGN、阻塞、既有 pending INT 或其他控制信号。CPython 默认 handler 也受继承 disposition 影响；SigCgt 的 bit 本身不证明实际 handler 会抛 KeyboardInterrupt。没有实际 source/runtime handler 证据，则不将 STOP/CONT 当作修复。未验证信号 handler 的情况下，可能只是恢复后继续调度而没有原 STOP 文件。
5. **停后状态会变：** 子进程未停，可能越 target/deadline、自行保存/报错/退出。必须紧邻 INT 前再核两个子身份活性、count/时间余量、GO和error/FINAL/close集合、C owner和停止总时耗；新增 terminal、unknown、过时进度或未匹配的新 GO 全部撤回 INT 计划。已有 fullsave 是回滚材料，不替代本次清理后的新 FINAL/全保存证据。
6. **恢复语义分阶段：** 只有“由本协调者已经停住”的同一 exact owner 才应被本协调者恢复；预先已停/追踪停或 PID复用的对象不接管。INT 前任一未知→恢复 own stop、无新 INT；INT 已排队后，CONT 是送达/退出 stop 的必做项，后续未知不等于可撤销 INT，也不等于恢复正常训练。只一次 INT，不重发，不向组/孩子发信号。原 pending 信号也可能在 CONT 后触发，须原样保留而非认作本次成功。

本设计没有实现调度器、信号操作、内核实测或独立恢复器。四项硬门为：可确认的正常 sleep/全部线程停止、实际 SIGINT handler、停止期间仍满足的两孩子/GO/余量、有界失联恢复。任一缺失，保持自然完整保存边界；任何后续评测仍按§3原 FINAL+原 OWNER_EXIT+原 canonical terminal rows 核验，不合成旧 sidefile，也不把计划 KeyboardInterrupt 写成 execution success。

## 附录 B：只用原 STOP 文件、全 owner 自然结清（当前父优先路线；未执行）

**所查 worker/core/gate 没有 zero-replay/zero-count 的源码硬阻碍；但“几分钟 bounded”没有源码保证。** 对本 owner 已核身份的8个原 job_root 使用原 `J/STOP_AFTER_SAVE.json` cooperative 请求（pending先于active仅是发布顺序，不是原子停队列），保留原因和请求时间，原父继续按原队列、资源、wait、account、finally运行。没有信号、没有暂停原锁/成本时钟，没有新调度器；本审阅没有写任何 STOP。

- **第一训练 action 之前：** [core:305–324](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/ctx_reward_full_resume_candidate_v2.py#L305-L324>) 的316–317 hook在318策略forward、320 env.step、324 replay.add之前，但history/norm已经更新。fresh train 的[563–570](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/ctx_reward_full_resume_candidate_v2.py#L563-L570>) 在WM/policy iteration前先collect warmup；预置STOP在第一hook触发。不是“纯未触碰norm”的快照，更不是SDK0步；原SDK构造/reset/teacher首次读取和learner/GPU/replay分配全部仍发生。
- **空 replay 与0 optimizer counts：** [export/import:116–125](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/ctx_reward_full_resume_candidate_v2.py#L116-L125>) 导出完整容量所有tensor，size=0允许；[checkpoint:493–511](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/ctx_reward_full_resume_candidate_v2.py#L493-L511>) 仍含完整4模型/4优化器、replay/history/RNG/environment metadata。训练采样函数拒空不影响此路径，因为WM/aux/policy训练尚未进入。
- **真实保存与semantic：** worker95–98捕WindowSavedStop、finally保存并写stop=True的原FINAL；[count/gate:71–149](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/resume_runtime_contracts_v3.py#L71-L149>) 允许非负九counts、target_reached=False，不要求>0；App230–254同样无>0门。原teacher/参数审计、所有错误与close gate仍须通过，已有STOP不豁免这些条件。fresh且第一hook前STOP成立时才有0增量；resume状态、此前已GO、发布竞态或已发生动作均以真实producer计数为准。
- **父不跳过pending：** owner58–80仍会逐个admit/GO；source/unusedjob gate不检查STOP缺失。正常路径65原wait/原PARENT_WAITED →81原结清→82原COHORT_FINAL→96原EXIT，证据比异常路径完整。67的真实semantic error会blocked后续；70/79的reserve门也会留pending，因此不预称八个都完成capture，更不把实际未GO六角色补成0训练。
- **成本与时效：** 完整N1024空replay仍保存完整容量，启动/teacher/GPU/写盘/close成本真实计入；STOP不在构造、WM/policy、save或App.close中轮询，owner63只继续请求STOP，没有强制有限分钟超时。卡住/写盘失败/close失败照原错误与未结清状态处理，不为早验而热改、删错、退款或强杀。
- **标签：** 六个fresh pending若实际完成0更新保存，应称 `quality-boundary frozen-baseline capture / zero-update fresh`，不是已训练、已评估或skill毕业；normalization/初始化/实际物理构造也不称0。只有真实成功FINAL+全保存+原wait/结清/锁释放后，新的E3+W35 subset评测才走独立原N80/配对同protocol验收，整体八角色效果仍待测。
