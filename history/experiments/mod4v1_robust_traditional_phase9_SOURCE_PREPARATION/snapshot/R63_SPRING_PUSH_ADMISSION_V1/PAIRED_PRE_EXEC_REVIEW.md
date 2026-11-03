# R63固定paired launcher：条件静态ready，不是launch审批
**ready_for_fixed_paired_TRAIN=true / issues=[]；actual nominal尚未存在或未过门时脚本先停；审查者未读取nominal结果、未launch。**
- 固定4602/4605/4606/4610，两wave各2；旧saved small baseline只读，不重放；完整profile仅剔ID/cohort/seed/nominal/新feature后匹配。
- 先generic binder核actual nominal cfg/kind/feature/CORE/ENTRY/DATA签名；完整bindings必须等独立approval.nominal_bindings；再flat原gate、RM原gate、finite firstflight，非把mainrear当wholebody证书。
- 独立paired父approval锁seeds/sourceindex/launcher/review；每wave前复核source+review checked_sources和approvalSHA，fresh V2 software-stop不改。
- V2软件失败保存actual batch/prefix后停止未来wave；wave后的candidate绑定失败单列并停止未来wave；valid completeFalse/health/guide/hard/gateFalse仍机器人失败，不因此停下一预列wave。
- protocol在首wave前新建，原ID不复用，attempted无最终row与unstarted分列；不以duration推消耗，不retune/换seed/补跑。名义与paired仍需父分别签审批。
- 未执行fixture、旧QA、candidate、模型、PHY、Git或新agent；PH8pending，无硬件/动态资格升级。
