"""Run only after the finite owner closes. Read/download own complete inputs."""
from pathlib import Path
import json,time,os,traceback
import transport_bodyframe_pipeline_v7 as t

REMOTE=r'''
from pathlib import Path
import json,hashlib,time,psutil,fcntl
r=Path(CONTEXT['root']);done=json.loads((r/'PIPELINE_COMPLETE_REVIEW_READY.json').read_bytes())
assert done['passed'] and done['formal']['updates']>0
owner=json.loads((r/'PARENT_IDENTITY.json').read_bytes())
try:assert psutil.Process(owner['pid']).create_time()!=owner['created']
except psutil.NoSuchProcess:pass
assert (r/'GUARDIAN_EXIT.json').is_file()
files=[]
def add(p,kind):
 if p.is_file():
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(1048576),b''):h.update(b)
  files.append(dict(path=str(p),relative=str(p.relative_to(r)),bytes=p.stat().st_size,sha256=h.hexdigest(),kind=kind))
for p in r.glob('*.json'):add(p,'root_metadata')
add(r/'pipeline_parent.log','root_stdout')
for name in ('native144','fullrestore120','formal300'):
 s=r/name;add(s/'OWN_STAGE_POSTEXIT_PASSED.json',name+'_postexit')
 
 for w in s.glob('NATIVE_*_WITNESS_*.pt'):add(w,name+'_native_root_witness')
 add(s/'BODYFRAME_TARGET_ACTUAL_MANIFEST.json',name+'_manifest');add(s/'BODYFRAME_SOURCE_FREEZE.json',name+'_freeze')
 add(s/'attempt/EXIT_RECEIPT.json',name+'_exit');add(s/'attempt/DISPATCH_RECEIPT.json',name+'_dispatch');add(s/'attempt/worker_stdout.log',name+'_stdout')
 own=json.loads((s/'OWN_STAGE_POSTEXIT_PASSED.json').read_bytes());p=Path(own['own_checkpoint']['path'])
 if name in ('fullrestore120','formal300'):add(p,name+'_wholeweight')
 for q in p.parent.glob('*.json'):add(q,name+'_worker_metadata')
 for q in p.parent.glob('*BODYFRAME*.pt'):add(q,name+'_bodyframe_roundtrip')
 if name=='formal300':
  for q in p.parent.glob('retention_prefix_*.npz'):add(q,'formal_complete_trace')
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');d=json.loads(B.read_bytes())
exit=json.loads((r/'formal300/attempt/EXIT_RECEIPT.json').read_bytes())
segment=[v for v in d['completed_segments'] if v['kind']==exit['canonical_unique_segment']];assert len(segment)==1 and d['active_segment'] is None
locks=[]
for p in [B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')]:
 f=p.open('r+b')
 try:
  fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);locks.append(dict(path=str(p),held=False))
 finally:f.close()
print(json.dumps(dict(epoch=time.time(),root=str(r),formal={k:done['formal'][k] for k in ('mode','own_checkpoint','source','actor_changed','Adam_delta','updates','controls','envsteps','callbacks')},source_original_SHA=CONTEXT['source'],files=files,owner=owner,actual_owner_guardian_child_out=True,two_fcntl_free=locks,unique_completed_segment=segment[0],canonical_remaining=d['remaining_training_seconds'],canonical_active=None)))
'''

def main():
    c=None;sftp=None
    try:
        c=t.connect();value,raw=t.run(c,REMOTE,dict(root=t.ROOT,source=t.SOURCE),'BODYFRAME_OWN_FINAL_INPUT_REMOTE_INDEX',timeout=180)
        folder=t.B/('own_pipeline_actual_'+str(time.time_ns()));folder.mkdir()
        sftp=c.open_sftp();sftp.get_channel().settimeout(60);local=[]
        for item in value['files']:
            p=folder/item['relative'];assert p.resolve().is_relative_to(folder.resolve());p.parent.mkdir(parents=True,exist_ok=True)
            sftp.get(item['path'],str(p),max_concurrent_prefetch_requests=16)
            assert p.stat().st_size==item['bytes'] and t.sha(p)==item['sha256']
            local.append(dict(item,local_path=str(p)))
        sftp.close();sftp=None
        result=dict(epoch=time.time(),actual=value,local_collected_files=local,twohost_byte_SHA_all_exact=True,collection_root=str(folder),CPU_verification_pending=True)
        out=t.save('BODYFRAME_OWN_FINAL_ALL_INPUTS_TWOHOST_ACTUAL',result)
        print(json.dumps(dict(report=str(out),formal=value['formal'],files=len(local),bytes=sum(v['bytes'] for v in local),all_twohost_SHA_exact=True)))
    except BaseException:
        print(t.save('BODYFRAME_FINAL_INPUT_COLLECTOR_ORIGINAL_ERROR',dict(epoch=time.time(),error=traceback.format_exc(),no_new_launch_or_retry=True)));raise
    finally:
        if sftp:sftp.close()
        t.close(c)

if __name__=='__main__':main()
