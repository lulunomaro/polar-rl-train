"""Build only new local source/metadata; no asset or model bytes are opened."""
from pathlib import Path
import hashlib
import json
import time
import traceback

A = Path(__file__).resolve().parent
N = A.parent
T = N.parent
P214 = T/'W35_FULL_RM70_MATERIAL_LIMIT_REPAIR_SOURCE_V214_20261101'
P219 = T/'W35_SOLO_INSTALL_FIRST_AND_CLOSED_READERS_SOURCE_V219_20261101'
P210 = T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031'


def ref(p):
    p = Path(p)
    assert p.suffix in ('.py', '.json', '.md')
    b = p.read_bytes()
    return dict(local_path=str(p), bytes=len(b), SHA=hashlib.sha256(b).hexdigest())


def write(p, data):
    with p.open('xb') as f:
        f.write(data)


def put(p, value):
    write(p, json.dumps(value, indent=2, allow_nan=False).encode())


def main():
    (A/'reports').mkdir(exist_ok=True)
    (A/'control227').mkdir(exist_ok=False)
    changes = []
    source = P214/'source/worker_full214.py'
    assert ref(source)['SHA'] == '3abbbbd66351380e2b287d8490cac73cfbc5dd27681c1b2d008085a88c082170'
    text = source.read_text(encoding='utf8')
    def change(old, new, count=1):
        nonlocal text
        assert text.count(old) == count, (old, text.count(old), count)
        text = text.replace(old, new)
        changes.append(dict(old=old, new=new, occurrences=count))
    change("SHA='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f'",
           "SHA='343e0fd8f4950ffea2b09808a3bf88d9dd68e14b06f84c7bdaad462dbc8a51bd'")
    change('BYTES=17619013; ADAM=648360; ITER=32336; LR=.00011390625000000003',
           'BYTES=17619269; ADAM=649720; ITER=32404; LR=.00017085937500000009')
    change("KIND='MOD4_W35_FULL_RM70_MATERIAL_SHARED214'", "KIND='MOD4_W35_FULL_RM70_QUALIFIED343E_CONTINUE227'")
    change("task['original_saved_W35_fullstate_CPU_proof_reused']", "task['selected219V3_fullstate_CPU_proof_reused']")
    change("source=job/'source/W35_ADAPTED92_FINAL78.pt'", "source=Path(task['model_path'])")
    change("assert cache.state['iter']==ITER", "assert cache.state['iter']==ITER and cache.state['actual_new_PPO_updates']==68\n    assert cache.state['typed_W35_RM70_task']['kind']=='MOD4_W35_FULL_RM70_MATERIAL_SHARED214'")
    change('new_original_CAD_RM70_course_assignment_query_reset=True,',
           'same_RM70_course_assignment_and_command_fullstate_restored=True,\n        new_physical_episode_and_query_cache_after_restore=True,source_prior_new_PPO_updates=68,')
    change("'--run_name','W35_ORIGINAL_RM70_FULL208_V3'", "'--run_name','W35_QUALIFIED343E_RM70_CONTINUE227'")
    change("run_name='owned_W35_RM70_v3_config'", "run_name='owned_W35_RM70_qualified227_config'")
    change("for name in required:assert read(receipts[name])['source_sha256']==SHA",
           "for name in required:assert read(receipts[name])['source_sha256']==SHA\n                terrain=read(receipts['E1_TERRAIN_RESUME_STARTUP_VERIFIED.json'])\n                assert terrain['original_terrain_restored_exact'] and terrain['one_new_physical_episode']")
    change('explicitly_new_RM70_course_assignment_query_reset=True)',
           'same_RM70_course_assignment_command_fullstate_restored=True)')
    change('old_G3_geometry_not_claimed_resumed=True,',
           'same_RM70_profile_terrain_assignment_and_command_restored=True,')
    # Existing receipt basenames remain the original node/reader ABI. Their
    # source_SHA and the new typed task unambiguously identify this new run.
    write(A/'worker_full227.py', text.encode())
    control = A/'control227'
    owner = (P219/'control219/solo219_finite_owner_authority72.py').read_text(encoding='utf8')
    assert owner.count('from solo218_protocol import validate_schedule,flat_go_fields') == 1
    owner = owner.replace('from solo218_protocol import validate_schedule,flat_go_fields',
                          'from solo227_protocol import validate_schedule,flat_go_fields')
    owner = owner.replace('Linux_W35_SHARED214_SOLO219_ONE_HOUR_', 'Linux_W35_QUALIFIED343E_SOLO227_ONE_HOUR_')
    write(control/'solo227_finite_owner_authority72.py', owner.encode())
    common = (P219/'control219/three_slot_common_v1.py').read_text(encoding='utf8')
    assert common.count('from solo218_protocol import valid_ready') == 1
    write(control/'three_slot_common_v1.py', common.replace('from solo218_protocol import valid_ready', 'from solo227_protocol import valid_ready').encode())
    node = (P219/'control219/solo219_fullstate_slot_node.py').read_text(encoding='utf8')
    assert node.count('ADMISSION218_READY.json') == 1
    write(control/'solo227_fullstate_slot_node.py', node.replace('ADMISSION218_READY.json', 'ADMISSION227_READY.json').encode())
    for name in ('contract227.py', 'solo227_protocol.py'):
        write(control/name, (A/name).read_bytes())
    write(control/'single_writer72_authority_V85M_source.py', (P219/'control219/single_writer72_authority_V85M_source.py').read_bytes())
    # Actual successful219V3 sender: do not reuse original219's rejected whitelist.
    sender = P210/'control_v2/forwarded_original_owner_control_v1.py'
    write(control/sender.name, sender.read_bytes())
    base = P219/'reports/INSTALL219_SOURCE_ROWS_FROZEN.json'
    rows = json.loads(base.read_bytes())['files']
    removed = {'contract218.py', 'worker_full214.py', 'worker_full218.py'}
    files = {r['relative']: r for r in rows if r['relative'] not in removed}
    for name in ('worker227.py', 'worker_full227.py', 'contract227.py'):
        files[name] = dict(relative=name, **ref(A/name))
    put(A/'reports/INSTALL227_SOURCE_ROWS_FROZEN.json', dict(schema='mod4.227.install.v1',
        status='SOURCE_MAP_ONLY_ROOT_INSTALLER_NOT_EXECUTED', base_install_ref=ref(base),
        removed_inactive_entrypoints=sorted(removed), files=[files[k] for k in sorted(files)],
        source_model_metadata=dict(path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_SHARED214_SOLO219_1793475223790058200/w35_72/production/model_final_complete.pt',
            bytes=17619269, SHA='343e0fd8f4950ffea2b09808a3bf88d9dd68e14b06f84c7bdaad462dbc8a51bd',
            not_copied_or_rehashed_by_installer=True, GPU_worker_byte_open=1, GPU_worker_decode=1),
        runtime_reward_command_physics_DR_native24_unchanged=True,
        asset_PT_NPZ_USD_raw_reads=0))
    put(A/'reports/DERIVE227_SOURCE_CHANGES.json', dict(epoch=time.time(), source=ref(source),
        worker=ref(A/'worker_full227.py'), exact_replacements=changes,
        controls=[dict(relative=p.name, **ref(p)) for p in sorted(control.glob('*.py'))],
        owner_HMAC_twofcntl_charge_budget_caps_stop_save_close_wait_terminal_ACK_unchanged=True,
        actual210v2_sender_byte_reused=True, no_remote_execution=True))


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        (A/'reports').mkdir(exist_ok=True)
        put(A/'reports/DERIVE227_ORIGINAL_ERROR.json', dict(error=traceback.format_exc(), no_automatic_retry=True))
        raise
