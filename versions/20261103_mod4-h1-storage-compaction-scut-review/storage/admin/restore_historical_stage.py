"""Extract one old stage, with its original paths and SHA256, only when needed."""
from pathlib import Path
import argparse, hashlib, json, zipfile

p=argparse.ArgumentParser()
p.add_argument('stage', help='Exact original top-level stage directory name')
a=p.parse_args()
scope=Path('F:/RMPOLAR-RL/mjcf_mod4_h1_archive_01a1967f_20261102')
root=scope/'workspace/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021'
assert a.stage and Path(a.stage).name==a.stage and a.stage not in {'.','..'}
rows=[]
with (scope/'history/h1_closed_stages_through_20261031.index.jsonl').open(encoding='utf8') as f:
    for s in f:
        row=json.loads(s)
        if Path(row['relative_path']).parts[0]==a.stage:rows.append(row)
assert rows, 'No such historical stage'
assert not (root/a.stage).exists(), 'Stage already exists; do not overwrite'
with zipfile.ZipFile(scope/'history/h1_closed_stages_through_20261031.zip') as z:
    for row in rows:
        dest=root/row['relative_path']
        assert dest.resolve().is_relative_to(root.resolve())
        dest.parent.mkdir(parents=True,exist_ok=True)
        h=hashlib.sha256()
        with z.open('objects/'+row['SHA256']) as inp, dest.open('xb') as out:
            for block in iter(lambda: inp.read(4*1024*1024),b''):
                h.update(block);out.write(block)
        assert h.hexdigest()==row['SHA256']
print(json.dumps(dict(restored_stage=a.stage,files=len(rows),byte_SHA256_verified=True)))
