from pathlib import Path
import ast,hashlib,json,shutil,time
O=Path(__file__).resolve().parent;N=O.parent/'FROZEN_SOURCE_COUNTERFACTUAL_V290_20261101';N.mkdir(exist_ok=False)
S=N/'source';shutil.copytree(O/'source',S,ignore=shutil.ignore_patterns('__pycache__'));R=N/'reports';R.mkdir()
for name in ('run289_eval_once.py','contract289.py'):
    out=N/name.replace('289','290');out.write_bytes((O/name).read_bytes().replace(b'289',b'290'))
worker=S/'evaluate290.py';worker.write_bytes((S/'evaluate289.py').read_bytes().replace(b'289',b'290'))
(S/'contract290.py').write_bytes((N/'contract290.py').read_bytes())
task=json.loads((O/'TASK289_FROZEN.json').read_bytes());task['kind']=task['kind'].replace('289','290');task['worker_SHA']=hashlib.sha256(worker.read_bytes()).hexdigest()
(N/'TASK290_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
for p in N.rglob('*.py'):ast.parse(p.read_text('utf8'))
(R/'SOURCE290_ACTUAL_BYTE_HASH_REPAIR.json').write_text(json.dumps(dict(epoch=time.time(),original289='Rejected before SDK/model: text.encode SHA differed from Windows CRLF bytes',repair='Use actual written worker.read_bytes SHA; separate new Task and namespace',passed_AST=True,model_reads289=0,optimizer_steps289=0,prior_once_replayed=False),indent=2),encoding='utf8')
print(json.dumps(dict(passed=True,path=str(N),worker_SHA=task['worker_SHA'])))
