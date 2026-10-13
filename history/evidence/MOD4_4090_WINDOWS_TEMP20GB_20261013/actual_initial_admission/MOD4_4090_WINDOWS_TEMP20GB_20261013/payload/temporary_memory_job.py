"""Windows kernel job commitment cap; no kill-on-close or termination API."""
import ctypes
from ctypes import wintypes as w
k=ctypes.WinDLL('kernel32',use_last_error=True)
class Basic(ctypes.Structure):
 _fields_=[('PerProcessUserTimeLimit',ctypes.c_longlong),('PerJobUserTimeLimit',ctypes.c_longlong),('LimitFlags',w.DWORD),('MinimumWorkingSetSize',ctypes.c_size_t),('MaximumWorkingSetSize',ctypes.c_size_t),('ActiveProcessLimit',w.DWORD),('Affinity',ctypes.c_size_t),('PriorityClass',w.DWORD),('SchedulingClass',w.DWORD)]
class IO(ctypes.Structure):_fields_=[(n,ctypes.c_ulonglong) for n in ('ReadOperationCount','WriteOperationCount','OtherOperationCount','ReadTransferCount','WriteTransferCount','OtherTransferCount')]
class Extended(ctypes.Structure):_fields_=[('BasicLimitInformation',Basic),('IoInfo',IO),('ProcessMemoryLimit',ctypes.c_size_t),('JobMemoryLimit',ctypes.c_size_t),('PeakProcessMemoryUsed',ctypes.c_size_t),('PeakJobMemoryUsed',ctypes.c_size_t)]
k.CreateJobObjectW.restype=w.HANDLE;k.CreateJobObjectW.argtypes=[ctypes.c_void_p,w.LPCWSTR]
k.SetInformationJobObject.argtypes=[w.HANDLE,ctypes.c_int,ctypes.c_void_p,w.DWORD];k.SetInformationJobObject.restype=w.BOOL
k.AssignProcessToJobObject.argtypes=[w.HANDLE,w.HANDLE];k.AssignProcessToJobObject.restype=w.BOOL
k.QueryInformationJobObject.argtypes=[w.HANDLE,ctypes.c_int,ctypes.c_void_p,w.DWORD,ctypes.c_void_p];k.QueryInformationJobObject.restype=w.BOOL
k.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];k.OpenProcess.restype=w.HANDLE
k.CloseHandle.argtypes=[w.HANDLE];k.CloseHandle.restype=w.BOOL
def require(ok):
 if not ok:raise ctypes.WinError(ctypes.get_last_error())
class MemoryJob:
 def __init__(self,limit):
  self.limit=limit;self.h=k.CreateJobObjectW(None,None);require(self.h)
  self.cfg=Extended();self.cfg.BasicLimitInformation.LimitFlags=0x200;self.cfg.JobMemoryLimit=limit
  require(k.SetInformationJobObject(self.h,9,ctypes.byref(self.cfg),ctypes.sizeof(self.cfg)))
 def assign(self,pid):
  p=k.OpenProcess(0x0100|0x0001,False,pid);require(p)
  try:require(k.AssignProcessToJobObject(self.h,p))
  finally:k.CloseHandle(p)
 def peak(self):
  info=Extended();require(k.QueryInformationJobObject(self.h,9,ctypes.byref(info),ctypes.sizeof(info),None))
  return int(info.PeakJobMemoryUsed)
 def close(self):require(k.CloseHandle(self.h))
