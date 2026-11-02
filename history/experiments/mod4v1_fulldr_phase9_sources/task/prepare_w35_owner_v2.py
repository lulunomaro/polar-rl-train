"""Keep owner-v1 wrong-private-path failure; new unused finite owner uses actual state roots."""
from pathlib import Path
import ast,json,runpy,sys
R=Path(__file__).resolve().parent
report=R/'reports/W35_OWNER_V1_PATH_ERROR_AND_V2_FIX.json';assert not report.exists()
report.write_text(json.dumps({'v1_parent':1421436,'status':'FAILED_BEFORE_GO_SDK_MODEL_OR_CANONICAL_WRITE','error':'PrivateGPU and finite-environment locks were looked up under authority subdirectory instead of original /state root','actual_source_evidence':'Native v3 and original solo227 node use /home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_UUID.lock and finite_environment_validation.lock','original_scope_preserved':True,'new_v2':'unused job, same original two canonical locks and unmodified original authority+charge_values; only actual private/finite path corrected'},indent=2),encoding='utf-8')
p=R/'w35_mod4v1_finite_original_owner_v2.py';assert not p.exists();s=(R/'w35_mod4v1_finite_original_owner_v1.py').read_text(encoding='utf-8').replace("b.C.parent/('three_expert_v2_'","b.C.parent.parent/('three_expert_v2_'").replace("b.C.parent/'finite_environment_validation.lock'","b.C.parent.parent/'finite_environment_validation.lock'");ast.parse(s);p.write_text(s,encoding='utf-8')
s=(R/'deploy_w35_finite_mod4v1_adaptation_once.py').read_text(encoding='utf-8').replace('w35_mod4v1_finite_original_owner_v1.py','w35_mod4v1_finite_original_owner_v2.py').replace('MOD4V1_W35_FULLDR_ADAPT_','MOD4V1_W35_FULLDR_ADAPT_V2_')
p=R/'deploy_w35_finite_mod4v1_adaptation_v2_once.py';assert not p.exists();ast.parse(s);p.write_text(s,encoding='utf-8');sys.path.insert(0,str(R));runpy.run_path(str(p),run_name='__main__')
