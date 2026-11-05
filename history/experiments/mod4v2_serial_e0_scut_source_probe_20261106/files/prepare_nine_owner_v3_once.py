"""Keep the original terminal-line newline outside the replaced local anchor."""
from pathlib import Path
D=Path(__file__).resolve().parent;s=(D/'prepare_nine_owner_v2_once.py').read_text(encoding='utf8');a='anchor=lines[n.lineno-1].lstrip()+lines[n.body[0].lineno-1]';assert s.count(a)==1;s=s.replace(a,"anchor=(lines[n.lineno-1].lstrip()+lines[n.body[0].lineno-1]).rstrip('\\r\\n')");exec(compile(s,str(Path(__file__)),'exec'),{'__name__':'__main__','__file__':str(Path(__file__))})
