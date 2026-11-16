"""Audit archived SCUT and adopted MOD4v3 rewards/trajectories, with no rollout or PPO update."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,math,re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
T=ROOT/'sources/local/MOD4V3_SCUT_PITCH_BRAKE_2H_20261116'
S=ROOT/'sources/local/SCUT_ORIGINAL_PITCH_AUDIT_20261116'
D=ROOT/'deliveries/MOD4V3_LOW_PITCH_20261116'
YAML=ROOT.parent/'refs/wheeled-legged_RL-main/pretrained/26_infantry/rough_rotation_stair/2026-07-23_16-23-21/params/env.yaml'
E=HERE/'evidence';E.mkdir(exist_ok=True)
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):
 try:return p.relative_to(ROOT).as_posix()
 except ValueError:return str(p)
raw=YAML.read_text(encoding='utf8');study=json.loads((T/'evidence/SCUT_REWARD_STUDY.json').read_text());startup=json.loads((T/'evidence/training/STARTUP.json').read_text());plan=json.loads((T/'PLAN.json').read_text());selected=json.loads((T/'evidence/checkpoint_evals/model_005m/EVALUATION.json').read_text());scut_result=json.loads((S/'evidence/RESULT.json').read_text())
def scalar(name):return float(re.search(r'^'+re.escape(name)+r': ([^\n]+)$',raw,re.M).group(1))
scut_weights=study['saved_reward_weights'];our_weights=startup['reward_weights'];scut_sigma=scalar('lin_vel_xy_square_sigma');our_sigma=float(startup['lin_vel_xy_square_sigma'])
eff_scut=scut_weights['track_lin_vel_xy_square']*scut_sigma**2;eff_ours=our_weights['track_lin_vel_xy_square']*our_sigma**2
assert abs(eff_scut+.00625)<1e-12 and abs(eff_ours+1.5)<1e-12
weight_rows=[]
for key in ['track_lin_vel_xy_square','track_lin_vel_xy','stand_still_lin_vel','flat_orientation_y_v','flat_orientation_y_exp','ang_vel_xy','action_rate','action_smoothness_leg','action_smoothness_wheel','joint_torque','wheel_power']:
 a=float(scut_weights[key]);b=float(our_weights[key]);weight_rows.append(dict(term=key,scut=a,ours=b,absolute_weight_ratio=abs(b/a)if a else None))
reward=dict(scut_velocity_square_sigma=scut_sigma,our_velocity_square_sigma=our_sigma,scut_effective_speed_square=eff_scut,our_effective_speed_square=eff_ours,effective_speed_square_ratio=eff_ours/eff_scut,raw_outer_weight_ratio=our_weights['track_lin_vel_xy_square']/scut_weights['track_lin_vel_xy_square'],weight_rows=weight_rows,pitch_scut='-2*A(cmd)^2*gx^2 + exp(-gx^2/0.02)',pitch_ours_target='-2.25*A(cmd)^2*gx^2 +3*exp(-gx^2/0.02)-2; native pitch damping-.05wy^2 plus specialist-.05wy^2',A='2*exp(-cmd_vx^2/3)+2',scope='per-second reward rates; actual rewards multiply dt=.02. Target extra requires active ground specialist; native state-machine weights may depend on state. Counterfactual algebra below assumes ordinary grounded state, roll0, pitch rate0.',disabled_gates=study['disabled_gates'])
reward['counterfactual_examples']=[]
for v in [0.,2.2]:
 for deg in [5.,10.,15.]:
  gx=math.sin(math.radians(deg));A=2*math.exp(-v*v/3)+2;u=1-math.exp(-gx*gx/.02)
  reward['counterfactual_examples'].append(dict(command_vx=v,pitch_deg=deg,scut_pitch_loss_relative_to_upright=2*A*A*gx*gx+u,ours_target_pitch_loss_relative_to_upright=2.25*A*A*gx*gx+3*u))
reward['speed_error_examples']=[dict(error=e,scut_cost=-eff_scut*e*e,ours_cost=-eff_ours*e*e)for e in [1.,2.2]]
dump(E/'REWARD_COMPARISON.json',reward)
paths=[S/'evidence/trajectory.npz',T/'evidence/checkpoint_evals/model_005m/pitch/trajectory.npz'];a=np.load(paths[0]);b=np.load(paths[1]);assert set(a.files)==set(b.files)
rows=[]
def metrics(z,horizon=13.98):
 reset=np.flatnonzero(z[:,8]>.5)
 if len(reset):z=z[:reset[0]]
 z=z[z[:,0]<=horizon+1e-7];time=z[:,0];vx=np.r_[np.nan,np.diff(z[:,5])/np.diff(time)]
 valid=time>=2.-1e-7;moving=valid&(z[:,9]>.5);start=moving&(z[:,10]<.8-1e-7);brake=valid&(z[:,9]<.5)&(z[:,10]>=1.-1e-7)&(z[:,10]<1.8-1e-7)
 pre=(time>=2.8-1e-7)&(time<3.-1e-7);firststop=(time>=3.-1e-7)&(time<3.8-1e-7)
 peak=lambda mask:float(np.rad2deg(abs(z[mask,1])).max())
 return dict(horizon_s=float(time[-1]),samples=len(z),pitch_RMS_deg=float(np.rad2deg(np.sqrt(np.mean(z[valid,1]**2)))),startup_peak_deg=peak(start),braking_peak_deg=peak(brake),first_stop_entry_world_vx_fd=float(vx[pre][-1]),first_stop_pitch_peak_deg=peak(firststop),first_stop_0p8s_displacement_m=float(abs(z[firststop,5][-1]-z[pre,5][-1])),moving_world_vx_MAE=float(np.mean(abs(vx[moving]-z[moving,3]))),startup_rate_peak_rad_s=float(abs(z[start,2]).max()),braking_rate_peak_rad_s=float(abs(z[brake,2]).max()))
for key in a.files:
 x,y=a[key],b[key];assert np.allclose(x[:,0],y[:,0]);assert not np.any(x[:,8]>.5)and not np.any(y[:,8]>.5)
 family=key.split('_h')[0];height,speed=map(float,key.split('_h')[1].split('_v'))
 assert np.allclose(x[:,3],y[:,3])and np.allclose(x[:,9:11],y[:,9:11])
 sm=metrics(x);om=metrics(y);rows.append(dict(case=key,family=family,height=height,command_speed=speed,SCUT=sm,adopted_MOD4v3=om,pitch_RMS_ratio=om['pitch_RMS_deg']/sm['pitch_RMS_deg'],first_stop_entry_speed_ratio=om['first_stop_entry_world_vx_fd']/sm['first_stop_entry_world_vx_fd'],common_7p98s=dict(SCUT=metrics(x,7.98),adopted_MOD4v3=metrics(y,7.98)),brake_teacher_covers_case=(height>=.38 and speed>=2.),startup_teacher_covers_case=False))
summary={}
for family in ['random_uniform_for_rm','plane_for_rm']:
 group=[r for r in rows if r['family']==family];g={}
 for side in ['SCUT','adopted_MOD4v3']:
  g[side]=dict(pitch_RMS_deg_mean=float(np.mean([q[side]['pitch_RMS_deg']for q in group])),startup_peak_deg_max=max(q[side]['startup_peak_deg']for q in group),braking_peak_deg_max=max(q[side]['braking_peak_deg']for q in group))
 g['ours_over_scut']={k:g['adopted_MOD4v3'][k]/g['SCUT'][k]for k in g['SCUT']};summary[family]=g
comparison=dict(created_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),adopted_model_sha256=json.loads((D/'MODEL_IDENTITY.json').read_text())['sha256'],scut_model_sha256=scut_result['sha256'],protocol='Archived 8 paired 14s runs; same commands/timestamps and terrain assets; respective own robots; every first episode complete, no reset. Full horizon and common7.98s both included; world speed from position differences.',no_new_rollouts=True,no_optimizer_updates=True,summary=summary,rows=rows)
dump(E/'TRAJECTORY_COMPARISON.json',comparison)
controls=dict(SCUT=json.loads((S/'PLAN.json').read_text())['preserved_native_control'],MOD4v3={k:startup[k]for k in ['physics_dt_s','control_dt_s','feedback_dt_s','wheel_feedback_dt_s','total_mass_kg']},training_retention=dict(target_envs=615,non_target_keep_envs=1433,num_envs=2048,keep_lambda=plan['teacher_retention']['lambda_bc'],high_stance_leg_anchor_lambda=plan['teacher_retention']['lambda_high_stance'],high_stance_leg_anchor_batch=plan['teacher_retention']['high_stance_minibatch'],brake_distillation=plan['brake_distillation']),causal_identification_limit='Different plants/controllers and unmatched achieved speeds; no common-state/current-student physics ablation. Reward ratios are algebraic facts, not measured causal shares. High-stance leg anchors still apply as global auxiliary minibatches, despite target environments being exempt from keep mask.')
dump(E/'CONTROL_AND_RETENTION.json',controls)
# Compact scientific comparison, using original trajectories without launching engines.
fig,axs=plt.subplots(2,2,figsize=(12,7),constrained_layout=True)
labels=['Rough h.28 v1.2','Rough h.28 v2.2','Rough h.40 v1.2','Rough h.40 v2.2','Flat h.28 v1.2','Flat h.28 v2.2','Flat h.40 v1.2','Flat h.40 v2.2'];idx=np.arange(8)
for ax,field,title in [(axs[0,0],'first_stop_entry_world_vx_fd','Actual speed before first stop (m/s)'),(axs[0,1],'first_stop_pitch_peak_deg','First-stop pitch peak (deg)')]:
 ax.bar(idx-.18,[q['SCUT'][field]for q in rows],width=.36,label='SCUT V14_2');ax.bar(idx+.18,[q['adopted_MOD4v3'][field]for q in rows],width=.36,label='MOD4v3 adopted 5m');ax.set_xticks(idx,labels,rotation=45,ha='right',fontsize=8);ax.set_title(title);ax.grid(axis='y',alpha=.25);ax.legend(fontsize=8)
for ax,key,title in [(axs[1,0],'random_uniform_for_rm_h0.28_v1.2','Comparable low-speed case: rough h.28 / cmd1.2'),(axs[1,1],'random_uniform_for_rm_h0.4_v2.2','Different achieved speeds: rough h.40 / cmd2.2')]:
 for label,arrays in [('SCUT V14_2',a),('MOD4v3 adopted 5m',b)]:
  z=arrays[key];mask=(z[:,0]>=1.8)&(z[:,0]<=4.2);ax.plot(z[mask,0],np.rad2deg(z[mask,1]),label=label)
 ax.axvline(2,ls='--',color='gray',lw=.8);ax.axvline(3,ls='--',color='gray',lw=.8);ax.set_title(title,fontsize=10);ax.set_xlabel('Time (s); start2s / stop3s');ax.set_ylabel('Pitch (deg)');ax.grid(alpha=.25);ax.legend(fontsize=8)
fig.savefig(E/'scut_adopted_pitch_speed.png',dpi=170);plt.close(fig)
inputs=[YAML,T/'PLAN.json',T/'weights/model_005m.pt',D/'model_full_ppo.pt',T/'evidence/training/STARTUP.json',T/'evidence/SCUT_REWARD_STUDY.json',T/'evidence/source_pin/pinned_scut_base_env.py',T/'support/mod4v3_ppo_v1/pitch_stability_env.py',T/'support/mod4v3_ppo_v1/pitch_stability_math.py',T/'support/mod4v3_ppo_v1/pitch_brake_math.py',T/'support/mod4v3_ppo_v1/scut_flat_forward_square_env.py',T/'support/mod4v3_ppo_v1/teacher_retention.py',S/'PLAN.json',S/'evidence/RESULT.json',*paths]
dump(E/'INPUT_INDEX.json',dict(inputs=[dict(path=rel(p),bytes=p.stat().st_size,sha256=sha(p),storage='existing Git text/PT'if p.suffix not in ['.npz','.yaml']else'local original indexed; not pushed by this audit')for p in inputs],code_sha256=sha(Path(__file__)),historical_retired_native_config='native_config.py contains legacy names; not used as current robot asset identity. Current identity from actual PLAN and STARTUP readback.'))
head=['# 华南虎奖励与11月16日低俯仰模型差距分析','', '本次已按用户指令采用5分钟完整检查点为“11月16日俯仰较低模型”，SHA c874a1af，iteration25362，作为当前综合默认。旧db6保存回退。没有新增训练、物理回放或改奖励；本报告复算两方已保存的8条完整14秒轨迹与固定配置。','', '## 1. “两倍”出现在哪里','', '| 地形 | 指标 | 华南虎 | 已采用MOD4v3 | 比值 |','|---|---|---:|---:|---:|']
for fam,title in [('random_uniform_for_rm','难度9崎岖'),('plane_for_rm','平地')]:
 for key,name in [('pitch_RMS_deg_mean','RMS均值'),('startup_peak_deg_max','启动峰值'),('braking_peak_deg_max','急停峰值')]:
  g=summary[fam];head.append(f'|{title}|{name}|{g["SCUT"][key]:.3f}°|{g["adopted_MOD4v3"][key]:.3f}°|{g["ours_over_scut"][key]:.2f}×|')
head+=['','崎岖RMS约2.26倍、启动约2.29倍，但急停为1.94倍；平地RMS约1.84倍、启动1.93倍，急停仅0.72倍。不能把所有指标合称超过两倍。','', '## 2. 同指令并非同实速','', '| 工况 | SCUT首次入刹实速 | MOD4v3首次入刹实速 | SCUT首次急停峰值 | MOD4v3首次急停峰值 |','|---|---:|---:|---:|---:|']
for q in rows:head.append(f'|{q["case"]}|{q["SCUT"]["first_stop_entry_world_vx_fd"]:.3f} m/s|{q["adopted_MOD4v3"]["first_stop_entry_world_vx_fd"]:.3f} m/s|{q["SCUT"]["first_stop_pitch_peak_deg"]:.3f}°|{q["adopted_MOD4v3"]["first_stop_pitch_peak_deg"]:.3f}°|')
head+=['','最接近且不利于我们解释的崎岖0.28m/1.2m/s工况：SCUT实际更快(1.489 vs1.210m/s)，首次急停5.085 vs5.754°，差距约13%；启动仍4.867 vs8.131°，确实还有动态姿态差距。高速工况则比较了2.1m/s制动与0.15–0.80m/s制动，不能从峰值比例归因奖励或策略优越。','', '## 3. 华南虎的直接俯仰奖励已存在于我们基础奖励中','', '`gx=sin(pitch)`，`A(vcmd)=2*exp(-vcmd^2/3)+2`。SCUT每秒基础直接俯仰项为 `-2*A^2*gx^2 + exp(-gx^2/0.02)`，并有 `-.05*(wx^2+wy^2)`。零速平方增益32，高速2.2m/s约11.505；停车比行驶更强回正，指数项从0°稠密生效。保存的速度直立、速度高度、姿态高度门控均false。','', '我们原生基础已经使用相同项；目标615环境另加 `-.25*A^2*gx^2 -2*(1-exp(-gx^2/.02)) -.05*wy^2`。同一普通接地状态下合并为 `-2.25*A^2*gx^2 +3*exp(-gx^2/.02)-2`，因此不能把现有差距解释为漏掉SCUT姿态项。','', '## 4. 新核出的关键差异：速度平方有效强度为240倍','', '不能只比较外部权重。源码原始量是 `(error*lin_vel_xy_square_sigma)^2`。SCUT保存值为外部-0.1、内部sigma0.25，因此有效 `-0.00625*e^2`；我们的实际STARTUP与选中检查点为外部-1.5、sigma1，实际 `-1.5*e^2`。外部权重15倍，完整有效系数240倍。指数速度奖励的误差clamp=1不会裁掉此独立平方项。','', '相同2.2m/s误差时，两者每秒平方成本为0.03025与7.26；实际20ms单步为0.000605与0.1452。这是同状态的奖励代数比较，不是整个回报/梯度比。我们的速度与姿态取舍强烈偏向保持速度；这与本次实测速度差一致，但尚无当前学生单项消融去量化贡献。','', '| 项 | SCUT权重 | MOD4v3原生权重 | 绝对值比 |','|---|---:|---:|---:|']
for q in weight_rows:head.append(f'|{q["term"]}|{q["scut"]:g}|{q["ours"]:g}|{q["absolute_weight_ratio"]:g}×|')
head+=['','停车L1残速成本2倍；动作一阶变化5倍、腿二阶2倍、轮二阶3倍；关节扭矩/轮功率10倍。更强的动作与能耗惩罚会给突发急停所需的快速腿轮调整增加代价。这些系数事实已确认；“因此延迟了多少毫秒”尚未用当前学生物理消融测量。','', '## 5. 旧动作锚与示范覆盖仍限制修复','', '1433/2048环境继续全6动作模仿原db6(系数1)，615/2048用于启停PPO。目标环境虽不受keep mask限制，训练每个minibatch仍有256条旧db6高站姿腿动作锚，系数0.25，直接约束同一个actor。两方环境标记不进入35维actor，状态分布重叠时可能形成目标冲突；目前只有机制证据，没有量化梯度归因。','', '本次新轮协调示范只覆盖高度>=0.38m、速度>=2m/s、硬停车后100ms(5拍)，仅轮动作；不覆盖起步，也不覆盖0.28m低站姿。选中模型最大的起步峰值正出现在低站姿高速工况，该工况不受新增轮示范覆盖。基础姿态PPO仍覆盖该工况，因此这不是完全未训练；它说明训练示范覆盖不足。','', '## 6. 物理和控制差异不能归给奖励','', 'SCUT使用作者V14_2、1ms物理和1kHz腿/轮PD；MOD4v3使用不同的机体/电机/弹簧，2.5ms物理、100Hz腿与400Hz轮PD，策略均50Hz。腿反馈周期差10倍、轮差2.5倍，是潜在动作响应差异。没有同机体同频率的策略消融，因此不能宣称改成1kHz就能复制SCUT，亦未改动实际控制合同。','', '若主要靠机身倾斜移动质心，倒立摆准静态量级tan(theta)≈a/g；1秒达到2.1m/s对应约12°，与我们的9–11°起步峰值量级接近。腿部移动轮位/质心可以改变这一关系，12°不是机械最低俯仰或不可改善结论。','', '## 7. 判断与下一步','', '有把握的判断：汇总中的两倍含有严重实速混杂；在相对接近的低速崎岖制动工况，差距已缩到约13%，但起步姿态差距仍真实存在。最强的奖励差异是240倍有效速度平方成本及更强的动作/能耗约束，而直接姿态项并不缺。旧教师动作锚、新示范只覆盖高站姿停车和不同控制带宽，是剩余差距的具体机制候选。','', '后续应从已采用5m模型出发，以同实际入刹速度/停车距离的固定协议比较；优先验证起步与低站姿腿轮协调，再做保留平地60/60、正向5/5、下阶5/5的单因素验证。-1.5速度奖励是现有训练合同，不为追低角度直接削弱。当前用户仅授权采用和分析，本次没有修改奖励或追加训练。','', '![原始轨迹实速与俯仰对照](evidence/scut_adopted_pitch_speed.png)','', '证据：[轨迹复算](evidence/TRAJECTORY_COMPARISON.json)、[奖励完整系数](evidence/REWARD_COMPARISON.json)、[控制与教师保留](evidence/CONTROL_AND_RETENTION.json)、[输入SHA索引](evidence/INPUT_INDEX.json)。所有原评测和失败保持；本报告为本次独立采用/分析记录。','', '读取过程记录：AGENTS引用的Git政策在当前稀疏工作区未落盘，已从HEAD的Git对象读取；部分脚本初次按名称查找未找到，随后按现有文件定位。持久Node REPL未能初始化，使用既有Python环境完成。以上均未改变训练/评测原件。']
(HERE/'REPORT.md').write_text('\n'.join(head)+'\n',encoding='utf8')
print(json.dumps(dict(speed_square_effective_ratio=eff_ours/eff_scut,summary=summary,rows=len(rows),report=rel(HERE/'REPORT.md'),additional_rollouts=0),ensure_ascii=False,indent=2))
