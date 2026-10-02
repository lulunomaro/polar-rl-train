# MOD4 追加 10 小时与直线提速修复交接

## 当前授权与目录

用户明确要求：预算再加 10 小时，先增加预算再修复。预算账本已先写入 budget_extension_20260930.json。原截止 2026-09-30 04:33:53，加 36000 秒，新截止 **2026-09-30 14:33:53 北京时间**。不要再次把 10 小时加一遍。

生产工作区：/home/egde/rl_candidates/MOD4_scut_speed_repair10h_20260930
原工作区保留：/home/egde/rl_candidates/MOD4_scut_continue10h_20260929

## 已实施修复

1. 新监督器先接管原 trainer，记录新预算，原 supervisor 168002 停止，原 trainer 169956 保持工作直到完整保存边界。
2. 新目录复制代码，原 USD 和资产只读引用。RM_GYRO_CURRICULUM=0 使 Mod4EnvCfg 移除旧 gyro_window CurriculumTerm；skills_isaac 同时防御关闭该覆盖逻辑。
3. 每 2400 控制步打印 COMMAND_AUDIT，实际 yaw 指令绝对值必须 <=1e-6。防止配置写 0、运行时被课程重写。
4. 20k env × 24、solver16/4、0.25m 根高度、±1.5m/s、10%站立、奖励/PPO/电机/弹簧/USD保持。DR关闭。完整加载 actor/critic/optimizer/std；不保证恢复仿真状态/RNG到逐位相同。
5. 固定 model_5925 短验收：20env×3秒，全部存活，闭链/耦合通过；128env两轮PPO完整保存5926，运行时yaw=0。短验收不是15秒性能毕业。
6. REPAIR_READY.json 包含代码指纹，监督器验证后请求 STOP_AFTER_SAVE，从新保存的生产检查点续训，不把烟雾测试权重用于主训练。
7. 新监督器每小时异步80env×1500步确定性评测（首次续训半小时后），连续两次1.5范围通过并2m缓变外推安全通过才进入2m。无单次性能失败重启；无盲目物理修改。到点保存与终验。
8. 新监控终端 selected_log 跟随 status.active_log，避免改目录后仍看旧日志。旧监控仅在确认新监控运行后关闭。
9. 评测输出逐环境数据，避免只看到组平均。原晋级窗口90%门槛暂不修改。

## 高速接触调查

旧 contact_diagnostic.py 用理想圆柱 r=62.5mm 算间隙；实际生产 USD /Robot/links/{left,right}_wheel/{left,right}_tire 为 radius=63.7mm、24边/48点、宽20mm的凸包 Mesh。旧诊断不能当准确的绝对碰撞间隙。

contact_diagnostic_actual_mesh.py 从实际 USD 读取轮网格及相对刚体变换，物理子步提取最低支撑点，记录：接触力、连续卸载时间、竖向冲量、相对承重间隙、根高度起伏、支撑点切向速度。最低顶点速度是打滑近似，不是真实接触流形求解结果；网格支撑不含PhysX cooking/contact/rest offset，报告使用绝对和相对承重基线两套间隙。

探针固定 model_5925，8env，0/1/−1.5/+1.5m/s各2env，5秒，1秒后统计并在首次失败截断。它不是15秒验收，不参与自动晋级。

24边轮面支撑半径理论周期起伏约0.545mm；1.5m/s时经过轮面的频率约90Hz，可能与100Hz策略采样相互影响。这是几何推算，不是已证实的因果关系。必须看2kHz数据和隔离同权重A/B才能改碰撞模型。

## 下一位AI按此顺序做

A. 先读 status.json、supervisor_repair.log、train_repair_*.log、/proc 进程、reports。确认只有一个主训练；不要直接重跑有一次性接管逻辑的 supervise_repair.py。
B. 若仍 checkpoint_handover，等 STOP_AFTER_SAVE 完整保存，不手动 kill trainer。若 attention_required，查明错误后从最新完整权重恢复，并保留新绝对截止。
C. 核对新进程 /proc/PID/environ 的 RM_RESCUE_DEADLINE=1790750033.1554604 和 COMMAND_AUDIT yaw=0。
D. 读 contact_actual_mesh_5925.json/.npz，区分真实离地、低力窄脉冲、轮面多边形周期波动和传感器混叠。无法区分时只补隔离测量，不猜因果。
E. 对齐训练范围后保持连续训练，评测比较基线5925和后续同seed。旧1m瞬时54%不证明厘米跳跃；当前1.5m窗口低也不能直接等同离地时间。
F. 若确有碰撞几何问题，冻结源资产哈希，新USD只在候选目录做同权重同seed对照，保证轮半径/宽度/惯量/质量/驱动/摩擦不被顺手改动。确认物理和GPU开销再在保存边界切换。不要把增加多边形数或换圆柱必然当作修复。
G. 2m通过后评估轻度DR。当前该监督器不自动开启DR：新DR候选需质量/惯量/电机倍率/摩擦实际回读、至少2种子配对、2轮PPO、20k材质和内存检查。未通过不可部署。输出倍率不等于力矩裁剪，computed-applied直接相减在DR下会误报。
H. 再适配SCUT Rough跑场。当前reset库flat-only，不直接切地形或加载RMUC；上游Flat/Rough有分支，不是必须逐版本编号线性训练。
I. 氮气弹簧仍3500N/m预载模型，不是SCUT240N恒力；300–700N力-行程未经标定，暂缓该DR。当前是14.22kg底盘，不要改成22kg整车。

## 完成定义

本次交付仅说明预算/课程/诊断修复已实施与如何接续，不意味着1.5m、2m、DR或Rough已验收通过。最终以状态和确定性报告为准。

训练从完整检查点续训；旧策略、日志和模型均保留。预算到点不得偷偷延长。自动化mod4-10逐小时检查，不恢复每5分钟轮询。最终验收完成后停用自动化。
## 阅读入口与交付范围

请优先阅读 snapshot/REPAIR_PLAN.md 和 snapshot/NEXT_AI_TASKS.json，它们包含此次修复、实际部署状态、反例诊断和后续步骤。snapshot/status.json 是打包时快照，实时状态请查目标机。

生产目录：/home/egde/rl_candidates/MOD4_scut_speed_repair10h_20260930
预算截止：2026-09-30 14:33:53 北京时间。

candidate_dr_not_deployed 是此前轻度DR代码的审计副本，明确尚未部署且尚未完成全部运行期测试。它不是当前训练程序；安装器保留旧源指纹，会拒绝直接用于已改代码的工作区。先重新审计，不得删掉指纹校验绕过。

此zip是修复代码、审计证据和接管任务包，不包含全部CAD/网格/检查点或完整可离线运行的Isaac安装。snapshot/diagnostic_assets/robot_wheel32_ab.usda引用远端原USD，A/B未达到部署条件，生产未切换。

32边轮面与固定腿动作两组短对照均未一致改善高速接触，因此保留原USD/动作控制。当前已落地的变化是关闭旧gyro课程、运行期yaw断言、预算监督与逐环境评测记录。

SHA256.json逐文件校验；sync_delivery.py只从环境变量读SSH密码，文件内不存密码。
