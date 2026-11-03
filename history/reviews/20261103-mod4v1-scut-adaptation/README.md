# 本阶段交付与真实验证状态

人类要求逐行核对华南虎跳台阶奖励和训练代码，适配最新增强 MOD4v1 USD 或 MJCF。已实现独立 USD 代码适配：仓库 `project/isaac/mod4v1_scut/README.md` 给出原始假设、实际改动、目标接口、配置和执行边界。源固定 SCUT commit `1a26356d6f591734d4f6f666f5cead1a6925da67`，17个源文件、14,492个非空非注释行有处理索引；86基础奖励体通过原 AST 复用。逐行索引是可审查的处理说明，不代表全部源行已在原生执行。

12项 CPU 集成检查全部通过，最新为 CPU_VALIDATION_ATTEMPT5.json；含真实 RSL5 rollout24/GAE/PPO更新/完整保存恢复，输入为合成数据。新适配没有生产模型读取、原生物理、GPU训练或新270mm技能结果。当前状态 **CPU_VERIFIED_NATIVE_PENDING**。远端一次只读检查时 canonical 被 owner1535837占用；保持原共享/私有锁和唯一预算，不启动第二writer。本机 stock SDK 不作目标定制SDK的替代；远端 app前 find_spec 只记录可见性，不能称扩展缺失。

公开台阶保存 YAML 关闭状态机；`trained_stair`移植该基础奖励配方，`jump270`显式开启原 Airborne/StepUp/Stair 分支并替换270mm检测和几何尺度。JumpTakeoff 的奖励代码已核对并可测试，但两个 CLI profile 中均关闭；外力/速度 assist 关闭。当前 V14 字典另行提取，仅供核对/CPU测试，不冒称公开模型原来使用或本次生产启用。全部语义差异见代码README，包括没有同义rear2时改用四个真实motor限位、35/78观测、原MOD4动作PD/DC/队列和完整D0–D7。

同时补录已完成的476关闭/477独立实际评测。476完整保存SHA `b80db767ae932f47806d7aa41d026d711a2c984299b4075c6b6cbbe5b713ff5b`、CPU1654finite，所有原once消费且原owner已安全关闭。477实际80个环境首次episode：0strict、0wholeclear、5leading；46环境触台，22环境双轮同时接触，2365双轮环境拍，最长env38 .3975s；真实接触仍非技能成功。8early/4late实际姿态和6曲线已当前模型原生审图；env40所谓late全为1.34s终态钳位。ALL80_MANIFOLD_NATIVE_REVIEW.json保存逐环境证据，不重跑评测或旧once。

失败原件保留：CPU Attempt1/3、CIM首次本地拒绝、local22620未知退出、只补unused阶段的47096恢复、所有schema/路径错误见 ALL_ERRORS_AND_LIMITS.json。归档脚本首次拼接字符串与WindowsPath的 TypeError发生于任何归档写入前，改用Path后完成，记录于补充文件。EVIDENCE_INDEX.json索引75个新小文本、54个同Gitblob引用和15项大型raw/媒体外部引用；不复制模型、USD、轨迹或上游整树。

FINAL_WORK_ORDER.json为本阶段冻结交接，当前实时状态以scope/admin/CURRENT_STATE.json及后续追加回执为准。原mod4-10继续ACTIVE、每小时、同一聊天；原prompt已改为476/477已完成、新MOD4v1软件适配待原生验证。归档使用新phase `mod4v1-scut-adaptation-final476-eval477`，唯一record一次；旧476phase和全部旧tagobjects不动。保存的后续回执通过ordinary supplement追加，postGit验证只在工具输出中显示。
