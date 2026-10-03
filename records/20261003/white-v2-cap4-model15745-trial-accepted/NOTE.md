固定4rad/s的white_v2加强DR正式45分钟试训及两种子回归已通过。原成熟完整15583开始、PPO预检策略弃用；正式试训原子完整保存model15745，SHA a869c4b2d7db80f63285db00b9d9e8690201fe675628cc8795d83e7976a83470，CPU actor/critic/optimizer/std/iter共68浮点张量完整有限。auto_0014_production绑定PID2472824，auto_0010_ACCEPTED明确cap_unchanged4、budget_addedfalse、real_robot_certifiedfalse，未偷偷加转速或预算。

同正式15745两seed20261002/20261003，各nominal/white_v2 flat80env与spin88env、1500步15秒共8份实际新冻结回放。四组同seed同协议完整初始root/q精确配对；white_v2初末参数实际回读通过，原flat nominal不发参数审计，不能冒充独立名义参数回读。原门槛和严重单样本安全否决均过：四份flat已训练8组每组8/8准入、64/64存活，四份spin88/88存活、全部原技能组通过。已训练flat最坏peaktilt6.926deg、均高差9.953mm；纯±4四报告实测+3.98253至3.98479/-3.98273至-3.99374rad/s，纯4最坏peaktilt1.37771deg。旧strict_pass_window仍false，未改毕业门槛；平地±2m/s只作外推诊断。

white_v2继续共同质量/惯量与六电机输出.925–1.075、轮μ.75–1、33桶、约20%干净样本，输出增益后原硬件曲线裁剪；其余弹簧/PD/COM/噪声/延迟/奖励/PPO不改，10ms感知延迟仍未部署。该结果是工程DR试训验收，不是实物标定、全地形或sim2real认证。6rad/s之前三失败块和原全部失败报告仍保留，rate_rejected含6，不凭4档DR通过宣布6或120rpm完成。

实际单一续训PID2484610/start17028324从原15745完整恢复，在新run logs/2026-10-03_16-14-33_auto_0016_autonomous_continued_cap4_white_v2。PID绑定model15775 SHA5d5a7c0bcc1b4f7ac9fa19293e5b1510dc7ecb8e7b9997061b33677f7dee779e已CPU回读68浮点张量有限，std存在，manifest start15745/cap4/white_v2/KEEP_STD1。约30.9k环境策略步/s、GPU91%/14222MiB/50C为检查快照，无所查运行/GPU异常、103源SHA一致。唯一180000秒账本及两原扩展保持，16:24快照余26065秒约7h14，后续须扣active尾段。只记录权重SHA，不提交权重或凭据。

本次仅读取已有训练/验收证据、CPU完整回读与Git记录，未发新探针、重启PPO或更改课程/物理/门槛/预算。下一原定2h保存边界继续既有监督器评测，不重复仿真。
