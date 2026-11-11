"""Build the R0 report and complete PT index from already saved evidence."""
from pathlib import Path
import json,hashlib,torch,collections
ROOT=Path(r'D:/claude2/fangzhen/_mod4v2_src_20261106')
TRIAL=ROOT/'sources/local/MOD4V3_ROUGH_R1_ABSCUBIC_20261111';E=TRIAL/'evidence';M=E/'training_round';W=TRIAL/'weights'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def put(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
rows=[];known={}
for f in sorted(W.glob('*.pt')):
 sha=hashlib.sha256(f.read_bytes()).hexdigest()
 if sha in known:known[sha]['aliases'].append(f.name);continue
 d=torch.load(f,map_location='cpu',weights_only=False)
 required=('actor_state_dict','critic_state_dict','optimizer_state_dict','cpu_rng','cuda_rng','domain_randomization_state','terrain_curriculum_state')
 assert all(k in d for k in required),f
 assert d['actor_state_dict']['mlp.0.weight'].shape[1]==35 and d['critic_state_dict']['mlp.0.weight'].shape[1]==78
 course=d['terrain_curriculum_state'];nominal=d['domain_randomization_state']['nominal_env_mask'];flat=course['flat_mask']
 row=dict(file=f.name,git_path=f.relative_to(ROOT).as_posix(),bytes=f.stat().st_size,sha256=sha,iteration=d['iter'],optimizer_entries=len(d['optimizer_state_dict']['state']),complete_PPO=True,terrain_state_fields=list(course),local_policy_steps=course['local_policy_steps'],level_counts=torch.bincount(course['terrain_levels'],minlength=4).tolist(),groups=dict(nominal_flat=int((nominal&flat).sum()),nominal_rough=int((nominal&~flat).sum()),DR_flat=int((~nominal&flat).sum()),DR_rough=int((~nominal&~flat).sum())),aliases=[])
 rows.append(row);known[sha]=row
put(E/'MODEL_ARCHIVE_INDEX.json',dict(models=rows,unique_models=len(rows),total_bytes=sum(x['bytes'] for x in rows),storage='ordinary Git full PPO PT blobs, not LFS pointers; byte-identical final alias noted'))
flat_path=E/'paired_flat_final_r1_RESULT.json';rough_path=E/'paired_rough_final_r1_RESULT.json'
if not flat_path.exists() or not rough_path.exists():
 print('Checkpoint archive updated; final paired results pending',len(rows));raise SystemExit()
flat=read(flat_path);rough=read(rough_path);final=read(E/'TRAIN_FINAL.json');candidates=[]
for model,sha in flat['input_sha256'].items():
 modelrow=dict(model=model,sha256=sha)
 for variant in ('nominal0','Step7_all_remaining_DR'):
  f=[x for x in flat['rows'] if x['model']==model and x['variant']==variant]
  post=[x for x in flat['recovery_rows'] if x['model']==model and x['variant']==variant]
  formal=[x for x in f if x['capability_gate']];formalpost=[x for x in post if x['task'] not in ('combo_0.9_1.2','forward_2.7_diagnostic')]
  forward=[x for x in post if x['task'] in ('forward_2.0','forward_2.2')]
  error=[abs(v[0]-(2. if x['task']=='forward_2.0' else 2.2)) for x in forward for v in x['per_env_post_stable']]
  r=[x for x in rough['rows'] if x['model']==model and x['variant']==variant]
  modelrow[variant]=dict(flat_passed=sum(x['post_push_passed'] for x in formalpost),flat_requested=sum(x['requested'] for x in formalpost),flat_resets=sum(x['resets'] for x in formal),flat_diagnostic_resets=sum(x['resets'] for x in f if not x['capability_gate']),flat_forward_MAE=sum(error)/len(error),flat_forward_signed_errors=[v[0]-(2. if x['task']=='forward_2.0' else 2.2) for x in forward for v in x['per_env_post_stable']],flat_post_rows=post,rough_crossed=sum(x['crossed_count'] for x in r),rough_requested=sum(x['requested'] for x in r),rough_resets=sum(x['resets'] for x in r),rough_first_episode_failures=sum(x.get('first_episode_terminal_failures',0) for x in r),rough_post_cross_recovered=sum(x.get('post_cross_recovered_count',0) for x in r),rough_post_cross_eligible_samples=sum(x.get('post_cross_eligible_samples',0) for x in r),rough_rows=r)
 candidates.append(modelrow)
level3_path=E/'paired_rough_level3_r1_RESULT.json'
if level3_path.exists():
 level3=read(level3_path)
 for modelrow in candidates:
  for variant in ('nominal0','Step7_all_remaining_DR'):
   r=[x for x in level3['rows'] if x['model']==modelrow['model'] and x['variant']==variant]
   modelrow[variant].update(rough_level3_crossed=sum(x['crossed_count'] for x in r),rough_level3_first_episode_failures=sum(x['first_episode_terminal_failures'] for x in r),rough_level3_resets=sum(x['resets'] for x in r),rough_level3_post_cross_recovered=sum(x.get('post_cross_recovered_count',0) for x in r),rough_level3_requested=sum(x['requested'] for x in r),rough_level3_rows=r)
summary=dict(training=final,original_segment_budget=read(TRIAL/'PLAN.json')['budget_accounting'],models=candidates,flat_num_envs=flat['num_envs'],rough_num_envs=rough['num_envs'],flat_numerical=sum(x['reasons']['numerical'] for x in flat['rows']),rough_numerical=sum(x['reasons']['numerical'] for x in rough['rows']),flat_action_error=flat['action_slot_max_error'],rough_action_error=rough['action_slot_max_error'],flat_envelope=flat['motor_envelope_violation_nm'],rough_envelope=rough['motor_envelope_violation_nm'])
if level3_path.exists():
 summary.update(rough_level3_numerical=sum(x['reasons']['numerical'] for x in level3['rows']),rough_level3_action_error=level3['action_slot_max_error'],rough_level3_envelope=level3['motor_envelope_violation_nm'])
put(E/'ROUND_SUMMARY.json',summary)
print('MODEL | fullDR Flat passed/reset/forwardMAE | fullDR Rough crossed/reset | nominal Rough crossed')
for m in candidates:
 f=m['Step7_all_remaining_DR'];n=m['nominal0']
 print(m['model'],f['flat_passed'],f['flat_resets'],round(f['flat_forward_MAE'],4),f['rough_crossed'],f['rough_resets'],n['rough_crossed'])
if level3_path.exists():
 print('LEVEL3 MODEL FULLDR crossed firstfail nominal crossed')
 for x in candidates:print(x['model'],x['Step7_all_remaining_DR']['rough_level3_crossed'],x['Step7_all_remaining_DR']['rough_level3_first_episode_failures'],x['nominal0']['rough_level3_crossed'])
print('training',final['elapsed_seconds'],final['last_progress']['done_totals'])
print('unique PT',len(rows),'total bytes',sum(x['bytes'] for x in rows))


# Preserve individual signs; an accurate group mean can conceal both tails.
speed=[]
for m in candidates:
 for variant in ('nominal0','Step7_all_remaining_DR'):
  for x in m[variant]['flat_post_rows']:
   if x['task'] not in ('forward_2.0','forward_2.2'):continue
   target=2. if x['task']=='forward_2.0' else 2.2
   actual=[v[0] for v in x['per_env_post_stable']]
   err=[v-target for v in actual]
   speed.append(dict(model=m['model'],variant=variant,task=x['task'],target=target,actual_mean=sum(actual)/len(actual),signed_error_mean=sum(err)/len(err),MAE=sum(abs(v) for v in err)/len(err),overspeed_above015=sum(v>.15 for v in err),underspeed_below015=sum(v<-.15 for v in err),within015=sum(abs(v)<=.15 for v in err),actual_min=min(actual),actual_max=max(actual),per_env_actual=actual,post_push_passed=x['post_push_passed'],requested=x['requested']))
put(E/'SPEED_ASSESSMENT.json',dict(rows=speed,definition='Postpush8–12s perenvironment averagevx; signed tails relative to eachcommand; formal pass still requires originalreset rules',comparison='parent is exact square2_015m trainingparent; flat_parent is originalFlat1.5_020m'))

# Human-readable report uses only saved paired results.
lines=['# R1二次加绝对三次项接续结果','',
 '用户要求压制速度偏差，保留−2e²并叠加−2|e|³/(1m/s)，超速与欠速对称，指数权重1.2保留；R1地形/指令/DR/PPO/接口/时序/solver/2mm单env重置未修改。','',
 '从二次2.0_015m完整检查点iter23027/SHA22513a6e…接续，恢复PPO与课程等级、地形分组、偏移和累计计数；物理episode重新开始。原R1段756.803s＋二次2.0段903.074s，当前三次接续实际%.3fs；三段合计%.3fs，属于同一轮40min预算。'%(final['elapsed_seconds'],final['elapsed_seconds']+read(TRIAL/'PLAN.json')['budget_accounting']['prior_total_consumed_seconds']),'',
 '原段是用户要求切段后的SIGINT退出，无FINAL/SAFE_CLOSED；新段正常终态见TRAIN_FINAL/TRAIN_SAFE_CLOSED，不补造旧段正常关闭。','',
 '## 同批PhysX配对','',
 'parent为实际二次2.0_015m训练父；flat_parent为原Flat1.5_020m参考。所有模型同批初态/DR/噪声/外力/推扰。以下前进为6s推扰后8–12s均值；名义参数不施加推扰。','',
 '| 模型 | fullDR2.0/通过 | fullDR2.2/通过 | 前进MAE | 正式通过/60 | 正式reset | 名义2.0/2.2 | R1L0穿越/160 | L0恢复/160 | R1L3穿越/160 | L3恢复/160 |','|---|---|---|---:|---:|---:|---|---:|---:|---:|---:|']
for m in candidates:
 f=m['Step7_all_remaining_DR'];n=m['nominal0'];r={x['task']:x for x in f['flat_post_rows']};nr={x['task']:x for x in n['flat_post_rows']}
 lines.append('| %s | %.5f (%d/10) | %.5f (%d/10) | %.5f | %d | %d | %.5f/%.5f | %d | %d | %s | %s |'%(m['model'],r['forward_2.0']['post_push_stable_mean'][0],r['forward_2.0']['post_push_passed'],r['forward_2.2']['post_push_stable_mean'][0],r['forward_2.2']['post_push_passed'],f['flat_forward_MAE'],f['flat_passed'],f['flat_resets'],nr['forward_2.0']['post_push_stable_mean'][0],nr['forward_2.2']['post_push_stable_mean'][0],f['rough_crossed'],f['rough_post_cross_recovered'],str(f.get('rough_level3_crossed','pending')),str(f.get('rough_level3_post_cross_recovered','pending'))))
lines+=['','穿越：首episode沿原指令净进度≥2m且地面变化≥3mm；中级阶梯双轮中心越过实际碰撞面累计两等效阶高位置并留.2m。阶梯为.1m采样高度场插值，不能称为垂直箱体台阶。恢复要求越障后速度误差≤.2m/s连续.5s，且在首次reset前。','',
 '## 每5分钟MuJoCo名义诊断','',
 '| 保存点 | 2.0实际/通过 | 2.2实际/通过 | 后退/旋转/低身/高身通过 | reset |','|---|---|---|---|---:|']
for path in sorted(M.glob('*EVAL_SUMMARY.json')):
 d=read(path);r=d['rows'];lines.append('| %s | %.5f/%d | %.5f/%d | %s | %d |'%(d['checkpoint'],r[0]['vx_mean'],r[0]['passed'],r[1]['vx_mean'],r[1]['passed'],','.join(str(x['passed']) for x in r[2:6]),sum(x['resets'] for x in r)))
lines+=['','MuJoCo名义与PhysX名义/fullDR分开解释；组均值接近不代表每个DR样本达标。SPEED_ASSESSMENT.json保存各env正负误差和超速/欠速尾部。旋转原±2%统计保留，不新设10/10硬阻断。','',
 '## 保存与物理','',
 '训练累计done：`'+json.dumps(final['last_progress']['done_totals'])+'`。terrain_boundary为timeout子集，不叠加。',
 '同批Flat/R1L0 numerical分别%d/%d，action槽误差%s/%s；电机包络超出%s/%s。'%(summary['flat_numerical'],summary['rough_numerical'],summary['flat_action_error'],summary['rough_action_error'],summary['flat_envelope'],summary['rough_envelope']),
 '本接续完整PT共%d份、%d bytes，全部保存实体；checkpoint别名另列MODEL_ARCHIVE_INDEX。原R1段3份，二次2.0段首完整＋005m/010m/015m另4份。'%(len(rows),sum(x['bytes'] for x in rows)),'',
 '候选选择与训练结论另见DECISION.md；未自动开启R2、追加40min或替换Step7主冻结。']
(TRIAL/'FINAL_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
