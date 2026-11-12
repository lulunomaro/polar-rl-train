from pathlib import Path
import json,time,hashlib,subprocess,sys
R=Path(r'D:\claude2\fangzhen\_mod4v2_src_20261106');T=R/'sources/local/MOD4V3_SCUT_ROUGH_V1_2H_20261112';E=T/'evidence'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
plan=read(T/'EFFECTIVE_RECIPE.json');done=read(E/'TRAINING_COMPLETION.json');paired=read(T/'PAIRED_SUMMARY.json');inventory=read(E/'CHECKPOINT_INVENTORY.json')
models={m['file']:m for m in inventory['models']};cpu_resets=sum(r['resets'] for r in inventory['nominal_MuJoCo_screening'])
checks=paired['checks'];print('actual completed evaluation checks',[(c['name'],c['numerical_total'],c['action_slot_max_error']) for c in checks])
selection=dict(status='PPO complete;5of10 PhysX assessment groups collected; target SSH unavailable',training_parent_model_id='roughv0_100m',training_parent_sha256=plan['parent_sha256'],training_parent_iteration=23665,rough_continuation_baseline='roughv0_100m',rough_continuation_baseline_reason='Retain actual trained Rough-v0 course capabilities; this round has no clear fullDR traversal gain and new high-wide-step ascent remains weak. No return to the initial plant/policy.',experimental_candidate='scutroughv1_105m',experimental_candidate_sha256=models['model_105m.pt']['sha256'],experimental_latest='scutroughv1_120m',experimental_latest_sha256=models['model_120m.pt']['sha256'],promoted=False,original_deployment_package_retained=True,pending_evaluations=read(E/'EVALUATIONS_PARTIAL.json')['pending_evaluations'],next_action='Restore target connection; first collect already-launched gyro job if complete, then finish the four unlaunched frozen-weight checks. Check actual GPU ownership before launching.',automatic_extra_PPO=False,same_recipe_more_time_justified_by_current_evidence=False)
write(T/'NEXT_RECOMMENDATION.json',selection)
report=f'''# 华南虎 Rough-v1 统一跑场两小时：训练完成、验收部分收齐

本轮从用户认可的 **Rough-v0 100m** 完整权重接续，已完成两小时PPO。当前本机已收齐5/10组PhysX对照；目标机SSH超时，旋转、落地及新模型Rough-v0保留测量尚未收齐。未收齐项目不记作0、通过或失败。原实车调试包保留。

## 实际训练与父模型

- 父：Rough-v0 `model_100m.pt`，iteration23665，SHA `{plan['parent_sha256']}`。R1第二轮005m只保留为原基线，没有作为本轮训练父。
- 实际PPO **{done['training_seconds']:.3f}秒**；iteration23665→{done['final_iteration']}，{done['PPO_updates']}次更新，{done['policy_environment_steps']:,}环境策略步。
- 4096环境，LR3e-5 fixed、clip.1、3epochs、rollout24、seed66；完整恢复actor/critic/STD/Adam/RNG，新地形与新物理episode。
- 每300秒完整保存、下载SHA核验、Torch实际读回及CPU回放：24定时点，首次更新和final，共26份完整训练PT、25种字节。120m与final同字节；短探针2份原件另存。
- 末点SHA `{models['model_120m.pt']['sha256']}`；轮内105m筛查候选SHA `{models['model_105m.pt']['sha256']}`。候选是进一步评测用点，没有预先称为全局最优。

## 科目与MOD4适配

保存的SCUT rough_dash参考全部11类地形、10难度行从启动并行：低速宽阶15–35cm、高速宽阶15–40cm、格栅2–6cm、较陡坡比.15–.35、反缓坡、正反浅阶、随机起伏、平地和短落差族。原13列复制到75列，以分散4096克隆；20%平地与20%名义参数独立交叉。各难度行是实际生成的难度桶，不把参数范围上限直接声称为某一次已通过的实际阶高。

当前完整DR、35actor/78critic/6action、2.5ms物理/10msPD/20ms策略、TGS32/4、2mm单env闭链保护、电机包络、−1.5e²与指数速度权重1.2均保持。指令上限2.2m/s；MOD4可行bank空中出生替代参考机器人的腿长逆解，根高按局部地面和可行支撑高度抬升。按允许地形40%条件air reset、3s空中临时命令，内部airborne奖励开启，7个actor模式槽仍为原normal语义。主动跳跃关闭。详细实际指令概率、各地形高度/速度覆盖和reset语义见EFFECTIVE_RECIPE.json及执行源码。

## 已收齐的同批PhysX结果

父=Rough-v0 100m；两新点=本轮105m/120m。下表分母按科目，不合并为统一毕业率。

| 完整DR项目 | 父100m | 新105m | 新120m |
|---|---:|---:|---:|
| 平地原六项 /60 |35|32|34|
| Rough-v1低档穿越 /200 |180|178|178|
| Rough-v1中档穿越 /200 |176|171|171|
| Rough-v1最高档穿越 /200 |170|162|169|
| 最高档允许高速族2.2指令穿越 /180 |162|154|154|

名义平地原六项34→41/40；名义PhysX指令2.2实际1.8207→1.9224/2.0177，欠速有所减小；但完整DR同指令实际2.2245→2.5800/2.6291，超速增大。不能只报名义改善或拿MuJoCo偏速方向替代PhysX。全部24点名义MuJoCo筛查共重置{cpu_resets}次，完整序列见CHECKPOINT_COMPARISON.md。

**宽台阶上行仍是明确短板。** 最高档完整DR里，两类宽阶的父和两新点上行各0/10；下行父均10/10，新105m为8/10、10/10，新120m为9/10、10/10。低档新105m高速宽阶有1/10上行，尚不足以称掌握。不能把下台阶、坡面通过数合并说成已经会爬高台阶。逐地形和上/下行分表见PAIRED_COMPARISON.md。

已收齐5组中，动作槽最大误差均0、电机包络违反均0、未构建优化器；实际numerical总计{sum(c['numerical_total'] for c in checks)}。这些数字只覆盖已收齐测试。

## 训练保护、短探针和中断

主训练原始结束episode255176；closure29494、numerical39、mimic10、closure_catastrophic1、timeout169618、terrain_boundary132178。原因可重叠，不能加总；按原单env保护重置，没有改成全程0或放宽阈值。

正式训练前4096短探针完成一更新9.434秒，numerical0；只作为启动验证，不作为本轮父或两小时预算。目标机15:01重启后原卷未挂载，恢复原已知UUID挂载后资产/父/53个上传文件读回校验通过。训练期间执行源码、物理、奖励、DR及接口没有热改。

本地PT检查器最初沿用9族统计假设，在实际11族PT处断言失败；已修正本轮读回器并重新读取相同字节，原检查器、错误输出和最初元数据原件均保留，不涉及远端训练。

训练已安全退出；后续第6组gyro最后收集到step960、numerical0，但未收齐RESULT/SAFE_CLOSED。随后SSH连续连接超时，finish_round读者退出。目标机当前评测进程/GPU状态未知，不能称全部资源已释放或剩余评测完成。已收齐的5组含原始RESULT/INITIAL_DR/NPZ/日志；未收齐路径和最后观察见evidence/ASSESSMENT_INTERRUPTED.json。后续先核对原gyro进程，避免重复启动或覆盖原证据。

53个本地执行文件仍逐一匹配开训前已在远端读回验证的SHA，见EXECUTED_SOURCE_LOCAL_VERIFIED.json；终端远端复读及主日志补收因连接中断待完成。

## 模型选择和下一步

Rough线保留Rough-v0 100m作为已测接续基座；本轮105m/120m完整实验权重均保留。当前没有证据支持把本轮末点自动晋升为综合最成熟模型，也不因本轮结果回到最初模型。原R1实车调试包继续保留原身份。

先恢复目标机连接并收齐剩余五组固定权重结果，再决定本轮点是否值得作为Rough线接续。已知宽阶上行未取得稳定突破，继续原配方追加时长目前缺乏收益证据；没有自动开下一轮PPO。

[实际配方](EFFECTIVE_RECIPE.json) · [同批结果](PAIRED_COMPARISON.md) · [所有保存点](CHECKPOINT_COMPARISON.md) · [模型选择](DECISION.md)。Git最终归档/推送状态另见SYNC_REPORT；本报告写入时待最终提交。
'''
(T/'FINAL_REPORT.md').write_text(report,encoding='utf-8')
(T/'REPORT.md').write_text(report,encoding='utf-8')
(T/'DECISION.md').write_text('''# Rough-v1本轮模型选择

训练父始终是Rough-v0 100m/iter23665/SHA0010283962…，该模型的粗糙地形能力继续保留。本轮完整PPO7206.600秒、26份训练PT已完成并核验。

本机已收齐5/10组PhysX：105m/120m名义Flat改善，但完整DR Flat/地形穿越未体现综合收益，最高档宽台阶上行均0/10；完整DR前进2.2指令的新120m均值2.6291，过冲增大。105m只是在MuJoCo筛查后选出的正式比较候选。没有把任何末点自动视为最优。

Rough线当前保留真实父Rough-v0 100m；本轮105m和120m为完整实验候选，等待补齐gyro、landing、Rough-v0保留测试。原R1实车包保留，不回退重训最初权重，不自动启动下一轮。

目标机SSH超时，gyro近末段结果和其余四组待收齐；缺失项目不是0分、失败或通过。执行前需核原评测进程与GPU占用；原失败读者日志保留。详见FINAL_REPORT与NEXT_RECOMMENDATION.json。
''',encoding='utf-8')
(T/'README.md').write_text(f'''# 华南虎 Rough-v1：统一跑场两小时

**PPO已完成{done['training_seconds']:.3f}秒，26份完整训练PT已核验；PhysX收齐5/10组，其余因目标机SSH超时待收齐。** 本轮实际父为Rough-v0 100m，未回退R1。原实车调试包保留，暂未晋升新模型。

| 用途 | 文件 | iteration | SHA256 |
|---|---|---:|---|
| 本轮真实父、Rough线保留基座 | [Rough-v0 100m](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/weights/model_100m.pt) |23665|`{plan['parent_sha256']}`|
| 本轮正式比较候选 | [105m完整PPO](weights/model_105m.pt) |{models['model_105m.pt']['iteration']}|`{models['model_105m.pt']['sha256']}`|
| 本轮末点、实验权重 | [120m完整PPO](weights/model_120m.pt) |24482|`{models['model_120m.pt']['sha256']}`|

11类地形/10级统一训练，不拆短课；保持完整DR、20%名义与20%平地独立交叉、35/78/6、2.5/10/20ms、TGS32/4、2mm单env保护、−1.5e²/指数1.2和2.2m/s上限。LR3e-5 fixed、clip.1、3epochs、rollout24、seed66。内部腾空落地开启，主动跳跃关闭。

每五分钟完整保存/下载SHA核验/实际Torch读回/名义MuJoCo筛查；24定时点、首次和final共26份PT，25种字节。全部PT本体随阶段Git归档，完整SHA/bytes/iteration见evidence/MODEL_ARCHIVE_INDEX.json。短探针原件另存，原始恢复训练盘、读回器修复和SSH读者错误均保留。

完整DR最高档穿越父/105m/120m=170/162/169（各200）；高速162/154/154（各180）；宽阶上行仍未掌握。原始逐地形结果在同批报告中，不把旋转/落地未收齐项写成通过。

[最终报告](FINAL_REPORT.md) · [模型选择](DECISION.md) · [同批结果](PAIRED_COMPARISON.md) · [全部保存点](CHECKPOINT_COMPARISON.md) · [实际配方](EFFECTIVE_RECIPE.json) · [复现](TRAINING_RECIPE.md)。

[前一轮Rough-v0行走与小陀螺分项报告](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/COURSE_COMPLETION_REPORT.md)。Git同步回执另见SYNC_REPORT；当前无新PPO。
''',encoding='utf-8')
write(E/'GPU_STATUS_UNAVAILABLE.json',dict(epoch=time.time(),training_scene_closed=True,last_known_evaluation='paired_unified_gyro_L9_r1',current_remote_gpu_status='unknown due SSH timeout',all_evaluations_closed_verified=False))
# The local frozen PT/recipe catalog is complete even when target connectivity is down.
subprocess.run([str(R.parent/'.venv/Scripts/python.exe'),'-X','utf8',str(T/'update_registry.py'),'--final'],check=True)
C=R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111';reg=read(C/'MODEL_REGISTRY.json')
status='Unified Rough-v1 PPO7206.600s complete;26fullPT;5of10PhysX groups collected; targetSSH unavailable; no promotion'
for stage in reg['stages']:
 if stage['id']=='scut_rough_v1_2h':stage['status']=status;stage['assessment_complete']=False;stage['completed_assessment_groups']=5;stage['planned_assessment_groups']=10
reg.update(as_of_date='2026-11-12',current_training_status=status,current_round_parent_model_id='roughv0_100m',current_rough_continuation_model_id='roughv0_100m',current_round_selected_model_id=None,current_assessment_status='pending target reconnection;5groups outstanding');write(C/'MODEL_REGISTRY.json',reg)
summary='''## 2026-11-12：统一Rough-v1两小时PPO完成，验收5/10

从用户选择的Rough-v0 100m/iter23665/SHA0010283962…接续，实际PPO7206.600s、817更新、80,314,368环境策略步；24定时点加首次/final，共26完整PT、25种字节。11族/10级统一训练及完整DR、原物理/接口/奖励保留。总模型索引30阶段、190个完整训练PT记录。

已收齐同批PhysX5组：完整DR最高档穿越父/105m/120m=170/162/169（各200），高速162/154/154（各180）；宽阶上行未稳定掌握。名义平地34/41/40，完整DR35/32/34（各60）。Rough线保留原Rough-v0 100m，本轮105m/120m实验候选，未晋升，也未回退R1重训。原实车包保留。

目标机SSH超时，第6组gyro末段和后续落地/原Rough-v0保留测量待收齐；训练及全部PT已在本机完整核验。不能称验收全部完成或GPU已确认释放。未自动开下一轮。

'''
p=R/'README.md';s=p.read_text(encoding='utf-8');start=s.index('## 2026-11-12：统一华南虎 Rough-v1 两小时正在训练');end=s.index('## 最新训练记录：2026-11-12统一Rough-v0两小时',start);s=s[:start]+summary+'[本轮最终报告/全PT](sources/local/MOD4V3_SCUT_ROUGH_V1_2H_20261112/README.md) · [Rough-v0逐地形完成报告](sources/local/MOD4V3_SCUT_ROUGH_V0_2H_20261112/COURSE_COMPLETION_REPORT.md)。以下旧轮次按各自时刻保留。\n\n'+s[end:];p.write_text(s,encoding='utf-8')
for rel in ('docs/ROUGH_CURRICULUM_README_20261111.md','docs/DR_TRAINING_INDEX_20261111.md','docs/DR_TRAINING_RESUME_20261111.md'):
 p=R/rel;p.write_text(p.read_text(encoding='utf-8')+'\n\n'+summary+'[配方/报告/全PT入口](../sources/local/MOD4V3_SCUT_ROUGH_V1_2H_20261112/README.md)。\n',encoding='utf-8')
p=C/'README.md';p.write_text(p.read_text(encoding='utf-8')+'\n\n'+summary+'[本轮记录](../MOD4V3_SCUT_ROUGH_V1_2H_20261112/README.md)。\n',encoding='utf-8')
# Make the final archive receipt explicitly describe the five collected assessment groups.
p=T/'sync_archive.py';s=p.read_text(encoding='utf-8-sig').replace('和正式PhysX评测已通过7897代理推送','和已收齐5组正式PhysX评测已通过7897代理推送').replace('- 实际训练父为Rough-v0 100m/iter23665/SHA0010283962…；未回退R1。','- 实际训练父为Rough-v0 100m/iter23665/SHA0010283962…；未回退R1。目标机SSH超时导致其余5组评测待收齐，不能称验收完成或GPU已释放。');p.write_text(s,encoding='utf-8')
print('Final training and partial assessment reports ready; registry',len(reg['stages']),len(reg['models']))
