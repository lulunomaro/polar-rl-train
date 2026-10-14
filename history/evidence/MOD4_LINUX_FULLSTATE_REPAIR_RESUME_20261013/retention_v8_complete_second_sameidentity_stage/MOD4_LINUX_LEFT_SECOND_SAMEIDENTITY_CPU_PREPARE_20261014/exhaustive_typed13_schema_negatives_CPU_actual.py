"""Exhaustive top-level typed13 predicates from actual receipts, CPU only."""
from pathlib import Path
import json,hashlib,time,importlib.util,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';P=D/'payload_v1'
OUT=R/'SECOND_TYPED13_ALL_ACTUAL_BOOLEAN_PREDICATES_NEGATIVE_CPU_REVIEW.json';assert not OUT.exists()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def witness(p):return dict(path=str(p),bytes=Path(p).stat().st_size,sha256=sha(p))
try:
 t=P/'left_sameidentity_typed13_receipts.py';before=sha(t)
 spec=importlib.util.spec_from_file_location('typed13_only_exhaustive',t);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 folder=W/'MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_first_formal_ownsave_1791939576241228200'
 accepted=[];neg=[];files=[]
 for p in sorted(folder.glob('*STARTUP*VERIFIED.json')):
  v=json.loads(p.read_bytes());name=p.name.split('_',1)[1];pid=v['pid'];source=v['source_sha256'];files.append(witness(p))
  accepted.append(m.validate_one(name,v,pid,source))
  def reject(case,new):
   try:m.validate_one(name,new,pid,source)
   except AssertionError:neg.append(dict(receipt=name,case=case,strict_rejected=True))
   else:raise AssertionError('Unexpectedschemaaccept:'+name+'/'+case)
  for field,value in m.REQUIRED_BOOLEAN_SCHEMA[name].items():
   z=dict(v);z[field]=not value;reject('flipped_'+field,z)
   z=dict(v);z.pop(field);reject('missing_'+field,z)
   z=dict(v);z[field]=int(value);reject('integer_not_boolean_'+field,z)
  z=dict(v);z['source_sha256']='0'*64;reject('wrong_source_sha',z)
  z=dict(v);z['pid']=-1;reject('wrong_pid',z)
 assert len(accepted)==13 and sum(not x['passed_field_required'] for x in accepted)==8
 expected=sum(len(v) for v in m.REQUIRED_BOOLEAN_SCHEMA.values())*3+13*2;assert len(neg)==expected
 names=list(m.REQUIRED_BOOLEAN_SCHEMA)
 setneg=[]
 for case,paths in [('missing_one',names[:-1]),('duplicate_receipt',names[:-1]+[names[0]]),('wrong_extra_name',names[:-1]+['NOT_A_REAL_RECEIPT.json'])]:
  try:m.validate_set(paths,1,'0'*64)
  except AssertionError:setneg.append(dict(case=case,strict_rejected_before_file_read=True))
  else:raise AssertionError('Badreceiptsetaccepted')
 assert sha(t)==before and all(sha(x['path'])==x['sha256'] for x in files)
 out=dict(epoch=time.time(),passed=True,helper_source=witness(t),actual_receipt_sources=files,all13_actual_positive_schema_passed=accepted,
  eight_actual_legacy_receipts_without_passed_accepted=True,actual_boolean_predicates=sum(len(v) for v in m.REQUIRED_BOOLEAN_SCHEMA.values()),negative_actual_field_copy_cases=neg,negative_count=len(neg),negative_receipt_set_cases=setneg,
  every_boolean_wrongvalue_missingfield_and_integer_type_strict_rejected=True,every_source_and_pid_mismatch_rejected=True,
  original_receipt_bytes_and_helper_before_after_exact=True,fixture_metadata_only_no_future_GPU_restore_proof=True,
  actual_target_CPU_sourcefreeze_resources_four_case_decision_PENDING=True,no_oldonce_import_execution_no_SSH_GPU_budget_or_Git=True,Git_archive_pending_root_owner=True)
 OUT.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(dict(report=str(OUT),positive=13,missingpassedAccepted=8,predicates=out['actual_boolean_predicates'],negatives=len(neg),badsets=len(setneg),GPU=False)))
except Exception:
 p=R/f'EXHAUSTIVE_SCHEMA_ORIGINAL_ERROR_{time.time_ns()}.json';p.write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),source_script=witness(__file__),no_GPU_SSH_budget=True,Git_archive_pending_root_owner=True),indent=2),encoding='utf8');raise
