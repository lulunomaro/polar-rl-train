from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from ninth_budget_ops import *
import traceback
REMOTE=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,time
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports');H=lambda b:hashlib.sha256(b).hexdigest();a=v['approval'];eid=EXTENSION_ID;locks=[]
def exclusive(p,j):
 with p.open('xb') as f:f.write(json.dumps(j,ensure_ascii=False,indent=2).encode());f.flush();os.fsync(f.fileno())
def cas(p,old,new):
 assert p.read_bytes()==old;tmp=p.with_name(p.name+'.ninth-'+str(time.time_ns()))
 with tmp.open('xb') as f:f.write(new);f.flush();os.fsync(f.fileno())
 assert p.read_bytes()==old;os.replace(tmp,p);fd=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
try:
 for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
  f=p.open('rb+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
 raw=C.read_bytes();c=json.loads(raw);assert H(raw)==v['before']['canonical_SHA'] and c['active_segment'] is None and c['remaining_training_seconds']==v['before']['remaining']
 owner=Path(v['closed']['owner_root']);node=Path(v['closed']['roots']['h1']);assert json.loads((owner/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled'] and json.loads((node/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited']
 assert not any(p.pid!=os.getpid() and any(any(x.startswith(str(root)+'/') for root in (owner,node)) for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
 protected_names=('MOD4_MOE_MASTER_PLAN.md','EXECUTION_TRACKS.json','MOD4_RM_TERRAIN_TRAINING_REVISION.json','MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_004.json','MOE_TERRAIN_SUBEXPERT_REVISION_004_APPROVAL.json');protected={n:(E/n).read_bytes() for n in protected_names};assert H(protected['MOD4_MOE_MASTER_PLAN.md'])==a['historical_master_sha256']
 names=('PLAN_APPROVAL.json','MOD4_MOE_EXECUTION_CONTRACT.json','MOE_PLAN_EXECUTION_CURRENT.json','LATEST_HANDOFF.md');old={n:(E/n).read_bytes() for n in names};ap=json.loads(old[names[0]]);ct=json.loads(old[names[1]]);current=json.loads(old[names[2]])
 assert ap['approved'] and not ap['S8_authorized'] and ap['authorized_budget_ceiling_seconds']==1548000 and ct['budget']['authorized_seconds']==1548000
 receipt=str(E/(eid+'_APPLIED.json'));after=extend_once(c,a,time.time(),receipt)
 exclusive(E/(eid+'_TRANSACTION_STARTED.json'),dict(epoch=time.time(),extension_id=eid,before_SHA=H(raw),two_original_fcntl=True,actual_closed63_allout=True))
 exclusive(E/(eid+'_APPROVAL.json'),a);ar=json.dumps(after,ensure_ascii=False,indent=2).encode();cas(C,raw,ar)
 proof=dict(epoch=time.time(),extension_id=eid,applied_once=True,added_seconds=720000,authorized_before=1548000,authorized_after=2268000,total_hours=630,charged_seconds=after['charged_training_seconds'],charged_unchanged=True,remaining_seconds=after['remaining_training_seconds'],active_segment=after['active_segment'],completed_segments_unchanged=True,completed_count=len(c['completed_segments']),completed_digest=H(json.dumps(c['completed_segments'],sort_keys=True).encode()),old_eight_extensions_unchanged=True,extension_records=9,before_SHA=H(raw),after_SHA=H(ar),canonical_path=str(C),original_two_fcntl_held=True,closed63_cost_already_settled=True,no_learning_launch=True,safety_seconds=64800,legacy_reserved_seconds=9912.860692501068)
 exclusive(E/(eid+'_APPLIED.json'),proof)
 amendment=dict(approved=True,authorization_basis='direct_human_user_message',human_message=a['human_message'],approval=a['central_approval_path'],extension_receipt=receipt,new_budget_seconds=720000,authorized_training_seconds=2268000,extensions=9,original_charged_history_unchanged=True,safety_seconds=64800,legacy_reserved_seconds=9912.860692501068,existing_H1_step270_and_E3_policy50_continuation_scope_only=True,no_new_S8_hardware_reward_or_input_scope=True)
 ap['authorized_budget_ceiling_seconds']=2268000;ap.setdefault('execution_amendments',{})[eid]=amendment
 ct['budget'].update(authorized_seconds=2268000,ledger_authorized_seconds_current=2268000,total_plan_authorized_seconds_after_pending_extension=2268000,extension_records_applied_once=9,latest_explicit_extension=amendment,current_remaining_seconds_snapshot=after['remaining_training_seconds'],current_snapshot_epoch=time.time());ct.setdefault('execution_amendments',{})[eid]=amendment;current.setdefault('budget_extension_amendments',{})[eid]=amendment
 for n,j in zip(names[:3],(ap,ct,current)):cas(E/n,old[n],json.dumps(j,ensure_ascii=False,indent=2).encode())
 note='\n\n2026-10-24 direct human: 预算增加200小时. USER_ADD200H_20261024_9TH applied once under both original fcntl at closed63 saved/allout boundary. Total2268000s630h/nine extensions; charged/completed history unchanged. Remaining '+str(after['remaining_training_seconds'])+'s pre-next-GO snapshot. Safety64800/Windows9400.860692501068/unknown512/next-pair7800 preserved. Existing H1 step270 and E3 policy50 continuation only.\n';cas(E/names[3],old[names[3]],old[names[3]]+note.encode())
 assert all((E/n).read_bytes()==b for n,b in protected.items()) and C.read_bytes()==ar
 sync=dict(epoch=time.time(),metadata_synced=True,extension_id=eid,authorized_total=2268000,extensions=9,protected_bytes_unchanged=True,resulting_metadata_SHA={n:H((E/n).read_bytes()) for n in names},historical_metadata_before_SHA={n:H(b) for n,b in old.items()});exclusive(E/(eid+'_METADATA_SYNCED.json'),sync)
 print(json.dumps(dict(passed=True,budget=proof,metadata=sync,transaction_texts={n:(E/n).read_text('utf8') for n in (eid+'_TRANSACTION_STARTED.json',eid+'_APPROVAL.json',eid+'_APPLIED.json',eid+'_METADATA_SYNCED.json')})))
finally:
 for f in reversed(locks):f.close()
'''
try:
 cpu=json.loads((R/'NINTH_EXTENSION_CONTRACT_CPU_ACTUAL.json').read_bytes());assert cpu['passed']
 put('APPLY_STARTED.json',dict(epoch=time.time()));q=closed();c=d.t.connect()
 try:v=d.code(c,d.t.PY,(B/'budget_ninth_contract.py').read_text('utf8')+REMOTE,dict(approval=json.loads((R/'DIRECT_HUMAN_APPROVAL.json').read_bytes()),before=json.loads((R/'ORIGINAL_BUDGET_NINTH_BEFORE_ACTUAL.json').read_bytes())['source210'],closed=q),timeout=90)
 finally:c.close()
 put('NINTH_BUDGET_APPLIED_AND_METADATA_SYNCED_ACTUAL.json',v);print(json.dumps(dict(passed=v['passed'],budget=v['budget'],metadata=v['metadata'])))
except BaseException:
 put('APPLY_ORIGINAL_ERROR.json',dict(error=traceback.format_exc(),do_not_replay=True));raise
