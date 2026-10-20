"""Wait for this new owner's actual post-listener publication, not just fork return."""
from pathlib import Path
import time,json
def validate_ready(root,pid,identity,current,actual,errors):
 root=Path(root);assert not errors and identity and current and actual
 assert identity['pid']==actual['pid']==pid and abs(identity['creation']-actual['creation'])<.01
 entry=str(root/'three_slot_finite_owner_v1.py');assert entry in identity['argv'] and entry in actual['argv']
 assert current['epoch']>=identity['creation'] and current['epoch']<=time.time()+60
 assert current['rows']=={'recovery':{}} and not current['go'] and not current['original_canonical_active'] and not current['original_two_fcntl_held']
 return dict(owner_identity=identity,actual_identity=actual,actual_listener_initialized_current_epoch=current['epoch'],post_listener_publication_before_registration=True,no_GO_no_budget_locks_yet=True)
def wait_actual(root,pid,timeout=20.):
 import psutil
 root=Path(root);start=time.monotonic()
 while time.monotonic()-start<timeout:
  errors=[str(root/name) for name in ('OWNER_ORIGINAL_ERROR.json','OWNER_EXIT_ACTUAL.json') if (root/name).exists()];assert not errors,errors
  paths=[root/'OWNER_IDENTITY.json',root/'OWNER_CURRENT.json']
  if all(p.is_file() for p in paths):
   identity,current=[json.loads(p.read_bytes()) for p in paths];p=psutil.Process(pid);assert p.status()!=psutil.STATUS_ZOMBIE;actual=dict(pid=p.pid,creation=p.create_time(),argv=p.cmdline(),root=p.cwd());return validate_ready(root,pid,identity,current,actual,errors)
  time.sleep(.05)
 raise TimeoutError('This owner has not published its actual post-listener current within20s')
