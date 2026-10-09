from pathlib import Path
import ast
D=Path(__file__).resolve().parent
s=(D/'collect20mm_actual.py').read_text(encoding='utf8').replace("R/'PUBLISHED.json'","R/'REPAIRED_PUBLISHED.json'").replace('E1_FULL_ROUTE_REVIEW','E1_ARTIFACT_SOURCE_REVIEW').replace('eval_worker_e1_full_route_review.py','eval_worker_e1_artifact_source_review.py').replace('ACTUAL_COLLECT','ACTUAL_REPAIRED_COLLECT');ast.parse(s);(D/'collect20mm_allowlist_actual.py').write_text(s,encoding='utf8')
s=(D/'review20mm_actual.py').read_text(encoding='utf8').replace('ACTUAL_COLLECTED','ACTUAL_REPAIRED_COLLECTED').replace('ACTUAL_REVIEW','ACTUAL_REPAIRED_REVIEW');ast.parse(s);(D/'review20mm_allowlist_actual.py').write_text(s,encoding='utf8')
