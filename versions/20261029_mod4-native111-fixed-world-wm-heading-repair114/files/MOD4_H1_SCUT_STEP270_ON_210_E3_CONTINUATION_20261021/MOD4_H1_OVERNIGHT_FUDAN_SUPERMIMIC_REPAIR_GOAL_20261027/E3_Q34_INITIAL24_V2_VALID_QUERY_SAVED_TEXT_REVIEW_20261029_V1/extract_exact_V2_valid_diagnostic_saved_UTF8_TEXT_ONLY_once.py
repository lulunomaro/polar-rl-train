"""One new saved-first JSON read, exact own producer paths/SHA. No host/arrays IO."""
from pathlib import Path
import hashlib,json,time,traceback
B=Path(__file__).resolve().parent;L=B.parent
INPUT=L/'E3_97_Q34_INITIAL24_DEVICE_ROUTING_CASE_SOURCE_20261029_V2/reports/E3_SOURCE210_FIRST_ORIGINAL_RETURNED_ACTUAL.json'
def H(b):return hashlib.sha256(b).hexdigest()
def put(n,v):
 with (B/n).open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 put('NEW_VALID_E3_QUERY_SAVED_TEXT_PURPOSE_CONSUMED_BEFORE_ONE_READ.json',dict(epoch=time.time(),source_path=str(INPUT),purpose='original74_reset_then_q34_requested_writes_then_original_control_end_closure_chain',model_NPZ_raw_or_host_reads=0))
 raw=INPUT.read_bytes();v=json.loads(raw);rows={r['relative']:r for r in v['complete_original_own_stage_UTF8']};assert len(rows)==len(v['complete_original_own_stage_UTF8']);evidence=[];values={}
 paths={'query':'frozen_regression/q34_existing_queries/E3_RESET_REQUEST_EXISTING_CLOSURE_QUERY_DIAGNOSTIC_ACTUAL.json','finalization':'frozen_regression/E3_INITIAL24_ORIGINAL_QUERY_FINALIZATION_ACTUAL.json','hook_install':'frozen_regression/E3_ORIGINAL_QUERY_HOOK_INSTALLED_BEFORE_RESUME.json','native24':'frozen_regression/ACTUAL_NATIVE24_E3_40050_CLOCK_QUEUE.json','terminal':'FROZEN_E3_ORIGINAL_WAITED_TERMINAL_ACTUAL.json','task':'FROZEN_CASE_TASK.json','restore':'frozen_regression/ACTUAL_E3_97_CUDA_FULLRESTORE_BEFORE_MEAN_ACTION.json'}
 for name,rel in paths.items():
  r=rows[rel];b=r['UTF8'].encode();assert len(b)==r['bytes'] and H(b)==r['SHA'];evidence.append({k:r[k] for k in ('path','relative','bytes','SHA')});value=json.loads(b);values[name]=value
  if name!='restore':
   with (B/('EXACT_'+name+'_ORIGINAL_SAVED_UTF8.json')).open('xb') as f:f.write(b)
 assert v['passed_first_actual_E3_CUDA_fullrestore_native24_queue'] and v['requested24_controls_physically_completed'] and v['passed_original_query_diagnostic'] and v['original_terminal_and_allownout_proven']
 q=values['query'];assert q==v['original_query_diagnostic'] and q['diagnostic_valid'] and not q['errors'] and len(q['records'])==95 and not q['retention_limited']
 # Only metadata scalar keys relevant to actual restore/old reset proof. Do not inspect
 # tensor arrays or derive model statistics from the already saved restore text.
 restore_scalars=[]
 wanted={'initial30q_error_rad','original_qerr_zero_guard_completed_before_declared_fall_axis','original_new_D0_D7_episode_then_geometry_conditioned_initial_fall','source_SHA','source_sha256','original_q30_bank_pose','legal_original_q30_bank_pose','original74_reset_retained','original_D0_D7_full_source_restore','original_D1_D7_full_source_restore','new_physical_episode','all_episode_counters_incremented_once','command_CUDA_disk_roundtrip_exact','selected_pose_index'}
 def walk(x,path=''):
  if isinstance(x,dict):
   for k,val in x.items():
    p=path+'/'+str(k)
    if (k in wanted or 'qerr' in k.lower() or 'declared_fall' in k.lower()) and (val is None or isinstance(val,(str,int,float,bool))):restore_scalars.append(dict(path=p,value=val))
    if isinstance(val,dict) or isinstance(val,list) and val and isinstance(val[0],dict):walk(val,p)
  elif isinstance(x,list):
   for i,val in enumerate(x):
    if isinstance(val,dict):walk(val,path+'/'+str(i))
 walk(values['restore'])
 report=dict(input_path=str(INPUT),input_bytes=len(raw),input_SHA=H(raw),selected_exact_original_UTF8_evidence=evidence,actual_first_flags={k:v[k] for k in ('passed_first_actual_E3_CUDA_fullrestore_native24_queue','requested24_controls_physically_completed','passed_original_query_diagnostic','original_terminal_and_allownout_proven','passed_original_frozen_execution','requested24_initial_controls_complete')},original_errors=v['original_errors'],integrity=v['integrity'],restore_core_scalar_summary={k:x for k,x in values['restore'].items() if not isinstance(x,(dict,list))},original_restore_reset_evidence_scalars=restore_scalars,no_original_restore_tensor_arrays_statistically_reanalysed=True,no_first_host_reader_or_original_model_NPZ_raw_gz_called=True)
 put('EXACT_SAVED_TEXT_EXTRACTION_AND_ORIGINAL_RESTORE_METADATA_EVIDENCE.json',report)
 print(json.dumps(dict(passed_extraction=True,records=len(q['records']),errors=len(q['errors']),events={k:sum(r['event']==k for r in q['records']) for k in sorted({r['event'] for r in q['records']})},restore_scalar_rows=len(restore_scalars))))
if __name__=='__main__':
 try:main()
 except BaseException:put('SAVED_TEXT_EXTRACTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_remote_or_model=True));raise
