from pathlib import Path
import sys,json,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
sys.path.insert(0,str(W/'MOD4_E1_WAVE50_ROUTE_LIFECYCLE_REPAIR_20261012'))
import route_fixture_io as previous
io=previous.io;H=previous.H;run=previous.run;OLD=previous.ROOT
ROOT='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012'
INIT_SHA='68401cae6402c5aa38797dabdbb7043f8036ed6fcbacd9c34fda0bdd95a813c5'
SOURCE='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_FIXTURE_REVIEWED_20261012/learning_logs/2026-10-12_12-52-16_e1_WAVE50_route_lifecycle_observation_1791780538491241968/model_32264.pt'
def save(name,value):
 p=R/name;assert not p.exists();p.write_bytes(json.dumps(value,ensure_ascii=False,indent=2).encode());return p
