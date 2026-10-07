# 2.5ms、TGS32/4：人类授权4090主训练验证

人类2026-10-07明确“按照2.5ms 求解器最优解直接加入主训练开始测试，用4090.磨刀不误砍柴工”。这是继3060五份隔离筛选后的新增实际训练授权，优先于此前仅冻结筛选的范围限制。原MOD4-MOE-PLAN-001 v1.5 SHA812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b不改；此补充不声称32/4是所有参数中的全局最优或永久通过。

已筛选32/4的128env15s实时探索P95 .544022mm、max .776970mm，无超2mm或taskfailure；16/4在该小样本也未失败，旧稀有20kPPO问题未复现。现在由4090验证真实新范围与长训。

实际源选择完整已回放24827 SHA5abd2a912f5c717849c25de09448581c226e6c9e79581f4a44e0e4a8f27261c1：此前完整2h健康、三类3060同条件旧技能检查通过。25300原3次任务终止完整保存保留，不借未回放候选、目录最高iter或预检策略作源。原208来源重基隔离新211根，只有env.json的RM_PHYSICS_DT_S 0.001→0.0025、RM_SOLVER_POS 16→32两项改变，增加实际读回探针/新控制器/CPU边界测试三文件；其他207源逐字一致。

固定100Hz控制、2.5ms×4、TGS32/4、5ms冲量bin/三history、20k×24、LR1e-4/adaptive、save25、KEEP_STD1。继续S2 D1+D2同任务、white_v3、actor噪声及四腿episodebias、35/38/6网络、原奖励、完整MOD4USD/闭链/mimic、硬件gain后转矩转速包络；PD/COM/弹簧/armature、感知与动作延迟不混改。2mm closure/.01rad mimic和原task/nonfinite/参数数据检查保持，不启用冻结shadow，也不修改旧全局task-stop合同。

新唯一入口supervise_dt2500_solver32_training_test.py：在旧父/guardian/trainer实际退出、完整源CPU有限、active/Sactive空并取得原两锁后，顺序20k短物理（warmup24/timed120控制步，真实每env TGS32/4和六闭链读回）、128×2与20k×4完整PPO预检。新范围预检权重弃用，不再重复旧范围预检；128测试使用fresh sensor流并披露，20k与正式训练完整恢复sensor/global/named RNG后新物理episode，不称PhysX exactresume。

通过后主机自动从同24827完整actor/critic/optimizer/std/iter接首45min正式PPO。首45min是有限训练验证，非已经采用长期基线、通过旧能力或所有科目完成。每25iter完整保存，15s主机guardian保护预算/失去父监督；实际task/numerical失败请求自己的STOP_AFTER_SAVE，保留完整保存和原始现场，唯一结清自己的账段，不直接kill、清active或盲复活旧entry。健康保存结束进入SOLVER32_REVIEW_READY；下一审查比较实际闭链余量、完整PPO吞吐、直线/左右4π/world整圈方向和跨平台scope，不能因reward或短窗口就宣称提速翻倍/修复成熟。

唯一canonical仍828000秒230h、六扩展各一次；本授权新增预算0，所有加载/PPO预检/正式学习/保存退出计同账。冻结物理/评测不计PPO但占真实GPU时间。3060原1ms scope不冒充新2.5ms32/4 scope；并行平台等待不阻塞4090自己已验证范围训练。

新根/home/egde/rl_candidates/MOD4_DT2500_SOLVER32_TRAINING_TEST_20261007，原P/status/log/canonical owner保持。所有stage/launch once仅一次，新真实部署/阶段结果唯一Git annotated trial，权重/大raw只SHA。原1ms工作基线、2ms SUSPENDED和旧2.5ms失败/全部权重保留。
