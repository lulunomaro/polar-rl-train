# MINIHOP_AIR_PITCH_REF_V1 — 父指定TRAIN假说，先锁架构再code

- Catalog为Office/ACL，无robotics匹配；文件/Python CLI。只写此新目录，不改旧controller/entry/grade/actuator/gain/observer，不读H5/R60 raw、不跑PHY/模型线性化/编译/Git/newagent/旧QA/blocked IO。
- 固定假说由父指定，不从AIR单位响应选择稳定gain：hGoal=clip(.25*estimated14[2]+.04*estimated14[9],±.10rad)，仅原100Hz预测flight内每tick变动≤.01rad。正θ给正absolute leg-reference增量，不加wheel torque。
- 新类继承原Position MiniHop→Landing V3→Observer V2→V1。air_pitch_ref_enable默认False时整条command/prepare_estimator直接delegate，不新算h，不变旧math/state/日志。operator默认仍False。
- 有效enabled approach/push仍delegate原position/next-tick trigger、launch guard、push、observer。time/theta/rate等无效先latched fault/INHIBIT，不继续NaN计算。
- flight中只在super前临时q_start=原q_start+h*ones4，finally恢复原对象；super真实计算140/3腿PD与原25*pitch+4*pitchrate wheel项，不在super后修改tau或补造target日志。absolute LH/LC/RH/RC共转，delta和L/R对称保持。
- first timed capture冻结最后flight h为capture_anchor，仅eq0 hip indices3/5平移，delta4/6不动，K0/K1/ff0/ff1/eq1不变；同时在super前设置ctrl.eq和ctrl.ref[3:7]为anchored eq0，覆盖真实V3 firstcapture u=0不写ref陷阱。随后V3原landing_weight自然桥接eq1，不在flight结束把h清零。这是air-ref反馈+连续capture anchor，不是单改空中τ。
- **先验source风险，不调整hypothesis掩盖：**公开crouch hip=.45417412979711813，XML upper=.50000000583640236，正余量.04582587603928423rad。固定51点[-.10,.10]会检查这个边界；任何超限均保留并使domain gate FAIL/NOT_READY，不扩limits、不缩h范围或gain。
- 51点仅pure公开FK/限位/共旋转，0 model/forward/linearization；600+600是新synthetic输入、不是旧QA/轨迹重放。既有GroundController用原冻结Ad/Bd/Q/R做固定P25初始化不变，没有新plant A/B或新gain profile。
- 派生entry只改package bootstrap、新controller import和诚实source/result metadata；main控制、actuator调用、grade/结果gate AST保持。真实main受控fake plant/DR/bounds与上游asset-manifest backend，仅到第一控制loop前；真实controller/geometry/estimator/StreamedRows初始化，0 step/forward/model boot。大asset验证及真实fullmodel boot在本轮UNKNOWN，不冒称PHY准入。
- 全部参数/容差/一次测试预算见[METHOD](<METHOD.json>)；任何失败保留原source/log/result，不因失败循环改gain/范围/gate。PH7 pending；contact/groundtruth/world position/permission/confidence不提升。
