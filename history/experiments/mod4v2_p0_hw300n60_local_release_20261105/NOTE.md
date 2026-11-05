# MOD4v2-HW300N60 P0本地验证交付

## 当前结论

独立MOD4v2硬件版已构建、完整模型本地验证与目标投影算法回归通过，并打包。**未热替换旧运行环境、未改旧专家/Registry/预算、未启动重训。目标Isaac/PhysX与实际100Hz反馈接入尚待原生验证，不把本地结果当硬件认证。**

[下载完整包](<MOD4v2_HW300N60_P0.zip>)：20,565,100 bytes，SHA256 **bf7193525eb75c342a7dbed1bc095abb6fb7bc855d1cebda41fd22cc6a3a903b**；解压根`MOD4v2-HW300N60/`，292文件，其中277个源网格字节不变。身份/逐文件校验见[DELIVERY_INDEX](<DELIVERY_INDEX.json>)。

## 实际修复

| 层 | 旧问题 | MOD4v2-HW300N60 |
|---|---|---|
| 主动髋输出/输入 | hip±.5、crank[-1.2,.9]硬角窗 | 每侧hip/crank与两个mimic跟随轴continuous；USD author±inf，MJCF limited=false |
| 被动机构 | operating样本极值与机械硬界混用 | 删除无机械依据的另一侧界，保留CAD低折单侧等效止挡；不是全关节任意无限 |
| 气缸几何 | 旧50mm/400N假设或父层恢复值 | 用户确认全伸展200mm、压缩140mm、行程60mm；slide=[−.039360558909870585,+.020639441090129412]m |
| 气缸标称力 | 旧400N语义 | 全伸展零速300N，USD/MJCF/contract相同target .1706394410901294m |
| 目标/角度 | 旧−1.0843/.85训练投影；跨±pi可能错误低折 | 按真实机械δ投影，先按当前相对角选nearest2pi，再共同unwrap，保留原delay/scale/reset/apply ABI |
| IK/复位 | 旧operating差角检查 | 绝对hip/crank输入、同源闭链支路、机械硬域检查；可选softwindow独立且默认关闭 |

真实止挡当前实现为**CAD回算的等效相对关节硬界**，原6闭链和4传动关系保留；没有声称新增了part145真实网格接触。145/124/134来源与视觉/过滤事实保留，图片箭头不冒认精确编号。

同源几何在CADδ处给rocker −.7828279184955527rad，已消除旧contract 2e−7rad元数据差，不另加经验收紧。新可行差角左右均 **[-1.0863195404360622,+.49192233306644084]rad**；上界来自200mm行程求根，不是旧.85常数。低折止挡时气缸眼距约152.606mm，先于气缸140mm最短端接触，这是机构与气缸硬域的交集。

## 本轮实际验证

[完整模型回归](<candidates/HW300N60/VALIDATION.json>)：MuJoCo3.14真实加载完整新场景，**100项检查通过**；32body含world、nq37/nv36/nu6/10eq、质量14.294140288606286kg。USD与MJCF/单一SI规格边界一致，主动共同±2pi不被旧角框阻挡；CAD低折以下被拒绝；140/200mm与300N伸展端力正确；便携mesh依赖完整。另0.3秒隔离机制CPU动力学状态有限，最大闭链误差 **0.170542mm**，小于原10mm界；此诊断暂置重力0，未改资产重力，不当任务/硬件动态通过。

[实际等效止挡恢复试验](<candidates/HW300N60/MECHANICAL_STOP_ENGINE_VALIDATION.json>)：另一个有界MuJoCo试验故意从低折CAD域外.01rad初始化（仅诊断时绕过IK检查），初始rocker限位穿透4.851604mrad，120物理步后该低折穿透为0且状态有限。它验证引擎等效止挡确实参与纠正，不是仅有Python拒绝；不是恒力贴挡保持/全域接触或真实网格止挡认证，末态的完整坐标仍原样保存在receipt，不外推为所有运动通过。该补充receipt在ZIP生成后产生，随本次Git和报告交付、不谎称已在ZIP内。

[目标层CPU回归](<candidates/HW300N60/RUNTIME_TARGET_CPU_VALIDATION.json>)：**9项通过**，实际检查opt-in、旧RM_DIFF窗替换、原delay/scale一次调用、原apply/reset继承、输入不变、共同多圈、跨±pi相对角、机械上下界。它是Torch CPU源码ABI stub，不是IsaacSDK/100Hz反馈证明。父源码检查发现的raw_delta先钳位遗漏已修，修前快照[保留](<candidates/HW300N60/attempts/runtime_adapter_before_relative_unwrap.py>)。

## 必须保留的硬件边界

1. **300N不是本轮实测完整力曲线。** 用户只给标称力，k=2000N/m、d=3Ns/m明确为沿用未标定工程近似；因此压缩端420N是计算值，不是厂家确认，force_curve_calibrated=false。
2. **旧截图208.154mm与已确认200mm伸展上限冲突。** 本版正确拒绝该状态，没有改锚点/扩大真实行程凑PASS；该差异应继续核对真实安装锚点/模型版本。参见[硬件修正说明](<HARDWARE_CORRECTION_300N60MM.md>)。
3. 共同2pi坐标可置入不等于所有360°运动路径都无实体干涉；真实mesh止挡接触、全域干涉和实车尚未认证。
4. [原生接入说明](<candidates/HW300N60/RUNTIME_MIGRATION.md>)只支持新process/prebuild显式opt-in。目标PhysX/真实100Hz反馈binding仍pending；不自动替换旧训练、不自动宣专家适配通过。

## 主要产物身份

| 产物 | SHA256 |
|---|---|
| [USD](<candidates/HW300N60/package/assets/robot.usd>) | `2237070ddc0a4e33f0c28e23fe5bb3db1f12bb619fddcdd89f9a74d5ac875f18` |
| [contract](<candidates/HW300N60/package/assets/import_contract.json>) | `00199c26533a9adaca6a35a49d30e8b8b27182230772674bd936d8b527169f4e` |
| [MJCF](<candidates/HW300N60/package/mjcf/scene.xml>) | `c19c72d2690dce90fdef56bebd3b36e4c319d47b8ac7152cf42b2d01f6dfd125` |
| [runtime适配器](<candidates/HW300N60/package/runtime_adapter_v2.py>) | `148cbfdfab17e9bad04c5974c196279200c645af31e2f0b70ea8aa474ee82d98` |

旧400N候选仅封存历史，runtime选择已disabled，不在当前交付ZIP中。旧MOD4v1与旧专家/全部真实试验保持，成绩仍属于原D0版本，不重写历史。当前P0代码、硬件spec、旧假设/工具错误、两份候选构建记录、本地验证与交付索引，需按原feature-only唯一annotated trial归档并真实远端核验；main只读，不为Git重开权重/旧raw/原once或物理。


## Archive boundary
Includes superseded400N candidate/source/receipts and unit-default capability probe note, user-confirmed300N60 stroke pivot, new hardware builder/assets references and portable source XML, continuous IK/runtime, relative target unwrap before-snapshot+fix, actual full-model100 and targetCPU9 checks, separate120-step physical-stop recovery, delivery index and all reports. No actual Isaac/PhysX or100Hz/hardware claim. No old expert/Registry/production hot replacement or extraPPO. Original record validates/redacts/hashes; only two short scoped add paths with exact staged-set. Large artifacts indexed only; no model/raw/oldonce/physics replay for Git.
