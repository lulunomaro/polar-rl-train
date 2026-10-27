"""New R5 method diagnostic only. Preserve old700 physics; no training or goal claim."""
from pathlib import Path
import hashlib,json,sys,tarfile,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;W=T.parent;R=S/'reports'
N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027'
L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
P=L/'native87R5_frozen_step_acceptance_preparation_v2_own_pid_only'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 R.mkdir(exist_ok=True)
 assert not (S/'BINDING.json').exists()
 sys.path.insert(0,str(P))
 from prepare_native87R5_closed_frozen_selection_unused_once import bind_new_eval
 from native87R5_own_pid_out_guard_v1 import records_from_evidence
 plan=json.loads((N/'reports/NATIVE87R5_CLOSED_FROZEN_SELECTION_DECLARED_ACTUAL.json').read_bytes())
 first=N/'reports/AVAILABLE_TWO_NATIVE87R5_FIRST_GO_ACTUAL_NEW_PREUPDATE_PI_RETURNED_ACTUAL.json'
 plan['evidence_pins']['first_identity']=dict(path=str(first),SHA=H(first))
 values={k:json.loads(Path(v['path']).read_bytes()) for k,v in plan['evidence_pins'].items()}
 names=('native87R5_frozen_single_sdk_entry_unused_once.py','native87R5_frozen_acceptance_contract_v1.py','native87R5_frozen_acceptance_driver_v1.py','native87R5_eval_environment_v1.py','native87R5_own_pid_out_guard_v1.py')
 codes={name:H(P/name) for name in names}
 root='/home/lc01/Zonglin Li/zonglin2/tasks/H1native87R5_old700_fixed3_diagnostic_20261027'
 relatives={k:'evidence/'+k+'.json' for k in plan['evidence_pins']}
 q=bind_new_eval(plan,eval_root=root,runtime_root=root+'/runtime',model_eval_relative='qualified_model/native_supermimic_H1_final.pt',GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',eval_code_pins=codes,evidence_eval_relatives=relatives)
 q.update(known_qualified_own_processes=records_from_evidence(values),hardware_scope='OLD700_CONFIG_DIAGNOSTIC_NOT_400N_HARDWARE_ACCEPTANCE',old_physics_preserved_no_spring_rewrite=True,not_hardware_aligned_goal_completion=True)
 put(S/'BINDING.json',q)
 files=[]
 def add(source,relative,SHA=None,bytes_=None):
  source=Path(source);assert source.is_file()
  if bytes_ is not None:assert source.stat().st_size==bytes_
  if SHA is not None and source.suffix.lower() not in ('.pt','.pth'):assert H(source)==SHA
  files.append(dict(local=str(source),relative=relative,bytes=source.stat().st_size,SHA=SHA))
 add(S/'BINDING.json','BINDING.json',H(S/'BINDING.json'))
 for name,digest in codes.items():add(P/name,'code/'+name,digest)
 for key,row in plan['evidence_pins'].items():add(row['path'],relatives[key],row['SHA'])
 for row in plan['runtime_files']:add(Path(plan['source_runtime_local'])/row['relative'],'runtime/'+row['relative'],row['SHA'],row['bytes'])
 add(plan['source_model']['local_path'],q['model_eval_relative'],plan['source_model']['SHA'],plan['source_model']['bytes'])
 assert len({r['relative'] for r in files})==len(files)
 with tarfile.open(S/'PINNED_NEW_EVAL_INPUTS.tar','x') as tar:
  for row in files:tar.add(row['local'],arcname=row['relative'],recursive=False)
 archive=dict(path=str(S/'PINNED_NEW_EVAL_INPUTS.tar'),bytes=(S/'PINNED_NEW_EVAL_INPUTS.tar').stat().st_size,SHA=H(S/'PINNED_NEW_EVAL_INPUTS.tar'))
 put(S/'INPUT_TRANSFER_INDEX.json',dict(epoch=time.time(),files=files,archive=archive,new_purpose_only=True,no_original_PT_load_or_requalification=True))
 put(R/'SOURCE_PREPARED_NOT_EXECUTED_ACTUAL.json',dict(epoch=time.time(),hardware_scope=q['hardware_scope'],fixed_seeds=q['seeds'],source_SHA=q['source_model']['SHA'],source_model_not_promoted=True,new_N1_SDK_or_actor_not_run=True,no_learning_or_account_write=True,files=len(files),archive=archive))
 print(json.dumps(dict(prepared=True,files=len(files),archive_bytes=archive['bytes'],source=q['source_model']['SHA'],hardware_scope=q['hardware_scope'])))
if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(exist_ok=True)
  put(R/('SOURCE_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_remote_or_actor=True));raise
