"""Explicit retry after guardian argv type failure before any probe or PPO."""
import ast,hashlib,json,subprocess,sys,time
from pathlib import Path
ROOT=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002');CODE=ROOT/'isaac/mod4';REPORTS=ROOT/'reports';STAGE=Path(__file__).resolve().parent
LEDGER=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
def read(p):return json.loads(p.read_text())
def identity(pid):
 try:
  p=Path('/proc')/str(pid);s=(p/'stat').read_text().split(') ',1)[1].split()
  return dict(pid=pid,start_ticks=s[19],state=s[0],argv=(p/'cmdline').read_bytes().decode().split('\0'))
 except OSError:return None
old=read(REPORTS/'TARGETED_MATURE5_ENTRY_20261003.json');assert old['stage']=='verified_settled_entry'
former=identity(old['supervisor_identity']['pid']);assert not former or former['state']=='Z'
log=ROOT/'supervisor_targeted_mature5_20261003.log';assert 'TypeError: expected str, bytes or os.PathLike object, not int' in log.read_text()
budget=read(LEDGER);assert not budget.get('active_segment') and budget['charged_training_seconds']==165433.3585538864 and budget['authorized_training_seconds']==252000
assert not read(REPORTS/'AUTONOMY_STATE.json').get('active_training') and read(ROOT/'status.json')['stage']=='targeted_repair_hold'
for p in Path('/proc').iterdir():
 if p.name.isdigit():
  x=identity(int(p.name))
  if x and x['state']!='Z' and '-c' not in x['argv']:
   assert not any(a.endswith(('/train_mod4_ppo.py','/fullscale_worst_diagnostic.py','/supervise_autonomy.py','/supervise_targeted_mature5.py','/spin_rate_probe.py','/validate_speed.py')) for a in x['argv']),x
p=CODE/'supervise_targeted_mature5.py';before=p.read_bytes();assert hashlib.sha256(before).hexdigest()=='c7b9a16aa51387b011515e5c67f69ee29cbe3865c0dcff60c6c22150aa170029'
text=before.decode();text=text.replace("RECEIPT=REPORTS/'TARGETED_MATURE5_ENTRY_20261003.json'","RECEIPT=REPORTS/'TARGETED_MATURE5_ENTRY_RETRY1_20261003.json'")
assert "owner['start_ticks'],str(old['pid'])" in text
text=text.replace("owner['start_ticks'],str(old['pid'])","str(owner['start_ticks']),str(old['pid'])")
ast.parse(text)
# Exact real-style PID/tick integers must never enter a subprocess argv.
owner={'start_ticks':123456};old_parent={'pid':111,'start_ticks':654321}
argv=[str(x) for x in [sys.executable,'script','--guardian',123,str(owner['start_ticks']),str(old_parent['pid']),str(old_parent['start_ticks'])]]
assert all(isinstance(x,str) for x in argv)
receipt=REPORTS/'TARGETED_MATURE5_GUARDIAN_ARG_RECOVERY_20261003.json';assert not receipt.exists()
backup=REPORTS/'targeted_mature5_entry_before_retry1.py';assert not backup.exists();backup.write_bytes(before)
p.write_text(text);freeze=read(REPORTS/'SPIN_SOURCE_FREEZE.json');freeze['sha256']['isaac/mod4/supervise_targeted_mature5.py']=hashlib.sha256(p.read_bytes()).hexdigest()
(REPORTS/'SPIN_SOURCE_FREEZE.json').write_text(json.dumps(freeze,indent=2))
assert read(LEDGER)==budget
newlog=ROOT/'supervisor_targeted_mature5_retry1_20261003.log';assert not newlog.exists()
with newlog.open('x') as stream:child=subprocess.Popen([sys.executable,'-u',str(p)],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
result=dict(stage='retry1_launched',previous_entry=old,new_parent_pid=child.pid,guardian_tick_arg_converted_to_str=True,charged_unchanged=budget['charged_training_seconds'],new_source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),no_old_segment_settlement=True,source_count=len(freeze['sha256']),log=str(newlog),epoch=time.time())
receipt.write_text(json.dumps(result,indent=2));print(json.dumps(result))
