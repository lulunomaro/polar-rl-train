# PC3_CANDIDATE_BUNDLE_V1 — 无发送数学候选服务

**`candidate_math_valid ≠ send_permission`；所有可用输出的send_permission恒为0。** 只有现有C3估计/P25/DC数学组合，没有dispatch/backend/enqueue、FSM、MPC、Power、driver或发送资格。最终封存状态见[VALIDATION](<VALIDATION.json>)与[receipt](<RECEIPT.json>)；[INDEX](<INDEX.json>)列新组件文件，不是全旧树清单。

## 已保存的真实证据

| 项目 | 结果 | 记录 |
|---|---|---|
| 原3200固定raw fixture的新API组合QA | 268829 checks/0；153600输出f32逐bit、73600编译fixture值和9600gyro值均0差异 | [saved comparison](<COMPARISON.json>)、[新raw输出](<host_attempt_01/CANDIDATE_RUNS.jsonl>) |
| internal/effective shaper区分 | 238行v/w确实不同；两套字段分别逐bit匹配 | [固定fixture receipt](<FIXTURE_RECEIPT.json>) |
| 新typed/native测试 | 首轮1583/1，修正测试oracle后1583/0；原失败保留 | [首轮失败](<host_attempt_01/run_native.stderr.log>)、[新版通过](<host_attempt_02/run_native.stderr.log>)、[错误说明](<ERROR_REPORT.md>) |
| 有界逻辑时钟插点 | 25项，覆盖5阶段budget/rollback/unavailable与1ns age/expiry越界，均无候选/send | [原始CSV](<host_attempt_02/CLOCK_INSERTIONS.csv>) |
| 实际C++调用C对象 | PASS，包括原command.enable=0保持disabled | [CPP输出](<host_attempt_02/run_cpp.stdout.log>) |
| 新M4/M7对象 | 首次2/2严格编译；M4 7868B，M7 7320B | [ARM build](<ARM_BUILD_01.json>)、[对象事实](<OBJECT_FACTS.json>) |

有效新host断言合计270412/0，CPP另列。3200通过后未重跑，C3/C2与新CB1核心未因测试oracle修正重编；新版只重编新native测试并首次运行已编CPP。随后分析只读取saved输出，没有再执行测试、编译器、SDK或物理。

## API / 生命周期

- [公共头](<cb1_candidate.h>) / [实现](<cb1_candidate.c>)：`cb1_config_default`→显式数学data/time/session合同与C3参数→`cb1_init`→显式`cb1_arm`→`cb1_step`。默认unbound；geometry/radius/offset由caller提供并经过原C3验证，没有自动采用硬件校准。
- arm仅声明SUPPORTED_UPRIGHT或STATIC_GRAVITY数学先验，不是operator/send许可。SUPPORTED显式先验可接有限零proper加速度；STATIC需要原C3静止重力条件。未知/空mean仍错误。
- 原`pc3_command.enable`按原值观察；0或unknown不会伪装1。disabled在P25前返回无候选并latch，之后要显式init+arm。每个有效控制tick仍满足原P25严格10000us周期，没有新增任意period或disabled监测模式。
- 固定caller-owned存储、无heap/VLA/内部可变全局。host sizeof context/workspace/output/input为1280/720/416/272B；只是host值，不是ARM stack/RAM/WCET测量。
- 唯一数学顺序为原`estimator_update`（held packet内部调用view）→`p25_step`→独立数组上的`original_dc_clip`。未调用`pc3_cycle`，源码包和host链接均不含dispatch实现；[nm证据](<host_attempt_02/new_core_undefined_symbols.stdout.log>)只列数学依赖。

## typed bundle / epoch合同

- STATE14、REF14、MATH row6、GUARDED row6均独立复制。row6=LH,LC,LW,RH,RC,RW；state14[4/6/11/13]仍为crank-minus-hip delta/rate，不是FK knee。无物理front/rear、符号、reducer或CAN绑定。
- `internal_shaper_v/w/a/internal_yaw_integral`与`result_effective_shaped_v/w/result_shaped_a`分开。前者是内部速度整形状态，后者v/w已过原速度包络；result a按原C3定义仍等于内部a，不冒称缩放后的实际速度导数。
- 明确source_sampled、observed_arrival、estimated/computed、drive、window_begin/aperture/count/sequence、session/frame ID和published_ns。packet/drive必须同session、同frame identity、同sampled epoch；新source ID/seq/stamp递增，同epoch hold要求raw及drive字节不变。arrival可为本次重投递时刻，但从不刷新source stamp。
- `gyro_boxcar_end_labeled_body3`是声明aperture的boxcar，time label是window-end/source epoch；bootstrap可声明aperture0/count1。它不是瞬时packet-end gyro，也不宣称与endpoint encoder或aged STATE在同一瞬时body frame同步。
- derived `attitude_roll_held_at_source`保持source epoch；STATE view仅前7分量age-predicted，其余分量保持raw-epoch语义。没有把gyro/roll旋转到aged body frame。平均窗口收集、真实采样与identity来源仍是producer合同，不是本服务实测证明。

## clock / fault / ownership

- available monotonic u64 ns callback，明确opaque全extent；ns/1000向下取整只喂原数学API，输入us→ns乘法必须无overflow。5阶段前后/最终poll用完整ns核对source/drive age、command expiry与外部cycle_start相对budget；外部起点可早于本调用。available=1的零ns合法，loss/backward/unknown availability均错误。
- computed/estimate时间保持entry的floor-us，published_ns单列最终poll时间；不会把计算结果重标成post时刻的新测量。最终ns检查可比旧floor-us条件严格不足1us。没有返回后driver或完整总链期限资格。
- 所有普通fault输出candidate全部清零、math_valid=0、send=0并latch；无旧候选cache/replay。C3数学状态可能在晚期fault前推进，之后必须显式init+arm；这不是transaction/actual-held反馈接口。
- 所有input/options/config/context/workspace/out及clock opaque范围独占且不重叠。out自身alias时为**UNUSABLE**，以ALIAS返回为准，不读取残留valid/send；为保护源数据不清覆盖其上的out。context与源重叠时同样不写源来伪造latch，需用分离存储显式重建。caller保留的旧输出副本不被追溯撤销。

## 构建 / 打包 / 范围

- [小source ZIP](<cb1_source_bundle.zip>)仅2个新runtime文件、6个逐字未改的C3/C2依赖和[BUILD](<BUILD.txt>)，保留相对目录；不含fixture大表、SDK、worker、parser、dispatch或新calibration。C3公共头中的dispatch声明并不代表本服务调用/链接了它。
- [预注册预算](<NUMERICAL_BUDGET.json>)在新代码执行前冻结，逐bit容差0未改；[ARCHITECTURE](<ARCHITECTURE.md>)和[17个实际引用](<SOURCE_REFERENCES.json>)给出小范围来源。旧saved P25 roundtrip只作为f32结果数据，不运行其SDK/旧exe。末次只核对这17引用，不遍历旧树。
- 新ARM对象为ELF32 LE ET_REL EM_ARM、ARMv7E-M Thumb、SP hard ABI、binary32/FLT_EVAL0；仍未链接C3/C2/libm/RT helpers/BSP或运行ARM。M7 fromelf的FP_arch8文字是FP ISA标签，不把CPU变成ARMv8。denormal属性也不是gradual/FPSCR运行证明；库、栈、ISR、WCET与硬件时基均unbound。
- 本服务不继承原C3 dispatch全部bindings/command/queue资格，不产生contact/normal/FSM许可，不接MPC/Power/量化器，不解决driver实际转矩/actual-held提交。完整发送链仍unbound。
- **父当前PH5快照cutoff排除整个CB1；本交付只归后续PH6 pending，不追溯纳入PH5。** 未读H5物理/结果来修改组件；0新physics/GPU/Git/agent/goal/blockedIO行为。
