"""Record completed student results, all full checkpoints, native retention and decision."""
from pathlib import Path
import json,time,hashlib
import torch
T=Path(__file__).resolve().parent;R=T.parents[2];B=T.parent
selected=json.loads((T/'weights/SELECTED_STUDENT.json').read_text());plan=json.loads((T/'PLAN.json').read_text());final=json.loads((T/'evidence/training/FINAL.json').read_text());post=json.loads((T/'evidence/post_native/COMPLETE.json').read_text());assert post['all_closed']
rank=json.loads((T/'evidence/STUDENT_FIXED_RANKING.json').read_text());parent=json.loads((T/'evidence/baseline_reference/FLAT60.json').read_text());stair_native=json.loads((T/'evidence/post_native/stairs/RESULT.json').read_text())
assert stair_native['models']['student']==selected['sha256'] and stair_native['models']['parent']==plan['parent_sha256']
def flat_metrics(j):
 out={}
 for task in ['forward20','forward22','reverse15','yaw14137','height020','height040']:
  rr=[r for r in j['rows'] if r['task']==task]
  out[task]=dict(passed=sum(r['passed'] for r in rr),requested=len(rr),vx_mean=sum(r['vx_mean'] for r in rr)/len(rr),vx_MAE=sum(r['vx_abs_error'] for r in rr)/len(rr),wz_mean=sum(r['wz_mean'] for r in rr)/len(rr),wz_MAE=sum(r['wz_abs_error'] for r in rr)/len(rr),height_mean=sum(r['height_mean'] for r in rr)/len(rr))
 return out
chosen_dir=T/'evidence/checkpoint_evals'/Path(selected['source_file']).stem;newflat=json.loads((chosen_dir/'flat60/RESULT.json').read_text());flat=dict(parent=flat_metrics(parent),student=flat_metrics(newflat))
retained={}
for skill in ['traverse','gyro','landing']:
 result=json.loads((T/'evidence/post_native'/('retained_'+skill)/'RESULT.json').read_text());assert result['input_sha256']['student']==selected['sha256'];agg={}
 for row in result['rows']:
  key=(row['model'],row['variant']);a=agg.setdefault(key,dict(requested=0,passed=0,samples=0,error_sum=0.))
  a['requested']+=row['requested']
  if skill=='traverse':a['passed']+=row['crossed_count']
  elif skill=='gyro':
   g=row['gyro_metrics'];a['passed']+=g['first_episode_survived6s'];a['samples']+=g['prepush_first_episode_samples'];a['error_sum']+=(g['prepush_first_episode_wz_MAE'] or 0.)*g['prepush_first_episode_samples']
  else:a['passed']+=row['landing_metrics']['command_recovered']
 retained[skill]=[dict(model=k[0],variant=k[1],**v,wz_MAE=v['error_sum']/v['samples'] if v['samples'] else None) for k,v in agg.items()]
last=final['last_progress'];teacher_meta=json.loads((T/'evidence/TEACHER_DATA_ADMISSION.json').read_text())
decision=dict(status='complete bounded student experiment; original comprehensive parent still frozen',actual_training_seconds=final['elapsed_seconds'],selected=selected,parent_sha256=plan['parent_sha256'],specialist_teacher_sha256=plan['teacher_retention']['stair_teacher_sha256'],teacher_data_sha256=plan['teacher_retention']['dataset_sha256'],flat_fixed=flat,native_stairs=stair_native['summaries'],retained_original_Rough_v1_L9=retained,numerical=last['done_totals'],frozen_parent_untouched=True,automatic_deployment_promotion=False,fullDR_stair_graduation_claim=False)
(T/'DECISION.json').write_text(json.dumps(decision,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
lines=['# 冻结上台阶教师指导综合父模型：完成报告（2026-11-13）','',f"实际PPO {final['elapsed_seconds']:.3f}秒；2048环境，819台阶/717原rough/512平地；每5分钟完整检查点与固定回放。原综合父db6e9ccf和独立教师715c40b6均完整冻结，学生从父初始化。",'',f"本轮固定任务实验候选：**{selected['model_id']}**，完整PT `weights/selected_specialist_student.pt`，SHA256 `{selected['sha256']}`。这是实验选优；原父模型保留，未自动晋升部署。",'','## 同口径名义MuJoCo结果','','| 保存点 | 平地/60 | 正向两阶/5 | 真正斜向两阶/20 | 下阶/5 | 前进MAE(m/s) |','|---|---:|---:|---:|---:|---:|','| 冻结父 |60|4|0|5|0.076371|']
for row in sorted(rank,key=lambda x:x['source_file']):lines.append(f"| {row['source_file']} |{row['flat60_passed']}|{row['straight_passed']}|{row['actual_oblique_passed']}|{row['descent_passed']}|{row['forward_MAE_m_s']:.6f}|")
lines+=['','速度/高度用原六任务、原初态与容差。斜向为±15°/±30°各5初态，实际第一阶立面触阶仍至少10°且连续完成两阶；不把初态斜向随后转正的成功算斜向。正向与下阶沿用原协议。原父既有结果均先验证完整权重SHA相同后引用，未为凑基线重跑。','','## 所选候选的原技能与速度','','| 任务 | 父通过/10 | 学生通过/10 | 父平均vx | 学生平均vx | 父wzMAE | 学生wzMAE |','|---|---:|---:|---:|---:|---:|---:|']
for task,a in flat['parent'].items():
 b=flat['student'][task];lines.append(f"|{task}|{a['passed']}|{b['passed']}|{a['vx_mean']:.5f}|{b['vx_mean']:.5f}|{a['wz_MAE']:.5f}|{b['wz_MAE']:.5f}|")
lines+=['','## 原生名义/完整DR两阶配对','','| 模型 | 条件 | 正向通过/20 | 斜向初态通过/80 |','|---|---|---:|---:|']
for name,variants in stair_native['summaries'].items():
 for variant,groups in variants.items():lines.append(f"|{name}|{variant}|{groups['straight']['passed']}|{groups['oblique']['passed']}|")
lines+=['','原生400环境：同机械/噪声/外力/推扰初态配对，双侧上阶，0/±15/±30°，1.8/2.2m/s，每组合5初态，首个20秒物理回合。原生近边接触朝向代理与MuJoCo精确立面触阶角分别保存；不得混报fullDR毕业。 MuJoCo与原生矩阵还存在单/双入阶面、速度集合和命令平滑/阶跃差别；只在各自矩阵内作父/学生对比，不把跨矩阵数字差异直接归为物理引擎因果，详见evidence/EVALUATION_PROTOCOL_NOTE.md。','','## 原Rough-v1最高档保留','','| 原课程指标(L9) | 模型 | 条件 | 数量 | 附加yawMAE(rad/s) |','|---|---|---|---:|---:|']
for skill,rows in retained.items():
 for row in rows:
  label={'traverse':'10族双向穿越','gyro':'小陀螺首6秒存活','landing':'落地后指令恢复'}[skill];yaw='—' if row['wz_MAE'] is None else f"{row['wz_MAE']:.6f}";lines.append(f"|{label}|{row['model']}|{row['variant']}|{row['passed']}/{row['requested']}|{yaw}|")
full_data=json.loads((T/'next_full_episode/DATA_COMPLETE.json').read_text())
lines+=['','## 已补齐的教学覆盖缺口（未开新训练）','',f"当前40分钟使用原来的>=3秒示范，保持实验配方未热替换。已有轨迹发现教师前三秒平均前移0.185m，原父0.434m，学生约0.59～0.64m，起步状态已经不同；该准备阶段没有被原示范覆盖。监督缺口已补为完整成功回合：{full_data['observations']}帧，从端点0开始，仍仅收真实两级成功；移动仍3秒后开始。原生与MuJoCo原件分别保留，数据SHA {full_data['dataset_sha256']}，下一轮PLAN在next_full_episode/PLAN_NEXT_NOT_STARTED.json，未自动开新训练。此为已修的数据覆盖缺口，不把它当成唯一因果根因。"]
lines+=['','## 配方、保护与边界','',f"固定LR3e-5、clip0.1、3epochs、rollout24；原奖励−1.5e²和原登阶落轮奖励未改。80%原完整DR/20%名义。35/78/6、R3机械/电机包络、2.5ms物理/100Hz腿/400Hz轮/50Hz策略、2mm单环境保护不变。",'',f"冻结父策略在原flat/rough及正向/下行台阶当前观测上作保留指导；新教师只提供30条实际完成两阶成功轨迹、4433帧，来自15条原生＋15条MuJoCo成功。两分支有效权重各0.125，原成功回放也继续积累。父自身17项Adam/actor/critic/STD/RNG完整恢复。",'',f"本轮原生保护累计：{json.dumps(last['done_totals'],ensure_ascii=False)}。普通单环境保护按原规则处理；失败未写成成功或作为教师成功示范。",'','专项教师在MuJoCo改善但原生对照较弱，两个后端分开记录。保留原综合父、专项教师及本轮全部PT；大角度斜向与完整DR登阶仍按实测结果解释，没有新增部署导出。']
(T/'FINAL_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
(T/'README.md').write_text('\n'.join(['# 冻结台阶教师指导综合父模型（2026-11-13）','',f"已完成本轮{final['elapsed_seconds']:.3f}秒PPO和固定任务/原生两阶/原Rough-v1配对复核。",'',f"当前实验候选{selected['model_id']}，SHA{selected['sha256']}，完整PT：`weights/selected_specialist_student.pt`。",'',f"固定名义：平地{selected['flat60']}/60，正向两阶{selected['straight5']}/5，真实斜向{selected['actual_oblique20']}/20，下阶{selected['descent5']}/5；原生完整DR结果单列，原综合父db6e9ccf保持冻结。",'','[完整结果、选优与局限](FINAL_REPORT.md)；全部配方见PLAN.json，模型身份见weights/SELECTED_STUDENT.json。原始检查点/回放/失败/成功数据均保留，没有只保存模型地址。'])+'\n',encoding='utf8')
# Append this actual stage/checkpoint metadata without changing earlier stage decisions.
f=B/'MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json';reg=json.loads(f.read_text(encoding='utf8'));stage_id='stairs_specialist_student_20261113';assert not any(x['id']==stage_id for x in reg['stages'])
collection=json.loads((T/'evidence/MODEL_COLLECTION.json').read_text())['models'];ids=[]
for item in collection:
 mid=stage_id+'_'+Path(item['file']).stem.removeprefix('model_');ids.append(mid);data=torch.load(T/'weights'/item['file'],map_location='cpu',weights_only=False)
 reg['models'].append(dict(id=mid,file=item['file'],git_path=(T/'weights'/item['file']).relative_to(R).as_posix(),bytes=item['bytes'],sha256=item['sha256'],iteration=data['iter'],optimizer_entries=17,complete_PPO=True,actor_input=35,critic_input=78,action_output=6,parent_sha256=plan['parent_sha256'],frozen_stair_teacher_sha256=plan['teacher_retention']['stair_teacher_sha256'],recipe_files=[(T/'PLAN.json').relative_to(R).as_posix(),(T/'FINAL_REPORT.md').relative_to(R).as_posix()],stage_id=stage_id,role='Experimental comprehensive student; see native and retention evidence'))
reg['stages'].append(dict(id=stage_id,title='冻结专项台阶教师成功示范指导综合父模型40分钟',profile='continuous200mm_oblique_stairs_plus_original_Rough_v1_flat_retention',parent_sha256=plan['parent_sha256'],source_directories=[T.relative_to(R).as_posix()],recipe_files=[(T/'PLAN.json').relative_to(R).as_posix()],model_ids=ids,experimental_candidate_model_id=selected['model_id'],status='Completed bounded PPO and native paired checks; original parent remains frozen',budget={'planned_seconds':2400,'actual_seconds':final['elapsed_seconds']},report_file=(T/'FINAL_REPORT.md').relative_to(R).as_posix()))
reg['current_training_status']='closed; specialist-guided student experiment and native checks complete; frozen comprehensive parent preserved';reg['latest_stair_specialist_student_model_id']=selected['model_id'];reg['latest_stair_specialist_student_decision_file']=(T/'DECISION.json').relative_to(R).as_posix();reg['updated_at_epoch']=time.time();reg['as_of_date']='2026-11-13';reg['weights_summary'].update(models=len(reg['models']),unique_sha256=len({m['sha256'] for m in reg['models'] if m.get('sha256')}),total_bytes=sum(int(m.get('bytes') or 0) for m in reg['models']));f.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
with (B/'MOD4V3_DR_TRAINING_RECORDS_20261111/README.md').open('a',encoding='utf8') as file:file.write('\n## 台阶教师迁移学生完成\n\n'+selected['model_id']+'；平地'+str(selected['flat60'])+'/60、正向'+str(selected['straight5'])+'/5、真实斜向'+str(selected['actual_oblique20'])+'/20；全PT与原生保留结果见相邻MOD4V3_STAIRS_SPECIALIST_DISTILL_40M_20261113/FINAL_REPORT.md。原冻结父保持。\n')
block='<!-- STAIRS_SPECIALIST_TEACHER_20261113_START -->\n## 2026-11-13：综合父冻结、独立台阶教师及40分钟迁移实验完成\n\n冻结父db6e9ccf完整PT保留；专项教师715c40b6名义正向5/5、真实斜向10/20，原生fullDR仍弱。独立学生候选'+selected['model_id']+'：名义平地'+str(selected['flat60'])+'/60、正向'+str(selected['straight5'])+'/5、真实斜向'+str(selected['actual_oblique20'])+'/20，下阶'+str(selected['descent5'])+'/5。两引擎与原Rough-v1保留分别记录，不自动晋升部署。[全PT、配方和完整报告](sources/local/MOD4V3_STAIRS_SPECIALIST_DISTILL_40M_20261113/FINAL_REPORT.md)。\n<!-- STAIRS_SPECIALIST_TEACHER_20261113_END -->'
for file in [R/'README.md',R/'docs/DR_TRAINING_INDEX_20261111.md']:
 s=file.read_text(encoding='utf8');begin=s.index('<!-- STAIRS_SPECIALIST_TEACHER_20261113_START -->');end=s.index('<!-- STAIRS_SPECIALIST_TEACHER_20261113_END -->',begin)+len('<!-- STAIRS_SPECIALIST_TEACHER_20261113_END -->');b=block.replace('](sources/','](../sources/') if file.parent.name=='docs' else block;file.write_text(s[:begin]+b+s[end:],encoding='utf8')
print(json.dumps(decision,ensure_ascii=False),flush=True)
