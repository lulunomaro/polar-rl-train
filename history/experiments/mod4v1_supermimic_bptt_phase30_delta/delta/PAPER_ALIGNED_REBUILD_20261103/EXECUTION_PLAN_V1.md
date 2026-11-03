# MOD4v1：按论文闭环重建的执行顺序 V1

2026-11-03 15:46 +08:00，直接按用户15:38“重新搞goal开始按照你说的顺序推进”。持久Goal `goal-1c14ef7d-c888-4287-83bf-c008d54545fb` 已从revision13改为**14，active/armed**；不是只改显示todo。原历史全部保留，最终原技能80/90与独立鲁棒性/保持仍是验收，不为约3000更新凑数。

## 当前正在做：阶段1

已经启动两个独立SOURCE实现任务：

- `cffddedf-0c4e-4a0f-bffd-8b2d48a6785b`：[source_phase1_state_context_partition_v1](<../source_phase1_state_context_partition_v1/>)，以bridge/实际worker及八角色已出版STARTUP/context_layout为依据，逐字段划分static DR、dynamic actuator/feedback queues、sensor clean/noise、command clock/phase、actor-visible/WM-only/unknown，交schema、验证模块、CPU合约和缺件清单。
- `0ad8300a-6e15-43f7-ad90-657780f697bf`：[source_phase1_passive_sensor_capture_v1](<../source_phase1_passive_sensor_capture_v1/>)，沿真实100Hz feedback活链设计可执行bounded tap。五反馈通道原调用输入value本身是已计算clean；原sensor.cache存已用noise，原delay cache有cursor/out/sample_tick。优先用实际实例method包装、原函数只一次/返回identity不变，不重新抽噪声、compute obs/clean_policy、step/reset或SDK getter。

父已实际读取原sensor_a0_runtime、feedback_delay_runtime全源，并向实现者指出`clean_policy()`会临时toggle/compute_group，**不作为被动捕获方法**。当前新物理窗口/新GPU训练尚未启动；先在真实source+CPU合约中排除额外调用和时序错误。

### 已有source事实，不冒充现场验证

- 原physics400Hz、control50Hz：每control8个physics子步，原scene.update每4个physics子步采一次反馈，因此是mid/end两个100Hz采样，**不是每8子步才采**。
- 实际八角色layout都已观察：E0/E2 context117、W35和四E1角色119、E3 context122；只有E3/W35有非零A1训练，其余六actual0 complete capture不叫训练。
- raw35[0:35]已经带噪声/延迟，绝不是clean。旧bridge只有feedback lag标量，缺真实feedback FIFO/cursor、100Hz mid/end clean/noise-used receipt。
- 目前原管线可暴露的是clean反馈16维（gyro3/gravity3/legpos4/legvel4/wheelvel2）及实际noise/bias/queue；**中间时刻完整clean35原本未计算，仍Unknown**，不逆造19个非feedback分量。后续组合actor35时必须记录原command/height/prev-action/mode的实际clock和source，不能把50Hz端点当前值投射成mid采样真值。
- 原joint_vel_rel减实际default_joint_vel，不默认0；样本body-frame不旋转到apply帧；scale、单位、quat顺序沿实际source核验。

## 严格的五阶段门

|顺序|交付|进入下一阶段前的证据|
|---|---|---|
|1（进行中）|分层schema、原100Hz被动采样/新回放接口、old/new source绑定、UNKNOWN字段|stdlib+真实Torch CPU；原函数call-count/RNG/queue mutation顺序/返回identity；原资源准入下最小实际capture；2samples/control与actor raw35不变证据。仅clean16有receipt时只声明该范围，不宣完整clean35。|
|2（等待1）|同k8 predicted state/dynamic context上的state+learned reward/cleanobs/done训练与校准|future真dynamic xi不teacher-force；原noise/lag可推演；terminal pre-reset/invalid/cut/完整checkpoint与梯度数值/缓存守恒通过。新schema不得切旧Adam或计数冒resume。|
|3（等待2）|地形可识别性、E2原body/world指令、phase/resample、timeout/bootstrap|保持原任务/阈值的source与实际时序；WM/critic补信息不泄漏actor；未知不补猜。|
|4（等待3）|critic尾值、残差support/饱和、合法start与H16/32单因素|既有gamma/lambda/clip/Adam/softsurvival正确项保留；不同时混bound/anchor/reward/H/容量；不因H更长假定更好。|
|5（等待4）|1–2角色有限实际BPTT段→完整save/close/wait/结算释放→独立冻结复测|原predicate/完整分母/多seed、moving/stand/normal/recovery分开；坏则停保母，有证据才扩量。updates/loss/RC0/SOURCE/CPU非技能验收。|

可并行仅source核对、独立测试或不修改policy的原teacher保持评测准备；**阶段1的真实接口门未通过，不放行阶段2候选native训练**。好C878/S135的独立seed保持source已封，但尚无新native materialization/dispatch，不偷把source测试当已测保持率。

## 冻结边界

- H1、Registryv12及所有母本/候选/失败保留；E3 dense upright仍disabled/κnull，零更新bound没收益不晋级，badlegacy不续跑凑数。
- 原2c/bae/400N/k2000/d3/50Hz控制100Hz反馈/.0025/TGS32,4/.01闭链/.01mimic/全D0D7/速度/原接受不改。
- 原canonical唯一writer、两authorityEX、GPU私EX、train有限SH/eval有限EX、reserve86412.86069250107、3900/3600/300/1800保持；共享低compute不越过项目锁/owner，不清外国锁/发signal、不扩预算/退款/造账本。
- 每阶段新source/purpose/manifest/真实receipt；旧封件不热补，不为Git/标签重开模型/raw或重放旧once。feature独立annotated trial归档全部失败/未知，main仅读。

本执行计划表示**已开工阶段1，不表示阶段1通过、已开始新BPTT或最终80/90达到**。父接下来review冻结模块→真实Torch CPU验证→最小原SDK接口窗口，再按门推进。
