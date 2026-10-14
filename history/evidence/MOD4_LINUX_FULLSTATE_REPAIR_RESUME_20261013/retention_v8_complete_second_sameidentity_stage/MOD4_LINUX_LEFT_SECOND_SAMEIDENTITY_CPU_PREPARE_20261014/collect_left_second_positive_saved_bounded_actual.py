"""Future read-only positive saved checkpoint collector. No launch or target writes."""
from pathlib import Path
import os,json,time,hashlib
import second_root_owned_transport_common_v1 as t
MATH_CODE='def verify_positive_state'+(t.D/'left_second_saved_positive_CPU_math_v1.py').read_text().split('def verify_positive_state',1)[1]
PRE=r'''
from pathlib import Path
import sys,json,time,hashlib,psutil,torch
R=Path(CONTEXT['proposed_root']);a=R/'left_second_formal3600_v1';sys.path.insert(0,str(R))
from second_target_CPU_pure_guard_v2 import logical_fullsave,same,walk,KEY,sha,SOURCE_SHA
from left_sameidentity_typed13_receipts import validate_set
assert not torch.cuda.is_initialized();cpu_rng=torch.get_rng_state().clone()
def record(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
mfile=R/'LEFT_SECOND_SAMEIDENTITY_ADMISSION_MANIFEST.json';m=json.loads(mfile.read_bytes())
assert sha(mfile)==CONTEXT['actual_manifest_SHA'] and m['source']['sha256']==SOURCE_SHA==CONTEXT['source_SHA']
assert m['num_envs']==20000 and m['no_initializer_repeat'] is True and m['scope_learning_block_index']==m['max_blocks_same_axis']==2
source_path=Path(m['source']['path']);assert sha(source_path)==SOURCE_SHA and source_path.stat().st_size==19044152
paths=list((a/'learning_logs').glob('*/latest_complete.json')) if (a/'learning_logs').is_dir() else []
if not paths:print(json.dumps(dict(epoch=time.time(),pending_own_complete_save=True,root=str(R),PPO_claimed=False)));sys.exit(0)
assert len(paths)==1;latest=json.loads(paths[0].read_bytes());p=Path(latest['checkpoint'])
assert p.is_file() and p.parent==paths[0].parent and p.resolve().is_relative_to(a.resolve())
own_record=record(p);c=torch.load(p,map_location='cpu',weights_only=False);source=torch.load(source_path,map_location='cpu',weights_only=False)
'''
POST=r'''
info=verify_positive_state(c,source)
dispatch_path=a/'DISPATCH_RECEIPT.json';dispatch=json.loads(dispatch_path.read_bytes())
assert dispatch['source']==m['source']
initial=R/'LEFT_SECOND_FORMAL_DISPATCH_ACTUAL.json';parent=json.loads(initial.read_bytes())
assert parent['pid']==CONTEXT['expected_parent_pid'] and parent['start_ticks']==CONTEXT['expected_parent_start_ticks']
proofpaths=list(p.parent.glob('*STARTUP*VERIFIED.json'));typed=validate_set(proofpaths,dispatch['child']['pid'],SOURCE_SHA)
proofs=[dict(**record(q),proof=json.loads(q.read_bytes())) for q in sorted(proofpaths)]
actual=[]
for role,row in [('parent',dispatch['parent']),('worker',dispatch['child'])]:
 try:
  proc=psutil.Process(row['pid']);ticks=int(Path('/proc',str(proc.pid),'stat').read_text().split(') ',1)[1].split()[19])
  got=dict(role=role,pid=proc.pid,created=proc.create_time(),start_ticks=ticks,argv=proc.cmdline(),cwd=proc.cwd())
  assert got['created']==row['created'] and got['argv']==row['argv'] and got['cwd']==row['cwd']==str(R)
  if role=='parent':assert got['pid']==parent['pid'] and ticks==parent['start_ticks']
  else:
   assert got['argv'][got['argv'].index('--init_checkpoint')+1]==str(source_path)
   assert got['argv'][got['argv'].index('--num_envs')+1]=='20000'
  actual.append(got)
 except psutil.NoSuchProcess:actual.append(dict(role=role,pid=row['pid'],actual_absent=True))
health=json.loads((p.parent/'CLOCK_TRAINING_HEALTH.json').read_bytes());verify_latest_health(health)
raw=(a/'worker_stdout.log').read_bytes()
assert all(x not in raw for x in (b'buffer overflow detected',b'Contacts have been dropped',b'PhysX scene is corrupted',b'CUDA error',b'Traceback (most recent call last)'))
assert sha(p)==own_record['sha256'] and sha(source_path)==SOURCE_SHA and torch.equal(torch.get_rng_state(),cpu_rng) and not torch.cuda.is_initialized()
artifacts=[own_record]+[{k:v for k,v in q.items() if k!='proof'} for q in proofs]+[record(mfile),record(dispatch_path)]
print(json.dumps(dict(epoch=time.time(),passed=True,root=str(R),own_checkpoint=own_record,source=m['source'],source_manifest=record(mfile),saved_state=info,thirteen_actual_typed_startup=typed,startup_proofs=proofs,own_dispatch=dispatch,actual_processes=actual,health_latest_separate_from_saved_controls=health,worker_stdout_observed_prefix_bytes=len(raw),worker_stdout_observed_prefix_SHA=hashlib.sha256(raw).hexdigest(),no_error_in_observed_log_prefix=True,no_CPU_RNG_draw=True,no_CUDA_initialized=True,artifacts=artifacts,formal_final_claimed=False,qualified50=False)))
'''
CODE=PRE+MATH_CODE+'\n'+POST
def main():
    local=json.loads((t.REPORTS/'SECOND_ROOT_UNIQUE_FORMAL_DISPATCH_ACTUAL.json').read_bytes())
    assert local['cwd']==t.ROOT and local['source']['sha256']==t.SOURCE_SHA
    c=None;sf=None
    try:
        c=t.connect();context=dict(proposed_root=t.ROOT,source_SHA=t.SOURCE_SHA,expected_parent_pid=local['pid'],expected_parent_start_ticks=local['start_ticks'],actual_manifest_SHA=local['manifest_SHA'])
        v=t.run(c,CODE,'LEFT_SECOND_OWN_POSITIVE_SAVED_CPU_REMOTE_ACTUAL',context)
        if v.get('pending_own_complete_save'):print(json.dumps(v));return
        stamp=str(time.time_ns());dest=t.D/('left_second_ownsave_actual_'+stamp);dest.mkdir()
        sf=c.open_sftp();sf.get_channel().settimeout(60);rows=[]
        for i,row in enumerate(v['artifacts']):
            name=row['path'];p=dest/(str(i)+'_'+name.rsplit('/',1)[1])
            assert sf.stat(name).st_size==row['bytes']
            sf.get(name,str(p),max_concurrent_prefetch_requests=16)
            assert p.stat().st_size==row['bytes'] and t.sha(p)==row['sha256'] and sf.stat(name).st_size==row['bytes']
            rows.append(dict(remote_path=name,local_path=str(p),bytes=p.stat().st_size,sha256=t.sha(p)))
        assert len(rows)==16 and rows[0]['sha256']==v['own_checkpoint']['sha256']
        path=t.REPORTS/('LEFT_SECOND_OWN_POSITIVE_SAVED_ACTUAL_'+stamp+'.json')
        t.write_once(path,dict(epoch=time.time(),remote_CPU=v,two_host_byteSHA_exact=rows,actual_file_bytes_from_this_own_second_scope=True,formal_final_claimed=False,pending_independent_local_CPU_verification=True))
        print(json.dumps(dict(collection_report=str(path),checkpoint_SHA=rows[0]['sha256'],saved_state=v['saved_state'],formal_final=False)))
    except BaseException:t.original_error('LEFT_SECOND_OWN_POSITIVE_COLLECTION_ORIGINAL_ERROR');raise
    finally:
        if sf:sf.close()
        if c:c.close()
        os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
