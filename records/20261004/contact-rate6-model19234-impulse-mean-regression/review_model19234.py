"""Review existing completed auto0064, keeping all gate versions and failures."""
import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone,timedelta
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from contact_gate import assess,VERSION
R=D/'continuation_receipts/production';read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=read(R/'auto_0064_contact_assessment_cap6_white_v2_rate.json');flat=read(R/'auto_0064_contact_assessment_cap6_white_v2_flat.json');v=read(R/'auto_0064_contact_assessment_cap6_white_v2_decision.json');h=read(D/'HEALTH_USER_RATE6_DATA_20261004.json')
a=assess(r);assert a==v['loaded_contact_assessment']
prior=read(D/'latest6_20261002_white_v2.json')
assert r['seed']==prior['seed']==20261002 and r['profile']==prior['profile']=='white_v2'
paired=all(r[k]==prior[k] for k in ('reset_joint_pos_before_physics','reset_root_before_physics'))
assert paired and r['probe_sha256']==prior['probe_sha256']
assert r['substep_contact_readback']['callbacks']==30000 and all(row[w]==29000 for row in r['substep_contact_readback']['per_environment']['valid_ticks'] for w in (0,1))
assert v['continue_current_rate'] and not v['current_rate_skill_pass'] and not a['pass_'] and not a['severe_individual_veto']
assert v['checkpoint']['iteration_stored']==19234 and v['checkpoint']['sha256']=='6ff344c7d4925125aaa7dee2cdccb624c215453be959065c03841d6ff7a47a92'
assert h['checkpoint']['finite_tensors']==68 and h['run_manifest']['start_iteration']==19234 and h['run_manifest']['env']['RM_KEEP_STD']=='1'
assert h['continuation_state']['consecutive']==0 and h['continuation_state']['failed_blocks']==1
cp=r['substep_contact_readback']['per_environment'];pe=r['per_environment'];groups=[]
for g in r['groups']:
 ids=[i for i,x in enumerate(r['group_ids']) if x==g['group_id']];gate=next(x for x in a['groups'] if x['group_id']==g['group_id'])
 groups.append(dict(group_id=g['group_id'],vx=g['vx'],wz=g['wz'],profile=g['profile'],passing=gate['passing'],count=gate['count'],yaw_mean=g['means']['yaw_rate'],
  worst={**{k:max(pe[k][i] for i in ids) for k in ('peak_tilt','height_error','spin_translation_speed','maximum_gap_m','longest_both_low_s','left_slip','right_slip')},
  **{k:max(cp[k][i][w] for i in ids for w in (0,1)) for k in ('loaded_time_mean_tangent_speed','loaded_impulse_weighted_tangent_speed','longest_loaded_over015_s','positive_force_point_peak_speed')}}))
bad=[]
for item in a['individual']:
 if not item['pass_']:
  i=item['env'];bad.append(dict(**item,loaded_time_m_s=cp['loaded_time_mean_tangent_speed'][i],loaded_impulse_m_s=cp['loaded_impulse_weighted_tangent_speed'][i],longest_excess_s=cp['longest_loaded_over015_s'][i],
                            control={k:pe[k][i] for k in pe},contact={k:cp[k][i] for k in cp}))
x=dict(checkpoint=v['checkpoint'],gate_version=VERSION,original_spin_skill_pass=r['spin_skill_pass'],legacy_spin_skill_pass=r['spin_skill_pass_legacy_reference'],contact_spin_skill_pass=a['pass_'],
       original_flat_pass=v['original_flat_admission']['eligible_for_mild_dr_trial'],original_flat_trained_count=64,legacy_strict_window=v['original_flat_admission']['legacy_strict_pass_window'],
       physical_smoke_pass=r['physical_smoke_pass'],survived=sum(r['alive']),num_envs=len(r['alive']),seconds=r['seconds'],groups=groups,failure_samples=bad,severe_individual_veto=a['severe_individual_veto'],
       full_initial_root_q_exact_with19078=paired,probe_sha_same_with19078=True,initial_actual_parameters=r['initial_parameter_audit']['actual_parameters_pass'],final_actual_parameters=r['final_parameter_audit']['actual_parameters_pass'],
       closure_mm=r['max_closure_m']*1000,mimic_rad=r['max_mimic_rad'],source_weight_changed_not_isolated_reward_or_physics_causality=True,
       actual_training_checkpoint=h['checkpoint'],actual_parent=h['parent'],actual_guardian=h['guardian'],actual_trainer=h['processes']['training'],actual_run=h['run'],next_deadline_epoch=h['status']['trainer_deadline_epoch'],
       source_counts=h['source_counts'],budget=h['budget'],consecutive=0,failed_blocks=1,no_probe_PPO_settlement_or_configuration_mutation=True,
       evidence_sha={p.name:sha(p) for p in (R/'auto_0064_contact_assessment_cap6_white_v2_flat.json',R/'auto_0064_contact_assessment_cap6_white_v2_rate.json',R/'auto_0064_contact_assessment_cap6_white_v2_decision.json')})
(D/'MODEL19234_CONTACT_REVIEW.json').write_text(json.dumps(x,indent=2),encoding='utf8')
p,n=[g for g in groups if g['profile']=='spin' and abs(g['wz'])==6]
deadline=datetime.fromtimestamp(x['next_deadline_epoch'],timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
note=f'''# model19234：6档首45分钟后，承重冲量均速边界回归未过

最新已回放策略19234 SHA{x['checkpoint']['sha256']}，原auto0064的80env站跑与88env自转各15秒已完成。原站跑64个已训练环境全部准入通过，旧strict_window=false保留。自转88/88存活、原physical_smoke=true、初末实际参数读回通过，但新contact技能false，原全时网格和legacy技能亦false，三种布尔完整保留。

正转+6实测均{p['yaw_mean']:.6f}rad/s，新承重门槛6/8=75%，低于原80%组门槛。仅env40与73右轮冲量加权切向均速分别{cp['loaded_impulse_weighted_tangent_speed'][40][1]:.9f}和{cp['loaded_impulse_weighted_tangent_speed'][73][1]:.9f}m/s，超过.15；其余验收项通过。对应承重时间均速.136927/.134765m/s、持续超限3.5/3ms均过，因此不能把两种加权均值混用来毕业。未改数值或测量版本。

反转-6实测均{n['yaw_mean']:.6f}rad/s，新门槛8/8。最坏冲量均速{n['worst']['loaded_impulse_weighted_tangent_speed']:.9f}m/s，距离.15余量很小，不能只报正转的失败或宣称持久成熟。其余9组（站跑、低速、自转启停反向）各8/8，总共10组8/8，正6单组6/8；没有严重个体额外否决。

纯±6最坏峰倾角{max(p['worst']['peak_tilt'],n['worst']['peak_tilt']):.6f}deg、每环境平均XY速度{max(p['worst']['spin_translation_speed'],n['worst']['spin_translation_speed']):.6f}m/s<.12、控制网格gap{1000*max(p['worst']['maximum_gap_m'],n['worst']['maximum_gap_m']):.6f}mm、最长双轮低载{1000*max(p['worst']['longest_both_low_s'],n['worst']['longest_both_low_s']):.3f}ms、closure{x['closure_mm']:.6f}mm/mimic{x['mimic_rad']:.6f}rad。纯正转有力报告点峰值仍.788087m/s，时间/冲量均值不代表瞬时峰或真实材料点/实车认证。

与先前19078同seed20261002、white_v2、同probe SHA及完整初始root/q精确相同。权重不同，不能归因为生产物理变化或新滚动奖励单独因果。新测量规则正确检查到边界回归，不能把校准19078通过当作新19234也通过，不能挑选旧权重覆盖失败。

新CONTACT_CONTINUATION_STATE consecutive0/failed_blocks1，父按已有有界流程继续6/white_v2/rolling_v1，尚未开展成熟配对或8档预检。当前唯一trainer{x['actual_trainer']['pid']}/start{x['actual_trainer']['start_ticks']}从19234完整恢复；实际run{x['actual_run']}，自身保存19250 SHA{x['actual_training_checkpoint']['sha256']} CPU68浮点完整有限。19250尚未15秒回放，源104/候选130指纹一致。下一最长2小时段约北京时间{deadline}保存后已有顺序验收，勿重复probe或热改trainer。

此前条件性16:10–16:30升8估计因本轮未过已不成立。必须重新积累不同正式策略通过并完成新权重双seed nominal/white配对；若三个连续失败或旧能力/物理退化则回真实paired17196/5并hold保存预算。不调整.15、15.01ms或奖励/DR/硬件/物理/PPO来解释本次失败。

唯一252000秒/三授权扩展保持，核验余{x['budget']['remaining_training_seconds']:.2f}秒只是快照，主PPO活跃继续合法记账。本轮仅读取既有报告、逐环境审查、完整CPU/来源核验与归档，没有新probe/PPO、暂停重启或预算/配置修改。旧原门槛与报告及17773反例仍保留，6未持续成熟、8/120rpm未达到。
'''
(D/'MODEL19234_CONTACT_REPORT.md').write_text(note,encoding='utf8')
print(json.dumps(dict(groups=[dict(group_id=g['group_id'],passing=g['passing'],yaw=g['yaw_mean'],worst=g['worst']) for g in (p,n)],failure_samples=[dict(env=i['env'],reasons=i['reasons'],loaded_impulse=i['loaded_impulse_m_s']) for i in bad],next_deadline_Beijing=deadline,contact_gate=False,continue6=True),indent=2))
