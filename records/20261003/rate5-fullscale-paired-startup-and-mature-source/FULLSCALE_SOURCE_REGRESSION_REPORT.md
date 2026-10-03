# 同源4/5对照与预选成熟源回滚

原16450的5档物理预检15.265deg倾角拒绝后，未开PPO、未改门槛。实施两份20000env×120steps1.2s冻结只读诊断：同16450/seed20260927/white_v2，cap4和cap5，保留完整初始root/q压缩数组及SHA、逐环境峰倾角/高度/峰时刻和最坏环境时序。源码只添加读回，未修改力、随机数、奖励、动作或reset。原cap5物理指标、实际参数、raw contact字段严格复现，完整root/q数组逐项array_equal。

两份都是env6065、group5直行+1.5m/s/yaw0在step34（0.35s）出现15.265189deg。groups0–7全部逐环境倾角/高度/峰时刻bit-exact；只有纯±当档上限的groups8/9变化。纯5两组全2000样本最坏峰倾角约4.45/4.99deg，旧直行异常没有由cap4→5引起。本受控证据只排除该特定异常由新增yaw上限造成，不能推广到实车或所有6档滑移问题。

随后只检查AUTONOMY_STATE预先指定的last paired mature：model16425、SHA63662952ea6be6ca6c259a0563fe2495cefc0ebadf9eb729c69ec1e92aba9075、cap4/white_v2。未遍历其它权重或挑选最好样本。该正式策略已有auto0023两seed nominal/white2 flat/spin八份原协议通过和严格初始配对，CPU68浮点张量完整有限。

用16425进行同seed/white_v2的20k5档检查，完整初始root/q与16450精确相同；原物理门控通过，最坏峰12.399391deg，env6065为11.653218deg。闭链/材料/有限数与承重法向合同通过；原combined=false（最坏高度差70.949mm）仍保留，未宣称1.2秒姿态/15秒技能全部通过。说明这次预检异常取决于两个权重对同一初始条件的响应，不证明监督器、参考点修复或DR造成退化；两个源及全部报告均保留。

三次新全量诊断均无PPO，完整账本字节不变，charged165433.3585538864、总252000保持。下一正式源采用预选成熟16425的完整actor/critic/optimizer/std/iter，较最新16450少25轮；不从零、不重置std、optimizer或预算。最新源的5拒绝和旧6拒绝记录保留，新的明确成熟源试训是独立续接，不以新报告覆盖旧失败。

原始root/q数组在目标机报告路径索引，不提交大轨迹；原raw JSON、COMPARISON、MATURE_SOURCE_DIAGNOSTIC、逐组REVIEW和只读源码保存。本记录为诊断/源回滚选择证据，正式试训启动/保存需读取独立TARGETED_MATURE5_ENTRY_RETRY1及PRODUCTION_VERIFIED。
