# 为什么没有接管BALANCE（仅使用已保存bounded EVENTS/REPORT）

实际.31开始SHAPE，2.31进入VERIFY后一直没有BLEND；6.00日志明确`startup timeout6s`并六轴请求清零。不是后处理异常使已经BALANCE的控制器丢失结果。
VERIFY抽样3/4/5s的estimated pitch=.6716603/.6975282/.6735058rad，encoder对current qref最大差=.0957659/.1108205/.100808rad，分别不满足已锁的pitch<.15rad和qerr<=.04rad；这些采样及相位序列支持未形成.5s ready hold，不冒称对所有未保存的逐帧ready分项另作证明。rootZ私有高度不参与controller ready门。
3/4/5s双轮请求均为+5.7759097744Nm；全程leg请求峰值17.69/16.74/18.59/16.65Nm，低于40Nm。请求饱和/跟踪差/倾角同现不证明轮真实可用力矩、接触身份或唯一机械原因；68.9MB physics未读，禁止补造。
末post6.01s truepitch=.633385852rad、estimated=.668698823rad、rootZ=.277183204m；与initial约.38369rad/.23714m相比并未收敛到upright。原601/12020消费与后处理`runtime_receipt` AttributeError分别留账，不生成伪result/完整成功率，不择新gain、不重run。PH10pending。
