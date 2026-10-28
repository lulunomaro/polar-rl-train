from pathlib import Path
import json,time,ast
S=Path(__file__).resolve().parent
old=S/'analyze_same_NEW98_motion_text_only_once.py'
with (S/'reports/ORIGINAL_NEW98_TEXT_READER_INITIAL_CACHE_KEYERROR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),original_entry=str(old),error="KeyError: 'wheel_bottom_above_floor_m'",scope='Only initial snapshot physics_callback0 has no derived wheel cache. All actual2000 physics callbacks have it.',no_model_read_new_physics_network_or_training=True),f,indent=2)
s=old.read_text(encoding='utf8');a="both_bottom=[min(row['state']['metrics']['wheel_bottom_above_floor_m']) for row in physics]";b="missing=[row['physics_callback'] for row in physics if 'wheel_bottom_above_floor_m' not in row['state']['metrics']]\nassert missing==[0]\nboth_bottom=[min(row['state']['metrics']['wheel_bottom_above_floor_m']) for row in physics if row['physics_callback']>0]\nassert len(both_bottom)==2000"
assert s.count(a)==1;s=s.replace(a,b);ast.parse(s)
exec(compile(s,str(old),'exec'),dict(__file__=str(old),__name__='__main__'))
