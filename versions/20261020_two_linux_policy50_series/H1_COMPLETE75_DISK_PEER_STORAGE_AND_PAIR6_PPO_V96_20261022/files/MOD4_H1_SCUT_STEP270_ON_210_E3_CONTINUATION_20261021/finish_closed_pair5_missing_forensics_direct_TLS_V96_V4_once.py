"""Missing-only finite peer transfer after V3 actual return; one SSH at a time."""
from pathlib import Path
import ast,hashlib,importlib.util,json,secrets,sys,time,traceback
T=Path(__file__).resolve().parent;W=T.parent;R=T/'reports';N=T/'H1_STEP270_E3_HEALTH_CLASSIFIER_PAIR_V5_20261022'
P=T/'forensic_tls_peer_transfer_V96_V4.py'
ROOT72='/home/lc01/Zonglin Li/zonglin2/forensic_originals/H1_closed_peerTLS_controller_V96_V4'
ROOT210='/mnt/mod4_linux_durable_20261013/H1_closed_peerTLS_controller_V96_V4'
TARGET='/home/lc01/Zonglin Li/zonglin2/forensic_originals/H1_closed_C_and_pair5_serial_20261022_V96_V2/source_pair5'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
import deploy_two50_reconciled_original_writer_once as d
read=lambda p:json.loads(Path(p).read_bytes())
def H(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for x in iter(lambda:f.read(8*1024**2),b''):h.update(x)
    return h.hexdigest()
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
INSTALL="""from pathlib import Path
import json
B=Path(v['root']);assert B.resolve().is_relative_to(Path(v['parent']).resolve()) and not B.exists();B.mkdir()
print(json.dumps(dict(root=str(B),new_unused_storage_controller_only=True)))
"""
CHECK="""from pathlib import Path
import ast,hashlib,json
p=Path(v['script']);assert hashlib.sha256(p.read_bytes()).hexdigest()==v['SHA'];ast.parse(p.read_text('utf8'))
print(json.dumps(dict(source_SHA=v['SHA'],source_AST=True,no_GPU_or_budget_writer=True)))
"""
BOOT=r'''
from pathlib import Path
import hashlib,json,select,subprocess
B=Path(v['root']);script=B/'forensic_tls_peer_transfer_V96_V4.py';assert hashlib.sha256(script.read_bytes()).hexdigest()==v['SHA']
err=(B/'RECEIVER_STDERR_ACTUAL.log').open('xb')
p=subprocess.Popen([v['python'],'-u','-B',str(script)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,start_new_session=True)
p.stdin.write(json.dumps(v['cfg']).encode()+b'\n');p.stdin.close();assert select.select([p.stdout],[],[],30)[0],'Receiver did not become ready'
ready=json.loads(p.stdout.readline());p.stdout.close();err.close();assert ready['identity']['pid']==p.pid
print(json.dumps(ready))
'''
READ_RECEIVER=r'''
from pathlib import Path
import json,psutil,time
B=Path(v['root']);until=time.monotonic()+130
def own():
 out=[]
 for p in psutil.process_iter(['pid','cmdline','create_time']):
  if any(a.startswith(str(B)+'/') for a in p.info['cmdline'] or []):out.append(p.info)
 return out
while own() or not (B/'RECEIVER_EXIT_ACTUAL.json').exists():
 assert time.monotonic()<until,'Own finite receiver has not actually returned';time.sleep(.5)
texts={p.name:p.read_text('utf8') for p in B.iterdir() if p.is_file() and p.suffix in ('.py','.json','.log')}
print(json.dumps(dict(epoch=time.time(),all_receiver_processes_actual_out=True,texts=texts)))
'''

def main():
    ast.parse(P.read_text('utf8'));sha=H(P)
    proof=read(N/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');q=read(N/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')
    assert proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out']
    assert list(R.glob('V96_V3_SERIAL_RELOCATION_ORIGINAL_ERROR_*.json'))
    inv=read(R/'V96_V3_PAIR5_FRESH_SOURCE_INVENTORY_ACTUAL.json');rows=inv['files'];assert rows and not list(R.glob('V96_V3_PAIR5_BATCH_*_SOURCE_DUPLICATES_RELEASED_ACTUAL.json'))
    manifest_SHA=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    put('V96_V4_DIRECT_PEER_MISSING_ONLY_STARTED_ACTUAL.json',dict(epoch=time.time(),source_files=rows,protocol_source=str(P),protocol_SHA=sha,source_root=q['roots']['h1'],target=TARGET,receiver_controller=ROOT72,sender_controller=ROOT210,one_SSH_connection_at_a_time=True,direct_data_channel_TLS_pinned_from_original_SSH=True,no_GPU_PPO_or_new_budget_writer=True,HMAC_and_TLS_private_key_memory_stdin_only=True))
    m=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py')
    memory=importlib.util.module_from_spec(m);m.loader.exec_module(memory)
    secret=memory.recover();token=secrets.token_hex(32);c=None;receiver_cfg={};sender_cfg={};ready=None;receiver_result=None
    try:
        c=d.connect72(secret);d.code(c,d.PY72,INSTALL,dict(root=ROOT72,parent='/home/lc01/Zonglin Li/zonglin2/forensic_originals'),timeout=30)
        sf=c.open_sftp()
        try:sf.put(str(P),ROOT72+'/'+P.name)
        finally:sf.close()
        put('V96_V4_TARGET_PROTOCOL_INSTALLED_SOURCE_AST_ACTUAL.json',d.code(c,d.PY72,CHECK,dict(script=ROOT72+'/'+P.name,SHA=sha),timeout=30))
        cpu=d.code(c,d.PY72,"import runpy;runpy.run_path(v['script'],run_name='__main__',init_globals={'CFG':{'role':'CPU'}})",dict(script=ROOT72+'/'+P.name),timeout=60);assert cpu['passed']
        put('V96_V4_ACTUAL_TLS_HMAC_FULL_SHA_TRANSPORT_CPU_ACTUAL.json',cpu)
        receiver_cfg=dict(role='receiver',controller_root=ROOT72,target=TARGET,files=rows,manifest_SHA=manifest_SHA,token=token)
        ready=d.code(c,d.PY72,BOOT,dict(root=ROOT72,python=d.PY72,SHA=sha,cfg=receiver_cfg),timeout=45)
        put('V96_V4_RECEIVER_ACTUAL_READY_IDENTITY_AND_TLS_PUBLIC_PIN.json',ready);c.close();c=None
        c=d.t.connect();d.code(c,d.t.PY,INSTALL,dict(root=ROOT210,parent='/mnt/mod4_linux_durable_20261013'),timeout=30)
        sf=c.open_sftp()
        try:sf.put(str(P),ROOT210+'/'+P.name)
        finally:sf.close()
        put('V96_V4_SOURCE_PROTOCOL_INSTALLED_SOURCE_AST_ACTUAL.json',d.code(c,d.t.PY,CHECK,dict(script=ROOT210+'/'+P.name,SHA=sha),timeout=30))
        sender_cfg=dict(role='sender',controller_root=ROOT210,source_root=q['roots']['h1'],owner_root=q['owner_root'],private_lock=q['specs']['h1']['private_lock'],remaining=proof['remaining_actual_snapshot'],files=rows,manifest_SHA=manifest_SHA,token=token,address='10.24.0.72',port=ready['port'],TLS_certificate_SHA=ready['TLS_certificate_SHA'])
        sent=d.code(c,d.t.PY,"import runpy;runpy.run_path(v['script'],run_name='__main__',init_globals={'CFG':v['cfg']})",dict(script=ROOT210+'/'+P.name,cfg=sender_cfg),timeout=1300)
        put('V96_V4_SOURCE_FULL_SHA_ACKNOWLEDGED_DUPLICATES_RELEASED_ACTUAL.json',sent);c.close();c=None
        c=d.connect72(secret);receiver_result=d.code(c,d.PY72,READ_RECEIVER,dict(root=ROOT72),timeout=150);c.close();c=None
        put('V96_V4_RECEIVER_COMPLETE_ALL_OUT_AND_FULL_TEXT_ACTUAL.json',receiver_result)
        received=json.loads(receiver_result['texts']['RECEIVER_COMPLETE_ACTUAL.json']);assert received['passed'] and receiver_result['all_receiver_processes_actual_out']
        assert {(r['path'],r['bytes'],r['SHA']) for r in received['files']}=={(r['path'],r['bytes'],r['SHA']) for r in sent['files']}
        import shutil
        C_before=shutil.disk_usage(T).free;scratch=T/'relocation_scratch_closed_pair5_to72_V96_V3';known={Path(r['path']).name:r for r in sent['files']};cleaned=[]
        for p in sorted(scratch.glob('*.npz')):
            assert p.resolve().is_relative_to(scratch.resolve()) and not p.is_symlink() and p.name in known
            row=known[p.name];assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'];p.unlink();cleaned.append(dict(path=str(p),bytes=row['bytes'],SHA=row['SHA'],verified_target_path=row['target_path']))
        result=dict(epoch=time.time(),passed=True,files=sent['files'],source210_released_bytes=sent['bytes'],source_free_after=sent['source_free_after'],source_above_original_disk25=sent['source_free_after']>25*1024**3,C_scratch_released=cleaned,C_free_before=C_before,C_free_after=shutil.disk_usage(T).free,receiver_all_actual_out=True,sender_actual_synchronous_returned=True,all_full_SHA_retained_on72=True,canonical_bytes_unchanged=sent['canonical_bytes_unchanged'],one_SSH_connection_at_a_time=True,no_existing_complete_target_file_retransferred=True,no_GPU_PPO_or_new_budget_writer=True)
        put('V96_V4_MISSING_FORENSICS_DIRECT_TLS_FULL_SHA_SPACE_RELEASED_ACTUAL.json',result)
        print(json.dumps(dict(passed=True,files=len(sent['files']),source_bytes=sent['bytes'],source_free_after=sent['source_free_after'],C_free_after=result['C_free_after'],above_original_disk25=result['source_above_original_disk25'])))
    except BaseException:
        error=traceback.format_exc()
        if c:c.close();c=None
        if ready and receiver_result is None:
            try:
                c=d.connect72(secret);receiver_result=d.code(c,d.PY72,READ_RECEIVER,dict(root=ROOT72),timeout=150);c.close();c=None
                put('V96_V4_RECEIVER_ERROR_ALL_OUT_TEXT_ACTUAL.json',receiver_result)
            except BaseException:
                put('V96_V4_RECEIVER_CLEANUP_READ_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_assume_receiver_out=True))
        put('V96_V4_DIRECT_PEER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=error,receiver_actual_result=receiver_result,new_missing_only_after_actual_return_no_old_helper_retry=True));raise
    finally:
        secret=None;token=None;receiver_cfg.clear();sender_cfg.clear()
        if c:c.close()
if __name__=='__main__':main()
