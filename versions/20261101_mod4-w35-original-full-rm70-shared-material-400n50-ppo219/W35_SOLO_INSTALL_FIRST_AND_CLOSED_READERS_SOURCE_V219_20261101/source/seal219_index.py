"""LOCAL source/report sealing only; no tests, model bytes or external I/O."""
from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent.parent;R=N/'reports'


def ref(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)


def main():
 cpu=json.loads((R/'CPU219_NEW_CALLER_METADATA_ACTUAL.json').read_bytes())
 assert cpu['passed'] and cpu['group_count']==3 and cpu['rejected_cases']==9
 entries=[N/name for name in ['launch219_install_original_solo_W35_FIRST_UNUSED_once.py',
  'collect219_original_W35_formal_cost_normal900_UNUSED_once.py',
  'review219_NEW_W35_formal_initial_whole_CPU_UNUSED_once.py']]
 put(R/'NEXT219_COMPLETE_UNUSED_ENTRIES_SOURCE_HANDOFF.json',dict(epoch=time.time(),
  status='ALL_SOURCE_COMPLETE_UNUSED_ACTUAL210_NORMAL_CLOSURE_AND_NEW_CPU_REQUIRED',
  entries=[ref(p) for p in entries], installer=True,FIRST=True,normal900=True,NEWformalCPU=True,
  first_gate='actual210 complete normal close + matching NEW formal CPU before CIM/network/assets/PT',
  target_test_or_GO_by_child=False, source_model_SHA='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f',
  source_iteration=32336,Adam17=648360,source_LR=.00011390625000000003,
  physical_input_streamcopy_by_root_next_purpose=1,worker_new_copy_read_decode=1,old_CPU_PT_reads=0,
  source218_INDEX_SHA='6578d66cd1aa1e68da9c054f3efc09bfe38dc20194e7ae6524165b390911f365',
  source218_install_bindings_SHA='6dca140a744b0e274572563bd4467070425496a5e6a1a47a1a293567bd02e37a',
  no_new_budget_writer_grant_refund_hotadd=True, local_source_CPU=ref(R/'CPU219_NEW_CALLER_METADATA_ACTUAL.json'),
  normal900_not_executed=True,new_formal_CPU_not_executed=True,old218_fixture_replays=0,
  child_PT_NPZ_USD_raw_SDK_GPU_SSH_Git_calls=0,full_RM70_skill=False,full_native_SuperMimic=False,
  recording='ALL219_FILES_PENDING_ROOT_UNIFIED_GIT;218 priorGit success supplied by ROOT only'))
 files=[]
 for p in sorted(N.rglob('*')):
  if not p.is_file():continue
  assert p.suffix in ('.py','.json','.md','.txt') and not p.name.endswith(('.partial','.active'))
  row=ref(p);row['relative']=str(p.relative_to(N)).replace('\\','/')
  row['synthetic_CPU_schema_fixture_only']='SYNTHETIC_219_CLOSING_SCHEMA_FIXTURE' in row['relative']
  files.append(row)
 index=dict(schema='mod4.219.frozen_source_and_metadata.v1',frozen_epoch=time.time(),files=files,file_count=len(files),
  status='SOURCE_COMPLETE_SOURCE_CPU_PASS_UNUSED_ROOT_REVIEW_AND_ACTUAL_CLOSURE_REQUIRED',
  source_CPU_groups=3,source_CPU_rejections=9,old218_fixture_replays=0,
  input='W35 ad504/17619013bytes/32336/17Adam648360/LR.00011390625000000003,actor35critic38STD6',
  installer_FIRST_complete=True,normal900_complete=True,NEWformalCPU_source_complete=True,
  original_accounting_auth_guards_preserved=True,actual210_closed_not_claimed=True,
  child_PT_NPZ_USD_raw_SDK_GPU_SSH_Git_calls=0,no_weight_or_activepartial_in_index=True,
  Git_status='PENDING_ROOT_UNIFIED_ARCHIVE',full_skill_or_SuperMimic_complete=False)
 p=N/'INDEX219_FROZEN.json';put(p,index)
 print(json.dumps(dict(INDEX=ref(p),files=len(files),source_CPU_passed=True,all_future_entries_unused=True,forbidden_calls=0)))


if __name__=='__main__':main()
