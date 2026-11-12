"""Summarize actual Rough-v1 fixed-weight results; retain separate task denominators."""
from pathlib import Path
import json
T=Path(__file__).resolve().parent;E=T/'evidence'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def total(rows,key):return sum(r.get(key,0) or 0 for r in rows)
complete=read(E/('EVALUATIONS_COMPLETE.json' if (E/'EVALUATIONS_COMPLETE.json').exists() else 'EVALUATIONS_PARTIAL.json'));results={name:read(E/(name+'_RESULT.json')) for name in complete['evaluations']}
flat=results['paired_flat_unified_r1'];variants=('nominal0','Step7_all_remaining_DR');models=[]
def crossing(rows):
 samples=total(rows,'post_cross_eligible_samples')
 wide={f:dict(approach_crossed=sum(sum(r['per_env_crossed'][:5]) for r in rows if r['family']==f),approach_requested=10,departure_crossed=sum(sum(r['per_env_crossed'][5:]) for r in rows if r['family']==f),departure_requested=10) for f in ('low_speed_stair_for_rm','high_speed_stair_for_rm') if any(r['family']==f for r in rows)}
 return dict(wide_steps=wide,crossed=total(rows,'crossed_count'),requested=total(rows,'requested'),first_episode_failures=total(rows,'first_episode_terminal_failures'),recovered_after_cross=total(rows,'post_cross_recovered_count'),post_cross_MAE=sum((r['post_cross_forward_MAE'] or 0)*r['post_cross_eligible_samples'] for r in rows)/samples if samples else None,family_rows=rows)
def gyro(rows):
 n=sum(r['gyro_metrics']['prepush_first_episode_samples'] for r in rows)
 return dict(first_episode_survived6s=sum(r['gyro_metrics']['first_episode_survived6s'] for r in rows),requested=total(rows,'requested'),first_episode_wz_MAE=sum((r['gyro_metrics']['prepush_first_episode_wz_MAE'] or 0)*r['gyro_metrics']['prepush_first_episode_samples'] for r in rows)/n if n else None,aligned_wz_mean=sum((r['gyro_metrics']['prepush_first_episode_wz_mean'] or 0)*(1 if r['command'][1]>0 else -1)*r['gyro_metrics']['prepush_first_episode_samples'] for r in rows)/n if n else None,family_rows=rows)
for model,sha in flat['input_sha256'].items():
 row=dict(model=model,sha256=sha,conditions={})
 for variant in variants:
  def rows(name):return [r for r in results[name]['rows'] if r['model']==model and r['variant']==variant]
  rr=rows('paired_flat_unified_r1');formal=[r for r in rr if r.get('passed') is not None]
  d=dict(flat_original_passed=total(formal,'passed'),flat_original_requested=total(formal,'requested'),flat_formal_resets=total(formal,'resets'),flat_task_rows=[{k:r.get(k) for k in ('task','mean','passed','requested','resets','reasons')} for r in rr],traverse={})
  for level in (0,5,9):d['traverse'][str(level)]=crossing(rows(f'paired_unified_traverse_L{level}_r1'))
  d['fast_L9']=crossing(rows('paired_unified_fast_L9_r1'));d['gyro_L9']=gyro(rows('paired_unified_gyro_L9_r1')) if 'paired_unified_gyro_L9_r1' in results else None
  d['landing']={}
  for level in (0,9):
   name=f'paired_unified_landing_L{level}_r1'
   if name not in results:
    d['landing'][str(level)]=None
    continue
   rr=rows(name);stats={k:sum(r['landing_metrics'][k] for r in rr) for k in ('observed_clearance','first_contact','posture_recovered','command_recovered')}
   d['landing'][str(level)]=dict(requested=total(rr,'requested'),first_episode_failures=total(rr,'first_episode_terminal_failures'),family_rows=rr,**stats)
  d['v0_retention_traverse_L9']=crossing(rows('paired_v0_retention_traverse_L9_r1')) if 'paired_v0_retention_traverse_L9_r1' in results else None;d['v0_retention_gyro_L9']=gyro(rows('paired_v0_retention_gyro_L9_r1')) if 'paired_v0_retention_gyro_L9_r1' in results else None
  row['conditions'][variant]=d
 models.append(row)
checks=[dict(name=name,num_envs=r['num_envs'],physics_dt=r['physics_dt'],action_slot_max_error=r['action_slot_max_error'],motor_envelope_violation_nm=r['motor_envelope_violation_nm'],no_optimizer_constructed=r['no_optimizer_constructed'],numerical_total=sum(x.get('reasons',{}).get('numerical',0) for x in r['rows']),model_sha256=r['input_sha256']) for name,r in results.items()]
(T/'PAIRED_SUMMARY.json').write_text(json.dumps(dict(scope='Same-batch PhysX nominal/fullDR fixed weights. Actual Rough-v0-100m parent, an intermediate assessment candidate and120m. Separate first-episode traversal/gyro/landing and original flat precision; no inferred graduation.',models=models,checks=checks,complete=complete.get('complete',True),pending_evaluations=complete.get('pending_evaluations',[])),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
L=['# Rough-v1 两小时：固定权重实测对照','','当前只收齐5/10组结果。目标机SSH超时；旋转、落地及新模型的Rough-v0保留测量待收齐，不记作0或通过。训练7206.600秒和26份完整PT已在本机核验。','','parent为本轮真实Rough-v0 100m父；候选由全部定时点的MuJoCo筛查选来做进一步比较，不预先称为综合最优。以下成绩全部来自实际同批PhysX。','','## 平地原六项保留','','| 模型 | 名义Flat /60 | 完整DR Flat /60 | 名义vx@2.0 / vx@2.2 |','|---|---:|---:|---:|']
for r in models:
 a=r['conditions']['nominal0'];b=r['conditions'][variants[1]];f={x['task']:x for x in a['flat_task_rows']};L.append(f"| {r['model']} | {a['flat_original_passed']} | {b['flat_original_passed']} | {f['forward_2.0']['mean'][0]:.4f} / {f['forward_2.2']['mean'][0]:.4f} |")
L+=['','## Rough-v1 实际地形穿越','','10类非平地×两方向×10初态，分母200；常规地形±1，高速宽阶/反高浅阶±1.5、落差族±2.0 m/s，遵守本轮按地形指令范围。宽阶每方向5个进阶、5个出阶初态，穿越要求实际高度变化和两轮清障，平平台上走够距离不算过阶。','','| 条件 | 难度 | 模型 | 地形指定速度穿越 /200 | 越障后恢复指令 /200 |','|---|---:|---|---:|---:|']
for var in variants:
 for level in ('0','5','9'):
  for r in models:
   d=r['conditions'][var]['traverse'][level];L.append(f"| {var} | {level} | {r['model']} | {d['crossed']} | {d['recovered_after_cross']} |")
L+=['','## 宽台阶：上行与下行分别计数','','以下为完整DR，每类宽阶各10个接近中央高平台的上行初态、10个离开平台的下行初态；两方向合计。不能用下行成绩替代上行能力。','','| 难度 | 模型 | 低速宽阶上行 /10 | 低速宽阶下行 /10 | 高速宽阶上行 /10 | 高速宽阶下行 /10 |','|---:|---|---:|---:|---:|---:|']
for level in ('0','5','9'):
 for r in models:
  w=r['conditions']['Step7_all_remaining_DR']['traverse'][level]['wide_steps'];a=w['low_speed_stair_for_rm'];b=w['high_speed_stair_for_rm']
  L.append(f"| {level} | {r['model']} | {a['approach_crossed']} | {a['departure_crossed']} | {b['approach_crossed']} | {b['departure_crossed']} |")
L+=['','## 最高档高速穿越与旋转','','高速2.2仅检查9个允许该速度的非平地族（180例）；旋转只检查5个训练角速范围含14.137的非平地族（100例）。宽台阶、指定高速下阶和落差族按参考为直行科目，不用其未训练高速陀螺组合作毕业条件。','','| 条件 | 模型 | ±2.2指令穿越（完成/请求） | 旋转首6秒保持（完成/请求） | 旋转MAE rad/s |','|---|---|---:|---:|---:|']
for var in variants:
 for r in models:
  d=r['conditions'][var];g=d['gyro_L9']
  if g is None:
   L.append(f"| {var} | {r['model']} | {d['fast_L9']['crossed']}/{d['fast_L9']['requested']} | 待收齐 | 待收齐 |")
   continue
  L.append(f"| {var} | {r['model']} | {d['fast_L9']['crossed']}/{d['fast_L9']['requested']} | {g['first_episode_survived6s']}/{g['requested']} | {g['first_episode_wz_MAE']:.4f} |")
L+=['','## 腾空落地','','4个参考允许地形×两方向×10初态，分母80。真正离地、接触、姿态恢复和指令恢复分别计数；后两项要求首次episode内连续保持.5秒，不用重置后的表现补分。','','| 条件 | 难度 | 模型 | 观测离地 /80 | 接触 /80 | 姿态恢复 /80 | 指令恢复 /80 |','|---|---:|---|---:|---:|---:|---:|']
for var in variants:
 for level in ('0','9'):
  for r in models:
   d=r['conditions'][var]['landing'][level]
   if d is None:
    L.append(f"| {var} | {level} | {r['model']} | 待收齐 | 待收齐 | 待收齐 | 待收齐 |")
    continue
   L.append(f"| {var} | {level} | {r['model']} | {d['observed_clearance']} | {d['first_contact']} | {d['posture_recovered']} | {d['command_recovered']} |")
L+=['','## Rough-v0 旧科目保留','','| 条件 | 模型 | 原最高档±1穿越 /160 | 原小陀螺首6秒保持 /160 | 原旋转MAE rad/s |','|---|---|---:|---:|---:|']
for var in variants:
 for r in models:
  d=r['conditions'][var];g=d['v0_retention_gyro_L9']
  if g is None or d['v0_retention_traverse_L9'] is None:
   L.append(f"| {var} | {r['model']} | 待收齐 | 待收齐 | 待收齐 |")
   continue
  L.append(f"| {var} | {r['model']} | {d['v0_retention_traverse_L9']['crossed']} | {g['first_episode_survived6s']} | {g['first_episode_wz_MAE']:.4f} |")
L+=['','## 原始证据与限制','','逐地形/方向结果及第一episode终止原因见PAIRED_SUMMARY.json和evidence/paired_*_RESULT.json；按模型配对的DR、延迟、噪声、外力和推扰原件在INITIAL_DR/trajectory中。每一组实际numerical、动作槽误差、电机包络与是否构建优化器见PAIRED_SUMMARY.checks。没有将少量保护事件改成全程0。','','这是一组固定初态和代表难度的实测，不把训练奖励、纯6秒旋转保持、触地或名义MuJoCo精度合并成全面毕业结论。新科目与旧R1模型的历史分数不作异批直接排名。']
(T/'PAIRED_COMPARISON.md').write_text('\n'.join(L)+'\n',encoding='utf-8');print(json.dumps(dict(models=len(models),evaluations=len(checks),report=str(T/'PAIRED_COMPARISON.md')),ensure_ascii=False))
