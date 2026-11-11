"""Write a factual R0 round report from final paired evaluation, no new runs."""
from pathlib import Path
import json,hashlib
ROOT=Path(r'D:/claude2/fangzhen/_mod4v2_src_20261106')
T=ROOT/'sources/local/MOD4V3_ROUGH_R0_20261111';E=T/'evidence'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def put(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
s=read(E/'ROUND_SUMMARY.json');idx=read(E/'MODEL_ARCHIVE_INDEX.json');plan=read(T/'PLAN.json');models=s['models'];parent=next(x for x in models if x['model']=='parent')
# Keep raw paired metrics; selection is finalized only after reading actual retention/tradeoffs.
trained=[x for x in models if x['model']!='parent']
ordered=sorted(trained,key=lambda x:(-x['Step7_all_remaining_DR']['rough_crossed'],x['Step7_all_remaining_DR']['rough_first_episode_failures'],-x['Step7_all_remaining_DR']['flat_passed'],x['Step7_all_remaining_DR']['flat_resets'],x['Step7_all_remaining_DR']['flat_forward_MAE']))
chosen=ordered[0];minute=int(chosen['model'].rsplit('_',1)[1]);file=T/'weights'/f'model_{minute:03d}m.pt';sha=hashlib.sha256(file.read_bytes()).hexdigest();assert sha==chosen['sha256']
row=next(x for x in idx['models'] if x['sha256']==sha);full=chosen['Step7_all_remaining_DR'];pfull=parent['Step7_all_remaining_DR']
selection=dict(label=chosen['model'],minute=minute,path=str(file),sha256=sha,iteration=row['iteration'],status='retained R0 experimental candidate; original Flat freeze unchanged; no automaticR1',criteria='fullDR level0 crossed count, firstepisodefailures, thenFlatretention; allrankedvalues explicitly reported',model_metrics=chosen,parent_metrics=parent,ranked_labels=[x['model'] for x in ordered])
put(E/'CANDIDATE_SELECTION.json',selection)
final=s['training'];last=final['last_progress'];tag='trial-20261111-mod4-rough-r0-final-01'
lines=['# MOD4 R0 首轮：40分钟训练与配对结果','',f'2026-11-11 用户授权按 R0 推进。实际训练 {final["elapsed_seconds"]:.3f} s /4096环境，末iter{last["iteration"]}；首完整＋每5分钟保存。父square1_030m / iter22618 / SHA`{plan["parent_sha256"]}`，恢复actor/critic/STD/Adam/RNG，新物理episode与level0课程。','', '保留完整DR、20%名义、20%平地交叉分组（164/655/655/2622）、原MOD4资产/接口/包络、2.5/10/20ms、TGS32/4、2mm单envreset及−1.0e²速度项。R0只新增浅地形，不含中级阶梯、airreset或新奖励。','', '## 同批结果','',f'Flat回归{s["flat_num_envs"]}环境、600步；Rough诊断{s["rough_num_envs"]}环境、1000步。父与8检查点同初态、同DR样本/噪声/扰动配对，无优化器。Flat仍按原六项统计；Rough为level0六类地形×正反1m/s×10初态，共120初态/条件/模型，20s窗口，首次reset前净行进≥2m且实测地面变化≥3mm计crossed。Rough是浅地形越障诊断，不是全课程毕业率。','', '| 模型 | 完整DR Flat六项 | Flat正式reset | 完整DR前进MAE | 完整DR Rough越障 | Rough首次episode终止失败 | 名义Rough越障 |','|---|---:|---:|---:|---:|---:|---:|']
for x in models:
 d=x['Step7_all_remaining_DR'];n=x['nominal0'];lines.append(f'| {x["model"]} | {d["flat_passed"]}/60 | {d["flat_resets"]} | {d["flat_forward_MAE"]:.5f} | {d["rough_crossed"]}/120 | {d["rough_first_episode_failures"]}/120 | {n["rough_crossed"]}/120 |')
lines+=['','## 本轮保留候选','',f'保留 **{chosen["model"]} / {minute}分钟**，iter{row["iteration"]}，SHA`{sha}`。完整DR Rough越障{pfull["rough_crossed"]}→{full["rough_crossed"]}/120；Flat正式{pfull["flat_passed"]}→{full["flat_passed"]}/60。选择标准如上，所有其它检查点都保留；不因40m叫final默认续它。此模型作为R0实验候选，原Flat主冻结保持，不自动启动R1。','', '| 条件 | Flat任务 | 受扰恢复后vx / wz / h | 通过 | reset |','|---|---|---|---:|---:|']
for variant in ('nominal0','Step7_all_remaining_DR'):
 for x in chosen[variant]['flat_post_rows']:
  score='诊断' if x['post_push_passed'] is None else f'{x["post_push_passed"]}/10'
  lines.append(f'| {variant} | {x["task"]} | '+', '.join(f'{v:.5f}' for v in x['post_push_stable_mean'])+f' | {score} | {x["resets"]} |')
lines+=['','| Rough地形/方向 | 父fullDR crossed | 候选fullDR crossed | 候选首次失败 | 候选平均净进度m |','|---|---:|---:|---:|---:|']
for x,y in zip(pfull['rough_rows'],full['rough_rows']):
 assert x['task']==y['task'];lines.append(f'| {y["task"]} | {x["crossed_count"]}/10 | {y["crossed_count"]}/10 | {y["first_episode_terminal_failures"]} | {y["net_progress_mean"]:.3f} |')
lines+=['','## 每5分钟MuJoCo名义回放','', '该回放不替代同源PhysX完整DR结果。','', '| 分钟 | 2.0实际/通过 | 2.2实际/通过 | 后退/旋转/两高度通过 | reset |','|---:|---|---|---|---:|']
for f in sorted((E/'training_round').glob('*_EVAL_SUMMARY.json')):
 if f.name.startswith('model_final'):continue
 d=read(f);r=d['rows'];minute_label=d['checkpoint'].replace('model_','')
 lines.append(f'| {minute_label} | {r[0]["vx_mean"]:.5f} / {r[0]["passed"]} | {r[1]["vx_mean"]:.5f} / {r[1]["passed"]} | '+','.join(str(x['passed']) for x in r[2:6])+f' | {sum(x["resets"] for x in r)} |')
lines+=['','## 物理与保存','',f'训练终态：`{json.dumps(last["done_totals"],ensure_ascii=False)}`。地形boundary是单列timeout，closure为2mm单envreset；numerical0不表示没有闭链终止。',f'轮末Flat numerical={s["flat_numerical"]}、Rough numerical={s["rough_numerical"]}；动作槽误差Flat={s["flat_action_error"]}、Rough={s["rough_action_error"]}；电机包络Flat={s["flat_envelope"]}、Rough={s["rough_envelope"]}。',f'{idx["unique_models"]}份不同字节完整PPO权重共{idx["total_bytes"]:,}bytes，包含课程等级/类型/分组状态；全部PT本体入Git，byte-identical final作别名。实际源SHA与远端支持文件核验记录保留。','', '80env与4096env探针均无优化器更新，原closure事件保留。80env探针后把累计路径课程指标改为指令方向净位移；原探针源SHA与实际上传SHA一致。评测原始失败与后续修复如有发生另列，不改raw。','',f'计划与源码见PLAN.json、support；逐模型见evidence/MODEL_ARCHIVE_INDEX.json，配对原始结果见evidence。最终归档标签`{tag}`。','']
(T/'FINAL_REPORT.md').write_text('\n'.join(lines),encoding='utf8')
print(json.dumps(dict(candidate=selection['label'],sha256=sha,rough=full['rough_crossed'],parent_rough=pfull['rough_crossed'],flat=full['flat_passed'],parent_flat=pfull['flat_passed']),ensure_ascii=False))
