# 72旧训练任务清理候选（未执行）

本次只读盘点120736个文件，未删除、移动、链接或修改远端文件，未触碰训练、GPU或预算。

| 方案 | 具体对象 | 预计释放 | 保留与损失 |
|---|---|---:|---|
| 无损去重 | 7组已逐文件核真完整SHA的不可变输入副本，共164份重复文件；主要为125份重复reset bank和重复来源模型 | 4,637,437,952字节，约4.64GB | 用同盘硬链接保留每个原路径和全部相同字节，另记inode/mtime/nlink变化；不删除唯一内容 |
| 将旧完整训练窗扩展为有界保留 | 清单15个已有passed production FINAL与NODE_EXIT全部子进程等待退出证明的旧训练窗；1450个中途NPZ/配套preupdate文件 | 251,572,674,560字节，约251.57GB | 每窗保留首个及最后两个完整pair；被移除的其余中间原件不可恢复。FINAL、来源、失败模型、正式评测/native原件、完整日志、错误、费用和所有producer路径/大小/SHA历史不删 |

两项候选路径互不重叠，总计约256.21GB。实际释放须以执行后的fresh容量为准。

无损去重的164份文件已在72逐个读取完整字节核对SHA，并核对读取前后size/inode/mtime/nlink以及原NODE_EXIT、mode/uid/gid/device；尚未实际创建硬链接。

旧窗扩展仅是具体提案：已有INDEX、FINAL、NODE_EXIT与fresh文件stat逐项绑定，尚未逐字节重读这251.57GB，不把候选称为已删除或已释放。执行前必须再次核准清单、身份与保留集合；任何不符保留原件并拒绝该项，不触碰当前训练。

此前人类批准的是“允许新目录采用有界保留”，不能据此自动删除旧目录的唯一中间原件。本清单的旧窗扩展需明确批准。

完整逐文件清单：

- `V112_HOST72_IMMUTABLE_DUPLICATE_ACTUAL_FULL_SHA_VERIFIED_REVIEWABLE_CANDIDATES.json`
- `V112_OLD_COMPLETE_TRAINING_PREFIX_FIRST_LATEST2_EXPANSION_PROPOSAL_NOT_AUTHORIZED_CPU_ACTUAL.json`

旧窗范围（仅以下15项，不包含其他目录）：

```text
/home/lc01/Zonglin Li/zonglin2/tasks/T3h4_1810v4/h1
/home/lc01/Zonglin Li/zonglin2/tasks/H1h2_1810p5
/home/lc01/Zonglin Li/zonglin2/tasks/T3h2_1810v2/h1
/home/lc01/Zonglin Li/zonglin2/tasks/T3h5_1810v5/h1
/home/lc01/Zonglin Li/zonglin2/tasks/T3h_1810v1/h1
/home/lc01/Zonglin Li/zonglin2/tasks/T3h3_1810v3/h1
/home/lc01/Zonglin Li/zonglin2/tasks/T3sf_1910v6/h1
/home/lc01/Zonglin Li/zonglin2/tasks/H1h1_1810p4
/home/lc01/Zonglin Li/zonglin2/tasks/T3sf16_1910v21/h1
/home/lc01/Zonglin Li/zonglin2/tasks/H1mb_1810p1
/home/lc01/Zonglin Li/zonglin2/tasks/H1mp_1810p2
/home/lc01/Zonglin Li/zonglin2/tasks/H124_1710b72
/home/lc01/Zonglin Li/zonglin2/tasks/H1r_1710v3
/home/lc01/Zonglin Li/zonglin2/tasks/H1r_1810v4
/home/lc01/Zonglin Li/zonglin2/tasks/H1cr_1810p3
```
