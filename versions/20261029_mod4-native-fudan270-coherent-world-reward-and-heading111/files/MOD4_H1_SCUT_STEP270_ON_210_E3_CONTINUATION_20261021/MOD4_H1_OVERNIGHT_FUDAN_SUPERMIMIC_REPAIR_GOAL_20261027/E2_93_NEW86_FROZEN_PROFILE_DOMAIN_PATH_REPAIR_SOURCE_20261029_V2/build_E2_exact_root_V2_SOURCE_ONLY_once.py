"""NEW unused path-only binding repair, no binary/model/remote access."""
from pathlib import Path,PurePosixPath
import ast,hashlib,json
B=Path(__file__).resolve().parent;L=B.parent;OLD=L/'E2_93_NEW86_FROZEN_PROFILE_DOMAIN_SOURCE_PREPARATION_20261029_V1'
OLD_STAGE='/data/robemo/polar-rl-train/evaluation_runs/E2_ADAPTED93_PROFILE_DOMAIN_20261029v1/w35'
STAGE='/data/robemo/polar-rl-train/evaluation_runs/E2_ADAPTED93_PROFILE_DOMAIN_20261029v2/e2'
OLD_ENTRY='upload_admit_detach_NEW86_E2_final93_profiles_secure_stdin_UNUSED_once_v1.py'
ENTRY='upload_admit_detach_NEW86_E2_final93_profiles_secure_stdin_UNUSED_once_v2_exactE2root.py'
OLD_REMOTE='remote_E2_new86_profile_install_and_detach_v1.py'
REMOTE='remote_E2_new86_profile_install_and_detach_v2_exactE2root.py'
INDEX='FROZEN_E2_93_NEW86_PROFILE_DOMAIN_SOURCE_INDEX_V2.json'
def H(b):return hashlib.sha256(b).hexdigest()
def write(n,b):
 with (B/n).open('xb') as f:f.write(b)
def put(n,v):write(n,(json.dumps(v,indent=2)+'\n').encode())
def main():
 (B/'reports').mkdir(exist_ok=True);old=json.loads((OLD/'FROZEN_E2_93_NEW86_PROFILE_DOMAIN_SOURCE_INDEX_V1.json').read_bytes());m=json.loads((OLD/old['manifest_local_filename']).read_bytes());kept=[]
 for name,sha in old['executable_source_SHAs'].items():
  if name in (OLD_ENTRY,OLD_REMOTE):continue
  raw=(OLD/name).read_bytes();assert H(raw)==sha;write(name,raw);kept.append(name)
 raw=(OLD/'E2_93_QUALIFIED_FORMAL_CPU_WITNESS.json').read_bytes();write('E2_93_QUALIFIED_FORMAL_CPU_WITNESS.json',raw)
 original=(OLD/OLD_REMOTE).read_bytes();remote=original.decode();old_paths="J=Path(v['stage']);D=Path(v['copy']);";new_paths="J=Path(v['stage']);assert str(J)=="+repr(STAGE)+";D=Path(v['copy']);";assert remote.count(old_paths)==1;remote=remote.replace(old_paths,new_paths);assert remote.replace(new_paths,old_paths).encode()==original;write(REMOTE,remote.encode())
 original_entry=(OLD/OLD_ENTRY).read_bytes();entry=original_entry.decode();replacements=[(OLD_STAGE,STAGE),(OLD_REMOTE,REMOTE),('FROZEN_E2_93_NEW86_PROFILE_DOMAIN_SOURCE_INDEX_V1.json',INDEX)]
 for a,b in replacements:assert entry.count(a)>0;entry=entry.replace(a,b)
 inverse=entry
 for a,b in reversed(replacements):inverse=inverse.replace(b,a)
 assert inverse.encode()==original_entry;write(ENTRY,entry.encode())
 rows=[]
 for row in m['files']:
  name=row['relative'];r=dict(row)
  if name==OLD_ENTRY:name=ENTRY
  if name==OLD_REMOTE:name=REMOTE
  if name in kept+[ENTRY,REMOTE,'E2_93_QUALIFIED_FORMAL_CPU_WITNESS.json']:
   raw=(B/name).read_bytes();r.update(relative=name,local_path=str(B/name),bytes=len(raw),SHA=H(raw))
  rows.append(r)
 m.update(files=rows,source_version='V2_exact_E2_root_metadata_only',target_stage=STAGE,old_V1_preserved_unused_not_selected=True,path_fix_only_no_model_CPU_reload=True)
 write('E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json',(json.dumps(m,indent=2)+'\n').encode())
 # Execute ONLY actual paths() source on a filesystem-free PurePosixPath fixture.
 tree=ast.parse(remote);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='paths')
 class FakePath(PurePosixPath):
  def resolve(self):return self
 scope=dict(Path=FakePath,ROOT=FakePath('/data/robemo/polar-rl-train'));exec(compile(ast.Module(body=[fn],type_ignores=[]),'<NEW remote actual paths() metadata CPU fixture>','exec'),scope)
 copy='/data/robemo/polar-rl-train/runtime_migrations/proven72_20261028_v1/runtime_copy_v1';J,D=scope['paths'](dict(stage=STAGE,copy=copy));assert str(J)==STAGE and str(D)==copy
 rejected=[]
 for label,v in [('V1 old w35 suffix',dict(stage=OLD_STAGE,copy=copy)),('wrong namespace',dict(stage=STAGE.replace('v2','v1'),copy=copy)),('outside project',dict(stage='/tmp/e2',copy=copy)),('outside clone root',dict(stage=STAGE,copy='/opt/other'))]:
  try:scope['paths'](v)
  except AssertionError:rejected.append(label)
  else:raise AssertionError(label)
 for name in kept+[ENTRY,REMOTE]:ast.parse((B/name).read_bytes())
 put('V1_REFUSED_UNUSED_PATH_LABEL_MISMATCH_AND_V2_EXACT_INVERSE_ACTUAL.json',dict(passed=True,old_entry=str(OLD/OLD_ENTRY),old_entry_SHA=H(original_entry),old_actual_stage_literal=OLD_STAGE,old_HANDOFF_e2_suffix_mismatched=True,old_remote_used_dynamic_stage_consistently=True,old_source_status='PREPARED_UNUSED_NOT_SELECTED_NO_REMOTE_BINDING',new_stage=STAGE,entry_inverse_exact=True,remote_only_added_exact_stage_assert_inverse_exact=True,unchanged_worker_CPU_supervisor_telemetry_sources=kept,actual_remote_paths_function_synthetic_positive=True,negative_paths_rejected=rejected,no_binary_PT_USD_NPZ_raw_stat_or_content_read=True,no_model_CPU_reload_or_SDK_or_remote=True))
 prior=(OLD/'reports/E2_FRESH_SYNTHETIC_CPU_AND_SOURCE_AST_ACTUAL_V1.json').read_bytes();write('PRIOR32_FRESH_CPU_SOURCE_WITNESS_UNCHANGED.json',prior)
 selection=dict(status='SOURCE_ONLY_UNUSED_PENDING_REVIEW',entry=ENTRY,remote=REMOTE,index=INDEX,manifest_local_filename='E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json',manifest_SHA=H((B/'E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json').read_bytes()),executable_source_SHAs={n:H((B/n).read_bytes()) for n in kept+[ENTRY,REMOTE]},clone_receipt_SHA=old['clone_receipt_SHA'],actual_clone_CUDA_SDK_receipt_SHA=old['actual_clone_CUDA_SDK_receipt_SHA'],target_stage=STAGE,source_model_SHA=old['source_model_SHA'],prior_frozen_index=str(OLD/'FROZEN_E2_93_NEW86_PROFILE_DOMAIN_SOURCE_INDEX_V1.json'),prior_frozen_index_SHA=H((OLD/'FROZEN_E2_93_NEW86_PROFILE_DOMAIN_SOURCE_INDEX_V1.json').read_bytes()))
 put('E2_V2_SELECTION_PENDING_FINAL_FREEZE.json',selection);print(json.dumps(dict(passed=True,stage=STAGE,input_rows=len(rows),metadata_negative_cases=len(rejected),no_execution=True)))
if __name__=='__main__':main()
