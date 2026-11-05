# MOD4v2 final60与独立评测修复

2026-11-05首小时20,000环境从零训练完成60次PPO更新，28.8M样本、1200新Adam步、11520物理回调。18:54:05 final60保存，18:54:35训练关闭；18:56:56 owner ownwait/settled/released，18:56:58本地正式回传。最终PT 40,556,571B，SHA bcda336fb8b949cc0a6543b1640c9234b7f0ce8335dc0d0775c622a2ad367cbf。

自动独立80评测运行后导出网格时报Accessed schema on invalid prim。旧sdk导出的MESH仍为scut_step270，实际配置和ray场地为scut_jump200；RESULT/ALL80缺失，不能将owner或进程returncode0当评测通过。原错误与已消费once完整保留，旧生产包不热改。

v2 configure在共享configure后同步所选MESH；实际函数CPU检查通过且0PT/0SDK/0physics。独立新eval_mesh01只覆盖sdk.py，沿用同一final60、80/seed9137/400Hz/400controls/0optimizer，不重训练。首次准入原canonical被另一聊天V36 PRODUCTION02 owner1668673占用，原三锁忙，未创建remote目录、未消费LAUNCH、0新仿真，SSH已关闭且SESSION恢复FREE。

唯一恢复控制器8572（创建19:12:43.690903+08）仅本地等待到已观察peer原3900秒边界后15秒，即20:13:22.874125+08；再freshLOCAL和原canonical/锁/GPU准入。不得另开读者、抢锁或重放旧launch；实际状态和完整身份见WORK_ORDER.json。补评测实际成功返回后必须看全部80与新实际姿态图，再根据证据决定接续。阶段已record，不重record/retag，所有本轮结果按ordinary supplement保存。
