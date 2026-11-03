# 修复版 E0 来源一小时训练的实际结果

原20,000环境窗完整保存并安全退出；60次PPO、28,800,000实际样本、1,200次Adamstep，final41,476,381B SHA d86732f97d0020c15036281bac2e23d300eb777db6643bb09b8cdc1740a7ae9a / FULL_V3。owner1551922及其worker/eval均ownwaited、settled、released；本地52704完成传回并退出。

独立80首局/seed9137/实际400Hz：0strict、0wholeclear、0leading、0台顶力。54局按原20连续终止、26局timeout，48–399controls、平均207.075=4.1415s；raw异常/closure/mimic/数值重置均0。原动作clip6及debugfalse/clock0生效。第一轴100%超过裁剪范围；前20controls的左右hip目标均值约1.050/.671rad，超过实际+.5rad上界，不能声称动作接口问题已全部解决。

当前模型已view_image早/晚侧顶共4图：所选0/1/40/41在中央低地下降，未到台顶；0/1/41的终态1.42/2.50/1.96s后图片clamp，不是持续存活；40到7.98s仍低地内。接触类型不靠二维投影全推断。

纠正此前归因：原E0的2026-11-02 retention已有STD第一轴23.351587和maxraw140.443；该原场地80局仅timeout。不能因STD23.35/大raw就断定SCUT训练造成网络退化。原文字报告保留，此处追加纠正；原场地评测也不证明当前270mm任务可达。

下一步为同一SCUT场地的原E0来源有限推理，保存每个相同物理端点的原MOD4观测和适配后观测及两种输入动作，不更新权重、不新训练窗、不重读已回传final。2026-11-04 02:16有限准入发现原canonical被standingV21 owner1556103/create1793728548.28使用，0SDK/0PT/0GPUscan；先等其原ownrelease。唯一本地timer27216已绑定，预计03:15:48.998+08后检查一次实际释放并执行未消费诊断。原训练全部once消费，不重跑。
