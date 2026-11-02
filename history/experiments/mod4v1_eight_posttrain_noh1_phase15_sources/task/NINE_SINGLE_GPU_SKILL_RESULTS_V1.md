# MOD4v1 九专家单卡并行评测结果

**已完成：1张 RTX4090，9专家×80环境，共720环境；实际控制 2026-11-02T10:16:10+08:00 至 2026-11-02T10:32:08+08:00。**

九个worker真实控制窗口有 **139.44秒共同交集**，全部RC0，原App关闭/parent wait/两个EX释放完成。GPU采样最低空闲3002MiB，9份新stdout未检出CUDA OOM或contact/pair/buffer overflow。**执行全部完成 ≠ 全部技能毕业。**

## 逐专家结果

| 专家 | 环境 / 仿真窗口 | 本轮实际技能事实 | 结论范围 |
|---|---|---|---|
| E0 平地基础 | 80 / 20s | 普通跌倒/闭链/mimic重置0；vx误差0.0395m/s；yaw误差0.1059rad/s | 基础保持诊断完成；原全技能毕业规则缺项 |
| E2 世界系移动整圈 | 80 / 24s | 187个完整整圈事件；原世界系联合谓词0/187，另43个不完整事件 | 按当前原观测器未达界；世界位移getter时序/参考点独立验证仍有缺口，不据此断言机器人完全不动 |
| E3 跌倒恢复 | 80 / 3.2s | 12类跌倒恢复初始74环境，原0.5s稳定credit 0/74；另6个正常姿态不计恢复分母 | 本3.2s初始episode窗口未取得恢复credit；不跨reset拼接，也不作旧20k的配对退化结论 |
| H1 normal 真270mm | 80 / 20s | 准备就绪64/80；起跳42/80；落台0/80；恢复成功0/80 | 真270mm源事件已测但未完成落台恢复；20s为原cfg默认观察窗口，非已接受cohort的完整复现 |
| W35 / W25 RM70 | 80 / 32s | 运动完整区间18/61达原界；站立26/26；观察goal 0/228 | 尚未RM70场地策略毕业；goal为observer非训练目标；本CPU固定0.30bin不等于整个高速人口，不宣高速已通过 |
| CURB878 路缘 | 80 / 15s | 上行22/27；下行27/27；站立无普通失败26/26 | 原端点接触谓词已测；上行仍有未完成环境，未声明整体毕业 |
| CURB113 路缘 | 80 / 15s | 上行22/27；下行27/27；站立无普通失败26/26 | 原端点接触谓词已测；上行仍有未完成环境，未声明整体毕业 |
| SLOPE135 5°/2m坡道 | 80 / 15s | 上行25/27；下行27/27；站立无普通失败26/26 | 原端点接触谓词已测；上行仍有未完成环境，未声明整体毕业 |
| SLOPE50 独立坡道 | 80 / 20s | 20s own training-axis筛查完成；41次边界、47次超时；无普通跌倒/闭链/mimic事件 | 原accepted80坡道cohort/完整端点谓词缺项，保留UNKNOWN，不借用SLOPE135标准 |

## 范围与解释

- 本轮为各自原factory、seed20260928、ONE fresh reset、D0–D7的新80环境筛查。完整checkpoint整缓存、actor及learned STD严格加载/前后核验；critic/17Adam/LR/iter及未知字段保在完整CPU缓存，不新造live runner/optimizer。原20k保存历史/RNG未切片/投影/施到80；此前20k完整恢复证据独立保留。
- 增强USD2c421a8e…/contractbae3203a…，400N/k2000/damping3、策略50Hz/反馈100Hz/物理2.5ms/TGS32,4、闭链10mm每env重置/mimic10mrad。只针对80环境显式GPU容量预分配并释放未引用Torch缓存；没改积分、几何、质量/COM/I、DR、动作或奖励。
- Curb/SLOPE135数字是原同episode、两轮端点顺序与1N接触确认，不跨reset拼接；站立原本不要求穿越，列出无普通失败而非用0跨越当失败。各组分母是本fresh80的27/27/26；不与旧accepted人口作配对比较。Slope135范围仅5°/2m，路缘是20mm/150mm条带，不泛化台阶或复杂场地。
- E2的0/187来自当前原观测谓词。Body速度/转向诊断、世界位移getter时间点/参考点仍应分开；不把该数字解释为完全不会动，不臆断迁移导致退化。
- E3稳定项严格读取recovery.credited，12种跌倒配方74环境；正常recipe12的6环境不计恢复分母。3.2s与0.5s稳定credit/3s请求的原门槛保留。
- H1读取真正270mm ownphase.goal自然事件；20s仅原cfg默认观察窗口，原已接受cohort/horizon未闭合。SLOPE50同样保持accepted cohort/predicate未知，不套其他专家指标。
- W35（W25）本轮61个完整运动区间中18达原联合界，26个站立区间均达界；228个route episode未记录观察goal。goal为observer、不是当前命令/奖励的训练目标，单独goal0不是执行器失效证明；运动完整区间观测along均值0.032343m/s/最大0.043333m/s，getter缓存相位/参考点独立验证仍是缺项，不宣物理0.04速度上限、不把旧量乘8。
- W35新raw171547B/543行及schema13125B均仅本次CPU读取1次、SHA核验，无限额截断/丢行。固定0.30命令bin为0不代表整个高速区间未暴露或通过，本轮主表只给运动/站立原界。先前20k32s高速0/8948属于独立旧cohort事实，未读取或改写来填本轮。
- 本轮没启动PPO/BPTT/GO、没写预算；W35此前真实PPO为162更新，这里没有额外训练。原CURB141 exact7b网络缺源条件仍保留，不用878替换。
- V1–V7启动/资源/依赖/reader错误与scope取消全部保留，它们没有共同技能控制窗口，不当作专家技能失败，也不覆盖为pass。

## 完整证据与交付

- [机器汇总](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports/SINGLE_GPU_NINE_FINAL_SUMMARY_V1.json>)
- [九个原终末与originalwait](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports/NINE_SINGLE_GPU_V8_CLOSED_20261102_101543/CLOSED_RESULT.json>)
- [并行交集/九专家原事实](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports/NINE_V8_COMPACT_FIRSTHAND_SKILL_FACTS.json>)
- [W35本次新raw一次CPU校验](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports/NINE_V8_W35_OWN_NEW_ROWS_CPU_ONCE.json>)
