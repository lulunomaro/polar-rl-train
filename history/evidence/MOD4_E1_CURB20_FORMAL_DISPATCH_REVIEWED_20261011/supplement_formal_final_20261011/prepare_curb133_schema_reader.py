"""Separate read-only reviewer for actual terrain and legacy skill schemas."""
from pathlib import Path
import json,hashlib,time
D=Path(__file__).resolve().parent;R=D/'reports';old=D/'review_formal_reviewed_curb133_actual.py';new=D/'review_formal_reviewed_curb133_schema_actual.py'
assert not new.exists()
collection=json.loads(sorted(R.glob('CURB133_COLLECTED_[0-9]*.json'))[-1].read_bytes());row=next(iter(collection['cases'].values()));p=row['probe']
assert 'checkpoint_sha256' not in p and 'checkpoint' in p and row['result']['checkpoint']['sha256']==collection['passed']['checkpoint']['sha256']==row['manifest']['artifacts']['checkpoint']['sha256']
src=old.read_text(encoding='utf8');needle="  assert r['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']==p['checkpoint_sha256']==b['checkpoint']['sha256']"
assert src.count(needle)==1
replacement="""  assert r['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']==b['checkpoint']['sha256']
  if 'full_route_raw' in p:assert p['checkpoint_sha256']==b['checkpoint']['sha256']
  else:assert p['checkpoint'].replace('\\\\','/').lower()==('D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs/'+jid+'/checkpoint.bin').lower()"""
src=src.replace(needle,replacement).replace("'CURB133_REVIEW_'","'CURB133_SCHEMA_REVIEW_'").replace("'CURB133_REVIEW_ERROR_'","'CURB133_SCHEMA_REVIEW_ERROR_'")
compile(src,str(new),'exec');new.write_bytes(src.encode())
v=dict(epoch=time.time(),trial_id='CURB133-REVIEWER-LEGACY-SKILL-SCHEMA-01',original_error='KeyError checkpoint_sha256 before independent data audit',original_reader_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),actual_skill_probe_has_checkpoint_path_without_SHA=True,actual_result_checkpoint_SHA_equals_manifest_and_own_formal=True,terrain_probe_SHA_contract_retained=True,new_skill_path_bound_to_exact_job_checkpoint=True,new_reader_sha256=hashlib.sha256(new.read_bytes()).hexdigest(),no_physics_GPU_learning_budget_or_old_result_change=True)
(R/'CURB133_ACTUAL_SCHEMA_READER_REVIEW.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
