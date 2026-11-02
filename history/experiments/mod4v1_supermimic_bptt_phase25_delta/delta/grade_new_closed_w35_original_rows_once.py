"""One actual grade per NEW reference or candidate artifact; no raw download.
Only published closure metadata locally; remotely stream each new data file once.
No models/SDK/C/locks/native calls, and no status/Git reread of telemetry.
"""
from pathlib import Path
import json,sys,time,hashlib,shlex,argparse
parser=argparse.ArgumentParser();parser.add_argument('--purpose',choices=('reference_v1','candidate_v2_admission2'),required=True);a=parser.parse_args();R=Path(__file__).resolve().parent
if a.purpose=='reference_v1':
 prefix='EMBEDDED_TEACHER_E3_W35_V1';label='ORIGINAL_EMBEDDED_TEACHER_REFERENCE';pointer=R/(prefix+'_LATEST_CLOSED_RESULT_PATH.json');source_input_marker=R/(prefix+'_SOURCE_INPUT_ONCE.json')
else:
 prefix='FROZEN_E3_W35_BATCH_V2_ADMISSION2';label='A1_RAW35_CANDIDATE';pointer=R/(prefix+'_LATEST_CLOSED_RESULT_PATH.json');source_input_marker=R/(prefix+'_SOURCE_INPUT_ONCE.json')
marker=R/(prefix+'_W35_ACTUAL_RAW_GRADE_STARTED_ONCE.json');out=R/'reports'/(prefix+'_W35_ORIGINAL_SPLIT_ACTUAL_GRADE_V1.json');assert not marker.exists()and not out.exists();ptr=json.loads(pointer.read_bytes());closed=json.loads(Path(ptr['path']).read_bytes());t=closed['top'];end=t['PARENT_EXIT_SCOPE.json'];assert closed['closed']and end['all_own_children_waited']and end['original_single_GPU_private_EX_released']and end['original_global_finite_EX_released'];row=next(x for x in closed['rows']if x['role']=='W35');final=row['FINAL'];assert final['role']=='W35'and final['controls']==1600 and final['num_envs']==80;root=closed['root'];case=root+'/cases/W35';source_sha=final['source_cache']['source_SHA'];assert source_sha=='b2f2878ff9aa04ddcd283fe71f5b5924b1bff78b3f04118cfa689244b0665cff';data=final['skill']['original_RM70_interval_route_facts']['producer']['path'];assert data==case+'/RM70_SAME_UID_COMMAND_AND_ROUTE_FACTS227.positional.jsonl'
if a.purpose=='reference_v1':
 qualified=closed['qualified_reference_execution']is True;assert final['policy_variant']=='ORIGINAL_EMBEDDED_TEACHER_MEAN_FROM_FULL_A1_V1';external_wait=t['REFERENCE_PARENT_WAITED_ACTUAL_V1.json'];assert external_wait['actual_parent_p_wait_returned']and external_wait['group_id']==closed['group_id']
else:
 terminal=t['TERMINAL_ROWS.json'];qualified=not end['errors']and len(terminal)==2 and all(x['actual_waited']and x['passed_execution']for x in terminal);external_wait=None
script=R/'source_w35_original_row_split_consumer_v1/w35_original_row_split_consumer_v1.py';raw=script.read_bytes();assert len(raw)==26594 and hashlib.sha256(raw).hexdigest()=='8b593a95c62981434dc99fc2475f1b7808b30f809109897e54c9db1f7d9ce879';source_input=json.loads(source_input_marker.read_bytes())['input_root'];remote_script=source_input+'/w35_original_row_split_consumer_v1.py';grade_output=case+'/W35_ORIGINAL_SPLIT_GRADE_'+a.purpose.upper()+'_V1.json';argv=[remote_script,'--input',data,'--case-root',case,'--expected-role','W35','--expected-source-sha',source_sha,'--expected-group',closed['group_id'],'--output',grade_output];marker.write_text(json.dumps(dict(epoch=time.time(),root=root,case=case,purpose=a.purpose,actual_grading_purpose='Once stream NEW own positional rows for original moving/standing conditions',raw_not_downloaded=True,consumed_on_attempt=True),indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 for path in(remote_script,grade_output):
  try:s.lstat(path)
  except FileNotFoundError:pass
  else:raise AssertionError('New grade script/output already exists; do not replay')
 with s.open(remote_script,'wb')as f:f.write(raw)
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -S -B '+' '.join(map(shlex.quote,argv)),timeout=90);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();value=dict(kind='ACTUAL_NEW_W35_ORIGINAL_CONDITION_ROW_GRADE_V1',purpose=a.purpose,policy_variant=label,root=root,case_root=case,epoch=time.time(),argv=argv,returncode=rc,stdout=text,stderr=err,qualified_execution=qualified,actual_parent_wait_and_release=end,external_reference_parent_actual_wait=external_wait,mother_paired_UID_reference=None,relative_skill_improvement=None,full_expert_pass_rate=None,no_model_SDK_C_ops=True,no_raw_download_or_second_raw_open=True);out.write_text(json.dumps(value,indent=2),encoding='utf-8')
 try:
  with s.open(grade_output,'rb')as f:graw=f.read()
 except FileNotFoundError:graw=None
 if graw:value['grade']=json.loads(graw);value['grade_receipt_bytes']=len(graw);value['grade_receipt_SHA']=hashlib.sha256(graw).hexdigest();out.write_text(json.dumps(value,indent=2),encoding='utf-8')
 assert rc in(0,2),err;print(json.dumps(dict(report=str(out),purpose=a.purpose,returncode=rc,qualified_execution=qualified,groups=value.get('grade',{}).get('groups'),integrity_errors=value.get('grade',{}).get('errors'),raw_streamed_for_actual_grading_once=True),indent=2))
finally:s.close();c.close()
