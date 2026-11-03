# 修复版原生复测与E0来源恢复

四卡实测后选用72第二张4090。原peer已在2026-11-04 00:14:38+08完整退出并结清、释放；唯一controller1904消费首次诊断launch，owner1551324/create1793722486.95。GPU准入free24203MiB/used13/util0，实际原authority/private/finite锁取得；未新增GO、优化器或账本写入。

修复版same-final `305f5a9e…` 已完整完成80firstepisodes、3192physics回调（400Hz）、seed9137，上限400controls。实际42–399controls，平均182.55（3.651s）；58个termination全部连续计数20，22个timeout。raw-observation、closure、mimic、numerical重置均0。原debug诊断false、时钟0，应用动作绝对值最大6，表明F1/F2执行修复实际生效。接口V2→V3显式repair，未改源模型。

0strict、0wholeclear、0leading、0台顶接触，所有首局mask内台顶力0。第一动作维原输出100%越过±6；实际raw范围约−134.42到96.25。此前final CPU已读到该轴STD23.35、合成mean约−79.8，不能假设接口修复能恢复已退化的网络。两次评测同final/seed但执行链及DR消耗不同，不把寿命变化解释为单项奖励的隔离因果。

早/晚侧/顶4图以保存actual31body poses和增强contract碰撞几何渲染，0新NN/physics，由当前模型原生view_image全审：四例早期降到低位，在中央低地附近移动；env0/41约1.56/1.54s终止，后图重复是ENDclamp；env1/40存活至7.98s仍在台前低处，无台顶支持。二维投影不用于推断全部非轮接触类型。

诊断owner已ownwait、安全退出并释放锁，SSHclosed/SESSIONrestored/FREE。实际400Hz轨迹15,734,759B SHA256 `256aa4728ac85055cedade09e304c7a6309b5751e13c642401e53f81028decd1`；pose1,099,361B SHA256 `23299e2da0878bf7ca2dc40b6f9542baeaa41834afd01300d3c4c9b2cb08daac`，原件保留并索引。

决定：从原成熟增强MOD4v1 E0 `6cdac1e4b84df407d41a38444b87eaa91309ed898af05fe95a6c80f6ac3fd693` 做SCUT风格weights-only初始化，freshAdam/iteration，开启已修复的执行与终止链。沿用人类20000环境、一小时窗（3600保存+300退出）、原唯一canonical及strictreserve86412.86069250107；新目录仅7变更module+ownerwrapper/entry/plan、9共享SHA引用，不复制原模型/资产/源码树。现有56CPU结果与同源原生评测复用，不为归档重读PT。

新run `MOD4V1_SCUT_REPAIRED_E0_20000ENV_1H_1793723033230108600`，root见WORK_ORDER；owner1551922/create1793723082.85。原生actual scene已确认20000；FIRST/完整首存以实际回执为准。PPO配方、奖励、物理、出生与验收不因来源恢复改变；这是新任务初始化而非Adam完整续训。完整保存/退出后由原owner立即独立80评测，再回放审图与决定下一轮。
