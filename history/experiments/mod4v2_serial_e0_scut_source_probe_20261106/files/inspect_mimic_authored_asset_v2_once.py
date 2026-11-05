"""Preserve continuous-limit signed infinities as text in the metadata-only readback."""
from pathlib import Path
D=Path(__file__).resolve().parent;s=(D/'inspect_mimic_authored_asset_once.py').read_text(encoding='utf8').replace('import json\n','import json,math\n');a='def value(v):\n';assert s.count(a)==1;s=s.replace(a,a+" if isinstance(v,float) and not math.isfinite(v):return '+inf' if v>0 else '-inf' if v<0 else 'nan'\n");exec(compile(s,str(Path(__file__)),'exec'),{'__name__':'__main__','__file__':str(Path(__file__))})
