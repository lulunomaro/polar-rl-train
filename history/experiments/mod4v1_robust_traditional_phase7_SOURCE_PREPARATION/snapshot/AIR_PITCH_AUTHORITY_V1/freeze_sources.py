"""Small source/pose lock before model boot, no raw or asset archive hashing."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;R=D.parent;O=R.parent/'traditional_control_20261101'
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=load(D/'METHOD.json')
paths=[R/'MODEL_AUDIT/mod4v1_usd_source_aligned.xml',O/'kinematics.py',O/'model_parameters.json',O/'reports/model_manifest.json',
       R/'sensor_core_jump_v1.py']+[R/p['file']for p in m['poses']]
assert len(paths)==len(set(paths))==8
assert sha(paths[0])=='0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324'
poses=[]
for p in m['poses']:
    v=load(R/p['file'])
    for k in p['key'].split('.'):v=v[k]
    assert len(v)==7 and v[:3]==[0,0,0]and v[3:5]==v[5:7]
    poses.append(dict(**p,q7=v))
assert poses[1]['q7'][4]==.2 and poses[2]['q7'][4]==0.
lock=dict(kind='SMALL_SOURCE_POSE_LOCK_BEFORE_12_FORWARD_QUERIES',method_SHA=sha(D/'METHOD.json'),poses=poses,
    sources=[dict(path=str(p.resolve()),bytes=p.stat().st_size,SHA=sha(p))for p in paths],
    model_boots=0,mj_forward_calls=0,raw_or_DR_samples_read=0,asset_archival_hashes=0)
with (D/'SOURCE_LOCK.json').open('x',encoding='utf-8')as f:json.dump(lock,f,indent=2);f.write('\n')
print(json.dumps(dict(status='LOCKED_BEFORE_MODEL_BOOT',small_sources=8,method_SHA=lock['method_SHA'],source_lock_SHA=sha(D/'SOURCE_LOCK.json'),poses=poses),indent=2))
