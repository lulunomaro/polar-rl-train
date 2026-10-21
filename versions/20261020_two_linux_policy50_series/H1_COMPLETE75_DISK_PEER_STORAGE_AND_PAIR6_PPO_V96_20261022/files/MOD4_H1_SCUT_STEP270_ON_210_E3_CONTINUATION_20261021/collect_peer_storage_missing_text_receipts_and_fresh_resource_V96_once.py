"""Finalize missing operational storage texts and fresh resource receipt only."""
from pathlib import Path
import importlib.util,json,sys,time,traceback
T=Path(__file__).resolve().parent;W=T.parent;R=T/'reports';N=T/'H1_STEP270_E3_HEALTH_CLASSIFIER_PAIR_V5_20261022'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
read=lambda p:json.loads(Path(p).read_bytes())
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
SOURCE=r'''
from pathlib import Path
import fcntl,hashlib,json,psutil,shutil,time
B=Path('/mnt/mod4_linux_durable_20261013/H1_closed_peerTLS_controller_V96_V4');e=json.loads((B/'SENDER_EXIT_ACTUAL.json').read_bytes());i=e['identity']
try:p=psutil.Process(i['pid']);alive=abs(p.create_time()-i['creation'])<.01
except psutil.NoSuchProcess:alive=False
assert not alive
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)
assert c['active_segment'] is None and c['authorized_training_seconds']==1548000 and len(c['budget_extensions'])==8 and c['remaining_training_seconds']==v['remaining']
for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),Path(v['private_lock'])):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
texts={p.name:p.read_text('utf8') for p in B.iterdir() if p.is_file() and p.suffix in ('.json','.log','.py')}
print(json.dumps(dict(epoch=time.time(),sender_actual_out=True,source_free_actual=shutil.disk_usage(B).free,canonical_SHA=hashlib.sha256(raw).hexdigest(),canonical_active_None=True,all_original_fcntl_free=True,texts=texts,no_model_or_raw_read=True)))
'''
TARGET=r'''
from pathlib import Path
import json,shutil,time
B=Path('/home/lc01/Zonglin Li/zonglin2/forensic_originals/H1_closed_C_and_pair5_serial_20261022_V96_V2')
texts={str(p.relative_to(B)):p.read_text('utf8') for p in B.rglob('VERIFIED_BATCH_*.json')}
assert 'C_T3_batch38/VERIFIED_BATCH_0.json' in texts
print(json.dumps(dict(epoch=time.time(),target_free_actual=shutil.disk_usage(B).free,texts=texts,no_model_or_raw_read=True)))
'''
def main():
    result=read(R/'V96_V4_MISSING_FORENSICS_DIRECT_TLS_FULL_SHA_SPACE_RELEASED_ACTUAL.json');proof=read(N/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');q=read(N/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')
    assert result['passed'] and result['receiver_all_actual_out'] and result['sender_actual_synchronous_returned']
    m=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(m);m.loader.exec_module(memory)
    secret=memory.recover();c=None
    try:
        c=d.t.connect();a=d.code(c,d.t.PY,SOURCE,dict(remaining=proof['remaining_actual_snapshot'],private_lock=q['specs']['h1']['private_lock']),timeout=45);c.close();c=None
        put('V96_SOURCE_PEER_STORAGE_ALL_OUT_FRESH_RESOURCE_AND_FULL_TEXT_ACTUAL.json',a)
        c=d.connect72(secret);secret=None;b=d.code(c,d.PY72,TARGET,{},timeout=45);c.close();c=None
        put('V96_TARGET_PRIOR_BATCH_ORIGINAL_FULL_TEXT_AND_FRESH_SPACE_ACTUAL.json',b)
        print(json.dumps(dict(sender_actual_out=True,source_free=a['source_free_actual'],target_free=b['target_free_actual'],missing_storage_text_receipts_finalized=True)))
    finally:
        secret=None
        if c:c.close()
if __name__=='__main__':
    try:main()
    except BaseException:
        put('V96_STORAGE_MISSING_TEXT_FINALIZE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_old_transfer_helper_retry=True));raise
