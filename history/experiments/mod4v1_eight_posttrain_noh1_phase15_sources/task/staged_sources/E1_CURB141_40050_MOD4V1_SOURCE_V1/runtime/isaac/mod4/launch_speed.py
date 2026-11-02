"""One-time audited transfer of this task's supervisor, never kills the trainer."""
from pathlib import Path
import ast,json,os,signal,subprocess,time

r=Path('/home/egde/rl_candidates/MOD4_scut_continue10h_20260929')
s=json.loads((r/'status.json').read_text())
assert s['stage']=='training' and time.time()<s['deadline_epoch']-1800
if (r/'speed_handover.json').exists():raise RuntimeError('handover already initialized')
tree=ast.parse((r/'isaac/mod4/supervise_speed.py').read_text());ns={}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['safety','safety_group']],type_ignores=[]),'gates','exec'),ns)
for name in ['speed_preflight_2m.json','speed_step15_smoke.json']:
 d=json.loads((r/'reports'/name).read_text());assert ns['safety'](d,1.5),name
pid=s['training_pid'];cmd=Path(f'/proc/{pid}/cmdline').read_bytes()
assert b'train_mod4_ppo.py' in cmd and b'scut_contact_reboot_resume' in cmd
parents=[]
for p in Path('/proc').glob('[0-9]*/cmdline'):
 try:
  args=p.read_bytes().split(b'\0')
  if any(x.endswith(b'/resume_after_reboot.py') for x in args) and (p.parent/'cwd').resolve()==r:parents.append(int(p.parent.name))
  if any(x.endswith(b'/validate_rescue.py') for x in args) and (p.parent/'cwd').resolve()==r:raise RuntimeError('hourly eval still running; avoid interference')
 except (FileNotFoundError,PermissionError):continue
assert len(parents)==1,parents
(r/'status_before_speed.json').write_text(json.dumps(s,indent=2))
plan=dict(outgoing_pid=pid,outgoing_log_dir=s['log_dir'],outgoing_supervisor_pid=parents[0],
 deadline_epoch=s['deadline_epoch'],started_epoch=time.time(),old_speed_range=[-1.2,1.2],new_stages=[1.5,2.],
 reason='User authorized speed curriculum after nominal pass; abrupt +2m/s preflight failed so 1.5m/s stage first')
(r/'speed_handover.json').write_text(json.dumps(plan,indent=2))
os.kill(parents[0],signal.SIGTERM)
for _ in range(100):
 p=Path(f'/proc/{parents[0]}/stat')
 if not p.exists() or p.read_text().split(') ')[1][0]=='Z':break
 time.sleep(.1)
else:raise RuntimeError('old supervisor still exists')
env=os.environ.copy();env['PYTHONUNBUFFERED']='1'
p=subprocess.Popen(['/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python','isaac/mod4/supervise_speed.py'],cwd=r,env=env,
 stdout=open(r/'supervisor_speed.log','w'),stderr=subprocess.STDOUT,start_new_session=True)
print('new_supervisor',p.pid,'trainer_checkpoint_boundary_handover_pending',pid)
