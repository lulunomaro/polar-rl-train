from pathlib import Path
import ast
S=Path(__file__).resolve().parent;p=S/'archive_actual98_fixed_motion_and_E0_regression_unique_once.py'
assert (S/'reports/ACTUAL98_UNIQUE_ARCHIVE_ORIGINAL_ERROR.json').is_file()
s=p.read_text(encoding='utf8')
for a,b in [('FROZEN_UNUSED_STAGE11_READONLY_TERMINAL_INDEX_V1.json','FROZEN_UNUSED_STAGE11_READONLY_SOURCE_INDEX_V1.json'),('ACTUAL98_UNIQUE_ARCHIVE_ORIGINAL_ERROR.json','ACTUAL98_UNIQUE_ARCHIVE_V2_ORIGINAL_ERROR.json')]:
 assert s.count(a)==1;s=s.replace(a,b)
ast.parse(s);exec(compile(s,str(p),'exec'),dict(__file__=str(p),__name__='__main__'))
