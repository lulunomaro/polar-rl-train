from pathlib import Path
import sys,shlex,json
D=Path(__file__).resolve().parent;R=D/'reports';root='/home/egde/rl_candidates/MOD4_PHYSICS_DT2000_PRACTICAL_REVIEW_20261007'
facts=json.loads((R/'DT2000_SELECTED_CLOCK_BEHAVIOR_REVIEW.json').read_text(encoding='utf8'))
assert facts['task_model_data_all_pass'] and facts['world']['pass_'] and all(v['all_in_original_signed_02'] for v in facts['pure4pi'])
decision=dict(accepted_for_bounded_adaptation=True,source_sha256='2f82374fe07a849dbbaeabbf8dd34b20d0df8da789f2ebc2be3e688a1b24498a',
 original_strict_sufficient_evidence=False,world64of64=True,pure4pi_signed_02_all16_pass=True,straight=facts['straight'],
 reason='Actual model/task/data healthy, matched complete initialstate/parameters. World64/64 and pure16/16 originalfacts; both straight directions correct, +1.5 under-speed about4.5percent and reverse3.8percent. Treat finite tracking residual as explicit adaptation target under human autonomy; no systematic loss of direction, no new numerical admission threshold.',
 only_after_exact_full_PPO_physical_health=True,no_quality_v4_veto_added=True,new_budget_seconds=0)
(R/'DT2000_PRACTICAL_ADMISSION.json').write_text(json.dumps(decision,indent=2),encoding='utf8')
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect;c=connect()
try:
 with c.open_sftp() as s:
  try:s.stat(root);raise AssertionError('Named practical review already staged')
  except FileNotFoundError:pass
  s.mkdir(root);s.mkdir(root+'/reports')
  s.put(str(D/'continue_clock2000_practical_review_once.py'),root+'/continue_clock2000_practical_review_once.py')
  s.put(str(R/'DT2000_PRACTICAL_ADMISSION.json'),root+'/reports/PRACTICAL_ADMISSION.json')
 code=r'''
from pathlib import Path
import sys,json,hashlib,shutil,time,subprocess
T=Path('/home/egde/rl_candidates/MOD4_PHYSICS_DT2000_IMPORT_REVIEW_20261007');D=Path('ROOT');R=D/'reports';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((T/'reports/SOURCE_FREEZE.json').read_text());assert len(f['sha256'])==183
for n,h in f['sha256'].items():
 assert sha(T/n)==h,n;p=D/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(T/n,p)
sources={n:sha(D/n) for n in f['sha256']};sources['continue_clock2000_practical_review_once.py']=sha(D/'continue_clock2000_practical_review_once.py')
(R/'SOURCE_FREEZE.json').write_text(json.dumps(dict(sha256=sources,prior183_byte_exact=True,scope='Explicit actual practical review and exact fullPPO audit before bounded2ms adaptation; no runtime changes'),indent=2))
sys.path.insert(0,str(D));import continue_clock2000_practical_review_once as q;q.verify()
launch=q.w.read(T/'reports/SELECTED_CLOCK_LAUNCHED.json');guard=q.w.read(T/'reports/SELECTED_CLOCK_GUARDIAN_STARTED.json')
for _ in range(60):
 owners=[q.helpers.identity(x['pid']) for x in (launch['owner'],guard)]
 if all(not p or p['state']=='Z' for p in owners):break
 time.sleep(.5)
else:raise RuntimeError('Prior plan-saved review authority still live')
assert q.base.budget_state()['active_segment'] is None and not q.w.read(q.ctl.STATE_PATH).get('active_training') and not q.base.trainers()
q.write('PRACTICAL_BOUNDARY.json',dict(epoch=time.time(),prior_saved_review=q.w.read(T/'reports/SELECTED_CLOCK_REVIEW_READY.json'),old_owner_guardian_exited=True,active_segment=None,no_budget_mutation=True,completed_SDK_native_behavior_reused=True))
with (D/'supervisor.log').open('x') as log:
 p=subprocess.Popen([q.base.PY,str(D/'continue_clock2000_practical_review_once.py')],cwd=q.P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
v=dict(epoch=time.time(),owner=q.helpers.identity(p.pid),root=str(D),source_count=len(sources),explicit_practical_admission=True)
q.write('SELECTED_CLOCK_LAUNCHED.json',v);print(json.dumps(v))
'''.replace('ROOT',root)
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=45);raw=o.read();err=e.read();rc=o.channel.recv_exit_status()
 if rc:(R/'DT2000_PRACTICAL_REVIEW_ERROR.txt').write_bytes(err);raise RuntimeError(err.decode())
 print(raw.decode())
 with c.open_sftp() as s:
  for n in ['SOURCE_FREEZE.json','SELECTED_CLOCK_LAUNCHED.json','PRACTICAL_ADMISSION.json']:s.get(root+'/reports/'+n,str(R/('DT2000_'+n)))
finally:c.close()
