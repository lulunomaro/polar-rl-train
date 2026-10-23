"""Root-dispatched, bounded, read-only host72 storage audit; no credentials."""
from pathlib import Path
import os, stat, time, json, shutil, subprocess, signal

ROOT = Path('/home/lc01/Zonglin Li/zonglin2')
START = time.monotonic()
DEADLINE = START + 85
errors = []

def remaining():
    return max(.05, DEADLINE-time.monotonic())

def st(p):
    try:
        s=p.lstat()
        return dict(path=str(p), bytes=s.st_size, allocated_bytes=s.st_blocks*512,
                    device=s.st_dev, inode=s.st_ino, nlink=s.st_nlink,
                    uid=s.st_uid, gid=s.st_gid, mode=oct(stat.S_IMODE(s.st_mode)),
                    mtime_ns=s.st_mtime_ns, is_regular=stat.S_ISREG(s.st_mode),
                    is_directory=stat.S_ISDIR(s.st_mode), is_symlink=stat.S_ISLNK(s.st_mode))
    except Exception as e:
        errors.append(dict(path=str(p), operation='lstat', error=repr(e)))
        return dict(path=str(p), exists_or_accessible=False)

def run(argv, timeout):
    try:
        p=subprocess.run(argv, capture_output=True, text=True,
                         timeout=min(timeout, remaining()))
        return dict(argv=argv, returncode=p.returncode, stdout=p.stdout, stderr=p.stderr)
    except subprocess.TimeoutExpired as e:
        def dec(v):return v.decode(errors='replace') if isinstance(v,bytes) else (v or '')
        return dict(argv=argv, timed_out=True, stdout=dec(e.stdout), stderr=dec(e.stderr))
    except Exception as e:
        return dict(argv=argv, error=repr(e))

assert ROOT.resolve(strict=True)==ROOT
disk=shutil.disk_usage(ROOT)
root_entries=[]
for p in sorted(ROOT.iterdir()):
    root_entries.append(st(p))

# du reads only metadata; symlinks are not followed, and no file content is read.
top_du=run(['du','-x','-B1','--max-depth=1','--',str(ROOT)], 32)

# A cache name is only a candidate. Installed envs, assets and originals are excluded.
cache_paths=[ROOT/'pkgs',ROOT/'miniconda3/pkgs',ROOT/'anaconda3/pkgs',
             ROOT/'miniforge3/pkgs',ROOT/'.conda/pkgs',ROOT/'.cache/pip',
             ROOT/'cache/pip',ROOT/'pip-cache',ROOT/'.cache/uv',ROOT/'cache/uv']
cache_stats=[]
cache_files=[]
cache_du=[]
for p in cache_paths:
    if time.monotonic()>DEADLINE-8:break
    if not p.exists():
        cache_stats.append(dict(path=str(p),exists=False));continue
    row=st(p);cache_stats.append(row)
    if row.get('is_symlink') or not row.get('is_directory'):continue
    assert ROOT in p.resolve(strict=True).parents
    cache_du.append(run(['du','-x','-B1','--max-depth=1','--',str(p)], 7))
    count=0
    def onerror(e):errors.append(dict(path=e.filename,operation='cache_walk',error=repr(e)))
    for folder,dirs,names in os.walk(p,followlinks=False,onerror=onerror):
        if time.monotonic()>DEADLINE-6 or count>=30000:
            errors.append(dict(path=str(p),operation='cache_walk',bounded_partial=True,files=count));break
        dirs[:]=[n for n in dirs if not (Path(folder)/n).is_symlink()]
        for name in names:
            q=Path(folder)/name
            row=st(q)
            if row.get('is_regular'):
                row['classification']='cache_candidate_only_not_approved_delete'
                cache_files.append(row);count+=1

# Existing controller directories and package archives: shallow metadata only.
# No recursion into tasks, forensic_originals, audit, installed SDK/envs, or raw.
shallow=[]
for base in [ROOT,ROOT/'tasks',ROOT/'tmp',ROOT/'staging',ROOT/'cache']:
    if time.monotonic()>DEADLINE-2:break
    if not base.is_dir() or base.is_symlink():continue
    try:
        for p in sorted(base.iterdir()):
            n=p.name.lower()
            if (n.endswith(('.tar.gz','.tar.zst','.tar','.zip','.whl','.conda','.part','.tmp'))
                or 'tls' in n or 'controller' in n or 'staging' in n or 'cache' in n or n=='pkgs'):
                row=st(p);row['classification']='shallow_candidate_only_requires_proven_duplicate_or_rebuildable'
                shallow.append(row)
    except Exception as e:errors.append(dict(path=str(base),operation='shallow_list',error=repr(e)))

print(json.dumps(dict(epoch=time.time(),elapsed_seconds=time.monotonic()-START,
    root=str(ROOT),filesystem=dict(total=disk.total,used=disk.used,free=disk.free),
    root_entries=root_entries,top_level_du=top_du,cache_path_stats=cache_stats,
    cache_du=cache_du,cache_file_metadata=cache_files,shallow_candidates=shallow,errors=errors,
    guarantees=dict(read_only=True,no_file_content_read_or_hash=True,
      no_GPU_or_peer_identity_or_process_argv_query=True,no_training_signal_or_budget_access=True,
      no_originals_FINAL_PT_raw_error_log_fulltext_or_installed_environment_touched=True,
      no_delete_move_hardlink_remote_output_or_permission_change=True),
    limitations=['Historical candidate lists are not existence proof.',
      'Cache directory names alone do not prove disposable state.',
      'Hardlink nlink and st_blocks are not independently additive reclaimed bytes.',
      'Archive duplicates require source/producer contract and exact duplicate proof before deletion.',
      'Interrupted or timed-out du/walk is partial, never a complete inventory.'])))
