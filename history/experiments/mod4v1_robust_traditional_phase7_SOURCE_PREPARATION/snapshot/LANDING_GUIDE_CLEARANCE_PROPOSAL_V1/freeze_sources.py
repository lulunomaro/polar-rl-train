"""Freeze small authoritative source refs before model boot; no asset hashes."""
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;R=D.parent;O=R.parent/'traditional_control_20261101'
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=load(D/'METHOD.json')
paths=[R/'MODEL_AUDIT/mod4v1_usd_source_aligned.xml',R/'physics_bridge.py',O/'kinematics.py',O/'model_parameters.json',
 O/'reports/model_manifest.json',R/'MODEL_AUDIT/mesh_support_helper_v1/mesh_support.py',R/'JUMP270_V1/GAIN_BANK.json',
 R/'MINIHOP_LANDING_V3/controller.py']+[R/x['file']for x in m['candidates']]
assert len(paths)==len(set(paths))==11
assert sha(paths[0])=='0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324'
crouch=load(R/m['start']['file'])['gains']['crouch']['q'];assert len(crouch)==7
poses=[]
for c in m['candidates']:
    q=load(R/c['file'])['gain']['q'];assert len(q)==7 and q[3:5]==q[5:7]
    poses.append(dict(**c,q7=q))
v=dict(kind='SMALL_NOMINAL_GEOMETRY_SOURCE_LOCK_BEFORE_0STEP_BOOT',method_SHA=sha(D/'METHOD.json'),
    sources=[dict(path=str(p.resolve()),bytes=p.stat().st_size,SHA=sha(p))for p in paths],crouch_q7=crouch,candidates=poses,
    raw_files_opened=0,DR_samples_read=0,model_boots=0,mesh_asset_archival_hashes=0)
with (D/'SOURCE_LOCK.json').open('x',encoding='utf-8')as f:json.dump(v,f,indent=2);f.write('\n')
print(json.dumps(dict(status='FROZEN_BEFORE_MODEL_BOOT',small_sources=len(paths),method_SHA=v['method_SHA'],lock_SHA=sha(D/'SOURCE_LOCK.json'),
    poses=poses,crouch_q7=crouch,asset_hashes=0),indent=2))
