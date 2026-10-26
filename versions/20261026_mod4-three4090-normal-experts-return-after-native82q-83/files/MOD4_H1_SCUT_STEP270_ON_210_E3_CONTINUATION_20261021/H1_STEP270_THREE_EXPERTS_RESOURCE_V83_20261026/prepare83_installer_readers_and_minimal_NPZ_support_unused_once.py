from pathlib import Path
import ast,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V80_20261026';Q=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82Q_20261026';H=T/'MOD4_UNISUPERMIMIC_H1_STEP270_ON72_CONVERGENCE_20261026';B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
tree=ast.parse((P/'e2_target72_same_backend_install_source_v1.py').read_text('utf8'));code=next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign))
code=code.replace('H1step270_three_experts_2610v80/e2','H1step270_three_experts_2610v83/e2').replace('H1step270_three_experts_2610v79c/e2','H1step270_three_experts_2610v80/e2')
needle="assert not any(p.pid!=os.getpid()"
pos=code.index(needle)
extra="""resource=v['resourceproof'];assert resource['passed'] and resource['qualification_scope']=='production_h1_recovery_pair_and_separate_native_method_diagnostic' and resource['all_owner_nodes_children_actual_out'] and resource['original_canonical_cost_settled'] and resource['all_original_private_shared_locks_free'] and set(resource['models'])=={'h1','recovery'}
displaced=Path(s['displaced_runtime_root']);assert str(displaced)==str(owned/'tasks/H1step270_mixed_supermimic_2610v82q/e2') and s['source_Adamstep']==855660 and s['source_SHA']=='632b3ffb929d76fcdf6b057aae4846424dcf09c90e4277bdbeedb78dccaaacaf' and not s.get('finite_method_test') and not s.get('h1_step270_method_test')
dx=json.loads((displaced/'NODE_EXIT_ACTUAL.json').read_bytes());dt=json.loads((displaced/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert dx['actual_all_own_children_waited'] and dx['validation_fcntl_released_if_acquired'] and dt['terminal_all_own_children_waited'] and dt['original_error'] and not (dt.get('final') or {}).get('passed') and resource['native_method']['present'] is False and resource['native_method']['original_terminal']['original_error']
assert resource['original_slots_cost']['e2']['duration_bound_passed'] and abs(resource['actual_cost_sumonce']-sum(x['charged_seconds'] for x in resource['original_slots_cost'].values()))<1e-5
assert not any(p.pid!=os.getpid() and any(a.startswith(str(displaced)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
"""
code=code[:pos]+extra+code[pos:];ast.parse(code)
(N/'e2_displaced_native_slot_qualified80_source_install_v1.py').write_text('"""Exact old80 E2 source plus current82Q nonproduction-slot closure, no source promotion."""\nCODE='+repr(code)+'\n','utf8')
oldcode=next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign));start=oldcode.index("for r in v['manifest']['files']:");end=oldcode.index('print(json.dumps',start);assert oldcode[start:end]==code[code.index("for r in v['manifest']['files']:"):code.index('print(json.dumps',code.index("for r in v['manifest']['files']:"))]
src=(P/'deploy_actual_three_experts80_V8_readonly_landing_journal_original_writer_unused_once.py').read_text('utf8').replace(P.name,N.name).replace("P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V79C_20261026'","P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V80_20261026'")
src=src.replace('DEPLOYER_REUSED_H1_HELPER_EXACT_SOURCE.py\'\n with captured', 'DEPLOYER_REUSED_H1_HELPER_83_EXACT_SOURCE.py\'\n with captured')
src=src.replace('from e2_target72_same_backend_install_source_v1 import CODE','from e2_displaced_native_slot_qualified80_source_install_v1 import CODE')
needle="source=CODE;args=dict(args,closedproof=json.loads((N/'payloads/e2/CURRENT_ORIGINAL_THREE_CLOSED_MODELS_COST_CPU_ACTUAL.json').read_bytes()))"
assert src.count(needle)==1;src=src.replace(needle,needle[:-1]+",resourceproof=json.loads((N/'payloads/e2/CURRENT_DISPLACED_NATIVE_82Q_CLOSURE_ACTUAL.json').read_bytes()))",1)
(N/'deploy_actual_three83_normal_experts_qualified82Q_80_original_writer_unused_once.py').write_text(src,'utf8')
first=(P/'collect_three_experts80_readonly_landing_journal_first_PPO_finite_unused_once.py').read_text('utf8').replace(P.name,N.name)
(N/'collect_actual_three83_normal_experts_first_PPO_finite_unused_once.py').write_text(first,'utf8')
c=(P/'collect_actual_three80_finals_original_cost_unused_once.py').read_text('utf8');c=c.replace("q=v['q'];owner=Path(q['owner_root']);","q=v['q'];assert max(x['nominal_end_epoch'] for x in v['original_go'].values())-time.time()<=900;owner=Path(q['owner_root']);",1).replace('READ210,dict(q=q),timeout=900',"READ210,dict(q=q,original_go=metadata['source210']['current']['go']),timeout=900",1)
(N/'collect_actual_three83_finals_original_cost_unused_once.py').write_text(c,'utf8');(N/'review_three83_normal_complete_models_original_cost_CPU_unused_once.py').write_bytes((P/'review_three_expert_complete_models_original_cost_CPU_V5_unused_once.py').read_bytes())
# New exact NPZ-only headroom support, never reuse consumed old relocation once or old missing-file indices.
s=(H/'relocate_minimal_closed80_79c_NPZ_for82Q_same_approved_TLS_V5_unused_once.py').read_text('utf8');start=s.index(" O=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81O_20261026'");end=s.index(' known_payload_bytes=',start)
s=s[:start]+''' O=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82Q_20261026'
 proof=read(O/'reports/PRODUCTION_PAIR_AND_NATIVE_METHOD_FULLSTATE_ORIGINAL_COST_CPU_ACTUAL.json');current=read(O/'reports/THREE_EXPERT_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json');assert proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out'] and proof['qualification_scope']=='production_h1_recovery_pair_and_separate_native_method_diagnostic'
 sources=[]
 for name,report in [('H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81O_20261026','HEALTHY_PRODUCTION_PAIR_AND_FAILED_METHOD_ORIGINAL_ALL_COST_CPU_ACTUAL.json'),('H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82Q_20261026','PRODUCTION_PAIR_AND_NATIVE_METHOD_FULLSTATE_ORIGINAL_COST_CPU_ACTUAL.json')]:
  stage=T/name;oldp=read(stage/'reports'/report);oq=read(stage/'reports/THREE_EXPERT_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json');assert oldp['passed'] and oldp['all_owner_nodes_children_actual_out'] and oldp['original_canonical_cost_settled'];sources.append(dict(source_root=oq['roots']['h1'],owner_root=oq['owner_root'],private_lock=oq['specs']['h1']['private_lock'],stage=name))
 q=read(R/'THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
'''+s[end:]
s=s.replace('CLOSED81O_FOR82Q_OLD80_79C','CLOSED82Q_FOR83_81O_82Q').replace("['CLOSED81O_FOR82Q_OLD80_MINIMAL','CLOSED81O_FOR82Q_OLD79C_MINIMAL']","['CLOSED82Q_FOR83_OLD81O_MINIMAL','CLOSED82Q_FOR83_CURRENT82Q_MINIMAL']")
np=N/'relocate_minimal_closed81O_82Q_NPZ_for83_TLS_V5_unused_once.py';np.write_text(s,'utf8')
names=['deploy_actual_three83_normal_experts_qualified82Q_80_original_writer_unused_once.py','collect_actual_three83_normal_experts_first_PPO_finite_unused_once.py','collect_actual_three83_finals_original_cost_unused_once.py',np.name]
w=(B/'same_authorized_session_compressed_transport_v136.py').read_text('utf8');needle="        'read_actual81o_failed_method_error_and_original_terminal_cost_unused_once.py',";assert needle in w;wp=B/'same_authorized_session_compressed_transport_v137.py';assert not wp.exists();wp.write_text(w.replace(needle,needle+'\n'+''.join('        '+repr(n)+',\n' for n in names),1),'utf8')
for p in N.glob('*.py'):ast.parse(p.read_text('utf8'))
with (R/'NORMAL83_PROTOCOL_SOURCE_AND_ORIGINAL_COPY_LOOP_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),prepared_source_only=True,normal_three_expert_sources_only=True,new_E2_installer_exact80source_and82Qnative_resource_closure=True,original_E2_per_file_copy_loop_exact=True,original_owner_charge_resource_and_validready_functions_unchanged=True,original_closure900_local_and_remote=True,NPZ_support_fresh_allout_canonicalNone_and_originalTLS_SHA_before_duplicate_release=True,no_native_prefix_or_Fudan_reference_deployment=True),f,indent=2)
print(json.dumps(dict(prepared83_protocol=True,no_install_or_GO_yet=True)))
