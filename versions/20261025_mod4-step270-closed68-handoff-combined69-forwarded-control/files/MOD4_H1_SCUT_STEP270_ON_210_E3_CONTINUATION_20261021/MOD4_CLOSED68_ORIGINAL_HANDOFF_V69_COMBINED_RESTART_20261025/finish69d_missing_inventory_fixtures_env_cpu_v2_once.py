"""New69d roots after pre-GO source inventory error; retain nested SOURCE_FREEZE bytes exactly."""
from pathlib import Path
import ast,copy,fnmatch,hashlib,importlib.util,json,shutil,time
D=Path(__file__).resolve().parent;T=D.parent;R=D/'reports'
P=T/'H1_STEP270_REWARD_SAGITTAL_TUCK_V6A_RESOURCE_V68_20261025'
old=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V3_RESOURCE_V69_20261025';N=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V4_RESOURCE_V69_20261025'
assert (R/'COMBINED69C_EXACT_NETWORK_SCOPE_DEPLOY_ORIGINAL_ERROR_ACTUAL.json').exists() and not(old/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').exists()
def ignore(path,names):
 return [n for n in names if n=='__pycache__' or n.endswith('.pyc') or (Path(path)==old and n=='reports')]
assert N.exists();nr=N/'reports';assert nr.is_dir() and not(nr/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').exists()
q=json.loads((old/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());q['epoch']=time.time();q['owner_root']=q['owner_root'].replace('_2510v69c/','_2510v69d/')
restored=[];checks={}
for key in q['specs']:
 q['roots'][key]=q['roots'][key].replace('_2510v69c/','_2510v69d/');q['payloads'][key]=str(N/'payloads'/key);base=N/'payloads'/key
 prior=json.loads((base/'QUALIFIED_RUNTIME_BASE_MANIFEST.json').read_bytes());before={x['relative']:x for x in prior['files']}
 for rel,row in before.items():
  if rel.startswith(('job0/runtime/','job0/assets/','lib/')) and not(base/rel).is_file():
   source=P/'payloads'/key/rel;assert source.is_file() and source.stat().st_size==row['bytes'] and hashlib.sha256(source.read_bytes()).hexdigest()==row['SHA']
   target=base/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);restored.append(dict(key=key,relative=rel,bytes=row['bytes'],SHA=row['SHA'],source=str(source)))
 p=base/'job0/TASK.json';task=json.loads(p.read_bytes());task['id']=N.name+'_'+key;task['network_loader_revision']='V4_PRESERVE_NESTED_SOURCE_FREEZE';p.write_text(json.dumps(task,indent=2),encoding='utf8')
 mf=base/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';m=json.loads(mf.read_bytes());prev={x['relative']:x for x in m['files']};rows=[]
 for p in sorted(base.rglob('*')):
  if not p.is_file() or p==mf or '__pycache__' in p.parts:continue
  rel=p.relative_to(base).as_posix()
  if p.suffix in ('.pt','.npz','.usd','.stl'):
   row=prev[rel];assert p.stat().st_size==row['bytes'];sha=row['SHA']
  else:sha=hashlib.sha256(p.read_bytes()).hexdigest()
  rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=sha))
 m['files']=rows;mf.write_text(json.dumps(m,indent=2),encoding='utf8');q['specs'][key]['manifest_SHA']=hashlib.sha256(mf.read_bytes()).hexdigest()
 protected=lambda rel:rel.startswith(('job0/runtime/','job0/assets/','lib/'))
 current={x['relative']:x for x in rows};x={x for x in before if protected(x)};y={x for x in current if protected(x)}
 assert y==x|({'job0/runtime/isaac/mod4/e3_reset_bank_cache_v1.py'} if key=='recovery' else set())
 guard=base/('closed_production_continuation_CPU_v2.py' if key=='h1' else 'original_account_policy50_source_CPU.py')
 sp=importlib.util.spec_from_file_location('guard_fixture_'+key,guard);module=importlib.util.module_from_spec(sp);sp.loader.exec_module(module)
 cpu_parent=T/('H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V2_RESOURCE_V69_20261025' if key=='h1' else old.name)
 receipt=cpu_parent/'reports'/('H1_FULL_INSTALLED_SOURCE_SDK_RSL_CPU_ACTUAL.json' if key=='h1' else 'RECOVERY_TWO50_FULL_TARGET_SOURCE_RSL_SDK_CPU_ACTUAL.json')
 cpu=copy.deepcopy(json.loads(receipt.read_bytes()));cpu['sampling_acceleration_CPU']['base']=str(base.resolve())
 # This is an offline path-bound fixture from actual identical acceleration source/bank proof.
 # New target still executes its own source/RSL/SDK/full-state CPU and one fresh-bank check.
 speed=module._sampling_receipt(base,P/'payloads'/key,key,m,before,cpu);assert speed['passed']
 checks[key]=dict(protected_inventory_exact=True,original_sampling_receipt_logic_fixture_passed=True,fixture_actual_receipt=str(receipt),fixture_local_path_rebound_only=True,not_remote_installed_admission=True)
q.update(preGO_V3_failure_preserved_in=str(old),new_unused_remote_roots=True,restored_exact_prior_runtime_report=restored)
for name in ['ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json','RESOURCE_BRANCH_PREPARE_DECISION_ACTUAL.json']:shutil.copy2(old/'reports'/name,nr/name)
with (nr/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(q,f,ensure_ascii=False,indent=2)
with (R/'NEXT69D_EXACT_RUNTIME_REPORT_RESTORED_AND_LOCAL_GUARD_FIXTURES_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,restored=restored,checks=checks,new_namespace=str(N),original_preGO_failures_preserved=True,new_no_remote_install_or_GO=True),f,ensure_ascii=False,indent=2)
print(json.dumps(dict(passed=True,restored=restored,checks=checks,no_GO=True)))
