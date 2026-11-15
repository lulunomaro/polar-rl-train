"""Finish this single40m trial, rank fixed comparisons, archive all complete PTs."""
from pathlib import Path
import json,time,subprocess,sys,traceback,hashlib,datetime
T=Path(__file__).resolve().parent;E=T/'evidence';R=T.parents[2]
def put(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
try:
 while not(E/'MONITOR_COMPLETE.json').exists():time.sleep(20)
 monitor=json.loads((E/'MONITOR_COMPLETE.json').read_text());assert not monitor['training_has_error'],'See original ERROR.json; no restart'
 r=subprocess.run([sys.executable,'-X','utf8','-B',str(T/'select_student.py')],cwd=R,capture_output=True,text=True);(E/'SELECTION.log').write_text(r.stdout+r.stderr,encoding='utf8');r.check_returncode()
 selected=json.loads((T/'weights/SELECTED_STUDENT.json').read_text());final=json.loads((E/'training/FINAL.json').read_text());old=R/'sources/local/MOD4V3_PITCH_STABILITY_LEVEL9_ANGLE30_CONT_20261115/evidence/baseline_parent_pitch/RESULT.json';parent=json.loads(old.read_text())
 decision=dict(status='completed_fixed_suites',promoted=False,default_comprehensive_sha256='db6e9ccf5c6d4d05a68633fd82861d903c4c52fcc1a6dd89132e55e2a4bf1283',selected=selected,parent_pitch_summary=parent['summary'],elapsed_seconds=final['elapsed_seconds'],native_full_DR_probe_scope='Prior25m full-PPO parent zero-update instrumentation; fixed checkpoint suites are nominal MuJoCo, not full-DR graduation',automatic_extension=False)
 put(T/'DECISION.json',decision)
 lines=['# MOD4v3俯仰短时预测修复：40分钟实测','',f"实际PPO耗时 {final['elapsed_seconds']:.3f}s；每5分钟完整PPO/Adam/RNG检查点。冻结综合父模型保持db6e9ccf…；本轮候选不自动替换实车默认。",'',f"实验候选 {selected['source_file']}，SHA {selected['sha256']}。",'', '| 地形 | 父启动峰值° | 候选启动峰值° | 父急停峰值° | 候选急停峰值° | 父RMS° | 候选RMS° |','|---|---:|---:|---:|---:|---:|---:|']
 for k,x in parent['summary'].items():
  y=selected['pitch_summary'][k];lines.append(f"|{k}|{x['startup_peak_deg_max']:.3f}|{y['startup_peak_deg_max']:.3f}|{x['braking_peak_deg_max']:.3f}|{y['braking_peak_deg_max']:.3f}|{x['pitch_RMS_deg_mean']:.3f}|{y['pitch_RMS_deg_mean']:.3f}|")
 lines+=['',f"固定平地 {selected['flat60']}/60，正向两级台阶 {selected['straight5']}/5，下阶 {selected['descent5']}/5，实际斜向 {selected['actual_oblique20']}/20。",'', '完整结果、速度MAE、地图越界及所有中间检查点见 evidence/checkpoint_evals；不能把不同结束长度的RMS当严格等长对比，也不能把名义回放当fullDR毕业。','', '原因与奖励实现见 README.md、evidence/ROOT_CAUSE.json、evidence/diagnostic_causal/ROUGH_PROBE.json。']
 (T/'FINAL_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
 with (E/'ARCHIVE_COMPLETE.log').open('wb') as out:r=subprocess.run([sys.executable,'-X','utf8','-B',str(T/'archive_run.py'),'--phase','complete'],cwd=R,stdout=out,stderr=subprocess.STDOUT)
 r.check_returncode();put(E/'PIPELINE_COMPLETE.json',dict(epoch=time.time(),training_closed=True,fixed_suites_completed=True,full_PT_archived=True,promoted=False,automatic_extension=False))
 with (E/'ARCHIVE_CLOSURE.log').open('wb') as out:r=subprocess.run([sys.executable,'-X','utf8','-B',str(T/'archive_run.py'),'--phase','closure'],cwd=R,stdout=out,stderr=subprocess.STDOUT)
 r.check_returncode();print('PIPELINE_COMPLETE',flush=True)
except BaseException:
 put(E/'PIPELINE_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc(),automatic_relaunch=False));raise
