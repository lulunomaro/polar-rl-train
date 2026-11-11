"""Render the completed Flat1.5 trial from saved measurements only."""
from pathlib import Path
import json
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
def read(p):return json.loads(p.read_text(encoding='utf8'))
summary=read(E/'ROUND_SUMMARY.json');idx=read(E/'MODEL_ARCHIVE_INDEX.json');plan=read(T/'PLAN.json');final=read(E/'training_round/FINAL.json')
result=read(E/'paired_final_r1_RESULT.json')
lines=['# Flat完整DR：速度平方项1.5，40分钟结果','',f"实际训练{summary['training_elapsed_seconds']:.3f}s，4096env；首完整＋每5分钟完整PPO保存。父square1_030m / iter22618 / SHA`{plan['parent_sha256']}`。",'', '速度平方项−1.0e²→−1.5e²，sigma1，指数奖励1.2及其他项保留；819名义＋3277完整DR，Flat，TGS32/4、2.5/10/20ms、35/78/6、2mm单env重置。','', '## 同批PhysX名义与完整DR','',f"{result['num_envs']}env，固定权重无optimizer，10初态×8任务×2条件×父与检查点；相同DR/初态/噪声/外力/推扰。表为8–12s窗口，6s施加速度推扰；名义禁用推扰。",'', '| 模型 | fullDR 2.0 (通过/10) | fullDR 2.2 (通过/10) | fullDR前进MAE | fullDR六项/60 | 正式reset | 名义2.0/2.2 | 名义MAE |','|---|---|---|---:|---:|---:|---|---:|']
for label in result['input_sha256']:
 full=next(x for x in summary['models'] if x['model']==label and x['variant']=='Step7_all_remaining_DR')
 nominal=next(x for x in summary['models'] if x['model']==label and x['variant']=='nominal0')
 row=lambda x,name:next(y for y in x['post_rows'] if y['task']==name)
 a=row(full,'forward_2.0');b=row(full,'forward_2.2');c=row(nominal,'forward_2.0');d=row(nominal,'forward_2.2')
 lines.append(f"| {label} | {a['post_push_stable_mean'][0]:.5f} ({a['post_push_passed']}) | {b['post_push_stable_mean'][0]:.5f} ({b['post_push_passed']}) | {full['forward_post_mean_absolute_error']:.5f} | {full['post_passed']} | {full['formal_resets']} | {c['post_push_stable_mean'][0]:.5f}/{d['post_push_stable_mean'][0]:.5f} | {nominal['forward_post_mean_absolute_error']:.5f} |")
lines+=['','原±2%旋转通过数保留作为统计；用户已接受约2.9%平均欠速阶段可用，不把严格10/10重新设成晋级阻断。2.7和组合为诊断。','', '## 每5分钟MuJoCo名义回放','', '| 分钟 | 指令2.0实际/通过 | 指令2.2实际/通过 | 后退/旋转/低身/高身通过 | reset |','|---|---|---|---|---:|']
for minute in range(5,41,5):
 d=read(E/f'training_round/model_{minute:03d}m_EVAL_SUMMARY.json');rows=d['rows'];a,b=rows[:2]
 lines.append(f"| {minute} | {a['vx_mean']:.5f}/{a['passed']} | {b['vx_mean']:.5f}/{b['passed']} | {','.join(str(x['passed']) for x in rows[2:6])} | {sum(x['resets'] for x in rows)} |")
lines+=['','MuJoCo为5ms名义回放，与训练完整DR的PhysX统计分列。不能以一个引擎的通过数替另一个验收。','', '## 保存与物理终止','',f"训练done_totals：`{json.dumps(final['last_progress']['done_totals'],ensure_ascii=False)}`。",f"配对numerical={summary['paired_numerical']}，closure_reset={summary['paired_closure_resets']}，action槽误差={summary['action_slot_max_error']}，六电机包络超限={summary['motor_envelope_violation_nm']}。",f"保存{idx['unique_models']}份不同字节完整PT，共{idx['total_bytes']:,}bytes；final别名{idx['final_model_id']}。全部普通Git实体，配方与源码同目录保存。",'', '## 解释范围','', '这轮是从相同Flat父继续训练并加权的独立实验。父与新权重同批评测可判断接训后的实际变化；本轮未另开同父同seed的−1.0e²控制组，因此不能把所有变化仅归因于系数。R0同时改变地形，不能作为纯奖励系数因果对照。','', '候选选择在CANDIDATE_SELECTION.json与后续结论追加；原主冻结保留。此次预算仅本轮40分钟，未自动再开训练或R1。','']
(T/'FINAL_REPORT.md').write_text('\n'.join(lines),encoding='utf8');print('Wrote final measured report')
