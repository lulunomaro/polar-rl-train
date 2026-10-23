"""Read-only metadata audit. Root runs once in its single pinned finite transport.
No model/raw content read, process query, deletion, budget write, or filesystem mutation.
"""
import os, sys, stat, time, json, heapq, collections

START = time.monotonic()
DEADLINE = START + 84.0
DURABLE = '/mnt/mod4_linux_durable_20261013'
EXCLUDED_TOP_NAMES = {'H1step270_reward_tuckclear4_2310v43', 'H1step270_reward_tuckclear4_2310v44'}
CACHE_ROOTS = [
    '/home/egde/.cache/pip',
    '/home/egde/anaconda3/pkgs',
    DURABLE + '/.cache/pip',
    DURABLE + '/pip_cache',
]
errors, skips = [], []
out = {'schema': '210_storage_waste_metadata_readonly_v1', 'started_epoch': time.time(),
       'read_only': True, 'no_model_raw_contents_hash_load_or_GPU': True,
       'no_process_identity_or_budget_read_write': True,
       'no_deletion_or_cleanup_performed': True, 'protected_current_future_roots': sorted(EXCLUDED_TOP_NAMES),
       'candidate_names_are_not_deletion_approval': True}

def error(path, exc):
    if len(errors) < 1000:
        errors.append({'path': path, 'type': type(exc).__name__, 'error': str(exc)})

def meta(path, s=None):
    s = os.lstat(path) if s is None else s
    return {'path': path, 'bytes': s.st_size, 'allocated_bytes': getattr(s, 'st_blocks', 0)*512,
            'device': s.st_dev, 'inode': s.st_ino, 'nlink': s.st_nlink,
            'mtime_ns': s.st_mtime_ns, 'mode': stat.S_IMODE(s.st_mode),
            'uid': s.st_uid, 'gid': s.st_gid, 'regular': stat.S_ISREG(s.st_mode),
            'directory': stat.S_ISDIR(s.st_mode), 'symlink': stat.S_ISLNK(s.st_mode)}

def keep(heap, limit, size, row):
    item=(size, row['path'], row)
    if len(heap) < limit: heapq.heappush(heap, item)
    elif item[:2] > heap[0][:2]: heapq.heapreplace(heap, item)

def disk(path):
    try:
        v=os.statvfs(path); s=os.lstat(path)
        return {'path': path, 'device': s.st_dev, 'total_bytes': v.f_blocks*v.f_frsize,
                'free_bytes': v.f_bfree*v.f_frsize, 'available_bytes': v.f_bavail*v.f_frsize,
                'read_only_flag': bool(v.f_flag & getattr(os, 'ST_RDONLY', 1))}
    except Exception as exc: error(path,exc); return {'path': path, 'error': str(exc)}

out['fresh_disks']=[disk(DURABLE),disk('/home/egde')]
out['mountinfo_selected'] = []
try:
    with open('/proc/self/mountinfo', 'r') as f:
        for line in f:
            p=line.split()
            if len(p)>4 and p[4] in (DURABLE,'/','/home'):
                out['mountinfo_selected'].append(line.rstrip())
except Exception as exc: error('/proc/self/mountinfo',exc)

def scan(root, cache=False):
    record={'path': root, 'exists': False, 'complete': False, 'files':0,'directories':0,
            'logical_bytes':0, 'unique_allocated_bytes':0, 'hardlink_files':0,
            'classes':{}, 'top_level':{}, 'largest_files':[], 'candidate_metadata':[]}
    try:
        root_s=os.lstat(root); record['root_stat']=meta(root,root_s); record['exists']=True
        if not stat.S_ISDIR(root_s.st_mode) or stat.S_ISLNK(root_s.st_mode):
            record['skipped_non_directory_or_symlink']=True; return record
    except FileNotFoundError:
        return record
    except Exception as exc: error(root,exc); return record
    seen=set(); top=collections.defaultdict(lambda:collections.Counter()); classes=collections.defaultdict(lambda:collections.Counter())
    largest=[]; candidates=[]; stack=[root]
    while stack and time.monotonic()<DEADLINE:
        here=stack.pop()
        try:
            entries=sorted(os.scandir(here),key=lambda e:e.name)
        except Exception as exc: error(here,exc); continue
        for e in entries:
            if time.monotonic()>=DEADLINE: stack.append(here); break
            if root==DURABLE and here==DURABLE and e.name in EXCLUDED_TOP_NAMES:
                skips.append({'path':e.path,'reason':'current_or_future_training_root_no_traversal'}); continue
            try: s=e.stat(follow_symlinks=False)
            except Exception as exc: error(e.path,exc); continue
            rel=os.path.relpath(e.path,root); first=rel.split(os.sep)[0]
            if stat.S_ISLNK(s.st_mode):
                top[first]['symlinks']+=1; continue
            if stat.S_ISDIR(s.st_mode):
                record['directories']+=1
                if s.st_dev!=root_s.st_dev:
                    skips.append({'path':e.path,'reason':'different_device_no_traversal'}); continue
                stack.append(e.path); continue
            if not stat.S_ISREG(s.st_mode): continue
            record['files']+=1; record['logical_bytes']+=s.st_size
            allocated=getattr(s,'st_blocks',0)*512; key=(s.st_dev,s.st_ino)
            unique=allocated if key not in seen else 0; seen.add(key)
            record['unique_allocated_bytes']+=unique; record['hardlink_files']+=int(s.st_nlink>1)
            lower=e.name.lower(); parts=rel.lower().split(os.sep)
            if cache:
                kind='pip_cache' if 'pip' in root else ('conda_download_archive' if lower.endswith(('.conda','.tar.bz2','.part','.partial')) else 'conda_unpacked_cache_or_metadata')
            elif lower.endswith(('.pt','.pth','.npz','.npy','.usd','.usda','.usdc','.zip','.tar','.tar.gz','.zst')):
                kind='protected_models_raw_assets_archive'
            elif lower.endswith(('.json','.jsonl','.log','.txt','.csv','.md','.yaml','.yml')) or 'error' in lower:
                kind='protected_reports_logs_sources_or_config'
            elif '__pycache__' in parts or lower.endswith(('.pyc','.pyo')): kind='regenerable_python_bytecode'
            elif lower.endswith(('.part','.partial','.tmp','.download')): kind='partial_or_temporary_name_only_unproven'
            else: kind='other_unclassified_not_junk_proven'
            for q in (top[first],classes[kind]):
                q['files']+=1; q['logical_bytes']+=s.st_size; q['unique_allocated_bytes']+=unique
            row=meta(e.path,s); row['class']=kind
            keep(largest,120,s.st_size,row)
            if cache or kind in ('regenerable_python_bytecode','partial_or_temporary_name_only_unproven'):
                keep(candidates,1000,s.st_size,row)
    record['complete']=not stack
    record['unvisited_directory_count']=len(stack)
    record['classes']={k:dict(v) for k,v in sorted(classes.items())}
    record['top_level']={k:dict(v) for k,v in sorted(top.items(),key=lambda kv:-kv[1]['unique_allocated_bytes'])}
    record['largest_files']=[x[2] for x in sorted(largest,reverse=True)]
    record['candidate_metadata']=[x[2] for x in sorted(candidates,reverse=True)]
    record['candidate_metadata_cap']=1000
    return record

# Cache metadata gets priority. Unpacked conda entries may hardlink into an installed
# environment: they are inventory only and cannot be removed based on this report.
out['cache_inventories']=[scan(p,True) for p in CACHE_ROOTS]
out['durable_inventory']=scan(DURABLE,False)
out['errors']=errors; out['skipped']=skips
out['timed_out']=time.monotonic()>=DEADLINE
out['elapsed_seconds']=time.monotonic()-START
out['ended_epoch']=time.time()
out['fresh_disk_end']=disk(DURABLE)
print(json.dumps(out,ensure_ascii=False,separators=(',',':')))
