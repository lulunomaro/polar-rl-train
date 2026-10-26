from pathlib import Path
import ast,json,time
H=Path(__file__).resolve().parent;T=H.parent;O=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81O_20261026';F=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82P_20261026';B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
tree=ast.parse((O/'e2_target72_same_backend_install_source_v1.py').read_text('utf8'));code=next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign))
code=code.replace('H1step270_mixed_supermimic_2610v81o/e2','H1step270_mixed_supermimic_2610v82p/e2').replace('H1step270_three_experts_2610v80/e2','H1step270_mixed_supermimic_2610v81o/e2')
code=code.replace("all(x['actual_cost']['duration_bound_passed'] for x in proof['models'].values())","all(x['duration_bound_passed'] for x in proof['original_slots_cost'].values()) and proof['qualification_scope']=='healthy_h1_recovery_models_with_failed_method_all3_original_cost' and set(proof['models'])=={'h1','recovery'} and proof['failed_method']['original_error'] and proof['failed_method']['no_qualified_model']")
old="r['returncode']==0 and r['final']['passed'] and r['final']['final']['SHA']==proof['models']['e2']['final']['SHA']"
assert code.count(old)==1;code=code.replace(old,"r['original_error'] and not (r.get('final') or {}).get('passed') and proof['original_slots_cost']['e2']['charged_seconds']>0",1)
(F/'e2_target72_same_backend_install_source_v1.py').write_text('"""Exact previous failed H1 method resource closure; healthy H1 source is separate."""\nCODE='+repr(code)+'\n','utf8')
src=(O/'deploy_actual_mixed81o_H1_method_original_writer_unused_once.py').read_text('utf8')
start=src.index('  partial=d.code(');end=src.index("  d.upload(c,d.PY72,'recovery',q)",start);src=src[:start]+src[end:]
start=src.index('  if source==d.OWNER:');end=src.index("  if source==d.INSTALL",start);src=src[:start]+src[end:]
src=src.replace('H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81O_20261026','H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82P_20261026').replace('DEPLOYER_REUSED_H1_HELPER_81O_EXACT_SOURCE.py','DEPLOYER_REUSED_H1_HELPER_82P_EXACT_SOURCE.py')
(F/'deploy_actual82p_checkpoint_context_fixed_H1_method_original_writer_unused_once.py').write_text(src,'utf8')
first=(O/'collect_actual_mixed81o_PPO_and_H1_native_policy_first_finite_unused_once.py').read_text('utf8').replace('H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81O_20261026','H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82P_20261026').replace('MIXED81O_ACTUAL_GO_PPO_AND_NATIVE_POLICY_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json','MIXED82P_ACTUAL_GO_PPO_AND_NATIVE_POLICY_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json')
(F/'collect_actual82p_PPO_and_native_H1_policy_first_finite_unused_once.py').write_text(first,'utf8')
for p in F.glob('*.py'):ast.parse(p.read_text('utf8'))
ast.parse(code)
oldcode=next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign));start=oldcode.index('for row in v[\'manifest\'][\'files\']:');end=oldcode.index('print(json.dumps',start)
assert oldcode[start:end]==code[code.index('for row in v[\'manifest\'][\'files\']:'):code.index('print(json.dumps',code.index('for row in v[\'manifest\'][\'files\']:'))]
w=(B/'same_authorized_session_compressed_transport_v130.py').read_text('utf8');needle="        'read_actual81o_failed_method_error_and_original_terminal_cost_unused_once.py',";assert needle in w
names=['deploy_actual82p_checkpoint_context_fixed_H1_method_original_writer_unused_once.py','collect_actual82p_PPO_and_native_H1_policy_first_finite_unused_once.py'];w=w.replace(needle,needle+'\n'+''.join('        '+repr(n)+',\n' for n in names),1)
wp=B/'same_authorized_session_compressed_transport_v131.py';assert not wp.exists();wp.write_text(w,'utf8')
(F/'reports/SOURCE_ONLY82P_EXACT_FAILED_METHOD_RESOURCE_AND_DEPLOY_PROTOCOL_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),source_only=True,previous_failed_method_exact_root=True,method_source_is_healthy81o_H1=True,original_per_file_copy_loop_exact=True,private_shared_GPU_RAM_disk_guards_preserved=True,no_controller_charge_or_budget_change=True,new_GPU_or_installed_admission_not_claimed=True),indent=2),'utf8')
print(json.dumps(dict(prepared82P=True,exact_file_copy_loop=True,not_installed=True)))
