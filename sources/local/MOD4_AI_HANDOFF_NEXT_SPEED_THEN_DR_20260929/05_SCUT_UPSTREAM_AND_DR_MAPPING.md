# 华南虎路线与DR实现前审计

冻结参考：`/home/egde/fangzhen_linux/refs/wheeled-legged_RL-main`，记录提交 `b8ff79f3df855faf9dc92f4a282bd80c42649466`。先查当前文件是否被改，不能拿GitHub最新代码与旧实验混说。

路径：`source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env_cfg.py`。

- EventCfg：base mass0.9–1.2倍，腿/轮0.9–1.1；COM x±2cm/y±4cm/z±2cm；轮静摩擦0.5–1.0、动摩擦0.4–0.8、恢复0–0.2；PD0.8–1.2；复位姿态/速度随机、间隔推扰。
- Flat指令范围[-3,3]m/s；不是其已验证全工况速度保证。
- `Wheelbipe25v3FlatEnvCfg.events=EventCfg()`，所以“上游一定先无DR训练、最后单独DR”说法不成立。

V14：`wheelbipe_V14/env_cfg.py`。

- Flat绑定EventCfgV14。附近写有Temporarily disable domain randomization的注释，但实际配置仍有随机化；部分惯量项确实被None关闭，应逐项追踪而非全开/全关推断。
- base质量0.9–1.3，COM x±4cm/y±2cm/z±2cm，关节摩擦、PD0.75–1.25、腿输出0.8–1.1、轮输出0.9–1.1等。
- Rough v1标为跑场；Rough v0标为小陀螺，继承相应Flat变体。预训练README描述的是多个分支链，不是统一固定轮数的线性毕业课程。
- `pretrained/26_infantry/readme.md`也明确其rough_dash分支飞坡仍有未解决问题；不要保证复刻即全科目成功。

MOD4 DR代码入口：`isaac/mod4/mod4_task.py`。

- `DR_OFF`同时影响事件、噪声、观测延迟和动作延迟；恢复DR不能只看EventCfg。
- 当前默认随机化还包括armature0.7–1.6、气弹簧刚度0.8–1.2/阻尼0.7–1.3、质量惯量、重心、摩擦、推扰等。**不能只把RM_DR_OFF改0就声称轻度DR已实现。**
- 建议显式白名单profile，在禁用其他随机项的前提下开启首批质量/轮摩擦/输出强度，运行后读回生效值。
- mod4_env.py负责step事件；新配置仍要验证其实际触发和reset状态清理，避免延迟缓冲跨episode串样。
- 20k环境曾受PhysX材质数量限制；不要恢复每碰撞体独立创建大量物理材质的旧方案。

上面上游数值用于理解结构；初期MOD4的轻度范围见02，属于工程建议，须以本车硬件和对照实验验证，不是直接照抄。
