"""Preserve the superseded partial round; no native GPU post-evaluation or retraining."""
from pathlib import Path
import json,time,hashlib,shutil,subprocess,sys
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence';previous=T.parent/'MOD4V3_ORDERED_REARWARD_FIX_40M_20261115'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def put(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+chr(10),encoding='utf8')
while not(E/'MONITOR_COMPLETE.json').exists()or not(previous/'evidence/MONITOR_COMPLETE.json').exists():time.sleep(10)
prior=read(previous/'evidence/MONITOR_COMPLETE.json');current=read(E/'MONITOR_COMPLETE.json');assert not prior['training_has_error']and not current['training_has_error']
shutil.copytree(previous/'evidence',E/'previous_valid_segment',ignore=shutil.ignore_patterns('*.partial','*_worker.log','post_native','post_native_r2'))
models=[];mapping={}
for row in prior['models']:
 old=row['file'];name={'model_final.pt':'model_segment040_final.pt','model_first_complete.pt':'model_segment040_first_complete.pt'}.get(old,old);assert not(T/'weights'/name).exists();shutil.copy2(previous/'weights'/old,T/'weights'/name);mapping[old]=name;models.append(dict(row,file=name,path=str(T/'weights'/name),original_segment_path=row['path']))
for d in(previous/'evidence/checkpoint_evals').iterdir():
 if not d.is_dir()or not(d/'EVALUATION.json').exists():continue
 j=read(d/'EVALUATION.json');name=mapping[Path(j['model']).name];dest=E/'checkpoint_evals'/Path(name).stem;shutil.copytree(d,dest);j.update(model=str(T/'weights'/name),original_evaluation=str(d/'EVALUATION.json'),copied_without_new_simulation=True);put(dest/'EVALUATION.json',j)
models+=current['models'];put(E/'MODEL_COLLECTION.json',dict(models=models,full_PT_bytes=True,previous_segment=prior,current_segment=current))
result=subprocess.run([sys.executable,'-X','utf8','-B',str(T/'select_student.py')],cwd=R);assert result.returncode==0
p=read(T/'PLAN.json');final=read(E/'training/FINAL.json');actual=final['elapsed_seconds'];total=p['cumulative_training_seconds_before']+actual;selected=read(T/'weights/SELECTED_STUDENT.json')
reason='Human requested fix coupled rear/up wheel transfer then fresh7200s from frozen comprehensive db6; old round stopped after complete iteration and full checkpoint'
decision=dict(status='superseded_by_user_requested_repair',reason=reason,authorized_old_budget_seconds=7200,actual_old_round_PPO_seconds=total,actual_last_segment_PPO_seconds=actual,invalid_initial_PPO_seconds=292.2261128425598,safely_closed=True,full_saved_final=final['checkpoint'],experimental_fixed_selection=selected,promoted=False,new_trial='sources/local/MOD4V3_COUPLED_REARWARD_LIFT_2H_20261115',frozen_comprehensive_parent_sha256=p['frozen_comprehensive_parent_sha256'],native_post_evaluations_not_run=True)
put(T/'DECISION.json',decision)
rows=['# 原两小时轮：用户要求修复后从冻结父重训，安全中止归档','',f'原授权7200秒，实际累计{total:.3f}秒，含最初无效292.226秒；接续段实际{actual:.3f}秒。本轮没有完成两小时。','',reason,'',f'停止时完整PT SHA {final["checkpoint"]["SHA"]}，iter {final["checkpoint"]["iteration"]}，17项Adam完整。','',f'全部原保存点和固定评测保留；实验固定选择{selected["model_id"]}，低速完整两阶{selected["low_whole_passed"]}/{selected["low_whole_requested"]}；平地{selected["flat60"]}/60，快速正向{selected["straight5"]}/5，实际斜向{selected["actual_oblique20"]}/20，下阶{selected["descent5"]}/5。未晋升。','', '原生最终配对评测未运行，避免占用新训练GPU；不能将固定MuJoCo选择冒称fullDR原生验收。新轮从db6独立7200秒，不加载本轮学生，不向新预算计旧用时。','', '数据见evidence/training、checkpoint_evals、previous_valid_segment，完整PT均保留。']
(T/'FINAL_REPORT.md').write_text(chr(10).join(rows)+chr(10),encoding='utf8')
put(E/'ARTIFACT_INDEX.json',[dict(path=str(q),bytes=q.stat().st_size,sha256=hashlib.sha256(q.read_bytes()).hexdigest(),storage='local original; SHA indexed in Git')for q in E.rglob('*.npz')])
regpath=R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json';reg=read(regpath);known={m['id']for m in reg['models']}
for row in models:
 mid='ordered_rearward_2h_20261115_'+Path(row['file']).stem.removeprefix('model_')
 if mid not in known:reg['models'].append(dict(id=mid,file=row['file'],git_path=(T/'weights'/row['file']).relative_to(R).as_posix(),sha256=row['sha256'],bytes=row['bytes'],complete_PPO=True,root_parent_sha256=p['frozen_comprehensive_parent_sha256'],role='Superseded experimental checkpoint; not promoted',git_storage='ordinary full PT body'))
sid='ordered_rearward_2h_superseded_20261115';assert not any(s.get('id')==sid for s in reg['stages']);reg['stages'].append(dict(id=sid,status='user_requested_safe_stop_and_repair',actual_PPO_seconds=total,source_directories=[T.relative_to(R).as_posix()],decision_file=(T/'DECISION.json').relative_to(R).as_posix()));reg['active_ordered_rearward_2h_training_20261115'].update(status='safely_stopped_superseded',actual_PPO_seconds=total,replaced_by=decision['new_trial']);put(regpath,reg)
with(T/'README.md').open('a',encoding='utf8')as f:f.write(chr(10)+'## 用户要求修复后从父重训：本轮已安全中止'+chr(10)+f'实际累计PPO {total:.3f}秒，未完成7200秒。停止PT及全部固定回放已保存，未做原生最终验收或晋升。见FINAL_REPORT.md。'+chr(10))
put(E/'SUPERSEDED_CLOSURE_READY.json',decision);print(json.dumps(decision,ensure_ascii=False),flush=True)
