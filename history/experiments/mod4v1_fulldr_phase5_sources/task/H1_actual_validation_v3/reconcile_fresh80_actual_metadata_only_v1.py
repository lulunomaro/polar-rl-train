"""Append-only reader reconciliation of an ACTUALLY completed fresh80 SDK run.
No SDK/PT/GPU/budget, no raw false overwrite, no once replay or codehotpatch.
"""
from pathlib import Path
import datetime,hashlib,json,sys
B=Path(__file__).resolve().parent;T=B.parent;sys.path.insert(0,str(T));from project_connector import connect72
loc=json.loads((B/'CURRENT_FRESH80_CASE.json').read_text(encoding='utf-8'));root=loc['remote_root'];report=dict(kind='H1_FRESH80_PARENT_READER_BASENAME_ERROR_RECONCILIATION',remote_root=root,PT_SDK_GPU_budget_operations=0,original_parent_false_preserved=True)
client=sf=None
try:
 client=connect72();sf=client.open_sftp();values={};shas={}
 for rel in ['H1_NORMAL_FRESH80_PLAN.json','FINAL.json','TERMINAL_ROWS.json','PARENT_EXIT_SCOPE.json','gpu1/H1_FRESH80_COMPLETE.json','gpu1/ENV_CLOSE_RETURNED.json','gpu1/APP_CLOSING.json','gpu1/TASK.json','probe_h1_normal_fresh80.py','supervise_h1_normal_fresh80.py']:
  with sf.open(root+'/'+rel,'rb') as f:raw=f.read()
  shas[rel]=hashlib.sha256(raw).hexdigest()
  if rel.endswith('.json'):values[rel]=json.loads(raw)
  elif rel=='supervise_h1_normal_fresh80.py':report['actual_mistyped_reader_line']=[l.strip() for l in raw.decode().splitlines() if 'data=json.loads' in l]
 plan=values['H1_NORMAL_FRESH80_PLAN.json'];proof=values['gpu1/H1_FRESH80_COMPLETE.json'];closed=values['PARENT_EXIT_SCOPE.json'];row=values['TERMINAL_ROWS.json'][0]
 signed=next(r for r in plan['files'] if r['relative']=='probe_h1_normal_fresh80.py');assert signed['sha256']==shas['probe_h1_normal_fresh80.py']==plan['worker_SHA']
 assert values['FINAL.json']['passed'] is False and row['data'] is None
 assert row['returncode']==0 and row['actual_waited'] and row['env_close_returned'] and row['App_close_bridge']
 assert closed['all_own_children_waited'] and closed['original_private_lock_released'] and closed['original_shared_lock_released'] and not closed['errors']
 assert proof['passed'] and proof['num_envs']==80 and proof['controls']==24 and proof['physics_callbacks']==proof['H1_callbacks']==192 and proof['feedback_samples']==48
 assert proof['asset_SHA']=='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3' and proof['contract_SHA']=='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
 assert proof['actual_mild_DR_audit_after']['actual_parameters_pass'] and all(v==0 for v in proof['sentinels'].values()) and proof['model_opens']==0
 assert proof['exact_H1_bank_compatibility']['pose_ranges']['all_poses']==133 and proof['exact_H1_bank_compatibility']['pose_ranges']['original_height_filter_selected_poses']==74
 try:
  sf.stat(root+'/gpu1/H1_FRESH80_ORIGINAL_ERROR.json');raise RuntimeError('Actual SDKerror exists')
 except FileNotFoundError:pass
 except OSError as e:
  if getattr(e,'errno',None)!=2:raise
 report.update(passed_actual_fresh_worker_and_clean_release=True,actual_original_final_summary_passed=False,actual_complete=proof,original_terminal_row=row,original_exit_scope=closed,original_file_SHA=shas,signed_worker_identity= signed,metadata_reader_error_only=True,no_Ready_or_GO_created=True,no_consumed_SDK_replay=True)
 with sf.open(root+'/H1_FRESH80_ACTUAL_READER_RECONCILIATION_V1.json','wx') as f:f.write(json.dumps(report,indent=2))
 dest=T/'reports'/('H1_fresh80_actual_reader_reconciliation_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');dest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 with (B/'FRESH80_RECONCILIATION_LOCATOR.json').open('x',encoding='utf-8') as f:json.dump(dict(local_report=str(dest),remote_report=root+'/H1_FRESH80_ACTUAL_READER_RECONCILIATION_V1.json',report_SHA=hashlib.sha256(json.dumps(report,indent=2).encode()).hexdigest()),f,indent=2)
 print(json.dumps(dict(actual_fresh80_passed=True,original_parent_false_preserved=True,local_report=str(dest),remote_root=root,SDK_PT_GPU_operations=0),indent=2))
finally:
 if sf:sf.close()
 if client:client.close()
