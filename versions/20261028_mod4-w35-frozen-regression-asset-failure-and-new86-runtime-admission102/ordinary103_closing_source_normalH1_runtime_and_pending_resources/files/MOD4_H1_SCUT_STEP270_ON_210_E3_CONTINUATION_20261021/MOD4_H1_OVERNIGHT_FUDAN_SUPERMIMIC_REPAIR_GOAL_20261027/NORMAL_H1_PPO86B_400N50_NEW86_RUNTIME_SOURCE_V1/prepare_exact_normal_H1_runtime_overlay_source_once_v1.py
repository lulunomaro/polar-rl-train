"""New normal-PPO-H1 runtime fork; text only, no model/USD binary reads."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys,time
B=Path(__file__).resolve().parent;L=B.parent;T=L.parent
OLD=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/h1'
NATIVE=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027/payloads/h1'
DEST=B/'candidate_payload';RT='job0/runtime/isaac/mod4/'
def H(raw):return hashlib.sha256(raw).hexdigest()
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 assert not DEST.exists();DEST.mkdir(parents=True)
 original_manifest=json.loads((OLD/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
 pins={r['relative']:r for r in original_manifest['files']}
 patcher=module('normal_H1_existing_exact_gas400_patcher',L/'native88C_selected_runtime_integration_source_v1/gas400_source_patcher_v1.py')
 assert pins['job0/assets/robot.usd']['SHA']=='694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87'
 assert pins[RT+'reset_bank.json']['SHA']=='48be349c9bae1ec089b8bfb46ccc79085576e14bf373f6cb514027c3c155e50f'
 root_python=['h1_lifetime_goal_counter_v1.py','h1_prefix_pair_retention_v1.py','h1_production_control_prefix_trace_v1.py','h1_step270_fullstate_checkpoint_candidate_uninstalled.py','h1_step270_path_reward_v1.py','h1_step270_sdk_runtime_candidate.py','own_H1_storage_finite_guard_v1.py','sampling_trace_npz_lossless_v1.py','scut_ballistic_reference_uninstalled.py','step270_goal_and_scut_rates_candidate.py','step270_triangle_geometry_cpu.py']
 selected=[r for r in original_manifest['files'] if r['relative'].startswith(('job0/runtime/','lib/')) or r['relative']=='job0/original_run_manifest.json' or r['relative'] in root_python]
 changes={
 RT+'mod4_task.py':[(b'POLICY_HZ = float(DELIVERY_CONTRACT["policy_hz"])                   # 100 Hz',b'POLICY_HZ = 50.0  # declared new normal-H1 PPO40050 fork; delivery observation contract retained',1)],
 RT+'action_delay_physics_queue.py':[(b'10000',b'20000',4)],
 RT+'action_delay_sdk_adapter.py':[(b'env.step_dt==.01 and env.cfg.decimation==4',b'env.step_dt==.02 and env.cfg.decimation==8',1)],
 RT+'train_H1_ground_prelaunch_fullstate_v2.py':[(b'schedule=RM_SCHEDULE, gamma=0.99,',b'schedule=RM_SCHEDULE, gamma=0.9801,',1),(b'lam=0.95, desired_kl=',b'lam=0.9025, desired_kl=',1)],
 'h1_step270_sdk_runtime_candidate.py':[(b'def finish_control_before_selected_reset(self):self.age_control+=1',b'def finish_control_before_selected_reset(self):self.age_control+=2',1)],
 RT+'scut_flat_rescue.py':[(b"        if actual!=raw['contract_sha256']:raise RuntimeError('reset-bank contract hash mismatch')",b"        if actual!=raw['contract_sha256']:\n            from gas400_reset_bank_exact_compatibility_v1 import require_exact_gas400_reset_bank\n            require_exact_gas400_reset_bank(source,task.MOD4_ISAAC/'import_contract.json',raw,actual_contract_SHA=actual)",1)],
 }
 rows=[];deltas=[];old_text={};new_text={}
 def write(rel,raw,oldSHA=None,scope='literal inherited source'):
  q=DEST/rel;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw)
  if q.suffix=='.py':ast.parse(raw)
  rows.append(dict(relative=rel,local_path=str(q),bytes=len(raw),SHA=H(raw),index_kind='actual_small_source_bytes'))
  if oldSHA and oldSHA!=H(raw):deltas.append(dict(relative=rel,old_SHA=oldSHA,new_SHA=H(raw),scope=scope))
 for row in selected:
  rel=row['relative'];p=OLD/rel
  if p.suffix.lower() in ('.pt','.npz','.usd','.zip','.npy'):
   # No old model may enter this fork. Other binary dependencies remain producer-indexed.
   assert p.suffix.lower()!='.pt',rel
   rows.append(dict(row,local_path=str(p),index_kind='existing original manifest binary witness; not read'));continue
  raw=p.read_bytes();assert len(raw)==row['bytes'] and H(raw)==row['SHA'],rel;old_text[rel]=raw;out=raw
  name=Path(rel).name
  if rel.startswith(RT) and name in patcher.SPECS:out=patcher.patch_python(name,raw)
  if rel in ('job0/assets/import_contract.json',RT+'import_contract.json'):out,_=patcher.contract_overlay(raw)
  for a,b,n in changes.get(rel,[]):assert out.count(a)==n,(rel,a,out.count(a));out=out.replace(a,b)
  new_text[rel]=out;write(rel,out,row['SHA'],'exact declared clock/nominal-gas/reset-compatibility change')
 # Asset is the pinned original700 binary under a new tiny composition layer.
 contract=(OLD/'job0/assets/import_contract.json').read_bytes();assert H(contract)==patcher.OLD_CONTRACT_SHA
 write('job0/assets/import_contract.json',patcher.contract_overlay(contract)[0],H(contract),'four gas scalars only')
 original_asset=pins['job0/assets/robot.usd'];rows.append(dict(relative='job0/assets/source_700N/robot.usd',local_path=str(OLD/'job0/assets/robot.usd'),bytes=original_asset['bytes'],SHA=original_asset['SHA'],index_kind='original asset producer witness; binary not read'))
 write('job0/assets/robot.usd',patcher.usda_override())
 for name in ('gas400_reset_bank_exact_compatibility_v1.py','RESET_BANK_700N_ORIGINAL_IMPORT_CONTRACT_EXACT.json'):
  raw=(NATIVE/RT/name).read_bytes();write(RT+name,raw,scope='unchanged qualified88C exact133/74 reset compatibility helper; not native model')
 # Keep the previous SOURCE_FREEZE evidence aligned only at paths actually changed.
 rel='job0/runtime/reports/SOURCE_FREEZE.json';old=old_text[rel];freeze=json.loads(old);updates={}
 for target,new in new_text.items():
  if target.startswith('job0/runtime/'):
   key=target.removeprefix('job0/runtime/')
   if key in freeze['sha256'] and new!=old_text[target]:
    assert freeze['sha256'][key]==H(old_text[target]),key
    updates[('sha256',key)]=(H(old_text[target]),H(new))
 new=patcher.replace_json_scalars(old,updates)
 (DEST/rel).write_bytes(new)
 next(x for x in rows if x['relative']==rel).update(bytes=len(new),SHA=H(new))
 deltas.append(dict(relative=rel,old_SHA=H(old),new_SHA=H(new),scope='derived manifest source-hash entries only'))
 typed=json.loads((L/'NORMAL_H1_PPO86B_400N50_NEW86_SOURCE_PREPARATION_V1/reports/NORMAL_H1_TYPED40050_ORIGINAL_FULLSTATE_CPU_ACTUAL_V1.json').read_bytes())
 assert typed['passed'] and typed['source']['original_Adam_step']==832460
 rows.append(dict(relative='job0/source/NORMAL_H1_86B138_N20K_PPO50_GAS400_NOT_GPU_ADMITTED.pt',local_path=typed['new_source']['path'],bytes=typed['new_source']['bytes'],SHA=typed['new_source']['SHA'],index_kind='actual typed source producer witness; not opened'))
 # Tiny source-clock proof uses only the actual edited methods, without SDK/model import.
 tree=ast.parse(new_text['h1_step270_sdk_runtime_candidate.py']);cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='H1Step270Phase')
 methods=[n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name in ('public_request','finish_control_before_selected_reset')]
 assert len(methods)==2
 tiny=ast.Module(body=[ast.ClassDef(name='Clock',bases=[],keywords=[],body=methods,decorator_list=[])],type_ignores=[]);ast.fix_missing_locations(tiny);ns={};exec(compile(tiny,'actual_H1_clock_methods','exec'),ns);c=ns['Clock']();c.age_control=0
 active=[]
 for i in range(100):
  if c.public_request():active.append(i)
  c.finish_control_before_selected_reset()
 assert active==list(range(50,90)) and c.age_control==200
 # Restore helper source is byte-identical; the original bank still selects74 of133.
 helper=module('normal_H1_exact400_bank_helper_local_source',DEST/RT/'gas400_reset_bank_exact_compatibility_v1.py');bankproof=helper.check_runtime_source(DEST/RT)
 assert bankproof['pose_ranges']['all_poses']==133 and bankproof['pose_ranges']['original_height_filter_selected_poses']==74
 result=dict(kind='normal_H1_PPO86B40050_runtime_candidate_v1',source_only=True,files=rows,source_changes=deltas,source_clock_CPU=dict(passed=True,actual_method_source_executed=True,policy_control_request_indices=[50,89],seconds=[1.,1.8],public_phase_ticks_100Hz=True,physical_landing12_recovery200_unchanged=True),exact_original133pose74selection_gas400_helper_CPU=bankproof,typed_model_producer=typed['new_source'],original_policy_role='normal_H1_PPO_not_native',original_reward_task270_mean_overflow_D1_D7_actor35_critic38_STD_Adam_retained=True,constructor_LR=.00038443359375000017,Adam_source=832460,new_targetSDK_CUDA_fullrestore_native24_firstPPO_and_original72GO_pending=True,no_model_USD_or_large_binary_opened=True,sole72_writer_required=True,original_frozen_qualification_not_inherited=True)
 (B/'NORMAL_H1_COMPLETE_SOURCE_INPUT_MANIFEST_NOT_GPU_ADMITTED_V1.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(dict(passed_source_clock_and_exact_bank_helper_CPU=True,source_files=len(rows),changed_source_files=len(deltas),manifest=str(B/'NORMAL_H1_COMPLETE_SOURCE_INPUT_MANIFEST_NOT_GPU_ADMITTED_V1.json'))))
if __name__=='__main__':
 try:main()
 except BaseException:
  import traceback
  (B/'SOURCE_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json').write_text(json.dumps(dict(epoch=time.time(),traceback=traceback.format_exc(),no_model_network_or_GPU=True),indent=2));raise
