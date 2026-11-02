"""Reuse shared renderer on actual465 saved poses; never start an NN or physics."""
from pathlib import Path
import ast
import json
import types
N=Path(__file__).resolve().parent;paths=json.loads((N/'RUN_PATHS.json').read_bytes())
G=Path(paths['repo']);T=Path(paths['task_root']);V=N/'evaluation'
source=(G/'archive_tools/analyze_h1_saved_route.py').read_text('utf8')
# Label-only adaptation; no simulation logic or source package is changed.
source=source.replace('actual456_','actual465_').replace('Recorded actual456 RL455','Recorded actual465 RL464').replace('Actual456 RL455','Actual465 RL464')
ast.parse(source)
renderer=types.ModuleType('saved_actual465_renderer');exec(compile(source,str(G/'archive_tools/analyze_h1_saved_route.py'),'exec'),renderer.__dict__)
receipt=renderer.read(V/'reports/ROOT465_SELECTED_REPLAY_TRANSFERS.json')
packets={r['env']:renderer.load_case(r)for r in receipt['cases']}
out=V/'recorded_native';out.mkdir(exist_ok=False)
media=renderer.dense_view(T,receipt,packets,out)
with(out/'RENDER_REPORT.json').open('x',encoding='utf8')as f:json.dump(dict(actual465=True,model_SHA=receipt['model_SHA'],media=media,NN=0,SDK=0,physics_steps=0),f,indent=2)
print(json.dumps(dict(rendered=True,output=str(out))))
