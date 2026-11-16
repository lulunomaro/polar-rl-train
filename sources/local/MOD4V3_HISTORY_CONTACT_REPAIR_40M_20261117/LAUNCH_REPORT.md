# 40分钟实际开训记录

实际PPO开始：2026-11-17T03:34:23.677869+08:00。严格截止：2026-11-17T04:14:23.677869+08:00，2400秒封顶，预留30秒保存关闭，不自动延长/重启/晋升。旧58m轮已停止，不恢复。

首完整iteration25488，实际12次Adam小批次，actor_changed=True，完整PT SHA de637200d2def4c19150062d4a46f11e0e8b54d9ed51d78198187282afe2fa9f。对完整PT实读：normal权重与六动作STD最大变化0，技能头最大参数变化0.0011320412158966064；四组实际lr=1e-4/3e-4/3e-5/1e-4，检查通过。native训练PID3096853，Windows监控PID20304；监控与deadline守护均已启动。

开训前独立学生：normal60/60，200mm真实越边5/5、出现>=.4s物理稳态5/5，正式整程<=.6仍0/5，落台后可能超速或失稳。上述为CPU热身候选成绩，不是新PPO检查点成绩；不能宣称全面修好。教师纠偏不计学生通过，所有失败保留。

代码/数据/步骤/方案见REPAIR_PLAN.md，预检PRECHECK_REPORT.md。视频preflight/SELECTED_STUDENT_CENTER_1X.mp4与实测曲线preflight/SELECTED_FIVE_STARTS.png。5/10/20分钟独立抽检与最终全套回归在evidence/checkpoint_evals。默认c874/CURRENT、原010m/8391及原物理/PD/电机/scene/fullDR/2mm仅诊断不变。
