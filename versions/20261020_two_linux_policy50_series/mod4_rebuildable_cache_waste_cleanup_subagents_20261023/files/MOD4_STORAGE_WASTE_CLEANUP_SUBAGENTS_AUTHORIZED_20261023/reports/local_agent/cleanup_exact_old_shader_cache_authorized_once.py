from pathlib import Path
import os, json, time, hashlib, shutil, ctypes, ctypes.wintypes as wt

OUT=Path(__file__).resolve().parent
INTENT=OUT/'EXACT_OLD_SHADER_CACHE_BEFORE_ANY_DELETE_INTENT_ACTUAL.json'
DONE=OUT/'EXACT_OLD_SHADER_CACHE_COMPLETE_ACTUAL.json'
ACTIONS=OUT/'shader_action_receipts'
assert not INTENT.exists() and not DONE.exists(), 'consumed intent/completion: do not rerun'
ROOTS=[Path(r'C:/Users/lulu/AppData/Local/NVIDIA/DXCache'),Path(r'C:/Users/lulu/AppData/Local/NVIDIA/GLCache'),Path(r'C:/Users/lulu/AppData/Local/D3DSCache')]
START=time.time(); CUTOFF=START-7*86400
GENERIC_READ=0x80000000; DELETE=0x00010000; FILE_READ_ATTRIBUTES=0x80
OPEN_EXISTING=3; FILE_FLAG_OPEN_REPARSE_POINT=0x00200000; REPARSE=0x400; DIRECTORY=0x10
INVALID=ctypes.c_void_p(-1).value
k=ctypes.WinDLL('kernel32',use_last_error=True)
k.CreateFileW.argtypes=[wt.LPCWSTR,wt.DWORD,wt.DWORD,ctypes.c_void_p,wt.DWORD,wt.DWORD,wt.HANDLE];k.CreateFileW.restype=wt.HANDLE
k.CloseHandle.argtypes=[wt.HANDLE];k.CloseHandle.restype=wt.BOOL
k.GetFileAttributesW.argtypes=[wt.LPCWSTR];k.GetFileAttributesW.restype=wt.DWORD
class BY_HANDLE_FILE_INFORMATION(ctypes.Structure):
    _fields_=[('attributes',wt.DWORD),('creation',wt.FILETIME),('last_access',wt.FILETIME),('last_write',wt.FILETIME),('volume',wt.DWORD),('size_high',wt.DWORD),('size_low',wt.DWORD),('links',wt.DWORD),('index_high',wt.DWORD),('index_low',wt.DWORD)]
class FILE_DISPOSITION_INFO(ctypes.Structure):
    _fields_=[('DeleteFile',wt.BOOL)]
k.GetFileInformationByHandle.argtypes=[wt.HANDLE,ctypes.POINTER(BY_HANDLE_FILE_INFORMATION)];k.GetFileInformationByHandle.restype=wt.BOOL
k.SetFileInformationByHandle.argtypes=[wt.HANDLE,ctypes.c_int,ctypes.c_void_p,wt.DWORD];k.SetFileInformationByHandle.restype=wt.BOOL
def winerr():
    e=ctypes.get_last_error();return {'winerror':e,'message':ctypes.FormatError(e)}
def stamp(ft):return (int(ft.dwHighDateTime)<<32)|int(ft.dwLowDateTime)
def info(h):
    f=BY_HANDLE_FILE_INFORMATION()
    if not k.GetFileInformationByHandle(h,ctypes.byref(f)):raise ctypes.WinError(ctypes.get_last_error())
    t=stamp(f.last_write)
    return {'file_attributes':int(f.attributes),'device_volume_serial':int(f.volume),'file_id':(int(f.index_high)<<32)|int(f.index_low),'bytes':(int(f.size_high)<<32)|int(f.size_low),'nlink':int(f.links),'mtime_filetime_100ns':t,'mtime_epoch':t/10_000_000-11644473600}
def norm(p):return os.path.normcase(os.path.abspath(p))
def boundary(p,root):
    assert p.is_absolute() and root.is_absolute()
    absolute=norm(p);base=norm(root)
    assert os.path.commonpath([absolute,base])==base and absolute!=base, 'outside exact cache root'
    # Neither the root nor any intervening parent may redirect to another location.
    current=root
    for part in (['']+list(p.relative_to(root).parts)):
        if part:current=current/part
        a=k.GetFileAttributesW(str(current))
        if a==0xFFFFFFFF:raise ctypes.WinError(ctypes.get_last_error())
        assert not (a&REPARSE),'reparse point rejected'
    resolved=norm(p.resolve(strict=True))
    assert resolved==absolute and os.path.commonpath([resolved,base])==base,'resolved path mismatch'
def write_exclusive(path,value):
    data=json.dumps(value,ensure_ascii=False,indent=2).encode('utf-8')
    with path.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    return hashlib.sha256(data).hexdigest()
selected=[]; retained_recent=[]; enumeration_errors=[]; rejected=[]
for root in ROOTS:
    if not root.is_dir():rejected.append({'path':str(root),'reason':'exact cache root missing'});continue
    stack=[root]
    while stack:
        folder=stack.pop()
        try:
            with os.scandir(folder) as it:entries=list(it)
        except OSError as e:enumeration_errors.append({'path':str(folder),'error':repr(e)});continue
        for ent in entries:
            p=Path(ent.path)
            h=None
            try:
                st=ent.stat(follow_symlinks=False)
                if ent.is_symlink() or getattr(st,'st_file_attributes',0)&REPARSE:
                    rejected.append({'path':str(p),'reason':'symlink/reparse'});continue
                if ent.is_dir(follow_symlinks=False):stack.append(p);continue
                if not ent.is_file(follow_symlinks=False):rejected.append({'path':str(p),'reason':'not regular file'});continue
                boundary(p,root)
                h=k.CreateFileW(str(p),FILE_READ_ATTRIBUTES,7,None,OPEN_EXISTING,FILE_FLAG_OPEN_REPARSE_POINT,None)
                if h==INVALID:raise ctypes.WinError(ctypes.get_last_error())
                data=info(h)
                if data['file_attributes']&(REPARSE|DIRECTORY):raise RuntimeError('handle is not ordinary cache file')
                row={'path':str(p),'exact_cache_root':str(root),**data}
                if data['mtime_epoch']<CUTOFF:selected.append(row)
                else:retained_recent.append(row)
            except Exception as e:enumeration_errors.append({'path':str(p),'error':repr(e)})
            finally:
                if h not in (None,INVALID):k.CloseHandle(h)
selected.sort(key=lambda r:r['path'].lower())
free_before=shutil.disk_usage('C:/').free
intent={'authorization':'2026-10-23 user requested this-turn agent cleanup; root explicitly delegated ONLY ordinary NVIDIA DXCache/GLCache/D3DSCache files last-modified >7 days. Root retains all other deletion leases.','scope':'Exact selected ordinary shader-cache files only; no root/directory deletion, no symlinks/reparse, no permissions changes, no process kill, no protected model/raw/PT/NPZ/source/log/report/credential/Git/host mutation. Only new cleanup receipts are written.','cache_removal_irrecoverable_but_compiled_shader_cache_rebuildable':True,'started_epoch':START,'cutoff_epoch_strictly_before':CUTOFF,'C_free_before_bytes':free_before,'selected_file_count':len(selected),'selected_logical_bytes':sum(r['bytes'] for r in selected),'selected':selected,'retained_recent_count':len(retained_recent),'retained_recent_logical_bytes':sum(r['bytes'] for r in retained_recent),'enumeration_errors':enumeration_errors,'rejected':rejected,'physical_reclaim_not_assumed_from_logical_bytes':True}
intent_sha=write_exclusive(INTENT,intent)
ACTIONS.mkdir(exist_ok=False)
summary=[]; compare_keys=['file_attributes','device_volume_serial','file_id','bytes','nlink','mtime_filetime_100ns']
for i,row in enumerate(selected):
    p=Path(row['path']);root=Path(row['exact_cache_root']);h=None
    action={'ordinal':i,'intent_SHA256':intent_sha,'intent_path':str(INTENT),'selected':row,'started_epoch':time.time(),'deleted':False,'skipped':False}
    marked=False
    try:
        boundary(p,root)
        # Zero sharing rejects any open readers/writers; DELETE only marks this verified handle.
        h=k.CreateFileW(str(p),GENERIC_READ|DELETE,0,None,OPEN_EXISTING,FILE_FLAG_OPEN_REPARSE_POINT,None)
        if h==INVALID:raise ctypes.WinError(ctypes.get_last_error())
        actual=info(h);action['exclusive_handle_before']=actual
        assert all(actual[x]==row[x] for x in compare_keys),'identity/size/mtime/attributes changed since intent'
        assert actual['mtime_epoch']<CUTOFF and not actual['file_attributes']&(REPARSE|DIRECTORY),'age/ordinary predicate no longer true'
        disposition=FILE_DISPOSITION_INFO(True)
        if not k.SetFileInformationByHandle(h,4,ctypes.byref(disposition),ctypes.sizeof(disposition)):raise ctypes.WinError(ctypes.get_last_error())
        marked=True;action['disposition_delete_by_verified_exclusive_handle']=True
    except Exception as e:
        action['skipped']=True;action['error']=repr(e)
    finally:
        if h not in (None,INVALID):
            action['handle_close_success']=bool(k.CloseHandle(h))
        action['ended_epoch']=time.time()
    action['path_absent_after_handle_close']=not p.exists()
    action['deleted']=bool(marked and action['path_absent_after_handle_close'])
    if marked and not action['deleted']:action['verification_error']='marked deletion but path remains; no retry/force'
    receipt=ACTIONS/f'ACTION_{i:06d}_ACTUAL.json'
    digest=write_exclusive(receipt,action)
    summary.append({'ordinal':i,'path':row['path'],'bytes':row['bytes'],'deleted':action['deleted'],'skipped':action['skipped'],'error':action.get('error'),'receipt':str(receipt),'receipt_SHA256':digest})
free_after=shutil.disk_usage('C:/').free
complete={'started_epoch':START,'ended_epoch':time.time(),'intent':str(INTENT),'intent_SHA256':intent_sha,'selected_files':len(selected),'deleted_files':sum(r['deleted'] for r in summary),'deleted_logical_bytes':sum(r['bytes'] for r in summary if r['deleted']),'skipped_files':sum(r['skipped'] for r in summary),'skipped_logical_bytes':sum(r['bytes'] for r in summary if r['skipped']),'C_free_before_bytes':free_before,'C_free_after_bytes':free_after,'C_free_difference_bytes':free_after-free_before,'free_difference_scope':'Whole-C-drive concurrent snapshot difference, not assumed byte-exact causal reclaim; per-action cache unlink receipts are separate.','retained_recent_files':len(retained_recent),'enumeration_errors':enumeration_errors,'rejected':rejected,'all_cache_roots_retained':all(r.is_dir() for r in ROOTS),'no_permissions_process_training_Git_or_protected_artifact_mutation':True,'actions':summary}
write_exclusive(DONE,complete)
print(json.dumps({k:complete[k] for k in ['deleted_files','deleted_logical_bytes','skipped_files','skipped_logical_bytes','C_free_before_bytes','C_free_after_bytes','C_free_difference_bytes','retained_recent_files','all_cache_roots_retained']}))
print(str(DONE))
