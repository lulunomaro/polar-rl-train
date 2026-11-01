from pathlib import Path
import ast,hashlib,json,shutil,time
O=Path(__file__).resolve().parent;T=O.parent;B=T/'TEACHER286_REPLAY_EVAL_V288_20261101';N=T/'FROZEN_SOURCE_COUNTERFACTUAL_V291_20261101';N.mkdir(exist_ok=False)
S=N/'source';shutil.copytree(O/'source',S,ignore=shutil.ignore_patterns('__pycache__'));R=N/'reports';R.mkdir()
for name in ('run290_eval_once.py','contract290.py'):
    out=N/name.replace('290','291');out.write_bytes((O/name).read_bytes().replace(b'290',b'291'))
worker=S/'evaluate291.py';text=(S/'evaluate290.py').read_bytes().replace(b'290',b'291')
text=text.replace(b"optimizer_constructs=0))",b"optimizer_constructs=0,actual_default_joint_pos=tensor(robot.data.default_joint_pos)[0].cpu().tolist(),actual_default_joint_vel=tensor(robot.data.default_joint_vel)[0].cpu().tolist(),joint_names=list(robot.joint_names)))")
worker.write_bytes(text)
(S/'contract291.py').write_bytes((N/'contract291.py').read_bytes())
(S/'terrain291.py').write_bytes((B/'source/terrain288.py').read_bytes())
task=json.loads((O/'TASK290_FROZEN.json').read_bytes());task['kind']=task['kind'].replace('290','291');task['worker_SHA']=hashlib.sha256(worker.read_bytes()).hexdigest()
(N/'TASK291_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
for p in N.rglob('*.py'):ast.parse(p.read_text('utf8'))
tree=ast.parse(worker.read_text('utf8'))
for node in ast.walk(tree):
    if isinstance(node,ast.Import):
        for item in node.names:
            if item.name.startswith('terrain'):assert (S/(item.name+'.py')).is_file()
    if isinstance(node,ast.ImportFrom) and node.module and node.module.startswith('contract'):assert (S/(node.module+'.py')).is_file()
(R/'SOURCE291_DEPENDENCY_REPAIR.json').write_text(json.dumps(dict(epoch=time.time(),original290='Missing terrain290; app closed before model read',repair='Explicit terrain291 from same9137 terrain288; named imports checked; actual-byte worker SHA',passed_AST=True,model_reads290=0,optimizer_steps290=0,actual_default_joint_metadata_added=True,prior_once_replayed=False),indent=2),encoding='utf8')
print(json.dumps(dict(passed=True,path=str(N),worker_SHA=task['worker_SHA'])))
