"""Fix an actual pre-main NameError only in a new E0 purpose; preserve first source/error/root."""
from pathlib import Path
import json,ast
D=Path(__file__).resolve().parent;v=json.loads(Path(json.loads((D/'E0_SINGLE_CLOSED_RESULT_PATH.json').read_bytes())['path']).read_bytes());m=v['metadata'];o=m['OUTER_OWNER_WAIT_ACTUAL.json'];assert v['closed']is True and o['original_owner_reaped']is True and o['actual_wait_returncode']==1 and o['original_owner_pid']==1679732 and o['controller_pid']==1679725 and m['OWNER_STARTED.json']is m['OWNER_EXIT_ACTUAL.json']is None and all(c['GO_PRODUCTION.json']is c['V2_NATIVE_INITIALIZED.json']is c['V2_LEARNER_LOADED.json']is None for c in v['cases'].values())and "name 'es' is not defined"in v['own_owner_log_tail_once']
outputs={};owner=(D/'source_owner_e0_single/migration_nine_original_owner_v1.py').read_text(encoding='utf8');a="require(len(es)==1 and es[0]['role']=='E0'";assert owner.count(a)==1;owner=owner.replace(a,"require(len(entries)==1 and entries[0]['role']=='E0'");outputs[D/'source_owner_e0_single_v2/migration_nine_original_owner_v1.py']=owner
for a,b in [('stage_e0_single_migration_once.py','stage_e0_single_admission2_migration_once.py'),('dispatch_e0_single_migration_once.py','dispatch_e0_single_admission2_migration_once.py'),('collect_e0_single_migration_once.py','collect_e0_single_admission2_migration_once.py')]:
 s=(D/a).read_text(encoding='utf8')
 for x,y in [('STAGE_E0_SINGLE_','STAGE_E0_SINGLE_ADMISSION2_'),('DISPATCH_E0_SINGLE_','DISPATCH_E0_SINGLE_ADMISSION2_'),('COLLECT_E0_SINGLE_','COLLECT_E0_SINGLE_ADMISSION2_'),('SOURCE_PLAN_E0_SINGLE_ACTUAL_V1.json','SOURCE_PLAN_E0_SINGLE_ADMISSION2_ACTUAL_V1.json'),('E0_SINGLE_CLOSED_RESULT_PATH.json','E0_SINGLE_ADMISSION2_CLOSED_RESULT_PATH.json'),('MOD4V2_E0_SINGLE_FULL_LEARNER_MIGRATION_','MOD4V2_E0_SINGLE_ADMISSION2_FULL_LEARNER_MIGRATION_')]:s=s.replace(x,y)
 if a.startswith('stage_'):
  s=s.replace('source_owner_e0_single/migration_nine_original_owner_v1.py','source_owner_e0_single_v2/migration_nine_original_owner_v1.py')
  # Add the actual zero-start proof before any new marker/connection.
  needle='D=Path(__file__).resolve().parent;';assert s.count(needle)==1;s=s.replace(needle,needle+"first=json.loads((D/'E0_SINGLE_PREMAIN_FAILURE_TRUTH.json').read_bytes());assert first['all_GO_SDK_PT_PPO']==0 and first['actual_outer_wait']['original_owner_reaped']is True;")
  s=s.replace("');runpy.run_path('","');ns=runpy.run_path('")
  a2="source_dependency_preflight_not_main');print('owner_import_only_passed_no_GO_SDK_models_or_locks')";b2="source_dependency_preflight_not_main');import json;ns['verify_sources'](json.loads((ns['B']/'OWNER_PLAN.json').read_bytes()));print('owner_manifest_and_source_validation_passed_no_GO_SDK_models_locks_or_C_access')";assert s.count(a2)==1;s=s.replace(a2,b2)
 outputs[D/b]=s
for p,s in outputs.items():assert not p.exists();ast.parse(s);compile(s,str(p),'exec')
for p,s in outputs.items():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8',newline='\n')
(D/'E0_SINGLE_PREMAIN_FAILURE_TRUTH.json').write_text(json.dumps(dict(root=v['root'],actual_outer_wait=o,error=v['own_owner_log_tail_once'],all_GO_SDK_PT_PPO=0,before_main_marker_or_lock=True,old_source_preserved=True,new_source_variable_correction_only=True),indent=2),encoding='utf8');print('E0 new purpose fixes only undefined guard name; verify_sources source/manifest preflight now called before dispatch; no model/SDK/remote execution')
