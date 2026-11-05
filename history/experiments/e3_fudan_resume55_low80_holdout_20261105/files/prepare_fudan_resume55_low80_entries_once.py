"""Prepare three UNUSED Root8 holdout CLIs, preserving original constructor/DR/resources/400 controls."""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent
pairs=(('stage_fudan_low80_confirm_once.py','stage_fudan_resume55_low80_holdout_once.py'),('dispatch_fudan_low80_confirm_once.py','dispatch_fudan_resume55_low80_holdout_once.py'),('collect_fudan_low80_confirm_once.py','collect_fudan_resume55_low80_holdout_once.py'));assert all(not(D/b).exists()for a,b in pairs)
S=D/'source_fudan_frozen_low80_holdout_v2_resume55';P=D/'source_fudan_frozen_low80_parent_v2_resume55';assert len(list(S.glob('*.py')))==10 and len(list(P.glob('*.py')))==3
native=(D/'stage_fudan_resume55_frozen_original_once.py').read_text(encoding='utf8');nt=ast.parse(native);lines=native.splitlines(keepends=True);headers=''.join(''.join(lines[n.lineno-1:n.end_lineno])for n in nt.body if isinstance(n,ast.Assign));front=native[native.index('    closed_path = Path(args.closed)'):native.index('    # All closure validation above precedes every mkdir, connector import and upload.')]
texts=[]
for old,new in pairs:
 s=(D/old).read_text(encoding='utf8').replace('FDNLOW80_CONFIRM_','FDNRESUME55_LOW80_HOLDOUT_').replace('source_fudan_frozen_low80_confirm_v1','source_fudan_frozen_low80_holdout_v2_resume55').replace('source_fudan_frozen_low80_parent_v1','source_fudan_frozen_low80_parent_v2_resume55').replace('E3_FDN_FROZEN_LOW80_CONFIRM_V1','E3_FDN_FROZEN_LOW80_HOLDOUT_RESUME55_V2').replace('FDN_LOW80_3SEED_ACTUAL_WAIT_QUALIFICATION_V1','FDN_LOW80_3SEED_RESUME55_ACTUAL_WAIT_QUALIFICATION_V2').replace('LOW80_FIVE_POSE16_8S_FULLDR_FIRSTEPISODE_CONFIRM','LOW80_FIVE_POSE16_8S_FULLDR_HOLDOUT_FIRSTEPISODE_CONFIRM')
 for a,b in [('20260929','20261002'),('20260930','20261003'),('20261001','20261004')]:s=s.replace(a,b)
 if old.startswith('stage_'):
  a=s.index('    closed_path = Path(args.closed)');b=s.index('    # All closure validation above precedes every mkdir, connector import and upload.');s=s[:a]+front+s[b:]
  st=ast.parse(s);sl=s.splitlines(keepends=True)
  for n in reversed(st.body):
   if isinstance(n,ast.Assign):del sl[n.lineno-1:n.end_lineno]
  s=''.join(sl);a=s.index('\n\ndef need(');s=s[:a]+'\n'+headers+s[a:];s=s.replace('PREFIX = "FDNRESUME55_FROZEN_"','PREFIX = "FDNRESUME55_LOW80_HOLDOUT_"').replace('EVAL_KIND = "E3_FDN_SEQUENCE_FROZEN_ORIGINAL_N80_V1"','EVAL_KIND = "E3_FDN_FROZEN_LOW80_HOLDOUT_RESUME55_V2"')
  a='     need(selected["sha256"]=="55afa';assert a not in s
  a='    need(selected["sha256"]=="55afa784423b5af3d3e3300932628d4d213756c3d2b6c4edaaba2e66b1aaabd7"and selected["bytes"]==146247985,"Actual retained candidate55afa required")';assert s.count(a)==1;s=s.replace(a,'    need(selected["sha256"]=="8e27c2f35d5e1ed5ad2f71324e729bdbda9a10e1486b151ca1dd9384d3ecfe32"and selected["bytes"]==146251569,"Actual complete Root8 continued 8e27 candidate required; source55 excluded")')
 s=s.replace('终点保持','曾获信用且末帧good（非连续25）')
 ast.parse(s);compile(s,new,'exec');texts.append(s)
for (old,new),text in zip(pairs,texts):(D/new).write_text(text,encoding='utf8',newline='\n')
print('Three UNUSED holdout entries compiled; seeds20261002/03/04; full runtime closure and actual parent wait unchanged; no physical/model/SDK/SSH')
