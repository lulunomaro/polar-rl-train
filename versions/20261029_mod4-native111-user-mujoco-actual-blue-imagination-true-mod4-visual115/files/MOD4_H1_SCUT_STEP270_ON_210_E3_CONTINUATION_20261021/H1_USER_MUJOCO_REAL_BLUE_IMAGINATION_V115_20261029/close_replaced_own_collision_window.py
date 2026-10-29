"""Graceful WM_CLOSE only to the exact previously launched owned display window.
Caller freshly verifies PID/executable/argv/creation with CIM before invoking.
"""
from pathlib import Path
import ctypes,json,time
from ctypes import wintypes
u=ctypes.WinDLL('user32',use_last_error=True)
u.GetWindowThreadProcessId.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.DWORD)]
u.GetWindowTextW.argtypes=[wintypes.HWND,wintypes.LPWSTR,ctypes.c_int]
u.PostMessageW.argtypes=[wintypes.HWND,wintypes.UINT,wintypes.WPARAM,wintypes.LPARAM]
found=[]
@ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
def visit(hwnd,lparam):
    pid=wintypes.DWORD();u.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
    if pid.value==72824:
        text=ctypes.create_unicode_buffer(512);u.GetWindowTextW(hwnd,text,512)
        if text.value.startswith('MOD4 | GRAY = recorded PhysX'):
            found.append(dict(hwnd=int(hwnd),pid=pid.value,title=text.value))
    return True
u.EnumWindows.argtypes=[type(visit),wintypes.LPARAM];u.EnumWindows(visit,0)
assert len(found)<=1
for row in found:assert u.PostMessageW(row['hwnd'],0x0010,0,0)
(Path(__file__).resolve().parent/'reports/OWN_COLLISION_WINDOW_GRACEFUL_REPLACEMENT.json').write_text(json.dumps(dict(epoch=time.time(),WM_CLOSE_only_own_returned_exact_title=found,no_kill=True),indent=2),encoding='utf8')
print(json.dumps(dict(graceful_close_requested=bool(found))))
