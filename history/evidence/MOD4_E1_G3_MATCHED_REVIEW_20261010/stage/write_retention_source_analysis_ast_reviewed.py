"""Build source-grounded SCUT analysis and explicit repair work order, no plant imports."""
from pathlib import Path
import ast, hashlib, json, time, zipfile
D=Path(__file__).resolve().parent; W=D.parent; R=D/'reports'
H=lambda b:hashlib.sha256(b).hexdigest()
def save(name,value):
 p=R/name; assert not p.exists(),p
 p.write_bytes(value.encode('utf8') if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2).encode('utf8'))
audit=json.loads((R/'SCUT_SOURCE_AUDIT_1791633510.json').read_bytes()); pin=audit['commit']
paths={x['path']:x for x in audit['files']}; anchors=[]
lookups={
 'source/agent_tasks/agent_tasks/manager/mdp/isaaclab/commands.py':['class SpecialModeUniformVelocityCommand','def set_training_iteration','def _assign_special_modes'],
 'source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py':['iteration_start=3000','iteration_start=4000','iteration_start=2000','class WheelbipeV14RoughEnvCfg('],
 'source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/cfg_utils.py':['V14_ROTATION_TERRAIN_COMMAND_OVERRIDES_1','"stair_for_rm_rot"'],
 'source/agent_tasks/agent_tasks/manager/mdp/terrain/terrain_command_manager.py':['disable_special_mode'],
 'scripts/rsl_rl/train.py':['def _load_policy_for_finetune','load_optimizer=True','load_iteration=True'],
 'scripts/rsl_rl/cli_args.py':['moe','cmoe'],
 'pretrained/26_infantry/rough_rotation_stair/2026-07-30_09-16-27/params/agent.yaml':['class_name: ActorCritic','class_name: PPO','launch_checkpoint:','resume_training: false'],
 'pretrained/26_infantry/rough_rotation_stair/2026-07-30_09-16-27/params/env.yaml':['commands:','special_modes: !!python/tuple','rel_envs: 0.15','rel_envs: 0.3','iteration_end: -1']}
for path,needles in lookups.items():
 item=paths[path]; raw=Path(item['local']).read_bytes(); assert H(raw)==item['sha256']
 lines=raw.decode('utf8').splitlines()
 anchors.append(dict(path=path,sha256=H(raw),bytes=len(raw),url=item['url'],matches={n:[i+1 for i,s in enumerate(lines) if n.lower() in s.lower()] for n in needles}))
parent=W/'MOD4_E1_G3_35MM_SCOPE_PREPARE_20261010/artifacts/e1-g3-derived35mm-complete-route-manifest-reviewed-v2-frozen.zip'
with zipfile.ZipFile(parent) as z:
 names=['runtime/isaac/mod4/e1_terrain_runtime.py','runtime/isaac/mod4/e1_rough_recipe.py','runtime/isaac/mod4/directional_spin_runtime.py']
 own=[]
 for name in names:
  raw=z.read(name); p=D/'implementation'/('original_'+Path(name).name); assert not p.exists() or p.read_bytes()==raw;
  if not p.exists():p.write_bytes(raw)
  own.append(dict(member=name,sha256=H(raw),bytes=len(raw),local=str(p.resolve())))
 narrow=z.read(names[0]).decode();assert 'uniform BODY vx[-.3,.3]' in narrow and 'rel_standing_envs=.2' in narrow
 recipe=z.read(names[1]).decode();weights=next(x.value for x in ast.walk(ast.parse(recipe)) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='intro_weights' for t in x.targets)); assert ast.literal_eval(weights)==dict(plane_for_rm=.30,tiny_step=.20,slope_for_rm_high=.20,inv_slope_for_rm_low=.15,random_uniform_for_rm=.15)
diag=json.loads((R/'PAIRED_PREFIX_RETENTION_DIAGNOSIS.json').read_bytes())
summary={role:{group:{k:v for k,v in row.items() if k!='incomplete'} for group,row in groups.items()} for role,groups in diag['source_and_candidate'].items()}
save('SCUT_RETENTION_FINDINGS.json',dict(epoch=time.time(),trial_id='SCUT-EXPERT-RETENTION-MATCHED-ANALYSIS-01',commit=pin,source_audit=str((R/'SCUT_SOURCE_AUDIT_1791633510.json').resolve()),anchors=anchors,own_original_source=own,actual127=summary,
 proof_levels=dict(implemented='persistent eligible on-policy command modes; terrain-specific restrictions; flat-to-rough transfer',saved_training_configuration='2026-07-30 rough run ordinary ActorCritic/PPO, old flat model8000; broad signed commands',not_proven='causal anti-forgetting ablation, frozen expert gradient isolation, gate retention, EWC or old-policy distillation in examined V14 path'),
 inferred_mechanism='Old skills remain in current rollout distribution after new tasks are enabled; our all-family narrow yaw0 command stream is a plausible forgetting mechanism, not causally proven.',
 moe_scope='CLI contains MoE/CMoE parameter entries. No matching complete active expert implementation/configuration plus retention results was established in downloaded registered V14 path; do not infer absence across private code.',
 historical_configuration_difference='Current defaults dash2000/lowspin3000/midspin4000, end-1. Saved July30 rough commands all three starts0/end-1. Fractions apply eligible non-standing envs, not terrain quotas.',
 no_model_import_or_GPU_or_budget_write=True,new_budget_seconds=0))
base=f'https://github.com/scutrobotlab/wheeled-legged_RL/blob/{pin}/'
report=f'''# 华南虎持续学习与 MOD4 E1 退化：源码及实际参数审查

已审公开版本 `{pin}`。本次取到114份源码/参数文件，6次HTTP超时原样记录。判断针对可见V14训练路径和已保存2026-07-30粗糙地形参数，不能替代其私有实现、完整训练日志或抗遗忘消融实验。

我们的实际问题位于同一E1策略连续更新过程中：G3 source32058→formal32063完整恢复actor/critic/std/optimizer、D1-D7、全局和私有CPU/CUDA流已经核验。新35mm几何的terrain_state_restored_exact=false是显式几何切换；没有证据说这次退化来自漏恢复优化器或物理状态。gate尚未训练，当前不能归因为路由器专家坍塌。E0冻结只能保护E0，无法自动保护仍在更新的E1内部旧能力。

|实际配对指标|32058旧源|32063短窗后|解释|
|---|---:|---:|---|
|35mm完整十波两轮退出，前/倒|24/27、26/27|{summary['candidate32063']['forward']['whole_wave_exit']}/27、27/27|未完成有效前缀全部保留|
|再含200mm后支撑，前/倒|17/27、25/27|13/27、26/27|倒退改善不抵消前进下降|
|旧world完整signed circle|62/64|56/64|最大abs cross .053276684→.060651110m/s，原容差与false不变|
|旧负向4π|5/8|2/8|正向仍8/8；不能拿均值掩盖逐环境有符号误差|
|旧±1.5直线误差，负/正|.024461027/.043439623|.026505746/.044777345|小幅变化；不是所有旧技能同时崩溃|

1. **旧任务一直有新rollout。** `SpecialModeUniformVelocityCommand`按迭代启用模式，end=-1表示一直保留。每次重采样在符合条件的非站立环境中做互斥概率分桶，桶顺序随机，剩余环境保持普通命令。不是每阶段覆盖上一阶段命令，也不是拿旧PPO轨迹直接重放。当前默认冲刺2000、低速旋转3000、中速旋转4000才启用；实际July30参数三者均从0启用，所以不能混用两份配置。[实现]({base}source/agent_tasks/agent_tasks/manager/mdp/isaaclab/commands.py)、[当前配置]({base}source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py)。持续覆盖可能减轻遗忘是根据代码的推断，仓库没有在这些文件中给出与MOD4对应的因果消融证明。

2. **真实粗糙地形训练仍混有旧动作。** July30保存参数使用普通ActorCritic/PPO、24steps、LR1e-4/adaptive、std1；从flat model8000加载作finetune（resume_training=false）。基础vx[-2.7,2.7]、yaw±2π、10%站立；非站立且具备准入条件的环境中低/中纯转各15%，冲刺30%。低纯转yaw±[2π,3.25π]，中纯转±[3.25π,4.5π]，冲刺vx±[2,3]。这些比例不是整个训练批或地形族配额，不可拿来替换我们30/20/20/15/15地形比例。[实际env参数]({base}pretrained/26_infantry/rough_rotation_stair/2026-07-30_09-16-27/params/env.yaml)、[实际agent参数]({base}pretrained/26_infantry/rough_rotation_stair/2026-07-30_09-16-27/params/agent.yaml)。参数说明训练意图，不证明每种模式实际访问次数或最终保留率。

3. **按实际地形约束命令。** rough类继承flat_v2后换地形。普通平面和连续地形保留宽命令；stair_for_rm_rot覆盖速度±[.5,2]、非heading yaw[-1,1]，并关闭special mode和空中模式。先判断地形可支持的行为，再决定该环境采样哪些模式。[覆盖配置]({base}source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/cfg_utils.py)、[实际地形命令管理]({base}source/agent_tasks/agent_tasks/manager/mdp/terrain/terrain_command_manager.py)。这与我们的S7净空限制一致，不能把高速旋转塞进E1跨坎/起伏/洞边。

4. **没有核到“MoE已经解决永久遗忘”的证据。** cli_args存在MoE/CMoE入口，包括router温度、负载均衡、expert辅助损失；已审注册V14和July30agent实际使用普通ActorCritic/PPO，没有对应的完整冻结专家实现与旧能力保持结果。冻结旧专家、只训练新专家、再训练gate是我们原计划的保护办法，不应冒称华南虎公开实验结论。PPO当前rollout的KL也不是长期旧任务记忆。未核到本路径使用EWC、旧教师蒸馏或经验回放来保证旧任务。[参数入口]({base}scripts/rsl_rl/cli_args.py)、[加载语义]({base}scripts/rsl_rl/train.py)。

本项目可用的修复方向是**保留必要旧命令的在线采样，限制在已验收的平地与净空范围**。当前E1的RoughStraightCommand把五类地形所有环境都改为20%站立、其余BODY vx[-.3,.3]、vy=yaw=0；即便30%plane_for_rm也没有旧定向移动数据。这是最直接的分布差异。下一单轴修复应在既有平地族引入必要的旧直行和world yaw±1–2在线命令，起伏/坡/坎维持原低速yaw0；不能把world yaw1–2误写成4π移动，不能扩大S7或同时改reward/LR/DR/几何。

新命令范围必须核实际terrain assignment/净空、命令RNG完整保存恢复、初次新physical episode、实际采样直方图和两方向覆盖，再做自己的CPU/SDK/native/完整PPO预检弃权重和300s有界观察。已有clock、同几何和D0-D7证据按SHA复用，不再45min clock。候选须完整保存并复评原地形与flat/spin/world，不能用reward或健康代替保留能力。负4π属于旧诊断事实；E1不通过扩张S7高转速任务来追分。

本轮128已实际发布：只把冻结接近段.65m改.40m，仍15s、全十波、两轮200mm后支撑，32058和32063初始化配对。两轮前支撑预测仍>.2m，实际raw回放才算证据。128不更新权重，只判断窗口/接近段因素；原126/127失败保留，不宣称35mm全部通行、永久抗遗忘或RM70mm毕业。所有真实拒绝、CRC读者错误和锁定位拒绝并列保存，canonical828000/new0保持。
'''
save('SCUT_RETENTION_DETAILED_REVIEW.md',report)
published=json.loads((R/'PAIRED_APPROACH_PUBLISHED.json').read_bytes())
work=dict(epoch=time.time(),trial_id='E1-G3-MATCHED-RETENTION-NEXT-WORK-01',actual127_complete=str((W/'MOD4_E1_G3_LEARNING_PREPARE_20261010/reports/CANDIDATE_127_REVIEW_1791592441.json').resolve()),decision='Do not blind continue32063 or advance50mm; perform paired128, then new command-only retention repair on verified plane family after contracts.',source_preferred=dict(iteration=32058,sha256='42cdc9d24519778a9da3e35b05a3eb3bb5745760c26a5842c78fcde2bd39e53b'),rejected_blind_source=dict(iteration=32063,sha256='e912058d079bf1db7e40c546c54f55568218d514937cba30c65d8c913882a2cf'),paired128=published['jobs'],readers=dict(collect=str((D/'collect_approach128_actual.py').resolve()),review=str((D/'review_approach128_actual.py').resolve())),next_command_scope='Preserve existing30%flat family, other4families/proportions/35mmgeometry; only eligible clear flat supports receive retained signed straight/world yaw1-2 on-policy modes; no high4pi rough spin/newS7/S8.',must_verify=['Actual128 raw before route conclusion; preserve all original valid failure prefixes','Full source32058 behavior binding, source bytes/SHA, own fullsave/old closed processes/two source-located locks/canonical active-Sactive empty/unique settled segments','New command masks from actual geometry assignments/physical clearance, no task mask actor/gate truth','CPU math/RNG/save/resume + SDK/native actual contact/ground/hardware + complete128x2/20kx4 PPO discard only genuinely new command scope once each samecanonical','Actual mode histogram signed directions/family; worldBODY vx=2Vcos(theta-alpha),vy0/no position correction','Formal300s includingload-learn-save-exit only after new contract PASSED; next complete terrain/flat/spin/world matched review, no autonomous blind second block'],fixed='MasterSHA/RM003002001/E0 frozen/clock/D0-D7/reward/LR/KEEPSTD/hardware/5family30-20-20-15-15/828000/sixextensions/new0/S3otherexperts-gate-reserve; S8laterapproval/gateuntrained93-94pausedMuJoCoended',monitor='mod4-10 ACTIVEevery2h; healthy/pending quiet; actual new stage/failure/major regression/human action notify; no5minSSH',permanent_anti_forgetting_proven=False,new_learning_launched=False,new_budget_seconds=0)
save('NEXT_E1_G3_RETENTION_REPAIR_WORK_ORDER.json',work)
save('NEXT_E1_G3_RETENTION_REPAIR_WORK_ORDER.md','# E1 G3 完整退化审查后的接续工作单\n\n'+report+'\n\n实际128 job/只读reader及新范围准入条件以同名JSON为准。所有旧once/main/resume关闭不可重跑；新命令修复是独立新范围，不能热改原338。\n')
errors=[('READ-01','zipmember lookup frozen_history_e1_terrain.py returned empty then IndexError','Correct actual frozen_history_flat.py; no mutation'),('READ-02','sync_g3_formal_closeout_metadata_once.py localpath not found','Actual sync_g3_formal_closeout_once.py only read; oldsync not executed'),('READ-03','rg literalWindows wildcard produced error123; inaccessible unrelated unpack dir','Exact rg --files/actual paths; no training action'),('READ-04','new_runtime and local reports/NEXT path not found; premature async SCUT file lookup','Actual payload/rootworkorder and completed download used'),('READ-05','guessed local q.P source paths absent','Read actual remote inheritance chain, found original spinroot locks'),('READ-06','Pythonzip expression SyntaxError unmatched parenthesis before IO','Independent corrected read only'),('READ-07','prepare_g3_learning_scope_once.py absent in L','Actual stage_g3_reviewed_once.py read; no oldstage execute'),('READ-08','KeyError zipmember mod4_directional_spin.py absent','Actual directional_spin_runtime.py now extracted read only')]
save('READER_LOOKUP_ERRORS.json',dict(epoch=time.time(),trial_id='E1-G3-READONLY-LOOKUP-ERRORS-01',items=[dict(id=i,observed=e,correction=c,evidence_level='original tool output retained in this task; occurrence epoch not reconstructed') for i,e,c in errors],all_read_only_no_plant_or_queue_or_budget_action=True,production_failure_not_inferred=True))
print(json.dumps(dict(detailed_report=str((R/'SCUT_RETENTION_DETAILED_REVIEW.md').resolve()),source_pin=pin,anchors=len(anchors),actual127=summary)))
