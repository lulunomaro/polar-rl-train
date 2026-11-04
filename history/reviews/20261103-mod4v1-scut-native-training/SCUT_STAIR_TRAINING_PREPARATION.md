# 2026-11-04：按人类要求准备空闲卡开训

人类最新要求“找张空闲卡开训”。已准备`env20000_scut_stairs_1h_20261104`：20,000环境、3600秒保存边界及原300秒安全退出，`scut_stairs`只选固定华南虎保存YAML的inverse-mid阶梯分支，不再要求270mm或首次飞行。6个源码模块及owner/entry/plan，28个共享文本SHA引用；没有复制整树、模型或资产。

来源为上一轮完整final：37,849,545B，SHA`0fdd9463205f739daff8713ade26d937846c832fba25392af4e515edc8904f86`。按原SCUT新任务微调模式载入actor35/critic78权重，保留已学输出与STD，新的Adam/iteration0；不再初始化第一轴，也不覆盖旧模型或恢复旧Adam。增强MOD4v1物理/DR、原奖励/PPO、唯一canonical/reserve及完整保存保持。

准备不等于GO。截至本次本地检查，唯一现存timer58540/create2026-11-04T09:48:09.899519+08仍健康，只等待原peerV25释放，未额外SSH或扫描卡。原peer保存时间10:42:07.432175、安全退出名义时间10:47:07.432175；冻结等待器11:02:07.432175后才核对exact OWNER_STARTED/OWNER_EXIT、ownwait/settled/released及共享锁。不能把此前09:41四卡快照当当前可用状态；不能用另一卡绕唯一计账或原评测锁。

释放后仍由现有timer完成尚未LAUNCH的80首局新场地诊断。回传后审实际motor/height/reward/400Hz接触曲线与保存姿态，使用当前模型视觉读取新图；执行正常但源策略未会上阶，本身不是无限阻止训练的理由。`scut_stair_training_control.py inventory`复用原授权四卡reader，`freeze`根据fresh资源/完整释放及原生审图固定GPU和INDEX，`launch`沿用原完整保存owner与FIRST流程。FIRST24controls/480000实际样本/非零actorcritic梯度和完整首存后绑定唯一postround，保存退出后立即独立评测。

新增两个准备控制脚本已做语法检查；本次没有生产模型解码、physics、优化器、预算写入或native训练。共享远端owner与SOURCE_PATHS未保留本地副本，两次本地错误路径读取及SDK路径定位错误已单独保留，随后使用现有SHA归档对象/实际SDK目录纠正。没有以读者问题派生新生产任务。

新准备源与报告作为既有trial的ordinary supplement；原annotated/peeled及全部历史记录不重建、不改写。
