# Full DR数值重置：先前solver归因的核对

2026-11-10，Asia/Shanghai。此阶段只读采集，没有GPU探针、训练、参数更新、停止进程或修改生产源码。所采集另一聊天正在运行的run不归本聊天控制，状态只描述采集时刻。

## 结论

目前确认的是full DR下大量单环境数值安全重置，不能直接叫PhysX进程崩溃。打开enable_external_forces_every_iteration有官方速度积分依据，但“1539降到4就证明根因是随机外力”不成立：两者暴露时长不同，且一迭代尚未覆盖随机外力事件。只提高scene最大velocity迭代数也不等于提高robot实际迭代数。

## 原始对比的时间轴

父checkpoint iteration15279，rollout24，policy dt=.02s，一rollout每环境仿真.48s。

|采样点|iteration|新增rollout|每环境累计仿真时间|numerical累计事件|
|---|---:|---:|---:|---:|
|原run被引用1539那条|15300|21|10.08s|1539|
|solverfix单迭代probe|15280|1|.48s|4|
|solverfix主训被引用769那条|15288|9|4.32s|769|

1539不是一个迭代的数量。769那条时长仍短于源码中每reset后首次5–10s随机外力timer。关闭FULL_DR_EXTERNAL不仅关闭wrench，还跳过timer、随机数消费、速度push与每步写入路径，所以单迭代on/off即使不同，也不能直接归到非零推力。

4env的有效r2probe也只是一rollout，并且该probe代码会执行一次algorithm.update（最后才按mode==probe退出），不是固定策略长时物理验收。4env r1甚至因iterations上限不超过恢复iter而未执行更新/rollout；不要把两个4env探针合并描述。4env无失败只说明这四个初始样本在短暴露里未触发安全重置，不能区分样本尾部、reset交互、时间累计、PPO变化和环境规模影响。

## numerical与统计口径

scut_flat_env.py::_get_dones: 非有限joint_pos/joint_vel/root_state，或active joint |qd|>500rad/s、root |angular|>200rad/s、root |linear|>100m/s即numeric。episode重置不等于SDK报错或进程崩溃。769/2218=34.67%是累计reset事件的构成，不是4096环境的唯一失败比例，更不是仿真步失败率；同一环境可能多次重置。进程是否崩溃另查ERROR/退出状态。

numeric_peaks在_get_dones每step被覆盖，训练loop只在rollout结束读取最后一次张量。因此joint_vel_max=354并不意味着整个24step从未超500；先前4次重置可能发生在rollout较早时刻。max_closure_m则在rollout里累计最大，两者统计窗口不同。closure较小与关节数值微分/速度异常可并存，不能用前者否定后者。

## solver改动的实际含义

安装版PhysxCfg规定actor请求迭代数clamp到scene min/max。robot资产仍solver_position_iteration_count=32、solver_velocity_iteration_count=4。只把scene max_velocity_iteration_count=4改8不要求actor使用8；没有实际solver次数读回，因此不能声称4对8已验证。两个4096solverfix/vel8单迭代探针的losses、reward、numeric_peaks、closure完全相同，进一步支持实验变量尚未真正改变。

enable_external_forces_every_iteration的官方含义是TGS每position iteration应用external forces并改善velocity updates，涉及求解中的外力积分，不能仅按字段名等同为本任务随机推力开关。官方来源以IsaacLab v3.0.0-beta2 PhysX Configuration及安装版physx_manager_cfg.py为准；是否发生了特定随机wrench，必须读timer/hold/力值。

## 当前FullDREnv尚保留的已知问题

实际新run profile为flat_robust_full，父SHA0a5d4e43...，全量恢复actor/critic/Adam/RNG；不同于本聊天884cd07b...父的独立physical-delay试验。该FullDREnv仍COM读取当前值再+=，摩擦每组default全量写回覆盖，external hold只有clamp没有递减，动作buffer按20ms策略推进，观测整35维历史延迟。这些源码事实需要修，具体谁引发最早500rad/s尚无首次失败样本记录，不能全部归成唯一爆炸根因。

COM每reset累积还可能形成“失败→更多reset→COM漂移→更易失败”的反馈；这是有代码依据的机制假设，未采到当前每env COM与失败序列，不能当已量化因果。

## 下一项真正可区分原因的验证

不继续长训练。保留同一权重、初态、DR属性与随机数流，在GPU释放后用固定策略做external wrench/velocity push分别开关的等仿真时长回放，至少覆盖首次5–10s事件及reset。逐env记录首次numeric前的episodeage、具体joint与qd、是否非有限、wrench/COM/gas/contact与实际PD目标；同一失败状态可缩成单env复现。若无随机外力时仍在5s前失败，应先查初态、gas/PD、COM/reset和接触；只在非零外力后出现时，再查施力API/单位/坐标/持续期和solver积分。改变solver须改变实际actor请求或scene最小值并读回，不靠max字段推断。

报告只确认已有证据与下一项辨别性验证，未承诺唯一根因，不提高任何终止阈值。

## 采集证据

REMOTE_SNAPSHOT.json保存8个实际job现存JSON、启动收据、4份源文件文本及原始SHA。动态job按captured_utc冻结，不称final。HISTORICAL_PROGRESS_EXTRACT.json仅从已存在原聊天function_call_output提取被覆盖的1539与769两条数值，未重建原始文件。其他失败试验由原owner继续保存，本补充不宣称拥有其完整轨迹。

源码副本采集时发生过Windows换行再序列化错误；已从REMOTE_SNAPSHOT恢复原始字节，4份源码SHA与原路径读回一致，语法解析通过。详见COLLECTION_NOTE.json，不把本地采集错误归到训练程序。

## 上游资料与版本范围

安装元数据读回：IsaacSim6.0.1.0、IsaacLab6.1.14、omni.physx110.1.13。官方PhysX配置说明确认external-every-iteration用于改善TGS速度积分，scene min/max是actor次数的夹取范围。官方仓库issue553另报告在部分GPU版本开启此选项、发生articulation睡眠/移除后，active-index映射可能串用别的articulation的关节力和重力；公开复现版本为IsaacSim6.1.0/omni.physx110.3.2及PhysX5.11源码，不与本机版本相同。此条只作为有条件的上游线索；本轮未读取sleep事件/核验GPU二进制，不宣称本机命中，不因此自动关闭开关或升级。
