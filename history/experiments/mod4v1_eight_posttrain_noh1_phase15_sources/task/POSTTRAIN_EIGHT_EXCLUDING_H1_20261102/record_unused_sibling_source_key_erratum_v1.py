"""AST-onlyauditofneverexecutednaive-rolereplacement siblingstagers. Preserveoriginal; usenewdata-drivenbuilders."""
from pathlib import Path
import ast,json,hashlib
D=Path(__file__).resolve().parent;p=D/'reports/UNUSED_SIBLING_SOURCE_ROLE_REPLACEMENT_ERRATUM_V1.json';assert not p.exists();rows=[]
for pair,name in((2,'stage_dispatch_pair2_v1_e2_curb113_once.py'),(3,'stage_dispatch_pair3_v1_e3_slope135_once.py')):
 f=D/name;raw=f.read_bytes();t=ast.parse(raw.decode('utf-8'));bad=[dict(line=n.lineno,key=n.arg)for n in ast.walk(t)if isinstance(n,ast.keyword)and n.arg in('native2pt_evidence_file','native3pt_evidence_file')];assert bad
 marker=D/('PAIR'+str(pair)+'_V1_DISPATCH_ONCE.json');assert not marker.exists(),'Ifoldrootstartedreportactualstateinstead ofclaimingunused'
 rows.append(dict(source=str(f),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),bad_keys=bad,expected_key='native0pt_evidence_file',old_dispatch_marker_absent=True,action='KEEP_IMMUTABLE_OLD_SOURCE_DO_NOT_EXECUTE; useDATA_DRIVEN_genericV2specs',runtime_failure_or_PPO_inferred=False))
v=dict(kind='AST_CONFIRMED_UNUSED_SIBLING_ROLE_TEXT_REPLACEMENT_ERROR_NOT_RUNTIME_FAILURE',rows=rows,source_model_stat_hash_decode_SDK_SSH_C_GO_or_physical_ops=0);p.write_text(json.dumps(v,indent=2),encoding='utf-8');print(p);print(json.dumps(v,indent=2))
