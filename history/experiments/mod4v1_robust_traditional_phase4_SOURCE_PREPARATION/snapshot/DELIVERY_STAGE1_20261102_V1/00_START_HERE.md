# MOD4v1 传统控制保底 — 阶段性交付包 V1

先读 [当前进度与未完成项](<reports/STAGE1_DELIVERY_PROGRESS_20261102.md>)。

## 交付重点

- C3：V4估计器 + 实际P25 + 独立失效/输出gate，带C2纯FK依赖。
- ASQP：真正active-set boxQP；原生C MPC supervisor直接in-process调用，并保留独立C3 fallback。
- 原生C FSM：None/unknown、时钟、持续窗、hard inhibit/reset与动作默认unbound。
- H2：自转反馈的数学C移植；不是完整发送/启停换向资格。
- 另附已封存的COM/接触proxy/shadow与粗糙失效分析，只作诊断证据，不是可信触地或自动动作许可。

## 入口

1. `SPR_AUDIT/portable_control_v3_current/README.md`
2. `SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1/README.md`
3. `SPR_AUDIT/portable_fsm_detector_v1/README.md`
4. `C_P25_SPEC625_H4_V1/PROTOCOL.json`
5. `HARDWARE_BINDING_CHECKLIST.md`

源码本身保持原字节。可单独取用FSM/MPC模块中的source_bundle.zip；相关C代码依赖也按原sibling结构放在本包。

## 使用等级

本包可用于代码审查、host数学/接口联调、板级适配与HIL准备；不是可刷整车固件。原生C MPC的valid/fallback不是发送许可，默认未知接触不能被当作0N。跳跃/预测腾空/非normal/接触许可未绑定时MPC必须显式disabled，最终输出还需caller与driver独立准入。

`BUILD_C_CORES_ONLY.ps1`仅编译host对象的便捷入口，本次打包未执行它；没有BSP链接、BIN或刷写。目标M4/M7的原编译事实/依赖以各模块BUILD_RECEIPT/OBJECT_SUMMARY为准，软件double/libm与目标时序待板级验证。

## 数据与包的边界

本包是源码/验证资料的精选快照，不是完整历史仓库、模型mesh或机器人raw数据镜像。大文件与预构建host EXE/DLL不随本源码包提供，MANIFEST列出遗漏及原因；原数字test/raw/INDEX路径保留历史引用，不保证都在此ZIP内。完整物理重跑需原模型资产、原工作区依赖及相应DR环境。已有host adapter程序在原工程中，包内提供其源码与构建收据。

NATIVE_C_MPC_SUPERVISOR与RAW2K_COM_WINDOW在本次cutoff前已经真正seal；仍BLOCKED的ASQP production stdio、尚未运行的world-leg实验、R39实验控制代码不混作baseline。R39结果仅作进度证据。

此包/新模块目前PH4pending；PH3 Git tag截止R34。当前Goal继续，不把这份阶段包当整车最终防线已毕业。
