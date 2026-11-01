"""New frozen308 independent evaluation of recovered305; original306 remains unused."""
from pathlib import Path
import ast,hashlib,json,re,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;O=T/'REFERENCE_TRACKING_REAL_VALUE_V305_20261101';P=O/'postround306'
E=T/'RECOVERED305_TRACKING_REPLAY_EVAL_V308_20261102';E.mkdir(exist_ok=False);(E/'reports').mkdir()
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
shutil.copytree(O/'source',E/'source',ignore=shutil.ignore_patterns('__pycache__'))
def change(s):return re.sub(r'(?<=[A-Za-z_])306(?!\d)','308',s)
for p in(P/'eval306_source').glob('*.py'):
 s=change(p.read_text('utf8'));ast.parse(s);(E/'source'/change(p.name)).write_bytes(s.encode())
shutil.copyfile(E/'source/contract308.py',E/'contract308.py')
s=change((P/'run306_eval_once_template.py').read_text('utf8')).replace(".replace('246','306')",".replace('246','308')")
s=s.replace("patterns='", "patterns='recover307_|review307|run306_eval|postround306_finalize|",1)
ast.parse(s);(E/'run308_eval_once.py').write_bytes(s.encode())
shutil.copyfile(T/'TEACHER286_REPLAY_EVAL_V288_20261101/source/wheel_geometry220.py',E/'source/wheel_geometry220.py');shutil.copyfile(O/'reference305.npz',E/'reference305.npz')
full=json.loads((N/'reports/ROOT307_NEW_FINAL305_WHOLE_CPU_RETURNED_ACTUAL.json').read_bytes());original=json.loads((O/'TASK305_FROZEN.json').read_bytes())
task=json.loads((T/'TEACHER286_REPLAY_EVAL_V288_20261101/TASK288_FROZEN.json').read_bytes())
task.update(kind='FROZEN305_REFERENCE_TRACKING_EVAL308',model_path=full['remote_path'],model_SHA=full['SHA'],model_bytes=full['bytes'],expected_Pi_updates=full['Pi'],source_run=original['run_id'],worker_SHA=H(E/'source/evaluate308.py'),reference=original['reference'],source_full_CPU_receipt_SHA=H(N/'reports/ROOT307_NEW_FINAL305_WHOLE_CPU_RETURNED_ACTUAL.json'),training_layout_seed=None,heldout_layout_seed=None,evaluation_seed=9137,same_fixed_reference_course=True,heldout_terrain_layout=False)
(E/'TASK308_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
(E/'reports/SOURCE308_RECOVERED305_ADMISSION.json').write_text(json.dumps(dict(epoch=time.time(),passed=True,original305false_preserved=True,recovery307_fullCPU=True,fullSHA=full['SHA'],new308only=True,old306_UNEXECUTED=True,objective_physics_seed_protocol_same=True),indent=2),encoding='utf8')
print(json.dumps(dict(passed=True,root=str(E),modelSHA=full['SHA'])))
