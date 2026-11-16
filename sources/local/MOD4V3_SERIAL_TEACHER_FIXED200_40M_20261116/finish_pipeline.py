"""Finish this run after native safe close and queued independent evaluations; no new training."""
from pathlib import Path
import sys,json,time,hashlib,datetime,subprocess,os,traceback
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
def load(f):return json.loads(f.read_text(encoding='utf8'))
def write(f,d):f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
try:
 while not(E/'MONITOR_COMPLETE.json').exists():time.sleep(20)
 final=load(E/'training/FINAL.json')if(E/'training/FINAL.json').exists()else None;closed=load(E/'training/SAFE_CLOSED.json');assert closed['scene_closed']
 before=load(E/'DEFAULT_BEFORE.json');default=R/'deliveries/CURRENT_COMPREHENSIVE_MODEL.json';unchanged=hashlib.sha256(default.read_bytes()).hexdigest()==before['sha256'];assert unchanged
 first=load(E/'training/FIRST_UPDATE.json')if(E/'training/FIRST_UPDATE.json').exists()else None
 last=load(E/'training/LATEST_PROGRESS.json')if(E/'training/LATEST_PROGRESS.json').exists()else{};has_error=(E/'training/ERROR.json').exists()
 evaluations={f.parent.name:load(f)for f in sorted((E/'checkpoint_evals').glob('*/EVALUATION.json'))}
 status=dict(epoch=time.time(),training_closed=True,training_has_error=has_error,final=final,last_iteration=last.get('iteration'),optimizer_minibatches=last.get('losses',{}).get('actual_optimizer_minibatches_total'),PPO_iterations=last.get('iteration',25362)-25362,default_c874_unchanged=unchanged,teacher_dataset_frames=2500,teacher_demonstrations=5,fixed_height_m=.2,curriculum_enabled=False,evaluations={k:{z:d.get(z)for z in ['complete','single_step_qualified_passed','single_step_requested','flat60_passed','straight_passed','actual_oblique_passed','descent_passed']}for k,d in evaluations.items()},additional_training=False,automatic_promotion=False)
 write(E/'FINAL_STATUS.json',status)
 text='# 固定200mm教师监督40分钟：实际收尾\n\n'+('训练正常保存关闭。'if not has_error else'训练发生错误，原错误和完整已存权重保留，未自动重开。')+' 默认c874保持。\n\n'
 if final:text+='实际PPO耗时：'+str(round(final.get('elapsed_seconds',0.),3))+' 秒；最后iteration '+str(last.get('iteration'))+'，PPO迭代 '+str(status['PPO_iterations'])+'，实际优化器小批次步 '+str(status['optimizer_minibatches'])+'。\n\n'
 text+='819台阶环境全部固定20cm、无升降和低阶复习；1229保留平地/崎岖，full-DR和原35/78/6、物理电机不变。5条获准教师示范2500帧，技能lambda1/batch192和c874保留lambda1进入同一PPO优化器，学生实际执行无教师辅助。\n\n'
 text+='|检查点|纯学生20cm|normal平地|normal正向双阶|normal斜向|normal下阶|\n|---|---:|---:|---:|---:|---:|\n'
 for name,d in evaluations.items():text+=f"|{name}|{d.get('single_step_qualified_passed','?')}/5|{d.get('flat60_passed','?')}/60|{d.get('straight_passed','?')}/5|{d.get('actual_oblique_passed','?')}/20|{d.get('descent_passed','?')}/5|\n"
 text+='\n这些是名义MuJoCo固定回放，不能作为原生完整DR毕业。成功/失败原件、逐帧轨迹和5m/最终center视频均在evidence/checkpoint_evals。启动r1缺配置、r2字段检查失败均为零优化器更新且不耗PPO预算，原始记录保留。无新增预算或默认晋升。\n'
 (T/'FINAL_REPORT.md').write_text(text,encoding='utf8')
 memory='## 2026-11-16 固定200mm教师监督40分钟已收尾\n\n'+f"当前独立实验{T.name}已保存关闭；iteration {last.get('iteration')}，实际优化器小批次步{status['optimizer_minibatches']}，训练错误={has_error}。默认c874未变、无自动晋升/延长。独立学生表现仅按该目录FINAL_REPORT.md及实际回放，不继承教师5/5；固定20cm无高度课程。\n\n"
 for f in [R/'AGENTS.md',R.parent/'AGENTS.md',R/'sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/README.md',R/'sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/MEMORY_ENTRY.md']:
  f.write_text(memory+f.read_text(encoding='utf8'),encoding='utf8')
 for args in [['--phase','complete'],['--phase','complete','--record']]:
  with(T/('archive_complete_prepare.log'if '--record'not in args else'archive_complete_record.log')).open('xb')as log:r=subprocess.run([sys.executable,'-X','utf8','-B',str(T/'archive_stage.py'),*args],cwd=R,stdout=log,stderr=subprocess.STDOUT)
  if r.returncode:raise RuntimeError('Completion archive failed; preserve existing commit/tag if created; inspect archive log without rerunning record')
 print('PIPELINE_COMPLETE no added PPO budget or promotion',flush=True)
except Exception:
 write(E/'PIPELINE_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc(),additional_training=False));raise
