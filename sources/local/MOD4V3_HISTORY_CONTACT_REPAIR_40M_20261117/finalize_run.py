"""Report measured independent outcomes, protect frozen originals, archive all results."""
from pathlib import Path
import json,hashlib,sys,time,subprocess
import numpy as np
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
def read(f):return json.loads(f.read_text())if f.exists()else{}
def main():
 protected=read(E/'PROTECTED_INPUTS.json');checks=[dict(**row,unchanged=hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()==row['sha256'])for row in protected];final=read(E/'training/FINAL.json');clock=read(E/'training/TRAINING_CLOCK.json');error=read(E/'training/ERROR.json');closed=read(E/'training/SAFE_CLOSED.json');evaluations={}
 for f in(E/'checkpoint_evals').glob('*/EVALUATION.json'):evaluations[f.parent.name]=read(f)
 current=evaluations.get('model_final',{});single=read(E/'checkpoint_evals/model_final/single_step/RESULT.json');parent=read(R/'sources/local/MOD4V3_FIXED200_DAGGER_SEMANTIC_10M_20261116/evidence/checkpoint_evals/model_010m/EVALUATION.json')
 receipt=dict(epoch=time.time(),default_promoted=False,automatic_extension=False,protected_checks=checks,all_protected_unchanged=all(row['unchanged']for row in checks),training_error=error,final=final,clock=clock,closed=closed,evaluations=evaluations,independent_student=True,teacher_assistance=False,pretrained_encoder_optimizer_steps=0,reused_prior_encoder_steps=3000,actual_local_CPU_optimizer_steps=22000,selected_lineage_CPU_optimizer_steps=13000)
 from inspect_run import snapshot
 final_weights=T/'weights/model_final.pt'
 if final_weights.exists():receipt['training_speed_checkpoint']=snapshot(final_weights)
 (E/'FINAL_SUMMARY.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 lines=['# 历史观测固定200mm实验实测报告','', '本轮只在独立目录改变actor。默认c874、CURRENT指针、原010m、原8391帧保护检查：'+str(receipt['all_protected_unchanged'])+'。不自动晋升、不延长。','', '本轮初始normal60/60；原10229帧保留，加18条合格现场纠偏共15645帧/65个episode。CPU实际优化22000步，最终继承路径13000步；本轮encoder新预训练0，复用旧3000步编码器。PPO小批次另计。','', 'PPO时间：'+str(clock.get('epoch'))+' → '+str(final.get('epoch'))+'；elapsed='+str(final.get('elapsed_seconds'))+'秒；原生安全关闭='+str(bool(closed))+'；错误='+str(bool(error))+'。', '', '实际新增PPO迭代与Adam小批次见FINAL及LATEST_PROGRESS；中止或未完成项不计通过。', '', '|检查点|normal flat60|严格低速200mm|真实双轮越边|物理稳态事件|原双阶|斜向|下阶|','|---|---:|---:|---:|---:|---:|---:|---:|']
 for name,v in sorted(evaluations.items()):lines.append('|'+name+'|'+'|'.join(str(v.get(k,'未测'))for k in ['flat60_passed','single_step_qualified_passed','physical_crossed','physical_stable_events','straight_passed','actual_oblique_passed','descent_passed'])+'|')
 lines+=['','正式速度线始终<=0.6m/s；训练放宽档位的完成数不能充当正式成绩。教师辅助为0。nominal冻结回放不等于full-DR毕业。','','## 最终200mm各起点','','|起点mm|严格通过|双轮越边|最大物理稳态s|入阶m/s|近阶峰速|首秒位移m|首秒峰速|峰值俯仰deg|','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
 for r in single.get('rows',[]):lines.append('|'+str(r['start_offset_mm'])+'|'+'|'.join(str(r.get(k))for k in ['success','physical_bilateral_crossed','physical_max_hold_s','entry_speed_m_s','maximum_entry_ascent_speed_m_s','pre1s_displacement_m','pre1s_peak_speed_m_s','pitch_peak_deg'])+'|')
 lines+=['','急停/原双阶/斜向/下阶原始数据：evidence/checkpoint_evals/model_final/。视频：同目录single_step/STUDENT_CENTER_1X.mp4。历史实验与方案：REPAIR_PLAN.md。所有失败预检、训练错误与未通过评测均保留。']
 if receipt.get('training_speed_checkpoint'):lines+=['','实际训练速度课程计数（不能当独立成绩）：'+json.dumps(receipt['training_speed_checkpoint'],ensure_ascii=False)]
 if error:lines+=['','本轮出现训练错误，未自动重启。原始错误：'+json.dumps(error,ensure_ascii=False)]
 (T/'FINAL_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
 # Scientific trace curves are emitted only from measured arrays.
 if single:
  import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
  fig,axes=plt.subplots(4,1,figsize=(12,11),sharex=True)
  for dest in(E/'checkpoint_evals/model_final/single_step').glob('start_*'):
   f=dest/'rollout.npz'
   if not f.exists():continue
   tr=np.load(f)['trace'];label=dest.name
   if not len(tr):continue
   for ax,y in zip(axes,[tr[:,1],tr[:,5],np.rad2deg(tr[:,6]),tr[:,3]]):ax.plot(tr[:,0],y,label=label)
  for ax,title in zip(axes,['Base X [m]','Horizontal speed [m/s]','Pitch [deg]','Base Z [m]']):ax.set_ylabel(title);ax.grid(True,alpha=.3)
  axes[1].axhline(.6,color='k',ls='--');axes[0].legend();axes[-1].set_xlabel('Time [s]');fig.tight_layout();fig.savefig(E/'FINAL_FIVE_STARTS.png',dpi=150);plt.close(fig)
 with(E/'ARCHIVE_FINAL.log').open('wb')as log:r=subprocess.run([sys.executable,'-X','utf8','-B',str(T/'archive_stage.py'),'--stage','complete-01','--note','FINAL_REPORT.md'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError('Final archive pending; see ARCHIVE_FINAL.log')
 print('FINAL_REPORT_AND_ARCHIVE_COMPLETE',flush=True)
if __name__=='__main__':main()
