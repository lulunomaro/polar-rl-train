"""One new actual grade of bound-probe W35 data; no old rows/models or native run."""
from pathlib import Path
import json,sys,time,hashlib,shlex
R=Path(__file__).resolve().parent;prefix='BOUND_ONLY_E3_W35_V1_ADMISSION2';purpose='bound_only_zero_update_admission2_v1';marker=R/(prefix+'_W35_ACTUAL_RAW_GRADE_STARTED_ONCE.json');out=R/'reports'/(prefix+'_W35_ORIGINAL_SPLIT_ACTUAL_GRADE_V1.json');assert not marker.exists()and not out.exists()
ptr=json.loads((R/(prefix+'_LATEST_CLOSED_RESULT_PATH.json')).read_bytes());closed=json.loads(Path(ptr['path']).read_bytes());t=closed['top'];end=t['PARENT_EXIT_SCOPE.json'];assert closed['closed']and closed['qualified_bound_probe_execution']is True and end['all_own_children_waited']and end['original_single_GPU_private_EX_released']and end['original_global_finite_EX_released']and not end['errors'];wait=t['BOUND_PROBE_PARENT_WAITED_ACTUAL_V1.json'];assert wait['actual_parent_p_wait_returned']and wait['returncode']==0 and not wait['controller_errors']and wait['group_id']==closed['group_id']
row=next(x for x in closed['rows']if x['role']=='W35');final=row['FINAL'];assert final['role']=='W35'and final['controls']==1600 and final['num_envs']==80 and final['policy_variant']=='A1_RAW35_ZERO_UPDATE_BOUND_ONLY_TANH_NATIVE_PROBE_V1'and final['optimizer_updates']==0
root=closed['root'];case=root+'/cases/W35';sha=final['source_cache']['source_SHA'];assert sha=='b2f2878ff9aa04ddcd283fe71f5b5924b1bff78b3f04118cfa689244b0665cff';data=final['skill']['original_RM70_interval_route_facts']['producer']['path'];assert data==case+'/RM70_SAME_UID_COMMAND_AND_ROUTE_FACTS227.positional.jsonl'
script=R/'source_w35_original_row_split_consumer_v1/w35_original_row_split_consumer_v1.py';raw=script.read_bytes();assert(len(raw),hashlib.sha256(raw).hexdigest())==(26594,'8b593a95c62981434dc99fc2475f1b7808b30f809109897e54c9db1f7d9ce879')
source_input=json.loads((R/(prefix+'_SOURCE_INPUT_ONCE.json')).read_bytes())['input_root'];remote_script=source_input+'/w35_original_row_split_consumer_v1.py';grade_output=case+'/W35_ORIGINAL_SPLIT_GRADE_BOUND_ONLY_ZERO_UPDATE_ADMISSION2_V1.json';argv=[remote_script,'--input',data,'--case-root',case,'--expected-role','W35','--expected-source-sha',sha,'--expected-group',closed['group_id'],'--output',grade_output]
marker.write_text(json.dumps(dict(epoch=time.time(),root=root,case=case,purpose=purpose,actual_grading_purpose='Stream ONLY this new probe artifact once for original moving/standing predicates',raw_not_downloaded=True,consumed_on_attempt=True),indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 for path in(remote_script,grade_output):
  try:s.lstat(path)
  except FileNotFoundError:pass
  else:raise AssertionError('New grade artifact already exists; no replay')
 with s.open(remote_script,'wb')as f:f.write(raw)
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -S -B '+' '.join(map(shlex.quote,argv)),timeout=90);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();v=dict(kind='ACTUAL_NEW_BOUND_ONLY_W35_ORIGINAL_SPLIT_GRADE',purpose=purpose,policy_variant=final['policy_variant'],probe_training_updates=0,root=root,case_root=case,epoch=time.time(),argv=argv,returncode=rc,stdout=text,stderr=err,qualified_execution=True,actual_parent_wait_and_release=end,external_bound_parent_actual_wait=wait,matched_UID_pose_cohort=None,relative_or_causal_training_improvement=None,full_expert_pass_rate=None,no_model_SDK_C_ops=True,no_raw_download_or_second_raw_open=True);out.write_text(json.dumps(v,indent=2),encoding='utf-8')
 try:
  with s.open(grade_output,'rb')as f:graw=f.read()
 except FileNotFoundError:graw=None
 if graw:v.update(grade=json.loads(graw),grade_receipt_bytes=len(graw),grade_receipt_SHA=hashlib.sha256(graw).hexdigest());out.write_text(json.dumps(v,indent=2),encoding='utf-8')
 assert rc in(0,2),err;print(json.dumps(dict(report=str(out),returncode=rc,qualified=True,zero_training_updates=True,groups=v.get('grade',{}).get('groups'),integrity_errors=v.get('grade',{}).get('errors')),indent=2))
finally:s.close();c.close()
