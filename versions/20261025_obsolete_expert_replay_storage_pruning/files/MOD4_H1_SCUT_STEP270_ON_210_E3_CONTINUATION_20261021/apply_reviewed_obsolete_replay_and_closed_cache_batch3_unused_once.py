from pathlib import Path
import hashlib,importlib.util,json,os,sys,time,traceback
T=Path(__file__).resolve().parent;W=T.parent;S=W/'MOD4_REPLAY_WASTE_AUDIT_CLEANUP_AUTHORIZED_20261025';R=S/'reports'
def put(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
    source=(S/'remote_exact_obsolete_replay_and_closed_cache_prune_v3.py').read_text('utf8');plan=json.loads((R/'ROOT_REVIEWED_EXACT_REMOTE_REPLAY_PRUNE_BATCH3_PLAN_ACTUAL.json').read_bytes())
    put(R/'REMOTE_BATCH3_EXACT_PRUNE_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,source_SHA=hashlib.sha256(source.encode()).hexdigest(),selected={h:q['selected_files'] for h,q in plan['batches'].items()}))
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    spec=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);secret=m.recover()
    for host in ('210','72'):
        q=plan['batches'][host];q.update(host=host,human_lower_threshold=plan['human_lower_threshold'],source=source,audit=('/home/egde/rl_candidates/' if host=='210' else '/home/lc01/Zonglin Li/zonglin2/audit/')+'OBSOLETE_REPLAY_PRUNE_20261025_BATCH3')
        c=d.t.connect() if host=='210' else d.connect72(secret)
        try:result=d.code(c,d.t.PY if host=='210' else d.PY72,source,q,timeout=600)
        finally:c.close()
        texts=result.pop('all_audit_texts');dest=S/'actual_remote_unlink_audit_texts'/(host+'_BATCH3');dest.mkdir(parents=True)
        for row in texts:
            assert Path(row['relative']).name==row['relative'];raw=row.pop('text').encode();assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['SHA']
            with (dest/row['relative']).open('xb') as f:f.write(raw)
        put(R/('HOST'+host+'_EXACT_REPLAY_PRUNE_BATCH3_RETURNED_ACTUAL.json'),dict(result,full_audit_texts=texts,all_original_intents_actions_complete_text_returned=True))
        print(json.dumps({k:result[k] for k in ('passed','deleted_count','deleted_logical_bytes','allocated_bytes_all_selected_links_removed','filesystem_snapshot_deltas','skips')}),flush=True)
    secret=None
except BaseException:
    put(R/('REMOTE_BATCH3_ORIGINAL_READER_OR_EXECUTION_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),partial_actual_unlinks_not_rolled_back_or_rerun=True));raise
