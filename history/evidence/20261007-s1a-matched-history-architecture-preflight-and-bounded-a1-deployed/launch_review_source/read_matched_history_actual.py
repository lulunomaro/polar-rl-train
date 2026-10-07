"""Read actual S1A owner/guardian/worker and its own receipt; never signals or writes ledger."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
ROOT=sys.argv[1] if len(sys.argv)>1 else '/home/egde/rl_candidates/MOD4_S1A_MATCHED_HISTORY_TRAINING_20261007'
MODULE='supervise_matched_history_launch_review_once' if 'LAUNCH_REVIEW' in ROOT else 'supervise_matched_history_once'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import sys,json,time
D=Path('ROOT');sys.path.insert(0,str(D))
import importlib;q=importlib.import_module('MODULE');q.verify()
rows={p.name:q.q.w.read(p) for p in (D/'reports').glob('*.json') if p.name in ('S1A_HISTORY_LAUNCHED.json','S1A_HISTORY_STATE.json','S1A_HISTORY_GUARDIAN_STARTED.json','S1A_HISTORY_ATTENTION.json','A1_COMPLETE_PPO_PREFLIGHT_PASSED.json','A2_COMPLETE_PPO_PREFLIGHT_PASSED.json','A1_MATCHED_LEARNING_COMPLETE.json','A2_MATCHED_LEARNING_COMPLETE.json','S1A_MATCHED_HISTORY_REVIEW_READY.json')}
owner=q.q.helpers.identity(rows['S1A_HISTORY_LAUNCHED.json']['owner']['pid'])
state=rows.get('S1A_HISTORY_STATE.json',{})
child=q.q.helpers.identity(state['child']['pid']) if state.get('child') else None
g=rows.get('S1A_HISTORY_GUARDIAN_STARTED.json')
actual=dict(epoch=time.time(),owner=owner,guardian=q.q.helpers.identity(g['pid']) if g else None,child=child,receipts=rows,
 budget=q.q.base.budget_state(),stage_used_seconds=q.stage_used(),source_count=len(q.q.w.read(D/'reports/SOURCE_FREEZE.json')['sha256']))
if state.get('active_log'):actual['log_tail']=Path(state['active_log']).read_text(errors='replace')[-3000:]
if state.get('own_run'):
 run=Path(state['own_run']);mf=q.q.w.read(run/'run_manifest.json')
 actual['manifest']=mf
 rf=q.q.w.read(run/'rolling_source_freeze.json');assert rf['sha256']==q.q.w.read(D/'reports/SOURCE_FREEZE.json')['sha256']
 for n,h in mf['src_sha256'].items():assert q.q.base.sha(run/'src_snapshot'/n)==h
 receipt=q.q.w.read(run/'latest_complete.json');actual['own_latest_complete']=receipt
 info,meta=q.fullsave(Path(receipt['checkpoint']));actual['own_full_save']=info;actual['architecture']=meta
print(json.dumps(actual))
'''.replace("Path('ROOT')","Path("+repr(ROOT)+")").replace("import_module('MODULE')","import_module("+repr(MODULE)+")")
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=40)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,err.decode()
 v=json.loads(raw);(R/'S1A_HISTORY_CURRENT_ACTUAL.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps({k:v.get(k) for k in ('epoch','owner','guardian','child','own_full_save','architecture','log_tail','source_count','stage_used_seconds')}))
 print(json.dumps(v['receipts'].get('S1A_HISTORY_ATTENTION.json')))
finally:c.close()
