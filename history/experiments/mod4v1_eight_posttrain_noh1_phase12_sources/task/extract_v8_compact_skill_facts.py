from pathlib import Path
import json,re
R=Path(__file__).resolve().parent;loc=json.loads((R/'reports/NINE_SINGLE_GPU_V8_LATEST_CLOSED_RESULT_PATH.json').read_bytes());v=json.loads(Path(loc['path']).read_bytes());D=Path(loc['path']).parent;out=[];starts=[];ends=[];assert v['actual_execution_passed_count']==9
for r in v['rows']:
 f=r['final'];start=f.get('first_eval_epoch',f.get('wall_start_epoch'));end=f.get('last_eval_epoch',f.get('wall_end_epoch'));assert start>=v['common_barrier']['epoch']and end>start;starts.append(start);ends.append(end);x={'role':r['role'],'seconds':f['seconds'],'controls':f['controls'],'execution_passed':r['passed_execution'],'RC':r['wait']['returncode'],'start_epoch':start,'end_epoch':end,'wall_seconds':end-start,'source_cache':f['source_cache'],'termination_events':f.get('termination_events_by_reason',f.get('termination_counts')),'actual_started_evidence':'FINAL.wallstart+group_barrier'if'wall_start_epoch'in f else'WORKER_EVAL_STARTED+FINAL.first_eval_epoch','skill':f.get('skill')}
 if 'metrics'in f:
  m=f['metrics'];x['metric_kind']=m.get('kind');x['original_endpoint_groups']=m.get('groups');x['original_endpoint_rows_count']=len(m.get('rows',[]));x['original_scope_no_new_totalgrade']=True
  rr=m.get('rows',[])
  if rr:x['stand_no_ordinary_failure']={'total':sum(z['group']=='stand'for z in rr),'no_failure':sum(z['group']=='stand'and z['first_ordinary_failure_control']is None for z in rr)}
 if 'skill'in f:
  skill=f['skill'];x['skill']={k:z for k,z in skill.items()if k not in('body_velocity_absolute_error_time_integral_per_env','root_before_and_last_terminal_world_xyz_per_env')};err=skill.get('body_velocity_absolute_error_time_integral_per_env')
  if err:x['diagnostic_fullwindow_body_abs_error_mean_vx_vy_yaw']=[sum(z[i]for z in err)/(len(err)*f['seconds'])for i in range(3)]
 raw=(D/r['role']/'SDK_FULL_STDOUT_STDERR.log').read_bytes().decode('utf-8',errors='replace');bad=[line for line in raw.splitlines()if re.search(r'(?i)overflow|out of memory|CUDA error|buffer.*(too small|insufficient|exceeded)|contact.*capacity.*exceeded',line)];x['closed_stdout_error_or_capacity_lines']=bad;assert not bad
 out.append(x)
assert max(starts)<min(ends);memory=json.loads((D/'GROUP_GPU_MEMORY_SAMPLES.json').read_bytes());report={'kind':'NINE_ACTUAL_FRESH80_SINGLE_GPU_FACTS_NOT_FULLSKILL_GLOBALPASS','root':v['root'],'group_id':v['group_id'],'GPU_UUID':v['GPU_UUID'],'all9_execution_RC0':True,'all9_actual_control_window_overlap_seconds':min(ends)-max(starts),'min_GPU_free_MiB_observed':min(x['free_MiB']for x in memory),'max_GPU_utilization_percent_observed':max(x['utilization_percent']for x in memory),'original_parent_allwaited_EXreleased':all(v[k]for k in('all_own_children_waited','single_GPU_EX_released','global_finite_EX_released')),'rows':out,'newPPO_BPTT_GO_ledgerwrites':0,'freshN80_not_saved20k_projection':True};p=R/'reports/NINE_V8_COMPACT_FIRSTHAND_SKILL_FACTS.json';assert not p.exists();p.write_text(json.dumps(report,indent=2),encoding='utf-8');print(p)
for x in out:
 y={k:z for k,z in x.items()if k not in('source_cache',)};print(json.dumps(y,ensure_ascii=False))
print('PARALLEL',report['all9_actual_control_window_overlap_seconds'],'MINFREE',report['min_GPU_free_MiB_observed'])
