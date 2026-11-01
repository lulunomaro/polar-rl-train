from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;R=N/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
p=N/'review286_NEW_final_whole_CPU_UNUSED_once.py';ast.parse(p.read_text('utf8'))
report=R/'NEW_FINAL_CPU_READER_V1_AST_FALSE_AND_REPAIR.json'
put(report,dict(epoch=time.time(),trial_id='teacher286-new-final-reader-v1-ast-false',
 error='missing whitespace between else and42940 in conditional',old_false_source=str(R/'NEW_FINAL_CPU_READER_V1_AST_FALSE_SOURCE.py'),
 corrected_before_any_use=True,model_raw_SDK_GPU_network_optimizer_steps=0,
 purpose='one NEW normal-qualified286 full-tree CPU reader; pending original safe closure and unique formal'))
index=N/'INDEX286_NEW_FINAL_CPU_READER_FROZEN.json';put(index,dict(epoch=time.time(),kind='UNUSED_NEW286_FINAL_FULLTREE_CPU_READER',
 files=[dict(path=str(q),bytes=q.stat().st_size,SHA=H(q))for q in (p,N/'teacher_task286.py',Path(__file__),report)]))
put(R/'HANDOFF286_NEW_FINAL_CPU_UNUSED.json',dict(epoch=time.time(),reader=str(p),caller_index_SHA=H(index),
 after='normal286_v2 final/fees/locks/uniqueformal transfer PASS only',old_reader_replay=False,
 required='full finite tree/actor44critic47/STD6/full17teacher frozen/actor9critic8WM Adam/norm/RNG/DR/queue/memory/counts'))
print(json.dumps(dict(passed_AST=True,index_SHA=H(index))))
