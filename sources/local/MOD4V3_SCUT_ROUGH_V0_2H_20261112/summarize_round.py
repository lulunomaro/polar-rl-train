"""Summarize the completed same-batch fixed-weight comparisons without promotion."""
from pathlib import Path
import json
T=Path(__file__).resolve().parent;E=T/'evidence'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def put(name,data):(T/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
complete=read(E/'EVALUATIONS_COMPLETE.json')
flat=read(E/'paired_flat_unified_r1_RESULT.json')
models=list(flat['input_sha256']);variants=['nominal0','Step7_all_remaining_DR'];all_results={name:read(E/(name+'_RESULT.json')) for name in complete['evaluations']}
sumkey=lambda rows,key:sum(r.get(key,0) or 0 for r in rows)
output=[]
for model in models:
 row=dict(model=model,sha256=flat['input_sha256'][model],conditions={})
 for variant in variants:
  plains=[r for r in flat['rows'] if r['model']==model and r['variant']==variant]
  formal=[r for r in plains if r.get('passed') is not None]
  data=dict(flat_original_passed=sumkey(formal,'passed'),flat_original_requested=sumkey(formal,'requested'),flat_formal_resets=sumkey(formal,'resets'),flat_all_task_resets=sumkey(plains,'resets'),flat_task_rows=[{k:r.get(k) for k in ('task','mean','passed','requested','resets','reasons')} for r in plains],traverse={},gyro={})
  for level in (0,5,9):
   crossing=all_results[f'paired_unified_traverse_L{level}_r1']
   rr=[r for r in crossing['rows'] if r['model']==model and r['variant']==variant]
   data['traverse'][str(level)]=dict(crossed=sumkey(rr,'crossed_count'),requested=sumkey(rr,'requested'),first_episode_failures=sumkey(rr,'first_episode_terminal_failures'),first_episode_timeouts=sumkey(rr,'first_episode_timeouts'),recovered_after_cross=sumkey(rr,'post_cross_recovered_count'),family_rows=rr)
   rotation=all_results[f'paired_unified_gyro_L{level}_r1'];rr=[r for r in rotation['rows'] if r['model']==model and r['variant']==variant]
   samples=sum(r['gyro_metrics']['prepush_first_episode_samples'] for r in rr)
   mae=sum((r['gyro_metrics']['prepush_first_episode_wz_MAE'] or 0)*r['gyro_metrics']['prepush_first_episode_samples'] for r in rr)/samples if samples else None
   aligned=sum((r['gyro_metrics']['prepush_first_episode_wz_mean'] or 0)*(1 if r['command'][1]>0 else -1)*r['gyro_metrics']['prepush_first_episode_samples'] for r in rr)/samples if samples else None
   data['gyro'][str(level)]=dict(first_episode_survived6s=sum(r['gyro_metrics']['first_episode_survived6s'] for r in rr),requested=sumkey(rr,'requested'),first_episode_wz_MAE=mae,aligned_wz_mean=aligned,eligible_window_samples=samples,family_rows=rr)
  rr=[r for r in all_results['paired_unified_fast_L9_r1']['rows'] if r['model']==model and r['variant']==variant]
  data['fast_L9']=dict(command_abs_vx=2.2,crossed=sumkey(rr,'crossed_count'),requested=sumkey(rr,'requested'),first_episode_failures=sumkey(rr,'first_episode_terminal_failures'),first_episode_timeouts=sumkey(rr,'first_episode_timeouts'),family_rows=rr)
  row['conditions'][variant]=data
 output.append(row)
checks=[]
for name,result in all_results.items():
 checks.append(dict(name=name,num_envs=result['num_envs'],physics_dt=result['physics_dt'],action_slot_max_error=result['action_slot_max_error'],motor_envelope_violation_nm=result['motor_envelope_violation_nm'],no_optimizer_constructed=result['no_optimizer_constructed'],numerical_total=sum(sum(r.get('reasons',{}).get('numerical',0) for r in result['rows']) for _ in [0]),model_sha256=result['input_sha256']))
put('PAIRED_SUMMARY.json',dict(scope='Same-batch frozen weights on the current PhysX/fullDR course. Flat is original six windows; rough traversal is first-episode actual crossing; gyro is first6s survival and angular tracking among valid first-episode window samples. Distinct denominators; no automatic graduation or promotion. Only representative terrain rows0/5/9 assessed; highest-speed2.2 at row9.',models=output,checks=checks))
lines=['# 统一 SCUT Rough-v0 两小时：固定权重对照','', '同批比较R1父模型、名义MuJoCo原六项筛选的中间候选及120m保存点。MuJoCo筛选不等于PhysX或完整DR成绩。Flat沿用原判据；穿越和旋转分别统计首次物理episode，重置后的表现不补入首次成绩。','', '| 模型 | 名义Flat /60 | 完整DR Flat /60 | 完整DR Flat原六项重置 |','|---|---:|---:|---:|']
for row in output:
 a=row['conditions']['nominal0'];b=row['conditions']['Step7_all_remaining_DR'];lines.append(f"| {row['model']} | {a['flat_original_passed']} | {b['flat_original_passed']} | {b['flat_formal_resets']} |")
lines+=['','## 统一地形：±1 m/s穿越与±14.137 rad/s旋转','','旋转同时列首次6秒存活和有效窗口角速度MAE，避免只看幸存样本的误差。该MAE单位rad/s，不额外套用新的毕业容差。','', '| 条件 | level | 模型 | 首次穿越 /160 | 旋转首次6秒存活 /160 | 旋转MAE rad/s | 对齐正负方向平均转速 rad/s |','|---|---:|---|---:|---:|---:|---:|']
for variant in variants:
 for level in (0,5,9):
  for row in output:
   c=row['conditions'][variant];g=c['gyro'][str(level)];v=lambda x:'—' if x is None else f'{x:.4f}'
   lines.append(f"| {variant} | {level} | {row['model']} | {c['traverse'][str(level)]['crossed']} | {g['first_episode_survived6s']} | {v(g['first_episode_wz_MAE'])} | {v(g['aligned_wz_mean'])} |")
lines+=['','## 最高代表档：±2.2 m/s穿越','','| 条件 | 模型 | 首次穿越 /160 | 首次episode终止 |','|---|---|---:|---:|']
for variant in variants:
 for row in output:
  d=row['conditions'][variant]['fast_L9'];lines.append(f"| {variant} | {row['model']} | {d['crossed']} | {d['first_episode_failures']} |")
lines+=['','各地形、方向、初态及保护原因见[PAIRED_SUMMARY.json](PAIRED_SUMMARY.json)和evidence内原始RESULT/INITIAL_DR/trajectory；全部保存点的名义MuJoCo筛选另见CHECKPOINT_COMPARISON.md。最终接续选择另见DECISION。']
(T/'PAIRED_COMPARISON.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps(dict(models=len(output),evaluations=len(checks),report=str(T/'PAIRED_COMPARISON.md')),ensure_ascii=False))
