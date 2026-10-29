"""Fix source-only internal module references; preserve first two fixture errors."""
from pathlib import Path
import ast,hashlib,json,time,traceback
B=Path(__file__).resolve().parent
def main():
 names={'e0_profile_domain_telemetry_v1':'e0_long_command_domain_telemetry_v1','e0_original_profile_catalog_candidate_v1':'e0_original_profile_catalog_v1','e0_frozen_worker_call_guard_v3':'e0_frozen_worker_call_guard_v1','run_E0_new86_readonly_secure_stdin_v4':'run_E0_new86_readonly_secure_stdin_v1'}
 changed=[]
 for name in ('evaluate_E0_adapted82_new86_frozen1000_once_v1.py','e0_long_command_domain_telemetry_v1.py','E0_new86_target_source_SDK_metadata_admission_v1.py','read_E0_new86_FIRST_native24_queue_secure_stdin_UNUSED_once_v1.py','collect_E0_new86_TERMINAL_fulltext_secure_stdin_UNUSED_once_v1.py'):
  p=B/name;raw=p.read_bytes();s=raw.decode('utf8')
  for a,b in names.items():s=s.replace(a,b)
  if s.encode()!=raw:
   p.write_text(s,encoding='utf8',newline='\n');changed.append(dict(name=name,before_SHA=hashlib.sha256(raw).hexdigest(),after_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),exact_inverse_bytes=all(a not in s for a in names)))
 p=B/'e0_declared_entry_receipt_cli_contract_v1.py';s=p.read_text(encoding='utf8');a="elif name not in stdlib:external.add(name)";b="elif name not in stdlib:\n     assert not name.startswith(('e0_','E0_')),'Missing declared internal E0 module: '+name\n     external.add(name)";assert a in s;s=s.replace(a,b);p.write_text(s,encoding='utf8',newline='\n')
 mf=B/'E0_NEW86_COMPLETE_INPUT_MANIFEST_V1.json';m=json.loads(mf.read_bytes())
 for r in m['files']:
  p=B/r['relative']
  if p.parent==B and p.is_file() and p.suffix=='.py':raw=p.read_bytes();r['bytes']=len(raw);r['SHA']=hashlib.sha256(raw).hexdigest()
 mf.write_text(json.dumps(m,indent=2),encoding='utf8')
 original=B/'finalize_E0_source_manifest_and_CPU_fixture_v1.py';tree=ast.parse(original.read_bytes());func=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main');offset=next(i for i,n in enumerate(func.body) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='closure' for x in n.targets))
 scope={'__file__':str(original),'__name__':'local_source_fixture_remaining_v3'};setup=[n for n in tree.body if not isinstance(n,ast.If) and not (isinstance(n,ast.FunctionDef) and n.name=='main')];exec(compile(ast.Module(body=setup,type_ignores=[]),str(original),'exec'),scope)
 paths={r['relative']:Path(r['local_path']) for r in m['files']};cmd=paths['runtime/isaac/mod4/directional_spin_runtime.py'];scope.update(manifest=m,rows=m['files'],allpaths=paths,cmd=cmd,tree=ast.parse(cmd.read_bytes()))
 class Output(ast.NodeTransformer):
  def visit_Constant(self,n):
   if n.value=='reports/FRESH_CPU_SELECTED_CONSTRUCTOR_OUTPUT':return ast.copy_location(ast.Constant(value='reports/FRESH_CPU_SELECTED_CONSTRUCTOR_OUTPUT_V3'),n)
   return n
 body=Output().visit(ast.Module(body=func.body[offset:],type_ignores=[]));exec(compile(ast.fix_missing_locations(body),str(original),'exec'),scope)
 with (B/'reports/SELECTED_INTERNAL_MODULE_REFERENCE_SOURCE_CORRECTION_V3.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,changes=changed,missing_local_E0_modules_rejected=True,source_only_no_models=True),f,indent=2)
if __name__=='__main__':
 try:main()
 except BaseException:
  p=B/'reports'/('LOCAL_REMAINING_CPU_V3_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(traceback=traceback.format_exc(),no_model_or_remote=True),indent=2),encoding='utf8');raise
