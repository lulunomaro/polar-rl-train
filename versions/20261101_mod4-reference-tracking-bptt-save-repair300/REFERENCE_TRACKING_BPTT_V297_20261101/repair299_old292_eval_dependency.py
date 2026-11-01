from pathlib import Path
import ast,hashlib,json,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;O=T/'RETENTION292_POSTROUND_REPLAY_EVAL_V293_20261101';E=T/'RETENTION292_DEPENDENCY_REPLAY_EVAL_V299_20261101';E.mkdir(exist_ok=False);R=E/'reports';R.mkdir()
shutil.copytree(O/'source',E/'source',ignore=shutil.ignore_patterns('__pycache__'))
for name in('contract293.py','run293_eval_once.py'):
    text=(O/name).read_text('utf8').replace('293','299');p=E/name.replace('293','299');p.write_bytes(text.encode());ast.parse(text)
worker=E/'source/evaluate299.py';worker.write_bytes((O/'source/evaluate293.py').read_bytes().replace(b'293',b'299'))
(E/'source/contract299.py').write_bytes((E/'contract299.py').read_bytes())
(E/'source/terrain299.py').write_bytes((O/'source/terrain293.py').read_bytes())
shutil.copyfile(T/'TEACHER286_REPLAY_EVAL_V288_20261101/source/wheel_geometry220.py',E/'source/wheel_geometry220.py')
task=json.loads((O/'TASK293_FROZEN.json').read_bytes());task['kind']=task['kind'].replace('293','299');task['worker_SHA']=hashlib.sha256(worker.read_bytes()).hexdigest()
(E/'TASK299_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
for p in E.rglob('*.py'):ast.parse(p.read_text('utf8'))
with(R/'SOURCE299_ORIGINAL293_MISSING_DEPENDENCY_REPAIR.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),original='Actual293ModuleNotFoundErrorwheel_geometry220 afterscene before model read. All own waited/free androotSSHclosed.292fullsaveCPU passed.',repair='Independent299includes existing wheel220 dependency plus correctsame9137terrain; one new frozen292actor evaluation purpose, no oldonce replay.',modelreads293=0,trainingGO=0),f,indent=2)
print(json.dumps(dict(passed=True,eval=str(E))))
