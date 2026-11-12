"""Report existing fixed-weight Rough-v0 evidence by terrain; no new simulation."""
from pathlib import Path
import json,math
T=Path(__file__).resolve().parent
s=json.loads((T/'PAIRED_SUMMARY.json').read_text(encoding='utf-8'))
labels={'tiny_step_rot':'栅格小台阶（1–3 cm）','slope_for_rm_low':'正缓坡（坡比0.05–0.15）','inv_slope_for_rm_low':'反缓坡／凹坡（坡比0.05–0.15）','stair_slope_for_rm_low':'正浅阶（0.5–1.5 cm）','stair_slope_for_rm_mid':'正中阶（2.5–4 cm）','inv_stair_slope_for_rm_low':'反浅阶／下阶（0.5–1.5 cm）','inv_stair_slope_for_rm_mid':'反中阶／下阶（2.5–4 cm）','random_uniform_for_rm':'随机起伏（0–3 cm）'}
models=s['models']; condition='Step7_all_remaining_DR'
def merged(rows,family,skill):
 r=[x for x in rows if x['family']==family]
 n=sum(x['requested'] for x in r)
 if skill=='traverse':return dict(count=sum(x['crossed_count'] for x in r),requested=n,recovered=sum(x['post_cross_recovered_count'] for x in r))
 vals=[x['gyro_metrics'] for x in r];samples=sum(v['prepush_first_episode_samples'] for v in vals)
 return dict(count=sum(v['first_episode_survived6s'] for v in vals),requested=n,mae=sum((v['prepush_first_episode_wz_MAE'] or 0)*v['prepush_first_episode_samples'] for v in vals)/max(samples,1),aligned_speed=sum(abs(v['prepush_first_episode_wz_mean'] or 0)*v['prepush_first_episode_samples'] for v in vals)/max(samples,1))
def stat(x):return f"{x['count']}/{x['requested']}"
L=['# 华南虎 Rough-v0：粗糙地形行走与小陀螺完成报告','','本报告整理已完成的两小时统一 Rough-v0 及其同批 PhysX 固定权重评测，没有追加训练或把回放重置后的成绩补入首次成绩。报告日期：2026-11-12。','','**结论：已展示较强的粗糙地形穿越和旋转保持能力；本轮没有形成综合优于原 R1 父模型的替换模型。** 100m 在最高档完整 DR 高速穿越和旋转保持上小幅改善，120m 普通穿越略降；两者平地精度均退化。原实车调试包保留 R1 第二轮 005m。用户随后选择100m作为下一轮 Rough-v1 的实验父模型，继续利用已获得的粗糙地形能力；这不重写原轮末对照结果。','','## 科目和统计口径','','- 训练：9 类地形、10 行难度统一混训，4096 环境，完整 DR 与名义参数、平地与 Rough 独立交叉。实际 PPO 7206.137 秒，848 次更新，每 5 分钟完整保存。','- 正式逐地形回放：8 类非平地地形，每类正反方向各 10 初态，共 160 次；代表难度为 level 0、5、9。每次观察 20 秒。平地另列保留能力评测。','- 行走完成：首次 episode 内沿指令方向移动至少 2 m，实际地面变化至少 3 mm；中阶另要求两轮越过两级有效高度变化后的清障距离。','- 小陀螺保持：指令 ±14.137 rad/s（约 2.25 转/秒），首次 6 秒无结束。另列首次 episode 有效窗口的角速度绝对误差 MAE；保持不等于精确跟踪。','- 高速穿越：±2.2 m/s 是指令值。完成穿越不表示越障全程达到该实速。','- “浅坑”对应反坡、反台阶／凹地与随机起伏；本轮没有独立的深坑、空洞或缝隙科目。Rough-v0 未启用腾空 reset 或主动跳跃。','','## 完整 DR：总体成绩','','| 难度 | 模型 | 普通穿越（±1 m/s） | 小陀螺首6秒保持 | 旋转 MAE（rad/s） | 实际对齐转速（rad/s） |','|---|---|---:|---:|---:|---:|']
for level in ('0','5','9'):
 for m in models:
  c=m['conditions'][condition];t=c['traverse'][level];g=c['gyro'][level]
  L.append(f"| {level} | {m['model']} | {t['crossed']}/{t['requested']}（{t['crossed']/t['requested']:.1%}） | {g['first_episode_survived6s']}/{g['requested']}（{g['first_episode_survived6s']/g['requested']:.1%}） | {g['first_episode_wz_MAE']:.4f} | {g['aligned_wz_mean']:.4f} |")
L+=['','## 最高代表档 level 9：逐地形完整 DR','','每格分母 20 = 正／反方向各 10 个初态。旋转列表示首6秒保持；误差列为两方向按有效样本数加权。','','| 地形 | 父：走 | 100m：走 | 120m：走 | 父：转 | 100m：转 | 120m：转 | 100m／120m 旋转MAE（rad/s） |','|---|---:|---:|---:|---:|---:|---:|---:|']
output=[]
for f,name in labels.items():
 ts=[merged(m['conditions'][condition]['traverse']['9']['family_rows'],f,'traverse') for m in models]
 gs=[merged(m['conditions'][condition]['gyro']['9']['family_rows'],f,'gyro') for m in models]
 L.append('| '+name+' | '+' | '.join([stat(x) for x in ts]+[stat(x) for x in gs])+f" | {gs[1]['mae']:.3f} / {gs[2]['mae']:.3f} |")
 output.append(dict(family=f,label=name,traverse=ts,gyro=gs))
L+=['','## 最高代表档：高速穿越与越障后速度','','| 条件 | 模型 | ±2.2 m/s指令穿越 /160 | 越障后有效窗口速度MAE（m/s） |','|---|---|---:|---:|']
for cond in ('nominal0',condition):
 for m in models:
  a=m['conditions'][cond]['fast_L9'];print('FAST',m['model'],cond,{k:v for k,v in a.items() if not isinstance(v,list)})
  rows=a['family_rows'];ns=sum(r['post_cross_eligible_samples'] for r in rows);mae=sum((r['post_cross_forward_MAE'] or 0)*r['post_cross_eligible_samples'] for r in rows)/max(ns,1)
  L.append(f"| {cond} | {m['model']} | {a['crossed']}/160 | {mae:.4f} |")
L+=['','## 原有平地能力保留','','| 模型 | 名义平地原六项 /60 | 完整DR平地原六项 /60 | 名义PhysX实速：指令2.0 / 2.2 m/s |','|---|---:|---:|---:|']
for m in models:
 c=m['conditions']['nominal0'];r={x['task']:x for x in c['flat_task_rows']};L.append(f"| {m['model']} | {c['flat_original_passed']}/60 | {m['conditions'][condition]['flat_original_passed']}/60 | {r['forward_2.0']['mean'][0]:.4f} / {r['forward_2.2']['mean'][0]:.4f} |")
L+=['','## 如何理解完成度','','基础的小障碍行走和高速旋转保持已具备。完整 DR 在最高代表档主要剩下凹坡、正反中阶和少量随机地形的穿越失败，以及旋转欠速／误差。具体薄弱项以逐地形表为准。普通穿越、旋转保持、高速穿越和精确速度跟踪是不同测量，不能合并成一个“全面通关率”。','','本轮 100m 相比父模型的完整 DR 最高档高速穿越 145→148/160、旋转保持 153→158/160，但普通穿越 134→133/160，旋转 MAE 1.7066→1.8705 rad/s，且平地精度降低。120m 也未综合改善。故已完成训练和代表项评测，**未晋升新模型**；这不表示机器人没有 Rough-v0 能力。','','只正式检查了代表行 0/5/9 与行9高速，没有声称全部10行、全部随机种子、边走边高速旋转组合或更深坑都已验收。评测8组的 numerical、动作槽误差及电机包络违反为0；主训练原始 numerical34，不能混称全程0。','','## 可追溯文件','','- 原始同批汇总：[PAIRED_SUMMARY.json](PAIRED_SUMMARY.json)。','- 协议和原始评测：[checkpoint_unified_replay.py](checkpoint_unified_replay.py) 与 `evidence/paired_unified_*_RESULT.json`。','- 完整训练报告：[FINAL_REPORT.md](FINAL_REPORT.md)。','- 模型选择：[DECISION.md](DECISION.md)。','- 父模型 SHA：`'+models[0]['sha256']+'`。','- 100m SHA：`'+models[1]['sha256']+'`。','- 120m SHA：`'+models[2]['sha256']+'`。','']
(T/'COURSE_COMPLETION_REPORT.md').write_text('\n'.join(L),encoding='utf-8')
(T/'COURSE_COMPLETION_BY_TERRAIN.json').write_text(json.dumps(dict(source='PAIRED_SUMMARY.json',condition=condition,level=9,model_order=[m['model'] for m in models],rows=output),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('\n'.join(L[25:41]))
