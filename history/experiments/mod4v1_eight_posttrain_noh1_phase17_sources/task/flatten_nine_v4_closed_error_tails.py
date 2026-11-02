from pathlib import Path
import json
R=Path(__file__).resolve().parent;loc=json.loads((R/'reports/NINE_SINGLE_GPU_V4_LATEST_CLOSED_RESULT_PATH.json').read_bytes());v=json.loads(Path(loc['path']).read_bytes());rows=[]
for r in v['rows']:
 if r['error']:
  e=r['error'];rows.append({'role':r['role'],'controls_completed':e.get('controls_completed'),'trace_tail_lines':e['error'].splitlines()[-18:],'source_cache':e.get('source_cache')})
p=R/'reports/NINE_V4_ERROR_TAILS_PROCESSED_ONLY.json';assert not p.exists();p.write_text(json.dumps(rows,indent=2),encoding='utf-8');print(p)
