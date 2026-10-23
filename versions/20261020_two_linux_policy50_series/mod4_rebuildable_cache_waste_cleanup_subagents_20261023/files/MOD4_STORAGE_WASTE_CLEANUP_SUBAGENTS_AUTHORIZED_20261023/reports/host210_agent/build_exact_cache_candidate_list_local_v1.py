import json, pathlib, posixpath, hashlib
S=pathlib.Path(__file__).resolve().parents[2]
R=pathlib.Path(__file__).resolve().parent
P=S/'HOST210_FRESH_READONLY_METADATA_AUDIT_ACTUAL.json'
# The source report is at S/reports; parent arithmetic above points there.
if not P.is_file():
    P=R.parent/'HOST210_FRESH_READONLY_METADATA_AUDIT_ACTUAL.json'
raw=P.read_bytes(); outer=json.loads(raw); o=outer['remote']
D='/mnt/mod4_linux_durable_20261013'
archive_roots={D+'/anaconda/pkgs','/home/egde/anaconda3/pkgs'}
selected={}
for x in o['durable_inventory']['largest_files']:
    if posixpath.dirname(x['path']) in archive_roots:
        selected[x['path']]=x
for cache in o['cache_inventories']:
    for x in cache.get('candidate_metadata',[]): selected[x['path']]=x
rows=[]
for p,x in selected.items():
    if not(x.get('regular') and not x.get('symlink') and x.get('nlink')==1): continue
    if posixpath.dirname(p) in archive_roots and p.endswith(('.conda','.tar.bz2')):
        kind='conda_complete_download_archive'
        why='Complete compressed package in the direct conda download-cache directory; installation consumes extracted packages, not this download archive. Excludes all unpacked package files and env paths.'
    elif p.startswith('/home/egde/.cache/pip/wheels/') and (p.endswith('.whl') or posixpath.basename(p)=='origin.json'):
        kind='pip_rebuildable_wheel_cache'
        why='Disposable pip wheel download/build cache or its origin metadata; installed site-packages remain outside this root and unchanged.'
    elif (p.startswith('/home/egde/.cache/pip/http/') or p.startswith('/home/egde/.cache/pip/http-v2/')):
        kind='pip_http_response_cache'
        why='Disposable pip HTTP response cache; excludes installed packages and all task source/model/trace/report roots.'
    else: continue
    row=dict(x)
    row.update(selection_class=kind,reason=why,expected_fresh_stat_required_before_unlink=True,
               expected_guard_fields=['path','bytes','device','inode','nlink','mtime_ns','mode','uid','gid','regular','symlink'],
               can_release_durable_filesystem=(x['device']==o['fresh_disks'][0]['device']),
               exclude_if_now_open_or_modified_or_symlink=True)
    rows.append(row)
rows.sort(key=lambda x:(not x['can_release_durable_filesystem'],-x['bytes'],x['path']))
summary={}
for x in rows:
    key='durable_device66309' if x['can_release_durable_filesystem'] else 'home_device66310'
    q=summary.setdefault(key,{'files':0,'logical_bytes':0,'allocated_bytes':0})
    q['files']+=1;q['logical_bytes']+=x['bytes'];q['allocated_bytes']+=x['allocated_bytes']
plan={'schema':'host210_exact_rebuildable_cache_candidates_v1','source_report':str(P),
      'source_report_SHA256':hashlib.sha256(raw).hexdigest(),'remote_audit_started_epoch':o['started_epoch'],
      'audit_complete':o['durable_inventory']['complete'],'audit_errors':o['errors'],
      'no_remote_connection_hashing_or_cleanup_executed_by_this_local_builder':True,
      'selection_is_metadata_based_cache_only_pending_root_fresh_stat_execution':True,
      'size_totals_are_candidate_bytes_not_actual_release':True,'summary':summary,'files':rows,
      'excluded':['all partial/part/download/tmp without separate completed-source proof','all unpacked conda package files and installed environments','all current43/future44 root descendants','all MOD4 source/FINAL/raw/errors/fulltext/log/cost/budget','zy_ckpt/checkpoints','unknown user datasets/application installations/Recycle Bin data','symlink entries and nlink>1 entries'],
      'no_new_training_guard':'Original startup25GiB/runtime8GiB unchanged; cleanup itself does not establish next launch admission.'}
(R/'EXACT_CACHE_CANDIDATES_PENDING_FRESHSTAT_EXECUTION_ACTUAL.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
analysis={'schema':'host210_space_findings_actual_v1','source_report_SHA256':plan['source_report_SHA256'],
          'audit_elapsed_seconds':o['elapsed_seconds'],'audit_errors':o['errors'],
          'durable_disk':o['fresh_disks'][0],'home_disk':o['fresh_disks'][1],
          'different_filesystems':o['fresh_disks'][0]['device']!=o['fresh_disks'][1]['device'],
          'durable_classes':o['durable_inventory']['classes'],
          'durable_top40':[{'name':k,**v} for k,v in list(o['durable_inventory']['top_level'].items())[:40]],
          'cache_safe_selected_summary':summary,
          'coverage_limits':['Initial durable largest-file detail contains only top120; direct conda archives smaller than threshold are missing exact file metadata.','Initial home conda candidate_metadata is capped1000 and includes many unpacked files; only42 complete archive paths selected, not the entire286 archive-class aggregate. The286 class includes .partial/.part, which remain excluded.','1.718GB aggregate pyc is not selected: source counterpart stat and complete per-file metadata not captured for all140787 entries.','Home conda 32.189GB allocated within cache is not an estimated freeable quantity:319163 entries have nlink>1; package files may be linked into environments.'],
          'minimal_missing_only_audit':'Direct scandir+lstat of complete .conda/.tar.bz2 regular files in exact two known conda pkgs roots, no recursion/content/hash. Returns every archive expected stat and optional expanded-package index stat; partial names remain excluded.',
          'delete_performed':False}
(R/'HOST210_SPACE_MAJOR_FINDINGS_AND_SAFE_CACHE_SELECTION_ACTUAL.json').write_text(json.dumps(analysis,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'summary':summary,'selected_count':len(rows)},ensure_ascii=False))
