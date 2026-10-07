"""Build a new entry with two explicit additions; old frozen train file stays exact."""
from pathlib import Path
import ast,json
D=Path(__file__).resolve().parent
t=(D/'reports/runtime_source/isaac/mod4/train_sensor_ppo.py').read_text()
a='    from sensor_a0_runtime import install_sensor_save_contract';assert t.count(a)==1
t=t.replace(a,'    from sensor_resume_contract import resume_sensor_new_episode\n    resume_sensor_new_episode(runner,env,args.init_checkpoint,log_dir)\n'+a)
a='    manifest["sensor_recipe"]=env._sensor_mild.receipt()';assert t.count(a)==1
t=t.replace(a,'    for name in ("sensor_resume_contract.py","train_sensor_resume_ppo.py"):\n        shutil.copy2(Path(__file__).parent/name,snapshot_dir/name);snapshot[name]=_sha256(Path(__file__).parent/name)\n'+a)
ast.parse(t);(D/'continuation_source/train_sensor_resume_ppo.py').write_text(t)
print(json.dumps(dict(only_resume_and_own_snapshot_added=True,old_train_unchanged=True)))
