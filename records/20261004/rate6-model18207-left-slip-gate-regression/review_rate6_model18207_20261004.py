"""Review an existing gate regression; no simulator, training or gate edits."""
import json
from datetime import datetime,timezone,timedelta
from pathlib import Path
D=Path(__file__).resolve().parent
read=lambda n:json.loads((D/n).read_text(encoding='utf8'))
r=read('auto_0053_assessment_cap6_white_v2_rate.json');old=read('auto_0051_assessment_cap6_white_v2_rate.json')
dec=read('auto_0053_assessment_cap6_white_v2_decision.json')
assert r['physical_smoke_pass'] and not r['spin_skill_pass'] and r['spin_skill_pass_legacy_reference']
assert all(r['alive']) and len(r['alive'])==88 and not r['nonfinite']
assert dec['original_flat_admission']['eligible_for_mild_dr_trial'] and all(g['physical_admission_fraction']==1 for g in dec['original_flat_admission']['groups'])
assert all(r[k]==old[k] for k in ['reset_root_before_physics','reset_joint_pos_before_physics','group_ids','probe_sha256','seed','profile'])
assert r['initial_parameter_audit']['actual_parameters_pass'] and r['final_parameter_audit']['actual_parameters_pass']
p=r['per_environment'];failed=[];rows=[]
for g in r['groups']:
 ids=[i for i,v in enumerate(r['group_ids']) if v==g['group_id']]
 count=0
 for i in ids:
  bad=[]
  limits={'peak_tilt':12,'tilt':8,'height_error':.03,'left_slip':.15,'right_slip':.15,'delta':.18,'d2':.25,'maximum_gap_m':.002,'longest_both_low_s':.01501,'guide_force':1,'base_force':1,'wheel_rating_clip':.2,'leg_rating_clip':.2}
  for k,v in limits.items():
   if p[k][i]>v:bad.append(k)
  for k in ['left_fz','right_fz']:
   if p[k][i]<10:bad.append(k)
  if not r['alive'][i]:bad.append('survival')
  if p['yaw_error'][i]>max(.2,.2*abs(g['wz'])):bad.append('yaw_error')
  if p['speed_error'][i]>max(.12,.25*abs(g['vx'])):bad.append('speed_error')
  if g['wz']!=0 and p['spin_translation_speed'][i]>.12:bad.append('spin_translation_speed')
  if g['profile']=='spin_ramp_stop_reverse' and p['stop_yaw_abs'][i]>.2:bad.append('stop_yaw_abs')
  if bad:failed.append(dict(environment=i,group_id=g['group_id'],reasons=bad,values={k:p[k][i] for k in bad if k in p}))
  else:count+=1
 assert abs(count/len(ids)-g['spin_skill_fraction'])<1e-6
 rows.append(dict(group_id=g['group_id'],profile=g['profile'],yaw_command=g['wz'],count=len(ids),skill_count=count,legacy_fraction=g['spin_skill_fraction_legacy_reference']))
assert len(failed)==5 and all(f['reasons'] in [['left_slip'],['right_slip']] for f in failed)
health=read('HEALTH_20261004_1100.json');runtime=read('RUNTIME_ACTUAL.json')
saved=read('HEALTH_20261004_0900.json')['checkpoint']
assert saved['sha256']==dec['checkpoint']['sha256'] and saved['finite_tensors']==68
assert health['consecutive']==0 and health['failed_blocks']==1
pure=[i for i,g in enumerate(r['group_ids']) if g in [7,8]]
metrics=dict(positive_yaw_mean=r['groups'][7]['means']['yaw_rate'],negative_yaw_mean=r['groups'][8]['means']['yaw_rate'],
 pure_peak_tilt_deg=max(p['peak_tilt'][i] for i in pure),pure_gap_m=max(p['maximum_gap_m'][i] for i in pure),
 pure_both_low_s=max(p['longest_both_low_s'][i] for i in pure),closure_m=r['max_closure_m'],mimic_rad=r['max_mimic_rad'])
review=dict(checkpoint=dec['checkpoint'],physical_pass=True,original_skill_pass=False,legacy_skill_pass=True,survived=88,
 flat_trained64_all_original_admission=True,strict_window_retained=False,initial_final_parameter_readbacks=True,
 same17773_seed_profile_probe_initial_root_q=True,rows=rows,failed_environments=failed,metrics=metrics,
 consecutive=0,failed_blocks=1,source_cpu_verified=saved,current_health=health,
 no_new_probe_PPO_budget_config_restart_or_gate_change=True)
(D/'RATE6_MODEL18207_REVIEW.json').write_text(json.dumps(review,indent=2),encoding='utf8')
deadline=datetime.fromtimestamp(runtime['status']['trainer_deadline_epoch'],timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
note=f'''# 6档18207：原滑移门控回归未过，保留先前17773通过

auto0053原定平地80env与自转88env各15秒已经完成。源18207 SHA{dec['checkpoint']['sha256']}在前次自然冻结窗口已独立CPU读取68浮点完整有限；原flat的64已训练环境全部准入通过，旧strict_window=false。rate88/88存活、物理通过、初末实际参数读回通过，但corrected spin_skill=false，legacy_reference spin_skill=true，两种布尔均保留。

交错group_ids逐环境核查只有5个样本因原滑移代理失败：纯+6环境18右轮0.156309m/s>.15，该组仍7/8=87.5%达到原80%组门槛；纯-6环境8、30、41、63左轮分别0.153222、0.150462、0.152507、0.152752>.15，该组4/8=50%而未过。其余9组各8/8通过。所有失败样本的其他原验收项通过；没有NaN、死亡或物理/成熟站跑退化，不能把门控失败说成训练崩溃。

纯±6实测均{metrics['positive_yaw_mean']:.6f}/{metrics['negative_yaw_mean']:.6f}rad/s；最坏peaktilt{metrics['pure_peak_tilt_deg']:.6f}deg、gap{metrics['pure_gap_m']*1000:.6f}mm、双轮低载{metrics['pure_both_low_s']*1000:.3f}ms，closure{metrics['closure_m']*1000:.6f}mm/mimic{metrics['mimic_rad']:.6f}rad。与17773同seed20261002、white_v2、probe源及完整初始root/q精确相同，权重不同。先前17773的完整单seed通过保留，本次表明6尚不持续达标，不宣称新奖励普遍因果、PhysX材料点滑移或实车认证。原正确link参考点没有改动；不切换到legacy布尔宣布毕业，也不放宽.15。

专项consecutive清零、failed_blocks=1，监督器阻止升8并继续已安排的有界6学习。核验时单一trainer3743137/start23085130从18207完整续训，run logs/2026-10-04_09-04-02_auto_0054_rolling_rate_trial_or_continued_cap6_white_v2，parent3238128/guardian3238171实际身份正常，white_v2/rolling v1固定。最新PID绑定18625 SHA{health['checkpoint']['sha256']}已CPU回读68浮点有限、104原源/123候选源一致；此18625没有15秒回放，不能用训练日志reward或success宣布成熟。GPU69%/14562MiB/49C是快照，近期日志无NaN/Traceback/OOM。

本段deadline约北京时间{deadline}，核验时临近边界，随后已有自动完整保存与顺序flat/rate；实际子进程和状态可已自然转入评测，勿因cachedPID退出而重启/再发probe。3连续技能失败或旧能力/物理退化保留所有新权重、回实际paired17196/5并hold。另一份策略通过和同候选双seed名义/DR全部原门槛通过前不升8。当前尚有预算，不能把hold或冻结评测当finished。

唯一252000有效PPO秒及三扩展保持，核验余{health['remaining_effective_s']:.2f}秒约13小时41分为快照，实时扣active尾段。本轮只读取既有报告、CPU与来源/GPU核验和归档，没有新probe/PPO、暂停重启、物理/奖励/DR/门槛或预算改变。当前原地spin优先，移动/FPS/地形延期，120rpm仍目标。
'''
(D/'RATE6_MODEL18207_REPORT.md').write_text(note,encoding='utf8')
print(json.dumps(dict(corrected=False,legacy=True,rows=rows,failures=failed,metrics=metrics),ensure_ascii=False))
