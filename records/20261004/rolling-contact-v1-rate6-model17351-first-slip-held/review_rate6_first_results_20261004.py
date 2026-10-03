"""Review existing paired5 and first6 artifacts; never changes gates or training."""
import json
from datetime import datetime,timezone,timedelta
from pathlib import Path
D=Path(__file__).resolve().parent
read=lambda n:json.loads((D/n).read_text(encoding='utf8'))
paired=read('auto_0043_rolling_adaptation5_multiseed_cap5_white_v2_paired_decision.json')
assert paired['pass'] and all(p['initial_root_q_exact'] and all(p['original_plus_individual_safety_gates']) and all(p['actual_parameter_readbacks']) for p in paired['pairs'])
raws=sorted(D.glob('auto_0043_*_flat_*.json'))+sorted(D.glob('auto_0043_*_spin_*.json'))
assert len(raws)==8
reward=read('ROLLING_REWARD_ACCEPTED.json')
assert reward['accepted']['sha256']==paired['checkpoint']['sha256']
rate=read('auto_0049_assessment_cap6_white_v2_rate.json')
flat=read('auto_0049_assessment_cap6_white_v2_flat.json')
decision=read('auto_0049_assessment_cap6_white_v2_decision.json')
old=json.loads((D.parent/'MOD4_RATE6_SLIP_REPAIR_20261003/MATURE5_RATE6_model17039_rate6_white_v2_20261002_1500steps.json').read_text(encoding='utf8'))
assert all(rate[k]==old[k] for k in ['reset_root_before_physics','reset_joint_pos_before_physics','group_ids'])
assert rate['probe_sha256']==old['probe_sha256'] and rate['seed']==old['seed'] and rate['profile']==old['profile']
p=rate['per_environment'];rows=[];failures=[]
for g in rate['groups']:
 ids=[i for i,v in enumerate(rate['group_ids']) if v==g['group_id']]
 for i in ids:
  bad=[]
  upper={'peak_tilt':12,'tilt':8,'height_error':.03,'left_slip':.15,'right_slip':.15,'delta':.18,'d2':.25,'maximum_gap_m':.002,'longest_both_low_s':.01501,'guide_force':1,'base_force':1,'wheel_rating_clip':.2,'leg_rating_clip':.2}
  for k,t in upper.items():
   if p[k][i]>t:bad.append(k)
  for k in ['left_fz','right_fz']:
   if p[k][i]<10:bad.append(k)
  if not rate['alive'][i]:bad.append('survival')
  if p['yaw_error'][i]>max(.2,.2*abs(g['wz'])):bad.append('yaw_error')
  if p['speed_error'][i]>max(.12,.25*abs(g['vx'])):bad.append('speed_error')
  if g['wz']!=0 and p['spin_translation_speed'][i]>.12:bad.append('spin_translation_speed')
  if g['profile']=='spin_ramp_stop_reverse' and p['stop_yaw_abs'][i]>.2:bad.append('stop_yaw_abs')
  if bad:failures.append(dict(environment=i,group_id=g['group_id'],reasons=bad,values={k:p[k][i] for k in bad if k in p}))
  else:pass
 count=len(ids)-sum(f['group_id']==g['group_id'] for f in failures)
 assert abs(count/len(ids)-g['spin_skill_fraction'])<1e-6
 rows.append(dict(group_id=g['group_id'],vx=g['vx'],wz=g['wz'],profile=g['profile'],environments=len(ids),skill_count=count,
  yaw_mean=g['means']['yaw_rate'],left_slip_range=[min(p['left_slip'][i] for i in ids),max(p['left_slip'][i] for i in ids)],
  right_slip_range=[min(p['right_slip'][i] for i in ids),max(p['right_slip'][i] for i in ids)],
  peak_tilt_max=max(p['peak_tilt'][i] for i in ids),gap_max_m=max(p['maximum_gap_m'][i] for i in ids),
  both_low_max_s=max(p['longest_both_low_s'][i] for i in ids)))
assert len(failures)==14 and all(f['reasons'] in [['left_slip'],['right_slip']] for f in failures)
ids=[i for i,g in enumerate(rate['group_ids']) if g==7]
oldvals=[old['per_environment']['right_slip'][i] for i in ids];newvals=[p['right_slip'][i] for i in ids]
runtime=read('RATE6_FIRST_ACTUAL_VERIFIED.json')
state=read('REPAIR_STATE.json')
status=read('RUNTIME_ACTUAL.json')['status']
review=dict(reward_adaptation_accepted=True,paired_reward_checkpoint=reward['accepted'],paired5_eight_reports=8,
 paired5_initial_root_q_exact=True,rate_checkpoint=decision['checkpoint'],rate_survived=sum(rate['alive']),rate_environments=len(rate['alive']),
 original_skill_pass=rate['spin_skill_pass'],legacy_reference_skill_pass=rate['spin_skill_pass_legacy_reference'],physical_pass=rate['physical_smoke_pass'],
 original_flat_admission=decision['original_flat_admission']['eligible_for_mild_dr_trial'],flat_strict_window=decision['original_flat_admission']['legacy_strict_pass_window'],
 rows=rows,failed_environments=failures,prior17039_same_seed_profile_probe_initial_root_q=True,
 positive_right_proxy_old=dict(min=min(oldvals),max=max(oldvals),mean=sum(oldvals)/len(oldvals)),
 positive_right_proxy_new=dict(min=min(newvals),max=max(newvals),mean=sum(newvals)/len(newvals)),
 comparison_is_training_progress_not_isolated_reward_causality=True,mesh_proxy_not_PhysX_material_contact=True,
 current_phase=state['phase'],failed_blocks=state['failed_blocks'],consecutive=state['consecutive'],
 current_actual_verification=runtime,next_segment_deadline=status['trainer_deadline_epoch'],
 no_new_probe_PPO_budget_or_production_mutation=True)
(D/'RATE6_FIRST_ASSESSMENT_REVIEW.json').write_text(json.dumps(review,indent=2),encoding='utf8')
deadline=datetime.fromtimestamp(status['trainer_deadline_epoch'],timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
note=f'''# 滚动专项通过5回归并接续6档：首轮仍受滑移门控

固定5rad/s的新奖励适应已在正式17196完整保存后完成。两个seed20261002/3、nominal/white_v2各flat/spin共8份15秒原验收和严重个体否决全部通过，4对完整初始root/q严格相同，实际参数初末读回通过。ROLLING_REWARD_ACCEPTED保存精确源和接受权重，17196 SHA{reward['accepted']['sha256']}；这证明5旧能力回归，不是6或实车认证。

6独立预检已完成：短物理通过；20k1.2秒20000存活、无NaN，闭链0.175360mm/mimic0.001953rad，峰tilt13.188068deg。原combined=false及66.866010mm短高差警告保留。128环境2轮PPO通过、17197预检权重弃用且计同一账本；正式从17196完整actor/critic/optimizer/std/iter续训，未混入预检权重。

首45分钟6正式策略17351 SHA{decision['checkpoint']['sha256']}已经完整保存并完成auto0049既有顺序80env平地与88env自转15秒回放。平地64个已训练环境原准入全部通过；旧strict_window=false。自转88/88存活，原物理通过，但original/legacy整体spin_skill均false。纯+6组技能0/8，仅右轮每环境平均网格滑移代理0.180209–0.188529m/s>原.15；纯-6组技能2/8，6个样本仅左轮0.150173–0.158115>原.15（正确参考点，legacy该组8/8保留）。其余9组各8/8。纯正/反实际yaw均+5.940998/-5.902078rad/s；纯±6最坏峰tilt2.508738deg、gap0.703670mm、双轮低载11.5ms，闭链0.096223mm/mimic0.001691rad。

与先前17039同seed/profile/probe源及完整初始root/q完全相同，+6右轮代理区间0.202977–0.213584变为0.180209–0.188529，均值{sum(oldvals)/len(oldvals):.6f}→{sum(newvals)/len(newvals):.6f}。策略权重、奖励适应与6训练均发生变化，不能把下降当隔离奖励因果或6毕业。反转6也须解决；不只报正转变好。全时网格代理不是PhysX接触材料点，平均不是瞬时峰。

专项REPAIR_STATE consecutive=0/failed_blocks=1，原门控禁止升8，继续有界6专项学习。当前唯一trainer3417091/start21564559，从正式17351完整恢复，run logs/2026-10-04_04-50-37_auto_0050_rolling_rate_trial_or_continued_cap6_white_v2；parent3238128/guardian3238171身份正确，candidate rolling v1/cap6/white_v2/KEEP_STD1实际manifest核实。最新本次PID绑定17375 SHA{runtime['checkpoint']['sha256']}已CPU回读68浮点完整有限；104原源及123候选源一致，GPU92%/15214MiB/47C只是快照。新17375尚无确定性15秒验收。

当前段截止约北京时间{deadline}，随后监督器已有顺序flat/rate回放，勿发重复probe。两份不同正式策略通过后才同候选双seed名义/DR配对并决定6→8→10→4π。第三连续技能失败或旧能力/物理退化则保留所有新权重、回实际paired成熟17196/5并hold，不无限叠失败档。当前6是已开训，不是已修好；120rpm仍目标。

预算唯一252000秒、三扩展均原授权一次。本轮核验余{runtime['remaining_effective_s']:.2f}秒约19小时31分为快照，实时扣active段；没有新增预算/探针/PPO、重启、改奖励DR硬件门槛或结账。只读取既有报告、CPU和来源核验及归档。一次只读检查遇到新trainer尚无自身完整receipt，未触碰生产；读取器明确区分pending与PID绑定正式保存，随后已读回17375完整receipt。
'''
(D/'RATE6_FIRST_ASSESSMENT_REPORT.md').write_text(note,encoding='utf8')
print(json.dumps(dict(pair5_pass=True,rate6_survived=88,skill_pass=False,failures=len(failures),positive_slip=review['positive_right_proxy_new'],negative_skill=rows[8]['skill_count'],next_deadline=deadline),ensure_ascii=False))
