"""Summarize completed paired evidence without changing raw scores or promoting a model."""
from pathlib import Path
import json
T=Path(__file__).resolve().parent;E=T/'evidence'
def read(name):return json.loads((E/name).read_text(encoding='utf8'))
def put(name,data):(T/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
landing=read('paired_landing_r2_RESULT.json')
flat=read('paired_flat_r2_RESULT.json')
low=read('paired_rough_level0_r2_RESULT.json')
high=read('paired_rough_level3_r2_RESULT.json')
models=list(landing['input_sha256']);rows=[]
for model in models:
 row=dict(model=model,sha256=landing['input_sha256'][model],conditions={})
 for variant in ['nominal0','Step7_all_remaining_DR']:
  air=[r for r in landing['rows'] if r['model']==model and r['variant']==variant]
  plains=[r for r in flat['rows'] if r['model']==model and r['variant']==variant]
  easy=[r for r in low['rows'] if r['model']==model and r['variant']==variant]
  hard=[r for r in high['rows'] if r['model']==model and r['variant']==variant]
  forward=[r for r in plains if r['task'] in ('forward_2.0','forward_2.2')]
  formal=[r for r in plains if r.get('passed') is not None]
  sums=lambda values,key:sum(r.get(key,0) or 0 for r in values)
  row['conditions'][variant]=dict(air_requested=sums(air,'requested'),air_cleared=sums(air,'cleared_count'),air_landed=sums(air,'landed_count'),air_posture_recovered=sums(air,'posture_recovered_count'),air_command_recovered=sums(air,'command_recovered_count'),air_survived_first2s=sums(air,'survived_first2s'),air_first_episode_closure_peak_m=max(r['first_episode_closed_loop_peak_m'] for r in air),air_impact_peak_n=max(r['landing_force_peak_n'] or 0 for r in air),flat_original_passed=sums(formal,'passed'),flat_original_requested=sums(formal,'requested'),flat_forward_rows=forward,flat_all_task_resets=sums(plains,'resets'),R1_L0_crossed=sums(easy,'crossed_count'),R1_L0_requested=sums(easy,'requested'),old_R0_L0_crossed=sums([r for r in easy if r['family'] not in ('stair_slope_for_rm_mid','inv_stair_slope_for_rm_mid')],'crossed_count'),R1_L3_crossed=sums(hard,'crossed_count'),R1_L3_requested=sums(hard,'requested'),R1_L3_first_episode_failures=sums(hard,'first_episode_terminal_failures'))
 rows.append(row)
put('PAIRED_SUMMARY.json',dict(scope='Same-batch frozen weights; landingfirstepisode/Flatexistingwindows/R1firstcrossing have distinct denominators; no automatic graduation or promotion',models=rows))
lines=['# R2 首轮40分钟：同批固定权重比较','', '所有训练保存点与父模型使用同批条件。腾空是5/10cm额外落高，尚未测试主动跳高。表中落地恢复只算首次物理episode，reset后的站姿不给成绩。Flat通过数按原任务窗口判据，另列整段重置。R1为首次越障进度，三种指标不能合称全段无reset。','', '| 模型 | 名义落地姿态/160 | 完整DR落地姿态/160 | 完整DR落地后指令/160 | 名义Flat原六项/60 | 完整DRFlat原六项/60 | 完整DR R1-L3/160 |','|---|---:|---:|---:|---:|---:|---:|']
for row in rows:
 a=row['conditions']['nominal0'];b=row['conditions']['Step7_all_remaining_DR']
 lines.append(f"| {row['model']} | {a['air_posture_recovered']} | {b['air_posture_recovered']} | {b['air_command_recovered']} | {a['flat_original_passed']} | {b['flat_original_passed']} | {b['R1_L3_crossed']} |")
lines+=['','统计原表和完整边界见[PAIRED_SUMMARY.json](PAIRED_SUMMARY.json)及evidence/*RESULT.json；候选选择另见DECISION。']
(T/'PAIRED_COMPARISON.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
print(json.dumps(dict(models=len(rows),summary=str(T/'PAIRED_SUMMARY.json')),ensure_ascii=False))
