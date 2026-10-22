"""Retire only the exact owned READY admission node, never a learning worker."""
from pathlib import Path
import json,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent.parent
N=B.parent/'H1_STEP270_E3_REWARD_PATH_PAIR_V17_20261022'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
import deploy_two50_reconciled_original_writer_once as d
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE=r'''
from pathlib import Path
import json,os,psutil,signal,time,hashlib
q=v['q'];root=Path(q['roots']['h1']);owner=Path(q['owner_root']);read=lambda p:json.loads(p.read_bytes())
co=read(owner/'OWNER_CURRENT.json');n=read(root/'NODE_CURRENT.json');ident=read(root/'NODE_IDENTITY.json')
assert time.time()-co['epoch']<15 and time.time()-n['epoch']<15
assert 'h1' not in co['go'] and set(co['go'])=={'recovery'}
assert n['row']['phase']=='ready' and n['row']['worker'] is None and n['row']['latest_save'] is None
assert not (root/'GO_PRODUCTION.json').exists() and not (root/'job0/GO_PRODUCTION.json').exists()
assert not (root/'job0/production_STARTED_ACTUAL.json').exists() and not (root/'job0/production').exists()
p=psutil.Process(q['nodes']['h1']['detached_pid'])
assert p.pid==ident['pid'] and abs(p.create_time()-ident['creation'])<.01
assert p.exe()=='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python3.12'
assert p.cmdline()==ident['argv'] and str(root/'three_slot_finite_node_v1.py') in p.cmdline()
assert not p.children(recursive=True)
until=time.monotonic()+9
while (Path('/proc')/str(p.pid)/'wchan').read_text().strip() not in ('hrtimer_nanosleep','do_nanosleep'):
 assert time.monotonic()<until,'No safe sleeping boundary; no signal sent'
 time.sleep(.02)
before=dict(epoch=time.time(),pid=p.pid,exe=p.exe(),argv=p.cmdline(),creation=p.create_time(),children=[],H1_GO_absent=True,H1_worker_absent=True,E3_original_GO=co['go']['recovery'],signal='SIGINT',purpose='Unstarted READY admission schema failure; original node BaseException/finally emits genuine terminal and releases its own lease; no owner/learning-worker signal')
intent=root/'UNSTARTED_ADMISSION_RETIRE_INTENT_ACTUAL.json'
with intent.open('x') as f:json.dump(before,f,indent=2)
os.kill(p.pid,signal.SIGINT)
until=time.monotonic()+55
while not (root/'NODE_EXIT_ACTUAL.json').exists():
 assert time.monotonic()<until,'Single SIGINT did not complete original finally; do not retry this once'
 time.sleep(.2)
e=read(root/'NODE_EXIT_ACTUAL.json');t=read(root/'NODE_TERMINAL_ACTUAL.json');co=read(owner/'OWNER_CURRENT.json')
assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and e['terminal_received_by_source']
assert t['row']['terminal_all_own_children_waited'] and t['row']['original_error'] and t['row']['worker'] is None
assert 'h1' not in co['go'] and set(co['go'])=={'recovery'}
texts={str(x):x.read_text('utf8') for x in (root/'NODE_ORIGINAL_ERROR.json',root/'NODE_TERMINAL_ACTUAL.json',root/'NODE_EXIT_ACTUAL.json',intent)}
print(json.dumps(dict(epoch=time.time(),passed=True,intent=before,node_exit=e,node_terminal=t,current_owner=co,texts=texts,no_H1_learning_GO_or_cost_interval=True,no_owner_E3_worker_signal_or_account_write=True)))
'''
try:
 assert not (R/'UNSTARTED_H1_ADMISSION_RETIRE_STARTED_ACTUAL.json').exists()
 put('UNSTARTED_H1_ADMISSION_RETIRE_STARTED_ACTUAL.json',dict(epoch=time.time(),one_signal_only_no_learning_worker=True))
 q=json.loads((N/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes());c=d.t.connect()
 try:v=d.code(c,d.t.PY,CODE,dict(q=q),timeout=75)
 finally:c.close()
 put('UNSTARTED_H1_ADMISSION_ORIGINAL_FINALLY_TERMINAL_ACTUAL.json',v)
 print(json.dumps(dict(passed=v['passed'],H1_unstarted_admission_terminal=True,E3_original_GO_unaffected=True)))
except BaseException:
 put('UNSTARTED_ADMISSION_RETIRE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
