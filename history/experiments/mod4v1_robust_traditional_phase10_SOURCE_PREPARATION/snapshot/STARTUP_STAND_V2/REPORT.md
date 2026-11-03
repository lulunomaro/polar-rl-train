# Startup V2：一次新synthetic数学/phase/API检查，不是起立成功

- 状态：PASS_NEW_BOUNDED_V2_MATH_PHASE_API_SYNTHETIC_NOT_STANDUP；METHOD与预算在命令前锁定。
- 新enabled external commands：356；disabled20对(base+V2共40calls)；typed12；主轨迹340帧。嵌套base/GC调用另记，不冒机器人试验。
- 处方轨迹仅解析q/pitch/roll跟踪：.25 SHAPE、2.25 VERIFY、2.75 BLEND、3.25 BALANCE，下一prepare3.26恢复原observer；不是模型积分或真实站起。
- SHAPE/VERIFY exact K[LEG]反馈：距离/纵速/yaw4坐标局部副本清零，pitch/rate按原scale，nominalFF+原roll20/2±8；无并联60/3/120/4。
- samepacket轮速阻尼−.30、cap±2；四独立忽略坐标、非零腿误差/roll轮cap、真实last_tau/log和firstBLEND捕获验证通过。
- feature缺省False严格delegate；operatorFalse即使featureTrue不读packet；20对覆盖DISARMED/OBSERVE/SHAPE/VERIFY/BLEND/BALANCE，输出/log/相关数学状态bit相同(非wall成本)。
- bad轮型/NaN/Inf/missing在base command前INHIBIT，未推进last_command/source/phase队列/GC；其余原输入/prepare/BLEND gate仍保留，fault sticky。
- 新entry V4未import/run；V3 loop/healthy/good/complete/passed/原2k支持gate与driver不变；静态核FullDR.queue_receipt(self)，未call_DR._self_test。
- 所有小源SHA前后相同；0geometry/model/FK/MuJoCo/PHY/DR/旧499/旧raw/Git/newagent。V1原失败与后处理ERROR不改、不补result。
- 该线性反馈超出旧upright域仍待新nominal物理；未证明稳定、stop/真实支持、背躺/侧躺/DR/hardware；父独立review+新ID批准后才另行新PHY。
- [plan](<SYNTHETIC_PLAN.json>) / [preexec](<SOURCE_PREEXEC.json>) / [result](<PREFLIGHT_RESULT.json>) / [core](<controller.py>) / [entryAST](<ENTRY_DERIVATION.json>)。PH10pending，整体Goal仍active。
