"""Close the preserved R1 short run and document the2048-env spawn layout defect."""
from pathlib import Path
import json,time,subprocess,sys
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
while not(E/'MONITOR_COMPLETE.json').exists():time.sleep(5)
for script in ['select_student.py','finalize_run.py']:subprocess.run([sys.executable,'-X','utf8','-B',str(T/script)],cwd=R,check=True)
p=T/'DECISION.json';d=json.loads(p.read_text());d.update(status='Saved short R1 trial;spawn-grid layout defect;superseded by R2',two_hour_budget_completed=False,native_final_pair_performed=False,reason='Target359env consolidation enlarged shared random-column0.8m spawn grid for non-target neighbors;some non-target resets started outside original4m tile bounds',replacement='sources/local/MOD4V3_PITCH_STABILITY_LEVEL9_R2_2H_20261115',old_student_not_used_as_parent=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
with(T/'FINAL_REPORT.md').open('a',encoding='utf8')as out:out.write('\n## 短试中止原因\n\n本轮因2048环境下随机起伏列非目标邻居出生点网格超界而保存停止。不是两小时完成，也不晋升。R2将两组网格分开，边界与物理参数不改，从同一冻结综合父重新开始；R1用时独立留档。64环境探针未覆盖这一大量环境布局缺陷，R2改为2048环境200步实际复核。\n')
regpath=R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json';reg=json.loads(regpath.read_text());reg['active_pitch_stability_level9_training_20261115'].update(status=d['status'],promoted=False)
for s in reg['stages']:
 if s.get('id')=='pitch_stability_level9_20261115':s['status']=d['status']
regpath.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n')
(E/'SHORT_TRIAL_CLOSURE_COMPLETE.json').write_text(json.dumps(dict(epoch=time.time(),actual_PPO_seconds=d['actual_PPO_seconds'],all_fixed_evaluations_closed=True,all_PT_collected=True,no_native_final_rerun=True),indent=2)+'\n')
print(json.dumps(d),flush=True)
