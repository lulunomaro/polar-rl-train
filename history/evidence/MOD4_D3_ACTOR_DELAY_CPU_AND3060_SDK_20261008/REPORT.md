# D3感知0/10ms的实际actor管理器已在3060独立验证，当前4090训练持续

在218生产冻结源码之外隔离建立221源：旧218逐字不变，明确复用已有D3反馈队列数学，新增actor接口和12项CPU边界合同。噪声/整回合bias先注入raw反馈，再按各环境episode的0或1个100Hz控制周期延迟，最后使用原manager scale；不是2.5ms物理步延迟、50Hz采样或动作延迟。BODY矢量保留采样时帧，不旋转到应用时帧。35actor/38cleancritic/6action、commands/height/lastaction/mode/wheel-position槽、plant/task/reward/hardware保持。

两个新的immutable包分别delay off和0/10ms on，由原3060单GPU锁worker执行10env×300control、3秒真实SDK，不修改旧worker，不阻断4090的原范围PPO。用已完整旧技能验证25211 actor生成clean输入动作，actual noisy+delayed manager仅用于独立审查，不能把该SDK视为噪声闭环能力回放或D3学习。

原actor manager的五类反馈每类3000个环境采样读回：803次age0us、2197次age10000us；局部reset选中[1,4,7]产生3次warmup age0us，其他行完整队列和episode不变。实际sample/apply tick差与us相符，same tick不推进noise或queue。最大manager公式误差4.76837e-7；critic保持clean，原不延迟槽exact。两case全初始root/q/参数、末态root/q/参数在固定clean动作下bit-exact；这是本次同机隔离读回，不是跨GPU动态bit-exact。

两case exit0、taskreset0、非有限false、闭链峰.547196mm/mimic.001691456rad，实际10articulations/60closedloops/32-4/2.5ms读回。6份probe/result/manifest返回字节exact，assets仍实际694e9d54USD/importcontract/原引用，无重新导入/live覆盖。两进程wall98.511858s，传输5.538522s，2秒采样显存峰2765MiB不是连续峰。

这里只接受manager时戳/缩放/cache/reset/cleancritic的SDK合同，不称D3已开训、毕业或全平台能力通过。此probe没有保存完整physicalcallback计数，不能编造1200回调证明。下一步仍需真实4090新范围20k物理/回调、完整新增delay state/optimizer/RNG和新episode恢复合同、128x2/20kx4完整PPO权重弃用，再在实际完整保存/孩子退出/active明确/同canonical两锁安全边界接新唯一有界D3入口。

第一CPU fixture多传tick、第一publisher局部三引号parse错误发生在CPU/连接发布前，原错误保留并通过新的显式fixture审查及编译修正；生产无故障。所有准备/发布/review once已执行，不重跑旧入口。当前4090 block2继续D1+D2，预算230h/六扩展各一次不变，本次新增PPO/预算交易0。主计划v1.5 SHA未改，未开legacy bundle或40ms/动作延迟。
