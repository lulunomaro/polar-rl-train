"""Correct callback IO only; preserve the native learning algorithm and state."""
from pathlib import Path
import ast,copy,hashlib,json,os,shutil,sys,time,uuid
T=Path(__file__).resolve().parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
O=T/'MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V95_20261028'
N=T/'MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V97_20261028'
F=L/'native97_unique_sampler_diagnostic_receipts_source_v1'
def read(p):return json.loads(p.read_bytes())
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8')
def main():
 assert not N.exists() and not F.exists();N.mkdir();(N/'reports').mkdir();F.mkdir()
 entry='source/native_flat5cm_training_entry_candidate_v4_typed_producer.py'
 source=O/'payload'/entry;s=source.read_text('utf8')
 old="out/'NATIVE_TASK_FOCUS_SAMPLE_COUNTS_ACTUAL.json'"
 new="out/('NATIVE_TASK_FOCUS_SAMPLE_COUNTS_'+str(value['calls'])+'_ACTUAL.json')"
 assert s.count(old)==1;changed=s.replace(old,new,1)
 candidate=F/'native_flat5cm_training_entry_candidate_v4_typed_producer.py';write(candidate,changed)
 # Verify the complete module differs solely in the target filename expression.
 assert ast.dump(ast.parse(changed.replace(new,old,1)))==ast.dump(ast.parse(s))
 finalization=O/'payload/source/native_finalization_own_flat5cm_v1.py'
 tree=ast.parse(finalization.read_text('utf8'));node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='atomic_json')
 env=dict(Path=Path,json=json,os=os,uuid=uuid)
 exec(compile(ast.Module(body=[node],type_ignores=[]),str(finalization),'exec'),env)
 def diagnostic(text):
  tree=ast.parse(text)
  call=next(x for x in ast.walk(tree) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='attach_task_focused_starts')
  return next(x.value for x in call.keywords if x.arg=='diagnostic')
 oldout=F/'CPU_original_same_name';newout=F/'CPU_new_unique_names';oldout.mkdir();newout.mkdir()
 oldcall=eval(compile(ast.Expression(diagnostic(s)),'old_actual_diagnostic_lambda','eval'),dict(atomic_json=env['atomic_json'],out=oldout))
 oldcall(dict(calls=1));old_failed=False
 try:oldcall(dict(calls=2))
 except FileExistsError:old_failed=True
 assert old_failed
 fixed=eval(compile(ast.Expression(diagnostic(changed)),'new_actual_diagnostic_lambda','eval'),dict(atomic_json=env['atomic_json'],out=newout))
 fixed(dict(calls=1));fixed(dict(calls=2))
 assert read(newout/'NATIVE_TASK_FOCUS_SAMPLE_COUNTS_1_ACTUAL.json')['calls']==1
 assert read(newout/'NATIVE_TASK_FOCUS_SAMPLE_COUNTS_2_ACTUAL.json')['calls']==2
 try:fixed(dict(calls=2))
 except FileExistsError:pass
 else:raise AssertionError('original duplicate-writer guard no longer rejects collision')
 put(F/'SOURCE_CPU_ACTUAL.json',dict(passed=True,epoch=time.time(),source_only=True,
  actual96A_failure='Second sampler diagnostic call reused a fresh-only atomic_json receipt name; not a WM/autograd failure',
  original_second_call_failure_reproduced=True,new_first_two_calls_persist_separate_receipts=True,
  original_duplicate_writer_refusal_retained=True,only_filename_expression_changed=True,
  original_entry_SHA=H(source),selected_entry_SHA=H(candidate),original_atomic_json_source_SHA=H(finalization),
  no_models_read_hash_forward_GPU_SDK_physics_remote_or_account=True))
 put(F/'FROZEN_SOURCE_INDEX_ACTUAL.json',dict(frozen=True,entries=[dict(path=p.relative_to(F).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(F.rglob('*')) if p.is_file()]))
 B=N/'payload';B.mkdir();manifest=read(O/'payload/THREE_SLOT_COMPLETE_MANIFEST_V1.json')
 for row in manifest['files']:
  src=O/'payload'/row['relative'];dest=B/row['relative'];dest.parent.mkdir(parents=True,exist_ok=True)
  if src.suffix.lower() in ('.pt','.npz','.usd','.zip') and src.stat().st_size>1024**2:os.link(src,dest)
  else:shutil.copy2(src,dest)
 write(B/entry,changed)
 cpu=B/'target_native_flat90_source_sdk_CPU_once.py';code=cpu.read_text('utf8')
 needle="require(not torch.cuda.is_initialized(),'CPU admission unexpectedly initialized CUDA')";assert code.count(needle)==1
 proof="""from native_finalization_own_flat5cm_v1 import atomic_json
 io=J/'NEW97_DIAGNOSTIC_RECEIPT_SOURCE_CPU';io.mkdir()
 import ast
 entry_tree=ast.parse((B/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py').read_text('utf8'))
 source_call=next(x for x in ast.walk(entry_tree) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='attach_task_focused_starts')
 callback=next(x.value for x in source_call.keywords if x.arg=='diagnostic')
 actual_callback=eval(compile(ast.Expression(callback),'actual_installed_diagnostic_callback','eval'),dict(out=io,atomic_json=atomic_json))
 actual_callback(dict(calls=1));actual_callback(dict(calls=2))
 require(read(io/'NATIVE_TASK_FOCUS_SAMPLE_COUNTS_1_ACTUAL.json')['calls']==1 and read(io/'NATIVE_TASK_FOCUS_SAMPLE_COUNTS_2_ACTUAL.json')['calls']==2,'two actual installed diagnostic calls retain independent receipts')
 """
 code=code.replace(needle,proof+needle,1).replace('task_focused_replay_source_CPU_passed=True,','diagnostic_receipt_IO_source_CPU_passed=True,task_focused_replay_source_CPU_passed=True,',1);write(cpu,code)
 contract=read(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');contract['diagnostic_receipt_revision']='unique_per_sampling_call_v1'
 contract['approved_python']={p.relative_to(B).as_posix():H(p) for p in B.rglob('*.py')}
 write(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json',json.dumps(contract,indent=2))
 task=read(B/'job0/TASK.json');task['id']='MOD4_H1_TASK_FOCUSED_DIAGNOSTIC_IO_FIXED_V97';task['flat_source_contract_SHA']=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');write(B/'job0/TASK.json',json.dumps(task,indent=2))
 oldrows={r['relative']:r for r in manifest['files']};rows=[]
 for p in sorted(B.rglob('*')):
  if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
  rel=p.relative_to(B).as_posix()
  row=oldrows[rel] if p.suffix.lower() in ('.pt','.npz','.usd','.zip') else dict(relative=rel,bytes=p.stat().st_size,SHA=H(p))
  assert row['bytes']==p.stat().st_size;rows.append(row)
 manifest['files']=rows;write(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',json.dumps(manifest,indent=2))
 current=read(O/'reports/NATIVE95_ACTUAL_CPU_BOUND_SPEC_PENDING_CONTROLLER_SEAL.json')['spec']
 job='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT05_TASK_FOCUSED_2610v97/h1'
 spec=copy.deepcopy(current);spec.update(logical_slot='h1',job_root=job,CPU_path=job+'/job0/FLAT90_SOURCE_SDK_CPU_ACTUAL.json',CPU_proof_path=job+'/job0/FLAT90_SOURCE_CPU_WAITED_ACTUAL.json',payload_manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'),payload_manifest_path=job+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json',source_contract_path=job+'/FLAT90_SOURCE_CONTRACT_ACTUAL.json')
 for k in ('source_CPU_SHA','CPU_waited_proof_SHA','manifest_SHA'):spec.pop(k,None)
 C=N/'controllers';C.mkdir()
 protocol=(L/'native96_H1_GO_alias_binding_source_v1/h1_next72_protocol_signed_alias96_candidate.py').read_text('utf8').replace('MOD4_H1_FLAT05_TASK_FOCUSED_2610v95/h1','MOD4_H1_FLAT05_TASK_FOCUSED_2610v97/h1')
 needle="'task_focused_replay_source_CPU_passed',";assert protocol.count(needle)==1;protocol=protocol.replace(needle,"'diagnostic_receipt_IO_source_CPU_passed','task_focused_replay_source_CPU_passed',",1)
 write(C/'h1_next72_protocol_diag97.py',protocol)
 for p in [*B.rglob('*.py'),*C.glob('*.py')]:ast.parse(p.read_bytes())
 put(N/'reports/NATIVE97_DIAGNOSTIC_IO_SOURCE_PREPARED_ACTUAL.json',dict(passed=True,epoch=time.time(),spec_pending_actual_new_source_CPU=spec,
  task=task,source_fullstate_same_qualified93=True,source_model_not_redecoded_locally=True,
  declared_new_target_fullstate_CPU_purpose='New diagnostic-callback IO code and source inventory admission; initial source93+normal86 load once, not statistics/Git',
  source_IO_proof=str(F/'SOURCE_CPU_ACTUAL.json'),payload_manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'),
  changed_source_files=[entry,'target_native_flat90_source_sdk_CPU_once.py'],learning_algorithm_models_norms_threeoptimizers_actions_physics_reward_unchanged=True,no_GO=True))
 print(json.dumps(dict(prepared=True,payload_manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),new_target_source_CPU_pending=True)))
if __name__=='__main__':main()
