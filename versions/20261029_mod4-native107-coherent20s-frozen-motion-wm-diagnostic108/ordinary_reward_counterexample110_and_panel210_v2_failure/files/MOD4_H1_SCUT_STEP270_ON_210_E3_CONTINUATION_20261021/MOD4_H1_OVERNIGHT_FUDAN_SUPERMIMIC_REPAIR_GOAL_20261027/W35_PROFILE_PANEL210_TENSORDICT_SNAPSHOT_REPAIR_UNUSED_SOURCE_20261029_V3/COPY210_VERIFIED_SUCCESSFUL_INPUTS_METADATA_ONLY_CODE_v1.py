from pathlib import Path
import hashlib,json,os,time

old=Path(v['old']);new=Path(v['new']);expected=v['expected']
assert new.resolve().is_relative_to(Path('/mnt/mod4_linux_durable_20261013').resolve()) and new.is_dir() and not any(new.iterdir())

def digest(raw):return hashlib.sha256(raw).hexdigest()
def known_out(row):
    p=Path('/proc')/str(row['pid'])
    try:
        raw=(p/'stat').read_text();fields=raw[raw.rfind(')')+2:].split()
        boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '))
        created=boot+int(fields[19])/os.sysconf('SC_CLK_TCK')
    except FileNotFoundError:return True
    return created!=row['creation'] or fields[0]=='Z'

failure=expected['failed_panel_context'];failed_root=Path(failure['root']);failed_raw=(failed_root/'FROZEN_W35_ORIGINAL_WAITED_TERMINAL_ACTUAL.json').read_bytes()
assert digest(failed_raw)==failure['terminal_SHA'];failed=json.loads(failed_raw)
assert failed['actual_worker_waited'] and failed['returncode']==failure['original_returncode'] and failed['private_EX_released'] and not failed['passed_frozen_execution'] and failed['result'] is None
assert failed['supervisor']==failure['supervisor'] and failed['worker']==failure['worker']
assert known_out(failure['supervisor']) and known_out(failure['worker'])
preclose_raw=(failed_root/'frozen_regression/FROZEN_W35_ORIGINAL_EXCEPTION_BEFORE_APP_CLOSE.json').read_bytes();assert digest(preclose_raw)==failure['preclose_error_SHA'];preclose=json.loads(preclose_raw)
assert preclose['exception_type']=='TypeError' and 'Unsupported actual domain value at : TensorDict' in preclose['traceback']
terminal_raw=(old/'FROZEN_W35_ORIGINAL_WAITED_TERMINAL_ACTUAL.json').read_bytes()
assert digest(terminal_raw)==expected['terminal_SHA']
terminal=json.loads(terminal_raw)
assert terminal['actual_worker_waited'] and terminal['returncode']==0 and not terminal['deadline_terminated']
assert terminal['passed_frozen_execution'] and terminal['private_EX_released'] and terminal['original_error'] is None and terminal['original_worker_errors']==[]
assert terminal['supervisor']==expected['supervisor'] and terminal['worker']==expected['worker']
assert known_out(expected['supervisor']) and known_out(expected['worker'])
r=terminal['result']
assert r['passed_execution'] and r['controls']==1200 and not r['wall_time_limited'] and r['source_SHA']==expected['model_SHA']
assert r['all17_Adam_steps']==648360 and r['core_actor_critic_STD_norm_optimizer_literal_unchanged'] and r['no_optimizer_step_no_norm_update']
sdk_raw=(old/'ACTUAL_SOURCE210_SOURCE_SDK_CPU_NO_MODEL_ADMISSION.json').read_bytes()
assert digest(sdk_raw)==expected['source_SDK_SHA'] and json.loads(sdk_raw)['passed']
whole_raw=(old/'W35_EXISTING_FORMAL_WHOLE_CPU_WITNESS.json').read_bytes()
assert digest(whole_raw)==expected['wholeCPU_SHA']
whole=json.loads(whole_raw)
assert whole['passed'] and whole['model']['SHA']==expected['model_SHA'] and whole['model']['bytes']==expected['model_bytes']
assert whole['model']['original_producer']['Adam_step']==648360
records=[]
for row in v['rows']:
    rel=row['relative'];p=old/rel;q=new/rel
    assert p.resolve().is_relative_to(old.resolve()) and q.resolve().is_relative_to(new.resolve()) and not p.is_symlink()
    before=p.stat();assert before.st_size==row['bytes'] and not q.exists()
    q.parent.mkdir(parents=True,exist_ok=True)
    large=rel.endswith(('.pt','.npz')) or rel=='runtime/assets/source_700N/robot.usd'
    if large:os.link(p,q)
    else:
        raw=p.read_bytes();assert digest(raw)==row['SHA']
        with q.open('xb') as out:out.write(raw)
    after=p.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
    same=os.path.samestat(after,q.stat()) if large else False
    if large:assert same
    records.append(dict(relative=rel,bytes=row['bytes'],producer_SHA=row['SHA'],
                        source_mtime_ns=after.st_mtime_ns,large_readonly_input_same_inode=same,
                        no_large_content_read=large,old_bytes_unchanged=True))
print(json.dumps(dict(passed=True,epoch=time.time(),records=records,old_source_wholeCPU_and_closure_bound=True,
                     old_wholeCPU_SHA=expected['wholeCPU_SHA'],original_source_SDK_SHA=expected['source_SDK_SHA'],
                     old_supervisor_worker_out=True,only_manifest_inputs_no_Task_GO_or_outputs_copied=True,
                     no_model_NPZ_decode_or_large_binary_rehash=True,no_source_environment_or_physics_change=True)))
