"""Render actual471 recorded poses through the shared reader; no NN or physics."""
from pathlib import Path
import json
import sys
N=Path(__file__).resolve().parent;paths=json.loads((N/'RUN_PATHS.json').read_bytes())
G=Path(paths['repo']);T=Path(paths['task_root']);V=N/'evaluation'
sys.path.insert(0,str(G/'archive_tools'))
from analyze_h1_saved_route import dense_view,load_case,read
receipt=read(V/'reports/ROOT471_SELECTED_REPLAY_TRANSFERS.json')
packets={r['env']:load_case(r)for r in receipt['cases']}
out=V/'recorded_native';out.mkdir(exist_ok=False)
media=dense_view(T,receipt,packets,out,title='Actual471 RL470',prefix='actual471')
with(out/'RENDER_REPORT.json').open('x',encoding='utf8')as f:json.dump(dict(actual471=True,model_SHA=receipt['model_SHA'],media=media,NN=0,SDK=0,physics_steps=0),f,indent=2)
print(json.dumps(dict(rendered=True,output=str(out))))
