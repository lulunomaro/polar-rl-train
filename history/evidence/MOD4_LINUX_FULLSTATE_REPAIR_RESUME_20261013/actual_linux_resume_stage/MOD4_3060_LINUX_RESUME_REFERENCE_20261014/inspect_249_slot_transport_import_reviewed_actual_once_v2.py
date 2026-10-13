"""Independent preconnection transport import reviewed249 CPU continuation; no GPU/210."""
from pathlib import Path
import sys, os, json, time, importlib.util, traceback
P = Path(__file__).resolve().parent
W = P.parent
P.joinpath('reports').mkdir(exist_ok=True)
spec = importlib.util.spec_from_file_location('prior_guard_readonly', W / 'MOD4_3060_DIRECT_FACTOR_20261013/deploy_direct3060_baseline120_WDDM_guard_reviewed_once.py')
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
ROOT = 'D:/MOD4_async_eval/MOD4_LINUX_RESUME_REFERENCE_20261014'
q = P / 'reports/REFERENCE17B_249_INITIAL_SLOT_ACTUAL.json'
assert not q.exists()
sys.path.insert(0, str(W / 'RM2026_TERRAIN_AUDIT_20261009'))
from reuse_authorized_session_transport import recover
secret, _ = recover('MOD4_EVAL_SSH_PASSWORD'); assert secret
os.environ['MOD4_EVAL_SSH_PASSWORD'] = secret
sys.path.insert(0, str(W / 'MOD4_MOE_PLAN_EXECUTION_20261007'))
from eval_remote_io import connect_eval
c = None
try:
    c = connect_eval()
    result = g.py(c, g.GUARD.replace('ROOT', repr(ROOT)))
    result['only_target249_authorized'] = True
    result['no_GPU_launch_or_oldtask_replayed'] = True
    q.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps(dict(report=str(q), connected249=True, unused=result['new_root_unused'],
                          lock_free=result['shared_OS_lock_free'], GPU_free_MiB=result['GPU']['free_MiB'],
                          RAM_available=result['RAM_available'], Dfree=result['durable_D_free'],
                          oldworker_and_GPUchild_absent=result['oldworker_and_GPUchild_absence'])))
except Exception:
    p = P / ('reports/REFERENCE17B_INITIAL_SLOT_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json')
    p.write_text(json.dumps(dict(epoch=time.time(), traceback=traceback.format_exc(),
                                no_launch=True, only249=True), indent=2), encoding='utf8')
    raise
finally:
    if c: c.close()
    os.environ.pop('MOD4_EVAL_SSH_PASSWORD', None)
