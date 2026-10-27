Ballistic V2最终参考已冻结：MOD4_OWN_BALLISTIC_HORIZONTAL_REFERENCE_V2_FINAL_NOT_ADMITTED.json，724902bytes，SHA 216838d62209881d78039cd71360355b20689aab09c7fa615813fa2a51e4c373。root应绑定FINAL文件。中间表及V1的原控制点通过结果均保留，未覆盖旧source/表。

新增quarter检查发现V1确实仅控制点通过：左轮在age128.25/128.5/128.75已跨前缘但bottom分别.252266/.259763/.267268m，低于.27，原V1 quarter结果false已保留。不能把旧control-grid通过当400Hz执行可行。

V2不重IK、不改q/Z/R或任何其它state列，只改X/VX。flightV优先固定.9m/s。结合所有control点和120..145每.25control的101个插值FK点，X_air可行区间[.210328304,.234200205]m，取中点.222264255m。相应vpre=.122043816m/s，全部pre100低于原.18计划上限/.2ready阈值；ground100..122加速3.53616447m/s²；flight122..145 VX恒.9/AX0，touchX=.429264255；touch后.4s以-2.25刹车，185停X=.609264255到300。公共request100..179和物理command.8原样。

新quarter/control全段无侧壁/平台轮底/footprint违规。pretop前缘和posttouch后缘的最小水平计划余量同为11.93595mm，远端余量477.428mm；straddle期间最小bottom=.286641598，即平台上方16.6416mm。小网格max-min最优也在此中点（11.93595mm），超过5mm设计目标。这是新reference设计余量，不是新物理审计门槛或真实tracking安全保证。

插值rootquat使用最短slerp，q/Z线性只为FK检查，closure插值最大.0001683545768m，原样记录不冒actual验证。没有改source air姿态，也没有把sourcecontact当own接触。原V2 contact IK表仅整体X相应平移，21帧IK未重算；所有非X/VX列逐字不变。

最终metadata把旧control-grid摘要标为provenance，并以当前quarter/control检查替换主要摘要；中间表数值与最终表完全相同，未藏任何数值修复。真实驱动/CoM动量/ready/接触/全body碰撞/原callback成功仍pending；没有模型/USD/mesh资产/raw/NPZ、actor/physics/GPU/SSH/Git/账本操作。普通补档由root负责。
