from pathlib import Path
import ast,json,time
D=Path(__file__).resolve().parent;W=D.parent;old=W/'MOD4_E1_G1_ACTUAL_REVIEW_20261010'
s=(old/'collect_proxy_route.py').read_text(encoding='utf8').replace("R/'PROXY_ROUTE_PUBLISHED.json'","R/'PUBLISHED.json'").replace('PROXY_ROUTE_COLLECT','ACTUAL_COLLECT').replace('E1-G1-PROXY-ROUTE-COLLECT-02','E1-G2-20MM-ACTUAL-COLLECT-01');ast.parse(s);(D/'collect20mm_actual.py').write_text(s,encoding='utf8')
s=(old/'review_proxy_fullroute.py').read_text(encoding='utf8')
s=s.replace("sys.path.insert(0,str(D))","sys.path.insert(0,str(W))") if False else s
s=s.replace("sys.path.insert(0,str(D))","sys.path.insert(0,str(D.parent/'MOD4_E1_G1_ACTUAL_REVIEW_20261010'))")
s=s.replace('approved_E1_G1_complete_wave_route_behavior_v4','approved_E1_G2_derived20mm_complete_wave_route_behavior_v1').replace('PROXY_ROUTE_COLLECTED','ACTUAL_COLLECTED').replace('PROXY_ROUTE_REVIEW','ACTUAL_REVIEW').replace('df378431ae186eb6d40eb6016095b42f03b077450c960916b8cef3ff0ef8de57','c4255fe5c3407a42019416fdffa6d6786a51b84ae4312f6e362e2b2a60ba1271')
s=s.replace('if len(review)==2:','if False: # This new geometric scope is a single selected-source actual interface/route check, not a paired learning result.')
s=s.replace('review_complete=len(review)==2','review_complete=len(review)==1').replace('initial_actual30q_parameters_assignments_geometry_seed_pair_exact=len(review)==2','single_selected_source_actual_ground_contact_route_scope=True')
s=s.replace("trial_id='E1-G1-FULLROUTE-ACTUAL-REVIEW-01'","trial_id='E1-G2-20MM-ACTUAL-FULLROUTE-REVIEW-01'").replace("trial_id='E1-G1-FULLROUTE-READER-01'","trial_id='E1-G2-20MM-CPU-READER-01'")
ast.parse(s);(D/'review20mm_actual.py').write_text(s,encoding='utf8')
(D/'reports/READERS_PREPARED.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G2-20MM-READERS-PREPARE-01',actual_source_package_protocol_pinned=True,completed_only_bridge_bytes_and_raw_SHA=True,original_numeric_ground_contact_coverage_hardware_contracts_reused=True,single_source_actual_new_geometry_scope_not_learning_pair=True,no_GPU_PPO_or_canonical_write=True),indent=2),encoding='utf8')
