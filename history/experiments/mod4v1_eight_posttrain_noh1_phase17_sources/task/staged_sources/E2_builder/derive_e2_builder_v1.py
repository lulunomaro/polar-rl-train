"""Text-only E2 builder derivation. No E0 environment/config is imported/executed."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent;STAGED=HERE.parent
source=STAGED/'E0_builder/build_e0_mod4v1_sources.py'
s=source.read_text(encoding='utf-8')

def change(old,new):
    global s
    if old not in s:raise ValueError('E2 builder derivation anchor missing: '+old[:120])
    s=s.replace(old,new)

s=s.replace('E0','E2').replace('e0','e2')
s=s.replace('31984','42822').replace('31985','42823').replace('641200','859300').replace('14031973','14615089').replace('.00038443359375000017','.00022500000000000002')
s=s.replace('a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a','b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1')
s=s.replace('MOD4_E2_PPO50_GAS400_2610v89d','MOD4_E2_PPO50_GAS400_2610v93').replace('final_valid_update82.pt','final_valid_update92.pt').replace('prior_new_PPO_updates=82','prior_new_PPO_updates=92')
s=s.replace('MOD4V1_E2_SELECTED42822_FULLD0D7_FLAT_V1','MOD4V1_E2_SELECTED42822_FULLD0D7_WORLD_SIGNED4_V1')
s=s.replace('1dbde5972c65baf8842bc82024fe7ddfd6393d73a51137cc9880ed6310ff1af1','ad1d4681d85d18dde8a545dbf58fc2460173faf556b6102c96f5eef69c33e80f')
s=s.replace('import argparse, ast, difflib, hashlib, importlib.util, json','import argparse, ast, difflib, hashlib, importlib.util, json, time, traceback')
change("old=night/'night_frozen_experts_PPO50_gas400_adaptation_20261027/E2_runtime50_gas400_candidate_v1'", "prep=night/'E2_PPO50_gas400_source_preparation_20261028'\n    old=prep/'runtime_candidate_v1'")
change("freeze=json.loads(freeze_text)['sha256']", "freeze=json.loads(freeze_text)['sha256']\n    install_text,install_ref=read(prep/'E2_COMPLETE_INSTALL_MANIFEST_V1.json','0e27157ce13a88748504c02a5702b7d6027ca14ca3224e4c6d4d5bcbe52175fd');refs.append(install_ref);rows={r['relative']:r for r in json.loads(install_text)['files']}")
change("text,ref=read(mod/name,freeze['isaac/mod4/'+name]);refs.append(ref);return text", "row=rows[P+name];text,ref=read(Path(row['local_path']),row['SHA']);refs.append(ref);return text")
change("read(night/'E2_PPO50_gas400_logger_presave_V5_source_candidate_20261027/E2_PPO50_gas400_finite_worker_v5_writer_before_presave.py')", "read(prep/'E2_PPO50_gas400_finite_worker_v1.py',rows['E2_PPO50_gas400_finite_worker_v1.py']['SHA'])")
change("source('train_chassis_pd_resume_ppo.py')", "source('train_E2_full_resume_v1.py')")
change("read(night/'night_frozen_experts_PPO50_gas400_adaptation_20261027/E2_original_run_manifest_frozen_v1.json'", "read(prep/'original_run_manifest.json'")
change("root/'MOD4_E2_PPO50_GAS400_REMOTE4090_RESOURCE_V89D_20261027/reports/E2_89D_FORMAL_FINAL_WHOLE_INITIAL_CPU_REVIEW_ACTUAL_V2.json'", "root/'MOD4_H1_FLAT05_TERMINAL_EXPOSURE_RESOURCE_V93_20261028/reports/E2_93_NEW_FORMAL_INITIAL_WHOLE_CPU_ACTUAL_V1.json'")
change("cpu,cr=read(cpu_path);", "cpu,cr=read(cpu_path,'d741414f54c22bff910541560e3af689f0c36afa507fb416e7beb7dd632468bb');")
change("'spring_pressure_checkpoint.py','gas_damping_checkpoint.py','chassis_pd_checkpoint.py']", "'spring_pressure_checkpoint.py','gas_damping_checkpoint.py','chassis_pd_checkpoint.py','e2_command_checkpoint_v1.py']")
change("        emit(P+name,text,initial)", "        if name=='e2_command_checkpoint_v1.py':\n            text=replace(text,'hashlib.sha256(Path(path).read_bytes()).hexdigest()','cached_H(path)')\n        emit(P+name,text,initial)")
change("    flat=replace(flat,\"env._gas400_reset_bank_compatibility_receipt = require_exact_gas400_reset_bank(\",\n                 \"env._mod4v1_e2_bank_compatibility = require_mod4v1_flat_reset_bank(\")", "    flat=replace(flat,\"require_exact_gas400_reset_bank(source,task.MOD4_ISAAC/'import_contract.json',raw,actual_contract_SHA=actual)\",\n                 \"env._mod4v1_e2_bank_compatibility = require_mod4v1_flat_reset_bank(source,task.MOD4_ISAAC/'import_contract.json',raw,actual_contract_SHA=actual)\")")
change("'from chassis_pd_training_env import ChassisPDMod4Env as Mod4Env'", "'from e2_h1_flat_environment_v1 import E2H1FlatEnv as Mod4Env'")
change("\\nfrom chassis_pd_training_env import ChassisPDMod4Env as Mod4Env\")", "\\nassert os.environ.get('OWN_E2_H1_KIND')=='E2_WORLD_MOVING_SIGNED4'  # H1 branch is never enabled\\nfrom e2_h1_flat_environment_v1 import E2H1FlatEnv as Mod4Env\")")
change("trainer.index('    from chassis_pd_checkpoint import install_chassis_pd_save_contract',start)", "trainer.index('    from e2_command_checkpoint_v1 import install_e2_save_contract',start)")
s=s.replace("SOURCE_SHA='54f53453a3f793cea990f0608c0a2c3bd3e5d37aecf41bb8817691af5fea0371'", "SOURCE_SHA='5b5d1ee88bf9f56f865378d82d9f8864fa5ec2859f636c9b33b07558323d7f6e'")
s=s.replace('E2_N20K_PPO50_GAS400_SOURCE_NOT_GPU_ADMITTED.pt','E2_83B90_N20K_PPO50_GAS400_SOURCE_NOT_GPU_ADMITTED.pt')
change("entry=mod/'train_chassis_pd_resume_ppo.py'", "entry=mod/'train_E2_full_resume_v1.py'")
change("    worker=worker.replace(\"'E2_PPO50_GAS400_v1'\",\"'E2_SELECTED42822_MOD4V1_FLAT_FULLDR'\")", "    worker=worker.replace(\"'E2_PPO50_GAS400_v1'\",\"'E2_SELECTED42822_MOD4V1_WORLD_SIGNED4_FULLDR'\").replace('6.666666666666667e-05','.00022500000000000002')")
change("worker.replace('==31903','==42822').replace('{639560}','{859300}').replace('639560+20*updates','859300+20*updates')", "worker.replace('==42731','==42822').replace('{857460}','{859300}').replace('857460+20*updates','859300+20*updates')")
a=s.index('    worker=replace(worker,\"assert real._gas400_reset_bank_compatibility_receipt')
b=s.index('    worker=replace(worker,\"value[',a)
s=s[:a]+'''    worker=replace(worker,"   from gas400_reset_bank_exact_compatibility_v1 import check_runtime_source\\n   bankproof=check_runtime_source(mod);assert bankproof['passed'] and bankproof['pose_ranges']['original_height_filter_selected_poses']==74", "   bankproof=real._mod4v1_e2_bank_compatibility;assert bankproof['new_contract_SHA']==identity.contract_sha256 and bankproof['pose_ranges']['original_height_filter_selected_poses']==74\\n   assert real._mod4v1_e2_nominal_guard.restore_completed")
'''+s[b:]
# E2 worker uses one MORE indentation space than original E0 worker inside work/save.
change("source_sha256\\\"]==SOURCE_SHA", "source_sha256\\\"]==SOURCE_SHA") if False else None
s=s.replace("read(receipt)[\"source_sha256\"]", "read(receipt).get(\"source_sha256\",read(receipt).get(\"source_SHA\"))")
# Align inserted work/save continuation lines to E2's original nesting.
s=s.replace('\\n  for receipt in receipts:', '\\n   for receipt in receipts:').replace('\\n   if receipt.name in required:', '\\n    if receipt.name in required:')
s=s.replace('\\n   value[', '\\n    value[')
s=s.replace('\\n  runner.current_learning_iteration=42823', '\\n   runner.current_learning_iteration=42823').replace('\\n  try:runner.learn', '\\n   try:runner.learn')
# Source-family-specific report and current typed metadata.
s=s.replace('E2_MOD4V1_FLAT_STAND_RUN_PURE_WORLD','E2_MOD4V1_WORLD_MOVING_SIGNED4').replace('original_E2_flat_stand_run_pure_world','original_E2_world_moving_signed4')
s=s.replace("task='E2_flat_stand_run_pure_world_NOT_H1jump_NOT_RM70'", "task='E2_WORLD_MOVING_SIGNED4_NOT_H1jump_NOT_RM70'")
s=s.replace('historical_E2_flat_reset_command_and_DR_scope_exactly_reused','historical_E2_world_signed4_reset_command_and_DR_scope_exactly_reused').replace('historical_E2_flat_scope_reuse_receipt_SHA','historical_E2_world_signed4_scope_reuse_receipt_SHA')
s=s.replace("'E2_flat_stand_run_pure_world_NOT_H1jump_NOT_RM70'", "'E2_WORLD_MOVING_SIGNED4_NOT_H1jump_NOT_RM70'")
# E2-specific provenance; do not copy E0's reader failures into E2's trial history.
a=s.index('    error_history,er=read(');b=s.index("    files['SOURCE_DIFF.patch']",a)
s=s[:a]+"    template,template_ref=read(STAGED/'E0_builder/build_e0_mod4v1_sources.py');driver,driver_ref=read(HERE/'derive_e2_builder_v1.py');refs.extend([template_ref,driver_ref])\n"+s[b:]
change("base_source_freeze=fr,base_files=[dict(relative='runtime/'+k,SHA=v,original_local_path=str(old/k)) for k,v in freeze.items()]", "base_source_freeze_historical=fr,original_complete_install_manifest=install_ref,base_files=[r for k,r in rows.items() if k.startswith('runtime/') and Path(k).suffix.lower() not in ('.pt','.pth')]")
s=s.replace('Original 89D flat/all commands retained: stand .1, pure .3, moving .2, world directional V=.5, signed spins; jump script probability0.', 'Original E2 flat/world-direction commands retained: stand .1, pure .3, moving .2, world V=.5, moving signed yaw cap4, pure cap4pi and complete12s transition; jump probability0. Original E2H1FlatEnv is legitimate only under pinned OWN_E2_H1_KIND=E2_WORLD_MOVING_SIGNED4; its H1 manual-jump step branch is unreachable. E2_moving4_command_state and its private mode RNG remain in the original restore/save chain.')
s=s.replace('derived from E2\'s own train_chassis_pd_resume_ppo.py', "derived from E2's own train_E2_full_resume_v1.py")
s=s.replace('prior82 saved by old RSL', 'prior92 saved by old RSL')
s=s.replace("if __name__=='__main__':main()", "if __name__=='__main__':\n    try:main()\n    except BaseException:\n        error_path=HERE/('E2_CPU_GENERATION_ERROR_'+str(time.time_ns())+'.json')\n        error_path.write_text(json.dumps(dict(kind='E2_CPU_SOURCE_GENERATION_FAILURE_NOT_SDK',error=traceback.format_exc(),PT_or_SDK_or_training=False),indent=2),encoding='utf-8')\n        raise")
ast.parse(s)
out=HERE/'build_e2_mod4v1_sources_v1.py'
with out.open('x',encoding='utf-8') as f:f.write(s)
print(json.dumps({'new_E2_generator':str(out),'SHA':hashlib.sha256(s.encode()).hexdigest(),'source_templates_only_no_E2_PT_or_SDK':True},indent=2))
