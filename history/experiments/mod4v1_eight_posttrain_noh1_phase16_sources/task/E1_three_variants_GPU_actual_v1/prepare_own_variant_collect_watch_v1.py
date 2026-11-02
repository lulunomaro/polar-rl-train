from pathlib import Path
import ast
B=Path(__file__).resolve().parent;OLD=B.parent/'E1_actual_qualification_v1'
for name in ['collect_e1_own_case_v1.py','watch_e1_terminal_metadata_v1.py']:
 raw=(OLD/name).read_bytes();ast.parse(raw)
 with (B/name).open('xb') as f:f.write(raw)
print('Ownvariant metadatawatch45s/collector prepared; no source/PT/GPU access now')
