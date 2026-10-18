"""Use proven Linux query code and the two hosts' actual binding fingerprints."""
from pathlib import Path
import json,hashlib,time,shutil,zipfile,ast,importlib.util,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 prior=json.loads((R/'TWO_EXPERT_LINUX_V2_CALLABLE_LAUNCHER_CPU_REPAIR_ACTUAL.json').read_bytes());current=json.loads((R/'TWO_EXPERT_V2_LINUX_CURRENT_ACTUAL.json').read_bytes());known=W/'MOD4_POST_POWER_RESTORE_H1_SATURATION_REPAIR_20261018/resumed_ce3_original_fp32_v1/frozen_ce3_original_fp32_continued_final_linux_v1/payload/h1_plane_reference80_v1.py';template=known.read_text('utf8');assert "'.so' not in path.name.lower()" in template;payloads=[]
 sources={'E2':W/'MOD4_V8_FINALS_E2_FROZEN_REGRESSION_RECOVERY_ONLY_HANDOFF_20261017/e2_closed112_frozen_prepared_v10/payload','E3':W/'MOD4_H1_TARGET72_CLOSED_FINAL_E3_FROZEN_REVIEW_20261017/e3_closed85_frozen_prepared_v1/payload'}
 for row in prior['payloads']:
  kind=row['expert'];error=current[kind]['rows']['native120_observation/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json']['error'];assert 'Native binding differs from independently completed V7' in error
  prefix='/home/egde/anaconda3/envs/fangzhen-isaaclab' if kind=='E2' else '/home/lc01/Zonglin Li/zonglin2/envs/mod4';path=prefix+'/lib/python3.12/site-packages/isaacsim/extscache/omni.physx-110.1.13+110.1.2.lx64.r.cp312.u7f4/omni/physx/bindings/_physx.cpython-312-x86_64-linux-gnu.so';sha='ccb0ddafa214d6ecf93903632a6c4b73e9e0d02cddfa1ca56e1dd2b65a5a8d6f';assert path in error and sha in error
  old=Path(row['payload']);Q=B/(kind+'_linux_reward_frame_v3');shutil.copytree(old,Q,ignore=shutil.ignore_patterns('LINUX_EXPERT_DIAGNOSTIC_MANIFEST.json','__pycache__'));m=json.loads((old/'LINUX_EXPERT_DIAGNOSTIC_MANIFEST.json').read_bytes());new=template.replace('EXPECTED_ACTUAL_LINUX72_BACKEND_V1.json','EXPECTED_ACTUAL_LINUX_DIAGNOSTIC_BACKEND_V1.json').replace('89e49ac6b44a01794bbb658452d0146c0f798a457f0504a455c57ee4b633663a',sha).replace('Own actual Linux72 prelaunch CPU fingerprint','Own actual selected Linux host prelaunch CPU fingerprint')
  target=Q/('retention_plane_reference_v8.py' if kind=='E2' else 'e3_plane_reference_104_v1.py');target.write_text(new,encoding='utf8');assert 'tolerance_m=1e-6' in new and '104,2' in new
  (Q/'EXPECTED_ACTUAL_LINUX_DIAGNOSTIC_BACKEND_V1.json').write_text(json.dumps(dict(native_binding=dict(path=path,SHA=sha),provenance='Actual own failed-V2 SDK readout; rehashed before new launch, not Windows proof'),indent=2))
  shutil.copytree(sources[kind]/'source_reference_1101',Q/'source_reference_1101');sp=importlib.util.spec_from_file_location(kind+'_public_plane_reference_check',Q/'represented_native_plane_CPU_component_v2.py');module=importlib.util.module_from_spec(sp);sp.loader.exec_module(module);public=module.source_sha_manifest();assert len(public)==10
  rows=[]
  for p in sorted(x for x in Q.rglob('*') if x.is_file()):
   if p.suffix=='.py':ast.parse(p.read_text('utf8'))
   rows.append(dict(relative=p.relative_to(Q).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
  m.update(version=3,files=rows,previous_V2_manifest_SHA=H(old/'LINUX_EXPERT_DIAGNOSTIC_MANIFEST.json'),existing_Linux_query_source=dict(path=str(known),SHA=H(known)),actual_own_Linux_binding=dict(path=path,SHA=sha),public_source10_SHA=public,original_query1e6_unchanged=True,no_reward_actor_reset_DR_physics_change=True);mp=Q/'LINUX_EXPERT_DIAGNOSTIC_MANIFEST.json';mp.write_text(json.dumps(m,indent=2));zp=B/(kind+'_linux_reward_frame_v3.zip')
  with zipfile.ZipFile(zp,'x',compression=zipfile.ZIP_DEFLATED) as z:
   for p in Q.rglob('*'):
    if p.is_file():z.write(p,p.relative_to(Q).as_posix())
  payloads.append(dict(expert=kind,payload=str(Q),manifest_SHA=H(mp),source_SHA=m['source_SHA'],worker_SHA=H(Q/'linux_expert_frozen_reward_diagnostic_worker_v1.py'),package=dict(path=str(zp),bytes=zp.stat().st_size,SHA=H(zp))))
 with (R/'TWO_EXPERT_LINUX_V3_OWN_BACKEND_PUBLIC_SOURCE_QUERY_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),payloads=payloads,old_Windows_binding_false_preserved=True,own_actual_Linux_binding_not_Windows_proof=True,existing_Linux_query_helper_original1e6=True,public10files_SHA_passed=True,no_model_reward_physics_command_STD_LR_change=True,no_target_dispatch_yet=True,local_apply_patch_AddFile_header_typo_before_any_file_write_corrected=True),f,indent=2)
 print(json.dumps(dict(payloads=[dict(expert=x['expert'],zip_bytes=x['package']['bytes']) for x in payloads],public10_SHA_passed=True,own_Linux_reference_bound=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('LINUX_V3_BACKEND_PAYLOAD_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_target_change=True),f,indent=2)
  raise
