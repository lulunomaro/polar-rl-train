"""Keep the actual reader refusal; bind the unchanged feedback audit to own150 raw."""
from wave_direction_io import *
import ast
original=PRIOR/'entry_second_feedback_reset_schema.py'
s=original.read_text().replace('from entry_second_io import *','from wave_direction_io import *').replace('ENTRY_SECOND_CANDIDATE_COLLECTED','DIRECTION_CANDIDATE_COLLECTED').replace('ENTRY_SECOND_FINAL_FEEDBACK_RESET_SCHEMA_ACTUAL_REVIEW','DIRECTION_FINAL_FEEDBACK_RESET_SCHEMA_ACTUAL_REVIEW')
p=D/'direction_feedback_reset_schema_reviewed.py';assert not p.exists();ast.parse(s);p.write_text(s,encoding='utf8',newline='\n')
review=(D/'review_direction_candidate_actual.py').read_text().replace('from entry_second_feedback_reset_schema import recipe_manager','from direction_feedback_reset_schema_reviewed import recipe_manager')
p=D/'review_direction_candidate_feedback_namespace_reviewed_actual.py';assert not p.exists();ast.parse(review);p.write_text(review,encoding='utf8',newline='\n')
save('FEEDBACK_READER_NAMESPACE_ACTUAL_REVIEW.json',dict(epoch=time.time(),original_fullreview_assertion_retained=True,original_helper_imported_prior_scope_R_and_selected_149_raw_not150=True,independent_helper_and_review_files=[p.name,'direction_feedback_reset_schema_reviewed.py'],only_IO_report_namespace_corrected=True,archive_SHA_and_all_raw_SHA_size_final_reset_feedback_formula_clock_tolerances_unchanged=True,no_GPU_or_physics_error_or_replay=True))
print(json.dumps(dict(independent_own150_feedback_namespace_prepared=True,strict_validator_unchanged=True)))
