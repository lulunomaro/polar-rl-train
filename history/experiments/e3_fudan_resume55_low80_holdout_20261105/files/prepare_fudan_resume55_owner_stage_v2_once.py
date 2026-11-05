"""New unused builder fixes only source-line anchoring before any producer outputs or remote I/O."""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent
s=(D/'prepare_fudan_resume55_owner_stage_once.py').read_text(encoding='utf8')
a="start=q.index('   checks.update(version3_timeout8_branch=');end=q.index('\\n  except Exception',start)"
b="""node=next(n for n in ast.walk(ast.parse(q)) if isinstance(n,ast.Call)and any(k.arg=='version3_timeout8_branch'for k in n.keywords))
qlines=q.splitlines(keepends=True);start=sum(map(len,qlines[:node.lineno-1]));end=sum(map(len,qlines[:node.end_lineno]))"""
assert s.count(a)==1;s=s.replace(a,b)
a="q=q[:start]+'''";assert s.count(a)==1;s=s.replace(a,"q=q[:start]+'''",1)
a="\n''' +q[end:]";assert s.count(a)==1;s=s.replace(a,"\n'''.replace('   init=', '  init=').replace('   checks.update(', '  checks.update(') +q[end:]")
ast.parse(s);exec(compile(s,str(D/'prepare_fudan_resume55_owner_stage_v2_once.py'),'exec'),{'__name__':'__main__','__file__':str(D/'prepare_fudan_resume55_owner_stage_v2_once.py')})
