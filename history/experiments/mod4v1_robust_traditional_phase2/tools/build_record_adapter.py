"""Derive isolated PH2 administrative adapter from OWN committed PH1 adapter.
Does not edit PH1 or archive_tools recorder. Assert every targeted substitution.
"""
from pathlib import Path
import hashlib
P=Path(__file__).resolve().parents[1];WT=P.parents[2]
old=WT/'history/experiments/mod4v1_robust_traditional_phase1/tools/record_phase1_adapter.py'
dest=P/'tools/record_phase2_adapter.py'
assert not dest.exists();text=old.read_text(encoding='utf-8')
# Keep the previously tested exact-set/blob validation, change only PH2 identity,
# append-on-owned-branch precondition, source counter schema and receipt scope.
text=text.replace('phase1','phase2').replace('PHASE1','PHASE2').replace('Phase1','Phase2')
def change(a,b):
    global text
    assert text.count(a)==1,(a,text.count(a));text=text.replace(a,b)
change("BASE='6d04141cb75c83220c60033c7e56b4f8174e507a'","BASE='93e0814f5d4dc165dda1f85f8ee12bc35be04d2f'")
change("MAIN_PRE='938b9ee8458f09a47e369995c8bfb1064b052a1f'","MAIN_PRE='412d5d5dcc12d725502849c0dc109367c61452bc'")
change("IDENT='mod4v1-robust-traditional-phase2';TAG='trial-20261102-'+IDENT","IDENT='mod4v1-robust-traditional-phase2';DATE=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d');TAG='trial-'+DATE+'-'+IDENT")
change("RECORD='history/experiments/20261102-'+IDENT+'.json'","RECORD='history/experiments/'+DATE+'-'+IDENT+'.json'")
change("out=text('ls-remote','origin','refs/heads/main','refs/heads/'+BRANCH,'refs/tags/'+TAG,'refs/tags/'+TAG+'^{}')","out=text('ls-remote','origin','refs/heads/main','refs/heads/'+BRANCH,'refs/tags/'+TAG,'refs/tags/'+TAG+'^{}','refs/tags/trial-20261102-mod4v1-robust-traditional-phase1','refs/tags/trial-20261102-mod4v1-robust-traditional-phase1^{}')")
change("assert 'refs/heads/'+BRANCH not in pre and 'refs/tags/'+TAG not in pre,'Owned refs already exist; never overwrite'","assert pre.get('refs/heads/'+BRANCH)==BASE and 'refs/tags/'+TAG not in pre,'Own base mismatch or new tag exists; never overwrite'\n    assert pre.get('refs/tags/trial-20261102-mod4v1-robust-traditional-phase1')=='1064f48cc077fdd3eb6c89e554b58f5d82ee5980' and pre.get('refs/tags/trial-20261102-mod4v1-robust-traditional-phase1^{}')==BASE")
change("assert 'refs/heads/'+BRANCH not in before_push and 'refs/tags/'+TAG not in before_push,'Owned refs appeared concurrently; do not overwrite'","assert before_push.get('refs/heads/'+BRANCH)==BASE and 'refs/tags/'+TAG not in before_push,'Owned base changed or new tag appeared; do not overwrite'")
change("main_window_unchanged=post.get('refs/heads/main')==before_push.get('refs/heads/main')","main_window_unchanged=post.get('refs/heads/main')==before_push.get('refs/heads/main')\n    assert post.get('refs/tags/trial-20261102-mod4v1-robust-traditional-phase1')==pre.get('refs/tags/trial-20261102-mod4v1-robust-traditional-phase1') and post.get('refs/tags/trial-20261102-mod4v1-robust-traditional-phase1^{}')==BASE")
change("'concurrent_main_advance_before_owned_writes_preserved':'REMOTE_MAIN_PRECHECK_EVENT.json'","'earlier_main_history':'Initial PH2 probe412d...; any later concurrent advance preserved in pre_record/pre_push/post, no rollback; old PH1 observations stay in prior receipt'")
change("'raw_index_only':manifest['summary']['raw_index_only_files']","'raw_index_only':manifest['summary']['raw_index_only']")
change("'raw_known_existing_producer_sha':manifest['summary']['raw_known_producer_sha']","'raw_known_existing_producer_sha':manifest['summary']['raw_existing_producer_SHA_known']")
change("'external_authority_indexes':manifest['summary']['external_authority_index_entries']","'external_authority_indexes':manifest['summary']['external_original_metadata_entries']")
change("'source_case_count':30","'source_case_count':446,'R15_software_failures_separate':33,'existing_Phase1_text_references':manifest['summary']['existing_phase1_Git_text_references']")
change("'Archive MOD4v1 robust traditional-control phase2 through R03'","'Archive MOD4v1 robust traditional-control phase2 through R16'")
change("'Sealed text hashes and exact owned staged set verified; no simulation rerun; R04/R05/active MPC and synchronization receipt pending phase2.'","'R00-R16 sealed text/reference hashes and exact new staged blobs verified; R15software33 separate; R17plus/activeCv3/receipt PH3pending; no rerun/Goal graduation.'")
change("'future_pending':'R04/R05 and future sources/reports, active portable_mpc_qp_v1, post-commit receipt and other new files; goal stays active'","'future_pending':'R17plus/exactRMterrain/activeportable_control_v3_current/dynamicCOM/postcommitreceipt PH3pending; goal stays active'")
change("'this_persisted_receipt_git_status':'PHASE2_PENDING_POST_COMMIT_REPORT_NOT_IN_PHASE2_COMMIT'","'this_persisted_receipt_git_status':'PHASE3_PENDING_POST_COMMIT_REPORT_NOT_IN_PHASE2_COMMIT'")
# Original comments refer to the first PH1 concurrent-main event; keep its factual
# context explicitly historical rather than asserting it happened again in PH2.
text=text.replace('# Earlier938... -> f070... advance was observed before ANY archive ref write.','# Historical PH1 main938... -> f070... advance is retained in the prior receipt.')
text=text.replace('Post-seal report is phase2pending.','Post-seal report is PH3pending.')
text=text.replace("'post_commit_receipt_pending_phase2':","'post_commit_receipt_pending_phase3':")
dest.write_text(text,encoding='utf-8');print({'adapter':str(dest),'source_adapter_SHA':hashlib.sha256(old.read_bytes()).hexdigest(),'new_adapter_SHA':hashlib.sha256(dest.read_bytes()).hexdigest()})
