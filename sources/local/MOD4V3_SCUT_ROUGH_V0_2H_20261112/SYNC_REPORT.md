# 最终Git同步回执

2026-11-12，统一SCUT Rough-v0两小时的完整源码、26份训练PT、2份短探针PT原件、实际失败/日志、8组同批PhysX评测、README和全局模型索引已提交并通过7897代理推送，TLS校验开启。

- 权重/源码最终提交：`9b8925b86bc502dbb48c328420e18944ef9baace`。
- 固定annotated tag：`trial-20261112-mod4-scut-rough-v0-2h-final-01`，远端peeled与该提交一致。
- 分支：`mod4v1-experts-fulldr-rm70`；推送后该分支HEAD与该提交一致，实际查询时刻与main引用见evidence/FINAL_GIT_PUSH_RECEIPT.json。
- 逐个从Git对象实际读出28个PT，bytes与SHA256均等于本地已读回的完整PT，含26个训练文件和2个短探针同字节原件；都是完整blob，不是LFS指针或仅地址。
- 综合继续选r1round2_005m，本轮100m/120m未晋升，原冻结和实车包保持原身份。

本文件和推送回执由后续独立sync记录提交，不改最终权重/源码tag。该sync记录只添加同步材料；其最终远端确认由本次工具结果及最终回复提供，不再生成递归回执。

补录：首次同步回执的普通git add返回exit1，未形成sync提交/tag；主体final提交/28个PT的推送与读回验证已经成功。此处继续同一个已创建的sync记录，使用本项目既有的--sparse -f路径加入方式；原失败执行源码sync_archive.py保留，恢复源码见finish_receipt.py。不重做训练、评测或权重推送。
