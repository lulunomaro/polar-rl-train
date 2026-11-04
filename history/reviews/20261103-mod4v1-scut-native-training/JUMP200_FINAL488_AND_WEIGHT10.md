# 单200mm跳跃：final488与projection权重修复

2026-11-05 07:34。原生训练、独立80、全部4幅savedpose和完整模型/日志核验已完成，跳跃目标未达成。下一候选仅加大现有请求投影代价，单个本地接续程序67764已绑定，新GO尚未发生。

- 原窗GO05:36:14.384236、SAVE06:36:14.384236/NOMINAL06:41:14.384236。final06:35:11.266724、TRAIN_CLOSED06:35:39.166001；独立80完成06:38:08.012310、owner06:38:08.741872完整等待/结算/释放；正式回传06:39:32.068074。旧69168已结束，所有生产/评测/回收once消费不重放。
- 112新PPO、53,760,000样本、21,504physicscallbacks、2,240新Adam，source376→488。FULL_V4 40,877,907B SHA `70280b66556f5aa354d29d6a918b43f6e928e0064b418ff437dea02e809e35fb`。
- 必要模型诊断1次：17项Adam全部9760，LR.0002562890625000001，actor35/critic78/STD、7组件/RNG/队列/globalcounter11712齐全，模型及Adam有限，新constructor nominal保持。3原SCUT permission未设NaN哨兵保留，不当损坏，不为Git再decode。
- 80局均399controls/7.98s timeout，0contacttermination/closure/mimic/numerical/rawoutlier。79局共362请求（1局0/5局3/29局4/39局5/6局6），0groundupwardflight/flight_id/wholeclear/actualtop/landing/success。
- push/tuck24.03%端点，push均vz .4742m/s、最大1.1051，但无双轮实际离地。rootmaxx.54246<edge.8，env32倒退至-2.2573m。四个实际选例到x.50-.534m反复推蹬；early是spawn下坠，late side/top没有越沿或落台。所有4图均当前模型原生视觉审看，wxyz不再换序、0新physics/NN回放。
- 原左crank rawmean-2.584降到-.0577，两hip rawmean由1.9613/1.7545降到1.7548/1.2644，但hip目标上限仍99.9937%/99.5551%。原目标/限位/CAD合规；projection确实执行，不把D4延时/跟踪误差称映射bug。
- projection代价总体每control-.00834；按真实phase重算push代价-.02664、push总reward+.05279。现有-2无法移除高正回报的贴地推蹬。只将该项权重改-10，其余几何/观察/动作/命令/奖励/增强物理/限位/PD/DC/CAD/D4/PPO完整保持。

旧轨迹反事实：按原.5rad/defaultoffset0和原CAD→限位/CAD重算，与生产每control投影term最大误差1.8626e-9；weight-10的同动作push平均总reward为-.053765、idle-.022822、tuck-.031186。仅旧动作的奖励核算，0新动作/0rollout/0PT/0physics，不是更好运动证据。新权重19项CPU通过；只改jump200配置，旧8项stairs回归证据复用，不额外重复。

完整日志：WORKER518236B SHA `754b1d7396e6979872fc4963f3219c4bdf97ba0b8374d8842b7be616cb935c3c`；EVAL15600B SHA `0b9ca6e255b112449f19b41924968a864971e4fff4bc1b14f59a015d38d45adb`，实际errors0。第一次reader在网络前遇另聊天22140 dispatch.py gpu拒绝，false/LOCAL_CIM原件保留、0SSH；随后sole67764补回全文并生成pending解除supplement，不覆盖原pendingreview。

逐body接触峰值：chassis1155.53N、guide04 1776.19N、guide06 1747.79N，其余列出的guide为0。峰值不等于满足持续接触终止；80局均timeout，台顶实际force0。命令vx恒.6、height/effectiveheight.25，完整原始curve保留，不能用生存称跳跃。

候选`env20000_jump200_projection_weight10_1h_20261105`只1个config module+owner/entry/plan，63sharedSHArefs，无资产/检查点/整树复制。恢复sourcefinal488/17Adam9760/LR/STD/组件/RNG/队列/counter，新constructor nominal后一次freshphysicalreset；不freshAdam/输出轴reset/PhysX恢复。

唯一local67764/parent56492/create07:31:23.503643，`jump200_training_control.py continue_segment --root A`，stdout/stderr0，CONTINUATION_BIND_ONCE/ONCE/SOURCE消费。先补齐全文并核ownerexit，现finite等另一聊天SCUT33 exactowner1640872/create1793834938.96，worker1640882/create1793834939.99，actualGO07:28:59.693263/SAVE08:28:59.693263/NOMINAL08:33:59.693263，来源本地STATUS_SCUT33_FIRST.json，context冻结pathbytesSHA。其是另一任务，不混同本聊天，不kill/忽略或第二SSH。

待exactownerdead/OWNER_EXIT all_own_waited/settled/released、canonicalNone/原三锁free、fresh四卡与原reserve上3900s，才唯一新launch。FIRST须489/480k样本/20新Adam/restore48817entries9760/非零actorcriticgrad/FULL_V4/完整firstlog0errors，再bind唯一postround。当前无INDEX/LAUNCH/GO；FIRST不是技能。每小时从actualGO计含初始化，保存退出后立即独立80/allactualimages再按实测接续，不延长旧窗。原100h累计授权继续，不逐小时再问；原canonical实际余额与strictreserve86412.86069250107不改，不grant/refund/复制/清active/另GPU绕锁。

fullreturned/transfer/NPZ/model媒体均原路径保留并入Git SHA索引，所有false、修复和普通报告进入既有阶段supplement，旧trial/tagpeel不改。实际Gitpush以工具为准。
