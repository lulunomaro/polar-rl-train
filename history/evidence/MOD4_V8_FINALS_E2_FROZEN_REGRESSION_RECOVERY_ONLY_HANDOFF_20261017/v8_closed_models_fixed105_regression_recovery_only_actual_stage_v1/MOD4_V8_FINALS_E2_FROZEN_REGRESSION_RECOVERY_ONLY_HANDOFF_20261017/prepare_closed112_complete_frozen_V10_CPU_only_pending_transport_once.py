"""New exact-weight frozen package from the admitted closed101 evaluator; CPU only."""
from pathlib import Path
import ast,hashlib,json,shutil,sys,time,zipfile,os
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
J=Path(__file__).resolve().parent;W=J.parent;R=J/'reports';I=W/'MOD4_TWO72_V6_FINALS_LATEST101_FROZEN_SAME_SCOPE_HANDOFF_20261017';A=I/'e2_closed101_frozen_prepared_v7/payload';F=J/'e2_latest_closed112_frozen_source_CPU_v1';E=J/'e2_closed112_frozen_prepared_v10';Q=E/'payload';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 proof=json.loads((R/'E2_LATEST_CLOSED112_SAME_RECIPE_FROZEN_SOURCE_CONTROLLER_CPU_PREPARED.json').read_bytes());assert proof['passed_source_controller_CPU_only'] and proof['source']['updates112'] and not E.exists();E.mkdir();shutil.copytree(A,Q,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for name in ('e2_closed112_source_guard_CPU_v1.py','e2_closed112_single35_CPU_v1.py'):shutil.copy2(F/name,Q/name)
 p=Q/'source/E2_closed112.pt';shutil.copy2(F/'E2_actual_latest_closed112.pt',p);assert H(p)==proof['source']['SHA']=='ca6fc2662d5bfe4d33ad63b370389504961a3c2500b4b476c1c527b17b12b2be'
 adapter=(A/'e2_closed101_retention_single_adapter_v7.py').read_text('utf8').replace('e2_closed101_single35_CPU_v1','e2_closed112_single35_CPU_v1').replace('E2_CLOSED101','E2_CLOSED112').replace('single_E2_closed101','single_E2_closed112');(Q/'e2_closed112_retention_single_adapter_v10.py').write_text(adapter,encoding='utf8',newline='\n')
 s=(A/'retention_native_witness_v8.py').read_text('utf8').replace('from e2_closed101_source_guard_CPU_v1 import','from e2_closed112_source_guard_CPU_v1 import').replace('from e2_closed101_retention_single_adapter_v7 import','from e2_closed112_retention_single_adapter_v10 import');shutil.copy2(A/'retention_native_witness_v8.py',Q/'historical_original_components/CLOSED101_V7_retention_native_witness_v8.py');(Q/'retention_native_witness_v8.py').write_text(s,encoding='utf8',newline='\n')
 worker=(A/'e2_frozen_worker_v7.py').read_text('utf8').replace('E2_CLOSED101','E2_CLOSED112').replace('MANIFEST_V7','MANIFEST_V10').replace('FROZEN_V7_20261017','FROZEN_V10_20261017').replace('from e2_closed101_source_guard_CPU_v1 import','from e2_closed112_source_guard_CPU_v1 import');(Q/'e2_frozen_worker_v10.py').write_text(worker,encoding='utf8',newline='\n')
 parent=(A/'e2_frozen_parent_v7.py').read_text('utf8').replace('e2_frozen_worker_v7.py','e2_frozen_worker_v10.py').replace('E2_CLOSED101_FROZEN_COMPLETE_MANIFEST_V7.json','E2_CLOSED112_FROZEN_COMPLETE_MANIFEST_V10.json');(Q/'e2_frozen_parent_v10.py').write_text(parent,encoding='utf8',newline='\n')
 recipe=json.loads((F/'E2_CLOSED112_EXACT_SAME_SIGNED4_RECIPE_CPU_PREPARED.json').read_bytes());assert recipe['source']['SHA']==proof['source']['SHA'] and recipe['source']['updates112'];(Q/'E2_CLOSED112_SIGNED4_RECIPE_EXACT_CPU_V1.json').write_text(json.dumps(recipe,indent=2),encoding='utf8')
 sys.path[:0]=[str(Q)];from e2_closed112_source_guard_CPU_v1 import validate_E2_source;from e2_closed112_single35_CPU_v1 import Single35
 ck=torch.load(p,map_location='cpu',weights_only=False);rng=torch.get_rng_state().clone();validate_E2_source(ck);actor=Single35(p,88,'cpu');assert actor.exact() and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 manifest=json.loads((A/'E2_CLOSED101_FROZEN_COMPLETE_MANIFEST_V7.json').read_bytes());manifest.update(version=10,source=proof['source'],source_relative='source/E2_closed112.pt',source_guard='e2_closed112_source_guard_CPU_v1.py',recipe=recipe,old101_native_not_new105_weight_admission=True,new_source_own_native120_and_independent_CPU_required=True)
 rows=[]
 for p in sorted(x for x in Q.rglob('*') if x.is_file() and '__pycache__' not in x.parts and x.suffix!='.pyc'):
  if p.suffix=='.py':ast.parse(p.read_text('utf8'))
  rows.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
 manifest.update(files=rows,package_files_v8=[dict(relative=r['relative'],bytes=r['bytes'],sha256=r['SHA']) for r in rows]);mf=Q/'E2_CLOSED112_FROZEN_COMPLETE_MANIFEST_V10.json';mf.write_text(json.dumps(manifest,indent=2),encoding='utf8');bundle=E/'E2_CLOSED112_COMPLETE_FROZEN_PAYLOAD_V10.zip'
 with zipfile.ZipFile(bundle,'x',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
  for row in rows:z.write(Q/row['relative'],row['relative'])
  z.write(mf,mf.name)
 out=dict(epoch=time.time(),passed_complete_payload_CPU_only=True,source=proof['source'],manifest=dict(path=str(mf),bytes=mf.stat().st_size,SHA=H(mf)),package=dict(path=str(bundle),bytes=bundle.stat().st_size,SHA=H(bundle)),worker=dict(path=str(Q/'e2_frozen_worker_v10.py'),SHA=H(Q/'e2_frozen_worker_v10.py')),parent=dict(path=str(Q/'e2_frozen_parent_v10.py'),SHA=H(Q/'e2_frozen_parent_v10.py')),files=len(rows),source_guard9_negative_cases_already_actual=proof['negative_cases'],source9_STD_literalexact_CPU_RNG_unchanged0CUDA=True,physics_reward_DR_command_hardware_and_all_strict_prefix_guard_code_exact_reused_except_source_bindings=True,old101_native_not_new105_qualification=True,unused_native120_then_full1500_every_saved_physical_row_CPU_required=True,matched_actual_initial_not_assumed=True,no_target_GPU_native_or_skill_pass_yet=True)
 with (R/'E2_CLOSED112_SIGNED4_COMPLETE_FROZEN_V10_CPU_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(complete_CPU_package=True,source_SHA=proof['source']['SHA'],files=len(rows),bytes=bundle.stat().st_size,no_GPU_yet=True)),flush=True)
if __name__=='__main__':main()
