"""LOCAL source hash/AST/read-contract only;no model/data/SDK imports."""
from pathlib import Path
import argparse,ast,hashlib,json,time
N=Path(__file__).resolve().parent;R=N/'reports'
ID='NEW222_RM70_CLOSED_SKILL_SOURCE_AST_INTERFACE_V1'


def ref(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=('freeze','AST','seal'));a=p.parse_args();R.mkdir(exist_ok=True)
 if a.mode=='freeze':
  files=[N/name for name in ('rm70_intervals222.py','evaluate222_CLOSED_W35_FULL_RM70_SKILL_UNUSED_once.py','make222_qualified_TASK_SOURCE_ONLY.py')]
  put(R/'CPU222_SOURCE_PURPOSE_FROZEN.json',dict(purpose_id=ID,frozen_epoch=time.time(),source_files=[ref(x) for x in files],
   scope='AST and declared source-interface presence only;not a behavioral/physical/model fixture',groups=1,
   PT_NPZ_USD_raw_Torch_SDK_GPU_SSH_Git_calls=0,old_once_fixture_replays=0))
  print(json.dumps(dict(source_purpose_frozen=True,source_files=3,fixture_runs=0)));return
 if a.mode=='AST':
  f=json.loads((R/'CPU222_SOURCE_PURPOSE_FROZEN.json').read_bytes());assert f['purpose_id']==ID
  put(R/'CPU222_SOURCE_ONCE_CONSUMED.json',dict(epoch=time.time(),purpose_id=ID,fixture_runs=0))
  for r in f['source_files']:
   raw=Path(r['path']).read_bytes();assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['SHA'];ast.parse(raw.decode('utf8'))
  worker=(N/'evaluate222_CLOSED_W35_FULL_RM70_SKILL_UNUSED_once.py').read_text(encoding='utf8')
  collector=(N/'rm70_intervals222.py').read_text(encoding='utf8')
  assert 'range(1600)' in worker and 'PinnedSource208' in worker and "runner.alg.optimizer.step=forbidden" in worker
  assert "book.terminal(real._e1_pre_reset_frame" in worker and 'runner.alg.actor(obs,stochastic_output=False)' in worker
  assert "not_full_expert_or_signed2pi_cycle_graduation=True" in collector and 'increment_uid=False' in collector
  put(R/'CPU222_SOURCE_AST_INTERFACE_ACTUAL.json',dict(epoch=time.time(),purpose_id=ID,passed_source_AST=True,groups=1,
   source_files=3,behavioral_fixture_or_model_test=False,actual_target_conformance='EXPLICIT_PENDING_ROOT',
   PT_NPZ_USD_raw_Torch_SDK_GPU_SSH_Git_calls=0,old_once_fixture_replays=0))
  print(json.dumps(dict(passed_source_AST=True,physical_or_model_proof=False,forbidden_calls=0)));return
 cpu=json.loads((R/'CPU222_SOURCE_AST_INTERFACE_ACTUAL.json').read_bytes());assert cpu['passed_source_AST']
 put(R/'ROOT222_UNUSED_SDK_MODEL_READ_CONTRACT.json',dict(status='SOURCE_AST_FROZEN_RUNTIME_CONFORMANCE_AND_SKILL_EXECUTION_EXPLICIT_PENDING',
  worker=ref(N/'evaluate222_CLOSED_W35_FULL_RM70_SKILL_UNUSED_once.py'),observer=ref(N/'rm70_intervals222.py'),
  task_builder=ref(N/'make222_qualified_TASK_SOURCE_ONLY.py'),
  source_model=dict(SHA='343e0fd8f4950ffea2b09808a3bf88d9dd68e14b06f84c7bdaad462dbc8a51bd',bytes=17619269,
   iteration=32404,Adam17=649720,new_PPO_updates=68,saved_LR=.00017085937500000009),
  ROOT_precondition='Fresh CURRENT CNone/exact LOCAL CIM/sole serialSSH + original selected GPU private/shared/resources;old219 active identity is historical',
  target='72',num_envs=20000,controls_max=1600,physics_max=12800,feedback_max=3200,seconds_max=32.,
  counts=dict(selected_formal_byte_hash_pass=1,selected_formal_decode=1,model_copies=0,old_model_CPU_reads=0,old_raw_reads=0,
   constructor_resetNPZ_and_CAD_assets='Original qualified219 physical constructor only',own_startup_roundtrip_PT_reads='Original existing restore-chain own artifacts,not source rereads'),
  optimizer_steps=0,new_learning_GO=False,account_writes=0,
  complete_window_needs='1600/12800/3200 + exact unions/core unchanged + no unknown observer/retention coverage;not whole expert graduation',
  unexposed_complete_skill_domains='UNKNOWN;no oldG3world.5 or2pi false credit',
  after_Appclose_marker_required=False,original_wait_out_EXrelease_and_source_finally_required=True,
  default_transfer='Small JSON receipts/producer metadata only,not JSONL/retentionNPZ',
  actual_target_executed=False,child_forbidden_calls=0))
 put(R/'SOURCE222_READER_NOTES_AND_PENDING.json',dict(
  source_reader_errors=[dict(id='SOURCE222_213_EVAL_HEAD_OUTPUT_CLIP',result='First broad source read clipped output;subsequent narrow interface/source reads used;no physical/model test'),
   dict(id='SOURCE222_CATALOG_SEARCH_ACCESS_DENIED',result='rg encountered rmuc2026_work/unpack_verify_4zomhj13 access denied;used actual build_catalog.py40/41/60 source hits;no permission change/retry traversal')],
  source_logic_revisions_before_freeze='Observer natural timer mask made full per-env;segments do not invent UIDs;goal entry stored before later failures;source E1 episode checked;no actual case consumed',
  prior_source_errors_or_failures_not_overwritten=True,old5039_stream_not_read=True,
  runtime_observer_conformance='EXPLICIT_PENDING_ROOT',actual_skill='EXPLICIT_PENDING_ROOT',Git='PENDING_ROOT_NEXT_STAGE'))
 files=[]
 for f in sorted(N.rglob('*')):
  if f.is_file():
   assert f.suffix in ('.py','.json','.md','.txt') and not f.name.endswith(('.partial','.active'))
   r=ref(f);r['relative']=str(f.relative_to(N)).replace('\\','/');files.append(r)
 index=dict(schema='mod4.222.closedRM70_skill_source_index.v1',frozen_epoch=time.time(),files=files,file_count=len(files),
  status='SOURCE_AST_FROZEN_ACTUAL_RUNTIME_CONFORMANCE_AND_SKILL_EXPLICIT_PENDING',
  child_PT_NPZ_USD_raw_Torch_SDK_GPU_SSH_Git_calls=0,old_once_fixture_replays=0,
  no_new_learning_GO=True,no_new_aggregate_skill_gate=True,full_SuperMimic_or_full_expert_graduation=False,
  Git_status='PENDING_ROOT_NEXT_UNIFIED_ARCHIVE')
 path=N/'INDEX222_FROZEN.json';put(path,index);print(json.dumps(dict(INDEX=ref(path),worker=ref(N/'evaluate222_CLOSED_W35_FULL_RM70_SKILL_UNUSED_once.py'),files=len(files),actual_target_execution=False)))


if __name__=='__main__':main()
