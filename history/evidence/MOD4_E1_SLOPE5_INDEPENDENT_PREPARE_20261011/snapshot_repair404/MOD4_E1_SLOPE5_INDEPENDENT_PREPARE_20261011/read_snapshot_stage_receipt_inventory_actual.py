from slope_io import *
n,w=connect_both()
try:
 v=linux_json(n,r'''from pathlib import Path
import json
D=Path(ROOT);runs=list((D/'discard_logs').glob('*_slope_discard20k_*'))
print(json.dumps(dict(runs=[dict(path=str(p),files=[q.name for q in p.glob('*')],startup=[q.name for q in p.glob('*STARTUP_VERIFIED.json')]) for p in runs])))
'''.replace('ROOT',repr(NEW)))
 save('SNAPSHOT_STAGE_RECEIPT_INVENTORY_'+str(time.time_ns())+'.json',v);print(json.dumps(v))
finally:cleanup(n,w)
