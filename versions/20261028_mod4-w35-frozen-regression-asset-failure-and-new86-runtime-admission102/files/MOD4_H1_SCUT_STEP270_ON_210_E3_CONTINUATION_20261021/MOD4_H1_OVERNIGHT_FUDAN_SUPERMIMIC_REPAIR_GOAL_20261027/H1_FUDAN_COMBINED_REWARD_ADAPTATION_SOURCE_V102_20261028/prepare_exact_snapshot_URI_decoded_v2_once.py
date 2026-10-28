"""Preserve original URI-as-Windows-name failure; new destination, decode URL path only."""
from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent
old=B/'prepare_exact_snapshot_and_enabled_reward_oracles_once.py';source=old.read_text('utf8');fixed='from urllib.parse import unquote\n'+source
for a,b in [("dest=B/'pinned_exact'","dest=B/'pinned_exact_v2'"),("path=v['display_url'].split('/8204e853dfd2ed06d85a322e1a998c3d20a3be2c/',1)[1]","path=unquote(v['display_url'].split('/8204e853dfd2ed06d85a322e1a998c3d20a3be2c/',1)[1])"),('PINNED_UPSTREAM_EXACT_TEXT_AND_ENABLED_REWARD_AUDIT_ACTUAL.json','PINNED_UPSTREAM_EXACT_TEXT_AND_ENABLED_REWARD_AUDIT_V2_ACTUAL.json'),('UPSTREAM_TEXT_OR_REWARD_READER_ORIGINAL_ERROR_','UPSTREAM_TEXT_OR_REWARD_READER_V2_ORIGINAL_ERROR_')]:
 assert fixed.count(a)==1;fixed=fixed.replace(a,b,1)
ast.parse(fixed)
with (B/'reports/URI_DECODED_READER_V2_SOURCE_REPAIR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(original_source_SHA=hashlib.sha256(source.encode()).hexdigest(),repaired_execution_source_SHA=hashlib.sha256(fixed.encode()).hexdigest(),only_changes='URI unquote, NEW destination and report names',original_partial_and_error_retained=True,no_model_GPU_or_network=True),f,indent=2)
exec(compile(fixed,str(old),'exec'),{'__name__':'__main__','__file__':str(old)})
