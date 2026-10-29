from pathlib import Path,PurePosixPath
import ast,hashlib,importlib.util,json,sys
B=Path(__file__).resolve().parent;L=B.parent
def main():
 p=B/'e3_declared_entry_receipt_cli_contract_v1.py';s=importlib.util.spec_from_file_location('e3_declared_entry_receipt_cli_contract_v1',p);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);manifest=json.loads((B/'E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json').read_bytes());rows={r['relative']:r for r in manifest['files']}
 cache={}
 def read(relative):
  if relative not in cache:cache[relative]=Path(rows[relative]['local_path']).read_bytes()
  return cache[relative]
 entry=read(m.ENTRY);worker=read(m.WORKER);sup=read(m.SUP);code=read(m.CODE);positive=m.validate_entry_cli_learn_hook(entry,worker);graph=m.selected_receipt_graph(worker,sup,code);closure=m.declared_import_closure(manifest,read);assert positive['passed'] and graph['passed'] and closure['passed']
 rejected=[]
 def reject(n,f):
  try:f()
  except (AssertionError,StopIteration):rejected.append(n);return
  raise AssertionError('Negative accepted: '+n)
 reject('old E2-derived full_resume filename',lambda:m.validate_entry_cli_learn_hook(entry,worker.replace(b'train_E3_fullstate_v1.py',b'train_E3_full_resume_v1.py')))
 reject('writer-only native34 file mismatch',lambda:m.selected_receipt_graph(worker.replace(b'ACTUAL_NATIVE24_E3_40050_CLOCK_QUEUE.json',b'ACTUAL_NATIVE34_E3_40050_CLOCK_QUEUE.json'),sup,code))
 reject('reader-only restore93 mismatch',lambda:m.selected_receipt_graph(worker,sup,code.replace(b'ACTUAL_E3_97_CUDA_FULLRESTORE_BEFORE_MEAN_ACTION.json',b'ACTUAL_E3_93_CUDA_FULLRESTORE_BEFORE_MEAN_ACTION.json')))
 reject('production learner hook not replaced',lambda:m.validate_entry_cli_learn_hook(entry,worker.replace(b'rescue_training.learn=work',b'rescue_training.learn=production_learn')))
 reject('entry main runs before patch via __main__',lambda:m.validate_entry_cli_learn_hook(entry,worker.replace(b"run_name='frozen_E3_original97_restore_config'",b"run_name='__main__'")))
 reject('incorrect final LR CLI',lambda:m.validate_entry_cli_learn_hook(entry,worker.replace(b"'--learning_rate','.0002562890625000001'",b"'--learning_rate','.0001'")))
 old=L/'E3_97_SOURCE210_ORIGINAL_FLAT_HEIGHT_PROVIDER_REPAIR_SOURCE_20261029_V3';reject('authentic V3 worker entry rejected',lambda:m.validate_entry_cli_learn_hook(entry,(old/m.WORKER).read_bytes()));reject('authentic V3 receipt graph rejected',lambda:m.selected_receipt_graph((old/m.WORKER).read_bytes(),(old/m.SUP).read_bytes(),(old/'E3_source210_actual_receipts_readonly_CODE_v3.py').read_bytes()))
 # PurePOSIX comparison evaluates the exact local selected actual-startup guard.
 runner=B/'run_E3_source210_readonly_v4.py';tree=ast.parse(runner.read_bytes());job=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='JOB' for t in n.targets));expr=next(n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='str' and n.args and isinstance(n.args[0],ast.BinOp) and isinstance(n.args[0].left,ast.Call) and isinstance(n.args[0].left.func,ast.Name) and n.args[0].left.func.id=='PurePosixPath');actual=eval(compile(ast.Expression(body=expr),'<selected true POSIX argv expression>','eval'),dict(JOB=job,PurePosixPath=PurePosixPath));assert actual==job+'/'+m.SUP and '\\' not in actual
 for p in B.glob('*.py'):ast.parse(p.read_bytes())
 assert 'torch.load(' not in (B/'E3_source210_target_source_SDK_metadata_admission_v1.py').read_text()
 with (B/'reports/REAL_SELECTED_ENTRY_RECEIPT_CLI_HOOK_DEPENDENCY_SOURCE_CPU_ACTUAL.json').open('x') as f:json.dump(dict(passed=True,actual_production_entry_CLI_hook=positive,actual_worker_sup_first_normal_receipt_graph=graph,complete_declared_internal_source_import_closure=closure,source_PY_files_read_only=len(cache),negative_cases_rejected=rejected,selected_startup_guard_PurePosix_actual_expression=actual,target_actual_SDK_parser_static_flag_check_pending=True,no_PT_raw_NPZ_USD_actor_SDK_GPU_remote=True),f,indent=2)
 print(json.dumps(dict(passed=True,negative_cases=len(rejected),source_closure_files=len(closure['entry_and_internal_import_source_SHA_closure']),external_roots=closure['external_SDK_or_package_roots_explicit'],source_only=True)))
if __name__=='__main__':main()
