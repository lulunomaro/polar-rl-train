# Spring push release：新synthetic与受控entry零步结果

**已完成新数学/源码/受控preloop验证；不是full-model、DR、驱动或PHY准入，不自动物理。**

## 实际功能与API
- 父core只在实际trigger后的push窗口临时以新dict/新tau副本加正tauGas，super一次，finally还原g/end；不修改物理spring、原gain、air h、轮/事件策略。
- 数据是已封[SPRING_PUSH_DECOMPOSITION_V1/ENDPOINTS.json](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/SPRING_PUSH_DECOMPOSITION_V1/ENDPOINTS.json>)：SHA 1b47bb7d75205c907f9116cb658adbb2922e82decee2c9b19c2fab8d86db762e。FF_new=old+tauGas；不是负counter，静态端点近似不等实际DR去弹簧。
- 新entry在真实plant构造前核data/helper SHA、public/gain来源、实际loaded q/tau/absolute pose；默认off不读取补偿table，enabled构造参数为start_gas_tau6/end_gas_tau6。

## 一次新unit事实（不重放旧600/436k或数学27FK）
- BasePosition/NewDefaultDisabled/NewEnabled各500同样sensor-only帧；9129 checks/0；实际phase为101 supported approach、14 push、25 predicted flight、360 capture，没有硬编码push帧数。
- 500默认off的旧tau、legacy log、ground ref/state与observer flags逐bit相同。True模式目标、phase/guards/observer不变；只push按原FF+PD/32clip/roll/yaw/wheel/final40原式对照，最大误差0Nm，push轮同输入bit一致。
- 非push enabled结果在这组相同固定输入下也bit一致；这不表示不同真实闭环trajectory的flight/capture输出相同。原方程相同与闭环状态相同分开。
- 首push1.01s此前launched=False但已applied；g/end identity、所有原gain array bytes不变，ground tau_eq未被overlay alias污染；原trigger guard和inner exception的finally恢复均核过。
- 实际旧Geometry.wheel_kinematics84次≤128，内部planar pose420另记；NominalModel FK0、MuJoCo0。oracle复用已有J，没有增加geometry查询。nondiagnostic wall timer固定0，仅比较math，不作WCET结论。

## actual entry与失败如实保留
- ENTRY首次harness在解析期因第67行__code__and连写失败，尚无main/help/ctor/model执行；原source/log/[ENTRY_FIRST_FAILURE.json](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/SPRING_PUSH_RELEASE_V1/ENTRY_FIRST_FAILURE.json>)与快照保留。
- 父明确批准仅一空格修复，另存[run_entry_once_v2.py](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/SPRING_PUSH_RELEASE_V1/run_entry_once_v2.py>)；先AST parse并验证逆向逐字节=原失败源码，再一次启动原预算，没有重跑unit/数学/core。
- 实际执行new main --help一次、default-off/on两个真实新controller构造与preloop；26 checks/0，5绑定失败案例。fake plant/DR各2，loop/packet/actuator/geometry/SDK/NominalFK全0。
- 真实loaders/geometry/controller/estimate构造/StreamedRows已走；plant/DR/Bounds与large-asset manifest明确fake，trace在首for-loop前停止。EXPECTED ERROR与空trace/physics producer prefix保留，不制造result.json trial。
- Manifest实际写入完整cfg、kind/requested/dataSHA与source records；off dataSHA=None，on为实际缓存SHA。result的actual-hop enabled字段只作AST验证，本轮未运行result结算。
- 所有kind固定NEW_NOMINAL_SPRING_RELEASE_PUSH_ONLY_TRAIN；relative_V3_push_flight_capture_equations_unchanged=False，only_push_nominal_spring_ff_changed=True，flight_and_capture_equations_unchanged=True；后两者仅说方程范围。

## 交父边界
- loop、good/main/local与plant/DR构造表达式最终AST相同；22个锁定source字节未变。新core/entry/binding/unit SHA见[RECEIPT.json](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/SPRING_PUSH_RELEASE_V1/RECEIPT.json>)，输入配置仅synthetic覆盖，不是父将冻结的物理协议。
- 数学cache、core与本次source/results转只读；等待父独立review、sourcefreeze和真正名义准入。没有PHY、旧QA、Git、新agent或goal操作。
