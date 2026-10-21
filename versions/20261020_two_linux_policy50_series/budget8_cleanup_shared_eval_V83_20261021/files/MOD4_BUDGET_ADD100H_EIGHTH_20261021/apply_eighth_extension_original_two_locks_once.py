from pathlib import Path
import importlib.util,json,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent
s=importlib.util.spec_from_file_location('strict210',W/'MOD4_TWO_LINUX_POLICY50_COHORT_49_20261021/strict_original_Linux_transport_memory.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
REMOTE=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,time
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports');H=lambda b:hashlib.sha256(b).hexdigest();a=v['approval'];eid=EXTENSION_ID;locks=[]
def exclusive(p,j):
 with p.open('xb') as f:f.write(json.dumps(j,ensure_ascii=False,indent=2).encode());f.flush();os.fsync(f.fileno())
def cas(p,old,new):
 assert p.read_bytes()==old
 tmp=p.with_name(p.name+'.eighth-'+str(time.time_ns()))
 with tmp.open('xb') as f:f.write(new);f.flush();os.fsync(f.fileno())
 assert p.read_bytes()==old;os.replace(tmp,p);fd=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
try:
 for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
  f=p.open('rb+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
 raw=C.read_bytes();c=json.loads(raw);assert H(raw)==v['before']['canonical_SHA'] and c['active_segment'] is None
 root=Path('/mnt/mod4_linux_durable_20261013/T2policy50_2010v48');assert json.loads((root/'owner/OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled'];assert not any(p.pid!=os.getpid() and any(x.startswith(str(root)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
 live=[]
 for p in psutil.process_iter(['pid','cmdline']):
  if p.pid==os.getpid():continue
  scripts=[x for x in p.info['cmdline'] or [] if x.endswith('.py') and ('/T2policy50_' in x or '/T3sf17_' in x)]
  if any(Path(x).name in ('three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py','native_admission_worker.py','recovery_worker.py') for x in scripts):live.append(p.pid)
 assert not live
 protected_names=('MOD4_MOE_MASTER_PLAN.md','EXECUTION_TRACKS.json','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json','MOE_TERRAIN_SUBEXPERT_REVISION_004_APPROVAL.json');protected={n:(E/n).read_bytes() for n in protected_names};assert H(protected['MOD4_MOE_MASTER_PLAN.md'])==a['historical_master_sha256']
 names=('PLAN_APPROVAL.json','MOD4_MOE_EXECUTION_CONTRACT.json','MOE_PLAN_EXECUTION_CURRENT.json','LATEST_HANDOFF.md');old={n:(E/n).read_bytes() for n in names};ap=json.loads(old[names[0]]);ct=json.loads(old[names[1]]);current=json.loads(old[names[2]]);assert ap['approved'] and not ap['S8_authorized'] and ap['authorized_budget_ceiling_seconds']==1188000 and ct['budget']['authorized_seconds']==1188000
 receipt=str(E/(eid+'_APPLIED.json'));after=extend_once(c,a,time.time(),receipt)
 exclusive(E/(eid+'_TRANSACTION_STARTED.json'),dict(epoch=time.time(),extension_id=eid,before_SHA=H(raw),two_original_fcntl=True,actual_all210out=True))
 exclusive(E/(eid+'_APPROVAL.json'),a)
 ar=json.dumps(after,ensure_ascii=False,indent=2).encode();cas(C,raw,ar)
 proof=dict(epoch=time.time(),extension_id=eid,applied_once=True,added_seconds=360000,authorized_before=1188000,authorized_after=1548000,total_hours=430,charged_seconds=after['charged_training_seconds'],charged_unchanged=True,remaining_seconds=after['remaining_training_seconds'],remaining_hours_snapshot=after['remaining_training_seconds']/3600,active_segment=after['active_segment'],completed_segments_unchanged=True,completed_count=len(c['completed_segments']),completed_digest=H(json.dumps(c['completed_segments'],sort_keys=True).encode()),old_seven_extensions_unchanged=True,extension_records=8,before_SHA=H(raw),after_SHA=H(ar),canonical_path=str(C),original_two_fcntl_held=True,cohort48_cost_already_settled=True,no_learning_launch=True,safety_seconds=64800,legacy_reserved_seconds=9912.860692501068)
 exclusive(E/(eid+'_APPLIED.json'),proof)
 amendment=dict(approved=True,authorization_basis='direct_human_user_message',human_message=a['human_message'],approval=a['central_approval_path'],extension_receipt=receipt,new_budget_seconds=360000,authorized_training_seconds=1548000,extensions=8,original_charged_history_unchanged=True,safety_seconds=64800,legacy_reserved_seconds=9912.860692501068,existing_two_slot_50Hz_continuation_scope_only=True,no_new_S8_or_hardware_or_reward_scope=True)
 ap['authorized_budget_ceiling_seconds']=1548000;ap.setdefault('execution_amendments',{})[eid]=amendment
 ct['budget'].update(authorized_seconds=1548000,ledger_authorized_seconds_current=1548000,total_plan_authorized_seconds_after_pending_extension=1548000,extension_records_applied_once=8,latest_explicit_extension=amendment,current_remaining_seconds_snapshot=after['remaining_training_seconds'],current_snapshot_epoch=time.time());ct.setdefault('execution_amendments',{})[eid]=amendment
 current.setdefault('budget_extension_amendments',{})[eid]=amendment
 for n,j in zip(names[:3],(ap,ct,current)):cas(E/n,old[n],json.dumps(j,ensure_ascii=False,indent=2).encode())
 note='\n\n2026-10-21 explicit human: 余额增加100小时. USER_ADD100H_20261021_8TH applied once under both original fcntl at actual saved/all-out boundary. Total1548000s430h/eight extensions; charged/completed history unchanged. Remaining '+str(after['remaining_training_seconds'])+'s pre-next-GO snapshot. Original safety64800s and legacy9912.860692501068s preserved. Existing E2/E3 policy50 two-slot continuation only; no new recipe/S8/hardware authorization.\n';cas(E/names[3],old[names[3]],old[names[3]]+note.encode())
 assert all((E/n).read_bytes()==b for n,b in protected.items()) and C.read_bytes()==ar
 sync=dict(epoch=time.time(),metadata_synced=True,extension_id=eid,authorized_total=1548000,extensions=8,protected_bytes_unchanged=True,resulting_metadata_SHA={n:H((E/n).read_bytes()) for n in names},historical_metadata_before_SHA={n:H(b) for n,b in old.items()})
 exclusive(E/(eid+'_METADATA_SYNCED.json'),sync);print(json.dumps(dict(passed=True,budget=proof,metadata=sync)))
finally:
 for f in reversed(locks):f.close()
'''
try:
 assert json.loads((R/'EIGHTH_EXTENSION_CONTRACT_CPU_ACTUAL.json').read_bytes())['passed']
 with (R/'APPLY_STARTED.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time()),f)
 c=t.connect()
 try:v=t.code(c,(B/'budget_eighth_contract.py').read_text('utf8')+REMOTE,dict(approval=json.loads((R/'DIRECT_HUMAN_APPROVAL.json').read_bytes()),before=json.loads((R/'ORIGINAL_BUDGET_EIGHTH_BEFORE_ACTUAL.json').read_bytes())),timeout=90)
 finally:c.close()
 with (R/'EIGHTH_BUDGET_APPLIED_AND_METADATA_SYNCED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
 print(json.dumps(v))
except BaseException:
 with (R/'APPLY_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),do_not_replay=True),f)
 raise
