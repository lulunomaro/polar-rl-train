"""Preseal text-only exact reader extension; no network/model/asset reads."""
from pathlib import Path
import ast,hashlib,json,time,traceback
B=Path(__file__).resolve().parent
def H(b):return hashlib.sha256(b).hexdigest()
def save(n,v):
 with (B/n).open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2)
def change(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def main():
 p=B/'E3_source210_actual_receipts_readonly_CODE_v4.py';before=p.read_bytes();tree=ast.parse(before);code=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='CODE' for x in n.targets));old=code
 code=change(code,"nominal=sup['creation']+1800","diagnostic=F/'q34_existing_queries/E3_RESET_REQUEST_EXISTING_CLOSURE_QUERY_DIAGNOSTIC_ACTUAL.json'\nquery_final=F/'E3_INITIAL24_ORIGINAL_QUERY_FINALIZATION_ACTUAL.json'\nnominal=sup['creation']+1800")
 code=change(code,"if restore.exists() and native.exists() or errors or tt is not None or time.monotonic()>=limit:break","if restore.exists() and native.exists() and query_final.exists() or errors or tt is not None or time.monotonic()>=limit:break")
 code=change(code,"paths=[J/n for n in", "qf=read(query_final);qd=read(diagnostic)\nevents={r['event'] for r in qd['records']} if qd else set()\nquery_valid=bool(qf and qf.get('diagnostic_valid') and qf.get('original_methods_restored') and qd and qd.get('diagnostic_valid') and not qd.get('errors') and {'DECLARED_FALL_BEFORE_ORIGINAL_WRITE','ORIGINAL_JOINT_WRITE_REQUEST','ORIGINAL_ROOT_WRITE_REQUEST','ORIGINAL_QUEUE_APPLY_RESULT','ORIGINAL_CLOSURE_QUERY_CACHED_INPUT_AND_RESULT'}<=events)\npaths=[J/n for n in")
 code=change(code,']+[restore,native]+errors',']+[restore,native,diagnostic,query_final,F/\'E3_ORIGINAL_QUERY_HOOK_INSTALLED_BEFORE_RESUME.json\']+errors')
 code=change(code,'requested24_initial_controls_complete=full,','requested24_initial_controls_complete=full,passed_original_query_diagnostic=query_valid,query_finalization=qf,original_query_diagnostic=qd,physical_postwrite_or_first_substep_not_observed=True,')
 ast.parse(code);p.write_bytes(('"""NEW known-own initial24 diagnostic first/terminal. No model or GPU API."""\nCODE='+repr(code)+'\n').encode())
 save('READER_PRESEAL_ORIGINAL_TEXT_AND_QUERY_EXTENSION_PROOF.json',dict(original_CODE_SHA=H(old.encode()),selected_CODE_SHA=H(code.encode()),original_CODE=old,selected_CODE=code,no_normal900_850_or_first360_or_identity_state_text_integrity_logic_changed=True,only_wait_for_final_diagnostic_and_collect_same_own_texts=True))
 mf=B/'E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json';m=json.loads(mf.read_bytes())
 for row in m['files']:
  if row['relative']==p.name:row.update(bytes=p.stat().st_size,SHA=H(p.read_bytes()))
 mf.write_bytes((json.dumps(m,indent=2)+'\n').encode())
 print(json.dumps(dict(prepared=True,selected_CODE_SHA=H(code.encode()),manifest_SHA=H(mf.read_bytes()))))
if __name__=='__main__':
 try:main()
 except BaseException:save('READER_PRESEAL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc()));raise
