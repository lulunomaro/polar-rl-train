"""Preserve V1partial/sourceanchor error; NEWV2 roots, normalizeentryEOL only."""
from pathlib import Path
import ast,json
B=Path(__file__).resolve().parent
s=(B/'join_three_variant_exact_sources_v1.py').read_text(encoding='utf-8');s=s.replace("+'_40050_MOD4V1_SOURCE_V1'","+'_40050_MOD4V1_SOURCE_V2'",1).replace('THREE_VARIANT_EXACT_SOURCE_MATERIALIZATION_V1.json','THREE_VARIANT_EXACT_SOURCE_MATERIALIZATION_V2.json');ast.parse(s)
with (B/'join_three_variant_exact_sources_v2.py').open('x',encoding='utf-8') as f:f.write(s)
s=(B/'derive_three_variant_source_overlays_v1.py').read_text(encoding='utf-8');s=s.replace("+'_40050_MOD4V1_SOURCE_V1'","+'_40050_MOD4V1_SOURCE_V2'",1);assert "join['baseline_canonical']+'_40050_MOD4V1_SOURCE_V1'" in s;s=s.replace("s=orig.decode('utf-8-sig');","s=orig.decode('utf-8-sig').replace('\\r\\n','\\n');",1);ast.parse(s)
with (B/'derive_three_variant_source_overlays_v2.py').open('x',encoding='utf-8') as f:f.write(s)
with (B/'V1_CRLF_ANCHOR_READER_ERROR_PRESERVED.json').open('x',encoding='utf-8') as f:json.dump(dict(kind='SOURCE_ONLY_GENERATOR_CRLF_ANCHOR_ERROR_NOT_MODEL_OR_SDK',original='derive_three_variant_source_overlays_v1.py',error='ValueError exactsource anchorcount0 for _sha256 newlineblock',cause='Exact protectedexecutedentry CRLF bytes; directbytes.decode retainsCRLF whereas literalanchor usedLF',action='Preserve allV1partial roots/errorjson; NEWV2 original_exact roots/outputs, normalizeentrylineendings onlybefore targetedanchors; factory AST remainsidentical',PT_SDK_SSH_GPU_operations=0),f,indent=2)
