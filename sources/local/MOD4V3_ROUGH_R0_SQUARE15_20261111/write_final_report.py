"""Report this user-directed Flat20/Rough20 round from completed paired evidence."""
from pathlib import Path
import json
T=Path(__file__).resolve().parent;R=T.parents[2];F=T.parent/'MOD4V3_FLAT_SQUARE15_20261111';E=T/'evidence'
def read(p):return json.loads(p.read_text(encoding='utf8'))
s=read(E/'ROUND_SUMMARY.json');idx=read(E/'MODEL_ARCHIVE_INDEX.json');plan=read(T/'PLAN.json');stop=read(F/'evidence/SEGMENT_COMPLETED_FOR_ROUGH.json');final=s['training']
lines=['# Flat20分钟→Rough R0 20分钟，速度平方项1.5','', '用户授权先加重平方项回Flat；约18分钟时要求下个保存点切Rough。实际用Flat020m完整检查点接续R0，保留完整PPO，预算按Flat20＋Rough20分配。','',f"Flat保存时刻{stop['actual_checkpoint_seconds']:.3f}s，iter{stop['checkpoint']['iteration']}，SHA`{stop['checkpoint']['SHA']}`；Rough实际{final['elapsed_seconds']:.3f}s。",'', '## 配方与实际切换','', '平方项−1.0→−1.5，sigma1，超/欠速对称，指数1.2保留。Flat819名义＋3277完整DR；R0交叉组为nominalFlat164/nominalRough655/DRFlat655/DRRough2622。原MOD4、35/78/6、2.5/10/20ms、TGS32/4、2mm单env重置。', '', 'Flat020m保存完成并核SHA后发送SIGINT，确认进程退出与GPU释放，再启动Rough。未观察到Flat FINAL/SAFE_CLOSED，记录为用户要求切段；不能称完成原40分钟Flat或补造正常关闭标记。Rough正常终态单独见TRAIN_FINAL/TRAIN_SAFE_CLOSED。','', '## 同批PhysX Flat保留与R0地形','', f"Flat{ s['flat_num_envs']}env；Rough{s['rough_num_envs']}env。父指实际Flat020m，flat_original指原square1_030m；所有版本同批初态/DR/噪声/外力/推扰。表为Flat8–12s速度、6s施加推扰；名义参数禁用推扰。",'', '| 模型 | fullDR2.0(通过) | fullDR2.2(通过) | 前进MAE | 正式六项/60 | 正式reset | 名义2.0/2.2 | R0首次穿越/120 | 首episode失败 |','|---|---|---|---:|---:|---:|---|---:|---:|']
for m in s['models']:
 f=m['Step7_all_remaining_DR'];n=m['nominal0'];get=lambda q,task:next(x for x in q['flat_post_rows'] if x['task']==task)
 a=get(f,'forward_2.0');b=get(f,'forward_2.2');c=get(n,'forward_2.0');d=get(n,'forward_2.2')
 lines.append(f"| {m['model']} | {a['post_push_stable_mean'][0]:.5f} ({a['post_push_passed']}/10) | {b['post_push_stable_mean'][0]:.5f} ({b['post_push_passed']}/10) | {f['flat_forward_MAE']:.5f} | {f['flat_passed']} | {f['flat_resets']} | {c['post_push_stable_mean'][0]:.5f}/{d['post_push_stable_mean'][0]:.5f} | {f['rough_crossed']} | {f['rough_first_episode_failures']} |")
lines+=['', 'R0穿越为首次episode内沿指令净进度≥2m且地面高度变化≥3mm，无终止；为浅地形诊断，不等于每种障碍精确成功证明。后续episode reset另列，不能把120/120说成整段无reset。','', '## 每5分钟MuJoCo名义回放','', '| 段/分钟 | 2.0实际/通过 | 2.2实际/通过 | 后退/旋转/低身/高身通过 | reset |','|---|---|---|---|---:|']
for folder,stage in [(F,'Flat'),(T,'R0')]:
 for minute in range(5,21,5):
  d=read(folder/f'evidence/training_round/model_{minute:03d}m_EVAL_SUMMARY.json');rows=d['rows'];a,b=rows[:2]
  lines.append(f"| {stage}/{minute} | {a['vx_mean']:.5f}/{a['passed']} | {b['vx_mean']:.5f}/{b['passed']} | {','.join(str(x['passed']) for x in rows[2:6])} | {sum(x['resets'] for x in rows)} |")
lines+=['', '该回放为5ms MuJoCo名义，不能替代PhysX完整DR验收。原±2%旋转通过数保留，但用户已接受约2.9%均值欠速阶段可用，不重新设10/10硬阻断。','', '## 物理与保存','',f"Rough训练done_totals：`{json.dumps(final['last_progress']['done_totals'],ensure_ascii=False)}`；terrain_boundary是timeout子集，不与timeout相加。",f"配对Flat numerical={s['flat_numerical']}、Rough numerical={s['rough_numerical']}；action误差{ s['flat_action_error']}/{s['rough_action_error']}，六电机包络超限{ s['flat_envelope']}/{s['rough_envelope']}。",f"本Rough段{idx['unique_models']}份不同字节完整PT，{idx['total_bytes']:,}bytes；另Flat首＋4周期共5份PT保存于前段目录。源码/PLAN/STARTUP/RESTORE/PPO/terrain状态与所有PT实体入普通Git。",'', '本轮未开同父同seed−1.0控制组，不把全部变化单独归因于系数；切换Rough后地形分布也变化。原主冻结保留，本轮未自动追加训练或R1。候选和结论按实际配对结果另行追加。','']
(T/'FINAL_REPORT.md').write_text('\n'.join(lines),encoding='utf8');print('Wrote split-round final report')
