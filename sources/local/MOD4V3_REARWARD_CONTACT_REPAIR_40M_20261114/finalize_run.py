"""Record the bounded40m result and candidate without automatic deployment promotion."""
from pathlib import Path
import hashlib,json,time,datetime
import torch
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
plan=json.loads((T/'PLAN.json').read_text());selected=json.loads((T/'weights/SELECTED_STUDENT.json').read_text());final=json.loads((E/'training/FINAL.json').read_text());post=json.loads((E/'post_native/COMPLETE.json').read_text());assert post['all_closed']
rank=json.loads((E/'STUDENT_FIXED_RANKING.json').read_text());collection=json.loads((E/'MODEL_COLLECTION.json').read_text())['models']
selected['status']='All fixed and native evaluations completed;low-speed task not achieved;experimental only,not promoted;frozen comprehensive parentdb6 remains default';selected['native_evaluation_complete']=True;selected['low_speed_goal_achieved']=False;(T/'weights/SELECTED_STUDENT.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
actual=final['elapsed_seconds'];rows=['# 真正搭阶承重奖励归类修复：原40分钟剩余预算结果','',f'本阶段实际PPO {actual:.3f}秒；本阶段预算{plan["training_round"]["seconds"]}秒，前阶段{plan["cumulative_training_seconds_before"]:.3f}秒，原整轮计划2400秒。综合父db6e9ccf/iter25331完整恢复；训练真实台面支撑后的后摆抬轮与落轮站立，旧高速台阶BC关闭。没有自动延长。','',f"实验候选：{selected['model_id']}，SHA {selected['sha256']}。完整PT见weights/selected_specialist_student.pt。",'', '| 保存点 | 低速双阶/4 | 辅助第一阶/2 | 后摆中段/3 | 平地/60 | 原快速正向/5 | 原快速斜向/20 | 下阶/5 | 前进MAE(m/s) |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for x in sorted(rank,key=lambda v:v['source_file']):rows.append(f"|{x['source_file']}|{x['low_whole_passed']}|{x['supported_first_passed']}|{x.get('late_supported_first_passed',0)}|{x['flat60_passed']}|{x['straight_passed']}|{x['actual_oblique_passed']}|{x['descent_passed']}|{x['forward_MAE_m_s']:.6f}|")
rows += ['', '同协议父低速整程0/4、辅助第一阶0/2，见../MOD4V3_REARWARD_RECOVERY_40M_20261114/evidence/parent_low_speed_r1。原高速基线和新低速协议分开解释。全部失败和训练保护保留；实验候选不自动替代综合父。','', '## 原生复核','', '|科目|模型|条件|数量|','|---|---|---|---:|']
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
rows += ['', '两引擎协议分别解释。原生台阶精确逐环境成绩以post_native/stairs/RESULT.json为准；rough穿越、首6秒旋转存活、落地指令恢复沿用原L9协议，不混作完整地图或主动跳跃毕业。','', '修改范围：上行0.35–0.75m/s；上行30%辅助底盘搭阶起步，单列不冒充整程；仅真实上台面承重局部接触豁免；原0.6抬轮额度拆成0.12支撑事件+0.24独立后摆进度+0.24独立抬升进度；初始进度不领奖；新增3个后摆中段辅助姿态及194帧/4条真实单阶恢复参考，仅腿动作监督0.25；真实落轮奖励沿用；落轮后恢复站高跟踪；旧高速台阶BC和在线示范池关闭；仅真实搭阶承重期间禁用腾空奖励段，原状态位恢复；参考四阶段均衡；父综合保留1.0及高站姿.25。原40/35/25配比、速度奖励、完整DR、35/78/6、MOD4电机与时序不变。每5分钟完整保存及检查记录在evidence/inspections。']
(E/'ARTIFACT_INDEX.json').write_text(json.dumps([dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),storage='complete local and native originals retained; indexed inGit') for p in sorted(E.rglob('*.npz'))],indent=2)+'\n',encoding='utf8')
rows += ['', '## 本轮判定与有针对性的后续', '', '原两阶段总PPO '+str(actual+plan['cumulative_training_seconds_before'])+'秒；没有追加预算。低速目标尚未实现，候选不替代综合父。', '', '真实卡住父快照root越沿52.3mm、全机器人COM只越沿2.1mm，车身/导轮相邻1s平均支撑5.86N；现有成功参考却从185–205mm更深入姿态起步，未覆盖实际受阻到稳定承重这一段。25m参考抬轮后交学生未站起，同前缀交父可站起；起始和落轮接续都未解决。', '', '冻结探针支持/airborne同现计数0，奖励归类冲突不能认定本轮失败主因。参考脚本姿态立即退出已在独立r2中改为原40deg/0.2s计时复核，真实受阻36条仍0恢复；训练和正式固定回放未改门槛。', '', '下一项最小实验见NEXT_REPAIR_PLAN.md：复用已有17个真实受阻起点，先单独训练支撑转移和后摆，再以父全部6动作保留落轮接续；当前未自动启动。']
(T/'FINAL_REPORT.md').write_text('\n'.join(rows)+'\n',encoding='utf8',newline='\n')
decision=dict(default_comprehensive_parent_sha256=plan['teacher_retention']['keep_teacher_sha256'],experimental_candidate=selected,promoted=False,low_speed_task_goal_achieved=False,reason='Original40m total budget completed; low-speed goal not achieved; preserve frozen comprehensive parent; no automatic extension',actual_PPO_seconds=actual,total_round_PPO_seconds=actual+plan['cumulative_training_seconds_before'],all_training_and_evaluations_closed=True)
(T/'DECISION.json').write_text(json.dumps(decision,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
with (T/'README.md').open('a',encoding='utf8') as f:f.write('\n## 实际完成\n\nPPO '+str(actual)+'秒，所有独立检查点与原生复核完成。实验候选'+selected['model_id']+'，未自动晋升；详见FINAL_REPORT.md与DECISION.json。\n')
registry=R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json';reg=json.loads(registry.read_text(encoding='utf8'));sid='rearward_contact_repair_20261114';assert not any(x['id']==sid for x in reg['stages']);ids=[]
for item in collection:
 data=torch.load(T/'weights'/item['file'],map_location='cpu',weights_only=False);mid=sid+'_'+Path(item['file']).stem;ids.append(mid)
 reg['models'].append(dict(id=mid,file=item['file'],git_path=(T/'weights'/item['file']).relative_to(R).as_posix(),bytes=item['bytes'],sha256=item['sha256'],iteration=data['iter'],complete_PPO=True,actor_input=35,critic_input=78,action_output=6,parent_sha256=plan['parent_sha256'],stage_id=sid,role='Experimental40m video-supported stair policy; default parent preserved'))
reg['stages'].append(dict(id=sid,title='真实搭阶承重奖励归类修复，原40分钟剩余预算',parent_sha256=plan['parent_sha256'],source_directories=[T.relative_to(R).as_posix()],recipe_files=[(T/'PLAN.json').relative_to(R).as_posix()],model_ids=ids,status='Completed original40m round;low-speed goal not achieved;not promoted',low_speed_goal_achieved=False,promoted=False,budget={'planned_seconds':plan['training_round']['seconds'],'previous_phase_seconds':plan['cumulative_training_seconds_before'],'original_total_budget_seconds':2400,'actual_seconds':actual},report_file=(T/'FINAL_REPORT.md').relative_to(R).as_posix()))
if reg.get('active_training',{}).get('id')==sid:reg.pop('active_training')
reg['current_training_status']='closed;original40m budget completed;low-speed goal not achieved;parentdb6 retained;next actual-support-transfer plan prepared';reg['latest_experimental_stair_model_id']=selected['model_id'];reg['updated_at_epoch']=time.time();reg['weights_summary'].update(models=len(reg['models']),unique_sha256=len({m['sha256'] for m in reg['models'] if m.get('sha256')}),total_bytes=sum(int(m.get('bytes') or 0) for m in reg['models']));registry.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\r\n')
for path in [R/'README.md',R/'docs/DR_TRAINING_INDEX_20261111.md',registry.parent/'README.md']:
 with path.open('a',encoding='utf8',newline='\r\n') as f:f.write('\n## 真实搭阶承重奖励归类修复，原40分钟剩余预算已结束\n\n实际PPO '+str(actual)+'秒；实验候选'+selected['model_id']+'，原综合父保持。源码、完整PT、配方和逐项结果：'+T.relative_to(R).as_posix()+'/FINAL_REPORT.md。\n')
print(json.dumps(decision,ensure_ascii=False),flush=True)
