# 当前MOD4验收与华南虎公开V14的剩余差异

结论：当前v3只取消了有限滑移数值及原地世界XY平均速度模长的独立硬否决。完整课程验收仍有多项MOD4额外门槛，不能说整套门槛已与华南虎一致。

实际主机源核实为 scut_style_nonslip_xymean_diagnostic_v3 / scut_speed_v3_rate7_budget_dynamic，共139候选源。仅读取源码/状态和已有20775报告，没有新probe、PPO、暂停、重启、配置或预算变化。固定公开SCUT提交 b8ff79f3df855faf9dc92f4a282bd80c42649466；本机HEAD精确一致、工作区干净。仅对应公开V14 Flat及其继承路径，不代表未公开实车验收或所有其他变体。

| 项目 | 当前MOD4 | 华南虎公开V14 / 差异性质 |
| --- | --- | --- |
| 有限滑移数值/原地平均世界XY速度模长 | 已取消.15/.12数值硬否决，全部保留诊断 | 公开V14没有这些回放晋级门槛 |
| 前向速度误差 | mean(abs(body vx-command vx)) <= max(.12,.25\|vx_cmd\|)，自转vx_cmd=0仍<=.12 | 前向水平投影body vx*cos(pitch)的指数/平方奖励及站立平移连续惩罚，没有对应晋级数值否决 |
| 转速误差 | mean absolute signed yaw error <= max(.2,.2\|yaw_cmd\|) | 指数/平方跟踪奖励；V14奖励约束.8是指数误差裁剪，非验收阈值 |
| 姿态验收 | 平均总倾角<=8deg，控制采样峰<=12deg；额外任一个体峰>15deg否决；短物理峰<=15deg | 训练roll或pitch>40deg进入终止，V14普通终止条件需连续20个控制步；另有连续姿态奖励 |
| 高度跟踪 | 平均abs(真实离地高度-.25)<=.03m | 高度跟踪连续奖励；height_err_constraint=.15裁剪奖励输入，并非3cm毕业线 |
| 动作平顺 | 动作平均一阶差delta<=.18、二阶差d2<=.25 | action_rate/action_smoothness连续惩罚，无同数值晋级线 |
| 轮载/双轮低载/轮地gap | 每轮平均法向载荷>=10N、最长双轮低载<=15.01ms、最大输入网格gap<=2mm；额外任一个体低载>20.01ms否决 | 历史接触峰值>1N判断轮接触；没有本项目10N均载/15ms/2mm晋级组合 |
| 停车 | spin启停组stop mean \|yaw\|<=.2rad/s；flat刹车\|vx\|<=.12m/s | 零指令跟踪/静止连续奖励，无同样回放停车数值毕业线 |
| 底盘/导轮接触 | 冻结验收guide/base平均力<=1N；训练底盘对地力>50N终止 | base/guide即时contact norm>1N加入终止，V14普通终止连续20步；有害接触奖励另用5N历史峰值 |
| 硬件裁剪使用率 | 冻结spin wheel/leg rating clip fraction<=.2，同时始终执行原硬件包络裁剪 | 不同资产/执行器包络和力矩/功率连续惩罚，没有本项目20%裁剪占比晋级线 |
| 闭链/mimic | 冻结closure<=2mm、mimic<=.01rad；训练closure2mm/mimic.05rad终止 | 不同机构；未发现等价离线残差数值毕业合同 |
| 接触读回完整性 | .5ms回调/有效承重样本齐全、均载与原积分差<=.1N、normalz差<=.01、COM/link点速差<=.001 | 不使用本项目报告点校准晋级合同 |
| 存活/组比例/严重个体 | 各15秒8样本组>=80%，physical_smoke组>=95%；任何严重个体独立否决 | 训练episode reset/timeout，无该固定冻结组80%及独立毕业合同 |
| 两策略/多seed/DR晋级 | 两份不同正式策略通过，同候选2seed nominal/white_v2八份严格root/q/参数配对；新cap物理/128PPO/45min前置，3失败回滚hold | Flat curriculum=None；spin_low/mid按iteration3000/4000启用，未见本项目分档成熟/配对/3失败合同 |

最容易遗漏的是 speed_error：取消 spin_translation_speed（世界XY模长）后，纯自转仍检查 mean(abs(body vx))<=.12。两者不是同一测量。20775原始真实报告当前正7最坏前向误差.0376235、负7为.0228477m/s，均通过此项；它不是这份策略的当前阻塞，但后续仍可能否决。仅在内存把正7组的这一字段改成.121，v3确实拒绝，原raw未改、没有新回放。此前36项CPU合同本就明确保留speed_error，这次审查指出它也不是华南虎的独立晋级线。

姿态必须区分“训练终止”和“冻结质量验收”：我们训练bad_orientation总倾角.75rad约42.97deg；验收均8/峰12deg及严重峰15deg是额外质量门槛。华南虎40deg是roll/pitch终止线，V14普通终止连续20控制步，不是合格姿态标准。不能简单把它当作允许40deg倾斜也算小陀螺成熟。

底盘/导轮接触同样不是简单严松比较：我们的验收时间均力1N与SCUT每个link即时力1N+连续终止、5N有害接触奖励、我们的训练50N且过滤地面，传感器、滤波、统计及用途都不同。

判断：速度/高度/动作等连续性能优化被我们另外变成了回放质量门槛，两策略、多seed与逐档物理预检也属于项目额外流程。闭链残差、mimic、真实硬件转矩转速包络、NaN/缺失和接触读回完整性则是MOD4自身机构与测量正确性要求，不是华南虎数值可以直接替代的质量目标。本轮只完成差异审查，不改变正在执行的v3流程。

精确来源：
- [v14](https://github.com/scutrobotlab/wheeled-legged_RL/blob/b8ff79f3df855faf9dc92f4a282bd80c42649466/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py)，SHA 68fe88ae683e6b020cc8fda64950881a8a21ee7920da2202cc0a5601f7919ef5
- [base_cfg](https://github.com/scutrobotlab/wheeled-legged_RL/blob/b8ff79f3df855faf9dc92f4a282bd80c42649466/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env_cfg.py)，SHA 5c844b544810e80d7ad2c262d9730182d6f1bb57b2ff2bbf8cb0dfef73c97acc
- [base_env](https://github.com/scutrobotlab/wheeled-legged_RL/blob/b8ff79f3df855faf9dc92f4a282bd80c42649466/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py)，SHA fb8a1da72c4ed90dce870e59bc3370350086f7ae34203cd2e4b3501219684b2e
- [v13_env](https://github.com/scutrobotlab/wheeled-legged_RL/blob/b8ff79f3df855faf9dc92f4a282bd80c42649466/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V13/env.py)，SHA be4980580febd62f738fcb87e531150e4e9ff590e3b4706a5ec94c0623739997
- [v14_env](https://github.com/scutrobotlab/wheeled-legged_RL/blob/b8ff79f3df855faf9dc92f4a282bd80c42649466/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env.py)，SHA 831c2688d9a66b82767ada34182f055fb1f852c0a5eb248d7a188e31ba093929
- [commands](https://github.com/scutrobotlab/wheeled-legged_RL/blob/b8ff79f3df855faf9dc92f4a282bd80c42649466/source/agent_tasks/agent_tasks/manager/mdp/isaaclab/commands.py)，SHA 423c02c651510b4ea9f7cbf0121bdc611ebb944f8d5598639192d90f5b7884e7
- [cfg_utils](https://github.com/scutrobotlab/wheeled-legged_RL/blob/b8ff79f3df855faf9dc92f4a282bd80c42649466/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/cfg_utils.py)，SHA be7bfbd24f2ea5aff49f54fde93ba65ff0fcc90c458726ab91c77f7dbdf1b0a4

目标机逐文件SHA、所有剩余门槛及用途、已有报告反例与内存验证在 REVIEW.json；来源验证在 ACTUAL_SOURCE_VERIFIED.json。
