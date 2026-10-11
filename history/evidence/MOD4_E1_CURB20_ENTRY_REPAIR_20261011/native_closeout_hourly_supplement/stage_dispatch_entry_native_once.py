from repair_io import *
import traceback,ast
def main():
 save('ENTRY_STAGE_STARTED.json',dict(epoch=time.time(),trial_id='CURB20-ENTRY-NATIVE-01',new_root=NEW,old_389_bytes_immutable=True,new_budget_seconds=0))
 n,w=connect_both()
 try:
  save('ENTRY_ACTUAL_STAGE_BOUNDARY.json',boundary(n))
  code=r'''from pathlib import Path
import json,hashlib,shutil
old=Path(OLDROOT);new=Path(NEWROOT);assert not new.exists();freeze=json.loads((old/'reports/SOURCE_FREEZE.json').read_bytes());new.mkdir();(new/'reports').mkdir()
for name,h in freeze['sha256'].items():
 p=old/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==h;q=new/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
shutil.copy2(old/'reports/SOURCE_SELECTED.json',new/'reports/SOURCE_SELECTED.json')
print(json.dumps(dict(old_source_count=len(freeze['sha256']),old389_all_bytes_exact_preserved=True,no_GPU_or_budget_action=True)))
'''.replace('OLDROOT',repr(OLD)).replace('NEWROOT',repr(NEW))
  save('ENTRY_OLD_SOURCE_COPIED.json',linux_json(n,code))
  a=json.loads((R/'ENTRY_AUTHORITY_ACTUAL.json').read_bytes());hashes=dict(a['oldsource']['sha256'])
  with n.open_sftp() as f:
   for p in sorted((D/'payload').rglob('*')):
    if not p.is_file() or '__pycache__' in p.parts:continue
    name=p.relative_to(D/'payload').as_posix();assert name not in hashes;raw=p.read_bytes();compile(raw,str(p),'exec');put(f,NEW+'/'+name,raw);hashes[name]=H(raw)
   freeze=dict(candidate_root=NEW,sha256=hashes,old389_bytes_exact_preserved=True,new_scope='CURB20_reset_entry_only_V2; SDK/native no learning')
   put(f,NEW+'/reports/SOURCE_FREEZE.json',json.dumps(freeze,indent=2).encode());save('ENTRY_SOURCE_FREEZE.json',freeze)
   for name in ('ENTRY_V2_COMPONENT_CPU_PASSED.json','ENTRY_COMPONENT_V1_CPU_REJECTED.json'):
    put(f,NEW+'/reports/'+name,(R/name).read_bytes())
  code=r'''from pathlib import Path
import sys,json,torch,time,ast,subprocess
D=Path(NEWROOT);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_curb20_entry_native_once as own
own.verify();own.wait_existing();source=Path(own.read(D/'reports/SOURCE_SELECTED.json')['path']);info=own.inherited.fullsave(source);assert info['finite_tensors']==102 and not torch.cuda.is_initialized()
v=dict(epoch=time.time(),passed=True,source_checkpoint=info,new_source_count=len(own.read(D/'reports/SOURCE_FREEZE.json')['sha256']),CPU_only=True,SDK_native_pending=True,fullstate_PPO_formal_pending=True,no_budget_extension=True)
(D/'reports/ENTRY_TARGET_CPU_PASSED.json').write_text(json.dumps(v,indent=2))
entry=D/'supervise_curb20_entry_native_once.py';ast.parse(entry.read_text());assert not (D/'controller.log').exists() and not (D/'reports/ENTRY_NATIVE_STARTED.json').exists()
args=[own.s.q.base.PY,str(entry)]
with (D/'controller.log').open('x') as f:p=subprocess.Popen(args,cwd=own.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
receipt=dict(epoch=time.time(),owner=own.identity(p.pid),argv=args,target_CPU=v,new_scope_native_only=True,no_PPO_or_budget_write=True)
(D/'reports/ENTRY_NATIVE_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
'''.replace('NEWROOT',repr(NEW))
  _,o,e=n.exec_command(PY+' -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:save('ENTRY_DISPATCH_REJECTED.json',dict(returncode=rc,stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace')));raise RuntimeError('New entry dispatch rejected')
  row=json.loads(raw);save('ENTRY_NATIVE_DISPATCH_ACTUAL_RECEIPT.json',row);print(json.dumps(dict(owner=row['owner'],source_count=len(hashes),native_only=True,formal_pending=True)))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('ENTRY_STAGE_DISPATCH_ERROR.json',dict(error=traceback.format_exc(),no_oldonce_replay=True));raise
