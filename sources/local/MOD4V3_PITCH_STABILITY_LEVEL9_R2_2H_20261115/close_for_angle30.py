"""Close the saved angle10 phase after a human-authorized coefficient change."""
from pathlib import Path
import json,time,subprocess,sys
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
replacement=T.parent/'MOD4V3_PITCH_STABILITY_LEVEL9_ANGLE30_CONT_20261115'
while not(E/'MONITOR_COMPLETE.json').exists():time.sleep(5)
for script in ['select_student.py','finalize_run.py']:subprocess.run([sys.executable,'-X','utf8','-B',str(T/script)],cwd=R,check=True)
p=T/'DECISION.json';d=json.loads(p.read_text());continuation=json.loads((replacement/'PLAN.json').read_text());d.update(status='Safely saved angle10 phase;human requested angle30 continuation',two_hour_budget_completed=False,replacement=replacement.relative_to(R).as_posix(),saved_state_used_as_continuation_parent=True,remaining_original_budget_seconds=continuation['training_round']['seconds'],original_total_budget_seconds=7200,no_native_final_rerun=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
with(T/'FINAL_REPORT.md').open('a',encoding='utf8')as out:out.write('\n## 人类要求加强俯仰惩罚后的保存接续\n\n本阶段实际PPO '+str(d['actual_PPO_seconds'])+'秒，未完成两小时。当前完整PPO已安全保存；新阶段仅将角度系数10改30，并接续剩余原预算。没有回到db6重新训练；db6仍为保留技能教师和综合默认。全部固定检查点评测收尾，未重复原生长评测。新目录：'+replacement.relative_to(R).as_posix()+'。\n')
regpath=R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json';reg=json.loads(regpath.read_text());reg['active_pitch_stability_level9_r2_training_20261115'].update(status=d['status'],promoted=False,replacement=d['replacement'])
for stage in reg['stages']:
 if stage.get('id')=='pitch_stability_level9_r2_20261115':stage['status']=d['status'];stage['replacement']=d['replacement']
regpath.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(E/'ANGLE10_PHASE_CLOSURE_COMPLETE.json').write_text(json.dumps(dict(epoch=time.time(),actual_PPO_seconds=d['actual_PPO_seconds'],all_fixed_evaluations_closed=True,all_PT_collected=True,new_angle30_continuation=d['replacement']),indent=2)+'\n',encoding='utf8')
print(json.dumps(d),flush=True)
