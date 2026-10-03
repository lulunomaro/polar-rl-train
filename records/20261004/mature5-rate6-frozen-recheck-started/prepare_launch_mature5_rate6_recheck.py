"""Prepare one isolated frozen diagnostic after the production controller holds.

Only copies source and deployment contracts. No production edits, PPO or ledger
changes. Never run this one-shot a second time; inspect its receipt instead.
"""
import json,shlex,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
D=Path(__file__).resolve().parent
DEST='/home/egde/rl_candidates/MOD4_RATE6_RECHECK_FROM_MATURE5_20261004'
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
REMOTE=r'''import hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
root=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
dest=Path('/home/egde/rl_candidates/MOD4_RATE6_RECHECK_FROM_MATURE5_20261004')
ledger=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reports=dest/'reports';reports.mkdir()
budget_raw=ledger.read_bytes()
assert read(root/'status.json')['stage']=='targeted_repair_hold'
assert read(ledger)['active_segment'] is None
assert read(ledger)['authorized_training_seconds']==252000
state=read(root/'reports/AUTONOMY_STATE.json')
assert state['mature']['cap']==5 and state['profile']=='white_v2' and state['active_training'] is None
before={name:sha(Path(name) if Path(name).is_absolute() else root/name) for name in read(root/'reports/SPIN_SOURCE_FREEZE.json')['sha256']}
assert before==read(root/'reports/SPIN_SOURCE_FREEZE.json')['sha256']
def ignore(path,names):
 return [n for n in names if n in ('__pycache__','.git','logs','reports','checkpoints','runs') or n.endswith(('.pt','.onnx','.npz','.npy','.log','.pyc'))]
shutil.copytree(root/'isaac',dest/'isaac',ignore=ignore)
shutil.copytree(root/'train',dest/'train',ignore=ignore)
cfgpath=dest/'isaac/mod4/env.json';cfg=read(cfgpath)
assert cfg['RM_SPIN_MAX_RAD_S']=='5.0' and cfg['RM_MILD_DR_PROFILE']=='white_v2'
cfg['RM_SPIN_MAX_RAD_S']='6.0';cfgpath.write_text(json.dumps(cfg,indent=2))
audit=[]
for part in ('isaac','train'):
 for p in (dest/part).rglob('*'):
  if p.is_file():
   rel=p.relative_to(dest).as_posix();original=root/rel
   audit.append(dict(path=rel,production_sha256=sha(original),candidate_sha256=sha(p),bytes_equal=p.read_bytes()==original.read_bytes()))
assert [x['path'] for x in audit if not x['bytes_equal']]==['isaac/mod4/env.json']
old=read(root/'isaac/mod4/env.json');assert {k:v for k,v in cfg.items() if k!='RM_SPIN_MAX_RAD_S'}=={k:v for k,v in old.items() if k!='RM_SPIN_MAX_RAD_S'}
test=subprocess.run([sys.executable,str(dest/'test_mature5_rate6_admission.py')],cwd=dest,capture_output=True,text=True)
assert test.returncode==0,test.stderr
(reports/'CPU_ADMISSION_VERIFIED.json').write_text(json.dumps(dict(returncode=test.returncode,stdout=test.stdout,scope='Evidence guards only; not simulator validation'),indent=2))
after={name:sha(Path(name) if Path(name).is_absolute() else root/name) for name in before}
assert after==before and ledger.read_bytes()==budget_raw
hashes={p.relative_to(dest).as_posix():sha(p) for p in dest.rglob('*') if p.is_file() and 'reports' not in p.relative_to(dest).parts}
prepared=dict(epoch=time.time(),production_root=str(root),source=state['mature'],candidate_source_hashes=hashes,source_difference_audit=audit,only_recipe_change='Isolated max yaw5->6 for frozen probes',production_source_hashes_unchanged=after,PPO_performed=False,ledger_bytes_unchanged=True,budget_authority=False,copied_controllers_not_authorized_to_run=True,CPU_tests=9)
(reports/'PREPARED.json').write_text(json.dumps(prepared,indent=2))
env={k:v for k,v in os.environ.items() if not k.startswith('RM_') and k!='RM_SSH_PASSWORD'}
env['PYTHONUNBUFFERED']='1'
with (dest/'worker.log').open('x') as log:
 p=subprocess.Popen([sys.executable,str(dest/'run_mature5_rate6_recheck.py')],cwd=dest,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
proc=Path('/proc')/str(p.pid);stat=(proc/'stat').read_text().split(') ',1)[1].split()
receipt=dict(pid=p.pid,start_ticks=stat[19],cwd=str((proc/'cwd').resolve()),argv=(proc/'cmdline').read_bytes().decode().split('\0'),epoch=time.time(),detached=True,PPO_performed=False,production_changed=False)
(reports/'LAUNCHED.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(dict(receipt=receipt,copied_files=len(audit),production_sources_verified=len(before),candidate_recipe_changes=['RM_SPIN_MAX_RAD_S'],CPU_tests=9)))
'''
c=connect()
try:
 with c.open_sftp() as s:
  try:s.stat(DEST)
  except FileNotFoundError:s.mkdir(DEST)
  else:raise AssertionError('Isolated recheck already prepared; inspect instead of repeating')
  for name in ('run_mature5_rate6_recheck.py','test_mature5_rate6_admission.py'):
   s.put(str(D/name),DEST+'/'+name)
 _,o,e=c.exec_command(PY+' -c '+shlex.quote(REMOTE),timeout=60)
 raw=o.read().decode();error=e.read().decode();rc=o.channel.recv_exit_status()
 (D/'MATURE5_RATE6_PREPARATION_OUTPUT.txt').write_text(raw+error,encoding='utf8')
 assert rc==0,error
 print(raw)
 with c.open_sftp() as s:
  for name in ('PREPARED.json','LAUNCHED.json','CPU_ADMISSION_VERIFIED.json'):
   s.get(DEST+'/reports/'+name,str(D/('MATURE5_RATE6_'+name)))
finally:c.close()
