from pathlib import Path
import hashlib,json,sys,traceback,time
B=Path(__file__).resolve().parent
original=Path('C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\\MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027\\E3_97_SOURCE210_ORIGINAL_FLAT_HEIGHT_PROVIDER_REPAIR_SOURCE_20261029_V3\\run_E3_source210_readonly_v3.py')
index=json.loads((original.parent/'FROZEN_E3_97_SOURCE210_RECIPE_DOMAIN_SOURCE_INDEX_V3.json').read_bytes())
raw=original.read_bytes();assert hashlib.sha256(raw).hexdigest()==index['local_source_SHAs'][original.name]
s=raw.decode('utf8');a="str(Path(JOB)/'detached_E3_source210_frozen_recipe_supervisor_once_v1.py')";b="str(PurePosixPath(JOB)/'detached_E3_source210_frozen_recipe_supervisor_once_v1.py')";assert s.count(a)==1
s=s.replace('from pathlib import Path','from pathlib import Path,PurePosixPath',1).replace(a,b)
ns=dict(__name__='new_readonly_POSIX_fix_definitions_only',__file__=str(original));exec(compile(s,str(original),'exec'),ns)
try:ns['main']('terminal')
except BaseException:
 with (B/'reports'/('ORIGINAL_METADATA_READER_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(traceback=traceback.format_exc(),no_model_GPU_or_training_action=True),f,indent=2)
 raise
