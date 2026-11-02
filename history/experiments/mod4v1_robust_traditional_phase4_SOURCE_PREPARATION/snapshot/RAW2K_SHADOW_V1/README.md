# RAW2K_SHADOW_V1 — 新信息分支，只作传感器shadow

**交付等级：已完成模拟发布链与新TRAIN采集验证；非旧benchmark等价难度，非实机2k采集，未用于控制输出。** H1/H2/H4、旧COM置信cap和FSM门槛保持不变。

## 为什么增加这条分支

[先前提案](<../INTEGRATED_COM_WINDOW_V1/MINIMUM_2K_CAPTURE_PROPOSAL.md>)指出，100Hz BODY均值丢失了窗口内R(t)与proper acceleration的相关项；窗口恒等式并不能凭均值补回这些信息。本分支保留模拟器本来以2kHz生成的IMU/编码器路径，但在producer边界内给每个源窗口添加**同一个原100Hz已抽出的D1/D2 offset**，并让整个窗口按原D3返回epoch延迟。

```text
y_i = x_i + b_window
mean(y_i) = 原100Hz noisy mean + 浮点roundoff
```

同窗差分会消去共同offset，因此这里确实暴露更多、较干净的窗口内变化。**不声称旧H4等价、不声称IID2k噪声，也不把D1噪声再除√20。** 原100Hz authoritative mean直接保留，raw重算mean仅到roundoff相等，未调整末条样本伪造bit-identical。

## 实现与数据隔离

- [publisher](<publisher.py>)是producer-private实现；clean raw/offset仅存在其私有缓存，不进入消费端projection。
- [派生物理采集桥](<../physics_bridge_raw2k_v1.py>)只增加关节/IMU读操作。移除两条只读hook后，actuation/contact/mean累积方法的AST与原v3完全一致；[零物理AST收据](<BRIDGE_PRECHECK.json>)保存来源SHA。它没有改变模型、PD/D4/motorGain/signedDC或接触。
- [grade桥](<../physics_bridge_raw2k_grade_v1.py>)保持原v4当前freejoint grading；不把grade返回给估计器。
- 原100Hz packet仍是V4估计器/P25+heading2的唯一控制输入，2k数据独立写到sensor-only projection文件。publisher完整性错误会终止该新采集case，未宣称所有故障路径或wall开销与旧系统相同。
- 全部消费端准入路径只列于[SENSOR_ONLY_MANIFEST](<SENSOR_ONLY_MANIFEST.json>)；原全trace/result/DR receipt是父级grading材料，不作为后续估计器输入。

## 时间与端点语义

- 稳态每源窗口20条样本、各500µs，100Hz源epoch为窗口末端。
- 每条raw的gyro/proper来自mj_step的**pre-step dynamics阶段**；采集器事先复制同一阶段q/qd/wheel-rate，因此这些raw字段共享sampled_us。末条raw是source epoch−500µs。
- `endpoint_joint_pos4`是原100Hz packet的窗口末端位置；`mean.joint_vel4`和mean gyro仍是窗口均值，**不是该位置端点的瞬时速度**。
- 后续COM窗口应选raw中同时间的q/qd/gyro端点，或明示额外对齐模型；不要把原packet endpoint q与旧mean rates直接当同步端点。
- Boot为1条instant/0 aperture；10ms D3会重复该已经加噪的boot包。重复source payload SHA保持一致，不重抽、不拼新旧通道。拼接连续2k路径时先去重source并单列/舍弃instant boot，避免将boot与首个full-window中相同物理时刻的不同噪声构造重复当独立样本。
- 没有末尾flush，最终尚未被100Hz消费的collector窗口保持未发表；published样本总数不等于全部physics回调数。

## 验证事实

[Mock单测](<attempts/001/RESULT.json>)61检查/0失败、0物理；覆盖数学均值、共同offset、D3/重复boot、cache隔离、严格字段白名单、时序/非finite/changed duplicate锁存。该fixture最后fault_latched=true是**故意注入changed duplicate后的预期结果**，不是运行采集故障。

[真实模型boot准入](<admission001/RESULT.json>)禁止mj_step，0物理步；projection有效、authoritative mean逐array相同，原估计器/控制器给出有限命令。

[R38新物理批次](<../batches/r38_raw2k_shadow6/BATCH_RESULT.json>)：名义stand2s、forward6s，固定新TRAIN4211–4214各forward6s，**6/6完整且过原短时筛选**；3200控制帧/64000物理步。4个DR病例全部保持D0–D7，分别出现0/10ms源延迟。它们是信息采集实验，不是新的robust holdout或技能毕业。

[独立消费端QA](<capture_qa001/RESULT.json>)：48020检查/0失败，0新物理；3200帧全部通过schema/源epoch/延迟/原packet均值比对。authoritative mean字段与原控制trace的对应packet数组完全相同；2k raw重算mean最大误差约2.132e−14。共发表63848条样本（包括2条重复boot），去重source后63846条，不当独立成功试次。每文件的原producer SHA/字节数已引用，没有为归档重新hash大raw。

## 仍未证明

没有给出接触/离地可信cue，没有提高COM/FSM confidence cap，没有新增已安装传感器/BSP或实时性资格。当前R38只有短时stand/forward；没有同时采集独立2k世界COM/外接触力真值，后续可比较离散传感器functional/模型预算，但不能用这批数据直接宣称连续时间真实COM窗口误差已测得。更动态的spin/jump验证需另建新实验，明确独立truth-grading与sensor-only边界。
