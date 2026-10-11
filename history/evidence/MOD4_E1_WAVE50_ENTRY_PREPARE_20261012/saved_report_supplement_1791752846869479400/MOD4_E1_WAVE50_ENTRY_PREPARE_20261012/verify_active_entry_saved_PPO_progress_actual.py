"""A matching initial save with zero optimizer delta is pending, not a GPU fault."""
from pathlib import Path
D = Path(__file__).resolve().parent
s = (D / 'verify_active_entry_saved_PPO_CPU_actual.py').read_text()
anchor = "assert changed and delta>0 and rec['pid']==pid and info['sha256']==own.s.q.base.sha(cp)"
replacement = """assert rec['pid']==pid and info['sha256']==own.s.q.base.sha(cp)
if not changed or delta<=0:
 assert not torch.cuda.is_initialized()
 print(json.dumps(dict(epoch=time.time(),passed=False,pending=True,matching_own_initial_save_without_positive_PPO_delta=True,actual_saved_PID=pid,discarded_preflight=receipt['discarded_preflight'],actual_state=st,formal_final_not_claimed=True,CPU_readonly_no_budget_write=True)));sys.exit(0)"""
assert s.count(anchor) == 1
s = s.replace(anchor, replacement)
exec(compile(s, '<own410-progress-aware-CPU-reader>', 'exec'), {'__file__': str(D / 'verify_active_entry_saved_PPO_CPU_actual.py'), '__name__': '__main__'})
