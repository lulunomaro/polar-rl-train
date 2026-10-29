"""V2 local identity uses native Windows API, not unavailable Python314 psutil.
V1 stopped before credentials/network; original error/marker remain intact.
"""
from pathlib import Path
import argparse,ctypes,json,os,sys,time,traceback
from ctypes import wintypes
HERE=Path(__file__).resolve().parent
old=(HERE/'collect_serial_and_publish_dashboard.py').read_text(encoding='utf8')
a="    import psutil\n    proc=psutil.Process();put('ONE_SERIAL_DASHBOARD_COLLECTOR_EXACT_LOCAL_IDENTITY_'+operation+'.json',dict(pid=proc.pid,creation=proc.create_time(),exe=proc.exe(),argv=proc.cmdline(),cwd=proc.cwd()))"
b="    put('ONE_SERIAL_DASHBOARD_COLLECTOR_EXACT_LOCAL_IDENTITY_'+operation+'.json',own_native_identity())"
assert old.count(a)==1
source=old.replace(a,b)
ns=dict(__name__='dashboard117_selected_v2',__file__=str(HERE/'collect_serial_and_publish_dashboard_v2.py'))
exec(compile(source,str(HERE/'collect_serial_and_publish_dashboard_v2.py'),'exec'),ns)
R=HERE/'reports/selected_v2';R.mkdir(exist_ok=True);ns['R']=R
def identity():
    k=ctypes.WinDLL('kernel32',use_last_error=True);k.GetCurrentProcess.restype=wintypes.HANDLE
    class FT(ctypes.Structure):_fields_=[('low',wintypes.DWORD),('high',wintypes.DWORD)]
    created=FT();exited=FT();kernel=FT();user=FT();k.GetProcessTimes.argtypes=[wintypes.HANDLE,*([ctypes.POINTER(FT)]*4)]
    assert k.GetProcessTimes(k.GetCurrentProcess(),ctypes.byref(created),ctypes.byref(exited),ctypes.byref(kernel),ctypes.byref(user))
    k.GetCommandLineW.restype=wintypes.LPWSTR;raw=k.GetCommandLineW()
    shell=ctypes.WinDLL('shell32');shell.CommandLineToArgvW.argtypes=[wintypes.LPCWSTR,ctypes.POINTER(ctypes.c_int)];shell.CommandLineToArgvW.restype=ctypes.POINTER(wintypes.LPWSTR)
    count=ctypes.c_int();array=shell.CommandLineToArgvW(raw,ctypes.byref(count));argv=[array[i] for i in range(count.value)]
    return dict(pid=os.getpid(),creation=((created.high<<32)+created.low-116444736000000000)/1e7,exe=sys.executable,argv=argv,cwd=os.getcwd(),identity_source='native GetProcessTimes + GetCommandLineW')
ns['own_native_identity']=identity
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--samples',type=int,default=3);p.add_argument('--period',type=float,default=30);p.add_argument('--refresh',action='store_true');a=p.parse_args()
    try:ns['main'](a.samples,a.period,a.refresh)
    except BaseException:ns['put']('V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_automatic_remote_task_relaunch=True));raise
