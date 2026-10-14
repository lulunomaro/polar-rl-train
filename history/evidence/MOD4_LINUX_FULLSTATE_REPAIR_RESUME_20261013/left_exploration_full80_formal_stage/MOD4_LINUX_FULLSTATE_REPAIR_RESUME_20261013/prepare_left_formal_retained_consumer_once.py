"""New consumers for independently admitted postexit source, no remote action."""
from pathlib import Path
import ast,json,time,hashlib
D=Path(__file__).resolve().parent
s=(D/'left_exploration_worker_v2.py').read_text()
a="        controls=0 if os.environ['MOD4_LEFT_ADMISSION_MODE']=='fresh0PPO' else 144"
assert s.count(a)==1
s=s.replace(a,"        env=runner.env.unwrapped\n"+a)
p=D/'left_exploration_worker_v3.py';assert not p.exists();compile(s,str(p),'exec');p.write_text(s,encoding='utf8')
# Normal formal execution uses neither native nor fresh branch; production learn remains original.
old=ast.parse((D/'left_exploration_worker_v2.py').read_text());new=ast.parse(s)
old_if=next(n for n in old.body if isinstance(n,ast.If));new_if=next(n for n in new.body if isinstance(n,ast.If))
assert ast.dump(old_if.test)==ast.dump(new_if.test)
assert [ast.dump(n) for n in old.body if n is not old_if]==[ast.dump(n) for n in new.body if n is not new_if]
s=(D/'left_first_formal_typed_parent_v1.py').read_text().replace('left_exploration_worker_v2.py','left_exploration_worker_v3.py').replace('LEFT_FRESH_OWN_FULLSAVE0PPO_PASSED.json','LEFT_FRESH_RETAINED_INDEPENDENT_POSTEXIT_CPU_PASSED.json')
s=s.replace("    assert m['source_is_fresh_own0PPO_not_discardtrained']","    assert m['source_is_fresh_own0PPO_not_discardtrained']\n    assert m['fresh_original_parent_passed'] is False and m['fresh_independent_retained_save_passed'] is True")
# Do not allow app.close swallowing a worker exception to turn parent verdict into pass.
needle="        assert worker.returncode==0 and not fault,'Original full stdout and failure retained'"
assert needle in s
s=s.replace(needle,needle+"\n        assert b'Traceback (most recent call last)' not in log.read_bytes(),'Worker traceback retained; independent review required'")
p=D/'left_first_formal_retained_parent_v2.py';assert not p.exists();compile(s,str(p),'exec');p.write_text(s,encoding='utf8')
out=dict(epoch=time.time(),new_worker_zero_control_env_binding_before_loop=True,formal_original_learn_branch_AST_exact=True,original_v2_and_missing_completion_error_preserved=True,first_formal_seconds=3600,source_original_parent_fail_separate_independent_review_required=True,no_GPU_replay_or_dispatch=True,files=[dict(path=str(D/n),sha256=hashlib.sha256((D/n).read_bytes()).hexdigest()) for n in ('left_exploration_worker_v3.py','left_first_formal_retained_parent_v2.py')])
(D/'reports/LEFT_FORMAL_RETAINED_CONSUMERS_CPU_PREPARED.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps(out))
