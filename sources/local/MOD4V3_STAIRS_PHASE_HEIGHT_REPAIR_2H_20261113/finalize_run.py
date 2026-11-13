"""Record the bounded2h result and candidate without automatic deployment promotion."""
from pathlib import Path
import hashlib,json,time,datetime
import torch
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
plan=json.loads((T/'PLAN.json').read_text());selected=json.loads((T/'weights/SELECTED_STUDENT.json').read_text());final=json.loads((E/'training/FINAL.json').read_text());post=json.loads((E/'post_native/COMPLETE.json').read_text());assert post['all_closed']
rank=json.loads((E/'STUDENT_FIXED_RANKING.json').read_text());collection=json.loads((E/'MODEL_COLLECTION.json').read_text())['models']
actual=final['elapsed_seconds'];rows=['# 高站姿保留与阶段均衡/单轮落地反馈：两小时结果','',f'实际PPO {actual:.3f}秒；计划7200秒。综合父db6e9ccf保持冻结，实际接续权重和SHA见PLAN；教师715c只提供运动后成功示范。没有自动延长或新科目。','',f"实验候选：{selected['model_id']}，SHA {selected['sha256']}。完整PT见weights/selected_specialist_student.pt。",'', '| 保存点 | 平地/60 | 正向/5 | 真实斜向/20 | 下阶/5 | 前进MAE(m/s) |','|---|---:|---:|---:|---:|---:|']
for x in sorted(rank,key=lambda v:v['source_file']):rows.append(f"|{x['source_file']}|{x['flat60_passed']}|{x['straight_passed']}|{x['actual_oblique_passed']}|{x['descent_passed']}|{x['forward_MAE_m_s']:.6f}|")
rows += ['', '父既有同SHA基线为平地60/60、正向4/5、真实斜向0/20、下阶5/5。全部失败和训练保护保留；实验候选不自动替代综合父。','', '## 原生复核','', '|科目|模型|条件|数量|','|---|---|---|---:|']
for label in ['stairs','retained_traverse','retained_gyro','retained_landing']:
 j=json.loads((E/'post_native'/label/'RESULT.json').read_text())
 for model in ['parent','student']:
  for variant in sorted({x['variant'] for x in j['rows']}):
   group=[x for x in j['rows'] if x['model']==model and x['variant']==variant]
   if not group:continue
   if label=='retained_gyro':passed=sum(x['gyro_metrics']['first_episode_survived6s'] for x in group)
   elif label=='retained_landing':passed=sum(x['landing_metrics']['command_recovered'] for x in group)
   elif label=='retained_traverse':passed=sum(x['crossed_count'] for x in group)
   else:passed=sum(x['whole_two_step_passed'] for x in group)
   total=sum(x.get('requested',0) for x in group)
   rows.append(f'|{label}|{model}|{variant}|{passed}/{total}|')
rows += ['', '两引擎协议分别解释。原生台阶精确逐环境成绩以post_native/stairs/RESULT.json为准；rough穿越、首6秒旋转存活、落地指令恢复沿用原L9协议，不混作完整地图或主动跳跃毕业。','', '修改范围：4433帧运动后成功示范按阶段/角度/引擎均衡；高站姿腿部单独保留；单轮真实台面落地各0.15+双轮0.2，总0.5不变；在线池新轮重建且占比0.25。原40/35/25配比、速度奖励、完整DR、35/78/6、MOD4电机与时序不变。每5分钟完整保存及检查记录在evidence/inspections。']
(E/'ARTIFACT_INDEX.json').write_text(json.dumps([dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),storage='complete local and native originals retained; indexed inGit') for p in sorted(E.rglob('*.npz'))],indent=2)+'\n',encoding='utf8')
(T/'FINAL_REPORT.md').write_text('\n'.join(rows)+'\n',encoding='utf8',newline='\n')
decision=dict(default_comprehensive_parent_sha256=plan['teacher_retention']['keep_teacher_sha256'],experimental_candidate=selected,promoted=False,reason='Completed new2h experiment; preserve frozen comprehensive parent; paired acceptance remains explicit',actual_PPO_seconds=actual,all_training_and_evaluations_closed=True)
(T/'DECISION.json').write_text(json.dumps(decision,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
with (T/'README.md').open('a',encoding='utf8') as f:f.write('\n## 实际完成\n\nPPO '+str(actual)+'秒，所有独立检查点与原生复核完成。实验候选'+selected['model_id']+'，未自动晋升；详见FINAL_REPORT.md与DECISION.json。\n')
registry=R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json';reg=json.loads(registry.read_text(encoding='utf8'));sid='stairs_phase_height_repair_2h_20261114';assert not any(x['id']==sid for x in reg['stages']);ids=[]
for item in collection:
 data=torch.load(T/'weights'/item['file'],map_location='cpu',weights_only=False);mid=sid+'_'+Path(item['file']).stem;ids.append(mid)
 reg['models'].append(dict(id=mid,file=item['file'],git_path=(T/'weights'/item['file']).relative_to(R).as_posix(),bytes=item['bytes'],sha256=item['sha256'],iteration=data['iter'],complete_PPO=True,actor_input=35,critic_input=78,action_output=6,parent_sha256=plan['parent_sha256'],stage_id=sid,role='Experimental2h stair continuation; default parent preserved'))
reg['stages'].append(dict(id=sid,title='高站姿保留与台阶阶段均衡及单轮落地反馈修复2小时',parent_sha256=plan['parent_sha256'],source_directories=[T.relative_to(R).as_posix()],recipe_files=[(T/'PLAN.json').relative_to(R).as_posix()],model_ids=ids,status='Completed with original baseline frozen; no automatic promotion',budget={'planned_seconds':7200,'actual_seconds':actual},report_file=(T/'FINAL_REPORT.md').relative_to(R).as_posix()))
if reg.get('active_training',{}).get('id')==sid:reg.pop('active_training')
reg['current_training_status']='closed; repaired2h stair experiment and native paired checks complete; comprehensive parentdb6 retained';reg['latest_experimental_stair_model_id']=selected['model_id'];reg['updated_at_epoch']=time.time();reg['weights_summary'].update(models=len(reg['models']),unique_sha256=len({m['sha256'] for m in reg['models'] if m.get('sha256')}),total_bytes=sum(int(m.get('bytes') or 0) for m in reg['models']));registry.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for path in [R/'README.md',R/'docs/DR_TRAINING_INDEX_20261111.md',registry.parent/'README.md']:
 with path.open('a',encoding='utf8') as f:f.write('\n## 完整台阶示范＋上阶约束修复2小时已结束\n\n实际PPO '+str(actual)+'秒；实验候选'+selected['model_id']+'，原综合父保持。源码、完整PT、配方和逐项结果：'+T.relative_to(R).as_posix()+'/FINAL_REPORT.md。\n')
print(json.dumps(decision,ensure_ascii=False),flush=True)
