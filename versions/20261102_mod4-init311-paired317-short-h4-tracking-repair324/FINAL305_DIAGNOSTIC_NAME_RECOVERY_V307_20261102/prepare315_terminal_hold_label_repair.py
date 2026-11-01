"""Prepare a new unused reference-label version; no checkpoint/SDK/network access."""
from pathlib import Path
import ast,hashlib,importlib.util,json,time,xml.etree.ElementTree as ET
N=Path(__file__).resolve().parent;T=N.parent
D=T/'REFERENCE_TERMINAL_HOLD_LABEL_REPAIR_V315_20261102'
assert not D.exists();D.mkdir();(D/'source').mkdir();(D/'reports').mkdir()
def put(name,value):
    with(D/'reports'/name).open('x',encoding='utf8')as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
old=T/'REFERENCE_TRACKING_REAL_VALUE_V305_20261101/source/tracking_reference305.py'
text=old.read_text('utf8')
needle="        index=phase.long().clamp(0,249);v=self.states[index].clone();wheel=self.wheels[index].clone()"
replacement=needle+"\n        # Beyond the final measured endpoint, keep its pose and target rest.\n        # The planned final sample still keeps its original velocities at249.\n        holding=phase.long()>249\n        v[holding,12:18]=0.\n        v[holding,48:78]=0."
assert text.count(needle)==1
text=text.replace(needle,replacement).replace('Reference305','Reference315').replace('tracking_cost305','tracking_cost315')
ast.parse(text);path=D/'source/tracking_reference315.py';path.write_bytes(text.encode())
put('SOURCE315_UNUSED_READY.json',dict(epoch=time.time(),status='NEW_UNUSED_CPU_VERIFICATION_PENDING',source=str(old),source_SHA=hashlib.sha256(old.read_bytes()).hexdigest(),derived=str(path),derived_SHA=hashlib.sha256(path.read_bytes()).hexdigest(),change='phase>249 pose fixed at final sample; rootlinear/angular/jointvelocity targets zero;phase0..249 unchanged',task_goal='human declared terminal stable/rest pose',causality='separate late-task label inconsistency; does not explain .26-.32s earlyorientation failure',deployed=False,GO=False,model_reads=0,SDK=0,network=0))
print(json.dumps(dict(passed=True,unused_root=str(D),source_SHA=hashlib.sha256(path.read_bytes()).hexdigest())))
