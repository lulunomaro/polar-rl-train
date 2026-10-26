from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;D=N/'controllers_v2';R=N/'reports';p=D/'three_slot_finite_owner_V86_authority72.py'
raw=p.read_bytes();old=raw.decode('utf8');needle="shared['go'][key]=dict(learning_started_epoch=now,"
assert old.count(needle)==1
extra="shared['go'][key]=dict(manifest_SHA=spec['manifest_SHA'],bootstrap_SHA=spec.get('bootstrap_source_SHA'),bootstrap_Adam=(spec['source_Adamstep'] if spec.get('native_continuation') else None),native_continuation_restore_required=bool(spec.get('native_continuation')),source_native_iteration=spec.get('source_native_iteration'),window_start_world_updates=spec.get('window_start_world_updates'),window_start_policy_updates=spec.get('window_start_policy_updates'),learning_started_epoch=now,"
new=old.replace(needle,extra,1);ast.parse(new)
history=N/'source_history';history.mkdir(exist_ok=True)
with (history/'OWNER86_BEFORE_NATIVE_SIGNED_GO_FIELDS.py.txt').open('xb') as f:f.write(raw)
p.write_bytes(new.encode('utf8'))
result=dict(epoch=time.time(),source_only=True,old_owner_SHA=hashlib.sha256(raw).hexdigest(),new_owner_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),
 signed_GO_adds_only=['manifest_SHA','bootstrap_SHA','bootstrap_Adam','native_continuation_restore_required','source_native_iteration','window_start_world_updates','window_start_policy_updates'],
 no_Task_manifest_hash_cycle=True,old_account_GO_clock_charging_and_terminal_handling_unchanged=True,no_GO_or_runtime=True,
 controller_pins=[dict(relative=q.name,SHA=hashlib.sha256(q.read_bytes()).hexdigest(),bytes=q.stat().st_size) for q in sorted(D.glob('*.py'))])
(R/'OWNER86_NATIVE_SIGNED_GO_SOURCE_FIELDS_ACTUAL.json').write_text(json.dumps(result,indent=2),'utf8')
print(json.dumps({'signed_GO_source_only':True,'owner_SHA':result['new_owner_SHA']}))
