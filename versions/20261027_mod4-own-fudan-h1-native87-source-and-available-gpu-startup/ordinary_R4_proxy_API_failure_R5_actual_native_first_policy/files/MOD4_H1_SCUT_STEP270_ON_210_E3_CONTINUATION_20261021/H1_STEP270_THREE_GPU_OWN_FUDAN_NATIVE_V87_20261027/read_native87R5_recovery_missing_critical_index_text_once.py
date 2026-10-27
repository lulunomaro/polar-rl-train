"""One missing recovery critical-index text after first-positive publication race."""
from pathlib import Path
import sys,json,time,hashlib,importlib.util,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def main():
 p=R/'AVAILABLE_TWO_NATIVE87R5_FIRST_GO_ACTUAL_NEW_PREUPDATE_PI_RETURNED_ACTUAL.json';old=json.loads(p.read_bytes());t=old['targets']['recovery'];first=t['first_positive'];idx=t['trace_index']
 assert set(old['errors'])=={'recovery'} and 'same actual preupdate source/control receipt' in old['errors']['recovery']
 assert t['passed_live_identity'] and t['status']=='exact_own_live_identity' and not t['reader_errors']
 assert first['policy_updates']==6 and first['before_control']==240 and idx['controls']==240 and max(x['before_control'] for x in idx['preupdate_full_sources'])==216
 root=Path(t['GO']['run_id']) # only validate scalar below, never filesystem access
 q=json.loads((R/'AVAILABLE_TWO_NATIVE87R5_ACTUAL_OWNER_NODES_DETACHED.json').read_bytes());assert q['run_id']==t['GO']['run_id']
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('native87R5_recovery_index_missing_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);secret=m.recover();c=None
 try:
  c=d.connect72(secret)
  value=d.code(c,d.PY72,"""from pathlib import Path
import json,time
B=Path(v['root']);assert str(B)=='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_own_fudan_native_2610v87r5/recovery'
p=B/'job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json'
assert p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(B.resolve()) and p.stat().st_size<8000000
raw=p.read_bytes();index=json.loads(raw)
print(json.dumps(dict(epoch=time.time(),path=str(p),bytes=len(raw),index=index,no_model_or_GPU_or_process_or_account_read=True)))""",dict(root=q['roots']['recovery']),timeout=45)
  matches=[x for x in value['index']['preupdate_full_sources'] if x['path']==first['path'] and x['SHA']==first['SHA'] and x['bytes']==first['bytes'] and x['before_control']==first['before_control']]
  assert len(matches)==1 and value['index']['controls']>=first['before_control']
  value.update(passed=True,actual_finite_returned=True,original_first_observer_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),original_first_false_preserved=True,original_failure='initial index publication preceded insertion of the new preupdate fullsource10; not a training failure',first_positive_previously_collected=first,match=matches[0],no_repeat_first_metadata_or_PT_or_raw_or_actor_or_GPU=True)
  with (R/'R5_RECOVERY_MISSING_CRITICAL_INDEX_CORROBORATION_RETURNED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
  print(json.dumps(dict(passed=True,missing_index_single_text_read=True,first_policy_updates=first['policy_updates'],first_before_control=first['before_control'],original_false_preserved=True)))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('R5_RECOVERY_MISSING_INDEX_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc()),f,indent=2)
  raise
