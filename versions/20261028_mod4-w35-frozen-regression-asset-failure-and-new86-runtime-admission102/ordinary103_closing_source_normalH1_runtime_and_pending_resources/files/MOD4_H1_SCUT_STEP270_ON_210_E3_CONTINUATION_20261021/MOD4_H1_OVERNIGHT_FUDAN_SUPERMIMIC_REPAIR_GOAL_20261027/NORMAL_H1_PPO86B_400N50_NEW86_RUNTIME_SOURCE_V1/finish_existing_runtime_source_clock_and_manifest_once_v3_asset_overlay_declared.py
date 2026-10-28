"""Finish the existing text candidate after V1's diagnostic class-name error."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys,time
B=Path(__file__).resolve().parent;L=B.parent;T=L.parent;D=B/'candidate_payload'
OLD=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/h1'
RT='job0/runtime/isaac/mod4/'
def H(x):return hashlib.sha256(x).hexdigest()
def main():
 out=B/'NORMAL_H1_COMPLETE_SOURCE_INPUT_MANIFEST_NOT_GPU_ADMITTED_V3.json';assert not out.exists()
 original=json.loads((OLD/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());pins={r['relative']:r for r in original['files']}
 rows=[];deltas=[]
 allowed={RT+n for n in ('mod4_task.py','action_delay_physics_queue.py','action_delay_sdk_adapter.py','train_H1_ground_prelaunch_fullstate_v2.py','scut_flat_rescue.py','spring_pressure_index_runtime.py','spring_pressure_audit_runtime.py','spring_nominal_sdk_readback.py','spring_pressure_training_env.py','import_contract.json')}|{'h1_step270_sdk_runtime_candidate.py','job0/runtime/reports/SOURCE_FREEZE.json','job0/assets/import_contract.json','job0/assets/robot.usd'}
 for p in sorted(D.rglob('*')):
  if not p.is_file():continue
  assert p.suffix.lower() not in ('.pt','.npz','.usd','.zip','.npy') or p.relative_to(D).as_posix()=='job0/assets/robot.usd'
  rel=p.relative_to(D).as_posix();raw=p.read_bytes()
  if p.suffix=='.py':ast.parse(raw)
  rows.append(dict(relative=rel,local_path=str(p),bytes=len(raw),SHA=H(raw),index_kind='actual_small_source_bytes'))
  if rel in pins and H(raw)!=pins[rel]['SHA']:
   assert rel in allowed,rel
   deltas.append(dict(relative=rel,old_SHA=pins[rel]['SHA'],new_SHA=H(raw)))
 for r in original['files']:
  rel=r['relative']
  if rel.startswith(('job0/runtime/','lib/')) and Path(rel).suffix.lower() in ('.npz','.usd','.zip','.npy'):
   rows.append(dict(r,local_path=str(OLD/rel),index_kind='existing original binary producer witness; not opened'))
 asset=pins['job0/assets/robot.usd'];assert asset['SHA']=='694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87'
 rows.append(dict(relative='job0/assets/source_700N/robot.usd',local_path=str(OLD/'job0/assets/robot.usd'),bytes=asset['bytes'],SHA=asset['SHA'],index_kind='existing original asset producer witness; not opened'))
 cpu=json.loads((L/'NORMAL_H1_PPO86B_400N50_NEW86_SOURCE_PREPARATION_V1/reports/NORMAL_H1_TYPED40050_ORIGINAL_FULLSTATE_CPU_ACTUAL_V1.json').read_bytes());assert cpu['passed']
 rows.append(dict(relative='job0/source/NORMAL_H1_86B138_N20K_PPO50_GAS400_NOT_GPU_ADMITTED.pt',local_path=cpu['new_source']['path'],bytes=cpu['new_source']['bytes'],SHA=cpu['new_source']['SHA'],index_kind='actual typed source producer witness; not opened'))
 assert len({r['relative'] for r in rows})==len(rows)
 tree=ast.parse((D/'h1_step270_sdk_runtime_candidate.py').read_bytes());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Step270Phase')
 methods=[n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name in ('public_request','finish_control_before_selected_reset')];assert len(methods)==2
 tiny=ast.Module(body=[ast.ClassDef(name='Clock',bases=[],keywords=[],body=methods,decorator_list=[])],type_ignores=[]);ast.fix_missing_locations(tiny);ns={};exec(compile(tiny,'actual_normal_H1_clock_methods','exec'),ns);c=ns['Clock']();c.age_control=0;active=[]
 for i in range(100):
  if c.public_request():active.append(i)
  c.finish_control_before_selected_reset()
 assert active==list(range(50,90)) and c.age_control==200
 p=D/RT/'gas400_reset_bank_exact_compatibility_v1.py';s=importlib.util.spec_from_file_location('normal_H1_unchanged400_bank_helper_CPU',p);helper=importlib.util.module_from_spec(s);sys.modules[s.name]=helper;s.loader.exec_module(helper);bank=helper.check_runtime_source(D/RT)
 assert bank['pose_ranges']['all_poses']==133 and bank['pose_ranges']['original_height_filter_selected_poses']==74
 val=dict(kind='normal_H1_PPO86B40050_runtime_candidate_v3',source_only=True,files=rows,source_changes=deltas,actual_clock_method_source_CPU_passed=True,public_phase_tick_hz=100,policy_hz=50,public_phase_increment=2,public_request_seconds=[1.,1.8],public_request_policy_indices_inclusive=[50,89],physics_dt_s=.0025,decimation=8,feedback_hz=100,landing12_recovery200_physics_callbacks_unchanged=True,exact_original133pose74selection_gas400_helper_CPU=bank,typed_model_producer=cpu['new_source'],original_source_PPO86B138_SHA=cpu['source']['original_source_SHA'],Adam_source=832460,required_constructor_LR=.00038443359375000017,original_actor35_critic38_STD6_D1_D7_and_original_true270_reward_task_retained=True,no_native101or103_method_or_newFudan_reward_injected=True,new_targetSDK_CUDA_fullrestore_native24_firstPPO_and_sole72GO_pending=True,no_model_USD_binary_opened=True,original_frozen_skill_qualification_not_inherited=True,Git='root pending ordinary; runtime worker/target admission not yet sealed')
 out.write_text(json.dumps(val,indent=2)+'\n')
 err=dict(epoch=time.time(),original_V1_source_unchanged=True,original_V1_failure='StopIteration selecting H1Step270Phase; actual source class is Step270Phase',secondary_error_while_persisting_original='TypeError: unsupported operand type(s) for +: WindowsPath and str at V1 line88',V1_created_source_copy_retained=True,new_v2_only_finishes_source_methods_and_manifest=True,no_model_GPU_or_network=True)
 (B/'V1_ORIGINAL_SOURCE_CLASS_LOOKUP_AND_ERROR_PERSISTENCE_FAILURE_RETAINED.json').write_text(json.dumps(err,indent=2)+'\n')
 print(json.dumps(dict(passed_source_clock_and_exact_reset_bank=True,files=len(rows),source_changes=len(deltas),manifest=str(out),SHA=H(out.read_bytes()))))
if __name__=='__main__':main()
