"""Derive existing bounded project transport; reads TEXT only, never model/bank/USD."""
from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent;L=B.parent;T=L.parent
S=L/'E2_PPO50_gas400_source_preparation_20261028';P=L/'NEW86_W35_ADAPTED92_N20K_PROFILE_REGRESSION_SOURCE_V1'
MODEL='b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1'
def Hraw(raw):return hashlib.sha256(raw).hexdigest()
def write(n,raw):
 p=B/n
 with p.open('xb') as f:f.write(raw)
def derive(source,name,replacements):
 raw=(P/source).read_bytes();text=raw.decode('utf8');proof=[]
 for old,new in replacements:
  count=text.count(old);assert count>0,(name,old);text=text.replace(old,new);proof.append(dict(old=old,new=new,count=count))
 ast.parse(text);write(name,text.encode());return dict(source=str(P/source),source_SHA=Hraw(raw),target=name,target_SHA=Hraw(text.encode()),literal_replacements=proof)
def main():
 proof=[];write('project_clone_launch_helpers_v1.py',(P/'project_clone_launch_helpers_v1.py').read_bytes())
 sup='detached_E2_new86_frozen_profile_supervisor_once_v1.py';cpu='E2_new86_target_source_SDK_metadata_admission_v1.py';worker='evaluate_E2_adapted93_new86_frozen900_once_v1.py';remote='remote_E2_new86_profile_install_and_detach_v1.py';entry='upload_admit_detach_NEW86_E2_final93_profiles_secure_stdin_UNUSED_once_v1.py'
 proof.append(derive('detached_W35_new86_frozen_profile_supervisor_once_v2_RAM_disk_preserved.py',sup,[('W35','E2'),("task['controls']==1200","task['controls']==900"),('evaluate_E2_adapted92_originalN20K_frozen_profiles_once_v1.py',worker),('BOUNDED_FROZEN_E2_N20K_PROFILES_ACTUAL.json','BOUNDED_FROZEN_E2_N20K_PROFILES_ACTUAL.json')]))
 # Add actual native24 receipt to successful execution; rc0 alone never suffices.
 text=(B/sup).read_text(encoding='utf8');old="and result.exists() and not errs";assert text.count(old)==1
 text=text.replace(old,"and result.exists() and (out/'ACTUAL_NATIVE24_E2_40050_CLOCK_QUEUE.json').exists() and not errs")
 (B/sup).write_text(text,encoding='utf8',newline='');proof[-1]['required_native24_success_extension']=True
 # One pass only; filenames/role remain explicit E2, no W35 command logic copied.
 proof.append(derive('remote_W35_new86_profile_install_and_detach_v2_RAM_disk.py',remote,[('W35','E2'),('source_SDK_CPU_admission_v2_self_identity.py','source_SDK_metadata_admission_v1.py'),('E2_new86_target_FINAL92_','E2_new86_target_'),('E2_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V1.json','E2_TARGET_SOURCE_SDK_METADATA_ACTUAL.json'),('detached_E2_new86_frozen_profile_supervisor_once_v2_RAM_disk_preserved.py',sup),('MOD4_E2_ADAPTED92_NEW86_ORIGINAL_N20K_FROZEN_PROFILES_V1','MOD4_E2_ADAPTED93_NEW86_FROZEN_PROFILE_DOMAIN_V1'),('qualified E2 fixed92 final78','qualified E2 fixed93 final92'),('ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f',MODEL),('controls=1200','controls=900'),("manifest_SHA=v['manifest_SHA'],full_WM_tap_included=False","manifest_SHA=v['manifest_SHA'],worker_SHA=v['worker_SHA'],domain_kind='E2_WORLD_MOVING_SIGNED4',original_Adam=859300,original_LR=.00022500000000000002,full_WM_tap_included=False")]))
 proof.append(derive('upload_admit_detach_NEW86_W35_final92_frozen_profiles_secure_stdin_UNUSED_once_v2_RAM_disk.py',entry,[('W35','E2'),('remote_E2_new86_profile_install_and_detach_v2_RAM_disk.py',remote),('FROZEN_NEW86_E2_FROZEN_PROFILE_SOURCE_INDEX_V2.json','FROZEN_E2_93_NEW86_PROFILE_DOMAIN_SOURCE_INDEX_V1.json'),('E2_ADAPTED92_N20K_PROFILE_20261029v2','E2_ADAPTED93_PROFILE_DOMAIN_20261029v1'),('NEW86_E2_WHOLECPU_CUDA_NATIVE24_ORIGINAL_RETURNED_ACTUAL.json','NEW86_E2_METADATA_WITNESS_AND_DETACHED_RETURNED_ACTUAL.json'),("source_SHA=manifest['typed_source_SHA'],remote_code_SHA","source_SHA=manifest['typed_source_SHA'],worker_SHA=index['executable_source_SHAs']['"+worker+"'],remote_code_SHA")]))
 witness=T/'MOD4_H1_FLAT05_TERMINAL_EXPOSURE_RESOURCE_V93_20261028/reports/E2_93_NEW_FORMAL_INITIAL_WHOLE_CPU_ACTUAL_V1.json';raw=witness.read_bytes();w=json.loads(raw);assert w['passed'] and w['model']['SHA']==MODEL and w['adaptive_LR']==.00022500000000000002
 write('E2_93_QUALIFIED_FORMAL_CPU_WITNESS.json',raw)
 base=json.loads((S/'E2_COMPLETE_INSTALL_MANIFEST_V1.json').read_bytes());common=json.loads((P/'W35_NEW86_COMPLETE_INPUT_MANIFEST_V2.json').read_bytes());rows=[]
 for r in base['files']:
  if r['relative'].endswith('.pt') or r['relative']=='E2_PPO50_gas400_finite_worker_v1.py':continue
  rows.append(r)
 rows.append(dict(relative='source/E2_ADAPTED93_FINAL92.pt',local_path=w['model']['local_path'],bytes=w['model']['bytes'],SHA=MODEL))
 executable=['project_clone_launch_helpers_v1.py',sup,cpu,worker,remote,entry,'e2_original_profile_catalog_candidate_v1.py','e2_profile_domain_telemetry_v1.py','lossless_snapshot_pinned75d683.py']
 for n in executable+['E2_93_QUALIFIED_FORMAL_CPU_WITNESS.json']:
  raw=(B/n).read_bytes();rows.append(dict(relative=n,local_path=str(B/n),bytes=len(raw),SHA=Hraw(raw)))
 assert len({r['relative'] for r in rows})==len(rows)
 value=dict(kind='E2_93_NEW86_SOURCE_ONLY_COMPLETE_INPUT_V1',files=rows,RSL_sources=common['RSL_sources'],SDK_math_SHA=common['SDK_math_SHA'],typed_source_SHA=MODEL,model_SHA=MODEL,qualified_formal_CPU_witness_SHA=Hraw(witness.read_bytes()),historical_input_manifest=str(S/'E2_COMPLETE_INSTALL_MANIFEST_V1.json'),historical_input_manifest_SHA=Hraw((S/'E2_COMPLETE_INSTALL_MANIFEST_V1.json').read_bytes()),no_binary_PT_USD_NPZ_bytes_or_stat_read_during_assembly=True,coverage=dict(controls=900,warmup=100,steady=800,seconds=18,full_original_skill_acceptance_claim=False),target_backend='new86',source_only=True,no_training_writer_or_GO=True)
 write('E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json',(json.dumps(value,indent=2)+'\n').encode())
 write('E2_BOUND_SOURCE_DERIVATION_ACTUAL.json',(json.dumps(dict(passed=True,derivations=proof,only_TEXT_read=True,no_remote_SDK_GPU_or_model_call=True),indent=2)+'\n').encode())
 print(json.dumps(dict(passed=True,files=len(rows),source_only=True)))
if __name__=='__main__':main()
