"""Repair missing signed alias fields, without changing any worker/model guard."""
from pathlib import Path
import copy,hashlib,importlib.util,json,sys,time
F=Path(__file__).resolve().parent;L=F.parent;T=L.parent
N=T/'MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V95_20261028'
def read(p):return json.loads(p.read_bytes())
def put(n,v):
 with (F/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 old=N/'controllers/h1_next72_protocol_actual95_v2.py';s=old.read_text('utf8')
 needle="require(s.get('key')==KEY and s.get('nativeflat90') is True,'one actual logical h1 flat slot')"
 assert s.count(needle)==1
 s=s.replace(needle,needle+"\n require(s.get('logical_slot')==KEY and s.get('canonical_worker_key')=='h1','explicit signed logical slot and native worker ABI')",1)
 needle="fields=('task_focused_real_replay','native_learning_seed',"
 assert s.count(needle)==1;s=s.replace(needle,"fields=('logical_slot','canonical_worker_key','task_focused_real_replay','native_learning_seed',",1)
 selected=F/'h1_next72_protocol_signed_alias96_candidate.py'
 with selected.open('x',encoding='utf8') as f:f.write(s)
 task=read(N/'payload/job0/TASK.json')
 directory=L/'TWO95_EARLY_TERMINAL_READONLY_FORENSIC_SOURCE_V1/reports/complete_original_UTF8_texts'
 original_go=[read(p) for p in directory.glob('*_GO_PRODUCTION.json') if read(p).get('source_SHA')==task['source_SHA']]
 assert original_go and all(x==original_go[0] for x in original_go)
 original_go=original_go[0]
 sys.path[:0]=[str(N/'payload'),str(N/'payload/source')]
 from native_flat90_source_guard_v1 import validate_task_go
 try:validate_task_go(task,original_go,original_go['payload_manifest_SHA'])
 except ValueError as e:assert str(e)=='exact physical target alias and native worker ABI'
 else:raise AssertionError('old actual GO unexpectedly admitted')
 corrected=copy.deepcopy(original_go)
 corrected.update(logical_slot='h1',canonical_worker_key='h1')
 validate_task_go(task,corrected,corrected['payload_manifest_SHA'])
 for key in ('logical_slot','canonical_worker_key'):
  wrong=copy.deepcopy(corrected);wrong[key]='h1_210'
  try:validate_task_go(task,wrong,wrong['payload_manifest_SHA'])
  except ValueError:pass
  else:raise AssertionError('wrong alias accepted')
 actual=read(L/'THREE95_H1_E3_mixed72_source_v1/reports/TWO95_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json')
 spec=copy.deepcopy(actual['experts']['h1']);spec.update(logical_slot='h1',canonical_worker_key='h1')
 p=module('signed_alias96_protocol_source',selected);p.validate_spec(spec)
 fields=p.flat_go_fields(spec)
 assert fields['logical_slot']=='h1' and fields['canonical_worker_key']=='h1'
 assert all(fields[k]==corrected[k] for k in fields)
 put('SOURCE_CPU_ACTUAL.json',dict(passed=True,epoch=time.time(),source_only=True,
  actual95_original_GO_missing_fields=[k for k in ('logical_slot','canonical_worker_key') if k not in original_go],
  original_actual_GO_rejected_by_unchanged_guard=True,only_two_field_GO_delta_admitted=True,
  wrong_alias_negatives_rejected=True,selected_protocol=str(selected),selected_protocol_SHA=H(selected),
  original_protocol=str(old),original_protocol_SHA=H(old),exact95_worker_and_payload_unchanged=True,
  new96_namespace_and_same_source_CPU_reuse_still_require_explicit_sealing=True,
  no_saved_model_load_hash_forward_GPU_SDK_physics_remote_or_account=True))
 rows=[dict(path=p.name,bytes=p.stat().st_size,SHA=H(p)) for p in sorted(F.iterdir()) if p.is_file()]
 put('FROZEN_SOURCE_INDEX_ACTUAL.json',dict(frozen=True,entries=rows))
 print(json.dumps(dict(passed=True,delta='two signed GO alias fields',worker_guards_unchanged=True)))
if __name__=='__main__':main()
