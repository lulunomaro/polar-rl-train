"""Same-backend healthy full-production continuation for the three independent experts."""
from pathlib import Path
import json,hashlib,os,psutil,ast
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
COUNTS={'h1':[199,105],'e2':[175,98],'recovery':[173,96]}
def normalize_worker(text,p):
 text=text.replace(p['new_source_filename'],p['previous_source_filename']).replace(str(p['Adam']),str(p['previous_Adam']))
 return text
def validate(p,spec,m):
 key=spec['key'];assert key==m['key']==p['key'] and key in COUNTS and p['kind']=='closed_same_backend_production'
 assert p['source_SHA']==spec['source_SHA']==m['source_SHA'] and p['GPU_UUID']==spec['GPU_UUID'] and p['execution_backend']==spec['execution_backend'];assert p['Adam']==m['source_Adamstep']==spec['source_Adamstep'] and p['whole_tensor_counts']==m['source_schema_counts']==COUNTS[key]
 assert p['all_model_runtime_finite'] and p['actual_original_owner_node_all_children_out'] and p['original_cost_once_settled'] and p['not_failed_partial_prefix'];assert p['native_runtime_assets_digest']==m['native_runtime_assets_digest'];assert p['unchanged_PPO_and_physical_guard_AST'] and p['whole_model_CPU_report_SHA'];return True
def load(spec,B):
 m=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());p=json.loads((B/'CLOSED_PRODUCTION_SOURCE_PROVENANCE.json').read_bytes());validate(p,spec,m);old=Path(spec['previous_runtime_root']);e=json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes());r=json.loads((old/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and r['returncode']==0 and not r['errors'] and r['final']['passed'];saved=r['final']['final'];assert saved['SHA']==m['source_SHA'] and saved['updates']==p['actual_previous_updates'] and saved['phase']=='production' and not saved.get('failed_partial_prefix',False);assert Path(saved['path']).stat().st_size==saved['bytes']
 for row in m['files']:
  if row['relative'].startswith(('job0/runtime/','job0/assets/','lib/')):
   q=old/row['relative'];assert q.stat().st_size==row['bytes'] and H(q)==row['SHA']
 before=(old/p['worker_filename']).read_text('utf8');after=normalize_worker((B/p['worker_filename']).read_text('utf8'),p);assert ast.dump(ast.parse(before))==ast.dump(ast.parse(after))
 current=json.loads((B/'TARGET_FULL_SOURCE_INSTALLED_RSL_SDK_CPU_ADMITTED_ACTUAL.json').read_bytes());assert current['passed_CPU_only'] and current['source_SHA']==m['source_SHA'] and current['source_schema_counts']==COUNTS[spec['key']] and current['all17Adam']==p['Adam'];assert not any(q.pid!=os.getpid() and any(s.startswith(str(old)+'/') for s in q.info['cmdline'] or []) for q in psutil.process_iter(['pid','cmdline']))
 v=dict(kind='closed_same_backend_production',key=spec['key'],passed=True,source_SHA=m['source_SHA'],GPU_UUID=spec['GPU_UUID'],execution_backend=spec['execution_backend'],all_source_model_runtime_finite_CPU=True,old_complete_production_checkpoint_actual_EXIT0=True,same_active_runtime_assets_and_PPO_AST=True,original_clip6_query_COM_closure_mimic_hardware_savedstop_guards_retained=True,not_another_native_or_frozen_skill_pass=True,whole_model_CPU_report_SHA=p['whole_model_CPU_report_SHA']);return dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True)
