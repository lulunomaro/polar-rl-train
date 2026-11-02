"""Request original cooperative full-save/close at a quality evaluation boundary.
Only OWN eight role STOP files; no signals/hotpatch/Cwrite/lock/budget changes.
Fixed old8 owner will still initialize admitted pending roles, then stop before
first action if it reaches that callback. These are NOT trained or skillpassed.
"""
from pathlib import Path
import json,sys,shlex,time
R=Path(__file__).resolve().parent;out=R/'reports/QUALITY_BOUNDARY_ORIGINAL_COOPERATIVE_STOP_REQUEST_V1.json';guard=R/'QUALITY_BOUNDARY_ORIGINAL_STOP_REQUESTED_ONCE.json';assert not out.exists()and not guard.exists();d=json.loads((R/'A1_NATIVE_V6_ADMISSION2_ORIGINAL_OWNER_DISPATCH_ONCE.json').read_bytes());r=d.get('receipt',d);root=r['root'];pid=r['parent']['pid'];ticks=str(r['parent']['linux_start_ticks']);pre=json.loads((R/'reports/QUALITY_BOUNDARY_OWN_READONLY_PREFLIGHT_V1.json').read_bytes());assert pre['returncode']==0 and pre['receipt']['root']==root
code='''from pathlib import Path
import json,time,os,hashlib
root=Path(ROOT);pid=PID;ticks=TICKS;roles={'E3','W35','CURB_INDEPENDENT113','CURB_PROTECTED878','SLOPE135','SLOPE_INDEPENDENT50','E0','E2'}
def read(p):
 try:return json.loads(p.read_bytes())
 except FileNotFoundError:return None
p=Path('/proc')/str(pid);t=(p/'stat').read_text();f=t[t.rfind(')')+2:].split();assert f[0]not in('Z','X')and f[19]==ticks;assert str(root/'supermimic_original_owner_shared_app_close_candidate_v5.py')in(p/'cmdline').read_bytes().decode();assert hashlib.sha256((root/'supermimic_original_owner_shared_app_close_candidate_v5.py').read_bytes()).hexdigest()=='0f1618046d5751879f0ce40ff4b7424c83303ed1f61066521215c1d40eb76619'
c=read(Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json'));a=c['active_segment'];assert a and a['owner_parent_pid']==pid and a['owner_run_id']==root.name
assert read(root/'OWNER_EXIT_ACTUAL.json')is None and read(root/'OWNER_ORIGINAL_ERROR.json')is None
state=read(root/'OWNER_CURRENT.json');assert state['run_id']==root.name and {x['role']for x in state['workers'].values()}=={'E3','W35'}
entries=read(root/'OWNER_PLAN.json')['entries'];assert len(entries)==8 and {e['role']for e in entries}==roles
for e in entries:
 J=Path(e['job_root']);assert J.parent==root/'roles'and J.name==e['role'];g=read(J/'GO_PRODUCTION.json')
 if e['role']in('E3','W35'):
  assert g and g['run_id']==root.name and read(J/'production/FINAL.json')is None;complete=read(J/'production/latest_complete.json');assert complete and complete['full_new_model_critic_aux_optimizers_replay_RNG_hist_saved']and complete['teacher_unchanged']and complete['counts']['pi_bptt_optimizer_steps']>0;assert not any((J/'production'/n).exists()for n in('WORKER_ERROR.json','WORKER_ERROR_FALLBACK_V2.json','WORKER_PRESTART_ERROR_V2.json'))
 else:assert g is None
nonce=str(time.time_ns())
def atomic_new(p,value):
 assert p==root/'USER_QUALITY_BOUNDARY_COOPERATIVE_REQUEST_V1.json'or(p.parent.parent==root/'roles'and p.name=='STOP_AFTER_SAVE.json')
 if p.exists():return dict(path=str(p),written=False,preexisting_preserved=read(p))
 temp=p.with_name(p.name+'.quality_'+nonce+'.tmp');assert temp.parent.resolve()==p.parent.resolve()and not temp.exists();raw=json.dumps(value,indent=2).encode()
 with temp.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
 if p.exists():return dict(path=str(p),written=False,preexisting_preserved=read(p),own_unmoved_temporary=str(temp))
 assert temp.resolve().parent==p.resolve().parent;temp.replace(p);return dict(path=str(p),written=True,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())
intent=dict(kind='USER_QUALITY_PRIORITY_ORIGINAL_COOPERATIVE_SAVE_BOUNDARY_V1',epoch=time.time(),run_id=root.name,parent_pid=pid,parent_startticks=ticks,reason='User23:39 clarified actual skill pass improvement is primary; save current candidate and release through original close/wait/account before frozen assessment, not train-count completion',current_trained_roles=['E3','W35'],pending_policy='Original fixed8 owner has no skip API; pending roles still may initialize SDK/reset/teacher/learner, then original first before_action stops with full zero-update checkpoint if callback reached; actual evidence decides; not claimed trained/graded',source_worker_SHA='7c42986077de62278e33a49f560f22602c9ba4d4e69b058f5f5f8f0893c099c7',signals_sent=0,C_or_source_or_budget_changes=0,original_stop_then_fullsave_thenclose=True,not_yet_closed_or_cost_settled_or_resource_released=True,finite_execution_time_not_guaranteed=True)
first=atomic_new(root/'USER_QUALITY_BOUNDARY_COOPERATIVE_REQUEST_V1.json',intent);written=[]
# Stop pending roles before asking active pair to yield, avoiding blind additional
# training in the fixed old queue; no claim about unobserved subsequent startup.
order=[e for e in entries if e['role']not in('E3','W35')]+[e for e in entries if e['role']in('E3','W35')]
for e in order:
 J=Path(e['job_root']);v=dict(epoch=time.time(),reason=intent['reason'],complete_full_own_save_thenclose=True,quality_boundary_intent_path=str(root/'USER_QUALITY_BOUNDARY_COOPERATIVE_REQUEST_V1.json'),intended_role=e['role'],run_id=root.name);written.append(dict(role=e['role'],**atomic_new(J/'STOP_AFTER_SAVE.json',v)))
print(json.dumps(dict(kind='ORIGINAL_OWN_COOPERATIVE_STOP_FILES_REQUESTED_NOT_CLOSE_PROOF',epoch=time.time(),root=str(root),parent_pid=pid,intent=first,requests=written,signals_Cwrite_ledger_budget_hyperparameter_active_source_changes=0,no_frozen_skill_result_claim=True)))
'''.replace('ROOT',repr(root)).replace('PID',str(pid)).replace('TICKS',repr(ticks))
guard.write_text(json.dumps(dict(epoch=time.time(),root=root,parent_pid=pid,purpose='One original cooperative stop request; no signals, no blindly replay if partial'),indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=45);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();v=dict(root=root,epoch=time.time(),returncode=rc,stdout=text,stderr=err);out.write_text(json.dumps(v,indent=2),encoding='utf-8');assert rc==0,err;v['receipt']=json.loads(text);out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v['receipt'],indent=2))
finally:c.close()
