# MOD4v2-HW300N60 — P0机械限位修复包

## 唯一当前硬件版本

- 气弹簧：用户确认全伸展孔中心距200mm、压缩140mm、行程60mm、标称300N。
- 连续主动轴：每侧hip/crank及其mimic从动轴不再具有旧±.5/[-1.2,.9]角度盒；保留实际电机力矩/速度等限制。
- 机构硬界：原CAD低折止挡的相对单侧等效约束与原六闭链共同生效；不是新限位块网格接触。训练softwindow独立可选，默认关闭。
- 真实缸行程和机构止挡分开：当前骨架下缸slide=[−.039360558909870585,+.020639441090129412]m；低折止挡时眼距约152.606mm，先于140mm压缩端接触。
- 机构差角可行支路约[-1.0863195404360622,+.49192233306644084]rad，上界由真实200mm行程求得，不是旧.85常数。

## 文件布局

- [robot.usd](<package/assets/robot.usd>)：独立USD。
- [import_contract.json](<package/assets/import_contract.json>)：同步机械/硬件/来源定义。
- [scene.xml](<package/mjcf/scene.xml>) + [mesh目录](<package/mjcf/assets/>)：完整31机器人刚体MJCF与277个原样网格，相对引用。
- [kinematics_v2.py](<package/kinematics_v2.py>)：绝对hip/crank输入、连续共同多圈与机械域IK。
- [runtime_adapter_v2.py](<package/runtime_adapter_v2.py>)：新进程prebuild显式接入，替换旧target差角窗，不热改live env。
- [RUNTIME_MIGRATION.md](<RUNTIME_MIGRATION.md>)：实际接口与状态。
- [VALIDATION.json](<VALIDATION.json>) / [RUNTIME_TARGET_CPU_VALIDATION.json](<RUNTIME_TARGET_CPU_VALIDATION.json>)：本轮实际本地模型/算法验证。

从解压目录把`package`加入Python路径，先执行`runtime_adapter_v2.prepare_environment(opt_in=True)`，随后导入已有MOD4 task、构造新cfg，再调用`apply_runtime_cfg(cfg,task_module,prebuild=True)`。不可把本包当作独立Isaac应用、直接热换旧env或自动复用旧专家评价资格；完整模板见迁移说明。

## 已验证与未验证

本地实际加载MuJoCo3.14：32个body含world、nq37/nv36/nu6/10eq、质量14.294140288606286kg，100项边界/结构/姿态/力学等检查通过；共同±2pi不被旧角框截断，CAD低折以下被拒绝，旧208.154mm眼距姿态按真实200mm行程拒绝。另0.3秒隔离机制CPU动力学有限，闭链误差约.171mm<原10mm。目标层CPU ABI算法9项通过（含跨±pi先相对unwrap再投影）。

**目标Isaac/PhysX、实际100Hz反馈绑定及实车验收未运行**，不把静态/MuJoCo/CPU ABI结果当原生硬件证明。300N按伸展端标称力处理；k2000N/m与d3Ns/m仍是未实测工程模型，零速压缩端420N是推算，不是厂家确认曲线。实际mesh止挡接触和全360路径无干涉也未认证。

之前400N/父层扩展上界候选已superseded，只在项目历史目录保留，**不在本发布包中选择或交付为当前版本**。旧MOD4v1、权重、Registry与原试验未改；本次没有新训练或自动专家晋升。

## 回滚与接入边界

回滚只在新任务选择原MOD4v1资产与旧适配器；不改本包为旧值，不覆盖旧文件。MOD4v2改变D0可达域与气弹簧硬件配置，旧策略若需迁移必须新purpose、完整来源和重新评测，不能沿用旧成绩或拷入旧环境状态。
