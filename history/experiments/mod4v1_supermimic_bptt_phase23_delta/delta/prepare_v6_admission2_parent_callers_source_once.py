"""Create NEW metadata-bound caller purposes after an actual zero-GO timeout.
No native invocation, source helper change, owner retry, SDK, model or C operation.
"""
from pathlib import Path
import ast,json,hashlib,difflib
R=Path(__file__).resolve().parent;out=R/'reports/V6_ADMISSION2_PARENT_CALLER_SOURCE_BUILD_V1.json';assert not out.exists()
file_pairs=[('upload_and_preflight_new_a1_v6_once.py','upload_and_preflight_new_a1_v6_admission2_once.py'),('stage_new_a1_v6_after_source_preflight_once.py','stage_new_a1_v6_admission2_after_source_preflight_once.py'),('dispatch_new_a1_v6_original_owner_once.py','dispatch_new_a1_v6_admission2_original_owner_once.py'),('collect_a1_native_v6_metadata_once.py','collect_a1_native_v6_admission2_metadata_once.py')]
metadata_names=['A1_NATIVE_V6_SOURCE_INPUT_ONCE.json','A1_NATIVE_V6_ACTUAL_SOURCE_PREFLIGHT_V1.json','A1_NATIVE_V6_ACTUAL_NONPT_STAGE_V1.json','A1_NATIVE_V6_NONPT_STAGE_ONCE.json','A1_NATIVE_V6_ORIGINAL_OWNER_DISPATCH_V1.json','A1_NATIVE_V6_ORIGINAL_OWNER_DISPATCH_ONCE.json','A1_NATIVE_V6_DISPATCH_READONLY_PREFLIGHT_V1.json','PARENT_A1_V6_DISPATCH_MARKER.json','A1_NATIVE_V6_OBSERVER_STARTED_ONCE.json','A1_NATIVE_V6_LATEST_METADATA_WATCH.json','A1_NATIVE_V6_LATEST_CLOSED_RESULT_PATH.json']
prior_gate="""
# Admission2 is allowed only after actual prior V6 zero-GO closure, never a physical replay.
prior_pointer=json.loads((R/'A1_NATIVE_V6_LATEST_CLOSED_RESULT_PATH.json').read_bytes());prior_closed=json.loads(Path(prior_pointer['path']).read_bytes());prior_exit=prior_closed['parent_exit'];assert all(prior_exit[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'));assert len(prior_closed['rows'])==8 and all(x['status']=='CLOSED_UNSTARTED'and x.get('actual_GO')is None and x.get('startup')is None and x.get('final')is None for x in prior_closed['rows']);assert'Original preGOresourcewait1800expired'in json.dumps(prior_exit['errors'])
"""
release_gate="""
# Stage is nonPT preparation only. Actual later dispatch additionally needs a post-closure release witness.
release=json.loads((R/'reports/A1_V6_RELEASE_OBSERVED_AFTER_TIMEOUT_V2.json').read_bytes());assert release['returncode']==0 and release['original_canonical_and_authority_private_locks_observed_clear']is True;assert release['prior_root']==prior_closed['root']and release['actual']['epoch']>prior_exit['epoch']
"""
rows=[]
for old_name,new_name in file_pairs:
 source=R/old_name;dest=R/new_name;assert not dest.exists();old=source.read_text(encoding='utf-8');new=old
 for name in metadata_names:
  if name in new:new=new.replace(name,name.replace('A1_NATIVE_V6_','A1_NATIVE_V6_ADMISSION2_').replace('PARENT_A1_V6_','PARENT_A1_V6_ADMISSION2_'))
 if old_name.startswith('upload_'):
  token="run='MOD4V1_A1_RAW35_V6_'";assert new.count(token)==1;new=new.replace(token,"run='MOD4V1_A1_RAW35_V6_ADMISSION2_'");token="[REDACTED]";assert new.count(token)==1;new=new.replace(token,prior_gate+'\n'+token)
 if old_name.startswith('dispatch_'):
  token='[REDACTED]';assert new.count(token)==1;new=new.replace(token,prior_gate+'\n'+release_gate+'\n'+token)
 if old_name.startswith('collect_'):new=new.replace("'ACTUAL_A1_NATIVE_V6_'","'ACTUAL_A1_NATIVE_V6_ADMISSION2_'")
 # Frozen CLI/owner logical ABI and immutable14source identity never change.
 assert'PARENT_APPROVED_NEW_A1_NATIVE_V6_ADMISSION2_DISPATCH_ONCE'not in new
 if old_name.startswith('dispatch_'):assert'PARENT_APPROVED_NEW_A1_NATIVE_V6_DISPATCH_ONCE'in new
 if old_name.startswith('upload_'):assert"P=R/'payload_a1_v6_small_source'"in new and'f12617c45596c752de12050e17132d9dfab0aea8ed1336abe23d8e0ce256fa90'in new
 new='''# NEW admission2 purpose: prior original1800 preGO timeout had zero physical GO; do not extend or replay it.\n'''+new
 ast.parse(new);dest.write_text(new,encoding='utf-8');patch=R/(new_name+'.SOURCE_PURPOSE_DIFF.patch');patch.write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=old_name,tofile=new_name)),encoding='utf-8');rows.append(dict(source=str(source),source_SHA=hashlib.sha256(old.encode()).hexdigest(),path=str(dest),bytes=len(new.encode()),SHA=hashlib.sha256(new.encode()).hexdigest(),patch=str(patch)))
out.write_text(json.dumps(dict(kind='NEW_UNUSED_ADMISSION2_CALLER_SOURCE_METADATA_BINDING_ONLY',rows=rows,native_source_helper_pins_changed=0,models_SDK_remote_C_locks_GO_owner_operations=0,not_stage_or_dispatch=True),indent=2),encoding='utf-8');print(json.dumps(dict(source_callers=len(rows),output=str(out),no_stage_or_native_admission=True),indent=2))
