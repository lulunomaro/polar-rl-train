"""Fix only a duplicate protected-source start marker before AST/output publication."""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent;s=(D/'prepare_fudan_resume55_low80_holdout_sources_once.py').read_text(encoding='utf8')
a='resource_start = b"\\n  try:"';b='resource_start = b"\\n   wait_until=time.monotonic()+1800;wait_rows=[]"';assert s.count(a)==1;s=s.replace(a,b)
ast.parse(s);exec(compile(s,str(D/'prepare_fudan_resume55_low80_holdout_sources_v2_once.py'),'exec'),{'__name__':'__main__','__file__':str(D/'prepare_fudan_resume55_low80_holdout_sources_v2_once.py')})
