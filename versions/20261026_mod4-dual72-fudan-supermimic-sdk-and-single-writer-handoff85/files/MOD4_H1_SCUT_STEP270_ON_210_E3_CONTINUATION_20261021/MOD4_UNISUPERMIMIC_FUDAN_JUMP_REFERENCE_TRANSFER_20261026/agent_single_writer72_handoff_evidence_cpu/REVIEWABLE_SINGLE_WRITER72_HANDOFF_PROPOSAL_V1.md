# 唯一记账权转72：待人类确认的具体方案

**当前仅提案，human_authorized=false；没有建账、复制canonical、迁权或启动训练。** 本机证据已核到83B结清10943.796510219574秒、余额595256.8240613937秒，以及最后fresh检查时active=None、旧owner全部退出。该检查早于单卡主机改Windows；不能冒充当前Linux实时读回。原快照SHA由root提供：`fa47cf989898d9c771f35dcaa1e25330456694fda044502aaf82a5887b205bb1`。

最新完整original canonical JSON的全部字节/逐run历史没有在本次限定证据中恢复。检索发现若干旧日期文件名，但未将它们当作当前完整账本；目录访问拒绝和检索边界保留。遵照root要求已停止扩大旧账检索。因此本方案明确是**新唯一权威的carry-forward边界快照，配合原Git历史引用**，不是逐字节迁账，也不补造缺失旧history。

确认后的唯一新路径为72：

`/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json`

同一目录的两把独占owner锁拟为 `canonical_owner.fcntl.lock`、`all_experts_owner.fcntl.lock`；现有每GPU私锁继续保留。所有新owner/源代码入口必须绑定这一个authority generation及路径。旧210 Linux路径 `/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json` 的记账权在明确确认后永久退役，任何旧owner以后都不得再写；即使旧盘/旧Linux路由恢复，也不得自动恢复旧writer或与72并行。

承接的边界数值保持原样：total2268000秒、9次扩展、charged1672743.1759386063秒、remaining595256.8240613937秒。二者相加恰为原total。83B已经结清，不再重复扣费；不加预算、不增扩展、不退款、不追溯补费或把未知历史拼成完整账本。所有已归档Git提交/tag/原始失败与成本凭据继续保留。

Windows待核9400.860692501068秒、unknown512秒、安全64800秒、原caps11700秒继续单列保留；strict要求86412.86069250107秒不变。这些待核项目在迁权时既不消失，也不被擅自变成已扣费。未来收费继续逐专家actual GO至收到terminal的区间sum-once，保持3900/3600/300边界；CPU准备、空闲及无GO不制造训练费。

确认后仍需：写明旧authority永久退役声明、唯一最后结清run `THREE4090_EXPERT_ORIGINAL_1792994651814636100` 与无active边界，核新两把独占锁/旧generation拒绝路径，审查新权威原子写与失败保护，再进入已有实际源/SDK/native/完整保存准入。未能证明唯一writer、发现未知active、保存/记账失败时，保留原凭据和partial，安全保存后停在所有者边界；不清active猜重启、不退费、不重复扣费、不回退启用旧210。

原private GPU锁、2.5ms/TGS32/4、float32/native160k同源证据、2mm单环境reset、模型/优化器/历史完整保存保护均保持。此次迁权确认不代表放宽物理、保存或技能毕业条件。

CPU纯验证11/11通过：原余额/total/9不变、权限默认false、旧writer不得复活或并存、锁必须同根且唯一、历史缺口不得伪称完整迁账、待核/安全/caps不变、实际GO-terminal只记一次及83B不得重扣。所有测试只操作内存fixtures，未写任何canonical。
