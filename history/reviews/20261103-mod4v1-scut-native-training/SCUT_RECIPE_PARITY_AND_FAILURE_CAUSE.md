# 公开台阶训练配方与当前任务的差异核对

结论：确有实现错误，也确有训练配方差异；当前0触台的唯一主因尚未隔离，不能拿18,540行索引或CPU通过宣称“一比一正确”。

| 项目 | 公开rough_rotation_stair保存配方 | 本轮实际jump270 |
|---|---|---|
| 初始策略 | flat_direct/model_8000，resume_training=false | 增强MOD4 E0 6cdac1e4…，weights-only/freshAdam |
| PPO | [256,128,64]ELU/rollout24/5epoch4batch/LR1e-4adaptiveKL.01/gamma.99lambda.95 | 同配方；本窗实际60updates，不是训练完公开上限20,000updates |
| Airborne/StepUp/Stair | enabled=false | 三者开启；JumpTakeoff仍关闭 |
| 奖励 | 原保存基础权重 | 基础权重加mod4_stair_wheel_clearance/height各1，状态机会改高度/奖励门控 |
| 命令 | vx−2.7..2.7，wz−2π..2π，heading50%，standing10% | vx=.6、vy=wz=0，无heading/special/standing |
| 高度/episode | .2.. .42m /20s | .25m起步、前扫改高/8s |
| 模型/物理 | SCUT机器人与公开参数 | 人类指定增强MOD4v1/400N/50-100-400/fullD0-D7，必要模型替换不能称逐字相同 |
| 场地 | 原rough训练布局 | 人类明确只对齐出生/相对台沿，中央1m、四边270mm；这是已选择范围，不因此擅自恢复rough |

公开agent.yaml明确使用flat模型8000做起点，所以华南虎这一公开台阶配方有成熟平地初始化证据，而非仅凭推测。我们也用了成熟E0，但同维数/权重strict加载并不证明输入含义和动态分布兼容；需要原与适配后观测逐槽在同一原生端点比较。

本轮实际20k/60PPO/2880万样本：独立80全部0top/0wholeclear/0leading/0strict。末次训练显示track_height_square −2.3242、两项新增stair奖励0.0000，Stair state ratio约.0199；这表明当前记录中高度代价和稀少台阶状态需要追查，但四位小数日志0不能证明奖励函数未执行，也不能仅据此断言数学符号错误。第一轴100%裁剪、前20hip目标超+.5rad为真实现象，仍不能单独给出因果。

曾发生的critic错位、clip遗漏、debugclock时序及最新SOURCE_PATHS启动错误均为真实工程问题，旧失败保留。最新源码路径/失败exit修复通过有限CPU与远端metadata验证，尚待原生运行；原E0对照首试失败于读取模型和physics前。唯一定时器7512等standingV23 exactownrelease后执行未消费REV3；不原样重训失败小时。
