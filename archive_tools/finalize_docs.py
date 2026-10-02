from pathlib import Path
import json
import shutil

R=Path(__file__).resolve().parents[1]
stats=json.loads((R/'provenance/archive_statistics.json').read_text(encoding='utf8'))
inventory=json.loads((R/'provenance/capture_inventory.json').read_text(encoding='utf8'))
entries=[e for e in inventory['entries'] if e['captured']]

def evidence(name):
    matches=[e for e in entries if (e['stage']+'/'+e['relative_path']).endswith(name)]
    matches.sort(key=lambda e:(e['site']!='remote',len(e['relative_path'])))
    return matches[0]['repository_path'] if matches else 'history/INDEX.md'

def write(path,text):
    p=R/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf8')

write('README.md',f'''# polar-rl-train

MOD4 强化学习项目的修复、训练、诊断和交接档案。仓库创建于 2026-10-03，默认私有。

本次从本机及 4090 目标机收集 **{stats['stages']} 个资料目录、{stats['captured_files']:,} 份文件**，为 **{stats['experiment_tags']} 条有保存证据的试验/修复/验证记录**补建提交和注释 Git 标签。另有每目录一个 `version-*` 标签。包含成功、失败、无效探针、被否决方案及其他 AI 留下的资料。

## 从这里看

- [按阶段看修了什么](docs/REPAIR_TIMELINE.md)：人工整理的修复主线、重要纠正和未完成事项。
- [完整试验/修复标签表](history/INDEX.md)：每条记录的标签、类别和证据链接。
- [全部版本目录](history/VERSIONS.md)：83 个目录各自的来源、源码和交接说明。
- [当前生产状态快照](CURRENT_STATE.md)：归档时实际阶段与未部署候选；不会自动更新为实时状态。
- [项目代码入口](project/README.md)：当前生产源代码的固定副本及外部运行依赖。
- [归档范围与缺口](docs/ARCHIVE_POLICY.md)、[检查结果](provenance/ARCHIVE_VALIDATION.json)。

## Git 标签是什么

`trial-日期-编号-试验名` 对应一次有证据的试验、训练运行、修复/诊断、失败程序或保存源码变体。类别写在记录里；不是每个标签都代表一次成功训练。`version-local--...` / `version-remote--...` 对应原始资料目录的完整归档快照。标签直接指向本次创建的提交，可在 GitHub 的 **Tags** 或提交历史查看，也可以：

```bash
git clone https://github.com/lulunomaro/polar-rl-train.git
cd polar-rl-train
git tag -l 'trial-*'
git show <tag>
git switch --detach <tag>
```

这些是**补建的证据历史**：提交时间是真实归档时间，记录另列原试验日期及来源。没有把今天的提交伪装成当时提交，也没有根据目录名猜测作者。保存的运行源码快照可证明当时版本；仅有当前源码或报告的记录会明确写出证据等级。

## 收录内容

`sources/local/` 与 `sources/remote/` 保留原相对路径，包含代码、配置、报告、交接、备份和资产。`objects/sha256/` 是去重内容库，`provenance/capture_inventory.json` 记录原路径、字节数、时间、原始/归档哈希及采集方式。训练 `run_manifest` 的环境参数、源码指纹和可找到的 `src_snapshot` 一起保留；相邻运行配置差异有单独记录。

**模型权重和大型二进制轨迹没有上传到 Git。** [检查点索引](provenance/checkpoints.jsonl) 保留 {stats['external_checkpoints']:,} 个文件条目的路径、大小、时间和能从原凭据解析到的哈希；重复目录副本也计作文件条目。未读取权重内容，不伪造缺失哈希。原目标机/本机权重原样保留。大型日志保留明确标注的首尾摘录，详见归档范围。

## 以后每次修复怎么记

先写一份说明：问题、改动、配置/来源权重、检查协议、实际结果和仍失败的项目。再把改变的代码/配置/证据连同标签一起推送：

```bash
python archive_tools/record_experiment.py --id yaw6-regression-01 --title "6rad/s 回归复核" --kind evaluation --note-file notes/yaw6.md --files project/isaac/mod4/env.json reports/yaw6.json --validation "协议与结果见报告" --push
```

这是用法示例，需替换为真实文件。脚本拒绝覆盖标签、夹带已暂存的无关改动或提交权重/明文凭据。历史批量构建脚本仅用于本次首次归档，不应重跑来改写既有标签。

仓库只记录项目，不会启动训练、变更目标机预算或停止现有任务。上游代码与资产的原许可证/来源保留，[第三方说明](docs/THIRD_PARTY.md) 不替代原许可。
''')

timeline=[
 ('09-10～09-15','早期模型/场地/材料与规模试验','保存机械模型、RMUC 来源、材料合并、不同 env/solver 的运行配置与快照。后续平地阶段不因此声称在 RMUC 训练。','ENV_SCALING_AB_20260927.md'),
 ('09-16～09-18','其他 AI 的平地专项对照','收录 DEEPSEEK_V41_20260916 中延长训练、PD、动作幅度、噪声 A/B 与原总结。原文判断保留为当时主张；作者仅按证据声明，不由目录名推断。','SUMMARY.md'),
 ('09-27','完整续训、12k/16k/20k 测速与手动关机恢复','保留所有测速、完整权重恢复和监督记录。用户确认的手动关机不能归因于 20k OOM；测速临时策略不替代正式来源。','RESUME_AFTER_MANUAL_SHUTDOWN_20260927.md'),
 ('09-27～09-28','弹簧、强姿态惩罚与高度实验','保留弹簧关/开和力曲线对照、SCUT 适配、强倾角/低高度惩罚及高度课程。旧弹簧 DR 报告不等同已标定的实物力—行程验收。','STRONG_POSTURE_EXPERIMENT_20260928.md'),
 ('09-29','SCUT 平地移植三项修复','真实平地 z=0，纠正未加载 RMUC 射线地面扣高度；纠正指数 sigma 分母被再次平方；使用完整闭链逆解复位库。暖启动保留网络/优化器/std。','MOD4_scut_rescue_20260929/isaac/mod4/scut_flat_rescue.py'),
 ('09-29','接管审计与错误判断纠正','保留另一 AI 窗口判据和瞬时影子；纠正“瞬时低力=厘米腾空”的过度推断。实测 lazy 历史 10ms 不能冒称已实测 3×5ms。','RESTART_AUDIT.md'),
 ('09-30','直线课程范围修复与单因素接触诊断','关闭误覆盖的旧 gyro yaw 课程；保留 solver/轮网格/固定腿探针。对照未一致改善的方案不部署，不把相关性写成原因。','REPAIR_PLAN.md'),
 ('09-30','接触采样积分修复','0.5ms 子步冲量累计，每 5ms 写均力历史。冻结物理数组对照和奖励门控验证保留；旧端点/eager/积分并列，统计变化不是学习进步。','MOD4_contact_integrated_repair_20260930/README.md'),
 ('09-30～10-01','原生 Plane 地板修复与续训','原 4km 薄地板失败样本的 raw 法向证据及同策略单因素对照；原生 Plane 消除该异常。不把所有失败归因于地板，保留未部署限速方案。','FINDINGS.md'),
 ('10-01','轻 DR 的实际回读、试训和配对','white_v1 只随机共同质量惯量、主轮摩擦和六电机输出；保留 nominal 配对、全量 combined 警告及独立物理验收。','MILD_DR_HANDOVER_20261001.md'),
 ('10-01～10-02','执行器裁剪诊断与预算/归档程序修复','纠正策略顺序与执行器局部 gain 顺序错配；预算扩展 ID/唯一账本、SameFileError 安全归档、STOP 控制目录和孤儿预检尾段核算保留。','MOD4_BUDGET_ADD20H_20261002_HANDOFF.md'),
 ('10-02～10-03','纯自转 1–2→3→4→6rad/s 阶梯','保留各档短预检、正式训练、两次技能及两 seed nominal/white 回归。4rad/s 有多 seed 成熟证据；归档时 6rad/s 仍在学习，目标 120rpm 不是已达到。','rate4p0_model15583_multiseed.json'),
 ('10-02～10-03','传感器 DR 的拒绝与隔离定位','全 sensor_v1 与 delay-only 出现真实异常，保留拒绝/回退证据；noise-only 单 seed 冻结检查不能冒称正式部署或实车适配完成。','SENSOR_REJECTION_AND_ABLATION_20261003.md'),
 ('10-03','本机最新策略与普通转弯候选','保存 model15600 拉取凭据、交互播放器修复、短冻结弧线检查和已有四份 15s 基线流程。未部署普通转弯 PPO，不把 3s 泛化当 15s 毕业。','LOCAL_PLAYBACK_OPENED.json'),
 ('未完成','世界定向移动、Rough、云台、MoE 与实物弹簧','保留已写的数学/SDK/地面查询/来源核对代码和待办；这些准备不等同真实训练和完成验收。','ROUGH_NEXT_TASKS_20261001.md')]
lines=['# 修复与试错主线','',
 '这里是阅读导航，原报告保留完整指标、协议和失败样本。历史计划可能已被后续审计取代，不能按旧计划直接重启生产。','',
 '|日期|版本/问题|实际变化与边界|原证据|','|---|---|---|---|']
for date,title,note,name in timeline:
    path=evidence(name)
    label=Path(name).name if path!='history/INDEX.md' else '原始记录索引'
    lines.append(f'|{date}|{title}|{note}|[{label}](../{path})|')
lines+=['','## 已纠正的说法','',
 '- 低力比例不是腾空比例；窗口/积分高通过率不是持续承重，也不是策略学习进步。',
 '- 旧报告的上游/赛场标准主张原样保留为历史；当前门槛是本项目自定实验条件。',
 '- “训练成功/奖励高”不能替代首次失败截断、逐环境和多种子确定性回放。',
 '- 当前 3500N/m 预载弹簧不是 SCUT 240N 恒力；300–700N 实物力—行程未标定。',
 '- 新增预算只来自明确用户授权，已应用扩展不得再次执行。',
 '- 旧源码/评测程序有偏差或缺口时明示；不因补建标签填造历史。','']
write('docs/REPAIR_TIMELINE.md','\n'.join(lines))

write('docs/ARCHIVE_POLICY.md',f'''# 归档范围与证据规则

收集范围：本机工作区中 MOD4、模型/播放器、修复/交接/诊断、机械模型及相关场地项目目录；目标机 `/home/egde/rl_candidates` 全部直系项目目录，以及 `/home/egde/fangzhen_linux` 的 isaac/train/logs/runs4090/incoming/sim2sim_mod4 与根文件。完整清单见 provenance。

- {stats['captured_files']:,} 个文件条目实际捕获，内容去重为 {stats['unique_objects']:,} 个 SHA256 对象；{stats['indexed_files']:,} 个文件条目已索引。
- 包含 `.py.before` / `.bak*` 等旧源码变体和当前对照 diff；这种 diff 可能包含多个中间改动，不能伪称一次已证明的修复。
- 包含 {stats['event_kinds']['training_run_configuration']} 个不同的训练运行配置记录；配置存在不等同训练完成。能找到的每运行源码快照及原源码哈希一起关联。
- {stats['log_excerpts']} 份超过 5MB 的日志仅保留头 32KiB、尾 512KiB，中间缺失已在原位置明确标注。其完整原始 SHA 未新计算。
- `.pt/.pth/.onnx`、大型轨迹、压缩包、视频及 TensorBoard 二进制事件仅索引。Checkpoint 哈希来自已有记录且明确标注未为本归档重算；查不到的留空。
- 超过文件大小限额、非选定类型、凭据/密钥路径、符号链接和依赖/缓存目录不复制。可读来源错误 {stats['source_capture_errors']} 个；这是指定范围内的结果，不是“整个电脑和所有 AI 历史已恢复”。
- 凭据不输出、不打包；文件原始哈希与必要的脱敏/编码转换后归档哈希分开。采集时发生变化的文件明确标注；本批检测到 {stats['moving_files']} 个。

## 历史与标签

提交与注释标签现在补建，不回填伪造的历史 Git 时间。`historical_date` 来自路径日期或捕获源文件 mtime，`date_basis` 会说明；复制/旧阶段目录的日期可能不精确到实际开训日。配置比较只说明同目录相邻归档运行的参数差异，不据此猜父检查点或因果。

证据级别：`preserved_run_source_snapshot` 是原运行留下的代码；`preserved_backup_variant` 是旧源码变体；`stage_source_at_archive_time` 只证明当前收集时目录内容。若只有报告，无当时代码，就不会声称能完整复现。

各 JSON 的 pass/strict/physical/safety 布尔量原样并列，不自动合成“毕业”。短物理预检、PPO 预检、冻结验收、正式生产、准备、拒绝和回退分别判断。作者未知时不猜测；目录名 DEEPSEEK 不自动等于作者身份，原文的自述也作为来源声明保留。

所有旧分歧和后来证伪的判断都保留。阅读旧报告时应同时看修复主线和更新审计。未保存/已删除/未落盘的代码、聊天或结果不能重建，未来新增试验应实时提交和打标签。
''')

licenses=[e['repository_path'] for e in entries if Path(e['relative_path']).name.lower().startswith(('license','notice'))]
write('docs/THIRD_PARTY.md','''# 第三方代码和资产

这是用户项目的私有归档，不重新授权上游代码/机器人 CAD/场地资产，也不自动添加覆盖全部内容的许可证。

SCUT wheeled-legged_RL 来源为 https://github.com/scutrobotlab/wheeled-legged_RL 。有关固定提交 `b8ff79f3df855faf9dc92f4a282bd80c42649466` 的关键文件字节核对见保存的 PINNED_SOURCE_VERIFICATION；归档目录缺 .git 元数据，不能冒称验证了全仓库 HEAD。复旦/浙江大学及其它参考资料按原交接、来源清单和目录保存，不能把参考机器人配置当 MOD4 已验证硬件。

已找到并保留的许可证：

'''+''.join(f'- [{p}](../{p})\n' for p in licenses)+'''
未找到许可的资产保留来源和原始路径，公开发布或复用时需按其原权利人要求处理。当前仓库保持私有。
''')

stage='MOD4_scut_spin_rate_20261002'
exported=[]
for e in entries:
    if e['site']=='remote' and e['stage']==stage and e['relative_path'].startswith(('isaac/mod4/','train/')):
        dest=R/'project'/e['relative_path'];dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(R/e['repository_path'],dest)
        exported.append({'path':dest.relative_to(R).as_posix(),'source':e['repository_path'],'sha256':e['object_sha256']})
write('project/CURRENT_VERSION.json',json.dumps({'source_root':'/home/egde/rl_candidates/'+stage,
    'captured_source_only':True,'files':exported,'training_not_started_by_archive':True},ensure_ascii=False,indent=2))
write('project/README.md','''# 当前项目代码快照

`isaac/mod4` 和 `train` 是归档时正式自转生产目录的固定源码副本；映射与 SHA256 见 CURRENT_VERSION.json。完整来源包含更多运行快照，见 ../sources/remote/MOD4_scut_spin_rate_20261002。

本目录不是自动安装器。运行依赖原目标机的 Isaac Lab / Isaac Sim、PyTorch、rsl_rl 和 USD 合同/资产；版本见保存的 run_manifest。部分配置仍是原绝对路径，模型权重是外部索引，因此未经路径/版本核对不可直接运行，更不能把旧 one-shot 交接/恢复脚本直接再跑一遍。

本机播放器来源在 sources/local/mod4-onnx-mujoco-launcher-git 及 MOD4_LOCAL_LATEST_SPIN_20261003；原播放器仓库和当前窗口均未因本次归档改动。
''')
write('CURRENT_STATE.md','''# 2026-10-03 归档时状态

正式训练仍在 MOD4_scut_spin_rate_20261002：20k env×24、solver16/4、原生平地、实际 root 0.25m、white_v1、完整 actor/critic/optimizer/std 暖启动。成熟 4rad/s model15583 有两 seed nominal/white 的 15s 回归证据，6rad/s 为当前学习档。归档时文件/status 只作快照，实时情况需读实际进程和唯一账本，不能把这里当实时监控。

目标原地 2转/秒=4π rad/s=120rpm，尚未达到。自转世界定向净进度 0.5m/s、普通组合转弯、Rough、云台负载和 MoE 不宣称已完成。普通转弯有独立冻结候选和短基线，未启动新转弯 PPO；传感器 full/delay 候选出现异常而拒绝，noise-only 初证据尚未正式部署。

唯一账本位于 MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json，总180000秒（50小时），36000+两条已应用72000扩展；归档不追加/复制/重置预算。两小时线程巡检授权继续，现有训练和其它 AI 任务未被本次收集打断。

旧窗口、eager5ms、积分均力及真实卸载/间隙/滑移保留。低力不是腾空，积分100%不是连续承重；实物弹簧力—行程未校准，仿真通过不是实车认证。
''')
print('Documentation and current source export complete:',len(exported),'files')
