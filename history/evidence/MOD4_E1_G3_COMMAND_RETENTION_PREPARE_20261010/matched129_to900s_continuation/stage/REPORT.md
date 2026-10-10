# E1 G3 有界命令保留修复：实际支撑准入

本阶段依据人类“继续修复”和 V2 工作单，保持 35mm 几何、plane30% 和另外四族20/20/15/15，只在实际生成的 plane_for_rm 支撑及旋转净空内在线采样旧正负直行和 world V=.5 / yaw±1–2。其他地形仍为 gentle yaw0。源为完整行为已审 model32058，SHA42cdc9d24519778a9da3e35b05a3eb3bb5745760c26a5842c78fcde2bd39e53b；没有选择退化的32063，也没有升到50mm。

华南虎源码和真实 July30 配置的详细结论沿用上一阶段完整审查：持续在线采样符合地形条件的旧命令，不能由 CLI 的 MoE 入口推断 V14 已实现冻结专家的永久抗遗忘。我们修复的是持续更新的 E1 内部旧能力，gate 尚未训练。CPU组件、SDK准入和健康保存均不能代替后续四case的实际行为保持证明。

source348 原338逐字保持并新增10个隔离文件。Torch2.10 CPU实际完成14项新状态拒绝测试、私有CPU随机流磁盘恢复和原96有限张量完整源读取。首SDK在 RewardManager 参数检查阶段拒绝 `**kwargs` 签名，未执行探针控制步/PPO；原源、错误与父guardian自然退出保留。source353 原348逐字加5个独立入口和显式参数shim，数值仍为原零代理贡献；第二SDK在选定10个支撑前拒绝固定行列选择器，未执行探针控制步/PPO。两个失败不能写成物理退化或通过。

source355 原353逐字加2个新入口，按实际生成记录选择最近的十个可用 plane 支撑，仅改变新SDK探针放置，不改20k/PPO默认网格、几何或配额。新的实际诊断：原固定行列选择器找0格，整个真实生成布局有480个可用plane格；不从族比例猜地点。10env / 300control / 1200callback 已实际通过，ordinary0，closure .691242574mm，ground-height与height reward公式误差0，正负直行及两方向world在线控制实际存在，world投影误差0，selected reset其它环境bias/episode精确保持，净空半径1m；全有效前reset命令轨迹保留。支撑射线是实际网格支撑证据，不冒称接触力硬件认证或连续全部姿态净空证明。

后续只运行该真正新命令范围必要的20k native、128×2和20k×4完整PPO弃权重，全部实际准入后才允许300秒load-learn-save-exit短窗，并完整保存、唯一原父结清和发布新129四case。当前实际状态以 COMMAND/SDK_REPAIR/ASSIGNMENT_REPAIR_ACTUAL 时间戳报告为准，未生成的预检、保存和回放是pending。本阶段没有预算扩展，旧clock、同scope geometry、D0-D7合同精确SHA复用；不改奖励权重、学习率、硬件、actor输入、KEEPSTD1，不启动S7/S8/teacher或额外无界块。

所有拒绝、读者问题、CPU组件、源图、派生入口、同步和后续结果保存后必须Git补交。大型原件仅真实路径/大小/SHA索引。当前一课的合法保存审查边界不代表全课程或真实RM70mm毕业。

实际后续：20k native已完整通过480 timed/576 total callbacks，ordinary/integrity/unknown0/nonfinitefalse、closure1.705825329mm，ground与reward公式误差0；128×2已完整6144环境步/192callback，CPU102有限张量，唯一28.112966537s已结清。source355 20k恢复在学习前新增_retention_rng混入旧named清单被拒绝，唯一219.338403225s已原父结清、无预检model/正式学习，所有父guardian孩子实际退出。新source360只把私有Generator移至显式拥有的容器，原方法通过property原样访问；旧restore_named严格集合保持，新增5项CPU ownership/disk/unknownschema在目标Torch2.10实际通过。原SDK/native/small证据精确复用，不重复GPU；新独立controller仅补被拒的完整20k恢复预检及实际准入后300秒正式窗。此前formal/129尚pending不是通过。

阶段644890ee归档后的新source360实际拒绝：原D1-D7/optimizer/globalnamed和G3旧terrain bookkeeping/newgeometry CUDAroundtrip/episode+1都已经实际通过；新外层wrapper错误地与加载前初始化counter比较，故仍在学习前拒绝。唯一222.321688652s已原父结清，未PPO更新/未ownbigsave。独立source364保留360逐字、增加4文件，只把wrapper基准改为保存源的episode+1，并以目标CPU实际源counter核验，拒绝doubleincrement；旧合同与旧false/raw/cost都保持。后续实际准入/保存/129尚须工具证明。

最新实际source364完整20k×4已PASSED：4更新/96控制/1.92M环境步/384callbacks exact，自己的完整CPU102有限张量、实际srcsnapshot72、full source map364；原D1-D7/optimizer/globalnamed与新增command CUDAroundtrip/保存源episode+1均真实通过。预检权重弃用，唯一293.5042884349823s已原父结清。正式300s确已从32058开始，未来完整保存及129行为尚pending，不以预检权重宣告遗忘修好。

正式实际自然完整保存退出：当前source364 model32063 SHA3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e，CPU102有限张量，自己的72实际srcsnapshot+364完整源冻结、PID/PASSED和唯一325.1909341812134s均已核验。6updates/144control/2.88M环境步/576callback exact，ordinary/integrity/unknown0/nonfinitefalse/STOPnone；旧全组恢复、新command/private CUDA磁盘恢复及保存源episode+1均通过。父guardian孩子实际全退出/noactive是合法review边界。旧338同编号32063 SHAe912完全不同，不能混为同源。新129四case已发布，尚须实际完整行为判断，不能以本保存说永久抗遗忘或35mm/E1/RM70mm毕业。
