"""Append the verified actual stage without altering training source or ledger."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
D=Path(__file__).resolve().parent
name='TARGETED_MATURE5_LATEST_HANDOFF_20261003.md'
root='/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002'
prepare='/home/egde/rl_candidates/MOD4_AUTONOMY_SLEEP_20261003'
text=(D/name).read_text(encoding='utf8')
marker='[TARGETED_MATURE16425_FORMAL5_VERIFIED_20261003]'
c=connect()
try:
 with c.open_sftp() as s:
  s.put(str(D/name),root+'/reports/'+name)
  for remote in (root+'/PLAN_AUTONOMY_SLEEP_20261003.md',prepare+'/PLAN_AND_HANDOFF.md'):
   with s.open(remote) as f:old=f.read().decode('utf8')
   if marker not in old:
    with s.open(remote,'w') as f:f.write((old+'\n\n'+marker+'\n'+text).encode('utf8'))
   with s.open(remote) as f:assert marker in f.read().decode('utf8')
 local=D.parent/'MOD4_AUTONOMY_SLEEP_20261003/PLAN_AND_HANDOFF.md'
 old=local.read_text(encoding='utf8')
 if marker not in old:local.write_text(old+'\n\n'+marker+'\n'+text,encoding='utf8')
 print('Verified actual5 stage handoff synchronized; no source/ledger mutation.')
finally:c.close()
