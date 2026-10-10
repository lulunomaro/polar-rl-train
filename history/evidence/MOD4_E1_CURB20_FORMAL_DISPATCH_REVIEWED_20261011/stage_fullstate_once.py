"""Stage a genuinely new full-state scope; no GPU, ledger mutation, or old once replay."""
from pathlib import Path
import sys,json,shlex,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011'))
from curb_io import connect_both,cleanup,linux_json,E,B,H
OLD='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_INDEPENDENT_20261011'
NEW='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_FULL_STATE_20261011'
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
def save(name,v):
 p=R/name;assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());return p
def put(f,path,raw):
 with f.open(path,'wbx') as out:out.write(raw)
 assert f.open(path).read()==raw
def main():
 save('FULLSTATE_STAGE_STARTED.json',dict(epoch=time.time(),trial_id='E1-CURB20-FULLSTATE-INDEPENDENT-DEPLOY-01',once=True,CPU_only_no_PPO=True))
 n,w=connect_both()
 try:
  copy=linux_json(n,r'''from pathlib import Path
import json,hashlib,shutil,fcntl,time
old=Path(OLD);new=Path(NEW);B=Path(BUDGET);E=Path(CENTRAL);budget=B.read_bytes();j=lambda p:json.loads(p.read_bytes());assert not new.exists()
s=j(old/'reports/CURB_NATIVE_SCOPE_STATE.json');passed=j(old/'reports/CURB_NATIVE_SCOPE_PASSED.json')
assert s['phase']=='CURB_new_native_contract_complete_review_ready' and s['child'] is None
for v in [s['owner']]+[j(old/('reports/'+k+'_PID_RECEIPT.json'))['child'] for k in ('CURB_SDK10','CURB_NATIVE20K')]:
 p=Path('/proc')/str(v['pid'])
 if p.exists():a=(p/'stat').read_text().split(') ',1)[1].split();assert a[0]=='Z' or int(a[19])!=v['start_ticks']
for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
l=j(B);assert l['active_segment'] is None and l['authorized_training_seconds']==828000
assert not list((E/'eval_queue').glob('*-133-*')) and not list((E/'results').glob('*-133-*')),'Future133 actual already exists; do not overwrite'
f=j(old/'reports/SOURCE_FREEZE.json');assert len(f['sha256'])==372;new.mkdir();(new/'reports').mkdir()
for name,h in f['sha256'].items():
 p=old/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==h,name;q=new/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
assert B.read_bytes()==budget
print(json.dumps(dict(epoch=time.time(),new_root=str(new),old372_byteexact=True,old_native_actual_exits_and_two_OS_locks_free=True,canonical_SHA=hashlib.sha256(budget).hexdigest(),no_PPO_or_ledger_transaction=True,source_freeze=f,native=passed)))
'''.replace('Path(OLD)','Path('+repr(OLD)+')').replace('Path(NEW)','Path('+repr(NEW)+')').replace('BUDGET',repr(B)).replace('CENTRAL',repr(E)))
  save('FULLSTATE_372_COPIED.json',copy)
  with n.open_sftp() as f:
   freeze=copy['source_freeze'];hashes=dict(freeze['sha256'])
   for p in sorted((D/'payload').rglob('*')):
    if not p.is_file():continue
    name=p.relative_to(D/'payload').as_posix();raw=p.read_bytes();compile(raw,name,'exec');assert name not in hashes
    put(f,NEW+'/'+name,raw);hashes[name]=H(raw)
   assert len(hashes)==378
   freeze=dict(freeze,candidate_root=NEW,sha256=hashes,old372_all_source_bytes_preserved=True,independent_expert='E1_CURB',new_fullstate_command_assignment_migration_scope=True)
   put(f,NEW+'/reports/SOURCE_FREEZE.json',json.dumps(freeze,indent=2).encode());save('FULLSTATE_SOURCE_FREEZE.json',freeze)
   selection=f.open(OLD+'/reports/SOURCE_SELECTED.json').read();put(f,NEW+'/reports/SOURCE_SELECTED.json',selection)
   context=json.loads(sorted(R.glob('CONTEXT_ACTUAL_[0-9]*.json'))[-1].read_bytes())
   review=context['reports']['E1_CURB20_132_COMPLETE_ACTUAL_REVIEW.json'];put(f,NEW+'/reports/CURB132_COMPLETE_ACTUAL_REVIEW.json',json.dumps(review['data'],indent=2).encode())
   reuse=dict(actual_SDK_native_exact_reused_no_replay=True,results=copy['native']['results'],source372_identity_exact_preserved=True,new_CPUCUDA_fullstate_only=True)
   put(f,NEW+'/reports/CURB_REUSED_NATIVE.json',json.dumps(reuse,indent=2).encode());save('FULLSTATE_REUSED_NATIVE.json',reuse)
   curb=json.loads((D.parent/'MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011/reports/CURB132_PUBLISHED.json').read_bytes())['jobs'][0]
   old_wave='/home/egde/rl_candidates/MOD4_S3_E1_WAVE_G3_INDEPENDENT_20261010'
   packages=json.loads(f.open(old_wave+'/reports/E1_PLANNED_BEHAVIOR_PUBLISHED.json').read())
   skills=[x for x in packages['jobs'] if x['seed']==20261002];assert len(skills)==3 and set(x['kind'] for x in skills)=={'flat','spin','world'}
   templates=dict(jobs=[curb]+skills,baseline132_CURB_and115_skills_exact=True)
   for x in templates['jobs']:
    for a in x['artifacts'].values():assert H(f.open(a['path']).read())==a['sha256']
   put(f,NEW+'/reports/CURB_FOUR_CASE_TEMPLATES.json',json.dumps(templates,indent=2).encode());save('FULLSTATE_FOUR_CASE_TEMPLATES.json',templates)
  code=r'''from pathlib import Path
import sys,json,time,torch
D=Path(ROOT);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'))
from test_curb_fullstate_cpu import main
source=json.loads((D/'reports/SOURCE_SELECTED.json').read_bytes());main(source['path'])
'''.replace('ROOT',repr(NEW))
  compile(code,'<curb-fullstate-targetCPU>','exec')
  _,o,e=n.exec_command(PY+' -c '+shlex.quote(code),timeout=90);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
  if rc:save('FULLSTATE_TARGET_CPU_ERROR.json',dict(epoch=time.time(),stdout=raw.decode(errors='replace'),stderr=err.decode(errors='replace'),returncode=rc,no_CUDA_GPU_or_ledger_transaction=True));raise RuntimeError('Target CPU fullstate admission rejected; preserve new root')
  cpu=json.loads(raw);cpu.update(epoch=time.time(),source_count=378,actual_CURB_CUDA_PPO_pending=True)
  p=save('CURB_TARGET_FULLSTATE_CPU_PASSED.json',cpu)
  with n.open_sftp() as f:put(f,NEW+'/reports/CURB_TARGET_FULLSTATE_CPU_PASSED.json',p.read_bytes())
  check=r'''from pathlib import Path
import sys,json,torch
D=Path(ROOT);sys.path.insert(0,str(D));sys.path.insert(0,str(D/'isaac/mod4'));torch.set_num_threads(1)
import supervise_curb20_fullstate_once as own
own.verify();own.wait_existing();assert not torch.cuda.is_initialized()
print(json.dumps(dict(passed=True,CPU_only=True,new_scope_count=len(own.read(D/'reports/SOURCE_FREEZE.json')['sha256']),original372_byteexact=True,two_locks_and_noactive_boundary_prelaunch=True,SDK_native_not_replayed=True)))
'''.replace('ROOT',repr(NEW))
  _,o,e=n.exec_command(PY+' -c '+shlex.quote(check),timeout=90);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
  guard=json.loads(raw);save('FULLSTATE_STAGE_VERIFIED.json',dict(epoch=time.time(),root=NEW,CPU=cpu,guard=guard,no_PPO_started=True,source_count=378))
  print(json.dumps(dict(root=NEW,source_count=378,CPU_passed=True,full_CUDA_PPO_pending=True,native_reused=True)))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:
  save('FULLSTATE_STAGE_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),original_new_root_and_outputs_retained=True,no_stage_replay=True));raise
