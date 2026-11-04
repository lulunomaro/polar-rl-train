"""Recover only the pre-network refused stair admission; old once stays intact."""
from pathlib import Path
import importlib.util
import inspect
import json
import time
import traceback

N=Path(__file__).resolve().parent
D=N/'env20000_target_axis_repair_1h_20261104/scut_stairs_eval1'
R=D/'reports'
spec=importlib.util.spec_from_file_location('scut_stair_original_diagnostic',N/'target_limits_control.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.D=D;m.R=R
assert not(R/'LAUNCH_ONCE.json').exists() and not(R/'ADMISSION.json').exists()
assert not(R/'PRELAUNCH_RECOVERY_ONCE.json').exists()
source=inspect.getsource(m.run)
needle="ready=c['active_segment']is None and e['all_own_waited']and e['original_cost_settled']and e['original_leases_released']"
wait=json.loads((D/'RESOURCE_WAIT.json').read_bytes())
additional="""
fixed_peer=Path(%r)
peer_started=json.loads((fixed_peer/'OWNER_STARTED.json').read_bytes())
assert peer_started['identity']['pid']==%r and peer_started['identity']['creation']==%r
exit_path=fixed_peer/'OWNER_EXIT.json'
peer_exit=json.loads(exit_path.read_bytes()) if exit_path.exists() else None
ready=ready and bool(peer_exit and peer_exit['all_own_waited'] and peer_exit['original_cost_settled'] and peer_exit['original_leases_released'])
"""%(wait['peer_root'],wait['peer_owner']['pid'],wait['peer_owner']['creation'])
assert source.count(needle)==1
source=source.replace(needle,needle+additional).replace("D/'INDEX.json'","D/'INDEX_REV2.json'")
old="label='TARGET_LIMIT_NATIVE01_RECOVERY' if recover else 'TARGET_LIMIT_NATIVE01'"
assert source.count(old)==1
source=source.replace(old,"label='SCUT_STAIRS_NATIVE03_VIEWER_PATH_FIX'")
try:
    scope=dict(vars(m));exec(compile(source,str(Path(__file__)),'exec'),scope);scope['run'](True)
except BaseException:
    m.put(R/('LOCAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc()))
    raise
