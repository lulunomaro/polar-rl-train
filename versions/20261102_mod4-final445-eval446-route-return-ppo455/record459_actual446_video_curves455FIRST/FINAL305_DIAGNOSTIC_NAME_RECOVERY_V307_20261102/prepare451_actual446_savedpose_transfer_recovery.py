"""Independent451 transfer/render preparation; frozen446copiedartifacts and failures stay untouched."""
from pathlib import Path
import ast
import hashlib
import json
import time

P=Path(__file__).resolve().parent;T=P.parent
E=T/'RL445_FINAL_INDEPENDENT_EVAL_V446_20261102'
C=T/'RL445_ACTUAL446_REPLAY_RECOVERY_V451_20261102'
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
read=lambda path:json.loads(path.read_bytes())
assert not C.exists()
actual=read(E/'reports/ROOT446_EVALUATION_FULL_RETURNED.json');result=actual['result']
assert not actual['wrapper_error']and result['passed']and len(result['replay'])==4
C.mkdir();(C/'reports').mkdir()
task=dict(kind='ACTUAL446_SAVED_POSE_RETRIEVAL_ONLY451',source_modelSHA=result['model_SHA'],
    source_result=str(E/'reports/ROOT446_EVALUATION_FULL_RETURNED.json'),
    source_resultSHA=H(E/'reports/ROOT446_EVALUATION_FULL_RETURNED.json'),
    source_evaluation_job=actual['job'],cases=result['replay'],
    original446error_preserved=True,original_eval_will_not_rerun=True,
    modelreads=0,SDK=0,physics=0,canonical_writes=0,account_writes=0,
    required_freshLOCALallknowncontrollers_serialFREE=True,
    parent_freshCNone_private_shared_nonblocking=True)
with(C/'TASK451_FROZEN.json').open('x',encoding='utf8')as stream:json.dump(task,stream,indent=2)
view=(E/'view446_actual_RL_replay.py').read_text('utf8')
view=view.replace("N=Path(__file__).resolve().parent;R=N/'reports';O=N/'VISIBLE_REPLAY446'", "N=Path(__file__).resolve().parent;R=N/'reports';O=N/'VISIBLE_REPLAY451'")
view=view.replace('ROOT446_SELECTED_REPLAY_TRANSFERS.json','ROOT451_ACTUAL446_SELECTED_REPLAY_TRANSFERS.json')
view=view.replace("policy_updates=161", "policy_updates=169")
ast.parse(view);(C/'view451_actual446_savedposes.py').write_bytes(view.encode('utf8'))
render=(E/'render446_recorded_frames.py').read_text('utf8')
render=render.replace('view446_actual_RL_replay.py','view451_actual446_savedposes.py')
render=render.replace("O=N/'VISIBLE_REPLAY446'", "O=N/'VISIBLE_REPLAY451'")
render=render.replace('RECORDED446_NATIVE_FRAMES','RECORDED451_ACTUAL446_NATIVE_FRAMES')
render=render.replace('ACTUAL446_RL_BODY_POSE_SEQUENCE.png','ACTUAL451_FINAL445_EVAL446_BODY_POSE_SEQUENCE.png')
ast.parse(render);(C/'render451_actual446_savedposes.py').write_bytes(render.encode('utf8'))
print(json.dumps(dict(passed=True,root=str(C),cases=4,totalbytes=sum(row['bytes']for row in result['replay']),modelreads=0,SDK=0,physics=0,network=0)),flush=True)
