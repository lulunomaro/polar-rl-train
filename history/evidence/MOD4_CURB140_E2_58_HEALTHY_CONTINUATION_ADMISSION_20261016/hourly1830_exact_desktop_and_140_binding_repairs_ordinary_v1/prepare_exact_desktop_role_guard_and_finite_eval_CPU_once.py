from pathlib import Path
import sys,json,time,copy,ast,hashlib,traceback
D=Path(__file__).resolve().parent;E=D/'curb140_frozen35_3060_v1';R=D/'reports';sys.path.insert(0,str(E));import transport_249_exact_deepseek_desktop_role_v4 as t
def main():
 out=R/'EXACT_DESKTOP_ROLE_GUARD_NEGATIVES_AND_EVAL_UNUSED_CPU_ACTUAL.json';assert not out.exists();expected=t.known_identity();assert t.exact_desktop(expected,expected);bad=0
 for path,value in [(('process','pid'),-1),(('process','creation'),0),(('process','exe'),'elsewhere'),(('process','argv'),['python','train.py']),(('parent','pid'),-1),(('parent','creation'),0),(('parent','exe'),'elsewhere'),(('parent','argv'),['python','train.py']),(('binary_SHA',),'0'*64)]:
  x=copy.deepcopy(expected)
  if len(path)==1:x[path[0]]=value
  else:x[path[0]][path[1]]=value
  assert not t.exact_desktop(x,expected);bad+=1
 source=t.guard_code();ast.parse(source);p=E/'EXACT_CURRENT_DESKTOP_ORIGINAL_GUARD_V4_CPU_FROZEN.py.txt';p.write_text(source,encoding='utf8');out.write_text(json.dumps(dict(epoch=time.time(),passed_CPU_only=True,negative_identities_rejected=bad,guard_source_path=str(p),guard_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),actual_signed_desktop_role_only=True,original_shared_msvcrt_unknown_compute_and_source_contract_unchanged=True,no_payload_physics_threshold_SDK_or_other_process_change=True,native_and_full_cases_still_unused=True),indent=2),encoding='utf8');print(json.dumps(dict(passed_CPU_only=True,bad_identities_rejected=bad)))
if __name__=='__main__':
 try:main()
 except BaseException:(R/('DESKTOP_ROLE_GUARD_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_GPU=True),indent=2),encoding='utf8');raise
