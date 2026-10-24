from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from ninth_budget_ops import *
import traceback
REMOTE="from pathlib import Path\nimport fcntl,json,os,psutil,time\nroots=[Path(x) for x in v['roots']]\nassert not any(p.pid!=os.getpid() and any(any(a.startswith(str(root)+'/') for root in roots) for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))\nfor root in roots:\n assert not (root/'NODE_IDENTITY.json').exists() and not (root/'OWNER_IDENTITY.json').exists()\n if root.exists():assert not list(root.rglob('GO_PRODUCTION.json'))\nfor path in v['locks']:\n with Path(path).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)\nprint(json.dumps(dict(epoch=time.time(),all_failed64_processes_out=True,no_GO_no_owner_no_fee=True,roots=[dict(path=str(p),exists=p.exists()) for p in roots],original_locks_free=True,no_raw_PT_or_GPU_read=True)))\n"
try:
 put('FAILED64_PREOWNER_NO_GO_PROBE_STARTED.json',dict(epoch=time.time()));q=closed();pw=secret();c=d.connect72(pw);pw=None
 try:r72=d.code(c,d.PY72,REMOTE,dict(roots=['/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_reward_tuckclear4_2410v64/recovery'],locks=[q['specs']['recovery']['private_lock'],'/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock']),timeout=60)
 finally:c.close()
 c=d.t.connect()
 try:r210=d.code(c,d.t.PY,REMOTE,dict(roots=['/mnt/mod4_linux_durable_20261013/H1step270_reward_tuckclear4_2410v64/owner','/mnt/mod4_linux_durable_20261013/H1step270_reward_tuckclear4_2410v64/h1'],locks=[q['specs']['h1']['private_lock'],'/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock','/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock']),timeout=60)
 finally:c.close()
 put('FAILED64_INSTALLED_PREOWNER_NO_GO_TWOHOST_ALL_OUT_ACTUAL.json',dict(passed=True,source72=r72,source210=r210,no_budget_refund_or_recharge=True));print(json.dumps(dict(passed=True,no64_GO_no_fee=True,both_hosts_actual_out=True)))
except BaseException:
 put('FAILED64_OUT_PROBE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()));raise
