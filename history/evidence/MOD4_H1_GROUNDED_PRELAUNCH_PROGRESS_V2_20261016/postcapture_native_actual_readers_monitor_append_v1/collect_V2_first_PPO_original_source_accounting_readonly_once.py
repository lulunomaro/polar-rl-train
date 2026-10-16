"""One material-first-PPO source receipt; no target connection or canonical writes."""
from pathlib import Path
import sys,json,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D));from collect_V2_actual_native_CPU_and_first_immutable_production_finite_once import SOURCE,code,t,S
def main():
 p=R/'V2_FIRST_IMMUTABLE_PPO_SOURCE_ORIGINAL_ACCOUNTING_CURRENT_READONLY_ACTUAL.json';assert not p.exists();assert json.loads((R/'V2_ACTUAL_NATIVE_MODELS_FIRST_IMMUTABLE_PRODUCTION_LOCAL_CPU_VERIFIED.json').read_bytes())['passed'];c=None
 try:c=t.connect();v=code(c,t.PY,SOURCE,S);p.write_text(json.dumps(v,indent=2),encoding='utf8');a=v['original_canonical_snapshot']['active_segment'];print(json.dumps(dict(epoch=v['epoch'],owner_processes=v['actual_owner_processes'],active_kind=(a or {}).get('kind'),actual_two_fcntl=v['actual_two_fcntl'],own_completed=len(v['own_matching_completed_segments']),no_budget_write_or_extra_window=True)))
 finally:t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:(R/('V2_FIRST_PPO_SOURCE_RECEIPT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_runtime_retry_or_budget_write=True),indent=2),encoding='utf8');raise
