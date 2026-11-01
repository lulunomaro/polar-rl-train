"""Final reader source-only key correction before first286 final model read."""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;R=N/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
old=N/'review286_NEW_final_whole_CPU_UNUSED_once.py'
text=old.read_text('utf8').replace('typed_TEACHER283_task','typed_TEACHER286_task')
text=text.replace('INDEX286_NEW_FINAL_CPU_READER_FROZEN.json','INDEX286_NEW_FINAL_CPU_V2_READER_FROZEN.json')
assert "typed_TEACHER286_task=TASK"in(N/'source/worker286.py').read_text('utf8')
assert "ck['typed_TEACHER286_task']"in text
ast.parse(text);new=N/'review286v2_NEW_final_whole_CPU_UNUSED_once.py'
with new.open('x',encoding='utf8')as f:f.write(text)
report=R/'NEW_FINAL_CPU_V2_ACTUAL_WORKER_KEY_SOURCE_JOIN.json'
put(report,dict(epoch=time.time(),trial_id='teacher286-final-CPU-v2-typed-key-source-join',
 old_reader_UNEXECUTED_preserved=True,reason='actual286 worker writes typed_TEACHER286_task; first reader retained original283 key',
 independent_fixed_reader=str(new),actual_worker_source_SHA=H(N/'source/worker286.py'),
 NEWfinal_model_reads=0,old_model_raw_SDK_GPU_network_reads=0,actual_source_AST_key_join=True))
index=N/'INDEX286_NEW_FINAL_CPU_V2_READER_FROZEN.json'
put(index,dict(epoch=time.time(),kind='UNUSED_NEW286_FINAL_CPU_V2_KEY_JOIN',files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in(new,N/'teacher_task286.py',report,Path(__file__))]))
handoff=R/'HANDOFF286_NEW_FINAL_CPU_V2_UNUSED.json'
put(handoff,dict(epoch=time.time(),reader=str(new),caller_index_SHA=H(index),old_v1_unused_retired=str(old),
 required_after='normal286_v2 full deadline save/owner originalfee/free locks/unique formal transfer PASS'))
print(json.dumps(dict(passed=True,reader=str(new),index_SHA=H(index))))
