from pathlib import Path
import json,datetime
R=Path(r'D:\claude2\fangzhen\_mod4v2_src_20261106');T=R/'sources/local/MOD4V3_SCUT_ROUGH_V0_2H_20261112';E=T/'evidence';CAT=R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
s=read(T/'PAIRED_SUMMARY.json');train=read(E/'TRAINING_COMPLETION.json');plan=read(T/'EFFECTIVE_RECIPE.json')
by={x['model']:x for x in s['models']};parent=plan['parent_sha256'];candidate=by['roughv0_100m']['sha256'];last=by['roughv0_120m']['sha256']
# Publish recovery/continuous speed error alongside the2.2-command crossing count.
for row in s['models']:
 for condition in row['conditions'].values():
  fast=condition['fast_L9'];rr=fast['family_rows'];samples=sum(r['post_cross_eligible_samples'] for r in rr)
  fast.update(post_cross_recovered_count=sum(r['post_cross_recovered_count'] for r in rr),post_cross_eligible_samples=samples,post_cross_forward_MAE=sum((r['post_cross_forward_MAE'] or 0)*r['post_cross_eligible_samples'] for r in rr)/samples if samples else None)
put(T/'PAIRED_SUMMARY.json',s)
with (T/'PAIRED_COMPARISON.md').open('a',encoding='utf-8') as f:
 f.write('\n高速表表示±2.2m/s指令下的实际穿越，不代表全过程实速达到2.2。越障后有效窗口MAE与恢复到±0.2m/s并持续0.5秒的数量另见PAIRED_SUMMARY；完整DR的父/100m/120m越障后MAE分别0.7494/0.8478/0.7300m/s。\n')
next_data=dict(status='completed_not_promoted',selected_continuation_model_id='r1round2_005m',parent_sha256=parent,parent_iteration=22959,parent_git_path='sources/local/MOD4V3_ROUGH_R1_ROUND2_20261111/weights/model_005m.pt',retained_experimental_model_id='roughv0_100m',retained_experimental_sha256=candidate,retained_experimental_iteration=23665,final_model_id='roughv0_120m',final_sha256=last,promote_new_checkpoint=False,completed_training_PPO_seconds=train['training_seconds'],frozen_weight_assessments=8,next_training_started=False,automatic_unchanged_continuation=False,route='User preference remains one combined SCUT course; no new R0/R1/R2 admission split is introduced.',reason='Tested100m/120m show small high-speed-crossing/first6s gyro-retention gains that do not cover nominal Flat tracking loss and worse rough yaw tracking. Retain existing R1 parent for comprehensive continuation and the existing real-robot debugging package. No claim that every other timed checkpoint has had full PhysX assessment.')
put(T/'NEXT_RECOMMENDATION.json',next_data)
decision=f'''# 两小时统一Rough-v0：模型选择

2026-11-12。综合接续继续选 **r1round2_005m**（iter22959，SHA `{parent}`）。本轮100m/120m不晋升，原Step6/Step7冻结及既有实车调试包保持原身份。

- **roughv0_100m**：iter23665，SHA `{candidate}`，保留作本轮已做PhysX细评的实验候选。名义MuJoCo旧六项60/60只是筛选结果；同批PhysX名义/完整DR为36/60、35/60，父为58/60、42/60。
- **roughv0_120m / final**：iter23807，SHA `{last}`，两文件同字节；PhysX名义/完整DR30/60、38/60，保留归档。
- 完整DR level9、±1m/s首次穿越：父/100m/120m为134/133/131（各160）；±2.2指令穿越145/148/144。100m多3个高速穿越样本，但越障后MAE0.8478m/s高于父0.7494。
- 完整DR level9旋转首次6秒未结束episode：153/158/156（各160）；角速度MAE1.7066/1.8705/1.8548rad/s。首次6秒保留有所增加，转速精度未改善，不能写成旋转全指标提高。

这些小幅收益不足以支持替换综合父模型。该选择依据原有任务统计和连续误差，不新增“全部100%”毕业线，也不要求回到拆分课程。未做单因素归因，不能断言某一个奖励项或DR实现是根因。本轮结果不支持自动延长同一配方。

全部26份完整训练PT均保留，其他保存点完成了固定名义MuJoCo检查；完整PhysX三模型对照仅覆盖父、100m、120m，不能把结论扩大为每个中间点都更差。

[同批原表](PAIRED_COMPARISON.md) · [全部保存点](CHECKPOINT_COMPARISON.md) · [实际配方](EFFECTIVE_RECIPE.json) · [精确接续记录](NEXT_RECOMMENDATION.json)。
'''
(T/'DECISION.md').write_text(decision,encoding='utf-8')
report=f'''# 统一SCUT Rough-v0两小时：最终报告

本轮已完成，未晋升新模型。综合接续/原实车调试包继续使用R1第二轮005m，SHA `{parent}`；100m保留为已细评的实验候选。

## 实际训练

用户授权统一训练华南虎Rough-v0两小时，不再拆R0/R1/R2短课。使用保存的rough_rotation_stair运行（2026-07-30_09-16-27）全部9地形族、10级难度，从启动一起采样；顶层curriculum为空、可选height-offset curriculum关闭，没有按成功率分段准入。为4096克隆分散出生点，将参考14列复制为70列；保留20%平地与20%名义参数的独立交叉分配。

实际PPO **{train['training_seconds']:.3f}秒**，iter22959→23807，共848更新、83,361,792环境策略步。4096env，LR3e-5 fixed、clip0.1、3epochs、rollout24、seed66。每300秒完整保存/下载核验/实际读回；24个定时点，加首次更新和final共26份完整PT、25种不同字节。final与120m同字节；另保留短探针两份同字节PT原件。

MOD4适配保留：35actor/78critic/6action，机身坐标指令，当前完整DR、2.2m/s上限，−1.5e²和指数速度权重1.2，2.5ms物理/10msPD/20ms策略，TGS32/4、2mm单env闭链保护与电机包络。MOD4无云台，没有新增云台观测。Rough-v0的air reset/airborne关闭。SCUT15%低档gyro、15%高档gyro、30%高速组合与普通/航向/站立指令统一混合，地形高度覆盖按保存参考；保留原ground-reset恢复段。

本轮是SCUT科目的MOD4适配，不把硬件、完整DR和上述已接受奖励改成参考机器人参数。完整实际配方见EFFECTIVE_RECIPE.json；原PLAN两个继承描述字段仍写rough_r2/air overlay，按启动原件保留。CLI/STARTUP始终是rough_scut_v0、air_reset_fraction0、airborneFalse；描述订正在实际配方中列明，未热改训练。

## 保护与执行证据

主训练153,821个结束episode；原始保护计数closure19,851、numerical34、mimic10、closure_catastrophic3，terrain_boundary65,341。原因可重叠，不能相加推算全部终止类型，也不能称训练全程numerical0。均按既有单env保护处理，没有放宽闭链或因单峰停整批。正常FINAL与SAFE_CLOSED齐全。

8项正式固定权重PhysX对照全部完成：dt0.0025、raw-action槽误差0、电机包络违反0、numerical0、没有漏接触容量警告、无PPO优化器更新。启动原生机械限位/质量/零隐式主动驱动检查留在STARTUP；轮末3个资产文件pin校核均匹配，根USD SHA e057969b136fd75613bb8d77985d43d043f54faae62dc060afb718ebabbe1c1c。49份训练源/参数及3份评测源/模型清单从目标机读回核SHA，52份一致。

## 同批结果与解释

| 指标 | R1父 | 100m | 120m |
|---|---:|---:|---:|
| PhysX名义Flat原六项 /60 |58|36|30|
| PhysX完整DR Flat原六项 /60 |42|35|38|
| 完整DR level9 ±1m/s穿越 /160 |134|133|131|
| 完整DR level9 ±2.2指令穿越 /160 |145|148|144|
| 完整DR level9旋转首次6秒未结束 /160 |153|158|156|
| 完整DR level9旋转MAE rad/s |1.7066|1.8705|1.8548|

名义PhysX指令2.0/2.2的父实际1.9054/2.1643，100m为1.7242/1.8077，120m为1.7282/1.8484，出现欠速。名义MuJoCo100m旧六项60/60、120m20/60；该引擎中120m前进实际2.1879/2.3958，属于超速。不能把MuJoCo筛选数当成PhysX/fullDR通过，也不能把两个引擎偏速方向混成一个结论。

低档完整DR穿越155→156/157，小幅改善；中档147→144/143；最高代表档134→133/131。高速指令穿越100m多3例，旋转首段保留多5例，但角速误差与平地精度没有相应收益。综合继续保留父；本轮100m为实验候选、120m仅归档，未替换原冻结或实车包。不是新增100%毕业要求。只评测了代表行0/5/9和行9高速，不声称全部10行/全部指令组合毕业；旋转MAE基于有效首次episode窗口，必须连同6秒保留数阅读。

## 原始失败与复现

首次4096短探针在初始化失败：同步漏了既有remaining_reset_bank.json，未产生PPO更新；ERROR/SAFE_CLOSED/原上传清单保留。补齐数据后独立r2短探针完成一更新9.950秒，numeric1；主训练仍从原R1父启动，没有把探针点冒充父。两次本地读者错误（GBK控制台打印、嵌套引号解析）在LOCAL_READER_ERRORS记录，均未改训练进程。

模型本体在weights/，全部SHA/iteration/bytes见evidence/MODEL_ARCHIVE_INDEX.json与CHECKPOINT_INVENTORY；训练完整源、launch/monitor、正式评测代码与原始RESULT/INITIAL_DR/NPZ/日志均保留。后续完整PPO接续仍是新物理episode；原R1四级地形状态仅保留父来源，不能重标成统一十级统计。

[配方](TRAINING_RECIPE.md) · [同批比较](PAIRED_COMPARISON.md) · [全部保存点](CHECKPOINT_COMPARISON.md) · [选择](DECISION.md) · [Git同步回执](SYNC_REPORT.md)。本报告写入时最终Git提交/推送待执行，完成状态另见同步回执；未启动下一轮。
'''
(T/'FINAL_REPORT.md').write_text(report,encoding='utf-8');(T/'REPORT.md').write_text(report,encoding='utf-8')
readme=f'''# SCUT Rough-v0统一科目：两小时已完成（2026-11-12）

用户授权的统一科目PPO已完成 **{train['training_seconds']:.3f}秒**，每5分钟完整保存检查，26份完整训练PT本体/25种不同字节均保留。8组正式PhysX同批对照已完成，当前没有训练或验收在运行。

**综合接续继续使用R1第二轮005m，未晋升本轮100m/120m。** 100m是本轮已做PhysX细评的实验候选，不能只凭名义MuJoCo60/60把它当成综合最优；具体差异见[模型选择](DECISION.md)。原Step6/Step7冻结、原实车调试包保持原身份。

| 用途 | 文件 | iteration | SHA256 |
|---|---|---:|---|
| 综合继续父 | [R1第二轮005m](../MOD4V3_ROUGH_R1_ROUND2_20261111/weights/model_005m.pt) |22959|`{parent}`|
| 本轮实验候选，未晋升 | [100m完整PPO](weights/model_100m.pt) |23665|`{candidate}`|
| 末点，未晋升 | [120m完整PPO](weights/model_120m.pt) |23807|`{last}`|

统一课程：保存的SCUT rough_rotation_stair全部9地形族、10难度行并行，包含浅栅格/坡面/正反小阶与中阶/随机起伏/平地，同时训练行进、小陀螺与组合指令；没有R0/R1分段准入或能力毕业线。14列扩成70列分散4096出生点。保留当前完整DR、20%名义/20%平地独立交叉、2.2m/s上限、35/78/6、2.5/10/20ms、TGS32/4、2mm单env保护、−1.5e²和指数1.2；无云台/air reset/airborne新增。

- [实际完整配方](EFFECTIVE_RECIPE.json)、[训练方法与入口](TRAINING_RECIPE.md)、[原始启动PLAN](PLAN.json)；PLAN继承描述字段的订正在实际配方中，CLI/STARTUP反映实际运行。
- [最终报告](FINAL_REPORT.md)、[PhysX同批原表](PAIRED_COMPARISON.md)、[全部24个保存点MuJoCo回放](CHECKPOINT_COMPARISON.md)。两引擎数据分开，首次穿越、首段旋转和Flat窗口统计分开。
- [全部26个完整PT索引](evidence/MODEL_ARCHIVE_INDEX.json)、[实际保存时刻/回放明细](evidence/CHECKPOINT_INVENTORY.json)、[目标机源校核](evidence/EXECUTED_SOURCE_VERIFIED.json)。不是只保存路径或LFS指针。
- [精确接续记录](NEXT_RECOMMENDATION.json)、[同步回执](SYNC_REPORT.md)。新预算或下一课程没有自动启动。

复现本轮以本目录support/和launch.py为入口：4096env/LR3e-5 fixed/clip0.1/epochs3/rollout24/seed66，父为上述R1点，--kind train --seconds7200。完整参数及目标机Python/package/support路径见实际配方。独立新试验使用新job名和独立记录目录；显式--checkpoint可选已保存PT，恢复同4096env的统一十级状态时需保留本目录环境实现。模型没有实时求解器状态，物理episode重新开始。
'''
(T/'README.md').write_text(readme,encoding='utf-8')
with (T/'TRAINING_RECIPE.md').open('a',encoding='utf-8') as f:
 f.write(f'\n\n## 已完成与后续定位\n\n实际{train["training_seconds"]:.3f}秒/848更新；26份完整PT/25种字节，全部PPO/STD/Adam/RNG/DR/9×10状态真实读回。最终选择见DECISION，综合接续R1父，本轮100m/120m未晋升。此配方冻结用于复现，不自动开启下一预算。原始启动PLAN不改；EFFECTIVE_RECIPE整理实际CLI与STARTUP。后续复制源码/配方建独立试验，再显式指定parent/checkpoint；同env数可恢复完整十级状态，新物理episode。\n')
train['initial_assessment_status']=train['assessment_status'];train['assessment_status']='completed8 frozen-weight comparisons; no new model promoted; selected R1 parent'
put(E/'TRAINING_COMPLETION.json',train)
reg=read(CAT/'MODEL_REGISTRY.json');stage=next(x for x in reg['stages'] if x['id']=='scut_rough_v0_2h')
stage.update(status='7206.137s PPO and8 paired assessments completed; tested100m/120m not promoted; comprehensive continuation r1round2_005m',selected_continuation_model_id='r1round2_005m',retained_experimental_model_id='roughv0_100m',decision_file=(T/'DECISION.md').relative_to(R).as_posix())
for row in reg['models']:
 if row['id']=='roughv0_100m':row['role']='Tested experimental candidate selected by nominal MuJoCo screen; not promoted after paired PhysX comparison'
 elif row['id'] in ('roughv0_120m','roughv0_final'):row['role']='Terminal archived checkpoint; not comprehensive best; not promoted'
reg.update(current_training_status=stage['status'],latest_scut_rough_v0_experimental_model_id='roughv0_100m',latest_scut_rough_v0_decision_file=stage['decision_file'],selected_comprehensive_continuation_model_id='r1round2_005m')
put(CAT/'MODEL_REGISTRY.json',reg)
# Update the stage-local index with the same final roles.
index=read(E/'MODEL_ARCHIVE_INDEX.json');current={m['id']:m for m in reg['models']}
index['models']=[current[m['id']] for m in index['models']];index['selected_continuation_model_id']='r1round2_005m';index['new_checkpoint_promoted']=False;put(E/'MODEL_ARCHIVE_INDEX.json',index)
append='''\n\n## 2026-11-12：统一SCUT Rough-v0两小时已完成\n\n按用户新指令，统一全部9地形族/10难度行和行进/小陀螺/组合指令，一次连续PPO7206.137秒，848更新；每5分钟保存，26份完整训练PT/25种不同字节，8组同批固定权重PhysX对照全部完成。完整DR最高代表档±1m/s穿越：父/100m/120m为134/133/131（各160），±2.2指令为145/148/144；旋转角速MAE为1.7066/1.8705/1.8548rad/s；PhysX名义Flat58/36/30（各60）。综合继续R1第二轮005m/iter22959/0dcc15f5…，本轮100m仅实验候选、120m未晋升。原冻结/实车包未替换，没有自动下一轮，也未重新引入拆分课准入。\n\n[最终报告]({prefix}sources/local/MOD4V3_SCUT_ROUGH_V0_2H_20261112/FINAL_REPORT.md) · [配方/全PT入口]({prefix}sources/local/MOD4V3_SCUT_ROUGH_V0_2H_20261112/README.md)。本轮当前总索引29阶段、164个完整训练PT记录；短探针原件另保留。\n'''
for rel in ('docs/ROUGH_CURRICULUM_README_20261111.md','docs/DR_TRAINING_INDEX_20261111.md','docs/DR_TRAINING_RESUME_20261111.md'):
 p=R/rel
 with p.open('a',encoding='utf-8') as f:f.write(append.format(prefix='../'))
for rel in ('README.md','MODELS.md'):
 p=CAT/rel
 with p.open('a',encoding='utf-8') as f:f.write('\n\n统一SCUT Rough-v0两小时与8组验收已完成；本轮26份完整PT均归档，综合接续保留r1round2_005m，100m/120m未晋升。[本轮模型选择](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/DECISION.md)。当前29阶段/164完整训练PT记录。\n')
p=R/'README.md';old=p.read_text(encoding='utf-8');brief='''\n## 最新训练记录：2026-11-12统一Rough-v0两小时\n\n7206.137秒PPO与8组PhysX对照已完成，26份完整PT本体保存；综合接续仍选R1第二轮005m，新100m/120m未晋升。见[当前报告与全PT入口](sources/local/MOD4V3_SCUT_ROUGH_V0_2H_20261112/README.md)，当前无训练在运行。原R0～R4表保留为历史规划，本轮按用户统一科目新指令执行。\n'''
cut=old.find('\n')+1;p.write_text(old[:cut]+brief+old[cut:]+append.format(prefix=''),encoding='utf-8')
(T/'SYNC_REPORT.md').write_text('# Git同步记录\n\n启动记录已通过7897代理推送并核对，见evidence/START_GIT_RECEIPT.json。当前最终完整PT/源码/评测归档准备提交；最终推送结果在完成后追加。\n',encoding='utf-8')
print(json.dumps(dict(selected_continuation='r1round2_005m',new_promoted=False,stage_count=len(reg['stages']),model_count=len(reg['models']),formal_assessments=len(s['checks']),report=str(T/'FINAL_REPORT.md')),ensure_ascii=False))
