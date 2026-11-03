# E3 signed-upright 单因子候选｜DISABLED / SOURCE-only

`{"enabled":false,"training_reward_only":true,"kappa_NEW_reward_per_s":null,"PBRS":false}`

**假设仅一项：** 原E3已有signed peak增量+一次stable credit；只新增request内密集upright占据奖励，不另加progress势差。原plant的reward/分项完整保留；不是“TOTAL倒立reward为0”或真实失败根因结论。

```text
g_b = -R[2,:]; u(s)=clip((1-g_b.z)/2,0,1)
m_t = original request latched by begin(): recipe!=12 AND age_before<300
r_shaping_t = enabled * kappa_NEW * .02 s * m_t * u(s1_physical_before_reset)
r_learning_t = r_original_t + r_shaping_t
```

- **坐标/时刻：** bridge真实源码`xyzw→wxyz`且断言`projected_gravity_b=-R[2,:]`，故正立gz=-1/倒立+1（本次未执行原生断言）。action前锁存command_t、recipe/age/request；原termination compute后、reset前采物理s1/term/trunc。age_before298这一步仍mask=1，即使age_after300；下一步0。E3 command_t为BODY零twist；不借reset后姿态/command/xi1。终端当步reward保留、不乘~done；新项只乘一次dt，r_original绝不再缩放。
- **标定：** κ量纲reward/s，当前null。**NEW**保守封套`0<κ<=1/3`，150步/3s新增未折扣额≤1（与原credit同量级是新设计，不是历史authority）；单步≤.02κ，γ=.99折扣上界`.02κ(1-.99^150)/(1-.99)`。以后凭原reward分项分布预登记κ/界限；合成测试常数不是选定值，超封套另立假设。
- **冻结/分账：** normal recipe12六例新项严格0；保留3s原request、.5s stable、predicate/完整74分母、normal6单列、termination/reset/动作/速度/physics/fullDR、所有母本/H1/旧源/失败。不混bound/anchor/H32/新噪声。逐行记录r_original/r_shaping/r_learning及episode/step、command_t、recipe、age_before、request_t、物理gz、term/trunc；aux仍监督original，未来imagined另加同定义shaping、critic明确学习目标与新schema。cleanstate只供privileged WM/critic奖励，不加actor通道；终端xi1无效不伪补。
- **源核对/局限：** metadata→worker/env→E3 entry/config/runtime：heightgate off、alive/termination/basecontact reward=0；RM_DR_OFF禁legacy bundle而非禁white_v3等fullDR。早期mask仅height族/lin_vel_z，orientation/actioncost保留。原orientation=`-(20gx²+16gy²)`，正倒立单分量同0。新u在精确倒立角度一阶梯度仍0；偏离ε时新增约κdtε²/4，原pitch/roll约−20dtε²/−16dtε²；两项孤立首步相抵κ=80/64，远超NEW封套，非可达动作/根因/提权建议。探索与WM梯度另待证，toy不证明技能。

| PBRS条件 | 实际source核对；本候选无不变性保证 |
|---|---|
| γ | SM worker沿vendor .99、λ=.95；原PPO .9801不是SMγ。 |
| term / timeout | bridge done=term\|trunc；aux学sigmoid(done)，可并入可选timeout；当前两者切尾，未见timeout专用bootstrap恢复。 |
| H尾 / value transform | H16=.32s**有**critic bootstrap；现有无强制`V'=V−Φ`。 |
| 完整恒等式 | 标准应同γ/c用`F=γcΦ1−Φ0`、terminal吸收Φ=0、timeout按实际bootstrap、request边界入Φ。本密集项非F，learned reward/done也未强制该恒等式。 |

**唯一下一步：** 保持disabled；只有父任务WM/replay一致性诊断证据及原质量闭环允许，才在独立新分支实现一个短段版本。先验分账/normal6全0，再按原first-episode original-requested完整74及normal6分别验收，完整保留term/incomplete/失败；退化即停，质量优先、不凑3000。用户的合格N80/E3160教师/A1/.05tanh零更新探针均0/74，normal首物理term=0/6、6/6、0/6；bound非训练收益、独立单seed cohort非因果。没有native executor/训练启动。

精确源行/bytes/SHA与详细核对见[manifest](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_e3_signed_upright_reward_review_v1/SOURCE_REFS_MANIFEST_V1.json>)；[stdlib tests](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_e3_signed_upright_reward_review_v1/test_signed_upright_stdlib_v1.py>)与[结果](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_e3_signed_upright_reward_review_v1/TEST_RESULTS_V1.json>)仅合成公式/时序/边界验证。
