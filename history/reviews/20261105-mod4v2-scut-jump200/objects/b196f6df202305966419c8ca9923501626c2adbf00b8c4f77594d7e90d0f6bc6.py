"""Resume only an unconsumed formal return after the local sleeper vanished."""
from pathlib import Path
import json
import os
import time
import traceback
from shared_control_access import connection, load

N = Path(__file__).resolve().parent
A = N / 'takeoff_velocity_final239_1h'
R = A / 'reports'
read = lambda path: json.loads(Path(path).read_bytes())


def put(name, value):
    with (R / name).open('x', encoding='utf8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)


def main():
    for name in ['POSTROUND_FINITE_READ_ONCE.json', 'POSTROUND_FULL_RETURNED.json',
                 'POSTROUND_COMPLETED.json']:
        assert not (R / name).exists(), name
    assert (R / 'POSTROUND_STDOUT.log').stat().st_size == 0
    assert (R / 'POSTROUND_STDERR.log').stat().st_size == 0
    inventory = load('takeoff_recovery_local_inventory',
                     N.parent / 'mod4v1_scut_step270_2h_20261103/run.py')
    rows = inventory.local_rows()
    original = read(R / 'POSTROUND_EXACT_CIM.json')['row']
    assert not any(row['ProcessId'] == original['ProcessId'] for row in rows)
    # Only this chat's existing receiver would duplicate the missing read.
    # Other chats' inventory is informational under the human's instruction.
    for row in rows:
        if row['ProcessId'] == os.getpid():
            continue
        command = (row.get('CommandLine') or '').replace('\\', '/')
        assert not ('takeoff_velocity_control.py collect --root' in command
                    and str(A).replace('\\', '/') in command)
    go = read(R / 'FIRST_ACTUAL_RETURNED.json')['files']['GO_PRODUCTION.json']
    put('POSTROUND_LOCAL_SLEEPER_MISSING_RECOVERY_ONCE.json', dict(
        epoch=time.time(), pid=os.getpid(), original_exact=original,
        local_inventory=rows, original_process_absent=True,
        original_exit_cause='Unknown: empty stdout/stderr, no control error receipt',
        original_once_preserved=True, original_window_preserved=go,
        recovery_scope='Only missing read and artifact transfer after original SAVE+45',
        training_restarts=0, evaluation_restarts=0, budget_mutations=0))
    print(json.dumps(dict(recovery_pid=os.getpid(),
                          not_before=go['save_deadline'] + 45)), flush=True)
    while time.time() < go['save_deadline'] + 45:
        time.sleep(min(10, go['save_deadline'] + 45 - time.time()))
    receiver = load('takeoff_missing_receiver',
                    N.parent / 'mod4v1_scut_step270_2h_20261103/postround.py')
    receiver.A=A; receiver.R=R; receiver.put=put
    receiver.m.connection=lambda label: connection(R, label)
    receiver.receive(read(A/'PLAN.json')['remote_root'], 'TAKEOFF_POSTROUND_RECOVERY')


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        put('RECEIVER_RECOVERY_ERROR_' + str(time.time_ns()) + '.json',
            dict(epoch=time.time(), error=traceback.format_exc()))
        raise
