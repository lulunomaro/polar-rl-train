"""Additional exact metadata only, root-dispatched. No process or content reads."""
from pathlib import Path
import json,os,stat,time,shutil
ROOT=Path('/home/lc01/Zonglin Li/zonglin2')
HOME=Path('/home/lc01')
start=time.monotonic();deadline=start+55
errors=[];groups=[]
def onerror(e):errors.append(dict(path=e.filename,error=repr(e),operation='walk'))
def meta(p):
    s=p.lstat()
    return dict(path=str(p),bytes=s.st_size,allocated_bytes=s.st_blocks*512,
       device=s.st_dev,inode=s.st_ino,nlink=s.st_nlink,uid=s.st_uid,gid=s.st_gid,
       mtime_ns=s.st_mtime_ns,mode=oct(stat.S_IMODE(s.st_mode)),
       regular=stat.S_ISREG(s.st_mode),symlink=stat.S_ISLNK(s.st_mode),directory=stat.S_ISDIR(s.st_mode))
assert ROOT.resolve(strict=True)==ROOT
exact=[ROOT/'downloads',ROOT/'cache',ROOT/'tmp',ROOT/'home',
       HOME/'.cache/pip',HOME/'.cache/uv',HOME/'.conda/pkgs',
       HOME/'miniconda3/pkgs',HOME/'anaconda3/pkgs',HOME/'miniforge3/pkgs']
for base in exact:
    if time.monotonic()>deadline:errors.append(dict(operation='global_deadline',path=str(base)));break
    group=dict(path=str(base),exists=base.exists(),files=[],directories=[],symlinks=[],complete=True)
    groups.append(group)
    if not base.exists():continue
    if base.is_symlink():group['symlinks'].append(meta(base));group['complete']=False;continue
    assert base.resolve(strict=True)==base
    allowed=(base==ROOT or ROOT in base.parents or base in exact)
    assert allowed
    for folder,dirs,names in os.walk(base,followlinks=False,onerror=onerror):
        if time.monotonic()>deadline or len(group['files'])>=50000:
            group['complete']=False;errors.append(dict(operation='bounded_partial',path=str(base),files=len(group['files'])));break
        for name in list(dirs):
            p=Path(folder)/name
            try:
                row=meta(p)
                if row['symlink']:group['symlinks'].append(row);dirs.remove(name)
                else:group['directories'].append(row)
            except Exception as e:errors.append(dict(path=str(p),operation='directory_lstat',error=repr(e)));dirs.remove(name)
        for name in names:
            p=Path(folder)/name
            try:
                row=meta(p)
                if row['symlink']:group['symlinks'].append(row)
                elif row['regular']:group['files'].append(row)
            except Exception as e:errors.append(dict(path=str(p),operation='file_lstat',error=repr(e)))
    group['regular_file_count']=len(group['files'])
    group['logical_bytes']=sum(x['bytes'] for x in group['files'])
    seen=set();allocated=0
    for row in group['files']:
        key=(row['device'],row['inode'])
        if key not in seen:allocated+=row['allocated_bytes'];seen.add(key)
    group['unique_inode_allocated_bytes']=allocated
disk=shutil.disk_usage(ROOT)
print(json.dumps(dict(epoch=time.time(),elapsed_seconds=time.monotonic()-start,
  root=str(ROOT),groups=groups,errors=errors,free_snapshot=disk.free,
  no_content_read_or_hash_or_GPU_peer_process_identity_query=True,
  no_delete_move_signal_permission_budget_or_environment_mutation=True,
  installed_envs_FINAL_forensic_raw_error_fulltext_log_all_excluded=True,
  pathnames_and_metadata_are_candidates_only_not_disposal_proof=True)))
