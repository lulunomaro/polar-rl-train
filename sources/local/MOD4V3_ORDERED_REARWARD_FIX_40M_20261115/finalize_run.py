"""Report measured results of this new round; no inherited success/failure conclusion."""
from pathlib import Path
import hashlib,json,time,datetime
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def put(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
plan=read(T/'PLAN.json');selected=read(T/'weights/SELECTED_STUDENT.json');final=read(E/'training/FINAL.json');post=read(E/'post_native/COMPLETE.json');assert post['all_closed']
rank=read(E/'STUDENT_FIXED_RANKING.json');collection=read(E/'MODEL_COLLECTION.json')['models'];actual=final['elapsed_seconds'];total_actual=actual+plan['cumulative_training_seconds_before']
selected.update(status='Completed fixed and native evaluations; experimental selection; frozen named comprehensive db6 remains default',native_evaluation_complete=True,low_speed_whole_observed=selected['low_whole_passed']>0)
put(T/'weights/SELECTED_STUDENT.json',selected)
rows=['# 先后摆、承重后收腿：本轮40分钟实际结果（2026-11-15）','',f'本修复阶段实际PPO {actual:.3f}秒；加原错误阶段{plan["cumulative_training_seconds_before"]:.3f}秒，总计{total_actual:.3f}秒；原总预算2400秒。每300秒完整检查点，时间标签按两阶段累计。初始化db6e9ccf/iter25331；原命名综合父保持冻结。','',f"本轮所选实验检查点：{selected['model_id']}，SHA {selected['sha256']}。",'',f"固定名义回放：低速完整两阶{selected['low_whole_passed']}/{selected['low_whole_requested']}；早期辅助一级落轮{selected['supported_first_passed']}/2；后摆中段辅助一级落轮{selected['late_supported_first_passed']}/3；平地{selected['flat60']}/60，原快速正向{selected['straight5']}/5，实际斜向{selected['actual_oblique20']}/20，下阶{selected['descent5']}/5。",'', '## 各完整检查点的独立回放','', '| 检查点 | 低速两阶/4 | 辅助早/2 | 辅助晚/3 | 平地/60 | 快速正向/5 | 实际斜向/20 | 下阶/5 |','|---|---:|---:|---:|---:|---:|---:|---:|']
for row in sorted(rank,key=lambda x:x['source_file']):rows.append('| '+row['source_file']+' | '+' | '.join(str(row[k])for k in ['low_whole_passed','supported_first_passed','late_supported_first_passed','flat60_passed','straight_passed','actual_oblique_passed','descent_passed'])+' |')
rows+=['','## 原生PhysX配对复核','', '父与学生使用同初态/同DR和相同原任务成功判据；名义、完整DR分别报告。回放通过次数不等于所有后续物理回合无保护重置。']
for directory in sorted((E/'post_native').iterdir()):
 if directory.is_dir()and(directory/'RESULT.json').exists():
  data=read(directory/'RESULT.json');rows+=['', '### '+directory.name,'','```json',json.dumps(data.get('summary',data.get('summaries',{})),ensure_ascii=False,indent=2),'```']
rows+=['','## 本轮实际改动与范围','', '触阶后先后摆，后摆25mm并达到20%重量上层支撑、连续3端点后才开放收腿/抬轮奖励。后摆不再等搭稳才有奖励；原旧收腿参考损失改0。连杆净受力结合已固定碰撞体包围半径和台阶几何作为训练支撑代理；MuJoCo另用实际接触点。没有动作脚本覆盖，actor35/critic78/action6保持。','', '17个已有真实受阻姿态只作为辅助姿态reset，速度/动作历史重新开始；不计完整从地面上两阶。原已有17段受阻轨迹的连杆向上力峰值实测均0，该事实不支持把旧失败归因于漏统计了已有承重；本轮训练检验是否能学到新增连杆/机身支撑路线。','', '原完整DR、40/35/25任务占比、速度奖励、电机/机械/时序和2mm单环境保护保留。父教师all6保留1.0，高站姿腿锚0.25，旧高速台阶模仿与旧后摆参考为0。','', '本轮40分钟已结束，无自动续训；综合默认不自动晋升。实际PPO与阶段事件见evidence/training/FINAL.json，各次检查见evidence/inspections，配方见PLAN.json。']
(T/'FINAL_REPORT.md').write_text('\n'.join(rows)+'\n',encoding='utf8')
decision=dict(default_comprehensive_parent_sha256=plan['parent_sha256'],experimental_candidate=selected,promoted=False,low_speed_whole_observed=selected['low_whole_passed']>0,actual_PPO_seconds=actual,total_round_PPO_seconds=total_actual,original_budget_seconds=2400,automatic_extension=False,all_training_and_evaluations_closed=True,reason='Bounded new40m window and paired evaluations complete; report actual counts; frozen named comprehensive model remains default')
put(T/'DECISION.json',decision)
put(E/'ARTIFACT_INDEX.json',[dict(path=str(q),bytes=q.stat().st_size,sha256=hashlib.sha256(q.read_bytes()).hexdigest(),storage='local original;indexed in Git')for q in E.rglob('*.npz')])
regpath=R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json';reg=read(regpath);sid='ordered_rearward_fix_20261115'
assert not any(s.get('id')==sid for s in reg['stages'])
model_ids=[]
for row in collection:
 name=row['file'];mid=sid+'_'+Path(name).stem.removeprefix('model_');model_ids.append(mid)
 reg['models'].append(dict(id=mid,file=name,git_path=(T/'weights'/name).relative_to(R).as_posix(),sha256=row['sha256'],bytes=row['bytes'],complete_PPO=True,actor_input=35,critic_input=78,action_output=6,parent_sha256=plan['parent_sha256'],recipe_files=[(T/'PLAN.json').relative_to(R).as_posix()],role='Experimental ordered low-speed stair checkpoint; not automatically promoted',git_storage='ordinary full PT blob'))
reg['stages'].append(dict(id=sid,title='触阶后先后摆、上层承重后收腿40分钟',parent_sha256=plan['parent_sha256'],retained_model_id=selected['model_id'],other_model_ids=model_ids,status='Completed2400s; measured results in final report; original comprehensive frozen',actual_PPO_seconds=actual,source_directories=[T.relative_to(R).as_posix()],recipe_files=[(T/'PLAN.json').relative_to(R).as_posix()],decision_file=(T/'DECISION.json').relative_to(R).as_posix()))
reg['latest_ordered_rearward_model_id']=selected['model_id'];reg['active_ordered_rearward_fix_training_20261115'].update(status='completed',actual_PPO_seconds=actual,all_evaluations_closed=True,promoted=False)
put(regpath,reg)
with(T/'README.md').open('a',encoding='utf8')as out:out.write('\n## 本轮结束\n\n实际PPO '+str(actual)+'秒，全部固定回放与原生配对复核完成。低速完整两阶'+str(selected['low_whole_passed'])+'/'+str(selected['low_whole_requested'])+'；实验选择'+selected['model_id']+'，默认综合父仍冻结。见FINAL_REPORT.md。\n')
for rel in ['README.md','docs/DR_TRAINING_INDEX_20261111.md']:
 with(R/rel).open('a',encoding='utf8')as out:out.write('\n### 2026-11-15 先后摆、承重后收腿轮完成\n\n实际PPO '+str(actual)+'秒；低速固定完整两阶'+str(selected['low_whole_passed'])+'/'+str(selected['low_whole_requested'])+'。全PT/配方/结果：sources/local/MOD4V3_ORDERED_REARWARD_STAIRS_40M_20261115/FINAL_REPORT.md；综合db6保持冻结。\n')
print(json.dumps(dict(actual_PPO_seconds=actual,selected=selected,decision=decision),ensure_ascii=False),flush=True)
