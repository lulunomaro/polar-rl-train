"""New338/G2-to-G3 readers; no old first-source or permanent-active assertions."""
from pathlib import Path
import ast,json,time
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';assert not (R/'FOLLOWUP_READERS_PREPARED.json').exists()
s=(W/'MOD4_E1_G2_LEARNING_PREPARE_20261010/read_g2_own_save_receipt_reviewed.py').read_text(encoding='utf8').replace('G2','G3').replace('g2','g3').replace('==329','==338').replace('source329','source338').replace('G0_to_G3','G2_to_G3')
s=s.replace(" if not run.is_dir():continue", " if not run.is_dir():continue\n if not (R/'e1_G3_reviewed_observation_PASSED.json').exists():pending.append(dict(run=str(run),phase='formal_final_not_yet_saved_or_closed'));continue")
ast.parse(s);(D/'read_g3_own_save_receipt_reviewed.py').write_bytes(s.encode())
s=(W/'MOD4_E1_G2_MATCHED_CONTINUE_20261010/collect_matched_candidate_actual.py').read_text(encoding='utf8').replace('E1_ARTIFACT_SOURCE_REVIEW','E1_G3_PACKAGE_REVIEW').replace('eval_worker_e1_artifact_source_review.py','eval_worker_e1_g3_package_review.py')
s=s.replace('MATCHED_ACTUAL_','G3_ACTUAL_').replace('CONTINUATION_124','CANDIDATE_127').replace('E1_124-e1-g2-matched-continuation_ASYNC_PUBLISHED.json','E1_127-e1-g3-observation_ASYNC_PUBLISHED.json').replace('e1_G2_matched_continuation_PASSED.json','e1_G3_reviewed_observation_PASSED.json').replace('E1-G2-CONTINUATION-124','E1-G3-300S-127')
ast.parse(s);(D/'collect_g3_observation_actual.py').write_bytes(s.encode())
s=(W/'MOD4_E1_G2_MATCHED_CONTINUE_20261010/review_matched_candidate_actual.py').read_text(encoding='utf8')
s=s.replace("sys.path.insert(0,str(W/'MOD4_E1_G2_20MM_SCOPE_PREPARE_20261010'))\nfrom review20mm_allowlist_actual import audit", "sys.path.insert(0,str(W/'MOD4_E1_G3_35MM_SCOPE_PREPARE_20261010'))\nfrom review35mm126_actual import audit")
s=s.replace('CONTINUATION_124','CANDIDATE_127').replace('c4255fe5c3407a42019416fdffa6d6786a51b84ae4312f6e362e2b2a60ba1271','ccf288b3f32c0d028d8e1cb555d64e98af5267be27fcf4157a3750b8bdfeeebc').replace('MOD4_E1_G2_20MM_SCOPE_PREPARE_20261010/reports/cases/clk2500-closure-episode-d3-122-e1-g2-20mm-source32053-fullroute-flat','MOD4_E1_G3_35MM_SCOPE_PREPARE_20261010/reports/cases/clk2500-closure-episode-d3-126-e1-g3-35mm-source32058-manifest-reviewed-fullroute-flat').replace('E1-G2-900S','E1-G3-300S')
ast.parse(s);(D/'review_g3_observation_actual.py').write_bytes(s.encode())
(R/'FOLLOWUP_READERS_PREPARED.json').write_bytes(json.dumps(dict(epoch=time.time(),trial_id='E1-G3-FOLLOWUP-READERS-PREPARED-07',readers=['read_g3_actual.py','read_g3_own_save_receipt_reviewed.py','collect_g3_observation_actual.py','review_g3_observation_actual.py'],own_source_count=338,actual_source_SHA_and_PID_from_own_PASSED=True,own_snapshot_count_read_not_guessed=True,formal_not_final_is_pending=True,only_actual127_jobs_read_no_queue_or_signal=True,terrain_anchor126_and_old115_valid_results_reused=True,G2_to_G3_newgeometry_startup_disclosed=True,no_more_PPO_without_actual127_review=True),indent=2).encode())
print(json.dumps(dict(readonly_future127_review_prepared=True,old_G0_G2_readers_unchanged=True)))
