"""Explicit clock migration/continuation admission; never relabel it unchanged 100 Hz production."""
from pathlib import Path
import hashlib,json,os,psutil
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(spec,B):
 read=lambda p:json.loads(p.read_bytes());m=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');p=read(B/'CLOSED_PRODUCTION_SOURCE_PROVENANCE.json');old=Path(spec['previous_runtime_root']);co=read(Path(p['previous_pending_owner_root'])/'COHORT_FINAL.json');oe=read(Path(p['previous_pending_owner_root'])/'OWNER_EXIT_ACTUAL.json');ne=read(old/'NODE_EXIT_ACTUAL.json');row=read(old/'NODE_TERMINAL_ACTUAL.json')['row']
 assert spec['policy_hz']==50 and spec['source_policy_hz'] in (50,100) and spec['source_SHA']==m['source_SHA']==p['source_SHA'] and spec['source_Adamstep']==m['source_Adamstep']==p['Adam']
 assert co['pending_cost_record_complete'] and oe['pending_cost_record_complete'] and co['original_cost_settled'] is False and co['pending_cost']['canonical_settled'] is False and co['pending_cost']['run_id']==p['previous_pending_run_id'] and set(co['go'])=={'recovery'}
 assert co['pending_cost']['cost']['actual_returncode']==0 and co['pending_cost']['cost']['duration_bound_passed'] and co['pending_cost']['cost']['actual_production_seconds']>0
 assert ne['actual_all_own_children_waited'] and ne['validation_fcntl_released_if_acquired'] and row['terminal_all_own_children_waited'] and row['returncode']==0 and not row['errors'] and row['final']['passed'] and row['final']['final']['SHA']==spec['source_SHA']
 for r in (old,Path(p['previous_pending_owner_root'])):
  assert not any(z.pid!=os.getpid() and any(a.startswith(str(r)+'/') for a in z.info['cmdline'] or []) for z in psutil.process_iter(['pid','cmdline']))
 current=read(B/'TARGET_FULL_SOURCE_INSTALLED_RSL_SDK_CPU_ADMITTED_ACTUAL.json');assert current['passed_CPU_only'] and current['source_SHA']==spec['source_SHA'] and current['source_schema_counts']==[173,96] and current['all17Adam']==spec['source_Adamstep']
 proof=read(B/'PREVIOUS_CLOSED_WHOLE_MODEL_CPU_REPORT.json');assert proof['passed'] and proof['final']['SHA']==spec['source_SHA'] and proof['all17Adam_after']==spec['source_Adamstep']
 changed={x['relative']:x for x in read(B/'POLICY50_OVERLAY_BINDING_ACTUAL.json')['changes']}
 for r in m['files']:
  rel=r['relative']
  if rel.startswith(('job0/runtime/','job0/assets/','lib/')):
   q=old/rel
   if rel in changed:assert H(q) in (changed[rel]['baseline_SHA'],changed[rel]['candidate_SHA']) and r['SHA']==changed[rel]['candidate_SHA']
   else:assert q.stat().st_size==r['bytes'] and H(q)==r['SHA']
 native=None
 if spec['source_policy_hz']==100:
  native=read(B/'POLICY50_CLOCK_RUNTIME_CPU_ADMITTED_ACTUAL.json');assert native['passed'] and native['source_SHA']==spec['source_SHA'] and native['source_actor9_critic8_STD17Adam_literal_exact']
 else:
  assert read(old/'job0/production/POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json')['policy_hz']==50
 v=dict(kind='policy_clock_100_to_50_migration' if spec['source_policy_hz']==100 else 'closed_same_backend_policy50_production',key='recovery',passed=True,source_SHA=spec['source_SHA'],GPU_UUID=spec['GPU_UUID'],execution_backend=spec['execution_backend'],all_source_model_runtime_finite_CPU=True,old_complete_production_checkpoint_actual_EXIT0=True,explicit_policy_clock_50Hz_admitted=True,policy_clock_native_CPU_SHA=H(B/'POLICY50_CLOCK_RUNTIME_CPU_ADMITTED_ACTUAL.json') if native else None,same_clock_closed_production=spec['source_policy_hz']==50,original_clip6_query_COM_closure_mimic_hardware_savedstop_guards_retained=True,not_another_skill_pass=True)
 return dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True)
