# R63 seed4610：一次只读事件审计预声明

仅新results/r63_spring_release_DR4610的trace.jsonl、physics.jsonl各open一次；总行上限17600，预期800+16000。小result/SourceManifest及旧R60同seed只smallresult；不读旧raw/其他seed/H5/ZIP/mesh，不做2kq推导、FK/模型/PHY/QA/Git/新agent或新参数。

原all-world positive normal总和<=1N连续20ms判operational air，确认time使用该row POST；firstlanding为确认后首total>1N，保留是否轮/guide/hard的真实身份。mainrear-firstflight仅原result时间join原physics row，不新算几何或换whole-robot门。guide/hard用原aggregate>1N逐physics row计，正点全部列出，点数与tick数分开；只保留air起/确认/landing/mainrear及3guide同stage快照，不导出时间窗。

stage time/drivepoint time/force/cache rotation/rootPRE一致；rootPOST另记。按sample_index//20关联控制command、sensor/post时间，记录dt、requestedτ与该stage actual driveτ/速度，不声称传输后同一command或可唯一解释差额。当前landing_position_ref4/weight才是capture参考，legacytarget另标；2k实际单腿q保持UNKNOWN，不从含D1D2 enc积分。

capture/首正weight/observer禁用与恢复依据实际100Hz日志；brake依据config与forward日志；gravity若未独立记录只写继承schedule非实测flag。只描述时序/接触几何事实，不用单案证明唯一因果，不替父选策略或改新旧score。原producer SHA引用、无raw重hash；preexec固定本method/script/小源/cache SHA后才开raw；失败保留source/trace，不自动重新扫描。

catalog Office/ACL无本控制日志审计匹配，使用只读文件和stdlib CLI。PH9pending（新于PH8 cutoff，旧source的PH8pending标记仅历史）。
