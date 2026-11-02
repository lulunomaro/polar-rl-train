"""Derive a NEW no-optimizer evaluation purpose, preserving all old source/once files."""
from pathlib import Path
import ast,hashlib,json
R=Path(__file__).resolve().parent;D=R/'staged_sources/W35_MOD4V1_EVAL_V1';assert not D.exists();D.mkdir(parents=True)
S=Path(r'C:\Users\lulu\Desktop\claude\mjcf\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\W35_LATEST32481_FULL32S_CLOSURE10MM_SOURCE_V1_20261101')
source=(S/'evaluate_latest32481_full32s_ROOT_ONLY_once.py').read_text(encoding='utf-8')
source=source.replace('from contract_latest32 import','from mod4v1_eval_contract import')
source=source.replace("ROOT=Path(task['qualified_latest227D_job_root']);runtime=ROOT/'runtime';mod=runtime/'isaac/mod4'","ROOT=Path(task['qualified_latest227D_job_root']);runtime=Path(task['runtime_job'])/'runtime';mod=runtime/'isaac/mod4'")
source=source.replace("assert H(ROOT/'original_run_manifest.json')", "assert H(Path(task['runtime_job'])/'original_run_manifest.json')")
source=source.replace("original=read(ROOT/'original_run_manifest.json')['env']","original=read(Path(task['runtime_job'])/'original_run_manifest.json')['env']")
source=source.replace("MOD4_RM70_ORIGINAL_ASSET_ROOT=str(ROOT/'original_field')","MOD4_RM70_ORIGINAL_ASSET_ROOT=str(Path(task['runtime_job'])/'original_field')")
source=source.replace("MOD4_RM70_ASSET_RECEIPT=str(ROOT/'RM70_BINARY_INSTALL_ACTUAL.json')","MOD4_RM70_ASSET_RECEIPT=str(Path(task['runtime_job'])/'RM70_BINARY_INSTALL_ACTUAL.json')")
source=source.replace("MOD4_NEW208_JOB_ROOT=str(job))","MOD4_NEW208_JOB_ROOT=task['runtime_job'],MOD4V1_ASSET_DIR=str(runtime/'assets'))")
source=source.replace("storage=job/'kit_isolation'","storage=Path(task['runtime_job'])/'kit_isolation'")
source=source.replace("entry=mod/'train_full214.py'","entry=mod/'train_mod4v1_w35.py'")
source=source.replace("    from guard_latest32 import install_before_main\n    guard_uninstall=install_before_main(ns,OUT/'BEFORE_CONSTRUCTOR_CLOSURE10MM_MIMIC01_ACTUAL.json')\n",'')
old="     guard=read(OUT/'BEFORE_CONSTRUCTOR_CLOSURE10MM_MIMIC01_ACTUAL.json');assert guard['passed'] and guard['planned_effective_mimic_radians']==.01 and guard['closure_m']==.01 and guard['previous_closure_m']==.002 and guard['user_authorized_closure10mm'] and guard['all_other_termination_params_unchanged_in_JSON_supported_projection']"
new="     guard=real._mod4v1_fresh_dr_guard.receipt();assert guard['new_constructor_nominal_caches_preserved'] and guard['fresh_D0_mass_inertia_based_on_new_asset'] and guard['original_fresh_reset_calls']==1 and guard['usd_sha256']==task['asset_USD_SHA'] and guard['contract_sha256']==task['asset_contract_SHA']"
assert old in source;source=source.replace(old,new)
source=source.replace('guard_before_constructor=guard','new_mod4v1_fullrestore_guard=guard')
needle="     obs=vec.get_observations();tick=int(real._integrated_contact.tick)"
assert needle in source;source=source.replace(needle,"     obs=vec.get_observations();real._mod4v1_fresh_dr_guard.check_observations(obs);put('MOD4V1_FULLRESTORE_GUARD_ACTUAL.json',real._mod4v1_fresh_dr_guard.receipt());tick=int(real._integrated_contact.tick)")
source=source.replace("original_conditions='400N50D0-D7/CAD70 peak-valley/user closure10mm/mimic.01/original sampler and reward'","original_conditions='MOD4v1 2c/bae +400N50D0-D7/CAD70 peak-valley/user closure10mm/mimic.01/original sampler and reward'")
ast.parse(source);(D/'evaluate_mod4v1_w35.py').write_text(source,encoding='utf-8')
for name in ('rm70_intervals227.py','positional_rows227.py','decode227_positional.py'):(D/name).write_bytes((S/name).read_bytes())
contract='''"""New MOD4v1/W35 EVAL_ONLY identity, no GO or authority writer."""\nfrom pathlib import Path\nSHA='2d0bc7b87c30f2f1d7b9130de2afddd554aab1fd8fe398a7e597ec7354d5650b'\nBYTES=17619333;ITER=32481;ADAM=651260;LR=.0002562890625000001;UPDATES=77\nKIND='MOD4V1_W35_LATEST32481_FULLDR_SAMEUID_EVAL_V1'\ndef validate_task(t,admitted=False):\n assert t['kind']==KIND and t['model_SHA']==SHA and t['model_bytes']==BYTES and t['model_iteration']==ITER and t['Adam17']==ADAM and t['actual_saved_LR']==LR\n assert t['num_envs']==20000 and t['controls_max']==1600 and t['worker_seconds']==3600 and t['parent_seconds']==3780 and t['no_new_learning_or_GO']\n assert t['asset_USD_SHA']=='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3' and t['asset_contract_SHA']=='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'\n if admitted:assert t['actual_current_authority_private_shared_resources_admitted'] and t['original_eval_parent_holds_private_and_validation_EX']\n return True\n'''
ast.parse(contract);(D/'mod4v1_eval_contract.py').write_text(contract,encoding='utf-8')
rows=[{'relative':p.name,'bytes':p.stat().st_size,'SHA':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(D.iterdir()) if p.is_file()]
(D/'SOURCE_INDEX.json').write_text(json.dumps({'source_old_eval_SHA':hashlib.sha256((S/'evaluate_latest32481_full32s_ROOT_ONLY_once.py').read_bytes()).hexdigest(),'files':rows,'scope':'Source-only new purpose. No PT, SDK, TaskGO, runtime result or budget write.'},indent=2),encoding='utf-8')
print(json.dumps({'new_source':str(D),'files':rows,'status':'AST_ONLY_NO_TARGET_EXECUTION'},indent=2))
