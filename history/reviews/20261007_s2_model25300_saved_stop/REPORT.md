# S2 1ms训练自行停止的独立审查

2026-10-07原208来源的D1+D2训练产生3次非timeout任务终止；旧clock hook将任何task termination视作整个学习段失败，自行STOP_AFTER_SAVE。原父/guardian/trainer退出，canonical active与S.active_training均空。这是原生产执行器的行为，不是本次3060求解器试验发送信号造成的暂停。

日志指向bad_orientation；旧hook没有逐次原因与时间明细，不编造3次精确分类。最大closure .737551mm、mimic .001953125rad，113760回调与期望exact，不能因此宣称1ms存在闭链超限，也不能以三次episode失败直接证明全策略系统性退化。保留原失败/attention与checkpoint，不擅自修改原全局停止合同或伪造健康完成。

正式25300完整保存SHA4d996ed32096e4bafe2541503a04d8d6ad57252d7c335f7cbca0c545e47a56a4，CPU74浮点有限，actor/critic/optimizer/std/sensor及独立RNG完整；208 source/runfreeze和15份snapshot exact。474实际updates、227520000环境政策步；stored iter差473不是实际更新量。原父已经唯一结清4548.050661563873秒，未重结尾段、未清charged/active或增加预算；余488048.389929秒仅审查快照。

25300尚未行为回放，不登记为成熟或最佳源，完整已配对24827与其他基准保留。当前4090没有trainer，不借缓存STATE称仍在训练。此审查没有新PPO、runtime修改、门槛放宽或恢复入口；2.5ms32/4候选仅另列短范围修复证据，生产采用仍需完整范围验证。批准主计划v1.5 SHA不改。
