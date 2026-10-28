"""One missing-import correction before original reader main/once/network."""
from pathlib import Path
import hashlib,importlib.util,runpy,sys
B=Path(__file__).resolve().parent.parent
assert (B/'reports').is_dir()
ENTRY=B/'observe_two95_H1_NEW_Pi_then_E3_actual_PPO_combined_once_v1.py'
assert hashlib.sha256(ENTRY.read_bytes()).hexdigest()=='606ab5b7b155fcfa2ccfbab368f399e03588c80bcfe18abab30a2d93ef6ffeed'
assert not (B/'reports/TWO95_COMBINED_FIRST_OBSERVER_CONSUMED_ACTUAL.json').exists()
MODULES={'OWNER_read_only_CODE_v1': 'f118c4aaf639de88f7a15328a96cd2dcb6f1d21ef5a08e5dfe3c6508cf93acfa', 'NATIVE_read_only_CODE_v1': '10983c2369b181587cb56aabd3bd7c4932b13be134eed6430f4ff861cc3ede11', 'E3_read_only_CODE_v1': '2f101aea9953c9c78873dcfbeffad6a973cfa26561d390e02101845adb984aa8'}
for name,sha in MODULES.items():
 path=B/(name+'.py');assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
runpy.run_path(str(ENTRY),run_name='__main__')
