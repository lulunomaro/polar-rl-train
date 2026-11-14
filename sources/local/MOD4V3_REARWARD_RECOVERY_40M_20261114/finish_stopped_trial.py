"""Archive the safely stopped first phase; do not launch GPU tests or another training."""
from pathlib import Path
import json,subprocess,sys,time,torch,traceback
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
try:
 while not(E/'MONITOR_COMPLETE.json').exists():time.sleep(10)
 monitor=json.loads((E/'MONITOR_COMPLETE.json').read_text());assert not monitor['training_has_error'];assert(E/'training/SAFE_CLOSED.json').exists()
 subprocess.run([sys.executable,'-X','utf8','-B',str(T/'select_student.py')],cwd=R,check=True)
 final=json.loads((E/'training/FINAL.json').read_text());spent=final['elapsed_seconds'];selected=json.loads((T/'weights/SELECTED_STUDENT.json').read_text());reports=[]
 for p in sorted((E/'checkpoint_evals').glob('*/EVALUATION.json')):
  j=json.loads(p.read_text())
  if j.get('complete'):reports.append(j)
 rows=['# 后摆参考第一阶段：提前停止，未晋升','',f'PPO实际{spent:.3f}秒；原40分钟总预算剩余{2400-spent:.3f}秒。完整保存后通过REQUEST_STOP退出，非崩溃。冻结综合父db6e9ccf保持。','', '|文件|低速双阶/4|早期搭阶/2|后摆中段/3|平地/60|原快速正向/5|实际斜向/20|下阶/5|','|---|---:|---:|---:|---:|---:|---:|---:|']
 for j in reports:rows.append('|'+Path(j['model']).name+'|'+ '|'.join(str(j[k])for k in ['low_whole_passed','supported_first_passed','late_supported_first_passed','flat60_passed','straight_passed','actual_oblique_passed','descent_passed'])+'|')
 rows+=['','5m平地30/60，10m恢复60/60，不能说持续平地退化；低速新能力仍未完成。已定位初始参考动作欠拟合，以及真实导向轮承重仍可触发腾空wheel-centering的奖励冲突。更强保留、初始阶段均衡采样、真实搭阶受力时奖励按地面归类的修复另建目录MOD4V3_REARWARD_CONTACT_REPAIR_40M_20261114，仍从冻结父开始，训练累计不超原2400秒（单迭代收尾可能略超）。','', '原5m本机MuJoCo分配内存失败保留；释放每个场景后同SHA独立r2完成，未改物理/门槛。原失败EVALUATION.json仍为false。','', '本阶段因低速新技能未形成提前停止，未运行额外原生Rough后验收，不宣称fullDR/Rough毕业。保留所有完整PT、原始失败、固定回放和物理参考证据。']
 (T/'FINAL_REPORT.md').write_text('\n'.join(rows)+'\n',encoding='utf8');(T/'DECISION.json').write_text(json.dumps(dict(status='stopped_for_concrete_reward_and_sampling_repair',promoted=False,default_comprehensive_parent_sha256='db6e9ccf5c6d4d05a68633fd82861d903c4c52fcc1a6dd89132e55e2a4bf1283',actual_PPO_seconds=spent,remaining_original_round_seconds=2400-spent,all_PT_collected=True,extra_native_post_evaluations=False),indent=2)+'\n')
 with(T/'README.md').open('a',encoding='utf8',newline='\r\n')as f:f.write('\n## 已安全提前停止，未晋升\n\n实际PPO '+str(spent)+'秒，5m平地30/60、10m恢复60/60，低速双阶仍0/4；原生腾空奖励和真实导向轮支撑归类冲突及初始参考欠拟合另行修复。剩余原40分钟预算由MOD4V3_REARWARD_CONTACT_REPAIR_40M_20261114继续，不延长预算。全部本阶段结果见FINAL_REPORT.md。\n')
 path=R/'sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json';reg=json.loads(path.read_text(encoding='utf8'));sid='rearward_recovery_40m_20261114';assert not any(s['id']==sid for s in reg['stages']);ids=[]
 for item in monitor['models']:
  data=torch.load(T/'weights'/item['file'],map_location='cpu',weights_only=False);mid=sid+'_'+Path(item['file']).stem;ids.append(mid);reg['models'].append(dict(id=mid,file=item['file'],git_path=(T/'weights'/item['file']).relative_to(R).as_posix(),bytes=item['bytes'],sha256=item['sha256'],iteration=data['iter'],complete_PPO=True,actor_input=35,critic_input=78,action_output=6,parent_sha256='db6e9ccf5c6d4d05a68633fd82861d903c4c52fcc1a6dd89132e55e2a4bf1283',stage_id=sid,role='Stopped experimental first phase; not promoted'))
 reg['stages'].append(dict(id=sid,title='后摆参考第一阶段提前停止',source_directories=[T.relative_to(R).as_posix()],recipe_files=[(T/'PLAN.json').relative_to(R).as_posix()],model_ids=ids,status='stopped;new low-speed skill not attained;parent frozen',budget=dict(original_round=2400,actual_seconds=spent,remaining_seconds=2400-spent),report_file=(T/'FINAL_REPORT.md').relative_to(R).as_posix()))
 if reg.get('active_training',{}).get('id')==sid:reg.pop('active_training');reg['current_training_status']='first rearward-reference phase stopped; same-round supported-airborne repair prepared'
 reg['updated_at_epoch']=time.time();reg['weights_summary'].update(models=len(reg['models']),unique_sha256=len({m['sha256']for m in reg['models']if m.get('sha256')}),total_bytes=sum(int(m.get('bytes')or 0)for m in reg['models']));path.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\r\n')
 for p in [R/'README.md',R/'docs/DR_TRAINING_INDEX_20261111.md',path.parent/'README.md']:
  with p.open('a',encoding='utf8',newline='\r\n')as f:f.write('\n## 2026-11-14 后摆参考首阶段提前停止\n\nPPO '+str(spent)+'秒完整保存；5m平地30/60、10m恢复60/60，低速新技能未形成，未晋升。余下原40分钟预算用于真实搭阶支撑/腾空奖励冲突及参考起始欠拟合修复；见'+T.relative_to(R).as_posix()+'/FINAL_REPORT.md。\n')
 with(E/'ARCHIVE_STOPPED_COMPLETE.log').open('xb')as out,(E/'ARCHIVE_STOPPED_COMPLETE_ERROR.log').open('xb')as err:r=subprocess.run([sys.executable,'-X','utf8','-B','-u',str(T/'archive_run.py'),'--phase','complete'],cwd=R,stdout=out,stderr=err)
 assert r.returncode==0,'Stopped-phase Git archive needs recovery, do not repeat training'
 (E/'STOPPED_PIPELINE_COMPLETE.json').write_text(json.dumps(dict(epoch=time.time(),all_complete_PT_collected=True,no_more_training=True,source_archived=True,actual_PPO_seconds=spent),indent=2)+'\n');print('STOPPED_PHASE_ARCHIVED',flush=True)
except BaseException:
 (E/'STOPPED_PIPELINE_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),traceback=traceback.format_exc()),indent=2)+'\n');raise
