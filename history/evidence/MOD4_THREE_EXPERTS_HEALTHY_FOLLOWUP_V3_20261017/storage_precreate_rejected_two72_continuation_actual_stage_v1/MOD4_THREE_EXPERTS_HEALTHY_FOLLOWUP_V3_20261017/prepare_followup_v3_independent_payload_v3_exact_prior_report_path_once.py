from pathlib import Path
import sys,time,json,ast,importlib.util,traceback
F=Path(__file__).resolve().parent;R=F/'reports'
def main():
 p=F/'prepare_recovered_three_finals_same_scope_next_finite_payloads_CPU_v2_once.py';s=p.read_text('utf8');assert "Q=V/'payload_v2'" in s and "U/'reports/THREE_SLOT_ACTUAL_CLOSED_SOURCES_FULL_CPU_FROZEN_PAYLOADS_PREPARED.json'" in s;s=s.replace("Q=V/'payload_v2'","Q=V/'payload_v3'").replace("U/'reports/THREE_SLOT_ACTUAL_CLOSED_SOURCES_FULL_CPU_FROZEN_PAYLOADS_PREPARED.json'","U/'reports/RECOVERED_THREE_FINALS_FULL_CPU_AND_NEW_SAME_SCOPE_NATIVE_PAYLOADS_PREPARED_ACTUAL.json'");ast.parse(s);q=F/'prepare_recovered_three_finals_same_scope_next_finite_payloads_CPU_v3_once.py';assert not q.exists();q.write_text(s,encoding='utf8');sp=importlib.util.spec_from_file_location('new_actual_followup_sources_CPU_v3',q);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);m.main();from finish_unchanged_runtime_proofs_and_new_deployer_CPU_only import finish;finish('payload_v3')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('FOLLOWUP_V3_CPU_V3_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_remote_GPU_or_budget=True),f,indent=2)
  raise
