"""Independent local CPU review of returned immutable text receipts only.
Never accesses the remote host, deleted cache, model/raw, GPU, or Git.
"""
import ast, collections, hashlib, json, pathlib, time
R=pathlib.Path(__file__).resolve().parent
S=R.parents[1]
A=S/'actual_remote_cache_audit_texts'/'host210'
O=R/'INDEPENDENT_210_CACHE_ACTIONS_CPU_VERIFIED_ACTUAL.json'
assert not O.exists(), 'Independent review result is immutable; do not repeat once'
errors=[];counts=collections.Counter();checks=collections.Counter();refs=[]

def read(p):
    b=p.read_bytes();refs.append({'path':str(p),'bytes':len(b),'SHA256':hashlib.sha256(b).hexdigest()})
    return json.loads(b)

def check(ok,name,detail=None):
    checks[name]+=1
    if not ok:errors.append({'check':name,'detail':detail})

idx=read(S/'reports'/'HOST210_ALL_AUDIT_RAW_TEXT_SHA_AND_ACTION_SET_EXACT_ACTUAL.json')
cfg=read(S/'reports'/'EXACT_AUTHORIZED_REMOTE_REBUILDABLE_CACHE_SELECTION_ACTUAL.json')
meta=read(S/'reports'/'HOST210_DIRECT_CONDA_ARCHIVE_METADATA_ACTUAL.json')
ret=read(S/'reports'/'HOST210_EXACT_CACHE_CLEANUP_RETURNED_ACTUAL.json')
intent=read(A/'FULL_EXACT_INTENT_BEFORE_ANY_UNLINK.json')
complete=read(A/'COMPLETE_ACTUAL.json')
host=cfg['hosts']['210']; roots=host['roots']
allowed={'/mnt/mod4_linux_durable_20261013/anaconda/pkgs':66309,'/home/egde/anaconda3/pkgs':66310}
check(set(roots)==set(allowed),'root_allowlist_exact')
check(all(k=='conda_download_archive' for k in roots.values()),'all_roots_download_archives_only')
check(cfg['human_authorized_this_turn'] is True,'human_authorization_present')
check(meta['errors']==[],'initial_metadata_no_errors')
check(ret==complete,'actual_return_equals_raw_complete')
check(intent['cache_only'] is True and complete['cache_only'] is True,'cache_only_receipts')
check(intent['source_manifest_SHA']==hashlib.sha256(json.dumps(host,sort_keys=True).encode()).hexdigest(),'full_source_manifest_SHA_exact')
check(intent['roots']==roots,'intent_roots_exact')
check(intent['before_disks']==complete['before_disks'],'before_disk_snapshot_exact')

raw_manifest={x['name']:x for x in idx['files']}
local_names={p.name for p in A.iterdir() if p.is_file()}
check(len(raw_manifest)==len(idx['files']),'raw_manifest_names_unique')
check(local_names==set(raw_manifest),'all_raw_text_file_names_exact',{'missing':sorted(set(raw_manifest)-local_names),'extra':sorted(local_names-set(raw_manifest))})
for name,row in raw_manifest.items():
    b=(A/name).read_bytes()
    check(len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['SHA'],'original_raw_text_bytes_SHA_exact',name)
    if name.endswith('.json'):json.loads(b);counts['raw_JSON_parsed']+=1
    else:ast.parse(b.decode('utf-8'));counts['raw_source_AST_parsed']+=1
    counts['raw_files_SHA_checked']+=1

fmeta={}
for group in meta['groups']:
    check(group['exists'] is True and group['urls_txt_exists'] is True and group['only_direct_download_archives'] is True,'metadata_cache_registry_sentinel_and_scope',group['path'])
    for row in group['files']:
        p=row['path'];check(p not in fmeta,'metadata_paths_unique',p);fmeta[p]=row
manifest=host['files']; manifest_paths=[x['path'] for x in manifest]
checked=intent['all_selected_freshstat']; checked_paths=[x['row']['path'] for x in checked]
check(len(set(manifest_paths))==len(manifest_paths),'manifest_paths_unique')
check(manifest_paths==checked_paths,'manifest_intent_order_and_set_exact')
check(set(manifest_paths)==set(fmeta),'complete_fresh_metadata_candidate_set_exact')
names=sorted(n for n in raw_manifest if n.startswith('ACTION_'))
check(names==['ACTION_'+str(i).zfill(5)+'.json' for i in range(len(checked))],'action_file_indices_exact')
check(idx['action_count']==len(checked)==len(names)==871,'all_action_counts_exact')

identity_fields=['bytes','allocated_bytes','device','inode','nlink','uid','gid','mtime_ns','mode']
bydev=collections.defaultdict(lambda:collections.Counter()); action_epochs=[]; action_digest_rows=[]
for i,(entry,row,name) in enumerate(zip(checked,manifest,names)):
    action=json.loads((A/name).read_bytes());p=row['path']; root=row['cache_root'];pp=pathlib.PurePosixPath(p)
    check(root in allowed and str(pp.parent)==root and pp.name.endswith(('.conda','.tar.bz2')) and '..' not in pp.parts,'exact_direct_complete_archive_only',p)
    check(not pp.name.endswith(('.part','.partial','.download','.tmp')),'partial_never_selected',p)
    check('/envs/' not in p and 'H1step270_' not in p and not any(x in pp.parts for x in ('source','production','control_prefix_raw','logs','forensic_originals')),'protected_env_training_model_raw_log_paths_excluded',p)
    check(row['regular'] is True and row['symlink'] is False and row['nlink']==1,'regular_nonsymlink_single_link',p)
    check(row['listed_in_cache_urls_by_basename'] is True,'registered_cache_URL_basename_boolean',p)
    check(row['device']==allowed[root],'device_matches_exact_cache_root',p)
    check(row['age_seconds']>86400 and intent['epoch']-row['mtime_ns']/1e9>86400 and action['epoch']-row['mtime_ns']/1e9>86400,'old_over_24h_at_audit_intent_and_action',p)
    check(all(row[k]==fmeta[p][k] for k in fmeta[p]),'manifest_matches_original_exact_fresh_cache_metadata',p)
    check(entry['row']==row and entry['eligible'] is True and entry['skip_reason'] is None,'intent_exact_row_eligible_no_skip',p)
    check(action['index']==i and action['path']==p and action['expected']==row,'action_intent_identity_order_exact',name)
    check(all(entry['fresh_stat'][k]==row[k] and action['actual_before_unlink'][k]==row[k] for k in identity_fields),'metadata_intent_and_immediate_unlink_stat_exact',p)
    check(action['removed'] is True and action['result']=='REMOVED_REBUILDABLE_CACHE' and action['path_absent_after'] is True and 'error' not in action,'successful_unlink_receipt_and_absence',p)
    action_epochs.append(action['epoch']); action_digest_rows.append({'name':name,'SHA256':hashlib.sha256((A/name).read_bytes()).hexdigest(),'path':p})
    q=bydev[str(row['device'])];q['files']+=1;q['logical_bytes']+=row['bytes'];q['allocated_bytes_before']+=row['allocated_bytes']

logical=sum(q['logical_bytes'] for q in bydev.values()); allocated=sum(q['allocated_bytes_before'] for q in bydev.values())
check(complete['passed'] is True and complete['errors']==[] and complete['skipped_preflight']==0,'complete_pass_no_errors_or_skips')
check(complete['selected_count']==complete['removed_count']==len(checked),'complete_selected_removed_counts_exact')
check(complete['removed_logical_bytes']==logical==8700379196,'complete_removed_logical_bytes_exact')
check(complete['removed_allocated_bytes_before']==allocated,'complete_removed_allocated_bytes_exact')
check(complete['removed_by_device']=={d:q['logical_bytes'] for d,q in bydev.items()},'complete_removed_by_device_exact')
check(dict(bydev['66309'])=={'files':625,'logical_bytes':7377358429,'allocated_bytes_before':sum(x['allocated_bytes'] for x in manifest if x['device']==66309)},'durable_625_archive_exact')
check(dict(bydev['66310'])=={'files':246,'logical_bytes':1323020767,'allocated_bytes_before':sum(x['allocated_bytes'] for x in manifest if x['device']==66310)},'home_246_archive_exact')
check(intent['epoch']<=min(action_epochs)<=max(action_epochs)<=complete['epoch'],'intent_before_all_actions_before_complete')
for disk,b in complete['before_disks'].items():
    a=complete['after_disks'][disk]
    check(a['total']==b['total'] and complete['free_snapshot_deltas'][disk]==a['free']-b['free'],'filesystem_snapshot_delta_arithmetic_exact',disk)
check(complete['free_delta_is_whole_filesystem_snapshot_not_exclusive_causation'] is True,'free_deltas_not_misrepresented_as_exclusive_cleanup')

# Review actual saved source structurally. It may create audit files and unlink
# only the exact whitelist candidates; there is no subprocess/peer/GPU/model path.
src=(A/'EXECUTED_CACHE_CLEANUP_SOURCE.py').read_text(encoding='utf-8');tree=ast.parse(src)
for n in ast.walk(tree):
    if isinstance(n,ast.Call):
        callname=n.func.attr if isinstance(n.func,ast.Attribute) else n.func.id if isinstance(n.func,ast.Name) else ''
        check(callname not in {'kill','killpg','Popen','system','exec','eval','rmtree','remove','rename','replace','chmod','chown','truncate','load','loads_from_file'},'no_process_training_model_or_broad_recursive_mutation_call',callname)
check("p.unlink()" in src and "p.parent==root" in src and "s.st_nlink==1" in src and "time.time()-s.st_mtime>86400" in src and "p.name in registry[str(root)]" in src,'actual_source_exact_cache_guard_clauses_present')

result={'schema':'host210_independent_completed_cache_actions_CPU_review_v1','epoch':time.time(),'passed':not errors,
        'scope':'Only already returned local immutable audit JSON/source bytes. No SSH, remote stat, deleted-cache rehash, model/raw read, GPU, new cleanup or Git.',
        'all_original_text_files_full_SHA_verified':counts['raw_files_SHA_checked'],
        'counts':dict(counts),'checks_executed_by_kind':dict(checks),
        'exact_action_count':len(names),'removed_by_device_independently_summed':{d:dict(v) for d,v in bydev.items()},
        'total_removed_logical_bytes':logical,'total_removed_allocated_bytes_before':allocated,
        'filesystem_free_snapshot_deltas':complete['free_snapshot_deltas'],
        'free_snapshot_scope':'Whole-filesystem before/after snapshots include ongoing activity; do not equate exclusively to cleanup or add home free to durable.',
        'protected_paths_absent_from_all_871_exact_unlink_receipts':not any(e['check']=='protected_env_training_model_raw_log_paths_excluded' for e in errors),
        'source_report_references':refs,
        'ordered_actions_identity_SHA256':hashlib.sha256(json.dumps(action_digest_rows,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        'errors':errors}
with O.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'passed':result['passed'],'files':counts['raw_files_SHA_checked'],'actions':len(names),'by_device':result['removed_by_device_independently_summed'],'errors':len(errors),'report':str(O)},ensure_ascii=False))
if errors:raise SystemExit(2)
