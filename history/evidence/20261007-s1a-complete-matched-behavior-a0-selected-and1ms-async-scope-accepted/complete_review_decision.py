from pathlib import Path
import json,hashlib,time
D=Path(__file__).resolve().parent;R=D/'reports'
v=json.loads((R/'S1A_ALL_MATCHED_BEHAVIOR_REVIEW.json').read_text());n=v['hosts']['native'];w=v['hosts']['windows']
assert n['A0']['world']['target_count']==64 and w['A0']['world']['target_count']==63
assert all(n[k]['world']['target_count']<64 and w[k]['world']['target_count']<63 for k in ('A1','A2'))
assert all(x['root_exact'] and x['q_exact'] and x['parameters_exact'] for x in v['pairing'])
decision=dict(epoch=time.time(),plan_id='MOD4-MOE-PLAN-001',version='1.5',plan_sha256='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b',selected_architecture='A0',
 selected_source=dict(path='/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/logs/2026-10-07_06-19-42_auto_0411_moe_S1A_A0_clock1000_recovery_learning_cap12.5664_white_v3/model_23783.pt',sha256='9eb36866f29fd223b2c41ebf4829a9847ef8842a9f6e7dc6105e93656fdfe3c8'),
 reason='Keep A0 under the approved no-practical-benefit fallback. A1 improved straight velocity error but both historical candidates degraded complete-cycle world cross tracking consistently on both hosts. No benefit claim from parameter count, reward or save success.',
 first_development_seed_white3_only=True,world_strict_native=True,world_strict_windows=False,windows_A0_remaining_failure=dict(target_count=63,total=64,worst_abs_cross_m_s=w['A0']['world']['max_abs_cross']),
 architecture_causality_isolated=False,optimizer_restore_vs_fresh_confound_retained=True,all_candidates_preserved=True,new_mechanical_percentage_gate=False,history_rejected_for_this_round_not_permanently=True,
 next_stage='S2 E0 D1+D2 raw observation noise and episode four-leg encoder bias; separate immutable branch, real SDK and new-scope PPO before formal45min',S1A_used_seconds=10783.433714389801,S1A_cap_seconds=21600,new_budget_seconds=0)
platform=dict(epoch=time.time(),accepted_functional_scope=True,scope='Immutable219 package;1ms/100Hz/white_v3/seed20261002/A0-A1-A2 frozen flat80/spin88/world88 x15s plus two3s SDK cases; new parameter ranges require own review',
 exact_initial_root_q_and_parameters=True,all24_full_native_windows_cases_v4_pass=True,anchor=v['platform'],matched_per_host_comparisons_required=True,dynamic_bit_exact=False,hardware_independent_target_counts=False,
 all14_uploaded_results_byte_verified=True,windows_wall=v['windows_cost'],no_canonical_write_or_production_authority=True)
(R/'S1A_ARCHITECTURE_SELECTION.json').write_text(json.dumps(decision,indent=2))
(R/'CLOCK1000_CROSS_HOST_FUNCTIONAL_CLOSEOUT.json').write_text(json.dumps(platform,indent=2))
lines=['# S1A 同量架构与1ms双机比较实际审查','', '三套各275实际更新、132M环境策略步。全部任务/模型/数据准入通过；每个条件的完整root/q和实际参数精确配对。仅开发seed20261002、white_v3，不是最终保留seed或全课程毕业。','', '| 主机 | 架构 | 完整圈方向目标 | 最大绝对净横漂 m/s | −1.5/+1.5直线误差 m/s | 正反4π |','|---|---|---:|---:|---|---|']
for host in ('native','windows'):
 for k in ('anchor','A0','A1','A2'):
  f=v['hosts'][host][k];g=[x['error'] for x in f['flat']['constant_speed'] if abs(x['command'])==1.5]
  lines.append(f"| {host} | {k} | {f['world']['target_count']}/64 | {f['world']['max_abs_cross']:.9f} | {g[0]:.6f}/{g[1]:.6f} | {sum(x['passed'] for x in f['spin']['pure4pi'])}/16 |")
lines+=['','选择A0继续E0共同DR。A1直线更准，但方向漂移的综合代价超过其收益；A2也没有保留方向优势。历史结构保留，未来可独立重新验证，不能从本轮推导历史网络永远无用。A0在3060有一个轻微cross边界失败，strict=false原样保留。A0恢复原optimizer、新结构freshoptimizer的差异保留，不声称纯架构因果。','',f"3060十四个实际进程累计{v['windows_cost']['physics_wall_total_s']/60:.3f}分钟，传输{v['windows_cost']['transfer_total_s']:.3f}秒，2秒采样显存峰{v['windows_cost']['sampled_peak_mib']:.0f}MiB。采样峰不是连续峰。锚点跨GPU最大完整圈netcross差{v['platform'][2]['max_net_cross_platform_difference']:.9f}m/s；不承诺动态bit-exact或硬件无关达成率。",'', '全部14份回传JSON已与3060原文件逐字核实；原始flags、逐圈、全窗口和失败前样本原样保留。首次本机离线读者错把3s SDK匹配到15s同后缀case，按immutable job类型修正后重新完整计算；没有新仿真、PPO或账本操作。']
(R/'S1A_MATCHED_SELECTION_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
print(json.dumps(dict(selected='A0',scope_accepted=True,S2_preparation_required=True)))
