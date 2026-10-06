from pathlib import Path
import sys,shlex,json
D=Path(__file__).resolve().parent;R=D/'reports';root='/home/egde/rl_candidates/MOD4_PHYSICS_DT2000_CROSSBIN_REVIEW_20261007'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
files={'physics_clock.py':D/'physics_clock2000.py','physics_clock2000.py':D/'physics_clock2000.py',
 'isaac/mod4/contact_capture.py':D/'dt2000_runtime/contact_capture.py','isaac/mod4/mod4_env.py':D/'dt2000_runtime/mod4_env.py',
 'isaac/mod4/train_mod4_ppo.py':D/'dt2000_runtime/train_mod4_ppo.py','isaac/mod4/clock_training_health.py':D/'clock_training_health.py',
 'supervise_clock2000_review.py':D/'supervise_clock2000_review.py','physics_speed2000_probe.py':D/'physics_speed2000_probe.py',
 'contact_crossbin_sdk.py':D/'contact_crossbin_sdk.py','contact_bin_oracle.py':D/'contact_bin_oracle.py','test_clock2000_cpu.py':D/'test_clock2000_cpu.py'}
c=connect()
try:
 with c.open_sftp() as s:
  try:s.stat(root);raise AssertionError('Named isolated2msroot already staged: review actual receipt rather than repeat')
  except FileNotFoundError:pass
  s.mkdir(root);s.mkdir(root+'/reports');s.mkdir(root+'/review_changes')
  for n,p in files.items():s.put(str(p),root+'/review_changes/'+p.name)
 code=r'''
from pathlib import Path
import json,hashlib,shutil,sys,time,subprocess,os,signal
J=Path('/home/egde/rl_candidates/MOD4_PHYSICS_DT1000_FALLBACK_20261007');D=Path('ROOT');R=D/'reports';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((J/'reports/SOURCE_FREEZE.json').read_text());assert len(f['sha256'])==175
changes=CHANGES
for n,h in f['sha256'].items():
 p=J/n;assert sha(p)==h,n;q=D/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for n in changes:
 p=D/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(D/'review_changes'/Path(n).name,p)
cfg=json.loads((D/'isaac/mod4/env.json').read_text());cfg['RM_PHYSICS_DT_S']='0.002';(D/'isaac/mod4/env.json').write_text(json.dumps(cfg,indent=2))
sources={n:sha(D/n) for n in set(f['sha256'])|set(changes)}
(R/'SOURCE_FREEZE.json').write_text(json.dumps(dict(sha256=sources,base= str(J),base175_preserved_except_explicit_changes=changes+['isaac/mod4/env.json'],scope='2ms clock; fixed5ms time-weighted bins; exact task-counter diagnostic; no task/DR/reward/PPO/nominal-hardware changes'),indent=2))
test=subprocess.run([sys.executable,str(D/'test_clock2000_cpu.py')],capture_output=True,text=True,cwd=D);(R/'CLOCK2000_CPU.txt').write_text(test.stdout+test.stderr);assert test.returncode==0
sys.path.insert(0,str(D));import supervise_clock2000_review as q;q.verify()
assert q.base.budget_state()['active_segment'] is None and not q.w.read(q.ctl.STATE_PATH).get('active_training') and not q.base.trainers()
state=q.w.read(J/'reports/SELECTED_CLOCK_STATE.json');child=q.helpers.identity(state['child']['pid']);assert not child or child['state']=='Z','Existing1ms frozen child still live'
oldflat=Path(state['output']);r=q.w.read(oldflat);assert q.w.assess_flat(r)['pass_'];assert r['checkpoint']==str(q.SOURCE)
owner=q.helpers.identity(690939);guard=q.helpers.identity(691835)
assert owner and owner['state']=='T' and owner['start_ticks']==46934422 and str(J/'supervise_clock1000_fallback.py') in owner['argv']
assert guard and guard['start_ticks']==46955018 and str(J/'supervise_clock1000_fallback.py') in guard['argv']
budget=q.ctl.CANONICAL.read_bytes()
os.kill(owner['pid'],signal.SIGTERM);os.kill(owner['pid'],signal.SIGCONT)
for _ in range(200):
 a=q.helpers.identity(owner['pid'])
 if not a or a['state']=='Z':break
 time.sleep(.05)
else:raise RuntimeError('Old paused launch authority failed to retire')
for _ in range(400):
 a=q.helpers.identity(guard['pid'])
 if not a or a['state']=='Z':break
 time.sleep(.05)
else:raise RuntimeError('Old guardian failed to exit after no-active authority retirement')
assert q.ctl.CANONICAL.read_bytes()==budget
v=dict(epoch=time.time(),retired_1ms_owner=owner,old_guardian=guard,old_flat_output=str(oldflat),old_flat_sha256=sha(oldflat),old_flat_actual_pass=True,old_frozen_child_naturally_exited=True,canonical_bytes_exact=True,no_tail_recharged=True,explicit_human_2ms_authority=True)
q.write('DT2000_SAFE_BOUNDARY.json',v)
q.base.atomic_json(J/'reports/DT2000_LAUNCH_AUTHORITY_RETIRED.json',v)
with (D/'supervisor.log').open('x') as log:
 p=subprocess.Popen([q.base.PY,str(D/'supervise_clock2000_review.py')],cwd=q.P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
v=dict(epoch=time.time(),root=str(D),owner=q.helpers.identity(p.pid),source_count=len(sources),scope='Actual2ms cross-bin SDK/20k/retention/exact PPO audit; conditional original23509 A0',new_budget_seconds=0)
q.write('SELECTED_CLOCK_LAUNCHED.json',v);print(json.dumps(v))
'''.replace('ROOT',root).replace('CHANGES',repr(list(files)))
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=60)
 raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
 if rc:(R/'DT2000_STAGING_ERROR.txt').write_bytes(err);raise RuntimeError(err.decode())
 print(raw.decode())
 with c.open_sftp() as s:
  for n in ['SOURCE_FREEZE.json','DT2000_SAFE_BOUNDARY.json','SELECTED_CLOCK_LAUNCHED.json','CLOCK2000_CPU.txt']:s.get(root+'/reports/'+n,str(R/('DT2000_'+n)))
finally:c.close()
