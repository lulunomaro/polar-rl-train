"""Bounded read-only collection of an actually complete own PPO save and its14 receipts."""
from pathlib import Path
import json,sys,time,hashlib,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as base
ROOT=base.BASE+'/bodyframe20k_second_resample_phase_remainder2470_v1_20261015'
CODE=r'''
from pathlib import Path
import json,hashlib,time
R=Path(CONTEXT['root']);stage=R/'formal2470';A=stage/'attempt';pointers=list((A/'learning_logs').glob('*/latest_complete.json'))
def record(p):return dict(path=str(p),relative=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
if not pointers:print(json.dumps(dict(actual_positive_saved_pending=True,readonly=True)))
else:
 assert len(pointers)==1;latest=json.loads(pointers[0].read_bytes());ck=Path(latest['checkpoint']);assert ck.resolve().is_relative_to((A/'learning_logs').resolve()) and ck.exists();folder=ck.parent
 m=json.loads((stage/'BODYFRAME_TARGET_ACTUAL_MANIFEST.json').read_bytes());assert m['actual_source_SHA']=='1a370588db7706006a303e8d4ccd2efbb966201b826d3719ae42692a5339fd1a'
 assert ck.resolve()!=Path(m['source_path']).resolve()
 files=[ck,pointers[0],stage/'BODYFRAME_TARGET_ACTUAL_MANIFEST.json',stage/'BODYFRAME_SOURCE_FREEZE.json',A/'DISPATCH_RECEIPT.json',R/'PIPELINE_TARGET_CPU_ACTUAL.json']+list(folder.glob('*STARTUP_VERIFIED.json'))
 assert len(list(folder.glob('*STARTUP_VERIFIED.json')))==14
 body=json.loads((folder/'BIRTH_BODYFRAME_RESUME_STARTUP_VERIFIED.json').read_bytes());assert body['passed'] and body['actual_GPU_fullrestore_passed'] and not body['first_declared_new_entry_and_BODYdirection'] and body['predecessor_bodyframe_state_present']
 for name in ('CLOCK_TRAINING_HEALTH.json','CLOCK_TRAINING_HEALTH_RUNNING.json'):
  if (folder/name).exists():files.append(folder/name)
 print(json.dumps(dict(epoch=time.time(),root=str(R),actual_positive_saved_pending=False,latest=latest,ownfiles=[record(p) for p in files],ownbody14=body,readonly=True)))
'''
def main():
 c=None;sf=None;stamp=str(time.time_ns())
 try:
  c=base.connect();si,so,se=c.exec_command('CUDA_VISIBLE_DEVICES= '+base.PY+' -',timeout=60);si.write('CONTEXT='+repr(dict(root=ROOT))+'\n'+CODE);si.flush();si.channel.shutdown_write();raw=so.read();err=se.read();rc=so.channel.recv_exit_status();assert rc==0,(rc,err.decode('utf8','replace')[-2000:]);v=json.loads(raw)
  if v['actual_positive_saved_pending']:print(json.dumps(v));return
  dest=D/('own_positive_actual_'+stamp);dest.mkdir();sf=c.open_sftp();sf.get_channel().settimeout(60);rows=[]
  for row in v['ownfiles']:
   p=dest/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);sf.get(row['path'],str(p),max_concurrent_prefetch_requests=16);assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'];rows.append(dict(**row,local_path=str(p),two_host_byteSHA_exact=True))
  v['two_host_byteSHA_exact']=rows;out=R/('PHASE_REPAIR_OWN_POSITIVE_SAVED_ACTUAL_'+stamp+'.json');out.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),own_weight=rows[0],startup14=True,all_twohost_byteSHA_exact=True)))
 except BaseException:
  (R/('PHASE_REPAIR_OWN_POSITIVE_COLLECTION_ORIGINAL_ERROR_'+stamp+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),readonly=True,no_retry=True),indent=2),encoding='utf8');raise
 finally:
  if sf:sf.close()
  base.close(c)
if __name__=='__main__':main()
