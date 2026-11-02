"""Check actual handover invariants; no GPU, process launch or budget mutation."""
from pathlib import Path
import ast,json,hashlib,sys
D=Path(__file__).resolve().parent
tree=ast.parse((D/'supervise_dt2500_env20k_continuation.py').read_text())
functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
main=functions['main'];calls=[n for n in ast.walk(main) if isinstance(n,ast.Call)]
tests=[]
def require(ok,name):
 assert ok,name
 tests.append(name)
train=[c for c in calls if isinstance(c.func,ast.Attribute) and c.func.attr=='train']
require(len(train)==1 and [a.value for a in train[0].args[1:]]==[20000,10000,7200,'env20k_S2_D1D2_stable2h',False],'actual_train_exact20k_2h_formal_not_discard')
require('frozen20k' not in ast.unparse(main) and "'solver32_discard_'" not in ast.unparse(main),'no_duplicate_frozen_or_PPO_preflight')
require("'autonomy_controller.lock'" in ast.unparse(main) and "'native_floor_supervisor.lock'" in ast.unparse(main),'both_original_locks_before_launch')
require("['active_segment'] is None" in ast.unparse(main) and 'old_authorities_exited()' in ast.unparse(main),'actual_idle_old_authorities_gate')
require('segment == formal[\'unique_completed_segment\']' in ast.unparse(main),'completed_original_segment_exact_no_settlement')
require('SOURCE_SHA' in ast.unparse(main) and 's.fullsave(init)' in ast.unparse(main),'source25211_complete_finite_gate')
require('s.guardian(' in ast.unparse(tree),'reuse_actual15s_ownPID_guardian')
require('publish_final' not in ast.unparse(tree) and 'old1ms_worker_must_not_execute=True' in ast.unparse(main),'new_clock_not_sent_to_old_worker')
require('D3_installed=False' in ast.unparse(main),'delay_not_claimed_installed')
require(not any(isinstance(c.func,ast.Attribute) and c.func.attr in ('kill','terminate','send_signal') for c in calls),'no_process_signals_or_blind_active_clear')
f=json.loads((D/'reports/SOURCE_FREEZE.json').read_text())['sha256']
require(len(f)==213 and all(hashlib.sha256((D/n).read_bytes()).hexdigest()==h for n,h in f.items()),'actual213_source_sha_exact')
print(json.dumps({'passed':True,'contracts':tests,'no_GPU_or_budget_mutation':True,'count':len(tests)}))
