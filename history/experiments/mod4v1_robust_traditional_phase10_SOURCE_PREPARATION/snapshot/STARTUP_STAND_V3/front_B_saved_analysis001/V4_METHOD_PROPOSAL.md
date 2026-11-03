# V4最小方法提案：先验证支撑几何转换，再轮姿态捕获（未实施/未准入）

B事实：2.31s eligible只说明q误差/qd满足代理条件；同时true pitch≈.608rad、随后double-support-all20-samples bins=0。对准后最小|POST pitch|仍.5355rad，末Z=.27293m；不是已直立。见[8事件](<EVENTS.json>)与[19行报告](<REPORT.md>)。
**值得独立检验“先展开/抬升并转换支撑，再轮对准”而非继续把nominal joint姿态当站姿**；现有数据没有证明单纯加长必能解除guide或稳定，不能将其写成既定原因。
公开delta20 q7的hip=.00253607567、delta=.2，故绝对crank=.20253607567；它是另一个几何/平衡设计点，不是把hip/crank都加同一h。[公开q](<../../TALL_ROUGH_BANK_V1/gain_delta20.json#L3-L10>)只作机制说明，本提案不选该点为新目标、不取K/ff/长度新值。
WorldLeg V1实际只用estimated pitch限幅/限速共移hip并保留delta，注释也不承诺world clearance；不是真rootZ控制、GRF规划或地面起立。[V1](<../../ROUGH_WORLD_LEG_V1/controller.py#L17-L34>)。
WorldLeg V3是seen_drive之后stop_capture按previous shaped-v缩放该shift；用于有行驶前缀的停止消偏，不是从摊卧起身的状态机。[V3](<../../ROUGH_WORLD_LEG_V3/controller.py#L15-L26>)。
旧R40四案原screen0/4，虽部分前进/接触改善；R42单个nominal4cm有原gatePASS，也仅证明那一行驶/停止case，不证明躺地起立或fullDR6cm。[R40](<../../reports/R40_WORLDLEG_FACTS.json#L1-L26>)；[R42](<../../reports/R42_NOMINAL4CM_FACTS.json#L1-L25>)。
|拟阶段|最小方法和所需绑定（无新增参数）|
|---|---|
|OBSERVE/锚定|沿用自然沉降fixture和fresh sensor gate，区分measured q与合法ref投影；不upright reset/teacher force。|
|SHAPE_SUPPORT|把共同摆角h与伸展delta分开规划，参考需同时考虑实际AHRS方向、q/qdot及机械/driver边界；目标是可检验的支撑几何转换，不是只追已知站姿q。|
|条件捕获|关节跟踪eligible不可直接授权轮pose对准；需明确传感器可见的支撑/姿态/轮速/剩余travel适用域。guide是否卸载没有已绑定在线观测时保持未知，private contact仅离线核验，不入控制。|
|VERIFY/BLEND|保持原就绪/超时/encoderTravel/私有真实双轮无非轮3s/XY/高度增量等gate；未站稳则保留失败，不靠放宽门或延时补偿。|
第一项最小验证建议：先在另批预算下检查“自然初姿→候选支撑姿→名义平衡姿”的参考可达性、速度/相对角/支链奇异域、弹簧与signed-DC力矩余量，明确指令FK不等于真实contact/支撑成功；本次0FK/0模型/0新proof。
只有该方法与坐标/端点/支撑观测边界另行锁定并获父审批，才有新synthetic/单独新ID nominal研究；不可直接搬旧WorldLeg gain、.48margin、delta20参数或旧terrain成功率。
轮阻尼/pose请求与实际driver受限τ仍分开；proxy>.50不等于真XY越界，也不证明打滑。B原fail、全部旧源/分数/限制不改，无B重跑/自动V4。PH10pending。
