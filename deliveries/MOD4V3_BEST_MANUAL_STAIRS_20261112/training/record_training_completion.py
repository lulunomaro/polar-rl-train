from pathlib import Path
import json,hashlib
T=Path(__file__).resolve().parent;E=T/'evidence';M=E/'training_round'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
final=read(M/'FINAL.json');plan=read(T/'PLAN.json');models=[]
for path in sorted((T/'weights').glob('*.pt')):
 label=path.stem;meta=read(M/(label+'_FULL_PT.json'))
 sha=hashlib.sha256(path.read_bytes()).hexdigest();assert sha==meta['sha256']
 models.append(dict(file=path.name,git_path=path.relative_to(T).as_posix(),bytes=path.stat().st_size,sha256=sha,iteration=meta['iteration'],full_ppo_rng_present=meta['full_ppo_rng_present'],all_policy_critic_optimizer_tensors_finite=meta['all_policy_critic_optimizer_tensors_finite']))
rows=[]
for minute in range(5,121,5):
 label=f'model_{minute:03d}m';d=read(M/(label+'_EVAL_SUMMARY.json'));save=read(M/f'PERIODIC_{minute:03d}M.json')
 row=dict(minute=minute,iteration=save['iteration'],actual_save_PPO_elapsed_seconds=save['training_elapsed_seconds'],sha256=save['SHA'],nominal_MuJoCo_six_task_passed=sum(x['passed'] for x in d['rows'] if x['passed'] is not None),resets=sum(x['resets'] for x in d['rows']),tasks=d['rows'])
 rows.append(row)
completion=dict(training_seconds=final['elapsed_seconds'],parent_iteration=23665,final_iteration=final['checkpoint']['iteration'],PPO_updates=final['checkpoint']['iteration']-23665,policy_environment_steps=(final['checkpoint']['iteration']-23665)*4096*24,timed_checkpoints=len(rows),full_training_PT_files=len(models),unique_training_PT_sha256=len({x['sha256'] for x in models}),final_is_120m_alias=next(x['sha256'] for x in models if x['file']=='model_final.pt')==next(x['sha256'] for x in models if x['file']=='model_120m.pt'),done_totals=final['last_progress']['done_totals'],safe_closed=read(M/'SAFE_CLOSED.json'),assessment_status='in progress; no model promotion')
(E/'TRAINING_COMPLETION.json').write_text(json.dumps(completion,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(E/'CHECKPOINT_INVENTORY.json').write_text(json.dumps(dict(models=models,nominal_MuJoCo_screening=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# 两小时全部保存点：名义MuJoCo固定权重回放','', '每点同一套10初态、物理5ms回放；这列统计与训练PhysX2.5ms/完整DR分开。原六项是前进2.0/2.2、后退1.5、旋转14.137、两档高度；组合运动另保留原表。二值通过数会在原容差边缘跳变，连续均值一并列出。','', '| 分钟 | iteration | 原六项 /60 | vx@2.0 | vx@2.2 | vx@−1.5 | wz@14.137 | 重置 |','|---:|---:|---:|---:|---:|---:|---:|---:|']
for row in rows:
 tasks=row['tasks'];vx=lambda target:next(x['vx_mean'] for x in tasks if x['command'][0]==target and x['command'][1]==0)
 yaw=next(x['wz_mean'] for x in tasks if x['command'][1]>10)
 lines.append(f"| [{row['minute']}](weights/model_{row['minute']:03d}m.pt) | {row['iteration']} | {row['nominal_MuJoCo_six_task_passed']} | {vx(2.):.4f} | {vx(2.2):.4f} | {vx(-1.5):.4f} | {yaw:.4f} | {row['resets']} |")
lines+=['',f"本轮实际PPO {completion['training_seconds']:.3f}秒，{completion['PPO_updates']}次更新；26份完整训练PT、{completion['unique_training_PT_sha256']}种不同字节；120m/final是否同字节：{completion['final_is_120m_alias']}。首次更新不混入5分钟筛选表。",'', '全部SHA/bytes/实际保存时刻及逐项高度/组合数据见evidence/CHECKPOINT_INVENTORY.json；PhysX对照另见PAIRED_COMPARISON.md。']
(T/'CHECKPOINT_COMPARISON.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
p=T/'README.md';s=p.read_text(encoding='utf-8');s=s.replace('当前状态：主训练正在运行，首次与005m完整PT已保存；最终成绩待轮末比较。',f"当前状态：PPO已完成{completion['training_seconds']:.3f}秒，26份完整PT已保存；固定权重PhysX对照正在执行。",1);p.write_text(s,encoding='utf-8')
print(json.dumps(completion,ensure_ascii=False))
