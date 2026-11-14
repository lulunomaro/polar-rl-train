"""Close user-superseded trial after its existing fixed evaluators drain; no GPU jobs."""
from pathlib import Path
import json,time,subprocess,sys,hashlib
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def put(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
while not(E/'MONITOR_COMPLETE.json').exists():time.sleep(5)
subprocess.run([sys.executable,'-X','utf8','-B',str(T/'select_student.py')],cwd=R,check=True)
final=read(E/'training/FINAL.json');actual=final['elapsed_seconds'];rank=read(E/'STUDENT_FIXED_RANKING.json');selected=read(T/'weights/SELECTED_STUDENT.json');models=read(E/'MODEL_COLLECTION.json')['models'];plan=read(T/'PLAN.json');frozen=plan['parent_sha256']
decision=dict(status='User superseded after sequential-mount diagnosis;7200second round not completed',authorized_seconds=7200,actual_PPO_seconds=actual,promoted=False,default_comprehensive_parent_sha256=frozen,experimental_candidate=selected,all_saved_full_PT_collected=True,all_fixed_evaluations_closed=True,final_native_evaluation_performed=False,reason='User urgently switched to comprehensive-parent pitch stability repair on level9 random uniform and hard start-stop',replacement='sources/local/MOD4V3_PITCH_STABILITY_LEVEL9_2H_20261115',no_more_training_for_this_trial=True)
put(T/'DECISION.json',decision)
lines=['# 顺序搭阶实验：用户紧急中止，切换综合父的俯仰稳定修复','',f'授权7200秒，实际PPO {actual:.6f}秒；未完成两小时，未晋升。综合默认仍为冻结db6e9ccf。','',f'完整检查点{len(models)}份已收回；最后完整PT SHA '+hashlib.sha256((T/'weights/model_final.pt').read_bytes()).hexdigest()+'。','', '已跑完本轮已有全部固定回放；未额外启动原生最终配对验收。原64环境零更新探针证据保留。','', '| 检查点 | 低速两阶/4 | 早辅助/2 | 晚辅助/3 | 平地/60 | 快速正向/5 | 实际斜向/20 | 下阶/5 |','|---|---:|---:|---:|---:|---:|---:|---:|']
for row in sorted(rank,key=lambda x:x['source_file']):lines.append('| '+row['source_file']+' | '+' | '.join(str(row[k])for k in ['low_whole_passed','supported_first_passed','late_supported_first_passed','flat60_passed','straight_passed','actual_oblique_passed','descent_passed'])+' |')
lines+=['','中止原因：用户紧急要求保存现有成果，优先从冻结综合最优父修复难度9随机起伏和启动急停时的俯仰不稳定。顺序搭阶轮未完成授权两小时，也没有证据宣称已学会低速上阶。','', '下一轮从冻结父完整恢复，旧轮学生不作为父；原完整DR、40/35/25任务占比及2mm保护保留。']
(T/'FINAL_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
put(E/'ARTIFACT_INDEX.json',[dict(path=str(q),bytes=q.stat().st_size,sha256=hashlib.sha256(q.read_bytes()).hexdigest(),storage='original retained; report index in Git')for q in E.rglob('*.npz')])
regpath=R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json';reg=read(regpath);sid='sequential_chassis_mount_20261115'
if not any(x.get('id')==sid for x in reg['stages']):
 ids=[]
 for row in models:
  mid=sid+'_'+Path(row['file']).stem.removeprefix('model_');ids.append(mid)
  reg['models'].append(dict(id=mid,file=row['file'],git_path=(T/'weights'/row['file']).relative_to(R).as_posix(),sha256=row['sha256'],bytes=row['bytes'],complete_PPO=True,actor_input=35,critic_input=78,action_output=6,root_parent_sha256=frozen,recipe_files=[(T/'PLAN.json').relative_to(R).as_posix()],role='Superseded experimental checkpoint; not promoted',git_storage='ordinary full PT blob'))
 reg['stages'].append(dict(id=sid,title='顺序搭阶：用户中止，改俯仰稳定',status='User superseded; not a completed two-hour run',total_PPO_seconds=actual,parent_sha256=frozen,retained_model_id=selected['model_id'],other_model_ids=ids,decision_file=(T/'DECISION.json').relative_to(R).as_posix()))
reg['active_sequential_chassis_mount_training_20261115'].update(status='user_superseded_safely_closed',actual_PPO_seconds=actual,promoted=False);put(regpath,reg)
text=f'\n2026-11-15 顺序搭阶轮用户中止：实际PPO {actual:.3f}秒，非两小时完成；未晋升；固定回放及完整PT已保留，见 '+(T/'FINAL_REPORT.md').relative_to(R).as_posix()+'。\n'
for path in [T/'README.md',R/'README.md',R/'docs/DR_TRAINING_INDEX_20261111.md']:
 if path.is_file():
  with path.open('a',encoding='utf8')as out:out.write(text)
put(E/'SUPERSEDED_CLOSURE_COMPLETE.json',dict(epoch=time.time(),actual_PPO_seconds=actual,all_fixed_evaluations_closed=True,no_native_final_rerun=True))
print(json.dumps(decision),flush=True)
