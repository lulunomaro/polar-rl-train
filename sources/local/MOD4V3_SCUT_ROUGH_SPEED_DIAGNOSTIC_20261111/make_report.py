"""Generate a concise report from measured pre-reset endpoint statistics."""
from pathlib import Path
import json
b=Path(__file__).resolve().parent;summary=json.loads((b/'evidence/SUMMARY.json').read_text(encoding='utf8'));rows=summary['rows'];labels={'parent':'Flat1.5_020m','r1_010':'R1_010m','r1_cubic005':'R1三次项005m','scut_rough_stair':'华南虎 rough_stair 1000（迁移）','scut_rough_dash':'华南虎 rough_dash 3500（迁移）'}
def num(x):return '无' if x is None else f'{x:.4f}'
text=['# 华南虎参考策略与 MOD4 full DR Rough 的速度误差','',
'测试日期：2026-11-11。两组固定权重回放已经完成；没有训练，没有更新策略。结果直接来自重置前物理状态，原始轨迹、脚本、配置及参考PT均保留。','',
'结论：原华南虎权重直接转到MOD4不能构成华南虎原机器人性能基准；本次迁移存在机器人几何/默认角/控制器差异，并且参考策略轮子动作频繁触及本项目统一±6裁剪。我们自身模型的窗口平均误差混合了起步、越障和重新加速，不能据此将中级台阶欠速认定为策略退化，也不能由此决定继续加强惩罚。相同窗口下fullDR与nominal的差异是真实测量值，但尚未区分正常动力学响应与持续跟踪偏差。','',
'## 测试口径','',
'- 每个模型、难度和DR条件：8类非平地 × 正反1m/s × 10初态，160环境；nominal/fullDR配对。R1 level0、level3独立，共3200条20s回放流。',
'- 表中速度按原华南虎奖励定义计算：v=root_lin_vel_b_x*cos(pitch)，e=v-command；不是世界坐标真实水平速度的另一种替代定义。机身vx统计也完整保存在SPEED_RESULT.json。',
'- 主要窗口0.5–3.0s；只统计首次episode，包含终止前末帧，排除重置后的新状态。该窗口早于5.5s外力与6s速度push，检验的是完整DR配置下的扰动前跟踪；后文的首次episode全段表另列。',
'- 主表每行同时列出具有数据的环境数与走完3s窗口的数量。后者可因地形边界timeout减少，不能全部称为摔倒。',
'- 超/欠速按实际运动的指令方向判断：directional_error=(v-command)*sign(command)，>0为超速，<0为欠速。',
'- 固定MOD4机构、原电机包络、35D/6D策略接口、2.5ms物理/10msPD/20ms策略、TGS32/4、2mm单环境重置；DR范围与已完成R1一致。','',
'## 扰动前速度误差：full DR','',
'|R1难度|策略|MAE m/s|RMSE m/s|P95绝对误差 m/s|有向偏差 m/s|±0.2内时间|有数据/完成3s|','|---|---|---:|---:|---:|---:|---:|---:|']
for row in rows:
 if row['variant']!='Step7_all_remaining_DR':continue
 m=row['steady_pre_push']['scut_horizontal_vx'];text.append(f"|{row['level']}|{labels[row['model']]}|{num(m.get('MAE'))}|{num(m.get('RMSE'))}|{num(m.get('P95_abs'))}|{num(m.get('directional_bias_positive_overspeed'))}|{100*m.get('within_0p2_fraction',0):.1f}%|{m['eligible_envs']}/{m['completed_window_count']}（共160）|")
text+=['','## 同条件 nominal 对照','','|难度|策略|nominal MAE|full DR MAE|fullDR超速>0.2占比|fullDR欠速>0.2占比|','|---|---|---:|---:|---:|---:|']
for row in rows:
 if row['variant']!='Step7_all_remaining_DR':continue
 nom=next(x for x in rows if x['model']==row['model'] and x['level']==row['level'] and x['variant']=='nominal0');m=row['steady_pre_push']['scut_horizontal_vx'];n=nom['steady_pre_push']['scut_horizontal_vx'];text.append(f"|{row['level']}|{labels[row['model']]}|{num(n.get('MAE'))}|{num(m.get('MAE'))}|{100*m.get('overspeed_gt_0p2_fraction',0):.1f}%|{100*m.get('underspeed_gt_0p2_fraction',0):.1f}%|")
text+=['','## 首次 episode 全段（0.5s之后、至首次终止/越界）','','以下不是各策略等长的20s稳定窗口：快策略更早越过瓦片边界，失败策略更早终止；所见数据包含实际活到5.5/6s的环境受到外力和推扰后的状态，不能称所有环境都经历了推扰。','','|难度|策略|全段MAE|平均首次episode s|首次物理终止/160|首次边界timeout/160|20s全部episode numerical|','|---|---|---:|---:|---:|---:|---:|']
for row in rows:
 if row['variant']!='Step7_all_remaining_DR':continue
 m=row['first_episode_after_start']['scut_horizontal_vx'];text.append(f"|{row['level']}|{labels[row['model']]}|{num(m.get('MAE'))}|{row['first_episode_duration_mean_s']:.2f}|{row['first_terminal_failures']}|{row['first_timeouts']}|{row['numerical_resets']}|")
text+=['','## 分地形结果','','下表使用扰动前相同窗口；所有数据和正反方向在SPEED_RESULT.json中保留。','','|难度|策略|地形/方向|实际平均水平投影速度|MAE|','|---|---|---|---:|---:|']
for level in (0,3):
 values=json.loads((b/f'evidence/paired_speed_level{level}_r1/SPEED_RESULT.json').read_text())
 for row in values['rows']:
  if row['variant']=='Step7_all_remaining_DR' and row['model'] in ('parent','r1_010','r1_cubic005') and row['task']!='all' and 'stair_slope_for_rm_mid' in row['task']:
   m=row['steady_pre_push']['scut_horizontal_vx'];text.append(f"|{level}|{labels[row['model']]}|{row['task']}|{num(m.get('mean_velocity'))}|{num(m.get('MAE'))}|")
text+=['','## 原权重与参考日志的含义','','原USD只查询运行时DOF顺序，没有推进物理。原策略actuator顺序核实为[LF,LR,RF,RR,LW,RW]，与本次MOD4环境一致。使用同名相对关节位移与default+0.5*a动作；没有为获得好成绩搜索排列或缩放。','',
'华南虎原agent clip_actions=null，原轮速目标10*a后在±100rad/s饱和；本测试沿用我们±6动作限制（轮速目标±60rad/s）。如下动作裁剪比例按每只轮子、整20s流统计（含重置后的后续episode），不可直接当主0.5–3s窗口的比例。','',
'|难度|策略|左轮裁剪比例|右轮裁剪比例|','|---|---|---:|---:|']
for level in (0,3):
 v=json.loads((b/f'evidence/paired_speed_level{level}_r1/SPEED_RESULT.json').read_text())
 for i,key in enumerate(v['input_sha256']):
  clips=v['action_clip_hits'][i];n=v['action_samples_per_model'];text.append(f'|{level}|{labels[key]}|{100*clips[4]/n:.1f}%|{100*clips[5]/n:.1f}%|')
text+=['',
'因此不能将这些迁移误差用于宣称华南虎原方案更差，不能由此判定奖励无效，也不能用迁移失败反向证实我们的模型已毕业。要测华南虎原系统，需要原机器人、原控制器和原DR下的独立基准，本次没有执行。','',
'原TensorBoard记录见evidence/REFERENCE_TRAIN_LOG.json：rough_stair最后100iter指数速度奖励0.5970，平方奖励−0.010927；rough_dash分别0.6464、−0.068847。原记录是训练中变化指令/混合地形下的episode奖励率，日志末迭代也不等于保存PT迭代；不能当本次固定1m/s的MAE，也不从指数均值反推m/s。','',
'## 物理与接口检查','']
for level in (0,3):
 v=json.loads((b/f'evidence/paired_speed_level{level}_r1/RESULT.json').read_text());text.append(f"- level{level}：{v['num_envs']}环境，numerical={sum(x['reasons']['numerical'] for x in v['rows'])}，action_slot_max_error={v['action_slot_max_error']}，motor_envelope_violation_nm={v['motor_envelope_violation_nm']}，SAFE_CLOSED=true。")
text+=['','## 文件与接下来判断','','- `PLAN.json`/`MODELS.json`：配方、远端路径及5个固定权重SHA。','- `REFERENCE_AND_MAPPING.json`：迁移语义及明确差异。','- `evidence/paired_speed_level*/SPEED_RESULT.json`：直接统计值及每环境误差。','- `evidence/paired_speed_level*/trajectory.npz`：重置前速度/pitch、firstalive、终止/timeout与指令原始数组，支持独立复算。','- `weights/`：两份未修改的原华南虎完整PT；MOD4三份完整PT已在先前Git提交中保存。','',
'本次不追加训练、不修改奖励或DR。本次结果不足以判定需要修复、模型已经退化或发生OOD。后续判断先分开越障成功/进度、正常减速与重加速过程、确认离开障碍并恢复支撑后的持续误差；不能仅凭这一窗口或原权重迁移成绩选择奖励系数。现有越障里程标记也不保证已离开整段连续台阶。','']
text += ['', '## 起步与越障瞬态：解释更正', '', '0.5–3s窗口混合起步、碰阶减速、爬升与重新加速，不能称为稳态误差。现有进度里程标记不等于整段障碍出口；其后的欠速也不能自动归为恢复失败。用户指出的正常动力学耗时已纳入[瞬态解释](TRANSIENT_INTERPRETATION.md)，原初稿在REPORT_INITIAL_INTERPRETATION.md保留。数值不变，但不再据此认定策略退化、OOD或需要继续提高惩罚。', '']
(b/'REPORT.md').write_text('\n'.join(text),encoding='utf8');print('wrote',b/'REPORT.md')
