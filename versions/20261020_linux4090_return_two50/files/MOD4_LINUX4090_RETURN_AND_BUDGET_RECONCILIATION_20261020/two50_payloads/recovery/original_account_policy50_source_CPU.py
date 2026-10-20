"""Source admission after actual closed cost reconciliation, with explicit clock migration."""
from pathlib import Path
import hashlib,json,os,psutil
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(spec,B):
 read=lambda p:json.loads(Path(p).read_bytes());m=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');prov=read(B/'TWO50_SOURCE_PROVENANCE.json');old=Path(spec['previous_runtime_root']);ne=read(old/'NODE_EXIT_ACTUAL.json');row=read(old/'NODE_TERMINAL_ACTUAL.json')['row'];receipt=read(B/'ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json');cpu=read(B/'TARGET_TWO50_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json');key=spec['key'];counts={'e2':[175,98],'recovery':[173,96]}[key]
 assert spec['policy_hz']==50 and key in ('e2','recovery') and spec['source_policy_hz']==(100 if key=='e2' else 50)
 assert spec['source_SHA']==m['source_SHA']==prov['source_SHA'] and spec['source_Adamstep']==m['source_Adamstep']==prov['source_Adamstep']
 assert ne['actual_all_own_children_waited'] and ne['validation_fcntl_released_if_acquired'] and row['terminal_all_own_children_waited'] and row['returncode']==0 and not row['errors'] and row['final']['passed'] and row['final']['final']['SHA']==spec['source_SHA']
 assert not any(p.pid!=os.getpid() and any(a.startswith(str(old)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
 assert receipt['passed'] and receipt['original_canonical_active_None_after'] and receipt['original_authorized_seconds']==1188000 and receipt['original_extension_count']==7
 assert cpu['passed_CPU_only'] and cpu['source_SHA']==spec['source_SHA'] and cpu['source_schema_counts']==counts and cpu['all17Adam']==spec['source_Adamstep'] and cpu['manifest_SHA']==H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
 original=read(B/'QUALIFIED_RUNTIME_BASE_MANIFEST.json');before={r['relative']:r for r in original['files']}
 for r in m['files']:
  if r['relative'].startswith(('job0/runtime/','job0/assets/','lib/')):assert r['SHA']==before[r['relative']]['SHA'] and r['bytes']==before[r['relative']]['bytes']
 native=None
 if key=='e2':
  native=read(B/'POLICY50_CLOCK_NATIVE24_ALL_STATE_CPU_ADMITTED_ACTUAL.json');assert native['passed'] and native['source_SHA']==spec['source_SHA'] and native['all_core_actor9_critic8_STD17Adam_literal_exact'] and native['whole_tensor_counts']==counts and native['actual_worker_waited_EXIT0'];co=read(old.parent/'owner/COHORT_FINAL.json');assert co['original_cost_settled'] and co['rows']['e2']['final']['final']['SHA']==spec['source_SHA']
 else:
  co=read(old.parent/'owner/COHORT_FINAL.json');assert co['pending_cost_record_complete'] and co['pending_cost']['run_id'] in receipt['distinct_run_ids_charged_once'];proof=read(old.parent/'CLOSED_FINAL_WHOLE_MODEL_CPU_ACTUAL.json');assert proof['passed'] and proof['final']['SHA']==spec['source_SHA'] and proof['all17Adam_after']==spec['source_Adamstep'];assert read(old/'job0/production/POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json')['policy_hz']==50
 value=dict(kind='policy_clock_100_to_50_migration' if key=='e2' else 'closed_same_backend_policy50_production',key=key,passed=True,source_SHA=spec['source_SHA'],GPU_UUID=spec['GPU_UUID'],execution_backend=spec['execution_backend'],all_source_model_runtime_finite_CPU=True,old_complete_production_checkpoint_actual_EXIT0=True,explicit_policy_clock_50Hz_admitted=True,policy_clock_native_CPU_SHA=H(B/'POLICY50_CLOCK_NATIVE24_ALL_STATE_CPU_ADMITTED_ACTUAL.json') if native else None,same_clock_closed_production=key=='recovery',source_cost_original_account_ready=True,source_account_reconciliation_receipt_SHA=H(B/'ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json'),original_clip6_query_COM_closure_mimic_hardware_savedstop_guards_retained=True,not_another_skill_pass=True)
 return dict(value=value,SHA=hashlib.sha256(json.dumps(value,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True)
