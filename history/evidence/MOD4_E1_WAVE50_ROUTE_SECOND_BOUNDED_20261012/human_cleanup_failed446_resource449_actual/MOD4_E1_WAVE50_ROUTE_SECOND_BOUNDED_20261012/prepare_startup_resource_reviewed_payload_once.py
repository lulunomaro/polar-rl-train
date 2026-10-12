from route_second_io import *
import ast

def main():
    dest=D/'resource_reviewed_payload';assert not dest.exists();dest.mkdir()
    raw=(D/'payload/isaac/mod4/train_wave50_route_same_scope_resume_ppo.py').read_text()
    assert raw.count('def main() -> None:')==1 and raw.count('        bounded_learn(runner, n_iter, log_dir)')==1
    raw=raw.replace('def main() -> None:', '_OWN_PPO_LEARN_STARTED = False\n\ndef main() -> None:\n    global _OWN_PPO_LEARN_STARTED')
    raw=raw.replace('        bounded_learn(runner, n_iter, log_dir)', '        _OWN_PPO_LEARN_STARTED = True\n        bounded_learn(runner, n_iter, log_dir)')
    needle='        print(traceback.format_exc(), flush=True)\n\n        raise'
    assert needle in raw
    raw=raw.replace(needle,'''        print(traceback.format_exc(), flush=True)
        if not _OWN_PPO_LEARN_STARTED:
            # A failed initialization has no PPO updates to save. Persist the
            # original traceback and return nonzero without hanging in Kit teardown.
            with crash.open('rb') as f:
                os.fsync(f.fileno())
            os._exit(1)

        raise''')
    p=dest/'isaac/mod4/train_wave50_route_startup_resource_reviewed_ppo.py';p.parent.mkdir(parents=True);compile(raw,str(p),'exec');p.write_text(raw,encoding='utf8')
    guard=(D/'resource_reviewed_source_guard_template.py').read_bytes();compile(guard,'guard','exec');(dest/'wave50_route_startup_resource_guard.py').write_bytes(guard)
    controller=(D/'resource_reviewed_controller_template.py').read_bytes();compile(controller,'controller','exec');(dest/'supervise_wave50_route_startup_resource_reviewed_once.py').write_bytes(controller)
    old=ast.parse((D/'payload/isaac/mod4/train_wave50_route_same_scope_resume_ppo.py').read_text());new=ast.parse(raw)
    excluded={'main'}
    a={n.name:ast.dump(n,include_attributes=False) for n in old.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name not in excluded}
    b={n.name:ast.dump(n,include_attributes=False) for n in new.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name not in excluded};assert a==b
    save('STARTUP_RESOURCE_REVIEWED_PAYLOAD_PREPARED.json',dict(epoch=time.time(),passed=True,source_count_expected=449,old446_allbytes_to_remain_exact=True,only_new_worker_prePPO_failure_exit_nonzero_without_Kit_teardown=True,normal_PPO_learn_save_exit_unchanged=True,all_restore_validator_functions_AST_exact=True,no_DR_physics_RNG_clock_geometry_entry_direction_route_change=True,component_only_not_target_or_GPU_startup_pass=True,newfiles={p.relative_to(dest).as_posix():H(p.read_bytes()) for p in dest.rglob('*') if p.is_file()}))
    print(json.dumps(dict(passed=True,newfiles=3,only_prePPO_failure_exit_and_resource_guard=True)))

if __name__=='__main__':
    try:main()
    except BaseException:save('RESOURCE_PAYLOAD_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),pre_target_pre_GPU=True));raise
