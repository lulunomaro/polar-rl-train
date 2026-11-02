"""Read ONLY own native identities/producer saves and original C ownership.
New quality-boundary purpose: no model stat/hash/decode, signal, lock or mutation.
"""
from pathlib import Path
import json,sys,shlex
R=Path(__file__).resolve().parent;out=R/'reports/QUALITY_BOUNDARY_OWN_READONLY_PREFLIGHT_V1.json';assert not out.exists();d=json.loads((R/'A1_NATIVE_V6_ADMISSION2_ORIGINAL_OWNER_DISPATCH_ONCE.json').read_bytes());receipt=d.get('receipt',d);root=receipt['root'];pid=receipt['parent']['pid'];ticks=str(receipt['parent']['linux_start_ticks']);assert root.endswith('MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000')
code='''from pathlib import Path
import json,time,hashlib
root=Path(ROOT);pid=PID;ticks=TICKS
def read(p):
 try:return json.loads(p.read_bytes())
 except FileNotFoundError:return None
p=Path('/proc')/str(pid);raw=(p/'stat').read_text();f=raw[raw.rfind(')')+2:].split();alive=f[0]not in('Z','X')and f[19]==ticks;assert alive
state=read(root/'OWNER_CURRENT.json');started=read(root/'OWNER_STARTED.json');c=read(Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'));a=c['active_segment'];assert a and a['owner_parent_pid']==pid and a['owner_run_id']==root.name and state['run_id']==root.name and started['pid']==pid
rows=[]
for e in read(root/'OWNER_PLAN.json')['entries']:
 J=Path(e['job_root']);assert J.parent==root/'roles'and J.name==e['role'];O=J/'production';rows.append(dict(role=e['role'],job_root=str(J),GO=read(J/'GO_PRODUCTION.json'),identity=read(J/'WORKER_IDENTITY_ACTUAL.json'),latest_complete=read(O/'latest_complete.json'),final=read(O/'FINAL.json'),preexisting_stop=read(J/'STOP_AFTER_SAVE.json'),errors={n:v for n in('WORKER_ERROR.json','WORKER_ERROR_FALLBACK_V2.json','WORKER_PRESTART_ERROR_V2.json')if(v:=read(O/n))is not None}))
owner=root/'supermimic_original_owner_shared_app_close_candidate_v5.py';b=owner.read_bytes();assert hashlib.sha256(b).hexdigest()=='0f1618046d5751879f0ce40ff4b7424c83303ed1f61066521215c1d40eb76619'
print(json.dumps(dict(kind='OWN_NATIVE_QUALITY_BOUNDARY_READONLY_PREFLIGHT',epoch=time.time(),root=str(root),parent=dict(pid=pid,startticks=ticks,state=f[0],cmdline=(p/'cmdline').read_bytes().replace(bytes([0]),b' ').decode(),source_SHA=hashlib.sha256(b).hexdigest()),parent_current=state,parent_error=read(root/'OWNER_ORIGINAL_ERROR.json'),parent_exit=read(root/'OWNER_EXIT_ACTUAL.json'),canonical_active_binding={k:a[k]for k in('owner_parent_pid','owner_run_id','started_epoch')},canonical_remaining_observation_only=c['remaining_training_seconds'],rows=rows,signals_Cwrite_locks_SDK_model_raw_operations=0)))
'''.replace('ROOT',repr(root)).replace('PID',str(pid)).replace('TICKS',repr(ticks))
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=45);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();value=dict(returncode=rc,stdout=text,stderr=err);out.write_text(json.dumps(value,indent=2),encoding='utf-8');assert rc==0,err;v=json.loads(text);value['receipt']=v;out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(dict(path=str(out),epoch=v['epoch'],parent=v['parent'],roles=[dict(role=x['role'],GO=x['GO']is not None,complete_count=None if not x['latest_complete']else x['latest_complete']['counts']['pi_bptt_optimizer_steps'],errors=bool(x['errors']),final=x['final']is not None)for x in v['rows']]),indent=2))
finally:c.close()
