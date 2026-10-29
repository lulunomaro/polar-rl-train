"""Reject unexecuted V1 Windows Path conversion; selectedV2 preserves remote POSIX."""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;R=N/'reports'
old=N/'install_NEW116_one_actual_target_sourceSDK_fullstate_CPU_UNUSED_once.py'
assert not (R/'NEW116_ONE_ACTUAL_TARGET_CPU_ENTRY_CONSUMED.json').exists()
s=old.read_text(encoding='utf8');new=s.replace('from pathlib import Path\n','from pathlib import Path,PurePosixPath\n',1)
a="old_root=str(Path(prep['source']['path']).parent.parent.parent)";b="old_root=str(PurePosixPath(prep['source']['path']).parent.parent.parent)"
assert new.count(a)==1;new=new.replace(a,b).replace("R/'FROZEN_NEW116_ONE_TARGET_CPU_ENTRY_SOURCE_INDEX.json'","R/'FROZEN_NEW116_ONE_TARGET_CPU_ENTRY_SOURCE_INDEX_V2.json'")
entry=N/'install_NEW116_one_actual_target_sourceSDK_fullstate_CPU_UNUSED_once_v2.py';assert not entry.exists();entry.write_text(new,encoding='utf8',newline='\n');ast.parse(new)
prep=json.loads((R/'NEW116_ONE_TYPED_REWARD_PAYLOAD_PREPARED_SOURCE_ONLY.json').read_bytes());proof=R/'SOURCE116_PREINSTALL_TASK_GO_OWN_FK_COUNTEREXAMPLE_CPU_ACTUAL.json'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with (R/'FROZEN_NEW116_ONE_TARGET_CPU_ENTRY_SOURCE_INDEX_V2.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),entry=str(entry),entry_SHA=H(entry),manifest_SHA=prep['manifest_SHA'],source_CPU_SHA=H(proof),V1_not_executed_not_selected=True,V1_entry_SHA=H(old),source_only=True,change=a+' -> '+b),f,indent=2)
print('Selected NEW116 V2 CPU entry sealed; V1 never executed')
