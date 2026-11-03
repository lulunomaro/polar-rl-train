# 阶段1：已完成的验证与仍缺的现场证据

2026-11-03 18:55 +08:00。当前持久Goal revision15 / round9 / active / armed；按[执行计划](<EXECUTION_PLAN_V1.md>)的五阶段顺序推进，当前仍为阶段1。没有进入阶段2 native训练，没有晋级任何候选。

## 这轮实际做成的事

|项目|实际结果|证据范围|
|---|---|---|
|八角色static/dynamic/sensor/clock分区|159个legacy命名字段，76条extended必需缺件；9成员封件与202项原source/出版元数据SHA一致|SOURCE结构与源码语义；六actual0capture不当非零训练|
|父独立复验分区模块|32/32 stdlib正反例通过；测试前后封件未变|SOURCE/synthetic，不是SDK|
|被动sensor tap|13文件封件；21 stdlib/fake用例通过；父已review核心源码并将两处部署/默认参数问题反馈后于seal前修正|组件SOURCE；尚未live preflight|
|真实原SensorCorruption/FeedbackDelay reference|实际远端Torch CPU运行10项通过，16controls/32正常feedback ticks+同tick局部reset；各channel258次实际draw；age0和10000us都覆盖|真实原两类、synthetic输入，非SDK|
|真实原两类 + 已封被动tap|25组输出bitwise一致；50次原return identity检查；baseline/observed的sensor、delay各恰好25调用；private RNG/full queue state与global Torch/Python RNG不变|fake env中的真实Torch CPU类和tap，**未执行native binding preflight/actor35/PhysX**|

父侧新增两个实际CPU用途均RC0、已实际收取，未重放旧once脚本；无自己的GPU/SDK/模型PT/raw/canonical操作。两个CPU回执分别是[原两类reference](<../reports/PHASE1_SENSOR_REFERENCE_CPU_V1.json>)、[原两类+tap](<../reports/PHASE1_PASSIVE_TAP_CPU_V1.json>)；SOURCE父复验见[分区独立回执](<../reports/PHASE1_PARTITION_PARENT_SOURCE_VERIFY_V1.json>)。

## 确认的接口缺口

1. 旧raw35已经带原噪声/延迟；新noise-free sensor head要从自然调用的clean输入采集，不能从旧raw35逆造或在已有噪声上再加一次。
2. 旧context中的feedback_delay只是lag选择标量，没有FIFO/cursor/sample_tick/ready。action lag/pending/applied也缺完整issue/due/valid/first_apply时序。
3. `mild_factor`仅是共享mass/inertia因子，不是motor全部gain；旧xi缺实际motor episode_scale4+2、mu等静态字段。其物理影响和旧策略失败的因果尚未得到对照证明，不宣称“发现即归因”。
4. command_time_left原生秒、legacy stored=秒×.01；recovery_age/stable原native centisecond、stored已经秒。这是显式编码映射，不凭名字将前者当100Hz tick；未改旧norm/权重，也不将其反缩放后拼回旧模型冒resume。
5. 原100Hz可直接捕获的是五组clean反馈16维。中间时刻完整clean35原本没被计算，仍Unknown；另19维command/height/prev_action/mode的clock需单独记实，不拿50Hz端点补中间真值。
6. 同tick可能是cache-hit，也可能partialreset后的fresh draw；sample身份必须含episode+tick+key，warmup lag1用当前新episode样本且age0/readyfalse，不能把所有apply调用数叫100Hz采样数。

[分区说明](<../source_phase1_state_context_partition_v1/README.md>)列完整单位/offset/缺件与Gate1条件；[tap说明](<../source_phase1_passive_sensor_capture_v1/README.md>)列真实函数/MRO/源码/默认实体的安装前绑定检查及bounded capture范围。默认2/2事件仅debug，不足5channel×MID/END完整对；实际短窗会显式设较大first/last和足够cap，`retained_last`只指cap内最后，不冒长run结尾。

## 下一步，仍只推进阶段1

- `cffddedf-0c4e-4a0f-bffd-8b2d48a6785b` 新actuation SOURCE任务进行中：只包装原queue.submit/apply及原目标setter的已有参数，补issue/due/valid/episode与静态已存字段，不新增SDKgetter，不与sensor tap双wrap reset；physicalreadback没有就Unknown。
- `565b1562-3c38-4864-8a0f-ed68a3526f7c` 新native interface集成SOURCE进行中。已确认旧frozen mean worker不构造NativeTaskBridge，且旧parent固定两成员和160/1600；仅贴tap/改purpose不会自动获得准入，必须NEW接口验证kind与明确bridge绑定/新semantics门。现在没有stage或Popen。
- 两个SOURCE交付后父review、验证组合，再按原资源门做最小有界实际SDK接口验证；新schema/新模型训练仍等待现场Gate1证据。

```text
stage1 source + CPU progress = verified
stage1 actual SDK binding / actor35 bitwise proof = UNKNOWN
stage1 gate admitted = false
new native policy BPTT = 0
mother/Registry_v12/H1 changed = false
```

原物理/完整DR/动作速度/原接受/预算与锁全部保持。当前材料及后续真实失败/Unknown按独立feature trial追加归档，main仅读；不为Git读取模型/raw、重跑旧用途。总目标80/90+鲁棒性/保持仍未满足，Goal保持active。
