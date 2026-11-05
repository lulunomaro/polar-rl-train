"""New-purpose source-dependency repair only after actual pre-import zero-GO failure."""
from pathlib import Path
import json,ast
D=Path(__file__).resolve().parent;old=json.loads((D/'NINE_CLOSED_RESULT_PATH.json').read_bytes());closed=json.loads(Path(old['path']).read_bytes());m=closed['metadata'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];tail=closed['own_owner_log_tail_once']
assert closed['closed']is True and outer['original_owner_reaped']is True and outer['actual_wait_returncode']==1 and outer['original_owner_pid']==1672466 and outer['controller_pid']==1672459 and m['OWNER_STARTED.json']is None and m['OWNER_EXIT_ACTUAL.json']is None and m['COHORT_FINAL.json']is None
assert all(v['GO_PRODUCTION.json']is None and v['V2_NATIVE_INITIALIZED.json']is None and v['V2_LEARNER_LOADED.json']is None and v['V2_MIGRATION_FINAL.json']is None for v in closed['cases'].values())and 'FileNotFoundError'in tail and 'SCHEDULE_PUBLIC.json'in tail
(D/'ADMISSION1_PREIMPORT_FAILURE_TRUTH.json').write_text(json.dumps(dict(first_root=closed['root'],first_closed=old['path'],actual_owner_wait=outer,original_error=tail,all9_GO_SDK_source_input_or_PPO=0,failed_before_original_main_or_locks=True,no_canonical_change_or_refund=True,new_purpose_repairs_source_dependency_only=True),indent=2),encoding='utf8')
outputs={}
for src,dst in(('stage_nine_migration_once.py','stage_nine_migration_admission2_once.py'),('dispatch_nine_migration_once.py','dispatch_nine_migration_admission2_once.py'),('collect_nine_migration_once.py','collect_nine_migration_admission2_once.py')):
 target=D/dst;assert not target.exists();s=(D/src).read_text(encoding='utf8');s=s.replace('STAGE_NINE_','STAGE_NINE_ADMISSION2_').replace('DISPATCH_NINE_','DISPATCH_NINE_ADMISSION2_').replace('COLLECT_NINE_','COLLECT_NINE_ADMISSION2_').replace('SOURCE_PLAN_ACTUAL_V1.json','SOURCE_PLAN_ADMISSION2_ACTUAL_V1.json').replace('NINE_CLOSED_RESULT_PATH.json','NINE_ADMISSION2_CLOSED_RESULT_PATH.json').replace('MOD4V2_NINE_FULL_LEARNER_MIGRATION_','MOD4V2_NINE_FULL_LEARNER_MIGRATION_ADMISSION2_')
 if src.startswith('stage_'):
  a="payload['SOURCE_PLAN.json']=json.dumps(plan,indent=2).encode();";assert s.count(a)==1;s=s.replace(a,a+"payload['SCHEDULE_PUBLIC.json']=json.dumps(dict(kind='ORIGINAL_SOURCE_WORK_SCHEDULE_NOT_LEDGER_OR_NEW_BUDGET',experts={e['role_key']:dict(max_parent_seconds=3900,GPU_UUID=('GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d')[i%2])for i,e in enumerate(entries)}),indent=2).encode();")
  # Preserve original failed-owner source, not an invented reconstruction.
  a='mkdirs(remote)\n for rel,raw in payload.items():';assert s.count(a)==1
  s=s.replace(a,"archive=D/'attempts/admission1_executed_owner.py';assert not archive.exists();archive.parent.mkdir(parents=True,exist_ok=True)\n with sftp.open("+repr(closed['root']+'/migration_nine_original_owner_v1.py')+",'r')as f:archive.write_bytes(f.read())\n mkdirs(remote)\n for rel,raw in payload.items():")
  a="D=Path(__file__).resolve().parent;";assert s.count(a)==1;s=s.replace(a,a+"z=json.loads((D/'ADMISSION1_PREIMPORT_FAILURE_TRUTH.json').read_bytes());assert z['all9_GO_SDK_source_input_or_PPO']==0 and z['failed_before_original_main_or_locks']is True;")
 ast.parse(s);compile(s,str(target),'exec');outputs[target]=s
for p,s in outputs.items():p.write_text(s,encoding='utf8',newline='\n')
print('Admission2 new source entries compiled; first actual0GO error preserved; source schedule dependency added, original budget accounting unchanged')
