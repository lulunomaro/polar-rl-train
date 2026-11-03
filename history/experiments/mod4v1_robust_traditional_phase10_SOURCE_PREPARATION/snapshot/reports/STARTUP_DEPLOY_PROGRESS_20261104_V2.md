# MOD4v1 摊卧启动与真实旧工程接入：第二份进度报告

**结论：摊卧启动起立仍未通过原始验收；旧工程已产出首个真实 ARM 目标文件，完整目标构建与实机接入继续核定。** 本轮新增两个真正物理案例，不以解析跟踪预检代替站起。

## 1. 摊卧启动：V3A/V3B 实际结果

两案都从同一自然前倾落稳状态开始：初始机身 pitch约0.38369rad、rootZ约0.23714m；仅time0一次初始化，无途中root重置或辅助力。保持完整MuJoCo接触/闭链、0.5ms物理步、100Hz反馈及原执行器链。本轮是 nominal seed0 的机制调试，不是新增全DR验收。

| 新方案 | 实际控制 / 物理步 | 结果 | 最大平面位移 | 机身高度增量 | 末端 pitch |
|---|---:|---|---:|---:|---:|
| V3A：120/4腿跟踪＋轮速阻尼 | 601 / 12,020 | 6s起立超时，无BALANCE | 0.10205m | +0.03695m | 0.60957rad |
| V3B：同腿控制＋满足传感器条件后轮姿态对准 | 298 / 5,960 | 轮转行程估计超过0.50m，无BALANCE | 0.36251m | +0.03579m | 0.60144rad |

- 两案都有正式result，launcher returncode0且software_failure=False；**物理技能验收均False**。执行成功不等于技能成功。
- V3A末VERIFY腿参考最大误差约0.071rad，相较前一V2约0.77rad显著收敛；但机身仍约35°前倾、rootZ仅0.27409m，导向几何仍支撑。关节追到附近不等于站稳。
- 对V3A新控制流进行一次601行读取，核得369个实际传感器eligible帧，首次2.31s。仅在此前提和A原门False后，才为B单独冻结44源、独立审阅并签批；没有拿synthetic eligibility替代真实前提。
- B触发的是**轮编码器转动推得的行程阈值**；实际最大平面位移0.36251m，尚低于0.50m。二者差异不是单独的打滑证明，也没有将阈值放宽来制造通过。
- 整段guide接触样本：A12,000/12,020，B5,407/5,960；两案hard contact样本均0，但末连续稳定段均0s。

原验收门保留：进入BALANCE后末连续3s，每个2kHz支持样本均双轮承重且guide/hard接触<=1N；100Hz姿态、速度、关节误差达标；rootZ>=0.30m、高度增加>=0.05m、最大平面位移<=0.50m。未将这些门改成“超时走完”或只看关节位置。2kHz采样之间的连续时间不另作证明。

来源：[A正式结果](<../results/startup_front065_tracking_v3a_nominal1/result.json>)、[A一次读取分析](<../STARTUP_STAND_V3/front_A_saved_analysis001/RESULT.json>)、[B正式结果](<../results/startup_front065_tracking_v3b_nominal1/result.json>)、[原方法与保护](<../STARTUP_STAND_V3/METHOD.md>)。

## 2. 真实旧工程：从漏选依赖推进到实际ARM对象

- V3A首次真实ARMCC编译停于器件头；从原ZIP精确补齐1,350,860B器件头后，V4推进到CMSIS-RTOS头。
- 只检查旧manifest的编码漏选类别，确认另缺一个53,065B的原始RTOS头；实测cp1252严格解码兼容，compiler仍用原始bytes，可读UTF8副本分离保存。原ZIP、旧封存工程不变。
- V6使用已有ARMCC5.06u6.750诊断变体，**main.c实际编译exit0，产生7,804B ELF32 little / ARM / v7E-M / Thumb2 / hard-float目标文件**，随后fromelf成功读取属性。
- 编译成功前缀为1，但原FILE-only ABI reader未在FILE层见wchar/enum，按当时gate停下；已保存SECTION证据对三个函数section明确给出wchar=2、enum最小够用容器策略=1。不是已证ABI不兼容，也不是“所有enum都1byte”。正在进行分层属性核定。
- **剩余161C＋1ASM尚未启动，未链接、未刷写、未实机通信。** 本轮不是原uVision/u4.422构建的精确复现，也没有把旧电机、旧几何标定当MOD4v1绑定。

来源：[V6实际报告](<../MOD4_DEPLOYMENT_TARGET_COMPILE_V6/REPORT_V6.md>)、[预算与属性事实](<../MOD4_DEPLOYMENT_TARGET_COMPILE_V6/FACTS_V6_FINAL.json>)。既有[stage1旧工程派生包](<../MOD4_DEPLOYMENT_PORT_V1/mod4_deployment_port_stage1.zip>)保持原版，不把新诊断产物冒充已链接固件。

## 3. 接续任务与保存状态

1. 已委托对B新控制流作一次有界诊断，区别“释放非轮支撑/抬高”和“带倾角移动”，再提出展开腿与姿态捕获的下一最小方案；尚无新FK或物理许可。
2. 对现存ARM对象和已保存fromelf输出进行FILE/SECTION属性继承审阅；不重编首个main、不追加探针，核定后再审剩余TU是否继续。
3. 所有原案例、失败、源锁、真实producer metadata保留；分析脚本首次JSON键错误发生在raw.open前、原始脚本和一行schema修订分版保存，未重物理补账。
4. [PH10归档截止草案](<../ARCHIVE_PHASE10_STARTUP_V3B_TARGET_V6_CUTOFF_DRAFT.json>)已保存，尚未执行本阶段Git record/commit/push；原PH9历史不改。

Goal保持active。全DR摊卧恢复、270mm跳阶、停启换向和实机/HIL验收仍独立开放，未由本轮名义案例或编译对象替代。
