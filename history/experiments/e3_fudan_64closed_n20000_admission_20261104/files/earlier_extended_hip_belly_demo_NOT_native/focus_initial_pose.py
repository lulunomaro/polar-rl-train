"""Own-window UI operation only: new pose foreground, pause initial, close old demos."""
from pathlib import Path
import ctypes,json,time
from ctypes import wintypes as w
D=Path(__file__).resolve().parent;v=json.loads((D/'VIEWER_STARTED.json').read_bytes());u=ctypes.windll.user32;k=ctypes.windll.kernel32
u.GetForegroundWindow.restype=w.HWND;u.GetWindowThreadProcessId.argtypes=[w.HWND,ctypes.POINTER(w.DWORD)];u.IsWindowVisible.argtypes=[w.HWND];u.SetForegroundWindow.argtypes=[w.HWND];u.BringWindowToTop.argtypes=[w.HWND];u.ShowWindow.argtypes=[w.HWND,ctypes.c_int];u.PostMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM];u.GetWindowTextW.argtypes=[w.HWND,w.LPWSTR,ctypes.c_int]
def pid(h):p=w.DWORD();u.GetWindowThreadProcessId(h,ctypes.byref(p));return p.value
def title(h):b=ctypes.create_unicode_buffer(512);u.GetWindowTextW(h,b,512);return b.value
h=next(h for h in v['window_handles']if pid(h)==v['pid']and u.IsWindowVisible(h));fore=u.GetForegroundWindow();p=w.DWORD();ft=u.GetWindowThreadProcessId(fore,ctypes.byref(p));ct=k.GetCurrentThreadId();attached=bool(u.AttachThreadInput(ct,ft,True))if ft and ft!=ct else False
try:u.ShowWindow(h,9);u.BringWindowToTop(h);focused=bool(u.SetForegroundWindow(h))
finally:
 if attached:u.AttachThreadInput(ct,ft,False)
scan=u.MapVirtualKeyW(ord('S'),0);down=bool(u.PostMessageW(h,0x100,ord('S'),1|(scan<<16)));up=bool(u.PostMessageW(h,0x101,ord('S'),1|(scan<<16)|(1<<30)|(1<<31)));closed=[]
for path,name in((D.parent/'mod4v1_e3_full_leg_pose_view_20261104/VIEWER_STARTED.json','previous tilted whole-leg attempt'),(D.parent/'mod4v1_e3_stowed_startup_20261104/VIEWER_STARTED.json','previous wheel-tucked replay')):
 if not path.exists():continue
 x=json.loads(path.read_bytes());hs=x.get('window_handles',[])
 for oh in hs:
  if oh!=h and pid(oh)==x['pid']and u.IsWindowVisible(oh)and'E3'in title(oh):u.PostMessageW(oh,0x10,0,0);closed.append(dict(pid=x['pid'],hwnd=oh,which=name,action='WM_CLOSE to verified owned window only'))
report=dict(epoch=time.time(),new_pid=v['pid'],new_hwnd=h,visible=bool(u.IsWindowVisible(h)),foreground_request_returned=focused,foreground_actual=int(u.GetForegroundWindow()or 0),initial_pause_key_posted=down and up,old_owned_windows_close_requests=closed,no_foreign_process_signals=True);(D/'UI_OPERATION.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2))
