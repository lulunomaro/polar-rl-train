from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,time,hashlib,shutil
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence';p=json.loads((E/'LATEST_PROGRESS.json').read_text(encoding='utf8'));recipe=json.loads((T/'PLAN.json').read_text())
local=json.loads((E/'local_stair_replay/RESULT.json').read_text());flat=json.loads((E/'ALIGNED_FLAT_EVAL.json').read_text())
flats=[]
for r in flat['replays']:
 groups={}
 for c in r['cases']:groups.setdefault((c['cmd_vx'],c['cmd_wz'],c['cmd_height']),[]).append(c)
 for command,cs in groups.items():
  flats.append(dict(model=r['model'],command=list(command),vx=sum(c['vx_mean'] for c in cs)/len(cs),wz=sum(c['wz_mean'] for c in cs)/len(cs),height=sum(c['height_mean'] for c in cs)/len(cs),resets=sum(c['reset_count'] for c in cs),seeds=len(cs)))
stairs=[{k:r[k] for k in ('model','direction','height','speed','success','resets','peak_x')}|dict(simulated_seconds=r['trajectory'][-1]['t']) for r in local['cases']]
weights=[]
for f in sorted((T/'weights').glob('*.pt')):
 d=json.loads((E/'training_round'/(f.stem+'_FULL_PT.json')).read_text());weights.append({k:d[k] for k in ('bytes','sha256','iteration','full_ppo_rng_present','all_policy_critic_optimizer_tensors_finite')}|dict(path='weights/'+f.name))
counts=[]
for g in p['terrain']['stair_lift']['counts_DR_then_nominal']:counts.append([sum(row[k] for family in g for row in family) for k in range(4)])
observed=datetime.now(timezone(timedelta(hours=8))).isoformat();last=datetime.fromtimestamp(p['epoch'],timezone(timedelta(hours=8))).isoformat()
result=dict(observed_at=observed,status='partial_remote_connection_lost',authorized_PPO_limit_seconds=1200,last_confirmed_PPO_seconds=p['training_elapsed_seconds'],last_confirmed_iteration=p['iteration'],last_confirmed_time=last,later_remote_state='unknown;15m/20m/final and SAFE_CLOSED pending',parent_sha256=recipe['parent_sha256'],weights=weights,flat_nominal=flats,stairs_nominal=stairs,training_stair_counts_DR_then_nominal=counts,done_totals=p['done_totals'],native_fullDR_evaluation='not launched because SSH unreachable',model_selection='keep original7cc1 user-named snapshot; no new promotion',no_new_training_window=True)
(E/'PARTIAL_RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(E/'PROVENANCE_CLARIFICATION.json').write_text(json.dumps(dict(actual_parent=recipe['parent'],actual_parent_sha256=recipe['parent_sha256'],actual_parent_iteration=24482,actual_parent_stage='selected Rough-v1 120m',verified_by='RESTORE.json and exact SHA before launch',historical_fields=['original_parent','original_parent_sha256','selected_parent_reason'],explanation='The copied selected_parent_reason describes the earlier Rough-v0-to-Rough-v1 choice. It does not identify this20m trial parent. Raw launched recipe preserved; use actual parent/SHA and restore receipt.'),indent=2),encoding='utf8')
md=f'''# 台阶抬高底盘20分钟试验：已确认10分36秒，远端末段待收

记录时间：{observed}。用户授权从“11月12日最牛逼的模型”接续单个1200秒PPO窗口，每300秒完整检查点；没有启动额外训练窗。

父模型是Rough-v1 120m/iter24482/SHA `{recipe['parent_sha256']}`，实际完整恢复actor、critic、STD、Adam及RNG。PLAN内早期selected_parent_reason是继承的历史描述；实际身份以parent、SHA与RESTORE为准，见PROVENANCE_CLARIFICATION。

修改：两类宽台阶的50%重置从外侧平地出发，先将高度0.28m缓升至0.365～0.40m，3秒后给1.5～2.2m/s前进；按相对地面高度符合程度奖励新的向内进展，每级真正上升一次0.5。保留完整DR、其余地形和指令、−1.5e²与指数1.2、LR3e-5/clip0.1/3epochs、2.5/10/20ms、TGS32/4、35/78/6与2mm单环境保护。

## 已完成与未确认

最后确认时间{last}，实际PPO {p['training_elapsed_seconds']:.3f}秒，iter{p['iteration']}。5m/10m及首次完整PT已取回、SHA及Torch内容核验；共{len(weights)}个PT本体。之后SSH banner错误及TCP22持续超时，尚未拿到15m/20m/final、FINAL及SAFE_CLOSED，不能推定已完成或已停止。原任务内部限制1200秒；未重开训练。完整DR原生台阶父子评测未启动，脚本已备好。

## 同条件本机MuJoCo结果

使用原始r00_c00：两级各16.5cm、平台33cm，每个条件每模型一条确定性回放；2秒缓升高度，3秒后前进。它是配对例子，不是多种DR成功率。

| 模型 | 高度.365/2.2m/s上阶 | 高度.40/2.2m/s上阶 | 高度.28/1m/s上阶 | 高度.28/1m/s下阶 |
|---|---|---|---|---|
'''
for model in ('parent','005m','010m'):
 rows=[r for r in stairs if r['model']==model]
 md+='| '+model+' | '+' | '.join(('成功' if r['success'] else '未通过')+f"，{r['simulated_seconds']:.2f}s，{r['resets']}重置" for r in rows)+' |\n'
md+='''
10m抬高上阶较父例子稍快，但仍是父模型已经能够完成的条件；低高度低速仍停在首级前。没有证据证明上阶难度或fullDR成功率提升。

平地保持测试：同一名义plant、10个扰动种子；实际2.5ms物理/10msPD/20ms策略，动作与传感器固定5ms延迟。原“physical5_sent”是延迟名字，先前将其说成5ms物理步是表述错误；原始输出与显式对齐补测均记录2.5ms，见OBSERVATION_TIMING_CLARIFICATION。所有这些案例均0重置。

| 指令 | 父 | 5m | 10m |
|---|---:|---:|---:|
'''
for command,label,key in [([2.,0.,.28],'前进2.0，实际m/s','vx'),([2.2,0.,.28],'前进2.2，实际m/s','vx'),([-1.5,0.,.28],'倒车−1.5，实际m/s','vx'),([0.,14.137167,.28],'旋转14.137，实际rad/s','wz'),([0.,0.,.2],'低姿.20，实际m','height'),([0.,0.,.4],'高姿.40，实际m','height')]:
 vals=[next(r[key] for r in flats if r['model']==model and r['command']==command) for model in ('parent','005m','010m')]
 md+='| '+label+' | '+' | '.join(f'{x:.4f}' for x in vals)+' |\n'
md+=f'''
前向超速随本轮更新增加，旋转/站姿保持，倒车略有变化。原生PhysX fullDR尚未对照，不将名义MuJoCo结果写成fullDR通过。

## 原训练记录与选择

最后累计重置项：`{json.dumps(p['done_totals'])}`。训练台阶计数[尝试,首级,顶台,终止]，DR `{counts[0]}`、名义 `{counts[1]}`，其难度分布与在途episode不同，不能直接当固定任务通过率；截至最后观测顶台计数0。闭链保护仍为单环境重置，出现超阈峰值不等于放宽阈值或整批训练崩溃。

原用户命名父模型继续保留，本轮5m/10m只作实验备份。目前不据本轮替换最佳模型；20m的完整评价仍待远端取回。高度由原35维接口的高度指令提供，本轮没有加入预见台阶的传感输入。

连接恢复后先只读原job的进度/FINAL/SAFE_CLOSED，收齐原15/20/final完整权重；确认GPU释放后做既有成对原生台阶回放。`monitor_round.py`原进程仍重连收件，避免启动重复监测；不调用remote_ops train，不重复发起PPO。无新训练授权的动作只限原任务取回、冻结评测及归档。

所有源码、配方、原生4096无优化器探针、恢复/启动回执、完整PT、成功/失败回放、连接错误和待办均保留。可变监测流在Git中取观察时刻快照，后续结果需追加新记录。
'''
(T/'REPORT.md').write_text(md,encoding='utf8')
readme=(T/'README.md').read_text(encoding='utf8');marker='\n## 当前结果与完整权重\n'
if marker in readme:readme=readme.split(marker)[0]
readme+=marker+'\n已核实PPO10分36秒，5m/10m与首次完整PT已取回；远端SSH随后失联，15/20/final及完整DR原生对照待收。低阶抬高上阶保留，平地前向超速增加，未替换原命名父模型。详见[实验报告](REPORT.md)、[结构化原始结果](evidence/PARTIAL_RESULT.json)。\n\n'+''.join(f"- [{w['path']}]({w['path']})：iter{w['iteration']}，{w['bytes']}字节，SHA `{w['sha256']}`。\n" for w in weights)
(T/'README.md').write_text(readme,encoding='utf8')
notice='## 2026-11-12 台阶抬高底盘20分钟接续：末段待收\n\n从用户选定Rough-v1 120m/7cc1fc6d…完整接续，保留fullDR和原−1.5e²，只新增台阶抬高/进展引导。已取回5m、10m与首次完整PT；最后确认10分36秒后目标SSH失联，15/20/final与原生fullDR对照待收。本机低阶抬高上阶保持、前向超速增加，原命名模型继续保留。'
for file,link in [('README.md','sources/local/MOD4V3_SCUT_STAIR_LIFT_20M_20261112/REPORT.md'),('docs/DR_TRAINING_INDEX_20261111.md','../sources/local/MOD4V3_SCUT_STAIR_LIFT_20M_20261112/REPORT.md'),('docs/ROUGH_CURRICULUM_README_20261111.md','../sources/local/MOD4V3_SCUT_STAIR_LIFT_20M_20261112/REPORT.md')]:
 f=R/file;t=f.read_text(encoding='utf8');title,rest=t.split('\n',1)
 if notice.split('\n')[0] not in t:f.write_text(title+'\n\n'+notice+'\n\n[实验配方、完整PT、实际结果与待办]('+link+')。\n'+rest,encoding='utf8')
print(json.dumps(dict(status=result['status'],weights=len(weights),flat_rows=len(flats),stair_cases=len(stairs)),ensure_ascii=False))
