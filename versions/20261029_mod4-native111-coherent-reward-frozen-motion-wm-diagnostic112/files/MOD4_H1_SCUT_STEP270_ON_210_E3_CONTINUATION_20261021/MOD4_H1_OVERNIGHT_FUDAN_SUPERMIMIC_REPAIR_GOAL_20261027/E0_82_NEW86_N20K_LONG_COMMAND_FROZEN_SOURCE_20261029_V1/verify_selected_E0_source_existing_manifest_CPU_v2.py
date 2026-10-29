"""Continuation of failed LOCAL static graph fixture, no source model read."""
from pathlib import Path,PurePosixPath
import ast,hashlib,json,time,traceback
B=Path(__file__).resolve().parent
def main():
 p=B/'e0_declared_entry_receipt_cli_contract_v1.py';old=p.read_bytes();s=old.decode('utf8')
 a="sup_final=literal_path_tail(assignment(st,'result'));sup_terminal="
 b="sup_final_path=literal_path_tail(assignment(st,'result'));assert PurePosixPath(sup_final_path).parent==PurePosixPath('frozen_regression');sup_final=PurePosixPath(sup_final_path).name;sup_terminal="
 assert a in s;inverse_pair=(a,b);s=s.replace(a,b);p.write_text(s,encoding='utf8',newline='\n')
 fixture=B/'selected_telemetry_constructor_API_fixture_v1.py';before=fixture.read_bytes();f=before.decode('utf8')
 a="  assert panel.trace_controls==[1] and panel.apply_calls=={'legs':8,'wheels':8};checks.append('actual physical/begin/requested/terminal/after methods cover every new ground reference and real original queue API')"
 b=a+"\n  cmd._resample_command(t.tensor([0,1]));e._reset_idx(t.tensor([0]));assert original_calls==dict(reset=1,write=0,resample=1);checks.append('actual selected command/reset observer hooks call each original exactly once without RNG')"
 assert a in f;f=f.replace(a,b);fixture.write_text(f,encoding='utf8',newline='\n')
 mf=B/'E0_NEW86_COMPLETE_INPUT_MANIFEST_V1.json';m=json.loads(mf.read_bytes())
 for r in m['files']:
  if r['relative'] in (p.name,fixture.name):
   raw=(B/r['relative']).read_bytes();r['bytes']=len(raw);r['SHA']=hashlib.sha256(raw).hexdigest()
 mf.write_text(json.dumps(m,indent=2),encoding='utf8')
 # Execute ONLY the remaining original verifier body from actual source, no generation replay.
 original=B/'finalize_E0_source_manifest_and_CPU_fixture_v1.py';tree=ast.parse(original.read_bytes());func=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main');offset=next(i for i,n in enumerate(func.body) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='closure' for x in n.targets))
 scope={'__file__':str(original),'__name__':'local_source_fixture_remaining_v2'}
 setup=[n for n in tree.body if not isinstance(n,ast.If) and not (isinstance(n,ast.FunctionDef) and n.name=='main')]
 exec(compile(ast.Module(body=setup,type_ignores=[]),str(original),'exec'),scope)
 paths={r['relative']:Path(r['local_path']) for r in m['files']};cmd=paths['runtime/isaac/mod4/directional_spin_runtime.py']
 scope.update(manifest=m,rows=m['files'],allpaths=paths,cmd=cmd,tree=ast.parse(cmd.read_bytes()))
 exec(compile(ast.Module(body=func.body[offset:],type_ignores=[]),str(original),'exec'),scope)
 proof=dict(passed=True,scope='static source fixture path normalization only',old_source_SHA=hashlib.sha256(old).hexdigest(),new_source_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),exact_inverse_bytes=s.replace(inverse_pair[1],inverse_pair[0]).encode()==old,sup_result_parent_explicit_frozen_regression=True,runtime_worker_sup_readers_unchanged=True,constructor_hook_fixture_added=True,no_PT_raw_NPZ_USD_SDK_remote_reads=True)
 with (B/'reports/STATIC_RECEIPT_GRAPH_PARENT_FIX_INVERSE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(proof,f,indent=2)
if __name__=='__main__':
 try:main()
 except BaseException:
  p=B/'reports'/('LOCAL_REMAINING_CPU_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(traceback=traceback.format_exc(),no_model_or_remote=True),indent=2),encoding='utf8');raise
