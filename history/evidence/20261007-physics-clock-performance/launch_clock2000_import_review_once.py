from pathlib import Path
import sys,shlex
D=Path(__file__).resolve().parent;R=D/'reports';root='/home/egde/rl_candidates/MOD4_PHYSICS_DT2000_IMPORT_REVIEW_20261007'
assert (R/'DT2000_SELECTED_CLOCK_ATTENTION.json').exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect;c=connect()
try:
 with c.open_sftp() as s:
  try:s.stat(root);raise AssertionError('Explicit import-review root exists; do not repeat entry')
  except FileNotFoundError:pass
  s.mkdir(root);s.mkdir(root+'/reports')
  s.put(str(D/'physics_clock2000.py'),root+'/reviewed_physics_clock.py')
  s.put(str(D/'supervise_clock2000_review.py'),root+'/continue_clock2000_import_review_once.py')
 code=r'''
from pathlib import Path
import sys,json,hashlib,shutil,subprocess,time
T=Path('/home/egde/rl_candidates/MOD4_PHYSICS_DT2000_CROSSBIN_REVIEW_20261007');D=Path('ROOT');R=D/'reports';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((T/'reports/SOURCE_FREEZE.json').read_text());assert len(f['sha256'])==182
attention=json.loads((T/'reports/SELECTED_CLOCK_ATTENTION.json').read_text());assert attention['active_segment'] is None
assert 'Native worker failed' in attention['error'] and 'Unreviewed physical timestep' in (T/'crossbin_sdk.log').read_text()
for n,h in f['sha256'].items():
 assert sha(T/n)==h,n;p=D/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(T/n,p)
shutil.copy2(D/'reviewed_physics_clock.py',D/'isaac/mod4/physics_clock.py')
sources={n:sha(D/n) for n in f['sha256']};sources['continue_clock2000_import_review_once.py']=sha(D/'continue_clock2000_import_review_once.py')
(R/'SOURCE_FREEZE.json').write_text(json.dumps(dict(sha256=sources,prior182_exact_except=['isaac/mod4/physics_clock.py'],scope='Both actual runtime import paths carry same reviewed2ms clock; original rejected worker ran no dynamic steps; no task/physics math changes'),indent=2))
assert sha(D/'physics_clock.py')==sha(D/'isaac/mod4/physics_clock.py')==sha(D/'physics_clock2000.py')
sys.path.insert(0,str(D/'isaac/mod4'));import physics_clock;assert physics_clock.validate_clock(.002)['decimation']==5
sys.path.insert(0,str(D));import continue_clock2000_import_review_once as q;q.verify()
launch=q.w.read(T/'reports/SELECTED_CLOCK_LAUNCHED.json');p=q.helpers.identity(launch['owner']['pid']);assert not p or p['state']=='Z'
assert q.base.budget_state()['active_segment'] is None and not q.base.trainers() and not q.w.read(q.ctl.STATE_PATH).get('active_training')
q.write('ACTUAL_IMPORT_SCOPE_REVIEW.json',dict(epoch=time.time(),retained_attention=attention,original_dynamic_steps=0,actual_CODE_clock_module_sha256=sha(D/'isaac/mod4/physics_clock.py'),root_clock_same=True,canonical_no_mutation=True))
with (D/'supervisor.log').open('x') as log:
 p=subprocess.Popen([q.base.PY,str(D/'continue_clock2000_import_review_once.py')],cwd=q.P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
v=dict(epoch=time.time(),owner=q.helpers.identity(p.pid),root=str(D),source_count=len(sources),actual_import_contract_reviewed=True)
q.write('SELECTED_CLOCK_LAUNCHED.json',v);print(json.dumps(v))
'''.replace('ROOT',root)
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=45);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
 if rc:(R/'DT2000_IMPORT_REVIEW_ERROR.txt').write_bytes(err);raise RuntimeError(err.decode())
 print(raw.decode())
 with c.open_sftp() as s:
  for n in ['SOURCE_FREEZE.json','ACTUAL_IMPORT_SCOPE_REVIEW.json','SELECTED_CLOCK_LAUNCHED.json']:s.get(root+'/reports/'+n,str(R/('DT2000_'+n)))
finally:c.close()
