# 完整恢复缓存别名：原加载器对照与整包入口复制修复的真实CPU结果

这是软件层实测，**不是原专家技能提升、native GPU恢复或PhysX逐位续接证据**。旧源/失败均保留，修复尚未安装到native训练树；当前未选择继续质量欠佳的A1 legacy GPU训练。

| 新CPU用途 | 原加载器对照V2 | 入口整包复制V3 |
|---|---:|---:|
| 实际remote返回码 | 1（预期严格失败） | 0 |
| 完整14项负例 | 14均挡住，无unhandled_error | 14均挡住，无unhandled_error |
| 真实同view完整恢复/有限增量 | 3→5 | 3→5 |
| 恢复并继续的四模型/四optimizer/replay/RNG/history/计数 | 已核验 | 已核验 |
| 保留decoded CPU root的值不变 | 否，optimizer step/exp_avg/exp_avg_sq别名被修改 | 是 |
| 保留root张量版本不变 | 否 | 是 |
| 原serialized bytes不变、一次open/hash/decode、后续PT重读0 | 是 | 是 |
| native专家BPTT计数 | 0 | 0 |

原始 [V1](<reports/QUALITY_MICROTRAIN_TORCH_CPU_V1.json>) 曾在第二个负例的错误fixture ordering处退出，positive段3→5已执行但负例未完成。NEW [V2](<reports/QUALITY_MICROTRAIN_TORCH_CPU_V2.json>) 只修正stale metadata的attempt/optimizer/verified及checkpoint counts为一致4，再用真实payload3验证正确层级；它完成全部14项负例，仍因whole-root严格不变性失败，未降低接受标准。NEW [V3](<reports/QUALITY_MICROTRAIN_TORCH_CPU_V3.json>) 仅换下述新core，全部同样检查通过。

新 [core-v3](<source_quality_microtrain_resume_alias_v2/ctx_reward_full_resume_candidate_v3.py>) 为36941B、SHA `20fd4945a0f2345c17505316560ae6d358fcce147c6988f62a08d867e084e749`。相对原811源只增加 `import copy` 和 `load_full_checkpoint` 首句 `payload=copy.deepcopy(payload)`；复制整个未知root并保留副本内部memo关系，不筛字段/切replay、不多解码。父自行实核移除这两处后全模块AST与原相同，见 [source caller/proof](<reports/RESUME_ALIAS_CPU_V2_V3_CALLERS_SOURCE_V1.json>) 和 [最小diff](<source_quality_microtrain_resume_alias_v2/CORE_V3_WHOLE_INGRESS_DELTA.patch>)。

实际调用仍先把单次缓存decode得到的完整root传入真实loader，复制发生在loader内部；不是在外部先复制而掩盖原路径。环境是明确的一次fresh初始化+streamcut和新live历史，非假装PhysX接触warmstart恢复。CPU原模型PT/SDK/GPU/canonical/原锁/评分轨迹操作全0，只使用这两个新用途自己的synthetic完整checkpoint。

[汇总机器证据](<reports/RESUME_ALIAS_CONTROL_FIX_ACTUAL_CPU_COMPARISON_V1.json>) 只消费已发布JSON，无重复测试或模型/原raw读取。未来若使用新core，两个logical aliases和新source index/manifest/worker-producer guard必须明确版本；旧13件proof/原811/旧7c guard未被静默替换。
