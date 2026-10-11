from pathlib import Path
import time,json
D=Path(__file__).resolve().parent
root='/home/egde/rl_candidates/MOD4_S3_E1_SLOPE5_SNAPSHOT_REVIEWED_20261011'
for old,new in (('read_slope_actual.py','read_slope_snapshot_actual.py'),('collect_slope135_actual.py','collect_slope_snapshot135_actual.py')):
 p=D/new;assert not p.exists();s=(D/old).read_text();s=s.replace('from slope_io import *','from slope_io import *\nNEW='+repr(root))
 if old.startswith('read_'):
  s=s.replace('==402','==404').replace('source_count=402','source_count=404').replace("'SLOPE_ACTUAL_'","'SLOPE_SNAPSHOT_ACTUAL_'").replace("D/'actual_remote'","D/'snapshot_actual_remote'")
 compile(s,str(p),'exec');p.write_text(s,encoding='utf8')
(D/'reports/SNAPSHOT_READONLY_READERS_PREPARED.json').write_text(json.dumps(dict(epoch=time.time(),root=root,source_count=404,old_readers_retained=True,collection_no_eval_replay=True),indent=2))
