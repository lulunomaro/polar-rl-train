# NEW V2 original-gated case must actually pass close/wait semantics before raw grading.
"""ONE actual grading pass over this NEW own frozen case, not old telemetry.
Artifacts/physical controls are retained with explicit unqualified-close caveat.
No raw download/model/SDK/C/lock operations, and no replay on failure.
"""
from pathlib import Path
import json,sys,time,hashlib,shlex
R=Path(__file__).resolve().parent;marker=R/'FROZEN_W35_BATCH_V2_NEW_RAW_GRADE_STARTED_ONCE.json';out=R/'reports/FROZEN_W35_BATCH_V2_ORIGINAL_SPLIT_ACTUAL_GRADE_V1.json';assert not marker.exists()and not out.exists();p=json.loads((R/'FROZEN_E3_W35_BATCH_V2_LATEST_CLOSED_RESULT_PATH.json').read_bytes());closed=json.loads(Path(p['path']).read_bytes());exit_value=closed['top']['PARENT_EXIT_SCOPE.json'];assert exit_value['all_own_children_waited']and exit_value['original_single_GPU_private_EX_released']and exit_value['original_global_finite_EX_released'];row=next(x for x in closed['rows']if x['role']=='W35');final=row['FINAL'];assert final['role']=='W35'and final['controls']==1600 and final['num_envs']==80;terminal=next(x for x in closed['top']['TERMINAL_ROWS.json']if x['role']=='W35');assert terminal['actual_waited']is True and terminal['passed_execution']is True and row['WORKER_ERROR']is None;source_sha=final['source_cache']['source_SHA'];assert source_sha=='b2f2878ff9aa04ddcd283fe71f5b5924b1bff78b3f04118cfa689244b0665cff';root=closed['root'];case=root+'/cases/W35';data=final['skill']['original_RM70_interval_route_facts']['producer']['path'];assert data==case+'/RM70_SAME_UID_COMMAND_AND_ROUTE_FACTS227.positional.jsonl';script=R/'source_w35_original_row_split_consumer_v1/w35_original_row_split_consumer_v1.py';raw=script.read_bytes();assert len(raw)==26594 and hashlib.sha256(raw).hexdigest()=='8b593a95c62981434dc99fc2475f1b7808b30f809109897e54c9db1f7d9ce879';source_input=json.loads((R/'FROZEN_E3_W35_BATCH_V2_SOURCE_INPUT_ONCE.json').read_bytes())['input_root'];remote_script=source_input+'/w35_original_row_split_consumer_v1.py';grade_output=case+'/W35_ORIGINAL_SPLIT_GRADE_V1.json';argv=[remote_script,'--input',data,'--case-root',case,'--expected-role','W35','--expected-source-sha',source_sha,'--expected-group',closed['group_id'],'--output',grade_output];marker.write_text(json.dumps(dict(epoch=time.time(),root=root,case=case,actual_grading_purpose='One pass of just-produced own positional rows for true original moving/standing counts, not status formatting',raw_not_downloaded=True,consumed_on_attempt=True),indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 for path in(remote_script,grade_output):
  try:s.lstat(path)
  except FileNotFoundError:pass
  else:raise AssertionError('New grade script/output already exists')
 with s.open(remote_script,'wb')as f:f.write(raw)
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -S -B '+' '.join(map(shlex.quote,argv)),timeout=90);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();value=dict(kind='ACTUAL_ORIGINAL_W35_SPLIT_QUALIFIED_EXECUTION_NOT_FULL_EXPERT_GRADUATION',root=root,case_root=case,epoch=time.time(),argv=argv,returncode=rc,stdout=text,stderr=err,qualified_execution=True,close_failure=None,actual_parent_wait_and_release=exit_value,mother_paired_reference=None,skill_improvement=None,full_expert_pass_rate=None,no_model_SDK_C_ops=True,no_raw_download_or_second_raw_open=True);out.write_text(json.dumps(value,indent=2),encoding='utf-8')
 try:
  with s.open(grade_output,'rb')as f:graw=f.read()
 except FileNotFoundError:graw=None
 if graw:value['grade']=json.loads(graw);value['grade_receipt_bytes']=len(graw);value['grade_receipt_SHA']=hashlib.sha256(graw).hexdigest();out.write_text(json.dumps(value,indent=2),encoding='utf-8')
 assert rc in(0,2),err
 print(json.dumps(dict(report=str(out),returncode=rc,grade_present='grade'in value,groups=value.get('grade',{}).get('groups'),unknown_or_integrity_reason=value.get('grade',{}).get('errors'),qualified_execution=True,raw_opened_for_real_grading_once=True),indent=2))
finally:s.close();c.close()
