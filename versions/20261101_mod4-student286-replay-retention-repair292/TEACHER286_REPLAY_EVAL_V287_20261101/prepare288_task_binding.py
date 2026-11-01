from pathlib import Path
import ast,hashlib,json,time
OLD=Path(__file__).resolve().parent;T=OLD.parent;N=T/'TEACHER286_REPLAY_EVAL_V288_20261101';N.mkdir(exist_ok=False)
(N/'reports').mkdir();(N/'source').mkdir()
for p in(OLD/'source').rglob('*.py'):
 if '__pycache__'in p.parts:continue
 rel=p.relative_to(OLD/'source');rel=rel.with_name(rel.name.replace('287','288'));q=N/'source'/rel;q.parent.mkdir(parents=True,exist_ok=True)
 text=p.read_text('utf8').replace('287','288');ast.parse(text);q.write_text(text,encoding='utf8')
for name in('contract287.py','run287_eval_once.py'):
 text=(OLD/name).read_text('utf8').replace('287','288');ast.parse(text);(N/name.replace('287','288')).write_text(text,encoding='utf8')
task=json.loads((OLD/'TASK287_FROZEN.json').read_bytes());task['kind']=task['kind'].replace('287','288')
task.update(current_authority_binding=dict(kind='FRESH_CNONE',authority_generation='MOD4_SINGLE_WRITER72_20261026'),
 worker_SHA=hashlib.sha256((N/'source/evaluate288.py').read_bytes()).hexdigest())
(N/'TASK288_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
(N/'reports/TASK288_BINDING_REPAIR.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='eval288-new-purpose-binding-repair',
 original287_false_preserved=True,error='missing current_authority_binding Task field consumed by existing parent',
 original_failure_before_worker_model_or_SDK=True,source_learner_unchanged=True,repair='explicit FRESH_CNONE authority binding'),indent=2),encoding='utf8')
print(json.dumps(dict(prepared=str(N))))
