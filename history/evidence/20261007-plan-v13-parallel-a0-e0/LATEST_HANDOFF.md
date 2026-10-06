# MOD4 v1.3 实际双机并行交接

用户明确要求4090开训、3060并行评测，并要求改入plan。主计划v1.3 SHA d7a2447ddb3cf215022ba552022f3dba6d275e2f74baeca2c6b85be7cd595413；v1.2整体批准与原发布任务保留，当前仅执行顺序修正，不新增预算/任务/DR/接口/硬件/reset范围。

4090学习根A=/home/egde/rl_candidates/MOD4_MOE_A0_E0_PARALLEL_20261007，实际source F167原runtime逐字一致，只加计划合同/新controller/明确状态reader接续。S1 CPU专家35/38/6/std/optimizer/不同存储和梯度隔离通过，E1只是候选，MoE和history尚未训练。S1A当前A0 E0单帧从23509 SHA2f82374fe07a849dbbaeabbf8dd34b20d0df8da789f2ebc2be3e688a1b24498a完整恢复，20k×24、KEEP_STD1、white_v3/world.5/pure4pi，F原nativePlane、reward、硬件和全部runtime保持。不是继续覆盖mixed权重。

唯一trainer670475/start46556747，实际observer671176/start46570338、guardian671219/start46570403独立。PID只是定位，后续真实/proc/自己manifest/latest_complete/runfreeze/active优先。原supervise_plan_a0.py已执行，启动训练/登记active后status重复budget_seconds导致原父670429退出；原错误A0_ATTENTION/state.reason保留。新的observe_active_a0_review_once.py明确在两原锁下接同一实际trainer，新guardian先启动，原670474明确退休。预算未清、未结尾段、未双开或停止重启trainer；status合并重复键合同通过。当前active持续正常计账。这个reader是当前监督入口，不重跑原controller/launch/adoption或任何旧once。

原deadline1791313088.677045约北京时间02:58:08，首块45min。02:22实际新PID自己的23525完整保存SHAff23210507d81f379e1e5cf7133ee825437f45470163d85417ff25e5a8123a39，actor/critic/optimizer/std/iter CPU68浮点有限，171 run freeze与自己的manifest精确核验。新策略尚未回放，不以保存宣称改善。保存后A0_SAVED_REVIEW_READY索引须实际完整checkpoint及自己的退出/active结清。observer定期核对PID/start并计账/冻结，每5s本地；guardian15s保护，父异常先同PID保存，不盲清active。源23509/23621原best与所有失败候选保留。

3060继续原v1.2发布S0E六份任务，原job/version/SHA不改。ROOT E=/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007，D:/MOD4_async_eval worker28668，read-only artifact bridge与CPU结果reader664155独立。初态/参数/功能校准完成前结果不冒充正式新平台能力证据，但不再阻塞4090本机已验证范围学习。原S0E reader可能最后把EXECUTION_STATE.phase写成校准saved_review，这一缓存phase不能掩盖A0实际active；优先EXECUTION_TRACKS学习指针/A0真实state和proc。

下一步从实际完整A0保存登记冻结评测需求；S1A A1/A2需CPU/SDK history/reset/time、Body速度监督/clean critic和新架构optimizer合同，从相同原23509做匹配更新量对照，不能从已额外训练A0取源或先扩DR。A0学习计入S1A总6h；新接口PPO必要预检弃权重同账。未实现encoder/gate/新DR执行器时不能声称已开训。正常同阶段训练与有效3060回放重叠，切科/扩范围等待对应实际证据。

唯一canonical已828000秒230h/六扩展各一次；本次新增预算0，剩余实时扣active尾段。加载/学习/保存退出同账，冻结回放不计学习。不重跑100h或原尾段，不新增账本。mod4-10每2h静默巡检，读取v1.3计划及actual并主动推进批准范围；不小时/5min SSH/ping、不新开Rich。真实新部署/修复/阶段结果唯一Git annotated trial核验main/tag；二进制/轨迹只SHA，凭据不归档。
