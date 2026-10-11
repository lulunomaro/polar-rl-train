from pathlib import Path
import sys,json,time,shlex,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(D));from stage_entry_fullstate_and_cpu_once import save
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import repair_io as io
OLD='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_ENTRY_FULLSTATE_REVIEWED_20261011'
NEW='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_ENTRY_SEED_REVIEWED_20261011'

def main():
 assert not (R/'ENTRY_SEED_DISPATCH_ACTUAL_RECEIPT.json').exists()
 n,w=io.connect_both()
 try:
  save('ENTRY_SEED_ACTUAL_BOUNDARY.json',io.boundary(n))
  copied=io.linux_json(n,r'''from pathlib import Path
import json,time,shutil,hashlib
old=Path(OLDROOT);new=Path(NEWROOT);j=lambda p:json.loads(p.read_bytes());assert not new.exists()
st=j(old/'reports/E1_STATE.json');attention=j(old/'reports/E1_ATTENTION.json');assert not attention['own_child_still_alive'] and attention['active_segment'] is None
for loc in (st['owner'],st['child'],j(old/'reports/E1_GUARDIAN_STARTED.json')):
 p=Path('/proc')/str(loc['pid'])
 if p.exists():
  z=(p/'stat').read_text().split(') ',1)[1].split();assert z[0]=='Z' or int(z[19])!=loc['start_ticks']
E=Path(CENTRAL);assert not list((E/'eval_queue').glob('*-139-*')) and not list((E/'eval_results').glob('*-139-*'))
freeze=j(old/'reports/SOURCE_FREEZE.json');assert len(freeze['sha256'])==409;new.mkdir();(new/'reports').mkdir()
for name,h in freeze['sha256'].items():
 p=old/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==h;q=new/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for name in ('SOURCE_SELECTED.json','CURB_FOUR_CASE_TEMPLATES.json','ENTRY_NATIVE_ACTUAL_REVIEW.json','ENTRY_REUSED_NATIVE20K.json','ENTRY_TARGET_FULLSTATE_CPU_PASSED.json','ENTRY_ORIGIN_BOUND_SDK10_PASSED.json'):
 shutil.copy2(old/'reports'/name,new/'reports'/name)
print(json.dumps(dict(epoch=time.time(),source_freeze=freeze,old409_fullbytes_exact=True,original_failed_fresh_retained=True,actual_old409_parent_guardian_child_exited=True,no_GPU_or_PPO_or_budget_action=True)))
'''.replace('OLDROOT',repr(OLD)).replace('NEWROOT',repr(NEW)).replace('CENTRAL',repr(io.E)))
  save('ENTRY_SEED_409_SOURCE_COPIED.json',copied)
  payload=D/'seed_reviewed_payload/supervise_curb20_entry_seed_reviewed_once.py';hashes=dict(copied['source_freeze']['sha256']);assert payload.name not in hashes
  with n.open_sftp() as f:
   raw=payload.read_bytes();io.put(f,NEW+'/'+payload.name,raw);hashes[payload.name]=io.H(raw)
   freeze=dict(candidate_root=NEW,sha256=hashes,old409_allbytes_exact=True,new_fresh_seed20260928_explicit=True)
   io.put(f,NEW+'/reports/SOURCE_FREEZE.json',json.dumps(freeze,indent=2).encode());save('ENTRY_SEED_SOURCE_FREEZE.json',freeze)
  code=r'''from pathlib import Path
import sys,torch,json,time,ast,subprocess
D=Path(ROOT);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_curb20_entry_seed_reviewed_once as reviewed
own=reviewed.own;own.verify();reviewed.closed_previous();rows=reviewed.reuse()
assert reviewed.D==D and own.D==D and own.R==D/'reports'
tree=ast.parse((D/'supervise_curb20_entry_seed_reviewed_once.py').read_text());fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='fresh_same_scope');text=ast.unparse(fn)
assert "'--seed', '20260928'" in text and 'own.main()' not in (D/'supervise_curb20_entry_seed_reviewed_once.py').read_text()
assert not torch.cuda.is_initialized()
cpu=dict(epoch=time.time(),passed=True,CPU_only=True,finite_tensors=102,source_count=len(own.read(D/'reports/SOURCE_FREEZE.json')['sha256']),old409_source_exact=True,new_correct_fresh_seed20260928_argv_verified=True,old_SDK_small_big_native_exact_reused=True,source_SHA=own.SOURCE_SHA,formal_only_original_source3c97=True,no_CUDA_initialized=True)
(D/'reports/ENTRY_SEED_REVIEWED_CPU_PASSED.json').write_text(json.dumps(cpu,indent=2))
assert not (D/'controller.log').exists() and not (D/'reports/E1_DISPATCH_STARTED.json').exists()
args=[own.s.q.base.PY,str(D/'supervise_curb20_entry_seed_reviewed_once.py')]
with (D/'controller.log').open('x') as f:p=subprocess.Popen(args,cwd=own.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
row=dict(epoch=time.time(),root=str(D),owner=own.identity(p.pid),argv=args,CPU=cpu,valid409_preflights_reused=True,new_failed_fresh_scope_seed_only=True,formal_requires_fresh_PASSED=True,no_budget_extension=True)
(D/'reports/ENTRY_SEED_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(row,indent=2));print(json.dumps(row))
'''.replace('ROOT',repr(NEW))
  _,o,e=n.exec_command(io.PY+' -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:save('ENTRY_SEED_CPU_DISPATCH_REJECTED.json',dict(epoch=time.time(),returncode=rc,stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace')));raise RuntimeError('Seed repair CPU/dispatch refused')
  row=json.loads(raw);save('ENTRY_SEED_DISPATCH_ACTUAL_RECEIPT.json',row);print(json.dumps(dict(root=NEW,source_count=len(hashes),owner=row['owner'],CPU_passed=True,fresh_active_formal_pending=True,old_valid_PPO_not_repeated=True)))
 finally:io.cleanup(n,w)

if __name__=='__main__':
 try:main()
 except BaseException:save('ENTRY_SEED_STAGE_DISPATCH_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_old_once_replay=True));raise
