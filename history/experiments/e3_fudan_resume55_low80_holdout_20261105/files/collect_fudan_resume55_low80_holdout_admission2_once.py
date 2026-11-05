"""One bounded metadata-only collector for three actual independent low80 cases.
No source model/raw/canonical access, no case qualification rerun or SDK lifecycle.
"""
from pathlib import Path
import json,time,sys
D=Path(__file__).resolve().parent;T=D.parent/'mod4v1_experts_fulldr_rm70_20261101';prefix='FDNRESUME55_LOW80_HOLDOUT_ADMISSION2_';stage=json.loads((D/(prefix+'STAGE_RESULT.json')).read_bytes());dispatch=json.loads((D/(prefix+'DISPATCH_RESULT.json')).read_bytes());root=stage['root'];members=stage['roles'];assert dispatch['returncode']==0 and dispatch['root']==root and len(members)==3
mark=D/(prefix+'COLLECTOR_ONCE.json');closed_path=D/(prefix+'CLOSED_RESULT.json');scope_path=D/(prefix+'SCOPE_RESULT.json');report_path=D/(prefix+'QUALITY_RESULTS_V1.md');out=D/'reports'/(prefix+time.strftime('%Y%m%d_%H%M%S'))
assert not any(p.exists()for p in(mark,closed_path,scope_path,report_path));out.mkdir(parents=True)
mark.write_text(json.dumps(dict(epoch=time.time(),root=root,output=str(out),case_members=members,read_only_own_metadata=True,source_model_raw_canonical_SDK_operations=0),indent=2),encoding='utf8')
sys.path.insert(0,str(T));from project_connector import connect72
root_names=('PARENT_STARTED.json','ACTUAL_GROUP_ADMISSION.json','GROUP_EVAL_START.json','GROUP_BARRIER_STATUS.json','BOUNDED_ORIGINAL_RESOURCE_WAIT.json','GROUP_ABORT.json','PARENT_ORIGINAL_ERROR.json','TERMINAL_ROWS.json','FINAL.json','PARENT_EXIT_SCOPE.json',prefix+'OUTER_DISPATCH.json',prefix+'PARENT_WAITED_ACTUAL.json')
case_names=('task.json','WORKER_SCENE_READY.json','WORKER_EVAL_STARTED.json','FRESH80_FULLDR_BEFORE_CONTROL.json','FINAL.json','PRE_CLOSE.json','FDN_N80_APP_CLOSE_INTENT.json','WORKER_ERROR.json','ENV_CLOSE_ERROR.json','APP_CLOSE_BINDING_ERROR.json','CLOSE_EVIDENCE_ERROR.json','APP_CLOSE_ERROR.json')
c=s=None;last=None;end=time.monotonic()+4500

def get(path):
 try:
  with s.open(path,'rb')as f:return json.loads(f.read())
 except FileNotFoundError:return None

def local(path,value):
 tmp=path.with_suffix(path.suffix+'.partial');tmp.write_text(json.dumps(value,indent=2,allow_nan=False),encoding='utf8');tmp.replace(path)

try:
 c=connect72();s=c.open_sftp()
 while True:
  rm={name:get(root+'/'+name)for name in root_names};cm={member:{name:get(root+'/cases/'+member+'/'+name)for name in case_names}for member in members}
  snap=dict(epoch=time.time(),root=root,metadata=rm,cases=cm);local(out/'LATEST_METADATA_SNAPSHOT.json',snap)
  progress=dict(admitted=rm['ACTUAL_GROUP_ADMISSION.json']is not None,common_start=rm['GROUP_EVAL_START.json']is not None,case_final=[k for k,v in cm.items()if v['FINAL.json']is not None],case_error=[k for k,v in cm.items()if v['WORKER_ERROR.json']is not None],closed=rm['PARENT_EXIT_SCOPE.json']is not None and rm[prefix+'PARENT_WAITED_ACTUAL.json']is not None)
  if progress!=last:print('RESUME55_LOW80_HOLDOUT_ADMISSION2_PROGRESS '+json.dumps(progress),flush=True);last=progress
  if progress['closed']:break
  if time.monotonic()>=end:raise TimeoutError('Own metadata observer4500 expired; original parent unchanged, inspect actual own PID/JSON before any continuation')
  time.sleep(15)
 snap['closed']=True;local(closed_path,snap);local(out/'CLOSED_RESULT.json',snap)
 exit=rm['PARENT_EXIT_SCOPE.json'];outer=rm[prefix+'PARENT_WAITED_ACTUAL.json'];rows=rm['TERMINAL_ROWS.json']or[];pf=rm['FINAL.json']or{}
 checks=dict(actual_external_parent_wait=outer.get('actual_parent_p_wait_returned')is True and outer.get('original_parent_reaped')is True and outer.get('returncode')==0 and outer.get('errors')==[],all_own_children_waited=exit.get('all_own_children_waited')is True,original_private_and_finite_released=exit.get('original_single_GPU_private_EX_released')is True and exit.get('original_global_finite_EX_released')is True,parent_error_absent=exit.get('errors')==[]and rm['GROUP_ABORT.json']is None and rm['PARENT_ORIGINAL_ERROR.json']is None,actual_all_cases_terminal=len(rows)==3 and {r.get('role')for r in rows}==set(members),original_parent_final_all_complete=pf.get('all_nine_actual_execution_complete')is True,actual_common_barrier=rm['GROUP_EVAL_START.json']is not None and set((rm['GROUP_EVAL_START.json']or{}).get('members',[]))==set(members))
 case_results=[]
 for member in members:
  meta=cm[member];f=meta['FINAL.json'];row=next((r for r in rows if r.get('role')==member),None);q=(row or{}).get('fdn_wait_qualification')or{}
  ok=bool(f and row and row.get('actual_waited')is True and row.get('returncode')==0 and row.get('passed_execution')is True and row.get('error')is None and q.get('qualified')is True and q.get('kind')=='FDN_LOW80_3SEED_RESUME55_ACTUAL_WAIT_QUALIFICATION_V2'and f.get('passed_execution')is True and f.get('controls')==400 and f.get('num_envs')==80 and f.get('optimizer_updates')==0 and meta['WORKER_ERROR.json']is None)
  checks['case_'+member]=ok;skill=f['skill']if ok else None
  if ok:
   assert skill['original_74_score_recomputed']is False and skill['no_reset_stitched_credit']is True and skill['low80_request_denominator']==80 and skill['reference_native_cohort_executed']is False and len(skill['pose_rows'])==5 and all(r['first_episode_denominator']==16 for r in skill['pose_rows'])
  case_results.append(dict(case=member,seed=int(member.rsplit('_',1)[1]),execution_qualified=ok,actual_parent_wait_qualification=q or None,source_cache=f.get('source_cache')if f else None,skill=skill,failed_worker_metadata=meta['WORKER_ERROR.json'],D0_D7_fresh_audit_before=f.get('D0_D7_fresh_audit_before')if f else None,D0_D7_fresh_audit_after=f.get('D0_D7_fresh_audit_after')if f else None))
 qualified=all(checks.values());total_credit=sum(x['skill']['first_episode_stable_credits']for x in case_results)if qualified else None;end_credit=sum(x['skill']['credited_and_stable_at_end']for x in case_results)if qualified else None
 result=dict(kind='E3_FROZEN_CANDIDATE_LOW80_THREE_INDEPENDENT_SEED_CONFIRMATION',epoch=time.time(),root=root,source=stage['source'],execution_qualified=qualified,execution_checks=checks,cases=case_results,independent_case_seeds=[20261002,20261003,20261004],controls_per_case=400,seconds_per_case=8.,num_envs_per_case=80,aggregate_denominator=240 if qualified else None,first_episode_stable_credits=total_credit,credited_and_stable_at_end=end_credit,original_E3_74_score_recomputed=False,previous_original_E3_credit=0,previous_original_E3_denominator=74,no_cross_scope_score_combination=True,reference_native_cohorts_executed=False,paired_native_difference=None,reference_comparison_NOT_established=True,source_IO_per_case=1,source_IO_group_expected=3,source_IO_group_actual=sum(x['source_cache']['physical_byte_opens']for x in case_results)if qualified else None,optimizer_updates=0,full_DR_fresh_constructor_per_case=True,decision='RETAIN_CANDIDATE_SCOPED_EVIDENCE_NO_REGISTRY_PROMOTION'if qualified else 'KEEP_PRIOR_REGISTRY_SCOPE_EXECUTION_UNQUALIFIED_NO_SCORE',Registry_v12_and_1cd_unchanged=True,H1_and_other_experts_unchanged=True,goal_complete=False,collector_model_raw_canonical_SDK_operations=0,metadata_paths=dict(closed=str(closed_path),source_stage=str(D/(prefix+'STAGE_RESULT.json'))))
 local(scope_path,result)
 lines=['# 冻结55afa：独立原生low80 × 三seed确认（不是原74评分）','',f'执行资格：**{qualified}**；aggregate信用 **{total_credit}/{240 if qualified else None}**；获得过信用且400控制末帧稳定 **{end_credit}/{240 if qualified else None}**。','', '| Seed | 第一episode连续.5s信用 | 8秒曾获信用且末帧good（非连续25） | 物理终止 |','|---|---:|---:|---:|']
 for x in case_results:
  sk=x['skill'];lines.append(f"| {x['seed']} | {str(sk['first_episode_stable_credits'])+'/80'if sk else 'null：未资格完成'} | {str(sk['credited_and_stable_at_end'])+'/80'if sk else 'null'} | {sk['first_episode_physical_terminated']if sk else 'null'} |")
 lines+=['','每个case是独立process/constructor seed/原fullD0D7与sole fresh reset，五个原合法pose各16、400控制/8秒；无learner/optimizer或checkpoint环境状态恢复。所有第一episode信用在reset前冻结，不移除物理失败样本或拼接多episode。原门限h≥.23/gz<−.984807753/v<.03/omega<.2/双wheel>1N/chassis<1N，连续25控制；终点另列。','', '本组是candidate-only第一批fullDR确认，**母版native配对参考尚未运行，差值null，不声称matched因果**。三个case各source一次physical/hash/CPU decode、wholeN20000未知根CPU保留、14pi上线；组预期三次真实输入，而非全组一次。原E3 74+6仍沿用上一真实0/74/normal物理0/6，不被新80分母覆盖或合并，Registryv12/1cd/H1/其它专家不动，goal保持active。','', '执行失败/未启动时分数null；真实原父privateEX/finiteEX/CownerNone/reserve、actual child/outer wait、App原close、错误和释放由原链闭环，collector只读自身JSON，不重跑资格或SDK、不开模型/raw/C。','',f'[完整结果](<{scope_path.as_posix()}>) / [实际闭环元数据](<{closed_path.as_posix()}>)。本轮全部代码/成功失败/报告待一次有意义feature-only唯一annotated trial归档，main只读，不为Git开模型/旧raw/物理。']
 report_path.write_text('\n'.join(lines)+'\n',encoding='utf8');print('RESUME55_LOW80_HOLDOUT_ADMISSION2_CLOSED '+json.dumps(dict(execution_qualified=qualified,checks=checks,first_episode_stable_credits=total_credit,credited_and_stable_at_end=end_credit,denominator=240 if qualified else None,result=str(scope_path),goal_complete=False)),flush=True)
finally:
 if s is not None:s.close()
 if c is not None:c.close()
