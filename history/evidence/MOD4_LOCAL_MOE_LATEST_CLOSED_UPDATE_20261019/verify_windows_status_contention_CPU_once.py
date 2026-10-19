"""Reproduce a real Win32 deny-delete handle without starting another player."""
from pathlib import Path
import ctypes,json,sys,time,traceback
from ctypes import wintypes
B=Path(__file__).resolve().parent;D=B.parent/'MOD4_LOCAL_MUJOCO_DRIVE_20261008'
sys.path.insert(0,str(D))
from player_status_io import write_json

def main():
    root=B/'windows_status_contention_actual';root.mkdir()
    target=root/'INTERACTIVE_CURRENT.json'
    assert write_json(target,dict(sequence=0,complete=True))
    api=ctypes.WinDLL('kernel32',use_last_error=True)
    api.CreateFileW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE]
    api.CreateFileW.restype=wintypes.HANDLE
    api.CloseHandle.argtypes=[wintypes.HANDLE];api.CloseHandle.restype=wintypes.BOOL
    # Share READ/WRITE, deliberately omit FILE_SHARE_DELETE to reproduce replace failure.
    handle=api.CreateFileW(str(target),0x80000000,0x1|0x2,None,3,0x80,None)
    assert handle not in (None,ctypes.c_void_p(-1).value),ctypes.get_last_error()
    outcomes=[]
    try:
        for seq in range(1,4):
            began=time.perf_counter();ok=write_json(target,dict(sequence=seq,complete=True))
            outcomes.append(dict(sequence=seq,returned=ok,elapsed_seconds=time.perf_counter()-began))
            assert not ok and json.loads(target.read_text('utf8'))['sequence']==0
    finally:
        assert api.CloseHandle(handle)
    assert write_json(target,dict(sequence=4,complete=True))
    assert json.loads(target.read_text('utf8'))==dict(sequence=4,complete=True)
    warnings=[json.loads(x) for x in (root/'STATUS_WRITE_WARNINGS.jsonl').read_text('utf8').splitlines()]
    assert len(warnings)==3 and all(x['winerror'] in (5,32,33) and x['attempts']==4 for x in warnings)
    # Exceptions unrelated to status sharing still propagate, as before.
    unexpected_propagates=False
    try:write_json(root/'missing_parent/status.json',{})
    except FileNotFoundError:unexpected_propagates=True
    assert unexpected_propagates
    report=dict(epoch=time.time(),status='PASS',actual_Win32_deny_delete_handle=True,
        original_complete_JSON_retained_during_contention=True,blocked_writes=outcomes,
        recovered_on_next_snapshot_after_handle_close=True,unrelated_errors_still_propagate=True,
        warning_rows=warnings,physics_policy_or_training_changed=False)
    with (B/'reports/WINDOWS_STATUS_CONTENTION_REPRODUCTION_AND_FIX_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
    print(json.dumps({k:v for k,v in report.items() if k not in ('warning_rows',)}))
if __name__=='__main__':
    try:main()
    except BaseException:
        with (B/'reports'/('STATUS_CONTENTION_CHECK_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc()),f,indent=2)
        raise
