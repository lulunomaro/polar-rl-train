"""Build a bounded handover bundle; remote training files are read only."""
from pathlib import Path
import os,json,hashlib,datetime,zipfile
import paramiko

LOCAL=Path(__file__).resolve().parents[1]/'MOD4_AI_HANDOFF_NEXT_SPEED_THEN_DR_20260929'
REMOTE='/home/egde/rl_candidates/MOD4_scut_continue10h_20260929'
REMOTE_BUNDLE=REMOTE+'/MOD4_AI_HANDOFF_NEXT_SPEED_THEN_DR_20260929'
LOCAL.mkdir(exist_ok=True)
ssh=paramiko.SSHClient();ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.24.4.210',username='egde',password=os.environ['RM_SSH_PASSWORD'],timeout=12)
sftp=ssh.open_sftp()

files=['status.json','budget_resume_20260929.json','speed_handover.json','speed_baseline_checkpoint.json',
 'SPEED_CURRICULUM.md','RESTART_AUDIT.md',
 'isaac/mod4/env.json','isaac/mod4/env_before_speed.json','isaac/mod4/supervise_speed.py',
 'isaac/mod4/validate_speed.py','isaac/mod4/validate_rescue.py','isaac/mod4/rescue_training.py',
 'isaac/mod4/train_mod4_ppo.py','isaac/mod4/supervise_rescue.py','isaac/mod4/tui_rescue.py',
 'reports/resumed_model_4725.json','reports/resumed_model_4950.json',
 'reports/speed_preflight_2m.json','reports/speed_step15_smoke.json',
 'reports/speed_config_diff.json','reports/speed_frozen_sha256.json','reports/speed_deployment_verified.json',
 'reports/speed_gate_tests.json']
for relative in files:
    target=LOCAL/'snapshot'/relative;target.parent.mkdir(parents=True,exist_ok=True)
    sftp.get(REMOTE+'/'+relative,str(target))
state=json.loads((LOCAL/'snapshot/status.json').read_text(encoding='utf8'))
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='seconds')
deadline=datetime.datetime.fromtimestamp(state['deadline_epoch'],datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def write(name,content): (LOCAL/name).write_text(content.strip()+'\n',encoding='utf8',newline='\n')

write('00_START_HERE_先读再接管.md',f'''
# MOD4 下一任务交接：先稳定提速，再轻度 DR，再地形

快照时间：{now}。**快照不是实时状态；第一步必须运行只读检查。**

你接手的是正在训练的真实机器人策略任务。先阅读 01 和 02，不能把这个文件夹当作可直接重跑的安装包。

- 当前任务根目录：`{REMOTE}`
- 目标机：`egde@10.24.4.210`，RTX 4090。认证使用已有 SSH 配置或向用户取得；本包不存密码、token、私钥。
- 当前任务：华南虎平地训练结构适配 MOD4，速度从 ±1.2 扩到 ±1.5，再有条件扩到 ±2 m/s。
- 当前训练是否运行：快照 `stage={state.get('stage')}`，已保存 iteration={state.get('iteration')}，速度上限={state.get('speed_limit_m_s')} m/s。运行中迭代通常高于最新保存迭代。
- 硬截止：**{deadline}（北京时间）**。不因接管、验证或改计划追加预算。用户没有授权新的 10 小时。
- 现在应做：观察监督器自动安排的首次提速回放，判断结果，而不是再次启动训练/探针。
- 接下来尚未实现：轻度 DR 的显式配置、隔离验证与训练交接；复杂地形适配。

## 阅读顺序

1. `01_LIVE_STATE_AND_PATHS.md`：实时路径、进程、已有结果。
2. `02_NEXT_TASKS_AND_DECISION_TREE.md`：逐项任务、通过条件与失败分支。
3. `03_READ_ONLY_COMMANDS.md` / `read_live_status.sh`：只读检查，避免双开。
4. `04_METRICS_AND_KNOWN_TRAPS.md`：判据、测量局限、已纠正的误判。
5. `05_SCUT_UPSTREAM_AND_DR_MAPPING.md`：上游真实配置与待实现 DR。
6. `06_SAFE_SWITCH_RECOVERY_AND_BUDGET.md`：安全保存/恢复协议。

`snapshot/` 仅是审计参考，不要覆盖目标机正在工作的源码。`next_task.json` 可机器读取；`PROMPT_FOR_NEXT_AI.txt` 可直接作为下一 AI 的任务提示。
''')
write('01_LIVE_STATE_AND_PATHS.md',f'''
# 实时状态与入口

## 当前运行（快照 {now}）

- task root：`{REMOTE}`
- `status.json`：stage、iteration、training_pid、attempt、latest_checkpoint、speed_limit_m_s、evaluation_path、deadline_epoch。
- 监督器：`isaac/mod4/supervise_speed.py`，日志 `supervisor_speed.log`。
- 当前训练：`train_{state.get('attempt')}.log`，PID {state.get('training_pid')}（仅快照；不可凭旧 PID 发信号）。
- 当前完整权重：`{state.get('latest_checkpoint')}`。
- 当前日志目录：`{state.get('log_dir')}`。
- Python：`/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python`。
- 已废止的旧监督器 `resume_after_reboot.py` 不可重启；`launch_speed.py` 是已执行的一次性交接工具，不可再跑。
- 当前 UI：`isaac/mod4/tui_rescue.py`，`start_tui.sh` 可打开终端；UI 只读、5 秒刷新，不负责训练。

## 已做完

- 原 model4725 和 model4950 在 64env×1500step、seed20260926 的 0/.3/.6/1m/s 四档窗口回放均 100% 通过。
- model5050 提速预检：+2m/s 从静止突变，8/8 约 0.52 秒终止；±2m/s 缓升/刹停/反向 15 秒全部存活，但接触窗口仍未通过。
- ±1.5m/s 加减速 15 秒以及另外 48env×5 秒突变指令检查安全通过。后者不是 15 秒性能通过。
- 原训练在 model5150 保存后退出；SHA256 `7db69742da42839a1cedf1cd0b9319d6ab7191d303c98514cf1bfee852d44d00`，见 speed_baseline_checkpoint.json。
- 1.5 阶段从 model5150 的 actor/critic/optimizer/std 继续，已核验首轮 PPO 输出与 manifest，只有 `RM_CMD_VX_MIN/MAX` 从 ±1.2 改为 ±1.5。
- 保持 20000env×24、solver16/4、根高度0.25m、DR关闭、10%站立。奖励/物理/闭链复位代码哈希未变。

## 自动处理与尚未处理

监督器至少在5150+100=5250轮后安排首次新评测，然后每小时评测。1.5范围性能/停车通过且2m/s外推安全通过才自动保存并切2m/s。具体看源码，而不是看到文件名就推断已晋级。

本监督器**不会自动开启 DR，不会自动切 Rough**。这两个阶段需要下一 AI 实现和验证。时间不足则如实交付，不能越过截止时间。

主要输出：`reports/speed_1.5m_model*.json`、`reports/speed_2m_model*.json`、`reports/final_speed_nominal.json`。文件缺失但对应评测进程活着表示尚在运行，勿重复启动。
''')
write('02_NEXT_TASKS_AND_DECISION_TREE.md','''
# 接下来执行什么

## P0：接管先读，不动活进程

- [ ] 运行 read_live_status.sh，确认唯一训练进程、监督器、截止时间、当前速度档、新完整权重和正在评测的进程。
- [ ] 比对 reports/speed_frozen_sha256.json 与当前源码，阅读接管期间新增记录；另一 AI 的判断要看实测证据。
- [ ] 如存在其他 AI 正在运行的任务，不双开、不改其文件。当前授权作用于本交接根目录。

## P1：完成 1.5 → 2 m/s（已部署自动课程）

- [ ] 等待监督器的首次 model>=5250 回放；检查 checkpoint、seed、步数、profile，不把旧 model4950 的通过率算作新速度已通过。
- [ ] 各档分别看站立、低速、正向、反向、加速、停车。窗口通过率、瞬时接触、速度误差、高度、倾角、动作、力矩裁剪和闭链都要列。
- [ ] 1.5 性能通过且2m/s安全通过：让已有监督器在保存边界升级，无需手工再启动。
- [ ] 仅窗口接触差但速度姿态正常：先检查亚步力、轮子相对地面的几何与采样混叠，不能直接叫“跳轮”，也不能为了晋级改阈值。
- [ ] 明显倾倒、持续饱和、非有限值、闭链爆开：保留日志和完整权重，保存后隔离诊断。原+2m/s突变失败就是此类风险，不能跳过。
- [ ] 普通性能不达标而物理健康：继续当前阶段，不因一次奖励变化重启。

## P2：轻度 DR 准备（尚未实现；下一项代码工作）

- [ ] 建立显式 `nominal` / `mild_dr` 配置入口和生效值报告。不要简单把 RM_DR_OFF 从1改0，旧默认会同时打开多类扰动，包括未校准弹簧。
- [ ] 从稳定速度检查点做隔离、无探索动作、配对同seed回放；追加至少两个seed，包含低速、正反向、停车。保留 nominal 基线。
- [ ] 初始候选范围（只是待验证设计，不是已实测或已部署）：质量0.95–1.05倍，腿/轮输出强度0.95–1.05倍，轮地摩擦在实际名义值附近±10%且动态<=静态。先分别验证，再组合。惯量随质量一致更新，避免重复随机化和非正定。
- [ ] 这一批先固定重心、PD、延迟、噪声、推扰、弹簧；后续在观测到鲁棒缺口后逐类增加，不是永远忽略这些误差。
- [ ] 读取最终仿真质量、惯量、轮材质、输出缩放、事件列表，验证随机化确实生效且 reset 不累乘。特别检查20k环境材质桶/PhysX限制，复用既有材质共享实现。
- [ ] 修好评测入口：当前 validate_speed.py/validate_rescue.py 启动时会无条件加载同目录 env.json；仅在 shell 设置 RM_DR_OFF 不能保证有效。提供独立配置文件参数或隔离代码目录，保持原 nominal 测试可重复。
- [ ] 跑短物理检查，再两轮PPO检查；不将试验更新后的权重冒充原配对检查点。通过后由用户已有授权在保存边界暖启动轻度DR，更新监督器、UI和自动化，保留原截止时间。
- [ ] 保留足够 nominal 验证，DR 下也必须守住平滑度、稳定性。弱DR性能未通过可以作为训练起点，但不得称鲁棒完成；物理安全失败先排查。

## P3：地形课程（未来，不能现在直接切）

- [ ] 平地适度DR和起停验证可靠后，再独立适配 SCUT V14 Rough v1 跑场。
- [ ] 当前复位是 flat-only，必须实现地形高度查询、合法闭链初态、出生净空、轮接触；不能把 terrain 参数改成 Rough 就当完成。
- [ ] 保留MOD4详细USD、电机/弹簧参数，按上游地形结构迁移；本轮不加载自家RMUC场地。
- [ ] 地形训练继承已有策略并继续DR；小陀螺/旋转台阶可按上游分支路线专项继续，不宣称所有科目同一阶段自动学会。

## P4：预算结束

- [ ] 到原deadline保存停止，确认无继续训练的子进程，最终名义回放，UI显示final_evaluation/finished。
- [ ] 若实际部署过DR，必须额外做相同seed的nominal与DR配对终验；未部署则明确写DR未开始。
- [ ] 报告达到的速度、未通过项、最佳与最终权重路径；不以奖励/步数替代验收。
- [ ] 完成终验后删除本线程自动化mod4-10；如另一AI不能操作Codex自动化，明确提醒用户/原线程协调，不能谎称已停用。
''')
write('03_READ_ONLY_COMMANDS.md',f'''
# 只读命令

连接：`ssh egde@10.24.4.210`。本文件不提供认证秘密。

```bash
cd {REMOTE}
bash {REMOTE_BUNDLE}/read_live_status.sh
tail -n 60 supervisor_speed.log
tail -n 80 train_3.log
# 晋级后按status.attempt查看train_4.log，而不是一直看旧日志。
```

`read_live_status.sh` 只读取，不启动仿真、训练、评测或修改状态。

```bash
# 查看实际环境配置，不等于运行中进程已重新加载它。
cat isaac/mod4/env.json
# 实际生效配置以当前run的run_manifest.json为准。
# 确认代码指纹
sha256sum isaac/mod4/mod4_task.py isaac/mod4/mod4_env.py isaac/mod4/scut_flat_rescue.py
```

现有监督器会发回放，不要重复运行 validate_speed.py。若评测失败，先看对应.log和.error.txt，确认旧评测已退出，再用相同checkpoint/seed/配置、唯一新输出文件名重试。

界面需要重新打开时才运行 `bash start_tui.sh`，避免堆出多个终端。
''')
write('read_live_status.sh',f'''#!/usr/bin/env bash
set -euo pipefail
cd '{REMOTE}'
python3 - <<'PY'
import json,pathlib,time
r=pathlib.Path.cwd();s=json.loads((r/'status.json').read_text())
print('Read at',time.strftime('%Y-%m-%d %H:%M:%S %z'))
keys=['stage','iteration','training_pid','attempt','speed_limit_m_s','latest_checkpoint','log_dir','deadline_epoch','evaluation_pid','evaluation_path','error','evaluation_error']
print(json.dumps({{k:s.get(k) for k in keys}},ensure_ascii=False,indent=2))
print('Remaining wall seconds:',max(0,s['deadline_epoch']-time.time()))
e=s.get('final_evaluation') or s.get('latest_evaluation') or {{}}
print('Evaluation',e.get('checkpoint'),e.get('seed'),e.get('seconds'))
for g in e.get('groups',[]):
 print({{k:g.get(k) for k in ['command_vx','profile','survival_fraction','strict_pass_window','strict_pass_instant_legacy','speed','vel_error','tilt','height_error','both_wheels_scut_history','delta','d2','stop_abs_speed']}})
print('physics',e.get('physics_pass'),'closure',e.get('max_closure_after_grace_m'),'mimic',e.get('max_mimic_after_grace_rad'))
PY
nvidia-smi --query-gpu=utilization.gpu,memory.used,temperature.gpu --format=csv,noheader
ps -eo pid,etime,args | grep -E 'supervise_speed.py|train_mod4_ppo.py|validate_speed.py|validate_rescue.py' | grep -v grep || true
''')
write('04_METRICS_AND_KNOWN_TRAPS.md','''
# 指标口径与不要重犯的错误

1. 当前窗口门槛是本任务自定，不是华南虎官方验收，更不是RM比赛标准。每速度组>=80%环境通过，不能只看总体平均。
2. 单环境按首个终止截断，15秒存活、速度误差<=max(.12,.25*abs(cmd))、平均倾角<=8°、高度误差<=.03m、动作delta/d2<=.18/.25、窗口双轮接触>=90%。全局闭链<2mm、mimic<.01rad。后退阈值必须用abs。
3. strict_pass_instant_legacy 保留旧“瞬时双轮>=90%”结果，不能把换判据当训练进步。
4. wheel_contact_scut 配置5ms，但当前lazy更新实测约10ms，3帧历史。每轮历史峰值通过不表示左右轮同时连续承重。
5. 2kHz诊断的低力事件大量仅0.5ms，轮子相对接触基线中位抬升接近0、最大约0.4mm。此前把瞬时双轮约54%直接称“不稳、腾空”证据不足。绝对几何间隙约1mm含接触偏置基线，不等于跳高1mm。
6. 车体约12.8mm起伏是旧诊断实测，但PD/弹簧因果尚未隔离证明。不要据此无测量改硬件。
7. 提速评测含ramp_brake_reverse，行内speed是全轨迹有符号平均，正反抵消后接近0正常；看steady_vel_error、stop_abs_speed和轨迹定义。不能称“给2m/s实际只有0.1m/s”。
8. torque裁剪为10ms采样computed-applied差>0.1Nm，不覆盖所有0.5ms子步峰值。max_tilt等报告字段是每环境极值的组平均，并非全环境最大值；后续鲁棒评测应补每环境分位数/最差值，而不偷偷改变旧报告含义。
9. 首0.5秒从均值中排除，但存活分母包括所有环境。若失败很早，sampled_envs很少，不能用剩余样本均值证明安全。
10. 检查点保存iteration不等于当前运行iteration；env步/秒是num_envs×policy_steps/墙钟，不是单环境物理步率。20kenv×24=480000 transitions/iteration。
11. 训练带探索动作，回放无探索，两者动作平滑度数值不能混用；time_out和训练success不等于正式通过。
12. 已修复三项移植错误：平地错误扣除未加载RMUC的0.19m地面；SCUT指数分母被Isaac std再次平方；只随机四主动关节破坏闭链。禁止带回旧实现。
13. 现训练是14.22kg底盘，不是装云台弹仓后的22kg整车；不把22kg直接覆盖本阶段资产。
14. 腿电机DM8009P、24V；轮DM3519配总减速比15.8（替换原箱，不再乘19.2）。实际执行端参数以run manifest及USD contract为准。
15. 当前弹簧为3500N/m预载模型，非SCUT240N恒力，也非已校准300–700N实物弹簧。不要为“对齐”直接复制另一台机器人的弹簧力。
16. “完整续训”这里指actor/critic/optimizer/std/iteration，不能声称物理环境状态、随机数流、课程内部计数逐位恢复；重新起进程会重置部分环境/课程计数，要检查日志。
''')
write('05_SCUT_UPSTREAM_AND_DR_MAPPING.md','''
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
''')
write('06_SAFE_SWITCH_RECOVERY_AND_BUDGET.md',f'''
# 保存、切换、故障恢复

当前硬截止epoch：`{state['deadline_epoch']}`，对应 `{deadline}`。目前没有新的预算。

1. 先确认当前进程cmdline/cwd属于本任务，不凭快照PID发信号；禁止pkill python、killall或停止整个桌面。
2. 健康运行不要手工切换，supervise_speed.py负责阶段晋级。若因实现DR需切换，先把候选代码、测试、显式环境配置和新监督器准备完。
3. 当前训练的rescue_training.py有STOP_AFTER_SAVE机制：只在**当前run日志目录**创建该文件，训练会在下一次原子完整保存时退出（一般每25轮），而不是立刻强杀。不能在旧run目录写错。
4. 同时必须处理旧监督器，避免它把计划停止解释成预算结束并启动final回放。检查源码后只终止本任务旧监督器或增加明确交接模式；不能先杀训练再想怎么恢复。
5. 验证新完整checkpoint：CPU torch.load成功，有actor_state_dict、critic_state_dict、optimizer_state_dict、iter，tensor有限；记录SHA256。 `.partial`不能用。验证旧trainer已退出，才启动新trainer。
6. 新阶段使用唯一run/log名，保留RM_KEEP_STD=1，runner.load恢复actor/critic/optimizer/std；不得使用会重写std的旧默认暖启动方式。
7. 保留同一绝对deadline，在新env与监督器都传递它；记录源checkpoint、代码hash、环境差异、实际物理合同。不能简单再调用一次初始化10小时的脚本。
8. 启动后检查manifest与首轮PPO输出、唯一trainer、NaN/PhysX错误、GPU和最新完整保存；只看到进程PID不算完成。
9. 更新同目录status.json/终端监控/原线程自动化mod4-10的当前阶段说明，避免后台旧指令拉回错误任务。
10. 评测无权延长训练：到点停止训练，允许做必要终验，但不能偷偷继续优化参数。

故障分支：性能波动不重启；程序崩溃/NaN/映射错误先保留现场，隔离修复，原截止前从最后完整权重恢复。若主机再次重启，要重新核算而非自行许诺补足；本交接不授权额外预算。

不要直接重跑 `launch_speed.py`、`resume_after_reboot.py`、旧 `supervise_rescue.py` 的main；它们包含一次性历史假设。
''')
write('PROMPT_FOR_NEXT_AI.txt',f'''
接管MOD4轮腿RL。先读本文件夹00_START_HERE，再按02任务清单执行。远端egde@10.24.4.210，任务根目录{REMOTE}。本包快照时间{now}，必须先只读核查实时status/进程/报告，禁止双开或凭旧PID停止任务。
用户已授权修复和继续训练，目标平地稳站、慢走、稳定跑并逐步鲁棒；目前正在从±1.2推进±1.5再有条件到±2m/s。监督器supervise_speed.py已部署自动评测/晋级，不重复发探针。截止{deadline}不延长，20kenv×24、16/4、详细MOD4 USD、实际root0.25m，DR关闭。保留所有旧检查点，从actor/critic/optimizer/std继续，不能从零训练。
现在最先做的是核查首次>=5250检查点提速回放。若仍在跑就等待。1.5稳定且2m/s安全后让原监督器升2；不能因为瞬时接触低就称腾空，也不能把训练success当通过。已实测静止突变+2m/s失败，而缓升到±2m/s存活，故禁止跳级。
下一个尚未实现任务是显式轻度DR profile与配对评测；绝不能直接切RM_DR_OFF=0，它会同时启用旧强扰动和未校准弹簧。按清单逐项读回验证参数、做隔离物理/PPO检查、安全保存后接续，原deadline不变。真正安全稳定后再考虑SCUT Rough v1，当前reset是flat-only。300–700N弹簧DR未校准暂缓。
给用户只报告有证据的改进。上游本来含DR，我们先关闭是MOD4排错过渡，不是上游固定课程。更新终端和自动化；健康无实质变化保持安静，故障、晋级或预算结束报告。不要把交接文档视为授权动其他AI的进程。
''')
nexttask={'snapshot_at':now,'remote_root':REMOTE,'remote_bundle':REMOTE_BUNDLE,
 'current_stage':'flat_speed_1p5_then_2','status_snapshot':{k:state.get(k) for k in ['iteration','stage','speed_limit_m_s','latest_checkpoint','training_pid','attempt']},
 'deadline_epoch':state['deadline_epoch'],'deadline_beijing':deadline,
 'immediate_action':'Read live status; await existing supervisor first speed evaluation at iteration >=5250; do not duplicate',
 'implemented':['speed_preflight','atomic_checkpoint_handover','speed_1p5_training','conditional_speed_2_promotion','hourly_speed_evaluation','terminal_monitor'],
 'not_implemented':['explicit_mild_DR_profile','paired_nominal_DR_evaluation','DR_training_handover','rough_terrain_closed_loop_reset'],
 'automation_id':'mod4-10','credentials_included':False}
write('next_task.json',json.dumps(nexttask,ensure_ascii=False,indent=2))
manifest={str(p.relative_to(LOCAL)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in LOCAL.rglob('*') if p.is_file() and p.name!='SHA256SUMS.json'}
write('SHA256SUMS.json',json.dumps(manifest,ensure_ascii=False,indent=2))
# Publish only inside a new dedicated handover folder; no active training file is changed.
def mkdir(path):
    try:sftp.mkdir(path)
    except IOError:sftp.stat(path)
mkdir(REMOTE_BUNDLE)
for p in LOCAL.rglob('*'):
    rel=p.relative_to(LOCAL).as_posix();dest=REMOTE_BUNDLE+'/'+rel
    if p.is_dir():mkdir(dest)
    else:sftp.put(str(p),dest)
sftp.chmod(REMOTE_BUNDLE+'/read_live_status.sh',0o755)
archive=LOCAL.with_suffix('.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in LOCAL.rglob('*'):
        if p.is_file():z.write(p,LOCAL.name+'/'+p.relative_to(LOCAL).as_posix())
sftp.put(str(archive),REMOTE+'/'+archive.name)
# Verify uploaded artifact bytes rather than assuming transfer success.
for rel,digest in manifest.items():
    with sftp.open(REMOTE_BUNDLE+'/'+rel,'rb') as f: actual=hashlib.sha256(f.read()).hexdigest()
    assert actual==digest,rel
sftp.close();ssh.close()
print(json.dumps({'local_folder':str(LOCAL),'zip':str(archive),'remote_folder':REMOTE_BUNDLE,'files_verified':len(manifest),'snapshot_iteration':state.get('iteration')},ensure_ascii=False,indent=2))
