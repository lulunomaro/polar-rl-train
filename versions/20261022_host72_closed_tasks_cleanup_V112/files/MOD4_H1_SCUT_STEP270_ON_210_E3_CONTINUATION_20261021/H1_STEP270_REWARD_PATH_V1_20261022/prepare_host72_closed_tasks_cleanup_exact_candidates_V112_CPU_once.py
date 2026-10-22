from pathlib import Path,PurePosixPath
from collections import defaultdict,Counter
import json,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports'
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
    inv=json.loads((R/'V112_HOST72_TASKS_EXACT_FILES_AND_SMALL_CLOSED_MANIFESTS_READONLY_ACTUAL.json').read_bytes())
    files={x['path']:x for x in inv['files']};markers={x['path']:x['value'] for x in inv['small_saved_markers']}
    closed={str(PurePosixPath(p).parent) for p,v in markers.items() if p.endswith('/NODE_EXIT_ACTUAL.json') and v.get('actual_all_own_children_waited') and v.get('validation_fcntl_released_if_acquired')}
    groups=defaultdict(list)
    for p,m in markers.items():
        if not p.endswith('/THREE_SLOT_COMPLETE_MANIFEST_V1.json'):continue
        root=PurePosixPath(p).parent
        if str(root) not in closed:continue
        for row in m['files']:
            rel=PurePosixPath(row['relative']);path=str(root/rel)
            if path not in files or files[path]['bytes']!=row['bytes']:continue
            # Preserve every path and byte: only immutable input/template files, never output/raw trajectories.
            if rel.suffix.lower() not in ('.pt','.npz','.usd','.stl'):continue
            if rel.parts[:2] not in (('job0','source'),('job0','runtime')):continue
            if files[path]['nlink']!=1:continue
            sha=row.get('SHA')
            if not sha or len(sha)!=64:continue
            groups[(sha,row['bytes'])].append(dict(files[path],producer_SHA=sha,closed_node=str(root),manifest=p))
    dup=[]
    for (sha,size),rows in groups.items():
        if len(rows)<2:continue
        rows=sorted(rows,key=lambda x:x['path'])
        dup.append(dict(SHA=sha,bytes=size,keeper=rows[0],copies=rows[1:],possible_released_allocated_bytes=sum(x['allocated_bytes'] for x in rows[1:])))
    dup.sort(key=lambda x:-x['possible_released_allocated_bytes'])
    put('V112_MANIFEST_BOUND_IMMUTABLE_INPUT_DUPLICATE_CANDIDATES_CPU_ACTUAL.json',dict(epoch=time.time(),
      candidate_groups=dup,groups=len(dup),candidate_replacements=sum(len(x['copies']) for x in dup),
      candidate_allocated_bytes=sum(x['possible_released_allocated_bytes'] for x in dup),
      full_producer_SHA_size_and_saved_node_EXIT_identity_bound=True,
      actual_current_binary_SHA_and_modes_not_verified_yet=True,
      path_preserving_hardlink_dedup_proposal_not_deletion_of_unique_bytes=True,
      no_remote_mutation=True))
    proposals=[];skipped=[]
    for p,index in markers.items():
        if not p.endswith('/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json'):continue
        raw=PurePosixPath(p).parent;production=raw.parent;node=production.parent.parent
        final=markers.get(str(production/'FINAL.json'))
        rows=index.get('index',[])
        reason=None
        if str(node) not in closed:reason='No original NODE_EXIT all-children-waited and released proof in saved inventory'
        elif not final or not final.get('passed'):reason='No passed production FINAL in saved inventory'
        elif index.get('retention_failure_flag_preserves_all_currently_present_files'):reason='Failure flag; retain existing original prefixes'
        elif not rows or any(x.get('controls')!=24 for x in rows) or index['controls']!=24*len(rows):reason='Not a complete whole-update index'
        elif not index.get('all_success_and_failed_control_prefixes_retained'):reason='Already bounded or incomplete retention; no old batch replay'
        if reason:skipped.append(dict(index=p,reason=reason));continue
        keep=sorted(set([0,max(0,len(rows)-2),len(rows)-1]));removed=[];retained=[];invalid=[]
        for i,row in enumerate(rows):
            pair=[row,row.get('preupdate_source')]
            actual=[]
            for item in pair:
                if not item or item.get('path') not in files or files[item['path']]['bytes']!=item['bytes'] or len(item.get('SHA',''))!=64:
                    invalid.append(dict(index=i,missing_or_unbound=True));continue
                meta=files[item['path']]
                if meta['nlink']!=1 or not PurePosixPath(item['path']).is_relative_to(raw):invalid.append(dict(index=i,unsafe_identity=True));continue
                actual.append(dict(meta,producer_SHA=item['SHA'],pair_index=i))
            if i in keep:retained+=actual
            else:removed+=actual
        if invalid:skipped.append(dict(index=p,reason='Some paired originals absent or metadata mismatch; require missing-only analysis, do not prune',invalid=invalid));continue
        if not removed:continue
        proposals.append(dict(node=str(node),index=p,original_FINAL=str(production/'FINAL.json'),
          original_NODE_EXIT=str(node/'NODE_EXIT_ACTUAL.json'),prefix_pairs=len(rows),retain_indices=keep,
          retained_files=retained,proposed_removed_unique_originals=removed,
          proposed_released_allocated_bytes=sum(x['allocated_bytes'] for x in removed)))
    proposals.sort(key=lambda x:-x['proposed_released_allocated_bytes'])
    result=dict(epoch=time.time(),proposal_only=True,explicit_new_human_authorization_required=True,
      prior_retention_authorization_only_future_new_roots_not_these_old_originals=True,
      stages=proposals,stages_count=len(proposals),proposed_removed_files=sum(len(x['proposed_removed_unique_originals']) for x in proposals),
      proposed_released_allocated_bytes=sum(x['proposed_released_allocated_bytes'] for x in proposals),skipped=skipped,
      all_FINAL_source_failed_models_formal_native_evaluation_raw_errors_full_logs_cost_producer_path_size_SHA_preserved=True,
      removed_middle_raw_preupdate_would_be_irrecoverable_and_not_duplicate=True,
      no_binary_raw_PT_read_hash_GPU_or_remote_mutation=True)
    put('V112_OLD_COMPLETE_TRAINING_PREFIX_FIRST_LATEST2_EXPANSION_PROPOSAL_NOT_AUTHORIZED_CPU_ACTUAL.json',result)
    print(json.dumps(dict(duplicate_groups=len(dup),duplicate_copies=sum(len(x['copies']) for x in dup),duplicate_possible_bytes=sum(x['possible_released_allocated_bytes'] for x in dup),old_retention_expansion_stages=len(proposals),old_retention_expansion_possible_bytes=result['proposed_released_allocated_bytes'],largest_expansion=[(x['node'],x['proposed_released_allocated_bytes']) for x in proposals[:8]],skipped=len(skipped))))
except BaseException:
    put('V112_CANDIDATES_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
