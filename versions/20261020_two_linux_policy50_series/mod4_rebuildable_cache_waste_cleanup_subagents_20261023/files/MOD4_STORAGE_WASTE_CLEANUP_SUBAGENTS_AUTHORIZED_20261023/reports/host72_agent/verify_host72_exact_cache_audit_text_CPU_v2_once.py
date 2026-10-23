"""Independent local-only audit of already-returned immutable cleanup receipts."""
from pathlib import Path, PurePosixPath
import collections, hashlib, json, time, traceback
HERE=Path(__file__).resolve().parent
S=HERE.parents[1]
R=S/'reports'
OUT=HERE/'INDEPENDENT_72_CACHE_ACTIONS_CPU_VERIFIED_ACTUAL.json'
assert not OUT.exists(),'Once-only local audit already consumed'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_bytes())
def normalize_mode(x):return int(x,0) if isinstance(x,str) else x
def identity(row):
    return tuple(row[k] for k in ('bytes','allocated_bytes','device','inode','nlink','uid','gid','mtime_ns'))+(normalize_mode(row['mode']),)
def put(p,v):
    with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
    index=read(R/'HOST72_ALL_AUDIT_RAW_TEXT_SHA_AND_ACTION_SET_EXACT_ACTUAL.json')
    base=S/'actual_remote_cache_audit_texts/host72'
    expected_names=[x['name'] for x in index['files']]
    assert len(expected_names)==len(set(expected_names))
    assert set(expected_names)=={x.name for x in base.iterdir() if x.is_file()}
    raw={};decoded={}
    for x in index['files']:
        b=(base/x['name']).read_bytes()
        assert len(b)==x['bytes'] and sha(b)==x['SHA'],x['name']
        raw[x['name']]=b
        if x['name'].endswith('.json'):decoded[x['name']]=json.loads(b)
    intent=decoded['FULL_EXACT_INTENT_BEFORE_ANY_UNLINK.json']
    complete=decoded['COMPLETE_ACTUAL.json']
    selection_bytes=(R/'EXACT_AUTHORIZED_REMOTE_REBUILDABLE_CACHE_SELECTION_ACTUAL.json').read_bytes()
    selection=json.loads(selection_bytes)
    assert sha(json.dumps(selection['hosts']['72'],sort_keys=True).encode())==intent['source_manifest_SHA']
    selected=selection['hosts']['72']
    rows=selected['files'];checks=intent['all_selected_freshstat']
    assert selected['roots']==intent['roots']=={
        '/home/lc01/miniconda3/pkgs':'conda_download_archive',
        '/home/lc01/.cache/pip':'pip_http_or_wheel_cache'}
    independent=read(HERE/'HOST72_EXACT_REBUILDABLE_CACHE_CANDIDATES_FROM_METADATA_ACTUAL.json')
    preselected=independent['candidate_lists']['pip']+independent['candidate_lists']['conda_download_archives']
    assert len(rows)==len(checks)==2980
    assert len({x['path'] for x in rows})==len(rows)
    bypath={x['path']:x for x in rows}
    assert set(bypath)=={x['path'] for x in preselected}
    for x in preselected:assert identity(x)==identity(bypath[x['path']])
    actions=sorted(x for x in decoded if x.startswith('ACTION_'))
    assert actions==['ACTION_'+str(i).zfill(5)+'.json' for i in range(len(rows))]
    categories=collections.Counter();logical=collections.Counter();allocated=collections.Counter()
    seen_inodes=set();ages=[]
    for i,(row,checked,name) in enumerate(zip(rows,checks,actions)):
        action=decoded[name]
        assert checked['row']==row and checked['eligible'] is True and checked['skip_reason'] is None
        assert identity(checked['fresh_stat'])==identity(row)
        assert row['regular'] is True and row['symlink'] is False and row['directory'] is False
        assert row['uid']==1001 and row['device']==2049 and row['nlink']==1
        age=intent['epoch']-row['mtime_ns']/1e9;assert age>86400;ages.append(age)
        p=PurePosixPath(row['path']);root=PurePosixPath(row['cache_root'])
        assert p.is_absolute() and '..' not in p.parts and p!=root
        if row['kind']=='conda_download_archive':
            assert root==PurePosixPath('/home/lc01/miniconda3/pkgs') and p.parent==root
            assert p.name.endswith(('.conda','.tar.bz2'))
        else:
            assert row['kind']=='pip_http_or_wheel_cache' and root==PurePosixPath('/home/lc01/.cache/pip')
            assert p.relative_to(root).parts[0] in ('http','http-v2','wheels')
        assert '/zonglin2/' not in str(p)
        assert action['index']==i and action['path']==row['path'] and action['expected']==row
        assert action['removed'] is True and action['result']=='REMOVED_REBUILDABLE_CACHE'
        assert action['path_absent_after'] is True and 'error' not in action
        assert identity(action['actual_before_unlink'])==identity(row)
        assert action['epoch']-row['mtime_ns']/1e9>86400
        key=(row['device'],row['inode']);assert key not in seen_inodes;seen_inodes.add(key)
        categories[row['kind']]+=1;logical[row['kind']]+=row['bytes'];allocated[row['kind']]+=row['allocated_bytes']
    assert dict(categories)=={'conda_download_archive':495,'pip_http_or_wheel_cache':2485}
    assert complete['passed'] is True and complete['cache_only'] is True
    assert complete['selected_count']==complete['removed_count']==len(actions)==2980
    assert complete['skipped_preflight']==0 and complete['errors']==[]
    assert sum(logical.values())==complete['removed_logical_bytes']==33891500604
    assert sum(allocated.values())==complete['removed_allocated_bytes_before']==33898487808
    assert complete['removed_by_device']=={'2049':33891500604}
    returned=read(R/'HOST72_EXACT_CACHE_CLEANUP_RETURNED_ACTUAL.json')
    # The saved returned wrapper may add provenance. Compare the actual complete value.
    returned_value=returned.get('remote',returned)
    assert all(returned_value[k]==val for k,val in complete.items()),'Returned receipt differs from COMPLETE'
    before=complete['before_disks'];after=complete['after_disks']
    aliases=['/home/lc01/Zonglin Li/zonglin2','/home/lc01']
    assert list(before)==aliases and list(after)==aliases
    assert before[aliases[0]]==before[aliases[1]] and after[aliases[0]]==after[aliases[1]]
    delta=after[aliases[0]]['free']-before[aliases[0]]['free']
    assert delta==33883545600
    assert complete['free_snapshot_deltas']==dict.fromkeys(aliases,delta)
    assert complete['free_delta_is_whole_filesystem_snapshot_not_exclusive_causation'] is True
    source=raw['EXECUTED_CACHE_CLEANUP_SOURCE.py'].decode('utf8')
    registry_guard="p.name in registry[str(root)]"
    assert registry_guard in source and "u=root/'urls.txt'" in source
    assert "p.parent==root" in source and "s.st_nlink==1" in source
    assert "fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)" in source
    assert "identity(s)==expected(row)" in source and "p.unlink()" in source
    assert complete['no_model_raw_FINAL_source_error_log_installed_environment_GPU_signal_or_budget_access'] is True
    result=dict(epoch=time.time(),passed=True,independent_local_CPU_only=True, prior_V1_reader_schema_error_preserved=True,
       audit_raw_file_count=len(raw),action_count=len(actions),all_raw_original_bytes_SHA_exact=True,
       all_filename_sets_intent_selection_action_complete_exact=True,source_manifest_host_canonical_JSON_SHA_exact=True,
       independent_prior_candidate_manifest_set_and_identity_exact=True,
       all_exact_cache_paths_regular_nlink1_uid1001_device2049_age24h=True,
       youngest_selected_age_seconds=min(ages),all_fresh_stat_and_immediate_preunlink_stat_exact=True,
       conda_registry_membership_scope='Executed immutable source enforces package basename in current urls.txt before eligible=true; all 495 corresponding preflights and actions passed. No new remote registry read performed by this checker.',
       logical_bytes_by_kind=dict(logical),allocated_bytes_by_kind=dict(allocated),counts_by_kind=dict(categories),
       actual_removed_logical_bytes=complete['removed_logical_bytes'],actual_removed_allocated_bytes_before=complete['removed_allocated_bytes_before'],
       same_device_aliases_counted_once=True,device=2049,
       filesystem_free_before=before[aliases[0]]['free'],filesystem_free_after=after[aliases[0]]['free'],
       filesystem_free_snapshot_delta_once=delta,free_snapshot_not_exclusive_causation=True,
       protected_zonglin2_FINAL_models_source_raw_forensic_error_fulltext_logs_installed_envs_not_in_actions=True,
       no_SSH_or_cache_original_read_hash_stat_or_new_delete=True,
       artifact_source_SHA=sha(Path(__file__).read_bytes()),
       index_SHA=sha((R/'HOST72_ALL_AUDIT_RAW_TEXT_SHA_AND_ACTION_SET_EXACT_ACTUAL.json').read_bytes()),
       raw_manifest_SHA=sha(raw['FULL_EXACT_INTENT_BEFORE_ANY_UNLINK.json']),
       raw_complete_SHA=sha(raw['COMPLETE_ACTUAL.json']),
       Git_status='pending root stage archive')
    put(OUT,result)
    print(json.dumps({k:result[k] for k in ('passed','audit_raw_file_count','action_count','actual_removed_logical_bytes','filesystem_free_after','filesystem_free_snapshot_delta_once')}))
except BaseException:
    put(HERE/('HOST72_INDEPENDENT_CPU_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),local_only_no_remote_or_delete=True))
    raise
