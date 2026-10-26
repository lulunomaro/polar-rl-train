from pathlib import Path
import hashlib,importlib.util,json,time,traceback
J=Path(__file__).resolve().parent;T=J.parent;W=T.parent;N=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M_20261026';R=N/'reports';P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026'
AUTH_SHA='fc029e1ec254bf64b86a0428be6695a564c23fbc67794daaea0b13b6adcd04cf'
STATE='/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026'
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
CODE=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,time
B=Path(v['state']);owned=Path('/home/lc01/Zonglin Li/zonglin2/state');assert B.parent==owned and B.name=='mod4_single_canonical_authority_20261026' and not B.exists()
authraw=v['authraw'].encode('utf8');assert hashlib.sha256(authraw).hexdigest()==v['authSHA'];auth=json.loads(authraw)
assert auth['approved'] and auth['temporary_budget_mode']=='unlimited_until_single4090_returns' and auth['human_verbatim']=='这段时间账本直接给你无限制，单主机回来后再加限制'
assert auth['old210_Linux_canonical_retired_from_authority'] and auth['old210_Linux_must_not_resume_a_separate_writer'] and auth['active_spending_cap_seconds'] is None
proof=v['proof'];assert proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out'] and proof['all_original_private_shared_locks_free'] and proof['remaining_actual_snapshot']==595256.8240613937
assert abs(proof['actual_cost_sumonce']-10943.796510219574)<1e-5 and set(proof['models'])=={'h1','e2','recovery'}
sdk=v['sdk'];assert sdk['actual_finite_returned'] and sdk['target_source_CPU_passed'] and not sdk['GO'] and not sdk['owner_launched'] and not sdk['node_launched']
for key,root in sdk['roots'].items():
 root=Path(root);assert root.is_relative_to(owned.parent/'tasks') and root.is_dir()
 assert not any((root/name).exists() for name in ('NODE_IDENTITY.json','GO_PRODUCTION.json','OWNER_IDENTITY.json'))
assert not any(any(a.startswith(root+'/') for root in sdk['roots'].values()) for p in psutil.process_iter(['cmdline']) for a in (p.info['cmdline'] or []))
held=[]
try:
 for key in ('e2','recovery'):
  f=Path(sdk['specs'][key]['private_lock']).open('rb+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);held.append(f)
 f=(owned/'finite_environment_validation.lock').open('rb+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);held.append(f)
 B.mkdir(mode=0o700)
 newlocks=[]
 for name in ('native_floor_supervisor.lock','autonomy_controller.lock'):
  p=B/name;f=p.open('xb+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);held.append(f);newlocks.append(str(p))
 assert auth['new_canonical_path']==str(B/'TRAINING_BUDGET_10H.json') and auth['new_owner_locks']==newlocks
 epoch=time.time();oldsha='fa47cf989898d9c771f35dcaa1e25330456694fda044502aaf82a5887b205bb1';authority_id='MOD4_SINGLE_CANONICAL_AUTHORITY_72_'+str(time.time_ns())
 c=dict(schema='mod4.single_writer_authority72.carry_forward_temporary_unlimited.v1',authority_generation='MOD4_SINGLE_WRITER72_20261026',authority_id=authority_id,budget_mode='temporary_unlimited_until_single4090_returns',active_spending_cap_seconds=None,remaining_is_tracking_not_launch_limit=True,authorized_training_seconds=2268000,charged_training_seconds=1672743.1759386063,remaining_training_seconds=595256.8240613937,active_segment=None,completed_segments=[],completed_segments_scope='only_after_this_authority_handoff',historical_budget_extension_count=9,new_authority_budget_extensions=[],historical_charged_training_seconds=1672743.1759386063,historical_remaining_training_seconds=595256.8240613937,historical_records_not_reconstructed=True,old_authority_retired=True,old_canonical_path='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json',old_canonical_last_verified_SHA=oldsha,history_Git_main='bc208d47c305f7dd25b2ee5863d07281909010cc',latest_closed_source_window='83B',latest_original_closed_fee=10943.796510219574,authorization_SHA=v['authSHA'],activated_epoch=epoch,finite_limits_resume_trigger='single4090 returns; root restores finite-limit admission before further GO; never reactivate retired210 ledger',source_proof_SHA=v['proofSHA'],original_legacy_pending_seconds=9400.860692501068,unknown_pending_seconds=512,safety_tracking_seconds=64800,lifecycle_seconds=3900,save_seconds=3600,exit_headroom_seconds=300,actual_cost_contract='one writer; independent actualGO to actualterminal sumonce; actual overcap fully charged with duration flag false; no refund roundoff idle fee or fabricated grant')
 assert abs(c['authorized_training_seconds']-c['charged_training_seconds']-c['remaining_training_seconds'])<1e-5
 def atomic(name,raw):
  p=B/name;assert not p.exists();tmp=p.with_suffix(p.suffix+'.partial')
  with tmp.open('xb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
  tmp.replace(p)
 raw=(json.dumps(c,ensure_ascii=False,indent=2)+'\n').encode('utf8');atomic('HUMAN_TEMPORARY_UNLIMITED_AUTHORIZATION_ACTUAL.json',authraw);atomic('TRAINING_BUDGET_10H.json',raw)
 result=dict(schema='mod4.single_writer72.authority_handoff.v1',authority_generation='MOD4_SINGLE_WRITER72_20261026',authority_host='72',owner_locks=newlocks,canonical_copied=False,historical_records_reconstructed=False,old_canonical_SHA256=oldsha,known_last_settled_run_id='THREE4090_EXPERT_ORIGINAL_1792994651814636100',latest_original_owner_allout=True,latest_original_active_segment=None,authorization_file_SHA256=v['authSHA'],seed_canonical_SHA256=hashlib.sha256(raw).hexdigest(),epoch=epoch,passed=True,approved=True,activated=True,authority_activated=True,authority_id=authority_id,single_writer_host72=True,old_authority_retired=True,old210_Linux_authority_retired=True,canonical_path=str(B/'TRAINING_BUDGET_10H.json'),canonical_seed_SHA=hashlib.sha256(raw).hexdigest(),locks=newlocks,human_authorization_SHA=v['authSHA'],budget_mode=c['budget_mode'],active_spending_cap_seconds=None,source_remaining_tracking_snapshot=595256.8240613937,source_charged_tracking_snapshot=1672743.1759386063,source_closed_window='83B',old_canonical_last_verified_SHA=oldsha,old_history_not_reconstructed=True,no_byte_exact_old_ledger_migration_claim=True,no_old83B_fee_recharge=True,canonical_active_None=True,no_owner_node_or_GO=True,actual_source_host_Linux_unreachable_due_to_human_Windows_change=True,source83B_allout_is_historical_verified_evidence=True,target85_no_nodes_or_GO_currently_verified=True,target_original_private_shared_locks_and_new_owner_locks_acquired=True,all_actual_cost_still_recorded=True,limits_restore_when_single4090_returns=True)
 atomic('AUTHORITY_HANDOFF_ACTUAL.json',(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps(result))
finally:
 for f in reversed(held):f.close()
'''
def main():
 authpath=R/'HUMAN_SINGLE_WRITER72_TEMPORARY_UNLIMITED_AUTHORIZATION_ACTUAL.json';raw=authpath.read_bytes();assert hashlib.sha256(raw).hexdigest()==AUTH_SHA
 proofpath=P/'reports/THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json';proofraw=proofpath.read_bytes();proof=json.loads(proofraw)
 sdk=json.loads((T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_RESOURCE_V85_20261026/reports/V85_ONLY72_INSTALLED_SOURCE_SDK_NATIVE_CPU_FINITE_RETURNED_ACTUAL.json').read_bytes())
 put('SINGLE_WRITER72_TEMP_UNLIMITED_INITIALIZATION_STARTED_ACTUAL.json',dict(epoch=time.time(),human_authorization_SHA=AUTH_SHA,no_budget_amount_gate_during_explicit_temporary_override=True,no_old_canonical_copy=True,no_owner_or_GO=True))
 sp=importlib.util.spec_from_file_location('defs',T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83_20261026/relocate_minimal_closed81O_82Q_NPZ_for83_TLS_V5_unused_once.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);d=m.d
 ms=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');mem=importlib.util.module_from_spec(ms);ms.loader.exec_module(mem);secret=mem.recover();c=None
 try:
  c=d.connect72(secret);secret=None;result=d.code(c,d.PY72,CODE,dict(state=STATE,authraw=raw.decode('utf8'),authSHA=AUTH_SHA,proof=proof,proofSHA=hashlib.sha256(proofraw).hexdigest(),sdk=sdk),timeout=90)
  put('SINGLE_WRITER72_TEMP_UNLIMITED_INITIALIZATION_RETURNED_ACTUAL.json',result);print(json.dumps(result))
 except BaseException:
  put('SINGLE_WRITER72_TEMP_UNLIMITED_INITIALIZATION_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_same_once_retry_or_new_authority_path=True,no_assume_partial_activation_passed=True));raise
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':main()
