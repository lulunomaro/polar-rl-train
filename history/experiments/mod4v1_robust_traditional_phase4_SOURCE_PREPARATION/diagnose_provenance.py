"""Summarize own capture metadata only; no original raw/source-tree scan."""
from pathlib import Path
from collections import Counter
import json
P=Path(__file__).resolve().parent;g=json.loads((P/'MISSING_AND_VERSION_GAPS.json').read_text(encoding='utf-8'));m=json.loads((P/'SOURCE_MANIFEST.json').read_text(encoding='utf-8'))
print('MISSING_REASONS',dict(Counter(e['reason'] for e in g['events'])))
print('MISSING_PRODUCER_TOP',Counter(str(e.get('producer',e.get('producers',['unknown'])[0] if e.get('producers') else 'unknown')) for e in g['events']).most_common(12))
print('UNRESOLVED_VERSION_CLAIMS',json.dumps(g['unresolved_expected_source_versions'],ensure_ascii=False,indent=2))
print('NON_REPO_MISSING_SAMPLE',json.dumps([e for e in g['events'] if '\\history\\experiments\\' not in e['path']][:30],ensure_ascii=False,indent=2))
print('UNKNOWN_RAW',json.dumps([{'path':e['path'],'bytes':e['bytes'],'status':e['SHA_status']} for e in m['entries'] if e['kind'].endswith('metadata_only') and e['source_SHA'] is None],ensure_ascii=False,indent=2))
