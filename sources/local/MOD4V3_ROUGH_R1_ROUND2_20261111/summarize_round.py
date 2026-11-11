"""Summarize actual saved R1 round2 checkpoints and paired frozen-weight evaluations."""
from pathlib import Path
import json,hashlib,torch,collections
R=Path(r'D:/claude2/fangzhen/_mod4v2_src_20261106');T=R/'sources/local/MOD4V3_ROUGH_R1_ROUND2_20261111';E=T/'evidence';W=T/'weights'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def put(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
models=[];bysha={}
for f in sorted(W.glob('*.pt')):
 sha=hashlib.sha256(f.read_bytes()).hexdigest()
 if sha in bysha:bysha[sha]['aliases'].append(f.name);continue
 d=torch.load(f,map_location='cpu',weights_only=False)
 required=['actor_state_dict','critic_state_dict','optimizer_state_dict','cpu_rng','cuda_rng','reset_rng','terrain_curriculum_state','domain_randomization_state']
 assert all(k in d for k in required),f
 assert d['actor_state_dict']['mlp.0.weight'].shape[1]==35 and d['critic_state_dict']['mlp.0.weight'].shape[1]==78
 tr=d['terrain_curriculum_state'];nom=d['domain_randomization_state']['nominal_env_mask'];flat=tr['flat_mask']
 row=dict(file=f.name,git_path=f.relative_to(R).as_posix(),sha256=sha,bytes=f.stat().st_size,iteration=d['iter'],complete_PPO=True,optimizer_entries=len(d['optimizer_state_dict']['state']),local_policy_steps=tr['local_policy_steps'],terrain_level_counts=torch.bincount(tr['terrain_levels'],minlength=4).tolist(),groups=dict(nominal_flat=int((nom&flat).sum()),nominal_rough=int((nom&~flat).sum()),DR_flat=int((~nom&flat).sum()),DR_rough=int((~nom&~flat).sum())),reward_recipe=d['reward_recipe'],aliases=[])
 models.append(row);bysha[sha]=row
put(E/'MODEL_ARCHIVE_INDEX.json',dict(unique_models=len(models),total_bytes=sum(x['bytes'] for x in models),models=models,storage='ordinary Git complete PT blobs; exact byte aliases listed'))
paths={k:E/(v+'_RESULT.json') for k,v in [('flat','paired_flat_final_r1'),('rough0','paired_rough_final_r1'),('rough3','paired_rough_level3_r1')]}
if not all(p.exists() for p in paths.values()):
 print(json.dumps(dict(index_updated=True,models=len(models),paired_results_pending=[k for k,p in paths.items() if not p.exists()])));raise SystemExit()
raw={k:read(p) for k,p in paths.items()};flat=raw['flat'];summary={'models':[], 'interpretation':'Rough progress marker is not an obstacle exit; short-window or post-marker speed error alone is not a steady-state regression verdict.', 'source_files':{k:str(p.relative_to(R)) for k,p in paths.items()}}
for model,sha in flat['input_sha256'].items():
 item=dict(model=model,sha256=sha,variants={})
 for variant in ['nominal0','Step7_all_remaining_DR']:
  rows=[x for x in flat['rows'] if x['model']==model and x['variant']==variant];formal=[x for x in rows if x['capability_gate']];forward=[x for x in rows if x['task'] in ('forward_2.0','forward_2.2')]
  speed=[]
  for row in forward:
   cmd=2.0 if row['task']=='forward_2.0' else 2.2
   speed.extend(abs(x[0]-cmd) for x in row['per_env'])
  post=[x for x in flat['recovery_rows'] if x['model']==model and x['variant']==variant and x['post_push_passed'] is not None]
  one=dict(flat_formal_passed=sum(x['passed'] for x in formal),flat_formal_requested=sum(x['requested'] for x in formal),flat_forward_MAE=sum(speed)/len(speed),flat_formal_resets=sum(x['resets'] for x in formal),flat_all_resets=sum(x['resets'] for x in rows),flat_numerical=sum(x['reasons']['numerical'] for x in rows),flat_post_push_formal_passed=sum(x['post_push_passed'] for x in post),tasks={x['task']:{k:x[k] for k in ['mean','passed','requested','resets']} for x in rows})
  for name in ['rough0','rough3']:
   rows=[x for x in raw[name]['rows'] if x['model']==model and x['variant']==variant]
   one[name]=dict(crossed=sum(x['crossed_count'] for x in rows),requested=sum(x['requested'] for x in rows),first_terminal_failures=sum(x['first_episode_terminal_failures'] for x in rows),resets=sum(x['resets'] for x in rows),numerical=sum(x['reasons']['numerical'] for x in rows),mean_net_progress_m=sum(x['net_progress_mean'] for x in rows)/len(rows),by_family={family:dict(crossed=sum(x['crossed_count'] for x in rows if x['family']==family),requested=sum(x['requested'] for x in rows if x['family']==family),first_terminal_failures=sum(x['first_episode_terminal_failures'] for x in rows if x['family']==family)) for family in dict.fromkeys(x['family'] for x in rows)})
  item['variants'][variant]=one
 summary['models'].append(item)
summary['physics']={name:dict(action_slot_max_error=data['action_slot_max_error'],motor_envelope_violation_nm=data['motor_envelope_violation_nm'],no_optimizer_constructed=data['no_optimizer_constructed'],wall_seconds=data['wall_seconds']) for name,data in raw.items()}
put(E/'PAIRED_SUMMARY.json',summary)
final=read(E/'TRAIN_FINAL.json');last=final['last_progress'];plan=read(T/'PLAN.json')
lines=['# R1第二轮40分钟最终记录','',f"实际PPO训练 {final['elapsed_seconds']:.3f} 秒，从R1_010m/iter22925恢复；原−1.5e²与指数1.2、完整DR保持。每5分钟完整保存并执行本地MuJoCo名义回放。",'', '## 同条件PhysX比较','', '以下表格为完整DR；原有Flat六项统计保留，Rough穿越按原进度/实际地形变化判据，不新增毕业线。','', '| 模型 | Flat前进MAE | Flat六项通过 | Flat六项reset | R1 L0穿越 | R1 L3穿越 | L3首次终止失败 |','|---|---:|---:|---:|---:|---:|---:|']
for row in summary['models']:
 s=row['variants']['Step7_all_remaining_DR'];lines.append(f"| {row['model']} | {s['flat_forward_MAE']:.5f} | {s['flat_formal_passed']}/{s['flat_formal_requested']} | {s['flat_formal_resets']} | {s['rough0']['crossed']}/{s['rough0']['requested']} | {s['rough3']['crossed']}/{s['rough3']['requested']} | {s['rough3']['first_terminal_failures']} |")
lines+=['','完整名义/DR逐项、推扰后恢复和分地形结果见evidence/PAIRED_SUMMARY.json及原始RESULT。Rough的post_cross只是进度标记，不保证离开整段障碍；不能将该段误差直接叫稳态退化。','', '## 每5分钟MuJoCo名义回放','', '| 保存点 | 2.0实际 | 2.2实际 | 后退/旋转/低身/高身通过 | reset |','|---|---:|---:|---|---:|']
for f in sorted((E/'training_round').glob('*EVAL_SUMMARY.json')):
 d=read(f);r=d['rows'];lines.append(f"| {d['checkpoint']} | {r[0]['vx_mean']:.5f} | {r[1]['vx_mean']:.5f} | {','.join(str(x['passed'])+'/10' for x in r[2:6])} | {sum(x['resets'] for x in r)} |")
lines+=['','MuJoCo是另一引擎的名义回放，和PhysX fullDR分开解读。父模型同协议名义结果保留在PARENT_NOMINAL_MUJOCO_EVAL_SUMMARY.json。','', '## 保存与训练物理','', f"训练done累计：`{json.dumps(last['done_totals'])}`。terrain_boundary是timeout子集，不重复相加。",'',f"本轮保存{len(models)}份不同字节完整PT，共{sum(x['bytes'] for x in models):,} bytes；同字节final别名另记MODEL_ARCHIVE_INDEX。",'', '权重身份、完整PPO/地形状态字段、每5分钟SHA见evidence/MODEL_ARCHIVE_INDEX.json；所有PT本体进入Git。','', 'R1最高level3的本地MuJoCo地形渲染图见terrain_screenshots；来自既有PhysX网格5cm采样重建，机器人只作比例参考。训练未因截图中断。','', '候选选择和是否推进R2另见DECISION.md。原Step7主冻结和Flat对照保留。']
(T/'FINAL_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps(dict(models=len(models),paired_comparison_models=len(summary['models']),report=str(T/'FINAL_REPORT.md')),ensure_ascii=False))
