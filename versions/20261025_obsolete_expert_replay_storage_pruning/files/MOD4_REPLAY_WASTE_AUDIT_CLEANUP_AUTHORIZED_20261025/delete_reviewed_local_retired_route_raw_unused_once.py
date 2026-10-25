"""Remove exact obsolete local route raw files through exclusive verified handles."""
from pathlib import Path
import ctypes,ctypes.wintypes as wt,hashlib,json,os,re,shutil,time,traceback
S=Path(__file__).resolve().parent;W=S.parent;R=S/'reports';OUT=R/'local_unlink_actions'
INTENT=R/'EXACT_LOCAL_ROUTE_RAW_DELETE_INTENT_ACTUAL.json';DONE=R/'EXACT_LOCAL_ROUTE_RAW_DELETE_COMPLETE_ACTUAL.json'
assert not INTENT.exists() and not DONE.exists() and not OUT.exists()
k=ctypes.WinDLL('kernel32',use_last_error=True);INVALID=ctypes.c_void_p(-1).value
k.CreateFileW.argtypes=[wt.LPCWSTR,wt.DWORD,wt.DWORD,ctypes.c_void_p,wt.DWORD,wt.DWORD,wt.HANDLE];k.CreateFileW.restype=wt.HANDLE
k.CloseHandle.argtypes=[wt.HANDLE];k.CloseHandle.restype=wt.BOOL
k.GetFileAttributesW.argtypes=[wt.LPCWSTR];k.GetFileAttributesW.restype=wt.DWORD
class INFO(ctypes.Structure):
    _fields_=[('attributes',wt.DWORD),('creation',wt.FILETIME),('last_access',wt.FILETIME),('last_write',wt.FILETIME),('volume',wt.DWORD),('size_high',wt.DWORD),('size_low',wt.DWORD),('links',wt.DWORD),('index_high',wt.DWORD),('index_low',wt.DWORD)]
class DISPOSITION(ctypes.Structure):_fields_=[('DeleteFile',wt.BOOL)]
k.GetFileInformationByHandle.argtypes=[wt.HANDLE,ctypes.POINTER(INFO)];k.GetFileInformationByHandle.restype=wt.BOOL
k.SetFileInformationByHandle.argtypes=[wt.HANDLE,ctypes.c_int,ctypes.c_void_p,wt.DWORD];k.SetFileInformationByHandle.restype=wt.BOOL
def info(h):
    a=INFO();assert k.GetFileInformationByHandle(h,ctypes.byref(a)),ctypes.WinError(ctypes.get_last_error())
    return dict(attributes=int(a.attributes),device=int(a.volume),file_id=(int(a.index_high)<<32)|a.index_low,bytes=(int(a.size_high)<<32)|a.size_low,nlink=int(a.links),mtime_filetime=(int(a.last_write.dwHighDateTime)<<32)|a.last_write.dwLowDateTime)
def boundary(p):
    p=p.absolute();assert p.resolve(strict=True)==p and p.is_relative_to(W) and not p.is_relative_to(W/'polar-rl-train')
    current=W
    for part in p.relative_to(W).parts:
        current=current/part;a=k.GetFileAttributesW(str(current));assert a!=0xffffffff and not a&0x400
    assert p.name=='route_raw.npz' or re.fullmatch(r'(control|retention)_prefix_[0-9_]+\.npz',p.name) or p.name in ('S4_FIRST_TRAINED_GATE_FROZEN35_V1.zip','S5_NOMINAL_COMPLETE_ISOLATED_ABC_V1.zip')
def put(p,v):
    raw=json.dumps(v,ensure_ascii=False,indent=2).encode()
    with p.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    return hashlib.sha256(raw).hexdigest()
try:
    plan=json.loads((R/'ROOT_REVIEWED_EXACT_REPLAY_PRUNE_PLAN_ACTUAL.json').read_bytes());rows=plan['local']['delete']
    assert plan['human_lower_threshold']=='删除门槛要降低一些，不要什么都留着占用大量地方'
    selected=[]
    for row in rows:
        p=Path(row['path']);boundary(p);s=p.stat();assert (s.st_size,s.st_mtime_ns)==(row['bytes'],row['mtime_ns'])
        h=k.CreateFileW(str(p),0x80,7,None,3,0x00200000,None);assert h!=INVALID,ctypes.WinError(ctypes.get_last_error())
        try:a=info(h);assert a['nlink']==1 and not a['attributes']&(0x400|0x10);selected.append(dict(row,win32_identity=a))
        finally:k.CloseHandle(h)
    before=shutil.disk_usage('C:/').free;OUT.mkdir()
    intent_sha=put(INTENT,dict(epoch=time.time(),source_plan=str(R/'ROOT_REVIEWED_EXACT_REPLAY_PRUNE_PLAN_ACTUAL.json'),selected=selected,all_reports_models_native_query_small_fixtures_retained=True,old_unused_route_raw_loss_authorized=True,C_free_before=before))
    actions=[]
    for n,row in enumerate(selected):
        p=Path(row['path']);h=None;a=dict(sequence=n,path=str(p),bytes=row['bytes'],intent_SHA=intent_sha,deleted=False)
        try:
            boundary(p);h=k.CreateFileW(str(p),0x80000000|0x10000,0,None,3,0x00200000,None)
            assert h!=INVALID,ctypes.WinError(ctypes.get_last_error());fresh=info(h);assert fresh==row['win32_identity'];a['exclusive_verified_identity']=fresh
            mark=DISPOSITION(True);assert k.SetFileInformationByHandle(h,4,ctypes.byref(mark),ctypes.sizeof(mark)),ctypes.WinError(ctypes.get_last_error())
            a['marked_delete_by_exact_handle']=True
        except Exception:a['error']=traceback.format_exc()
        finally:
            if h not in (None,INVALID):k.CloseHandle(h)
        a['absent_after']=not p.exists();a['deleted']=bool(a.get('marked_delete_by_exact_handle') and a['absent_after']);put(OUT/('ACTION_'+str(n).zfill(4)+'_ACTUAL.json'),a);actions.append(a)
    after=shutil.disk_usage('C:/').free
    result=dict(epoch=time.time(),passed=all(x['deleted'] for x in actions),actions=actions,deleted_count=sum(x['deleted'] for x in actions),deleted_logical_bytes=sum(x['bytes'] for x in actions if x['deleted']),C_free_before=before,C_free_after=after,C_snapshot_increase=after-before,whole_filesystem_snapshot_not_exclusive_causal_reclaim=True,no_raw_hash_model_load_or_GPU=True)
    put(DONE,result);print(json.dumps({k:v for k,v in result.items() if k!='actions'}))
except BaseException:
    put(R/('LOCAL_REPLAY_UNLINK_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_old_once_rerun=True));raise
