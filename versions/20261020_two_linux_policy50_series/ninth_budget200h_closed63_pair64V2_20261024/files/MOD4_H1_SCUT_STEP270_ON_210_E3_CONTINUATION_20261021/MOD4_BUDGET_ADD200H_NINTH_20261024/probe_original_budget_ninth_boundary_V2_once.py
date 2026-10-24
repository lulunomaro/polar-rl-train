from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from ninth_budget_ops import *
import traceback
try:
 put('PROBE_STARTED.json',dict(epoch=time.time()));q=closed();pw=secret();c=d.connect72(pw);pw=None
 try:r72=d.code(c,d.PY72,READ72,dict(closed=q),timeout=60)
 finally:c.close()
 c=d.t.connect()
 try:r210=d.code(c,d.t.PY,READ210,dict(closed=q),timeout=60)
 finally:c.close()
 put('ORIGINAL_BUDGET_NINTH_BEFORE_ACTUAL.json',dict(source210=r210,source72=r72))
 print(json.dumps(dict(passed=True,authorized=r210['authorized'],extensions=len(r210['extension_records']),remaining=r210['remaining'],twohost_allout=True)))
except BaseException:
 put('PROBE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc(),no_write=True));raise
