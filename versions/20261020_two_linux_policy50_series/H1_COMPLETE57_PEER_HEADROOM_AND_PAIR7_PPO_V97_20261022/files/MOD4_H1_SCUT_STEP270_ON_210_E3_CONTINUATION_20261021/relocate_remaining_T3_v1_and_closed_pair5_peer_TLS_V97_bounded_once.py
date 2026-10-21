"""Remaining closed-data relocation; reuse the passed, byte-identical TLS protocol.

Only the two named closed H1 control-NPZ directories are eligible. All original
contents remain on 72 after full SHA acknowledgement; models and text stay put.
"""
from pathlib import Path
import ast,hashlib,importlib.util,json,secrets,time,traceback
T=Path(__file__).resolve().parent;W=T.parent;R=T/'reports';N=T/'H1_STEP270_E3_PAIR_V6_20261022'
P=T/'forensic_tls_peer_transfer_V96_V4.py'
s=importlib.util.spec_from_file_location('passed_storage_definitions',T/'finish_closed_pair5_missing_forensics_direct_TLS_V96_V4_once.py');ops=importlib.util.module_from_spec(s);s.loader.exec_module(ops);d=ops.d
read=lambda p:json.loads(Path(p).read_bytes());H=ops.H
def put(name,value):
    with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
INVENTORY=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,re,shutil,time
current=Path(v['current_root']);owner=Path(v['owner_root'])
assert json.loads((current/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited']
assert json.loads((owner/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled']
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');canonical=C.read_bytes();c=json.loads(canonical)
assert c['active_segment'] is None and c['authorized_training_seconds']==1548000 and len(c['budget_extensions'])==8 and c['remaining_training_seconds']==v['remaining']
for lock in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),Path(v['private_lock'])):
 with lock.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
groups=[]
for label,oldroot in (('T3_1710v1','/mnt/mod4_linux_durable_20261013/T3_1710v1/h1'),('closed_pair5','/mnt/mod4_linux_durable_20261013/H1step270_healthrepair_2210v5/h1')):
 old=Path(oldroot);base=old/'job0/production/control_prefix_raw'
 exit=json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes());assert exit['actual_all_own_children_waited']
 for root in (old,current,owner):
  for p in psutil.process_iter(['pid','cmdline']):
   try:assert p.pid==os.getpid() or not any(a.startswith(str(root)+'/') for a in p.info['cmdline'] or [])
   except psutil.Error:pass
 indexbytes=(base/'CONTROL_VALID_PREFIX_INDEX_ACTUAL.json').read_bytes();index=json.loads(indexbytes);rows=[];total=0
 for row in sorted(index['index'],key=lambda x:x['path']):
  p=Path(row['path'])
  if not p.exists():continue
  assert p.resolve().is_relative_to(base.resolve()) and not p.is_symlink() and re.fullmatch(r'control_prefix_\d+\.npz',p.name)
  stat=p.stat();assert stat.st_size==row['bytes'] and stat.st_nlink==1
  if total+stat.st_size>20*1024**3:continue
  h=hashlib.sha256()
  with p.open('rb') as f:
   for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
  assert h.hexdigest()==row['SHA'];rows.append(dict(path=str(p),bytes=stat.st_size,SHA=row['SHA'],mtime_ns=stat.st_mtime_ns,inode=stat.st_ino));total+=stat.st_size
 groups.append(dict(label=label,source_root=str(old),files=rows,total_bytes=total,node_exit=exit,producer_index_SHA=hashlib.sha256(indexbytes).hexdigest()))
assert C.read_bytes()==canonical
print(json.dumps(dict(epoch=time.time(),groups=groups,source_free=shutil.disk_usage(current).free,all_named_old_sources_and_current_owner_actual_out=True,original_locks_free=True,canonical_SHA=hashlib.sha256(canonical).hexdigest(),no_training_or_budget_write=True)))
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
    proof=read(N/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');q=read(N/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')
    assert proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out']
    assert read(N/'reports/PEER_FORENSICS_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json')['all_own_storage_processes_actual_out']
    assert read(R/'V96_V4_ACTUAL_TLS_HMAC_FULL_SHA_TRANSPORT_CPU_ACTUAL.json')['passed']
    sha=H(P);assert sha=='31e6c729fad4c7e73e60843535f602f95ab0eec0b18f2cc24262d1167840dcd7'
    ast.parse(P.read_text('utf8'));ast.parse(INVENTORY);ast.parse(READ_SOURCE)
    put('V97_REMAINING_CLOSED_H1_PEER_STORAGE_STARTED_ACTUAL.json',dict(epoch=time.time(),only_named_closed_sources=['T3_1710v1','closed_pair5'],protocol_SHA=sha,reuse_passed_protocol_no_CPU_GPU_reexecution=True,no_model_FINAL_source_text_or_error_removal=True))
    s=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(s);s.loader.exec_module(memory)
    secret=memory.recover();c=None;results=[];ready=None;receiver_result=None;ROOT72=None;cfgs=[]
    try:
        c=d.t.connect();inv=d.code(c,d.t.PY,INVENTORY,dict(current_root=q['roots']['h1'],owner_root=q['owner_root'],private_lock=q['specs']['h1']['private_lock'],remaining=proof['remaining_actual_snapshot']),timeout=420);c.close();c=None
        put('V97_REMAINING_CLOSED_H1_FRESH_FULL_SHA_INVENTORY_ACTUAL.json',inv)
        for group in inv['groups']:
            label=group['label'];rows=group['files']
            if not rows:results.append(dict(label=label,no_remaining_NPZ=True,no_remote_process_created=True));continue
            token=secrets.token_hex(32);manifest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            ROOT72='/home/lc01/Zonglin Li/zonglin2/forensic_originals/PEER_TLS_REMAINING_H1_V97_'+label
            ROOT210='/mnt/mod4_linux_durable_20261013/PEER_TLS_REMAINING_H1_V97_'+label
            target=ROOT72+'/retained_control_npz';ready=None;receiver_result=None
            c=d.connect72(secret);d.code(c,d.PY72,ops.INSTALL,dict(root=ROOT72,parent='/home/lc01/Zonglin Li/zonglin2/forensic_originals'),timeout=30)
            sf=c.open_sftp()
            try:sf.put(str(P),ROOT72+'/'+P.name)
            finally:sf.close()
            d.code(c,d.PY72,"from pathlib import Path;import json;B=Path(v['target']);assert not B.exists();B.mkdir();print(json.dumps(dict(new_target=str(B))))",dict(target=target),timeout=30)
            put('V97_'+label+'_TARGET_SOURCE_AST_ACTUAL.json',d.code(c,d.PY72,ops.CHECK,dict(script=ROOT72+'/'+P.name,SHA=sha),timeout=30))
            rcfg=dict(role='receiver',controller_root=ROOT72,target=target,files=rows,manifest_SHA=manifest,token=token);cfgs.append(rcfg)
            ready=d.code(c,d.PY72,ops.BOOT,dict(root=ROOT72,python=d.PY72,SHA=sha,cfg=rcfg),timeout=45);put('V97_'+label+'_RECEIVER_READY_ACTUAL.json',ready);c.close();c=None
            c=d.t.connect();d.code(c,d.t.PY,ops.INSTALL,dict(root=ROOT210,parent='/mnt/mod4_linux_durable_20261013'),timeout=30)
            sf=c.open_sftp()
            try:sf.put(str(P),ROOT210+'/'+P.name)
            finally:sf.close()
            put('V97_'+label+'_SOURCE_AST_ACTUAL.json',d.code(c,d.t.PY,ops.CHECK,dict(script=ROOT210+'/'+P.name,SHA=sha),timeout=30))
            scfg=dict(role='sender',controller_root=ROOT210,source_root=group['source_root'],owner_root=q['owner_root'],private_lock=q['specs']['h1']['private_lock'],remaining=proof['remaining_actual_snapshot'],files=rows,manifest_SHA=manifest,token=token,address='10.24.0.72',port=ready['port'],TLS_certificate_SHA=ready['TLS_certificate_SHA']);cfgs.append(scfg)
            sent=d.code(c,d.t.PY,"import runpy;runpy.run_path(v['script'],run_name='__main__',init_globals={'CFG':v['cfg']})",dict(script=ROOT210+'/'+P.name,cfg=scfg),timeout=1300);put('V97_'+label+'_SOURCE_COMPLETE_ACTUAL.json',sent)
            put('V97_'+label+'_SOURCE_FULL_TEXT_ALL_OUT_ACTUAL.json',d.code(c,d.t.PY,READ_SOURCE,dict(root=ROOT210),timeout=45));c.close();c=None
            c=d.connect72(secret);receiver_result=d.code(c,d.PY72,ops.READ_RECEIVER,dict(root=ROOT72),timeout=150);c.close();c=None
            put('V97_'+label+'_RECEIVER_FULL_TEXT_ALL_OUT_ACTUAL.json',receiver_result)
            got=json.loads(receiver_result['texts']['RECEIVER_COMPLETE_ACTUAL.json']);assert got['passed'] and receiver_result['all_receiver_processes_actual_out']
            assert {(r['path'],r['bytes'],r['SHA']) for r in got['files']}=={(r['path'],r['bytes'],r['SHA']) for r in sent['files']}
            results.append(dict(label=label,files=sent['files'],bytes=sent['bytes'],source_free_before=sent['source_free_before'],source_free_after=sent['source_free_after'],all_full_SHA_retained_on72=True,all_own_storage_processes_actual_out=True))
            token=None;rcfg.clear();scfg.clear()
        result=dict(epoch=time.time(),passed=True,groups=results,total_verified_relocated_bytes=sum(x.get('bytes',0) for x in results),all_contents_retained_on72=True,all_original_models_source_text_errors_logs_retained=True,original_canonical_bytes_unchanged=True,no_new_training_guard_or_GPU_or_budget_writer=True)
        put('V97_REMAINING_CLOSED_H1_FULL_SHA_PEER_STORAGE_SPACE_RELEASED_ACTUAL.json',result)
        print(json.dumps(dict(passed=True,bytes=result['total_verified_relocated_bytes'],groups=[dict(label=x['label'],files=len(x.get('files',[])),source_free_after=x.get('source_free_after')) for x in results])))
    except BaseException:
        error=traceback.format_exc()
        if c:c.close();c=None
        if ready and receiver_result is None:
            try:
                c=d.connect72(secret);receiver_result=d.code(c,d.PY72,ops.READ_RECEIVER,dict(root=ROOT72),timeout=150);c.close();c=None
                put('V97_REMAINING_CLOSED_H1_RECEIVER_ERROR_ALL_OUT_TEXT_ACTUAL.json',receiver_result)
            except BaseException:put('V97_REMAINING_CLOSED_H1_RECEIVER_OUT_READ_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_assume_out=True))
        put('V97_REMAINING_CLOSED_H1_PEER_STORAGE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=error,completed_groups=results,only_new_missing_only_after_actual_return=True));raise
    finally:
        secret=None
        for cfg in cfgs:cfg.clear()
        if c:c.close()
if __name__=='__main__':main()
