"""Actual Windows deny-delete reader releases; replacement must retry and succeed."""
from pathlib import Path
from tempfile import TemporaryDirectory
import ctypes,os,time,json,threading
from resilient_json_atomic import atomic

def main():
    assert os.name=='nt'
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.CreateFileW.argtypes=[ctypes.c_wchar_p,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p]
    kernel.CreateFileW.restype=ctypes.c_void_p;kernel.CloseHandle.argtypes=[ctypes.c_void_p];kernel.CloseHandle.restype=ctypes.c_int
    errors=[]
    with TemporaryDirectory() as folder:
        target=Path(folder)/'receipt.json';target.write_text('{"old":true}',encoding='utf8')
        handle=kernel.CreateFileW(str(target),0x80000000,0x1|0x2,None,3,0x80,None)
        assert handle!=ctypes.c_void_p(-1).value,ctypes.get_last_error()
        def release():time.sleep(.3);assert kernel.CloseHandle(handle)
        thread=threading.Thread(target=release);thread.start()
        def replace(src,dst):
            try:os.replace(src,dst)
            except OSError as e:errors.append(e.winerror);raise
        before=time.monotonic();atomic(target,{'new':True},replace=replace);elapsed=time.monotonic()-before
        thread.join();assert errors and all(e in (5,32,33) for e in errors)
        assert json.loads(target.read_text(encoding='utf8'))=={'new':True}
    print(json.dumps(dict(passed=True,actual_Windows_share_denial_errors=errors,elapsed_seconds=elapsed,actual_replacement_after_reader_release=True,only_temporary_fixture_files_written=True,no_GPU_PPO_production_or_canonical_mutation=True)))
if __name__=='__main__':main()
