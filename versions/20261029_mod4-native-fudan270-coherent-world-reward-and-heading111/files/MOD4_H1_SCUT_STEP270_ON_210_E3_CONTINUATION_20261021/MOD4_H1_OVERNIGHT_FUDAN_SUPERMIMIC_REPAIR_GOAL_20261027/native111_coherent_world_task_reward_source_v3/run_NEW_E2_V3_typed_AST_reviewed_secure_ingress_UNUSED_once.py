"""New namespace after actual V2 metadata AST false; never replay V2 entry."""
from pathlib import Path
import ast,sys
B=Path(__file__).resolve().parent;A=B.parent/'native111_coherent_world_task_reward_source_v2/run_NEW_E2_V2_reviewed_same_session_hidden_ingress_UNUSED_once.py'
s=A.read_text(encoding='utf8')
s=s.replace("B=Path(__file__).resolve().parent;L=B.parent;R=B/'reports'","B=Path(__file__).resolve().parent;L=B.parent;R=B/'reports'")
s=s.replace('E2_93_NEW86_FROZEN_PROFILE_DOMAIN_PATH_REPAIR_SOURCE_20261029_V2','E2_93_NEW86_TYPED_AST_ENV_GUARD_REPAIR_SOURCE_20261029_V3')
s=s.replace('upload_admit_detach_NEW86_E2_final93_profiles_secure_stdin_UNUSED_once_v2_exactE2root.py','upload_admit_detach_NEW86_E2_final93_profiles_secure_stdin_UNUSED_once_v3_typedASTenv.py')
s=s.replace('FROZEN_E2_93_NEW86_PROFILE_DOMAIN_SOURCE_INDEX_V2.json','FROZEN_E2_93_NEW86_PROFILE_DOMAIN_SOURCE_INDEX_V3.json')
s=s.replace('016982d43d71f87f23d5aab24340754a1f46f1267e62a05a35310b3cbb4797b7','5f9928b271beed082bf1e125022d5cb23bd61c20bd4671c0854b4fa549cd335e')
s=s.replace('bc60ddb35af7f8850f5e99aa68995ac4dcfeda09e26723a33a56ad5228fc94fa','1ea93ca03877ea3addbe73adf5cec521668666820bcae554909b594fa68b4239')
s=s.replace('E2_V2','E2_V3').replace('E2_V2','E2_V3')
ast.parse(s);exec(compile(s,str(A),'exec'),dict(__name__='__main__',__file__=str(Path(__file__).resolve())))
