"""Summarize the actual two-hour result without promoting a default model."""
from pathlib import Path
import sys,json,hashlib,time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
T=Path(__file__).resolve().parent;E=T/'evidence';R=T.parents[2]
final=json.loads((E/'training/FINAL.json').read_text());selected=json.loads((T/'weights/SELECTED_STUDENT.json').read_text());rows=[]
for p in sorted((E/'checkpoint_evals').glob('*/EVALUATION.json')):
 d=json.loads(p.read_text())
 if not d.get('complete'):continue
 name=p.parent.name
 if not name.startswith('model_'):continue
 rough=d['pitch_summary']['random_uniform_for_rm']['braking_peak_deg_max'];flat=d['pitch_summary']['plane_for_rm']['braking_peak_deg_max'];rows.append(dict(checkpoint=name,rough_braking_deg=rough,flat_braking_deg=flat,flat60=d['flat60_passed'],straight5=d['straight_passed'],actual_oblique20=d['actual_oblique_passed'],descent5=d['descent_passed']))
from matched_pitch_metrics import compare
checks=[]
base=R/'sources/local/MOD4V3_PITCH_STABILITY_LEVEL9_ANGLE30_CONT_20261115/evidence/baseline_parent_pitch/trajectory.npz'
for p in sorted((E/'checkpoint_evals').glob('model_*m/EVALUATION.json')):
 d=json.loads(p.read_text())
 if not d.get('complete'):continue
 matched=compare(base,p.parent/'pitch/trajectory.npz',until_s=7.98)
 preserve=d['flat60_passed']==60 and d['descent_passed']==5 and d['straight_passed']>=4
 tracking=all(g['candidate'][k]<=g['parent'][k]*1.05 for g in matched['summary'].values()for k in ['moving_vx_MAE','braking_vx_MAE','braking_path_first0p8s_m_mean'])
 reduced=all(g['candidate']['braking_pitch_peak_deg']<=g['parent']['braking_pitch_peak_deg']*.85 and g['candidate']['startup_pitch_peak_deg']<=g['parent']['startup_pitch_peak_deg']*1.05 for g in matched['summary'].values())
 checks.append(dict(checkpoint=p.parent.name,passed=bool(preserve and tracking and reduced and matched['complete_requested_horizon']),preserve=preserve,tracking=tracking,pitch_reduced15pct_both_terrains=reduced))
stable=any(a['passed']and b['passed']and int(b['checkpoint'][6:-1])-int(a['checkpoint'][6:-1])==5 for a,b in zip(checks,checks[1:]))
(E/'PITCH_REPAIR_DECISION.json').write_text(json.dumps(dict(stable_improvement_met=stable,criterion='Two consecutive five-minute checkpoints: both-terrain braking peak>=15pct lower, startup<=5pct worse, speed/path<=5pct worse, flat60,straight>=4/5,descent5/5 preserved; same7.98s horizon',checkpoints=checks,promoted=False),indent=2)+'\n')
plan=json.loads((T/'PLAN.json').read_text());elapsed=final['elapsed_seconds'];summary=dict(stable_pitch_improvement_met=stable,training_elapsed_seconds=elapsed,requested_training_seconds=7200,selected=selected,checkpoint_results=rows,promoted=False,default_sha256=plan['frozen_comprehensive_parent_sha256'],automatic_extension=False)
(E/'FINAL_RESULT.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
lines=['# SCUT奖励与急停轮协调：两小时训练结果','','连续两点达到俯仰修复验收：'+str(stable)+'。未满足时不得宣称已修复。','','实际PPO时长：'+str(round(elapsed,3))+'秒；预算7200秒，按完整迭代保存结束。综合默认保持db6，未自动晋升。','','|检查点|崎岖急停°|平地急停°|平地|正向两阶|实际斜向|下阶|','|---|---:|---:|---:|---:|---:|---:|']
for r in rows:lines.append(f"|{r['checkpoint']}|{r['rough_braking_deg']:.3f}|{r['flat_braking_deg']:.3f}|{r['flat60']}/60|{r['straight5']}/5|{r['actual_oblique20']}/20|{r['descent5']}/5|")
lines+=['','实验候选：'+selected['source_file']+'，SHA256 `'+selected['sha256']+'`。','保留原能力：'+str(selected['preserves_comprehensive_fixed_baseline'])+'；世界水平速度/停车位移相对父模型5%内：'+str(selected['tracking_within5pct_of_starting_checkpoint'])+'。','本表列完整名义协议峰值；候选筛选使用同一7.98秒有效时段及世界x差分实速，见STUDENT_FIXED_RANKING.json。训练内累计极值不作为修复结论；一次低谷不足以证明稳定改进。完整DR仍按实际完成证据记录。']
(T/'FINAL_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
periodic=[r for r in rows if r['checkpoint'].removeprefix('model_').removesuffix('m').isdigit()]
if periodic:
 fig,ax=plt.subplots(figsize=(9,4.5));minutes=[int(r['checkpoint'][6:-1])for r in periodic];ax.plot(minutes,[r['rough_braking_deg']for r in periodic],'-o',label='Rough L9');ax.plot(minutes,[r['flat_braking_deg']for r in periodic],'-o',label='Flat');ax.axhline(22.6446,color='C0',ls='--',alpha=.5);ax.axhline(18.6731,color='C1',ls='--',alpha=.5);ax.set(xlabel='Training minutes',ylabel='Nominal braking peak (deg)',title='SCUT pitch / brake repair checkpoints');ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(E/'checkpoint_pitch_curve.png',dpi=160);plt.close(fig)
artifacts=[]
for p in T.rglob('*'):
 if p.is_file()and p.suffix in {'.npz','.npy'}:
  artifacts.append(dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),storage='Raw original retained locally; SHA indexed in Git'))
(E/'NUMPY_ARTIFACT_INDEX.json').write_text(json.dumps(artifacts,indent=2)+'\n')
(E/'PIPELINE_COMPLETE.json').write_text(json.dumps(dict(epoch=time.time(),training_complete=True,evaluations_complete=True,report_created=True,promoted=False,automatic_extension=False),indent=2)+'\n')
print(json.dumps(dict(actual_training_seconds=elapsed,selected=selected['source_file'],evaluated_models=len(rows),promoted=False)),flush=True)
