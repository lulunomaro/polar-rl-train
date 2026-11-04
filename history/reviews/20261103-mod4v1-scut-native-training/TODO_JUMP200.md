# MOD4v1 单个200mm直角台阶跳跃待办

2026-11-04人类最新：“我说的是跳台阶，机器人跳上去200mm的台阶不是这个碎台阶”“你设置todolist去做”。本清单覆盖此前inverse-mid小阶梯和“允许轮子保持接触”的任务选择。历史270mm、斜坡、小阶梯原始试验与false保留，不当作200mm跳跃完成。

- [x] 固定目标：从低地自主起跳，越过单个200mm竖直台沿，双主轮落在真实水平台顶并稳定恢复；爬坡、小阶梯、顶着台沿爬不计跳跃。
- [x] 核对固定华南虎源码的高台阶场地、起跳与落地控制；区分保存模型配方与源码可选分支。
- [x] 完成小阶梯attempt08最终运动评审；完整结果与原false随本阶段Git补充提交。
- [x] 新增独立jump200任务：200mm单台阶、接近/起跳/落台后的命令与奖励、400Hz真实离地/越沿/台顶支持评测，旧冻结包不改。
- [x] 完成针对200mm真实几何、起跳与爬台反例、落台稳定的必要CPU检查（8项通过，原false保留）。
- [x] 在原资源/预算/保存边界内做有限实际模型评测；立即原生审图与回放，按结果决定定向修复或训练（80局基线已回传并审完4图，0起跳越沿/0触台/0成功）。
- [ ] 查四张4090的实际可用容量和原canonical/authority/private/finite准入，安排明确授权的20,000环境一小时任务；不延长已结束窗口。
- [ ] FIRST核真实PPO/梯度/完整保存/日志，绑定唯一postround；训练完整退出后立即独立评测与实际回放。
- [x] 截至200mm基线与授权自动接续的全部试错、失败、源码、回放与决定纳入本阶段Git补充；CURRENT_STATE/WORK_ORDER/现有mod4-10已更新。
- [ ] 新训练FIRST及最终80结果产生后继续追加Git，并按真实动作决定下一步。

当前证据：固定SCUT commit `1a26356d6f591734d4f6f666f5cead1a6925da67` 的terrains.py有STAIR_FOR_RM 200–220mm/1.5m踏面，以及HIGH_STAIR_FOR_RM 150–350mm/1.25m踏面。当前误选inverse-mid为25–40mm/0.1m踏面。公开rough_rotation_stair保存YAML关闭Airborne/JumpTakeoff/Stair，不能把小阶梯保存配方称作200mm起跳配方；须进一步核对应源码分支。

当前attempt08已完整关闭：49新PPO、23.52M样本、980新Adam、final iteration80/FULL_V4，SHA `f6b6b649b78752a89c0688850ae89e93afd0a87fe21eb6b6705f9b02ecf81da4`。独立80小阶梯43双轮升阶/56单轮升阶/0连续.5s稳定，5导轮持续接触终止；全部4张新实际图已当前模型查看。此为小阶梯试验，不是200mm技能。

19:39实际覆盖：独立`jump200_step_eval1_20261104`已完整关闭回传/审图，remote owner1613410/create1793792185.63已ownwait/released。真实200mm单台阶mesh只有0和.2m高度，80局全部触发起跳请求但0实际向上起跳/0越沿/0触台。78接触终止、2原8秒timeout，平均2.65875s，无closure/mimic/数值异常。来源小阶梯策略未学会跳跃，不能继续用小阶梯结果冒称成功。人类已明确“批准200mm跳台阶训练一小时”，本轮20,000环境/3600save+300exit使用同一原canonical余额；原attempt08窗口不延长。已有有限评测once全部消费，禁止重跑。

19:59接续：修正版已获批准，PLAN及7module+3control准备完成，尚无INDEX/LAUNCH_ONCE/生产GO。首轮准入在网络前遇standingV30实际controller而拒绝，原false保留。V30真实GO19:51:35、SAVE20:51:35、NOMINAL20:56:35；唯一localtimer将在20:57:35后freshLOCAL核exactowner1614229/create1793793094.65已ownwait/settled/released、canonicalNone/原锁，并刷新四张4090后自动launch。等待不计入新小时，不再询问相同授权。

20:01实际：唯一localtimer67488/create2026-11-04T20:01:12.771869+08已绑定且stderr为空，RESOURCE_TIMER_BIND_ONCE/RESOURCE_TIMER_ONCE均消费。首次bind被另一聊天E3正式回传21548在网络前拒绝，原false保留；仅把本地等待的bind改为允许记录外部controller，所有网络前freshLOCAL原gate不变。不得再bind/timer/探卡或重复launch；等待程序自己负责原锁释放后的有限准入与FIRST→唯一postround。

20:38最新覆盖：人类指出端口转发单4090可以用Windows盘，实际独立210只读核GPU空闲23890MiB、Windows NTFS挂载`/mnt/mod4_expanded_original_EF3105C85DD986BD_20261026`可写剩694,983,204,864B（约695GB），第二别名是同一块盘，不重复加容量。HOME0不能再称无可用数据盘；当前MemAvailable43,310,092,288B仍低于既有20k的64GiB准入。旧67488在网络/生产前按exactCIM停止，其once全保留。新唯一35308/create20:36:24.331634运行`jump200_forwarded_windows.py resume`，先等另一聊天72只读observer52216结束，再fresh四卡/Windows盘/原exactV30释放及原canonical锁；取消额外固定20:57等待，原生产launch仍未消费，新授权小时仍未开始。首Windowsfourread被52216网络前拒绝false保留；210单独host只读已完成并SSHclosed/SESSIONrestoredFREE，没有碰72现有连接。
