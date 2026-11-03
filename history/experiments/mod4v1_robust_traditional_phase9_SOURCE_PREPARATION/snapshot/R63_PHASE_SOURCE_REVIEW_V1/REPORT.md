# R63 push-only静态FF：实际源链预审（候选尚未提交，未准入）
Catalog Office/ACL不匹配控制代码，使用read；只读8个必要small source，不读raw/QI/H5，不执行模型/FK/物理/QA/Git/newagent。PH8pending；气弹簧数值/符号等父与Cagent独立结论，不在此计算或选择。

## 需冻结的真实构造/访问位置
- 继承链应是新candidate→Position→LandingV3→ObserverV2→V1；不从AIR002继承，不叠air h、wheel coast或事件新策略。[Position:11,46–85](<../MINIHOP_POSITION_TRIGGER_V1/controller.py#L46-L85>)。
- V1构造直接引用self.g=start_gain/self.end=end_gain；ctrl用**start_gain**构造，q_start/q_end提前转换，last_tau提前copy。[V1:19–32](<../MINIHOP_V1/controller.py#L19-L32>)。
- **重要alias：**GroundController.tau_eq=np.asarray(gain['tau'])没有copy、self.g也引用gain。仅copy dict而in-place改原tau仍污染ctrl，构造前改gain会影响approach。[Ground:10–14](<../ground_controller_v4.py#L10-L14>)。
- 真正push FF只有74行`(1-s)*g['tau']+s*end['tau']`；随后加PD、leg±32、wheel公式覆盖、roll/yaw校正及最终±EFFORT。修正须进入FF访问，不在最终tau后补偿。[V1:65–101](<../MINIHOP_V1/controller.py#L65-L101>)。
- V3的K0/K1/ff0/ff1/eq0/eq1为构造时copies，u>0才写capture ctrl；不触碰这些、q_start/end、capture_from或last_tau以伪造隔离。[V3:12–48](<../MINIHOP_LANDING_V3/controller.py#L12-L48>)。

## 最小candidate结构及意外影响
- 默认False必须直接super；base构造仍传旧gain。enabled且落在原timed_push区间时，临时self.g/self.end置新dict，**各自tau必须新array**；try调用super，finally还原两个原对象identity，即使guard失败/异常也不泄漏；不改原gain或ctrl.g/ctrl.tau_eq。
- 只改LEG=[0,1,3,4]的已冻结静态FF；WHEEL=[2,5]原值保留（虽push77行随后覆盖）。旧FF包含重力等项，不能把整tau清零；gas-only正负/坐标/端点混合必须有独立符号证明，不凭命名相减。
- firstpush进分支前launched=False，overlay不可要求已launched才生效。Position上一tick锁下一tick，保留trigger/clock/age/deadline/单锁及68–70原pitch/roll/speed guard，让super决定INHIBIT，不复制宽放。[Position:22–43,60–72](<../MINIHOP_POSITION_TRIGGER_V1/controller.py#L22-L72>)、[V1:60–71](<../MINIHOP_V1/controller.py#L60-L71>)。
- prepare_estimator保持原顺序/原V2 quarantine和gravity公式；不要根据新FF改prepare flags或把timer当contact。浮点absolute-sum与since-subtraction原本可能一tick差，不加整数phase“修复”。[V1:34–40](<../MINIHOP_V1/controller.py#L34-L40>)、[V2:14–25](<../MINIHOP_OBSERVER_V2/controller.py#L14-L25>)。
- air/capture公式、K/ff/eq参考保持旧式≠新物理输出/轨迹保证相同；push实际输入改变会传播到后续状态。必须如实标识push FF改变而非宣称全部V3 torque equations unchanged。

## 新入口/来源绑定与软件停止
- 最小新entry从实际position runner派生，仅换candidate import、kind/feature/provenance；保留prepare→packet→estimate→command→privategrade/apply的实际loop、FullDR/driver/20substeps、good/main/local/health。[Runner:41–100](<../run_manual_position_v4.py#L41-L100>)。
- SOURCE_MANIFEST在plant前落盘；新增kind/精确bool feature、baseline identity、新CORE/ENTRY SHA、静态FF数据/分解receipt SHA及配置/单位/LEG顺序。不要继续写原`relative_V3_push_flight_capture_equations_unchanged=True`，改为pushFF changed而approach/air/capture formulas retained的准确字段。
- 原runner的StreamedRows+except/error_receipt必须保留：任何异常保留已写prefix/实际计数或未知，不能推配置预算充当消耗；completeFalse/health/controller/gateFalse是机器人失败，不改成software失败。[Runner:29–30,65–100](<../run_manual_position_v4.py#L65-L100>)。
- **当前V4并非candidate运行证据验证器：**它锁entry/source/review/approval，66行仅取flatgate选RM；未核实际result完整cfg/新feature/kind和SOURCE_MANIFEST对应新candidate。[Launcher:20–36,58–74](<../launch_manual_profile_train_v4.py#L20-L74>)。R62另有AIR002专用binder，其CORE/ENTRY/KIND常量不能照用gas。
- 建议最小新launcher复用V2 artifact-aware launch，另加R63独立binder：actual cfg==锁定PROTOCOL（仅明确场景标签差异）、feature严格True、新result kind、actual SOURCE_MANIFEST中CORE/ENTRY/FF数据签名==锁定索引；再按原flat gate/精确profile配对RM，独立review+父hash-bound approval，无旧ID重用。
- V2应原样保留rc!=0、ERROR（即使rc0）、missing/badJSON/schema/case/count错误统一softwarefail，完成当前wave即停且保存BATCH_RESULT/unstarted；有效机器人失败继续原规则。[Batch:34–72](<../fresh_train_batch_v2.py#L34-L72>)。
- 后续仅审delta：新source/FF数据、preparer、actual entry及独立binder/launcher/plan source索引；复用本read缓存与既存base证据，不重复旧600/FK/完整79/旧QA。fake actual-main preloop仅证明CLI/root/import/constructor wiring；假plant/DR/bounds＋0loop不冒真实model/asset/driver准入。

## 当前结论
结构上有清楚的push-only FF插入点，但**R63 candidate/entry/FF签名尚未给出，ready_for_physics=false**。无新controller、符号/数值、phase或gate改动；等父新delta后再做独立准入review。本报告不是实验或父审批。
