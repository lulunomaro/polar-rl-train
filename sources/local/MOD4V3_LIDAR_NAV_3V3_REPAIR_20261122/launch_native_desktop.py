"""Launch the requested GUI on the interactive Windows desktop, without a console."""
from nav_common import HERE,PYTHON,put
import ctypes
from ctypes import wintypes
import subprocess
import sys

class Startup(ctypes.Structure):
    _fields_=[('cb',wintypes.DWORD),('reserved',wintypes.LPWSTR),('desktop',wintypes.LPWSTR),('title',wintypes.LPWSTR),
        ('x',wintypes.DWORD),('y',wintypes.DWORD),('cx',wintypes.DWORD),('cy',wintypes.DWORD),
        ('charsx',wintypes.DWORD),('charsy',wintypes.DWORD),('fill',wintypes.DWORD),('flags',wintypes.DWORD),
        ('show',wintypes.WORD),('reserved2size',wintypes.WORD),('reserved2',ctypes.POINTER(ctypes.c_byte)),
        ('stdin',wintypes.HANDLE),('stdout',wintypes.HANDLE),('stderr',wintypes.HANDLE)]
class Process(ctypes.Structure):
    _fields_=[('process',wintypes.HANDLE),('thread',wintypes.HANDLE),('pid',wintypes.DWORD),('tid',wintypes.DWORD)]
startup=Startup();startup.cb=ctypes.sizeof(startup);startup.desktop='winsta0\\default'
process=Process();kernel=ctypes.WinDLL('kernel32',use_last_error=True)
kernel.CreateProcessW.argtypes=[wintypes.LPCWSTR,wintypes.LPWSTR,ctypes.c_void_p,ctypes.c_void_p,wintypes.BOOL,wintypes.DWORD,
                              ctypes.c_void_p,wintypes.LPCWSTR,ctypes.POINTER(Startup),ctypes.POINTER(Process)]
command=ctypes.create_unicode_buffer(subprocess.list2cmdline([str(PYTHON),'-B',str(HERE/'play_lidar_nav_wasd.py'),*sys.argv[1:]]))
if not kernel.CreateProcessW(str(PYTHON),command,None,None,False,0x08000200,None,str(HERE),ctypes.byref(startup),ctypes.byref(process)):
    raise ctypes.WinError(ctypes.get_last_error())
kernel.CloseHandle(process.thread);kernel.CloseHandle(process.process)
put(HERE/'evidence/NATIVE_DESKTOP_LAUNCH.json',dict(pid=process.pid,desktop=startup.desktop,console_hidden=True))
print(process.pid)
