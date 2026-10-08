D4实际物理动作延迟已补齐完整合同并在4090正式开始稳定训练。实际0/2500/5000us是在2.5ms物理回调可实现的时刻，处于已批准<=5ms通信压力范围；不是原拟议0/.5/1ms的精确实现，也不是100Hz控制队列冒充物理队列。四腿位置目标一组、两轮速度目标另一组，独立episode RNG；队列在原scale/defaultoffset/CAD投影后，原process/apply/PD及gain后torque-speed限幅路径保持。SDK计数先增再apply，实际施力目标应用时刻(counter-1)*2500us，首次转换延迟和hold年龄分列。动作DR是未标定工程压力。

候选243文件=原234逐字不变+9文件。Torch2.10目标CPU10保存恢复合同通过，已通过18数学/10adapter及3060 off/on300control SDK精确复用。新4090 20k在24warmup+120control中576总contact与两组apply回调各576，timed480回调exact，实际Articulation目标误差0/初末参数通过，closure.801881mm、mimic.001827、task0/nonfinitefalse。未新增实物施力标定或子步力矩峰认证；硬件限幅原来源路径精确保持，冻结技能仍读实际动作/torque/clip诊断。

128x2与20kx4完整新范围PPO实际6144/1920000环境策略步，192/384回调exact，CPU88保存完整有限/自己的243freeze与snapshot通过，closure.642261/.987135mm，任务0。预检权重弃用，正式不从预检权重接续。128使用fresh sensor/feedback/action流，20k完整恢复D3流后显式建立新actionqueue，差异保留。两段唯一canonical已分别结账8.039833/214.289975秒，不重复。

正式source为启动时已经完整行为审查的27575 SHAded074be755d5320a4050f69753163800a409d6eaf077fb3b990b686d9547a61，actor/critic/std/optimizer/sensor/feedback/globalCPU-CUDA/named command-physicalDR全部恢复，再新physicalepisode。D3前身没有actionqueue，首次D4 admission明确新队列；后续D4保存需完整queue/targets/timestamps/独立RNG精确恢复后显式清新episode并rebase，不宣称PhysX exactresume。CPU验证不把CUDA Generator序列冒充CPU可恢复序列，真正CUDA roundtrip已有SDK证明；下一块真实恢复仍需自己的startup回读。

实际parent1211569/start59835171、guardian1212716/start59858959、formaltrainer1213775/start59881209实读；run15:16:43_d4_stable_block1实际已PPO并保存27600 SHAd466bb05fcdd99c2b880ce5fea2144fea7ab1b37af55667211b46e8844213644，CPU88/自己的243runfreeze/24snapshot exact。该检查点只是保存证明，D4行为与长段结束尚待实际审查。首block截止epoch1791450833，三块各<=2h，save25/15s本地guardian，健康保存后自动发布3060flat/spin/world且直接续下一块；没有重复45min时钟实验，不等3060评测再训。

D3第三块28648的实际配对结果已另行唯一Git归档：三块合计3226更新/1548480000环境策略步/44普通事件（42姿态+2闭链），最新world64/64、worstabsnetcross.036299213、pure左右各8/8，±1.5误差.017559983/.039577819m/s。限定firstseed-white3/0-10ms反馈，不称全部延迟/全部DR毕业。D4已在最终回放前从27575启动，不为后完成28648热换源；全部候选/旧legacy2mmfalse/raw保持。

新D4 immutable闭环包SHA74200ad6e080c0483f8af95307ae385111a99f54e528ec359a29fcc834d93e18，真实USD/importcontract/引用原样、仅Windows路径适配，无reimport/live覆盖。原3060 demand worker/单GPU锁无需更换，已发布40-d4-anchor三份，新策略块末自动发布50-d4-b1/b2/b3，实际新平台闭环scope尚待结果。第一包误标initial assignment已在任何job发布前独立修读者并保留原artifact；第一次controller读者误猜SDK字段在GPU/账段前修正，全部错误保留，不当生产物理故障。

主计划v1.5 SHA不改，已有S2批准范围内实现，不自行创造新批准。230h/六扩展各一次、预算新增0；冻结CPU/SDK/native评测不计PPO，PPO加载学习保存退出同唯一canonical。healthv3继续：closure2mm仅单env终止/reset并计数，不以有限单峰停全批/降1ms；mimic/非有限/未知/回调缺失仍自己的STOP_AFTER_SAVE。原参数积分数据合同和硬件包络保持；系统性旧技能退化需实际处理。D5下一组须先审实际名义force-stroke/来源和标定状态，不借3500N/m宣称300–700N实物一致。MoEgate未训，S8后续具体批准规则不变。权重/大raw/USD只SHA索引。
