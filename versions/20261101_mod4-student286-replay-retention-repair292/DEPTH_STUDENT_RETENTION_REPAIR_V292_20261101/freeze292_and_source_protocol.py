from pathlib import Path
import ast,hashlib,importlib.util,json,time
N=Path(__file__).resolve().parent;R=N/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
taskpath=N/'TASK292_FROZEN.json';task=json.loads(taskpath.read_bytes())
task['source_CPU_report_SHA']=H(R/'CPU292_BOUNDED_UPDATE_SOURCE_TEST.json')
taskpath.write_text(json.dumps(task,indent=2),encoding='utf8')
spec=importlib.util.spec_from_file_location('protocol292',N/'teacher_task292.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
assert m.validate_task(task)
for p in N.rglob('*.py'):ast.parse(p.read_text('utf8'))
worker=(N/'source/worker292.py').read_text('utf8')
for s in ("ck['kind']=='LQR_MPC_DEPTH_TEACHER_STUDENT286_COMPLETE'",'wm.updates==7087','inherited_WM_updates=7087',"wm.updates>7087"):
    assert s in worker,s
assert H(N/'source/worker292.py')==task['worker_SHA']
learner=(N/'source/teacher_student292.py').read_text('utf8')
assert "self.optimizers['actor'].param_groups:group['lr']=1e-5" in learner
assert 'ground_loss+overflow_loss' in learner and 'bounded_actor_step' in learner
files=[p for p in sorted(N.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix in('.py','.json','.npz')]
index=N/'INDEX292_SOURCE_TASK_CALLERS_FROZEN.json'
with index.open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),kind='RETENTION292_FULL_SOURCE_TASK_CPU_FROZEN',files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files]),f,indent=2)
print(json.dumps(dict(passed=True,index_SHA=H(index),files=len(files),run_id=task['run_id'])))
