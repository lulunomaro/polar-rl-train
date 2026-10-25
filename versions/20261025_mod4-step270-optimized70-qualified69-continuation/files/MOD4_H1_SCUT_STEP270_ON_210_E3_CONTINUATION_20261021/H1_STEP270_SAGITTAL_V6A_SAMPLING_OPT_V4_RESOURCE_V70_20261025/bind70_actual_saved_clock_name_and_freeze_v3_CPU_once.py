"""Preserve uninstalledV2 bytes, bind the actual saved clock filename before deployment."""
from pathlib import Path
import ast,hashlib,json,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
P=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V4_RESOURCE_V69_20261025'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
assert not (R/'PAIR_DEPLOY_STARTED_ACTUAL.json').exists()
clock=read(P/'current_pair_closed_text/recovery/job0/production/POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json')
assert clock['policy_hz']==50 and clock['physics_dt_s']==.0025 and clock['decimation']==8
source=N/'same_optimized_installed_source_admission_v2.py';text=source.read_text('utf8')
needle="'job0/production/E3_POLICY50_CLOCK_ACTUAL.json'";assert text.count(needle)==1
text=text.replace(needle,"'job0/production/POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json'",1)
target=N/'same_optimized_installed_source_admission_v3.py'
with target.open('x',encoding='utf8') as f:f.write(text)
ast.parse(text)
history=N/'preinstall_v2_exact_bytes_history';history.mkdir()
q=read(R/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
shutil.copy2(R/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json',history/'PREPARED_q_V2.json')
for key in ('h1','recovery'):
 out=Path(q['payloads'][key]);hist=history/key;hist.mkdir()
 role='closed_production_continuation_CPU_v2.py' if key=='h1' else 'original_account_policy50_source_CPU.py'
 for name in (role,'SAME_OPTIMIZED_CONTINUATION_SOURCE_AUTH_ACTUAL.json','THREE_SLOT_COMPLETE_MANIFEST_V1.json'):shutil.copy2(out/name,hist/name)
 shutil.copy2(target,out/role)
 auth=read(out/'SAME_OPTIMIZED_CONTINUATION_SOURCE_AUTH_ACTUAL.json');auth.update(new_guard_SHA=H(out/role),actual_saved_policy50_clock_filename='POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json',uninstalled_V2_exact_bytes_retained_at=str(hist))
 (out/'SAME_OPTIMIZED_CONTINUATION_SOURCE_AUTH_ACTUAL.json').write_text(json.dumps(auth,indent=2),encoding='utf8')
 manifest=read(out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
 for row in manifest['files']:
  if row['relative'] in (role,'SAME_OPTIMIZED_CONTINUATION_SOURCE_AUTH_ACTUAL.json'):
   p=out/row['relative'];row.update(bytes=p.stat().st_size,SHA=H(p))
 (out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(manifest,indent=2),encoding='utf8');q['specs'][key]['manifest_SHA']=H(out/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
(R/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').write_text(json.dumps(q,indent=2),encoding='utf8')
report=dict(epoch=time.time(),passed=True,kind='preinstall_clock_filename_review_V3_no_training_failure',unused_V2_source_and_all_bound_auth_manifest_q_bytes_retained=True,old_assumed_filename='E3_POLICY50_CLOCK_ACTUAL.json',actual_saved_filename='POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json',actual_saved_clock=clock,guard_SHA=H(target),no_remote_install_GO_or_fee=True)
with (R/'ACTUAL_SAVED_CLOCK_NAME_BINDING_V3_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(passed=True,actual_saved_clock_50Hz=True,uninstalled_V2_preserved=True,no_GO=True)))
