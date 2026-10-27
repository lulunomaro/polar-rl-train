"""UNUSED metadata-only selection after formal closing/initial whole CPU/allout.

No checkpoint, asset, actor, SDK, transport or budget is opened by this preparer.
Root copies pinned runtime/model/evidence to a new eval root and supplies binding.
"""
from pathlib import Path
import argparse,hashlib,json
from native87R5_frozen_acceptance_contract_v1 import select_source
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def prepare(stage):
 N=Path(stage).resolve();R=N/'reports'
 paths=dict(cpu=R/'H1_NATIVE87R5_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json',collection=R/'H1_NATIVE87R5_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json',prepared=R/'AVAILABLE_TWO_NATIVE87R5_SOURCE_PREPARED_ACTUAL.json',detached=R/'AVAILABLE_TWO_NATIVE87R5_ACTUAL_OWNER_NODES_DETACHED.json')
 values={k:read(p) for k,p in paths.items()};cpu=values['cpu'];collection=values['collection'];events={};pins={k:dict(path=str(p),SHA=H(p)) for k,p in paths.items()}
 assert collection['run_id']==values['detached']['run_id']
 for key in ('h1','recovery'):
  p=N/'current_native87R5_closed_text'/key/'job0/production/control_prefix_raw/CONTROL_LIFETIME_GOAL_EVENTS_ACTUAL.json'
  rows=[r for r in collection['all_texts'] if r.get('local_path')==str(p)]
  if rows:
   assert len(rows)==1 and p.is_file() and H(p)==rows[0]['SHA'] and p.stat().st_size==rows[0]['bytes']
   events[key]=read(p);pins['events_'+key]=dict(path=str(p),SHA=H(p))
 selected=select_source(cpu,collection,events);key=selected['selected_key'];B=Path(values['prepared']['payloads'][key]);manifest=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
 assert H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')==values['detached']['specs'][key]['manifest_SHA']
 # Original manifest only: no training output/raw replay inventory. Bootstrap
 # .pt/.pth rows are not evaluation model sources and are excluded.
 runtime_files=[r for r in manifest['files'] if Path(r['relative']).suffix.lower() not in ('.pt','.pth','.npz')]
 return dict(passed=True,purpose='MOD4_native87R5_formal_frozen_3seed_step_acceptance',source_run_id=collection['run_id'],selection=selected,
  qualified_training_roots=values['detached']['roots'],qualified_owner_root=values['detached']['owner_root'],
  source_model=selected['source']['final'],source_runtime_local=str(B),source_runtime_remote=values['detached']['roots'][key],
  runtime_files=runtime_files,evidence_pins=pins,full_text_events=events,
  runtime_source_contract=read(B/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json'),reference_SHA=values['detached']['specs'][key]['reference_artifact_SHA'],
  reference_relative=read(B/'job0/TASK.json')['native_reference_relative'],original_owner_locks=collection['authority72']['original_locks'],
  GPU_original_locks={k:[r['path'] for r in collection['nodes'][k]['locks']] for k in ('h1','recovery')},
  source_qualification=dict(formal_FINAL_passed=True,initial_whole_CPU_passed=True,original_fee_allout_passed=True),
  actual_fresh_N1_source_SDK_resource_admission='PENDING; no SDK/actor has run',not_best_case_or_skill_claim=True)
def bind_new_eval(plan,*,eval_root,runtime_root,model_eval_relative,GPU_UUID,eval_code_pins,evidence_eval_relatives,external72_readonly_guard=None):
 """Pure explicit binding builder; does not copy/read a model or runtime asset.

 Root installs the original manifest runtime rows under a new eval-owned child,
 copies the formal native model and these evidence bytes, and pins this binding.
 External72 guard is only needed on source210; a ready receipt never replaces
 root's actual live stdin holder and final waited exit proof.
 """
 from native87R5_frozen_acceptance_contract_v1 import SEEDS,GPU_BACKENDS,validate_eval_binding
 assert plan['passed'] is True and GPU_UUID in GPU_BACKENDS
 backend=GPU_BACKENDS[GPU_UUID];slot='recovery' if backend=='target72' else 'h1'
 pins={k:dict(v,eval_relative=evidence_eval_relatives[k]) for k,v in plan['evidence_pins'].items()}
 q=dict(plan,purpose='MOD4_native87R5_formal_frozen_3seed_step_acceptance',selected_key=plan['selection']['selected_key'],selection_scope=plan['selection']['selection_scope'],
  seeds=list(SEEDS),episodes_per_seed=1,max_controls=500,max_physics_callbacks=2000,action_mode='deterministic_native_mean_no_collection_noise',
  GPU_UUID=GPU_UUID,execution_backend=backend,eval_root=str(eval_root),runtime_root=str(runtime_root),model_eval_relative=model_eval_relative,
  eval_code_pins=eval_code_pins,evidence_pins=pins,selected_GPU_original_locks=plan['GPU_original_locks'][slot],
  new_N1_fresh_episode_no_training_environment_restore=True,runtime_is_new_readonly_copy=True)
 if backend=='source210':
  assert external72_readonly_guard is not None
  q['external72_readonly_guard']=external72_readonly_guard;q['external72_guard_parent_keeps_live_stdin_and_requires_waited_exit_proof']=True
 validate_eval_binding(q);return q
def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',required=True);args=p.parse_args();N=Path(args.stage);value=prepare(N)
 with (N/'reports/NATIVE87R5_CLOSED_FROZEN_SELECTION_DECLARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
 print(json.dumps(dict(passed=True,selected_key=value['selection']['selected_key'],selection_scope=value['selection']['selection_scope'],actual_evaluation_not_started=True)))
if __name__=='__main__':main()
