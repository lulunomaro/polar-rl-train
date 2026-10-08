"""Preserve CPU-only alias-reader rejection; validate the actual imported class."""
from pathlib import Path
import json
D=Path(__file__).resolve().parent
old=(D/'package_d5_path_review_once.py').read_text(encoding='utf8')
anchor=" assert ('SpringPressureMod4Env as Mod4Env' in s) if name.endswith('world.py') else ('SpringPressureMod4Env as ActionDelayMod4Env' in s)"
assert anchor in old
new=" imports=[n for n in ast.parse(s).body if isinstance(n,ast.ImportFrom) and n.module=='spring_pressure_training_env'];assert len(imports)==1 and imports[0].names[0].name=='SpringPressureMod4Env' and imports[0].names[0].asname in ('Mod4Env','ActionDelayMod4Env')"
assert not (D/'package_d5_dispatch_review_once.py').exists()
(D/'package_d5_dispatch_review_once.py').write_text(old.replace(anchor,new),encoding='utf8')
(D/'reports/D5_PACKAGE_ALIAS_READER_ERROR.json').write_text(json.dumps(dict(error='Static observer incorrectly expected spin direct Mod4Env import to use flat wrapper alias. Actual spin import was correct; rejection before ZIP/job publication. New AST checks imported SpringPressure class and valid direct/wrapper alias.',production_changed=False),indent=2),encoding='utf8')
