"""Freeze source, tiny fixture text and reports; no binary model permitted."""
from pathlib import Path
import hashlib,json,time
D=Path(__file__).resolve().parent;T=D.parent.parent
P=D/'FROZEN_THREE_GPU86B_CLOSING_CPU_PROTOCOL_INDEX.json'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M2_20261026'
lineage=[]
for name in ('collect_V85M2_single72_finals_actual_cost_V2_UNUSED.py','review_V85M2_single72_native_E3_CPU_V3_one_load_partial_receipt_UNUSED.py'):
 p=old/name;lineage.append(dict(path=str(p),bytes=p.stat().st_size,SHA=H(p),source_only_not_executed=True))
files=[]
for p in sorted(D.rglob('*')):
 if p.is_file() and p!=P:
  assert p.suffix.lower() not in ('.pt','.npz','.usd','.zip')
  files.append(dict(relative=p.relative_to(D).as_posix(),path=str(p),bytes=p.stat().st_size,SHA=H(p)))
value=dict(schema='mod4.three_gpu86b.closing_source.frozen_index.v1',epoch=time.time(),frozen=True,
 file_count=len(files),files=files,excludes_only_self=True,source_lineage=lineage,
 synthetic_CPU_passed=35,synthetic_CPU_total=35,actual_collector_or_close_reviewer_executed=False,
 actual_PT_NPZ_read_hash_copy=False,remote_SSH_GPU_ledger_Task_GO_Git=False,
 reader_errors=[
  dict(id='CLOSE86B_READER_001',kind='guessed current common source path missing',result='N86B/three_slot_common_v1.py not present; inspected N86/controllers_v2 instead'),
  dict(id='CLOSE86B_READER_002',kind='detached report not yet written during source preparation',result='No readback or runtime claim inferred; collector waits for actual required input'),
  dict(id='CLOSE86B_READER_003',kind='guessed old83B collector basename missing',result='Corrected via rg to collect_actual_three83B_finals_original_cost_unused_once.py'),
  dict(id='CLOSE86B_READER_004',kind='guessed generic owner basename missing',result='Corrected via directory inventory to three_slot_finite_owner_V86_authority72.py')],
 archive_status='pending root phase Git archive; not claimed recorded')
with P.open('x',encoding='utf8') as stream:json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n')
print(json.dumps(dict(index=str(P),index_SHA=H(P),files=len(files),
 collector_SHA=H(D/'collect_three_gpu86b_finals_actual_cost_unused_once.py'),
 reviewer_SHA=H(D/'review_three_gpu86b_finals_CPU_unused_once.py'),frozen=True)))
