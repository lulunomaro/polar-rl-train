"""Keep the strict false; audit all existing raw on CPU with no admission/GO output."""
from pathlib import Path
import ast,json,time,hashlib
B=Path(__file__).resolve().parent;R=B/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 c=json.loads((R/'CE3_OWN_NATIVE_FIRST_COMPLETE_MERGED_MISSING_V2_BOUND_COLLECTION_ACTUAL.json').read_bytes());assert c['actual_transport_returned'] and c['target']['errors'] and not c['owner']['rows']['OWNER_CURRENT.json']['go'] and not c['target']['own_processes'] and not c['owner']['own_processes'];assert c['original_account']['original_canonical']['active_segment'] is None
 text=(B/'payload/h1/h1_owned_dual_FP64_mean_reference_same_bound_v1.py').read_text('utf8')
 old=" assert maxima['torch64_maxabs']<=1e-4 and maxima['numpy64_maxabs']<=1e-4,maxima"
 assert old in text;text=text.replace(old," maxima['strict_same_absolute1e4_pass']=bool(maxima['torch64_maxabs']<=1e-4 and maxima['numpy64_maxabs']<=1e-4)\n maxima['diagnostic_only_never_admission']=True")
 helper=B/'ce3_existing_native_dual_mean_strict_false_diagnostic_only_v1.py'
 with helper.open('x',encoding='utf8') as f:f.write(text)
 text=(B/'payload/h1/review_H1_prelaunch_v2_native_allrows_CPU_v1.py').read_text('utf8')
 text=text.replace('from h1_owned_dual_FP64_mean_reference_same_bound_v1 import audit_saved_mean','from ce3_existing_native_dual_mean_strict_false_diagnostic_only_v1 import audit_saved_mean')
 assert text.count('assert maxmean<=1e-4;control_count')==1
 text=text.replace('assert maxmean<=1e-4;control_count','control_count')
 text=text.replace('passed=True,prelaunch_proxy_actual_live_term_maxabs','passed=False,diagnostic_only_not_native_admission=True,strict_actor_reference_pass=(maxmean<=1e-4),all_other_original_checks_passed=True,prelaunch_proxy_actual_live_term_maxabs')
 text=text.replace('H1_PRELAUNCH_V2_NATIVE180_ALL_ROWS_CPU_ADMITTED.json','H1_CE3_NATIVE180_STRICT_ACTOR_FALSE_ALL_OTHER_ROWS_DIAGNOSTIC_CPU_ACTUAL.json')
 text=text.replace('H1_NATIVE_CPU_ORIGINAL_ERROR_','H1_CE3_NATIVE_CPU_DIAGNOSTIC_ORIGINAL_ERROR_')
 reader=B/'review_existing_ce3_native_strict_actor_false_all_other_rows_diagnostic_CPU_once.py'
 for p,t in [(reader,text)]:
  ast.parse(t)
  with p.open('x',encoding='utf8') as f:f.write(t)
 ast.parse(helper.read_text('utf8'))
 with (R/'CE3_EXISTING_NATIVE_NUMERICAL_REJECTION_CPU_DIAGNOSTIC_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),original_admission_false_retained=True,no_native_or_GPU_replay_or_GO_or_protocol_permission=True,all_other_original_physics_phase_source_checks_retained=True,reference_raw_mean_failure_collected_as_diagnostic_only=True,files=[dict(path=str(p),SHA=H(p)) for p in (helper,reader)],new_admitted_filename_never_written=True),f,indent=2)
 print(json.dumps(dict(prepared_diagnostic_only=True,no_admission=True)))

if __name__=='__main__':main()
