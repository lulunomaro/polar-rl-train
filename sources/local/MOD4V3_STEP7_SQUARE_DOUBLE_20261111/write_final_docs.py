"""Write the completed speed-square experiment from actual paired results; no training."""
from pathlib import Path
import json
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 s=read(E/'ROUND_SUMMARY.json');idx=read(E/'MODEL_ARCHIVE_INDEX.json');plan=read(T/'PLAN.json');sel=read(E/'SELECTED_TRAINED_CANDIDATE.json');final=read(E/'training_round/FINAL.json')
 chosen=sel['model_id'];label=sel['selected'];model=next(x for x in idx['models'] if x['id']==chosen)
 tag='trial-20261111-step7-square-double-final-01'
 def stats(label,variant):return next(x for x in s['models'] if x['model']==label and x['variant']==variant)
 def forward(row):
  d={x['task']:x for x in row['post_rows']};return [(d[k]['post_push_stable_mean'][0],d[k]['post_push_passed']) for k in ['forward_2.0','forward_2.2']]
 def fwtext(row):return ' / '.join(f'{v:.4f} ({n}/10)' for v,n in forward(row))
 a=stats(label,'nominal0');b=stats(label,'Step7_all_remaining_DR');parent=stats('parent','Step7_all_remaining_DR')
 out=['# 双侧速度平方惩罚加倍：40分钟完整结果','',
  '用户2026-11-11要求同时加强超速与欠速平方惩罚，并从父检查点单开40分钟。',
  f'实际{final["elapsed_seconds"]:.3f}s/4096env，8个周期检查点。父为remaining_010m，iter22265，SHA`{plan["parent_sha256"]}`，与上一轮完全相同父；完整actor/critic/std/Adam/RNG恢复，新物理episode。',
  '唯一行为改变：track_lin_vel_xy_square权重−0.5→−1.0，sigma=1；e=command_vx−root_lin_vel_b_x×cos(pitch)，每步−e²×0.02。指数奖励、819名义/3277完整DR、随机reset分布、PPO、solver、plant、35actor/78critic/6action保持。源差异与真实奖励路径短探针保留。','',
  '## 同批新旧配方比较','',
  f'{s["paired_num_envs"]}env/600步，19模型：本轮8检查点、旧−0.5配方8检查点、直接父、原主冻结、已接受push020。所有模型相同nominal0/fullDR、8任务×10初态、相同DR属性/噪声/外力/push；3.6～5.98s和8～12s分别统计。旧配方使用其原权重，但在新−1.0环境中无优化器、只取actor动作；奖励系数不会改变固定actor的物理轨迹。','',
  '| 模型label | PhysX名义2.0/2.2 | 完整DR2.0/2.2 | fullDR正式六项 | 正式reset |',
  '|---|---|---|---|---:|']
 for lab in dict.fromkeys(x['model'] for x in s['models']):
  n=stats(lab,'nominal0');d=stats(lab,'Step7_all_remaining_DR')
  out.append(f'| {lab} | {fwtext(n)} | {fwtext(d)} | {d["post_passed"]}/60 | {d["formal_resets"]} |')
 out += ['',f'本轮保留诊断候选 **{chosen}**，iter{model["iteration"]}，SHA`{model["sha256"]}`。{sel["reason"]}',
  '', 'label说明：remaining_005～040为本轮−1.0权重，mixed2_005～040为上一轮−0.5权重；parent为共同直接父。',
  '', '## 同时长对照','',
  '| 分钟 | 新/旧 fullDR前进通过数 | 新/旧 fullDR前进MAE | 新/旧名义MAE | 新/旧正式reset |',
  '|---:|---|---|---|---|']
 comparison=[]
 for minute in range(5,41,5):
  new='remaining_'+f'{minute:03d}';old='mixed2_'+f'{minute:03d}'
  nd=stats(new,'Step7_all_remaining_DR');od=stats(old,'Step7_all_remaining_DR');nn=stats(new,'nominal0');on=stats(old,'nominal0')
  npass=sum(n for _,n in forward(nd));opass=sum(n for _,n in forward(od))
  row={'minute':minute,'new_model':new,'old_model':old,'new_fullDR_forward_pass':npass,'old_fullDR_forward_pass':opass,'new_fullDR_MAE':nd['forward_post_mean_absolute_error'],'old_fullDR_MAE':od['forward_post_mean_absolute_error'],'new_nominal_MAE':nn['forward_post_mean_absolute_error'],'old_nominal_MAE':on['forward_post_mean_absolute_error'],'new_formal_resets':nd['formal_resets'],'old_formal_resets':od['formal_resets']};comparison.append(row)
  out.append(f'| {minute} | {npass}/{opass} | {row["new_fullDR_MAE"]:.5f}/{row["old_fullDR_MAE"]:.5f} | {row["new_nominal_MAE"]:.5f}/{row["old_nominal_MAE"]:.5f} | {row["new_formal_resets"]}/{row["old_formal_resets"]} |')
 out += ['', '一次训练seed下的同批评测比较，用于这次实验决策；不把随机训练差异写成普遍因果结论。没有增加任务门槛，也不以均值代替每环境通过数。',
  '', '## 选中检查点逐任务','', '| 条件 | 任务 | 均值vx/wz/h | 通过 | reset |', '|---|---|---|---:|---:|']
 for variant in ['nominal0','Step7_all_remaining_DR']:
  for x in stats(label,variant)['post_rows']:
   score='诊断' if x['post_push_passed'] is None else str(x['post_push_passed'])+'/10'
   out.append(f'| {variant} | {x["task"]} | '+', '.join(f'{v:.5f}' for v in x['post_push_stable_mean'])+f' | {score} | {x["resets"]} |')
 out += ['', '## 物理与保存', '',
  f'训练终态done_totals：`{json.dumps(s["training_last_progress"]["done_totals"],ensure_ascii=False)}`。2mm是单envreset，原闭链与电机常数保持。',
  f'轮末配对numerical{s["paired_numerical"]}、closure reset{s["paired_closure_resets"]}、最大闭链{s["paired_max_closure_m"]*1000:.5f}mm，action槽误差{s["action_slot_max_error"]}，电机包络越界{s["motor_envelope_violation_nm"]}。',
  f'{idx["unique_models"]}份不同字节完整PPO PT共{idx["total_bytes"]:,}bytes；final相同字节只作别名。全部PT本体入Git。原Step6/Step7主冻结和已接受push020未被覆盖；此轮不自动晋升，不自动启动下一轮或Rough。',
  '', 'MuJoCo每5min名义回放与同源PhysX分开报告。此前固定权重检验确认：两引擎前向偏差方向相反；原训练actor输入与paired包装差0，0/5ms与速度统计定义不能解释主要差距。训练收益以本轮同源配对为准，不能把跨引擎差异直接定为策略回归。',
  '', f'最终记录tag：`{tag}`。完整配方PLAN.json，原始试错、结果和全检查点索引见evidence。','']
 (T/'FINAL_REPORT.md').write_text('\n'.join(out),encoding='utf8')
 dump(E/'MATCHED_WEIGHT_COMPARISON.json',{'comparison':comparison,'same_parent_sha256':plan['parent_sha256'],'only_behavior_change':plan['experiment_change']})
 for name in ['REPORT.md','README.md']:
  with (T/name).open('a',encoding='utf8') as f:f.write(f'\n\n本轮完成{final["elapsed_seconds"]:.3f}s，8个周期完整检查点/回放及同源配对。结果见[FINAL_REPORT](FINAL_REPORT.md)；保留{chosen}，iter{model["iteration"]}，SHA`{model["sha256"]}`，仅诊断候选。选择理由：{sel["reason"]}。\n')
 regpath=R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json';reg=read(regpath)
 existing={x['id']:i for i,x in enumerate(reg['models'])}
 for x in idx['models']:
  x=dict(x);x['git_storage']='ordinary Git full PT bytes; no LFS pointer';x['role']='retained diagnostic candidate of speed-square double experiment' if x['id']==chosen else 'complete PPO checkpoint of speed-square double experiment'
  if x['id'] in existing:reg['models'][existing[x['id']]]=x
  else:reg['models'].append(x)
 stage=next(x for x in reg['stages'] if x['id']=='square1')
 stage.update(retained_model_id=chosen,retained_model_sha256=model['sha256'],other_model_ids=[x['id'] for x in idx['models'] if x['id']!=chosen],final_checkpoint_id=idx['final_model_id'],status='authorized40min completed with matched replay; not automatically promoted',selection_basis=sel['reason'],final_report=(T/'FINAL_REPORT.md').relative_to(R).as_posix(),final_tag=tag)
 stage['training_method']['actual_seconds']=final['elapsed_seconds']
 reg['latest_speed_square_diagnostic_model_id']=chosen;reg['last_update_tag']=tag;reg['weights_summary'].update(models=len(reg['models']),unique_sha256=len({x['sha256'] for x in reg['models']}),total_bytes=sum(x['bytes'] for x in reg['models']));dump(regpath,reg)
 with (R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODELS.md').open('a',encoding='utf8') as f:
  f.write('\n\n## 双侧平方惩罚加倍：完整40分钟检查点\n\n| 模型ID | iteration | bytes | SHA256 |\n|---|---:|---:|---|\n')
  for x in idx['models']:f.write(f'| [{x["id"]}](../MOD4V3_STEP7_SQUARE_DOUBLE_20261111/weights/{Path(x["git_path"]).name}) | {x["iteration"]} | {x["bytes"]:,} | `{x["sha256"]}` |\n')
 for rel in ['README.md','docs/DR_TRAINING_INDEX_20261111.md','docs/DR_TRAINING_RESUME_20261111.md','sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/README.md']:
  with (R/rel).open('a',encoding='utf8') as f:f.write(f'\n\n双侧平方惩罚加倍实验已完成{final["elapsed_seconds"]:.3f}s，−1.0e²，其余同第二轮。保留{chosen}（iter{model["iteration"]}，SHA`{model["sha256"]}`）供检查；原始结果见`sources/local/MOD4V3_STEP7_SQUARE_DOUBLE_20261111/FINAL_REPORT.md`，全部PT实体归档。总{len(reg["stages"])}阶段/分支、{len(reg["models"])}完整PT；不自动覆盖原冻结或开下一轮。\n')
 print(json.dumps({'selected':chosen,'model_files':len(reg['models']),'matched_comparisons':len(comparison),'tag':tag},ensure_ascii=False))
if __name__=='__main__':main()
