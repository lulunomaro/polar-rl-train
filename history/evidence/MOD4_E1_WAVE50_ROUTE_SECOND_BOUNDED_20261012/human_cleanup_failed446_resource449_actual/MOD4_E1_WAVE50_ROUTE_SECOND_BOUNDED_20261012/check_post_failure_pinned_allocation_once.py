from route_second_io import *

def main():
    assert not (R/'POST_FAILURE_PINNED_ALLOCATION_ACTUAL.json').exists()
    n,w=io.connect_both()
    try:
        v=run(n,r'''import json,time,ctypes,resource,subprocess,fcntl,hashlib
from pathlib import Path
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');before=B.read_bytes();assert json.loads(before)['active_segment'] is None
for pid in (3340858,3340979,3340947):assert not Path('/proc',str(pid)).exists()
apps=subprocess.run(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True).stdout.strip();assert not apps
fds=[]
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 f=p.open('r');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fds.append(f)
lib=ctypes.CDLL('libcuda.so.1');lib.cuInit.argtypes=[ctypes.c_uint];lib.cuDeviceGet.argtypes=[ctypes.POINTER(ctypes.c_int),ctypes.c_int];lib.cuDevicePrimaryCtxRetain.argtypes=[ctypes.POINTER(ctypes.c_void_p),ctypes.c_int];lib.cuCtxSetCurrent.argtypes=[ctypes.c_void_p];lib.cuMemHostAlloc.argtypes=[ctypes.POINTER(ctypes.c_void_p),ctypes.c_size_t,ctypes.c_uint];lib.cuMemFreeHost.argtypes=[ctypes.c_void_p];lib.cuDevicePrimaryCtxRelease.argtypes=[ctypes.c_int];lib.cuGetErrorName.argtypes=[ctypes.c_int,ctypes.POINTER(ctypes.c_char_p)]
def name(rc):
 p=ctypes.c_char_p();lib.cuGetErrorName(rc,ctypes.byref(p));return p.value.decode() if p.value else 'unknown'
assert lib.cuInit(0)==0;dev=ctypes.c_int();assert lib.cuDeviceGet(ctypes.byref(dev),0)==0;ctx=ctypes.c_void_p();assert lib.cuDevicePrimaryCtxRetain(ctypes.byref(ctx),dev.value)==0;assert lib.cuCtxSetCurrent(ctx)==0
rows=[];allocated=[]
try:
 for size in (658725376,337280000):
  p=ctypes.c_void_p();rc=lib.cuMemHostAlloc(ctypes.byref(p),size,2);rows.append(dict(bytes=size,flags=2,rc=rc,error_name=name(rc),succeeded=rc==0))
  if rc==0:allocated.append(p)
finally:
 for p in allocated:assert lib.cuMemFreeHost(p)==0
 assert lib.cuDevicePrimaryCtxRelease(dev.value)==0
assert B.read_bytes()==before
v=dict(epoch=time.time(),passed=all(x['succeeded'] for x in rows),allocations=rows,memlock_limit=resource.getrlimit(resource.RLIMIT_MEMLOCK),meminfo=Path('/proc/meminfo').read_text(),original_scene_failure_not_reproduced_by_empty_context_sizes=True,no_PhysX_simulation_or_asset_load=True,no_control_no_PPO_no_budget_write=True,no_OS_or_resource_limit_change=True,primary_docs=['https://docs.nvidia.com/cuda/cuda-driver-api/cuda_driver_api/group__CUDA__MEM.html','https://nvidia-omniverse.github.io/PhysX/physx/5.5.1/_api_build/program_listing_file_include_foundation_PxPinnedArray.h.html'],only_host_allocation_API_component_not_formal_startup_admission=True)
out=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012/reports/POST_FAILURE_PINNED_ALLOCATION_ACTUAL.json');assert not out.exists();out.write_text(json.dumps(v,indent=2));print(json.dumps(v))
''')
        save('POST_FAILURE_PINNED_ALLOCATION_ACTUAL.json',v);print(json.dumps(dict(passed=v['passed'],allocations=v['allocations'],memlock=v['memlock_limit'],no_PPO=True)))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('PINNED_RESOURCE_COMPONENT_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_old_PhysX_or_PPO_replay=True,unknown_outcome_read_remote_before_retry=True));raise
