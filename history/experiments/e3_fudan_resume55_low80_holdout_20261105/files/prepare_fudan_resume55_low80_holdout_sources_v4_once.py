"""New fixed version: unique indentation-independent protected byte-span anchors only."""
from pathlib import Path
D=Path(__file__).resolve().parent;s=(D/'prepare_fudan_resume55_low80_holdout_sources_once.py').read_text(encoding='utf8')
changes={
 'GENERATOR_NAME = "prepare_fudan_resume55_low80_holdout_sources_once.py"':'GENERATOR_NAME = "prepare_fudan_resume55_low80_holdout_sources_v4_once.py"',
 'resource_start = b"\\n  try:"':'resource_start = b"wait_until=time.monotonic()+1800;wait_rows=[]"',
 'final_prefix = b"   put(\'FINAL.json\',dict(kind="':'final_prefix = b"put(\'FINAL.json\',dict(kind="',
 'split(b"\\n  except BaseException:", 1)':'split(b"except BaseException:", 1)'
}
for old,new in changes.items():
 expected=2 if old.startswith('split(')else 1
 assert s.count(old)==expected,(old,s.count(old));s=s.replace(old,new)
exec(compile(s,str(Path(__file__)),'exec'),{'__name__':'__main__','__file__':str(Path(__file__))})
