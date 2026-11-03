"""Project published diagnostics into compact facts; no checkpoint/raw/native reads."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent;out=R/'reports/ACTUAL_REPLAY_CONSISTENCY_COMPACT_FACTS_V1.json';doc=R/'ACTUAL_REPLAY_CONSISTENCY_FINDINGS_V1.md';assert not out.exists()and not doc.exists()
def compact(m):return {k:m[k]for k in ('MAE','RMSE','max_abs')}
roles={}
for role in ('E3','W35'):
 p=R/'reports'/('ACTUAL_SAVED_REPLAY_CONSISTENCY_'+role+'_V1.json');raw=p.read_bytes();v=json.loads(raw);assert v['returncode']==0;r=v['receipt'];e=r['execution'];assert r['role']==role and e['physical_checkpoint_reads']==e['checkpoint_SHA_calculations']==e['weights_only_CPU_decodes']==1 and e['mother_checkpoint_reads']==e['optimizer_instances']==e['optimizer_updates']==e['native_BPTT_updates_this_diagnostic']==0 and e['whole_root_tensor_identity_version_values_unchanged']is True and e['live_models_frozen_unchanged']is True and e['global_Torch_Python_NumPy_RNG_unchanged']is True
 q=dict(source=dict(report=str(p),bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest(),checkpoint=r['provenance']['checkpoint_path'],checkpoint_SHA256=r['provenance']['checkpoint_SHA256']),sampling=r['sampling'],one_step_state={k:compact(m)for k,m in r['one_step']['state'].items()if isinstance(m,dict)},one_step_reward={},one_step_done={},actor=r['actor'],H16={},execution=e,interpretation=r['interpretation'])
 for name in ('aux_on_true_s_and_true_s1','aux_on_true_s_and_WM_s1'):
  q['one_step_reward'][name]=r['one_step'][name]['reward'];q['one_step_done'][name]=r['one_step'][name]['done']
 for mode,m in r['H16'].items():
  if not isinstance(m,dict):q['H16'][mode]=m;continue
  z=dict(n=m['n'],horizon=m['horizon'],cumulative_original_reward=m['cumulative_original_reward'],context_reanchored_after_start=m['context_reanchored_after_start'],actual_policy_imagination_full_chain=False,steps={})
  for i in (0,7,15):
   step=m['steps'][i];a=step['aux'];project=a['effective_legacy_projected_next_context'];z['steps'][str(i+1)]=dict(state={k:compact(x)for k,x in step['state'].items()if isinstance(x,dict)},reward=a['reward'],done=a['done'],projected_context={k:compact(x)if isinstance(x,dict)else x for k,x in project.items()}if project else None)
  q['H16'][mode]=z
 roles[role]=q
value=dict(kind='ACTUAL_REPLAY_POSTHOC_CONSISTENCY_COMPACT_FACTS_V1',roles=roles,new_original_checkpoint_reads_by_this_projection=0,SDK_or_GPU_or_native_updates_by_this_projection=0,skill_or_causal_or_generalization_claim=False,mother_selection='KEEP_REGISTRY_V12_UNCHANGED',next_training_enabled=False)
out.write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def n(v):return 'null'if v is None else f'{v:.6g}'
lines=['# 已保存回放一致性诊断：真实CPU结果 V1','','这是**POSTHOC / REPLAY RESUBSTITUTION**：回放可能已参与训练，以下不是heldout、原技能通过率、泛化或因果结论。两角色各1次真实own checkpoint bytes/SHA/CPU decode；无mother重开、无optimizer/SDK/GPU/训练；全root/live值与版本、全局RNG保持。','', '沿记录action（bridge clip6 raw manager command输入，不是延迟后物理torque）比较。H16使用完整无done/cut/invalid的survivor窗口；CONDITIONAL每步true xi，FULL只起点true xi后aux+savedmask+legacy projector，无oracle重锚；两个都不是actor新动作反事实。','', '|角色|样本/actor/H16|1步位置MAE m|1步旋转MAE rad|1步关节q MAE rad|原reward样本std|真s1奖励头MAE|WM s1串联奖励MAE|', '|---|---:|---:|---:|---:|---:|---:|---:|']
for role,q in roles.items():
 s=q['one_step_state'];a=q['one_step_reward']['aux_on_true_s_and_true_s1'];b=q['one_step_reward']['aux_on_true_s_and_WM_s1'];sel=q['sampling']['selected'];lines.append('|'+role+'|'+str(len(sel['one_step']))+'/'+str(len(sel['actor']))+'/'+str(len(sel['H16']))+'|'+ '|'.join(n(x)for x in (s['root_position_m']['MAE'],s['rotation_vector_rad']['MAE'],s['joint_position_rad']['MAE'],a['actual_reward_std'],a['MAE'],b['MAE']))+'|')
for role,q in roles.items():
 a=q['one_step_reward']['aux_on_true_s_and_true_s1'];d=q['one_step_done']['aux_on_true_s_and_WM_s1'];lines+=['',f'## {role}',f'- 原reward mean={n(a["actual_reward_mean"])}、mean_abs={n(a["actual_reward_mean_abs"])}；真s1奖励头MAE/样本std={n(a["MAE_over_sample_reward_std"])}，MAE/saved reward_norm.std={n(a["MAE_over_saved_reward_norm_std"])}。',f'- one-step done正例 {d["positive_labels"]}/{d["n"]}；串联Brier={n(d["Brier"])}、ECE10={n(d["ECE10"])}。若正例0，未验证终止检测，不能凭均值低宣称calibration良好。',f'- 合法actor池{q["sampling"]["populations"]["legal_actor_history"]}、合法H16池{q["sampling"]["populations"]["legal_H16"]}；全部排除数与selected chronological keys在机器件。', '', '|模式|h|位置MAE m|旋转MAE rad|线速度MAE m/s|关节q MAE rad|原sensor16 MAE（缩放观测单位）|奖励MAE|','|---|---:|---:|---:|---:|---:|---:|---:|']
 for mode,m in q['H16'].items():
  if not isinstance(m,dict):lines.append(f'- H16：{m}');continue
  for h,v in m['steps'].items():
   s=v['state'];c=v['projected_context'];sensor=c['raw35_sensor_slots4_14_and16_22']['MAE']if c else None;lines.append('|'+('conditional'if mode=='CONDITIONAL_STATE_OPENLOOP'else'FULL')+'|'+h+'|'+ '|'.join(n(x)for x in (s['root_position_m']['MAE'],s['rotation_vector_rad']['MAE'],s['linear_velocity_target_body_frame_m_s']['MAE'],s['joint_position_rad']['MAE'],sensor,v['reward']['MAE']))+'|')
  lines.append(f'\n{mode}：H16累计原reward误差 MAE={n(m["cumulative_original_reward"]["MAE"])} / RMSE={n(m["cumulative_original_reward"]["RMSE"])}。\n')
 actor=q['actor'];lines+=['- 当前deterministic mean在合法原raw35 history10上的六分量scaled residual RMS（非记录探索action误差）：`'+json.dumps(actor['residual_preclip_scaled']['RMS'])+'`。','- actor−clipped teacher六分量max_abs：`'+json.dumps(actor['actor_minus_clipped_teacher']['max_abs'])+'`；actor clip saturation：`'+json.dumps(actor['clip_saturation_per_component'])+'`。']
lines+=['', '## 决策边界','', '不把本表误差直接变成原技能分数或真实失败根因。继续保持Registry_v12母本/H1/原物理fullDR/原接受阈值，尚未因本诊断启用任何新训练/奖励/动作映射。下一个因素须依据这些真实一致性事实设计并独立冻结复测，不为更新数量盲目续训。','', '[完整压缩机器事实](<reports/ACTUAL_REPLAY_CONSISTENCY_COMPACT_FACTS_V1.json>)含source/provenance、自然done分布、全部sample/exclusion、h=1/8/16面板及不变性。原两角色完整诊断保留所有h=1..16结果。']
doc.write_text('\n'.join(lines)+'\n',encoding='utf-8');print(doc);print(out)
