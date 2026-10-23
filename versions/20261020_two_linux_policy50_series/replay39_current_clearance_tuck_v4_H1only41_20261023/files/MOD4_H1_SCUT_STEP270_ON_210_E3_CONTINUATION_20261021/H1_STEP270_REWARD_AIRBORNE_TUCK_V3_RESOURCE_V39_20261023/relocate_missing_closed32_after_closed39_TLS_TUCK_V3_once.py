"""Reserved storage support: run only after this pair actually closes and CPU passes.

Reuse the actually passed TLS/HMAC protocol; fresh manifests, identities and
space are required. This does not prepare a future model or launch training.
"""
from pathlib import Path
import ast,hashlib,importlib.util,json,secrets,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';P=T/'forensic_tls_peer_transfer_V96_V4.py'
spec=importlib.util.spec_from_file_location('passed_storage_protocol_controller_definitions',T/'finish_closed_pair5_missing_forensics_direct_TLS_V96_V4_once.py');ops=importlib.util.module_from_spec(spec);spec.loader.exec_module(ops);d=ops.d
read=lambda p:json.loads(Path(p).read_bytes());H=ops.H
ROOT72='/home/lc01/Zonglin Li/zonglin2/forensic_originals/PEER_TLS_CLOSED32_AFTER_CLOSED39_TUCK_V3'
ROOT210='/mnt/mod4_linux_durable_20261013/PEER_TLS_CLOSED32_AFTER_CLOSED39_TUCK_V3'
TARGET=ROOT72+'/retained_control_npz'
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
INVENTORY=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,re,shutil,time
old=Path(v['source_root']);owner=Path(v['owner_root']);base=old/'job0/production/control_prefix_raw'
assert json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited'] and json.loads((owner/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled']
for root in (old,owner):assert not any(p.pid!=os.getpid() and any(a.startswith(str(root)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');canonical=C.read_bytes();c=json.loads(canonical)
assert c['active_segment'] is None and c['authorized_training_seconds']==1548000 and len(c['budget_extensions'])==8 and c['remaining_training_seconds']==v['remaining']
for lock in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),Path(v['private_lock'])):
 with lock.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
free=shutil.disk_usage(old).free;rows=[];total=0
if free<=25*1024**3:
 index=json.loads((base/'CONTROL_VALID_PREFIX_INDEX_ACTUAL.json').read_bytes())
 for row in sorted(index['index'],key=lambda x:x['path']):
  p=Path(row['path'])
  if not p.exists():continue
  assert p.resolve().is_relative_to(base.resolve()) and not p.is_symlink() and re.fullmatch(r'control_prefix_\d+\.npz',p.name)
  s=p.stat();assert s.st_size==row['bytes'] and s.st_nlink==1
  if total+s.st_size>v['max_bytes']:continue
  h=hashlib.sha256()
  with p.open('rb') as f:
   for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
  assert h.hexdigest()==row['SHA'];rows.append(dict(path=str(p),bytes=s.st_size,SHA=row['SHA'],mtime_ns=s.st_mtime_ns,inode=s.st_ino));total+=s.st_size
  if free+total>25*1024**3+512*1024**2:break # transfer-selection copy allowance only; startup admission remains original25GiB
assert C.read_bytes()==canonical
print(json.dumps(dict(epoch=time.time(),files=rows,total_bytes=total,source_free=free,already_above_original_disk25=free>25*1024**3,canonical_SHA=hashlib.sha256(canonical).hexdigest(),actual_allout_and_original_locks_free=True)))
'''
READ_SOURCE=r'''
from pathlib import Path
import json,psutil,time
B=Path(v['root']);e=json.loads((B/'SENDER_EXIT_ACTUAL.json').read_bytes());i=e['identity']
try:p=psutil.Process(i['pid']);alive=abs(p.create_time()-i['creation'])<.01
except psutil.NoSuchProcess:alive=False
assert not alive
print(json.dumps(dict(epoch=time.time(),sender_actual_out=True,texts={p.name:p.read_text('utf8') for p in B.iterdir() if p.is_file() and p.suffix in ('.json','.log','.py')})))
'''
def main():
    proof=read(R/'PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');q=read(R/'PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')
    assert proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out']
    old_stage=T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V32_20261023'
    old_proof=read(old_stage/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');assert old_proof['passed'] and old_proof['all_owner_nodes_children_actual_out'] and old_proof['original_canonical_cost_settled']
    sourceq=read(old_stage/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')
    q['roots']=dict(q['roots'],h1=sourceq['roots']['h1'])
    q['specs']['h1']=dict(q['specs']['h1'],private_lock=sourceq['specs']['h1']['private_lock'])

    assert read(T/'reports/V96_V4_ACTUAL_TLS_HMAC_FULL_SHA_TRANSPORT_CPU_ACTUAL.json')['passed']
    sha=H(P);assert sha==read(T/'reports/V96_V4_TARGET_PROTOCOL_INSTALLED_SOURCE_AST_ACTUAL.json')['source_SHA'];ast.parse(P.read_text('utf8'))
    put('CLOSED39_OLD32_HEADROOM_STARTED_ACTUAL.json',dict(epoch=time.time(),protocol_source_SHA=sha,reused_actual_TLS_HMAC_CPU_no_reexecution=True,only_after_actual_closed_pair_CPU=True,one_SSH_connection_at_a_time=True,no_GPU_or_budget_writer=True))
    m=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(m);m.loader.exec_module(memory)
    secret=memory.recover();token=secrets.token_hex(32);c=None;ready=None;receiver_result=None;rcfg={};scfg={}
    try:
        c=d.connect72(secret)
        capacity=d.code(c,d.PY72,"import shutil,json,time;print(json.dumps(dict(epoch=time.time(),free=shutil.disk_usage('/home/lc01/Zonglin Li/zonglin2/forensic_originals').free)))",{},timeout=30);c.close();c=None
        put('CLOSED39_OLD32_HEADROOM_TARGET_FRESH_CAPACITY_ACTUAL.json',capacity)
        maximum=min(4*1024**3,capacity['free']-25*1024**3-64*1024**2);assert maximum>400*1024**2,'Target cannot safely hold even one missing closed prefix'
        c=d.t.connect();inv=d.code(c,d.t.PY,INVENTORY,dict(source_root=q['roots']['h1'],owner_root=q['owner_root'],private_lock=q['specs']['h1']['private_lock'],remaining=proof['remaining_actual_snapshot'],max_bytes=maximum),timeout=180);c.close();c=None
        put('CLOSED39_OLD32_HEADROOM_FRESH_SOURCE_ACTUAL.json',inv)
        if inv['already_above_original_disk25']:
            put('CLOSED39_OLD32_HEADROOM_NO_TRANSFER_NEEDED_ACTUAL.json',dict(epoch=time.time(),source_free=inv['source_free'],no_new_target_or_process=True));return
        rows=inv['files'];assert rows
        manifest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        c=d.connect72(secret);d.code(c,d.PY72,ops.INSTALL,dict(root=ROOT72,parent='/home/lc01/Zonglin Li/zonglin2/forensic_originals'),timeout=30)
        sf=c.open_sftp()
        try:sf.put(str(P),ROOT72+'/'+P.name)
        finally:sf.close()
        d.code(c,d.PY72,"from pathlib import Path;import json;B=Path(v['target']);assert not B.exists();B.mkdir();print(json.dumps(dict(new_target=str(B))))",dict(target=TARGET),timeout=30)
        put('CLOSED39_OLD32_HEADROOM_TARGET_SOURCE_AST_ACTUAL.json',d.code(c,d.PY72,ops.CHECK,dict(script=ROOT72+'/'+P.name,SHA=sha),timeout=30))
        rcfg=dict(role='receiver',controller_root=ROOT72,target=TARGET,files=rows,manifest_SHA=manifest,token=token)
        ready=d.code(c,d.PY72,ops.BOOT,dict(root=ROOT72,python=d.PY72,SHA=sha,cfg=rcfg),timeout=45);put('CLOSED39_OLD32_HEADROOM_RECEIVER_READY_ACTUAL.json',ready);c.close();c=None
        c=d.t.connect();d.code(c,d.t.PY,ops.INSTALL,dict(root=ROOT210,parent='/mnt/mod4_linux_durable_20261013'),timeout=30)
        sf=c.open_sftp()
        try:sf.put(str(P),ROOT210+'/'+P.name)
        finally:sf.close()
        put('CLOSED39_OLD32_HEADROOM_SOURCE_AST_ACTUAL.json',d.code(c,d.t.PY,ops.CHECK,dict(script=ROOT210+'/'+P.name,SHA=sha),timeout=30))
        scfg=dict(role='sender',controller_root=ROOT210,source_root=q['roots']['h1'],owner_root=q['owner_root'],private_lock=q['specs']['h1']['private_lock'],remaining=proof['remaining_actual_snapshot'],files=rows,manifest_SHA=manifest,token=token,address='10.24.0.72',port=ready['port'],TLS_certificate_SHA=ready['TLS_certificate_SHA'])
        sent=d.code(c,d.t.PY,"import runpy;runpy.run_path(v['script'],run_name='__main__',init_globals={'CFG':v['cfg']})",dict(script=ROOT210+'/'+P.name,cfg=scfg),timeout=1300);put('CLOSED39_OLD32_HEADROOM_SOURCE_COMPLETE_ACTUAL.json',sent)
        put('CLOSED39_OLD32_HEADROOM_SOURCE_FULL_TEXT_ALL_OUT_ACTUAL.json',d.code(c,d.t.PY,READ_SOURCE,dict(root=ROOT210),timeout=45));c.close();c=None
        c=d.connect72(secret);receiver_result=d.code(c,d.PY72,ops.READ_RECEIVER,dict(root=ROOT72),timeout=150);c.close();c=None
        put('CLOSED39_OLD32_HEADROOM_RECEIVER_FULL_TEXT_ALL_OUT_ACTUAL.json',receiver_result)
        got=json.loads(receiver_result['texts']['RECEIVER_COMPLETE_ACTUAL.json']);assert got['passed'] and receiver_result['all_receiver_processes_actual_out']
        assert {(r['path'],r['bytes'],r['SHA']) for r in got['files']}=={(r['path'],r['bytes'],r['SHA']) for r in sent['files']}
        put('CLOSED39_OLD32_HEADROOM_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json',dict(epoch=time.time(),passed=True,files=sent['files'],source_free_after=sent['source_free_after'],source_above_original_disk25=sent['source_free_after']>25*1024**3,all_full_SHA_retained_on72=True,canonical_bytes_unchanged=True,all_own_storage_processes_actual_out=True,no_GPU_PPO_or_budget_writer=True))
        print(json.dumps(dict(files=len(sent['files']),source_free=sent['source_free_after'],above_original_disk25=sent['source_free_after']>25*1024**3)))
    except BaseException:
        err=traceback.format_exc()
        if c:c.close();c=None
        if ready and receiver_result is None:
            try:
                c=d.connect72(secret);receiver_result=d.code(c,d.PY72,ops.READ_RECEIVER,dict(root=ROOT72),timeout=150);c.close();c=None
                put('CLOSED39_OLD32_HEADROOM_RECEIVER_ERROR_ALL_OUT_TEXT_ACTUAL.json',receiver_result)
            except BaseException:put('CLOSED39_OLD32_HEADROOM_RECEIVER_OUT_READ_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_assume_out=True))
        put('CLOSED39_OLD32_HEADROOM_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=err,receiver_actual=receiver_result,new_missing_only_after_actual_return=True));raise
    finally:
        secret=None;token=None;rcfg.clear();scfg.clear()
        if c:c.close()
if __name__=='__main__':main()
