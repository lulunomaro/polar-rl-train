from pathlib import Path
import ast,hashlib,json
C=Path(__file__).resolve().parent;L=C.parent
SPECS=[('E2','E2_93_NEW86_ORIGINAL_FLAT_HEIGHT_PROVIDER_REPAIR_SOURCE_20261029_V4','e2_profile_domain_telemetry_v1.py'),('E3','E3_97_SOURCE210_ORIGINAL_FLAT_HEIGHT_PROVIDER_REPAIR_SOURCE_20261029_V3','e3_recipe_domain_telemetry_v1.py')]
def H(b):return hashlib.sha256(b).hexdigest()
def put(D,n,x):
 with (D/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2)
def index_files(D):
 rows=[];local={}
 for p in sorted(D.rglob('*')):
  if not p.is_file():continue
  raw=p.read_bytes();row=dict(relative=p.relative_to(D).as_posix(),bytes=len(raw),SHA=H(raw))
  if p.suffix=='.gz':row['fresh_CPU_synthetic_fixture_output_metadata_only']=True
  else:assert p.suffix in ('.py','.json','.md','.txt')
  rows.append(row)
  if p.parent==D and p.suffix=='.py':ast.parse(raw);local[p.name]=H(raw)
 return rows,local
def main():
 both=json.loads((C/'reports/BOTH_SELECTED_CONSTRUCTORS_SOURCE_CPU_ACTUAL.json').read_bytes());assert both['passed']
 for role,name,component in SPECS:
  D=L/name;s=json.loads((D/'GROUND_REPAIR_SELECTION_PENDING_FINAL_FREEZE.json').read_bytes());proof=json.loads((D/'reports/SELECTED_CONSTRUCTOR_GROUND_AND_CLOCK_SOURCE_CPU_ACTUAL.json').read_bytes());assert proof['passed'] and proof['role']==role and proof['selected_component_SHA']==H((D/component).read_bytes()) and proof['no_ground_attribute_injected']
  normalizations=[]
  for p in D.glob('*.py'):
   raw=p.read_bytes();text=raw.decode();new=text.replace('E2_V3_','E2_V4_') if role=='E2' else text.replace('E3_V2_','E3_V3_')
   if new!=text:
    with (D/(p.name+'.preseal_namespace_label_reference.txt')).open('xb') as f:f.write(raw)
    p.write_bytes(new.encode());normalizations.append(dict(source=p.name,old_SHA=H(raw),selected_SHA=H(new.encode()),only_public_case_label_rebased=True))
  mf=D/s['manifest_filename'];oldraw=mf.read_bytes();m=json.loads(oldraw);changes=[]
  for r in m['files']:
   if Path(r['local_path']).parent!=D:continue
   p=Path(r['local_path']);raw=p.read_bytes();before=dict(r)
   if '/' not in r['relative']:r['relative']=p.name
   r.update(bytes=len(raw),SHA=H(raw))
   if r!=before:changes.append(dict(old=before,new=r))
  if changes:
   with (D/'PRESEAL_INPUT_MANIFEST_NAMESPACE_REFERENCE.json').open('xb') as f:f.write(oldraw)
   mf.write_text(json.dumps(m,indent=2)+'\n',encoding='utf8')
  s['manifest_SHA']=H(mf.read_bytes());put(D,'PRESEAL_NAMESPACE_METADATA_BINDING_RECONCILIATION_ACTUAL.json',dict(passed=True,public_label_changes=normalizations,manifest_selected_basename_rows=changes,worker_model_physics_unchanged=True,no_remote_or_model=True))
  text=f'''{role} original-flat-height repair FROZEN/UNUSED. Selected entry `{s['entry']}`, target `{s['target_root']}`. See `{s['index']}` for exact source/manifest/reader pins. Root review + fresh exact LOCAL CIM + global serial lease precedes execution. Preserve old cases, failures/partial/once; do not rearm them.

Root cause: original mod4_task.root_height_above_ground uses getattr(_mod4_ground_z, torch.zeros(...)); an uncreated cache is legal in flat E2/E3. New provider calls that exact original cached root-height getter, guarded by source SHA30ce41126a1a9b78a1c2b446281b28f4555c28052bfaa7c0e9a76079cf561fc5 and TERRAIN flat. It never injects _mod4_ground_z or calls ground_height/raycast/native query/RNG. Trace ground is root_z minus original relative height, and metric height uses the original getter directly. All selected telemetry ground references were audited; no direct W35 cache requirement remains. Original runtime/task/reward/physics/model/normalizer/optimizer/queue bytes are unmodified; only observer/helper/metadata and new namespace are changed.

The actual selected telemetry constructor and physical/begin/requested/original queue8pergroup/terminal/after methods executed in fresh CPU API fixtures WITHOUT any ground cache. No cache was created and global RNG was unchanged. Nonflat/wrong-source contract negatives rejected. E2 retained its existing saved successful fixture proof; E3 new fixture passed. Local wrapper glob ambiguity and attempted x-mode overwrite errors are preserved with appended correction. This is not real env/SDK/GPU qualification. The target metadata CPU now also executes this same actual selected constructor API fixture using fresh CPU values and installed target TensorDict before App, so its actual package API compatibility must pass before detach.

Original model/STD/17Adam/LR/D1-D7/source/witness/noPPO/noC/fullfinite/resource/privateEX/owned-cache guards remain. E2 keeps final93 Adam859300/LR.00022500000000000002/900controls100warm800steady; E3 keeps final97 Adam866060/LR.0002562890625000001/original13recipes3srequestpoint5srecovery/600controls100warm500steady. Neither is H1 learning or inherited skill graduation/complete WM data.

NEW FIRST reader `{s['first_reader']}` accepts `--actual-startup-json <NEW actual report> --actual-startup-SHA <actual full SHA>`. It waits ONCE360s for actual CUDA fullrestore/native24/192physics/48feedback/bothgroups192/trace1..24 or original error/terminal. Task/CPU/source/index explicitly record360; no repeated watcher. NEW normal `{s['terminal_reader']}` retains local+remote supervisor+1800 remaining<=900, one850 wait. Worker1680/supervisor1800/normal850/900 and all training/physical protocols are unchanged; no old first repeat.

{'E2 secure entry keeps source72 readonly close before86, exact project-only clone HOME/XDG/TMP and strictpin/one noecho stdin JSON. Use fresh known72-binding if active.' if role=='E2' else 'E3 entry keeps original route.PY control alias and canonical python3.12 worker payload, strict remote guard, NTFS EF31/rw, ownKit cache and exact known72 binding. No86secret needed.'} Actual target metadata/constructor/API/fullrestore/native24/fullprofile coverage remains pending. Ordinary root Git supplement pending, no trial/tag. Current source task completes idle.
'''
  with (D/'HANDOFF_FROZEN_ORIGINAL_HEIGHT_PROVIDER_FIRST360.md').open('x',encoding='utf8') as f:f.write(text)
  rows,local=index_files(D);s.update(status='FROZEN_SOURCE_ONLY_UNUSED_NEW_ACTUAL_TARGET_ADMISSION_PENDING',files=rows,local_source_SHAs=local,executable_source_SHAs=local,readonly_source_SHAs=local,entry_SHA=local[s['entry']],source_model_SHA=s['model_SHA'],first_native24_read_wait_maximum_seconds=360,worker1680_supervisor1800_normalremaining900_wait850_preserved=True,selected_constructor_and_all_ground_methods_CPU_fixture_passed=True,actual_target_metadata_CPU_will_execute_same_fixture=True,no_ground_attribute_injection_or_extra_SDK_raycast_RNG=True,metadata_CPU_PT_decode0=True,no_remote_model_GPU_or_ledger_write=True,Git_status='EXPLICIT_PENDING root ordinary supplement; no trial/tag',skill_graduation=False,complete_WM_dataset=False)
  put(D,s['index'],s);print(json.dumps(dict(role=role,index=str(D/s['index']),index_SHA=H((D/s['index']).read_bytes()),entry=s['entry'],entry_SHA=s['entry_SHA'],manifest_SHA=s['manifest_SHA'],source_only=True)))
 rows,local=index_files(C);put(C,'FROZEN_SHARED_ORIGINAL_FLAT_HEIGHT_SOURCE_AND_ALL_LOCAL_FIXTURE_ERRORS_INDEX.json',dict(status='FROZEN_SOURCE_CPU_ONLY',files=rows,local_sources=local,both_selected_constructors_passed=True,all_original_local_errors_and_corrections_preserved=True,no_old_PT_raw_SDK_GPU_remote=True,ordinary_Git_pending=True))
if __name__=='__main__':main()
