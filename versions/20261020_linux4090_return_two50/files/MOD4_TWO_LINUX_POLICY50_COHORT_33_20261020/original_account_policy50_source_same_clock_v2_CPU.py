"""Future source admission: two actually closed 50 Hz experts, costs already canonical."""
from pathlib import Path
import hashlib,json,os,psutil
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(spec,B):
 read=lambda p:json.loads(Path(p).read_bytes());key=spec['key'];counts={'e2':[175,98],'recovery':[173,96]}[key];m=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');proof=read(B/'CURRENT_ORIGINAL_COHORT_CLOSED_COST_CPU_ACTUAL.json');model=proof['models'][key];old=Path(spec['previous_runtime_root']);ne=read(old/'NODE_EXIT_ACTUAL.json');row=read(old/'NODE_TERMINAL_ACTUAL.json')['row'];cpu=read(B/'TARGET_TWO50_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json')
 assert spec['policy_hz']==spec['source_policy_hz']==50 and proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out']
 assert model['final']['SHA']==m['source_SHA']==spec['source_SHA'] and model['Adam']==m['source_Adamstep']==spec['source_Adamstep'] and model['counts']==counts
 assert ne['actual_all_own_children_waited'] and ne['validation_fcntl_released_if_acquired'] and row['terminal_all_own_children_waited'] and row['returncode']==0 and not row['errors'] and row['final']['passed'] and row['final']['final']['SHA']==spec['source_SHA']
 assert not any(p.pid!=os.getpid() and any(a.startswith(str(old)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
 assert read(old/'job0/production/POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json')['policy_hz']==50
 before={x['relative']:x for x in read(B/'QUALIFIED_RUNTIME_BASE_MANIFEST.json')['files']}
 for x in m['files']:
  if x['relative'].startswith(('job0/runtime/','job0/assets/','lib/')):assert x['SHA']==before[x['relative']]['SHA'] and x['bytes']==before[x['relative']]['bytes']
 assert cpu['passed_CPU_only'] and cpu['source_SHA']==spec['source_SHA'] and cpu['source_schema_counts']==counts and cpu['all17Adam']==spec['source_Adamstep'] and cpu['manifest_SHA']==H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
 v=dict(kind='closed_same_backend_policy50_production',key=key,passed=True,source_SHA=spec['source_SHA'],GPU_UUID=spec['GPU_UUID'],execution_backend=spec['execution_backend'],all_source_model_runtime_finite_CPU=True,old_complete_production_checkpoint_actual_EXIT0=True,explicit_policy_clock_50Hz_admitted=True,policy_clock_native_CPU_SHA=None,same_clock_closed_production=True,source_cost_original_account_ready=True,source_account_reconciliation_receipt_SHA=H(B/'CURRENT_ORIGINAL_COHORT_CLOSED_COST_CPU_ACTUAL.json'),original_clip6_query_COM_closure_mimic_hardware_savedstop_guards_retained=True,not_another_skill_pass=True)
 return dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True)
