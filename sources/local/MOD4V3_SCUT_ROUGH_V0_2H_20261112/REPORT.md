# 统一SCUT Rough-v0两小时：最终报告

本轮已完成，未晋升新模型。综合接续/原实车调试包继续使用R1第二轮005m，SHA `0dcc15f5ecfca08107dba8b1a1d80de57c777218b5f3a928c094be66c73a644f`；100m保留为已细评的实验候选。

## 实际训练

用户授权统一训练华南虎Rough-v0两小时，不再拆R0/R1/R2短课。使用保存的rough_rotation_stair运行（2026-07-30_09-16-27）全部9地形族、10级难度，从启动一起采样；顶层curriculum为空、可选height-offset curriculum关闭，没有按成功率分段准入。为4096克隆分散出生点，将参考14列复制为70列；保留20%平地与20%名义参数的独立交叉分配。

实际PPO **7206.137秒**，iter22959→23807，共848更新、83,361,792环境策略步。4096env，LR3e-5 fixed、clip0.1、3epochs、rollout24、seed66。每300秒完整保存/下载核验/实际读回；24个定时点，加首次更新和final共26份完整PT、25种不同字节。final与120m同字节；另保留短探针两份同字节PT原件。

MOD4适配保留：35actor/78critic/6action，机身坐标指令，当前完整DR、2.2m/s上限，−1.5e²和指数速度权重1.2，2.5ms物理/10msPD/20ms策略，TGS32/4、2mm单env闭链保护与电机包络。MOD4无云台，没有新增云台观测。Rough-v0的air reset/airborne关闭。SCUT15%低档gyro、15%高档gyro、30%高速组合与普通/航向/站立指令统一混合，地形高度覆盖按保存参考；保留原ground-reset恢复段。

本轮是SCUT科目的MOD4适配，不把硬件、完整DR和上述已接受奖励改成参考机器人参数。完整实际配方见EFFECTIVE_RECIPE.json；原PLAN两个继承描述字段仍写rough_r2/air overlay，按启动原件保留。CLI/STARTUP始终是rough_scut_v0、air_reset_fraction0、airborneFalse；描述订正在实际配方中列明，未热改训练。

## 保护与执行证据

主训练153,821个结束episode；原始保护计数closure19,851、numerical34、mimic10、closure_catastrophic3，terrain_boundary65,341。原因可重叠，不能相加推算全部终止类型，也不能称训练全程numerical0。均按既有单env保护处理，没有放宽闭链或因单峰停整批。正常FINAL与SAFE_CLOSED齐全。

8项正式固定权重PhysX对照全部完成：dt0.0025、raw-action槽误差0、电机包络违反0、numerical0、没有漏接触容量警告、无PPO优化器更新。启动原生机械限位/质量/零隐式主动驱动检查留在STARTUP；轮末3个资产文件pin校核均匹配，根USD SHA e057969b136fd75613bb8d77985d43d043f54faae62dc060afb718ebabbe1c1c。49份训练源/参数及3份评测源/模型清单从目标机读回核SHA，52份一致。

## 同批结果与解释

| 指标 | R1父 | 100m | 120m |
|---|---:|---:|---:|
| PhysX名义Flat原六项 /60 |58|36|30|
| PhysX完整DR Flat原六项 /60 |42|35|38|
| 完整DR level9 ±1m/s穿越 /160 |134|133|131|
| 完整DR level9 ±2.2指令穿越 /160 |145|148|144|
| 完整DR level9旋转首次6秒未结束 /160 |153|158|156|
| 完整DR level9旋转MAE rad/s |1.7066|1.8705|1.8548|

名义PhysX指令2.0/2.2的父实际1.9054/2.1643，100m为1.7242/1.8077，120m为1.7282/1.8484，出现欠速。名义MuJoCo100m旧六项60/60、120m20/60；该引擎中120m前进实际2.1879/2.3958，属于超速。不能把MuJoCo筛选数当成PhysX/fullDR通过，也不能把两个引擎偏速方向混成一个结论。

低档完整DR穿越155→156/157，小幅改善；中档147→144/143；最高代表档134→133/131。高速指令穿越100m多3例，旋转首段保留多5例，但角速误差与平地精度没有相应收益。综合继续保留父；本轮100m为实验候选、120m仅归档，未替换原冻结或实车包。不是新增100%毕业要求。只评测了代表行0/5/9和行9高速，不声称全部10行/全部指令组合毕业；旋转MAE基于有效首次episode窗口，必须连同6秒保留数阅读。

## 原始失败与复现

首次4096短探针在初始化失败：同步漏了既有remaining_reset_bank.json，未产生PPO更新；ERROR/SAFE_CLOSED/原上传清单保留。补齐数据后独立r2短探针完成一更新9.950秒，numeric1；主训练仍从原R1父启动，没有把探针点冒充父。两次本地读者错误（GBK控制台打印、嵌套引号解析）在LOCAL_READER_ERRORS记录，均未改训练进程。

模型本体在weights/，全部SHA/iteration/bytes见evidence/MODEL_ARCHIVE_INDEX.json与CHECKPOINT_INVENTORY；训练完整源、launch/monitor、正式评测代码与原始RESULT/INITIAL_DR/NPZ/日志均保留。后续完整PPO接续仍是新物理episode；原R1四级地形状态仅保留父来源，不能重标成统一十级统计。

[配方](TRAINING_RECIPE.md) · [同批比较](PAIRED_COMPARISON.md) · [全部保存点](CHECKPOINT_COMPARISON.md) · [选择](DECISION.md) · [Git同步回执](SYNC_REPORT.md)。本报告写入时最终Git提交/推送待执行，完成状态另见同步回执；未启动下一轮。
