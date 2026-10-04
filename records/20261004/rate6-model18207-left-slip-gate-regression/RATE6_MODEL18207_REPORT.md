# 6档18207：原滑移门控回归未过，保留先前17773通过

auto0053原定平地80env与自转88env各15秒已经完成。源18207 SHA955765dbaf93cd28ac66bded1d9408b95b6165960537853a7d483f76f188b2f4在前次自然冻结窗口已独立CPU读取68浮点完整有限；原flat的64已训练环境全部准入通过，旧strict_window=false。rate88/88存活、物理通过、初末实际参数读回通过，但corrected spin_skill=false，legacy_reference spin_skill=true，两种布尔均保留。

交错group_ids逐环境核查只有5个样本因原滑移代理失败：纯+6环境18右轮0.156309m/s>.15，该组仍7/8=87.5%达到原80%组门槛；纯-6环境8、30、41、63左轮分别0.153222、0.150462、0.152507、0.152752>.15，该组4/8=50%而未过。其余9组各8/8通过。所有失败样本的其他原验收项通过；没有NaN、死亡或物理/成熟站跑退化，不能把门控失败说成训练崩溃。

纯±6实测均5.990178/-5.891821rad/s；最坏peaktilt1.571843deg、gap0.672840mm、双轮低载11.500ms，closure0.076432mm/mimic0.001827rad。与17773同seed20261002、white_v2、probe源及完整初始root/q精确相同，权重不同。先前17773的完整单seed通过保留，本次表明6尚不持续达标，不宣称新奖励普遍因果、PhysX材料点滑移或实车认证。原正确link参考点没有改动；不切换到legacy布尔宣布毕业，也不放宽.15。

专项consecutive清零、failed_blocks=1，监督器阻止升8并继续已安排的有界6学习。核验时单一trainer3743137/start23085130从18207完整续训，run logs/2026-10-04_09-04-02_auto_0054_rolling_rate_trial_or_continued_cap6_white_v2，parent3238128/guardian3238171实际身份正常，white_v2/rolling v1固定。最新PID绑定18625 SHA10142fdd913ab5799a3c8f6e3034e083bc826e2235ff2bff75c10a45a17a8675已CPU回读68浮点有限、104原源/123候选源一致；此18625没有15秒回放，不能用训练日志reward或success宣布成熟。GPU69%/14562MiB/49C是快照，近期日志无NaN/Traceback/OOM。

本段deadline约北京时间2026-10-04 11:01:12，核验时临近边界，随后已有自动完整保存与顺序flat/rate；实际子进程和状态可已自然转入评测，勿因cachedPID退出而重启/再发probe。3连续技能失败或旧能力/物理退化保留所有新权重、回实际paired17196/5并hold。另一份策略通过和同候选双seed名义/DR全部原门槛通过前不升8。当前尚有预算，不能把hold或冻结评测当finished。

唯一252000有效PPO秒及三扩展保持，核验余49251.45秒约13小时41分为快照，实时扣active尾段。本轮只读取既有报告、CPU与来源/GPU核验和归档，没有新probe/PPO、暂停重启、物理/奖励/DR/门槛或预算改变。当前原地spin优先，移动/FPS/地形延期，120rpm仍目标。
