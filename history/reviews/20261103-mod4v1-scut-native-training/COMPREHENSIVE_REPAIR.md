# MOD4v1 上台阶完整链路检查与修复

用户要求“全面检查是否还有其他问题别再出问题修了”。本次基于已完成的20000环境训练与独立评测失败，核对固定SCUT来源、MOD4原执行wrapper及当前实际代码。修复源码的56项CPU检查全部通过；修复版目标SDK复测尚未执行，当前共享资源仍被其它任务持有。

## 已完成的实际运行

20000环境一小时窗已完整保存、安全退出、正式传回并完成独立80首局。final为iteration72、新46次PPO更新、22,080,000样本、41,479,518B，SHA `305f5a9e57086fd7e1b75ef3536e7c375081278479a91f33a9bb18c760b4cfcf`。全17个Adam状态step1440。原owner1545304已ownwaited、结清、释放；旧launch/FIRST/postround/传回均已消费。

独立结果：0strict、0wholeclear、0leading、0台顶接触；10–17controls结束，平均11.775controls即0.2355s。保存的实际碰撞几何姿态侧/顶图已由当前模型原生审看，机器人在出生附近倒下；终止后的重复面板是终态clamp。不能称为跳上台阶或仍在训练。

## 确认的问题与修复

| 编号 | 问题及证据 | 修复与验证 |
|---|---|---|
| F1 | 成熟MOD4 E0原入口使用 `clip_actions=6.0`，本适配遗漏执行裁剪。实际final第一维动作首次约−75，后续最小−344.43，直接进入动作历史/物理目标 | `ScutVecEnv.step`以新张量裁剪±6后送物理及history；PPO原采样、Gaussian logprob、storage不变。真实RSL合成24步及20次Adam更新验证 |
| F2 | 原SCUT只在debug开启时于reward尾部增加 `_value_debug_step`；保存YAML关闭debug。适配却每次读观测增加，错误激活 `>10` raw-observation终止门 | 恢复enabled判断及原推进位置；对原函数AST做开/关并列时序测试；真实速度异常、非有限、closure/mimic硬重置保留 |
| F3 | 原评测terminal control在reset后读取joint target，混入下一局；缺少直接终止原因输入 | 从同一pre-reset快照记录applied action、joint target、raw maxima、异常门、closure/mimic/numerical和连续计数。原曲线不回写 |
| F4 | 首局接触计数用了active mask，最大force却没用；后续reset局可污染最大值 | 所有首局接触统计统一mask；合成第二局9000N不进入首局最大值测试通过 |
| F5 | yaw验收基准取首次physics端点，遗漏出生到首次采样间转角 | reset时从实际根四元数建立yaw基准；选择性reset不改变其它环境基准 |
| F6 | 全局debug/common计数器未随完整检查点保存；存盘未显式flush/fsync | FULL_V3保存恢复计数器（含population变更路径），写partial后flush/fsync再replace；精确比对actor/critic/STD/Adam/LR/iteration、全局及命令RNG，恢复后一次fresh reset |

**F1的±6来自MOD4执行映射，SCUT保存YAML本身的clip_actions为null。** 这不是把新裁剪冒充上游原配方。FULL_V3显式标记动作与原debug时钟语义，V2只有 `--repair-unclipped-v2` 才允许迁移。旧V1/H1或错位字段拒绝。

早期 `ACTUAL20000_ACTION_FAILURE_CPU.json` 保留：上一动作abs>120与80个终止时刻逐例对应，但旧评测没有保存直接reason mask。F2是在后续源生命周期核对发现，不能把全部早退因果只归给F1，或把回推结果写成现场标签。

## 已核对的边界

- SCUT V14→V13→base继承，86基础reward原AST；26非零基础项独立NumPy方程、9组合输入，dt只乘一次。
- actor35、critic78语义顺序；clean/延迟反馈区别；clip→scale；原始观测缓存、height-before-state、action history只推进一次。
- done→reward→command重采样/height→selected reset→observation顺序，manager不重复推进命令；V13写回generator。
- 原>1N/40°/20连续controls/max−1 timeout；V14实际29非轮body含8导轮；单环境10mm闭链及.01rad mimic立即重置。
- MOD4按名字解析6执行器、30DOF、31body、轮半径/宽/hip锚点/软限位；增强USD身份；新constructor质量惯量不被旧PT覆盖。
- PPO rollout24、GAE .99/.95、5epoch/4batch、STD、timeout bootstrap、梯度；动作执行裁剪不改PPO采样分布或logprob。
- 同final独立80首局、400Hz接触、有限圆柱整轮footprint、出生yaw、全局计数器及一次fresh物理reset；来源SHA与FULL_V3兼容。
- 接收器曾遇到UnicodeDecodeError和nullable worker读者错误，原报告保留，修复后完成正式传回；没有重训旧once。

原18,540物理行对照仍为历史索引，本次新增 `COMPREHENSIVE_REPAIR_SOURCE_INDEX.json` 给出当前文件SHA与函数位置，`REPAIR_SOURCE_LINE_DELTA.json`列F1–F6对照。索引、CPU测试和静态阅读都不是全部分支已在目标SDK执行的证明。

## 当前验证与接续

`FULL_REPAIR_{ACTION_TESTS,AUDIT_TESTS,STARTUP_TESTS,PARITY_TESTS,REVIEW_TESTS,VALIDATE}_ATTEMPT1.json`分别5/5/4/16/14/12项，通过共56项。本轮合成测试0生产PT读取、0physics、0GPU训练；此前实际final CPU诊断的读取次数另记，不混入0计数。

同final诊断已在原 `env20000_1h/action_clip_eval1` 内修订至REV3，仅7个修改模块+owner+plan；原未启动REV1/REV2文件保留。当前执行入口为 `action_clip_eval.py run`，读 `PLAN_REV3.json`、`SOURCE_FROZEN_REV3.json`；80firstepisodes、400controls上限、seed9137、0优化、0账本写入。尚无LAUNCH_ONCE。原模型/资产/共享源码按路径引用，不复制树。

用户补充允许同GPU少量占用共用。新owner按目标GPU实际余量判断（保留原>15669MiB余量；有占用时≤4096MiB且利用率≤30%），不再只因存在compute PID拒绝；原canonical/private/finite锁仍先核实。23:47本地存在collector55748，peer SCUT20最后23:25回执仍live，原保存时间为2026-11-04 00:14:41+08、退出名义界00:19:41；这些是历史时钟，不是释放证据。未开第二SSH、未抢锁、未杀进程。

新诊断后必须核all80原因/接触、回放实际poses并原生审图，再决定修复来源模型或恢复训练。旧final已有较大动作偏移，不能仅因接口修好就假设策略恢复。20000环境训练需求保持；不得原样重放失败小时。

任务设计尚有已知限制：jump270恒定vx=.6没有台顶停稳命令阶段，且沿前基础高度与Stair目标高度可能竞争。这里保留8654任务配置便于隔离接口修复；需依据修复后真实轨迹决定后续奖励/命令调整，不能把它写成稳定技能已解决。

全部补充按既有native阶段普通提交；不重record/retag，旧false和二进制原件保留。工作单为 `WORK_ORDER.json`。

归档前检查曾因Windows写入CRLF将工作单新增行标为trailing whitespace；已将可编辑工作单规范为LF，随后diff检查通过。历史原始字节及SHA对象保留。此为格式检查失败，无训练、模型或物理重跑。

归档索引校验的一次内联Python命令因PowerShell引号转义失败，在执行前产生SyntaxError；改用here-string传入后完成文本SHA与外部文件大小核对。该失败未读模型、未改索引或执行physics。
