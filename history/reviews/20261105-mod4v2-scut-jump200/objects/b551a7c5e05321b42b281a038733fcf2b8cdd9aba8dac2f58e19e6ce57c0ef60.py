"""Recover only the unconsumed read/transfer blocked by a blanket local gate."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import subprocess
import time
import traceback
from shared_control_access import connection

N = Path(__file__).resolve().parent
A = N / 'continuation_final60_1h'
R = A / 'reports'
read = lambda path: json.loads(Path(path).read_bytes())


def put(name, value):
    with (R / name).open('x', encoding='utf8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)


def main():
    assert not (R / 'POSTROUND_FINITE_READ_ONCE.json').exists()
    assert not (R / 'POSTROUND_FULL_RETURNED.json').exists()
    assert not (R / 'POSTROUND_COMPLETED.json').exists()
    expected = read(R / 'POSTROUND_EXACT_CIM.json')['row']
    query = 'Get-CimInstance Win32_Process -Filter "ProcessId = '+str(expected['ProcessId'])+'" | Select-Object ProcessId,ParentProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json'
    result = subprocess.run(['pwsh', '-NoProfile', '-Command', query], capture_output=True, text=True, encoding='utf8', check=True)
    actual = json.loads(result.stdout)
    assert actual == expected, (actual, expected)
    assert (R / 'POSTROUND_STDOUT.log').stat().st_size == 0
    assert (R / 'POSTROUND_STDERR.log').stat().st_size == 0
    put('LOCAL_SERIAL_WAIT_REMOVAL.json', dict(
        epoch=time.time(), human='不用等控制器释放，账本共用，直接开训别浪费时间',
        original_exact_local=actual, only_missing_network_read_transfer=True,
        old_once_preserved=True, production_or_evaluation_replayed=False,
        original_controller_source_SHA=hashlib.sha256((N/'continuation_control.py').read_bytes()).hexdigest()))
    # This exact process is our local sleeper; the native owner already controls
    # its own immutable save/exit/evaluation boundary. No remote stop is sent.
    subprocess.run(['pwsh', '-NoProfile', '-Command', 'Stop-Process -Id '+str(expected['ProcessId'])+' -ErrorAction Stop'], check=True)
    query = 'Get-CimInstance Win32_Process -Filter "ProcessId = '+str(expected['ProcessId'])+'" | ConvertTo-Json'
    gone = subprocess.run(['pwsh', '-NoProfile', '-Command', query], capture_output=True, text=True, encoding='utf8', check=True)
    assert not gone.stdout.strip()
    put('LOCAL_SLEEPER_RETIRED.json', dict(epoch=time.time(), exact_process=actual, remote_operations=0))
    put('SHARED_POSTROUND_RECEIVER_ONCE.json', dict(epoch=time.time(), pid=os.getpid()))
    spec = importlib.util.spec_from_file_location('v2_shared_postround_receiver', N.parent/'mod4v1_scut_step270_2h_20261103/postround.py')
    receiver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(receiver)
    receiver.A=A; receiver.R=R; receiver.put=put
    receiver.m.connection=lambda label: connection(R, label)
    receiver.receive(read(A/'PLAN.json')['remote_root'], 'MOD4V2_SHARED_POSTROUND_RETURN')


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        put('SHARED_RECEIVER_ERROR_'+str(time.time_ns())+'.json', dict(epoch=time.time(), error=traceback.format_exc()))
        raise
