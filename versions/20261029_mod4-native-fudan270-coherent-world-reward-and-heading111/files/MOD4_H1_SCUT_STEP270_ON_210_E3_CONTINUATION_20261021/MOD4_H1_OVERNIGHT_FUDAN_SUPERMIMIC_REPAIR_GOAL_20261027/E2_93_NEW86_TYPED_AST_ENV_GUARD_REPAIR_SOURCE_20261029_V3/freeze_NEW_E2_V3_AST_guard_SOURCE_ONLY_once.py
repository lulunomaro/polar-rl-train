from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent
def H(b):return hashlib.sha256(b).hexdigest()
def main():
 selection=json.loads((B/'V3_SELECTION_PENDING_FINAL_FREEZE.json').read_bytes());proof=json.loads((B/'reports/V3_ACTUAL_TARGET_CPU_GUARD_SELECTED_SOURCE_POSITIVE_NEGATIVE_ACTUAL.json').read_bytes());assert proof['passed'] and len(proof['negative_cases_rejected'])==15
 manifest=B/selection['manifest_local_filename'];assert H(manifest.read_bytes())==selection['manifest_SHA'];m=json.loads(manifest.read_bytes());assert len(m['files'])==433
 for r in m['files']:
  if Path(r['local_path']).parent==B:raw=(B/r['relative']).read_bytes();assert H(raw)==r['SHA'] and len(raw)==r['bytes']
 for k in ('executable_source_SHAs','readonly_source_SHAs'):
  for n,sha in selection[k].items():assert H((B/n).read_bytes())==sha
 for p in B.glob('*.py'):ast.parse(p.read_bytes())
 e3=B.parent/'E3_97_NEW86_FROZEN_RECIPE_DOMAIN_SOURCE_PREPARATION_20261029_V1';rows=[dict(path=str(p),bytes=len(p.read_bytes()),SHA=H(p.read_bytes())) for p in e3.glob('*.py')]
 with (e3/'ACTIVE_SOURCE_SAVEPOINT_PAUSED_FOR_E2_V3_AST_REPAIR.json').open('x') as f:json.dump(dict(status='EXPLICIT_PENDING_SOURCE_ONLY_INCOMPLETE_NOT_EXECUTABLE',reason='Prioritize observed E2 metadata AST guard failure repair',saved_text_sources=rows,no_PT_raw_SDK_GPU_remote_call=True),f,indent=2)
 files=[]
 for p in sorted(B.rglob('*')):
  if p.is_file():
   assert p.suffix in ('.py','.json','.md');raw=p.read_bytes();files.append(dict(relative=p.relative_to(B).as_posix(),bytes=len(raw),SHA=H(raw)))
 selection.update(status='FROZEN_V3_SOURCE_ONLY_PREPARED_UNUSED_NOT_TARGET_ADMITTED',files=files,entry_SHA=selection['executable_source_SHAs'][selection['entry']],actual_target_CPU_AST_guard_section_on_exact_worker_passed=True,negative_cases=15,worker_model_metrics_physics_queue_exact_unchanged=True,originalV2_actual_false_preserved=True,metadata_CPU_PT_decode0=True,actual_App_GPU_fullrestore_native24_900coverage_pending=True,supervisor1800_worker1680_remaining900_normalwait850=True,Git_status='EXPLICIT_PENDING ordinary root supplement; no trial/tag',skill_graduation=False,complete_WM_dataset=False)
 with (B/selection['index']).open('x') as f:json.dump(selection,f,indent=2)
 print(json.dumps(dict(passed=True,index=selection['index'],index_SHA=H((B/selection['index']).read_bytes()),entry=selection['entry'],entry_SHA=selection['entry_SHA'],manifest_SHA=selection['manifest_SHA'],files=len(files),source_only=True)))
if __name__=='__main__':main()
