"""Read only new root424 process/state/log/save/budget; future receipts may be absent."""
from direction_io import *
from prepare_direction140_decision_and_exposure_continuation_once import ROOT

def main():
 n,w=io.connect_both()
 try:
  v=io.linux_json(n,r'''from pathlib import Path
import json,time,hashlib
D=Path(NEW_ROOT_TOKEN);R=D/'reports';B=Path(BUDGET_PATH_TOKEN);j=lambda p:json.loads(p.read_bytes())
def ident(pid):
 p=Path('/proc')/str(pid)
 if not p.exists():return None
 try:
  z=(p/'stat').read_text().split(') ',1)[1].split();return dict(pid=pid,state=z[0],start_ticks=int(z[19]),argv=(p/'cmdline').read_bytes().decode(errors='replace').split('\0'),cwd=str((p/'cwd').resolve()))
 except OSError:return None
st=j(R/'E1_STATE.json') if (R/'E1_STATE.json').exists() else None
reports={}
for name in ('E1_DISPATCH_STARTED.json','E1_GUARDIAN_STARTED.json','E1_ATTENTION.json','E1_ACTIVE_HEALTH.json','E1_CURRENT_SAVE.json','e1_CURB20_direction_exposure_matched_observation_PASSED.json','E1_CURB_DIRECTION_ASYNC_PUBLISHED.json','E1_REVIEW_READY.json'):
 p=R/name;reports[name]=j(p) if p.exists() else None
logs={str(p):p.read_text(errors='replace')[-6000:] for p in D.glob('*.log')}
b=j(B);loc=(st or {}).get('child');owner=(st or {}).get('owner') or j(R/'MATCHED_DISPATCH_ACTUAL_RECEIPT.json')['owner']
v=dict(epoch=time.time(),root=str(D),source_count=len(j(R/'SOURCE_FREEZE.json')['sha256']),state=st,actual_owner=ident(owner['pid']),actual_child=ident(loc['pid']) if loc else None,reports=reports,log_tails=logs,budget=dict(authorized_seconds=b['authorized_training_seconds'],extensions=len(b['budget_extensions']),charged_seconds=b['charged_training_seconds'],idle_remaining_snapshot=b['authorized_training_seconds']-b['charged_training_seconds'],active_segment=b['active_segment'],sha256=hashlib.sha256(B.read_bytes()).hexdigest()),no_write_or_signal=True)
print(json.dumps(v))
'''.replace('NEW_ROOT_TOKEN',repr(ROOT)).replace('BUDGET_PATH_TOKEN',repr(io.B)))
  p=save('EXPOSURE_MATCHED_ACTUAL_'+str(time.time_ns())+'.json',v)
  print(json.dumps(dict(report=str(p),state=v['state'],actual_owner=v['actual_owner'],actual_child=v['actual_child'],attention=v['reports']['E1_ATTENTION.json'],health=v['reports']['E1_ACTIVE_HEALTH.json'],budget=v['budget'],log_tails=v['log_tails']),ensure_ascii=True))
 finally:io.cleanup(n,w)

if __name__=='__main__':main()
